#!/usr/bin/env python
"""
Locateartforday.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : locateartforday
# @created     : Thursday Aug 14, 2025 13:01:55 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import sqlite3
import numpy as np
import hnswlib
import argparse
import datetime
import json
import os
import openai
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt
from pathlib import Path
import sys
from typing import cast, Literal, Dict, List, Any, Optional
from numpy.typing import NDArray
from simtools import get_embedding
from configconstants import ConfigConstants
from configenv import ConfigEnv
from dateutils import get_month_and_day,validate_day_range
from loggerutil import LoggerFactory
from markdownhelper import strip_code_guards
from arthelper import is_stock_image_url

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Locate artworks for a specific day of the year using vector similarity search.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'day',
        type=int,
        help='Day of year (1-366) to locate artwork for'
    )
    return parser.parse_args()

class ArtLocator:
    """Class for locating artworks using vector similarity search."""

    SpaceType = Literal["ip", "l2", "cosine"]

    def __init__(
        self,
    ) -> None:
        """
        Initialize the ArtLocator.

        Args:
        """
        config = ConfigEnv(include_os_env=True)
        self.db_path = config.get(ConfigConstants.ART_DATABASE, "art.db")
        self.hnsw_path = config.get(ConfigConstants.ART_DATABASE_HNSW_INDEX, "art.hnsw")
        self.hnsw_space = config.get(ConfigConstants.ART_DATABASE_HNSW_SPACE, "cosine")
        self.max_results = config.get(ConfigConstants.ART_DATABASE_HNSW_MAX_RESULTS, 3)
        self.hnsw_space_dimensions = config.get(ConfigConstants.VECTOR_EMBEDDINGS_MODEL_DIMENSIONS, 1024)
        self.year = int(config.get(ConfigConstants.YEAR, datetime.datetime.now().year))
        self.system_prompt = config.get(ConfigConstants.RIAY_PREAMBLE_PROMPT)
        self.rosary_prompt = config.get(ConfigConstants.ROSARY_PROMPT)
        self.text_llm_api_key = config.get(ConfigConstants.TEXT_LLM_API_KEY)
        self.temperature = config.get(ConfigConstants.TEMPERATURE)
        self.text_llm_base_url = config.get(ConfigConstants.TEXT_LLM_BASE_URL)
        self.text_llm_chat_endpoint = config.get(ConfigConstants.TEXT_LLM_CHAT_ENDPOINT)
        self.text_llm_model = config.get(ConfigConstants.TEXT_LLM_MODEL)
        self.create_caption_prompt = config.get(ConfigConstants.CREATE_CAPTION_PROMPT)
        self.logger = LoggerFactory.get_logger(
            name=os.path.basename(__file__),
            log_to_file=config.get(ConfigConstants.LOGGING, False)
        )

    # Add retry logic with exponential backoff
    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    def safe_chat_completion(self, client: openai.OpenAI, messages: List, temperature: float, top_p: float):
        return client.chat.completions.create(
            model=self.text_llm_model,
            messages=messages,
            temperature=temperature,
            top_p=top_p)

    def generate_caption(self, json_object: str, input_text: str) -> str:
        """Generate a caption for an image record using the OpenAI API.

        Args:
            json_object: JSON string containing artwork metadata
            input_text: Text input describing the artwork

        Returns:
            Generated caption string
        """
        self.logger.debug(f"Create caption prompt: {self.create_caption_prompt}")
        prompt = self.create_caption_prompt.replace("{json_object}", json_object)
        prompt = prompt.replace("{text_input}", input_text)

        timeout = httpx.Timeout(30.0, connect=10.0)
        client = openai.OpenAI(http_client=httpx.Client(timeout=timeout),
                               api_key=self.text_llm_api_key,
                               base_url=self.text_llm_base_url)

        try:
            messages: List = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
            self.logger.debug(f"messages: {messages}")

            response = self.safe_chat_completion(client, messages,1.0, 0.9)
            return str(response.choices[0].message.content).strip('"')
        except Exception as e:
            self.logger.error(f"Failed to generate caption: {e}")
            return ""

    def get_query_vector(self, query_text: str) -> NDArray[np.float32]:
        """Generate OpenAI embedding (float32, correct dim)."""
        self.logger.info("Generating query vector for text")
        vec = get_embedding(query_text)
        return vec

    def load_metadata(self, record_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Fetch artwork metadata from SQLite for given IDs."""
        self.logger.info(f"Loading metadata for record IDs: {record_ids}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in record_ids)
        cursor.execute(
            f"SELECT record_id, artist, caption, date, day_num, description, image_filepath, "
            f"image_url, location, medium, mystery_name, mystery_type, original_title, "
            f"original_title_ISO_code, original_title_language, style, subject, title "
            f"FROM art_records WHERE record_id IN ({placeholders})",
            record_ids
        )
        rows = cursor.fetchall()
        conn.close()
        # Map ID -> metadata
        return {
            row[0]: {
                "artist": row[1],
                "caption": row[2],
                "date": row[3],
                "day_num": row[4],
                "description": row[5],
                "image_filepath": row[6],
                "image_url": row[7],
                "location": row[8],
                "medium": row[9],
                "mystery_name": row[10],
                "mystery_type": row[11],
                "original_title": row[12],
                "original_title_ISO_code": row[13],
                "original_title_language": row[14],
                "style": row[15],
                "subject": row[16],
                "title": row[17]
            } for row in rows
        }

    def get_matching_artworks(self, mystery_type: str, mystery_name: str) -> List[Dict[str, Any]]:
        """Find artworks that directly match mystery type and name."""
        self.logger.info(f"Searching for direct matches of {mystery_type}/{mystery_name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = """
            SELECT record_id, artist, caption, date, day_num, description, image_filepath,
                   image_url, location, medium, mystery_name, mystery_type, original_title,
                   original_title_ISO_code, original_title_language, style, subject, title, embeddings
            FROM art_records
            WHERE (mystery_type LIKE ? OR mystery_type GLOB ?)
            AND (mystery_name LIKE ? OR mystery_name GLOB ?)
        """
        cursor.execute(query, (
            f"%{mystery_type}%",
            f"*{mystery_type}*",
            f"%{mystery_name}%",
            f"*{mystery_name}*"
        ))
        rows = cursor.fetchall()
        conn.close()
        return [{
            "record_id": row[0],
            "artist": row[1],
            "caption": row[2],
            "date": row[3],
            "day_num": row[4],
            "description": row[5],
            "image_filepath": row[6],
            "image_url": row[7],
            "location": row[8],
            "medium": row[9],
            "mystery_name": row[10],
            "mystery_type": row[11],
            "original_title": row[12],
            "original_title_ISO_code": row[13],
            "original_title_language": row[14],
            "style": row[15],
            "subject": row[16],
            "title": row[17],
            "embeddings": row[18]
        } for row in rows]

    def get_rosary_mysteries(self, text: str) -> List[Dict[str, str]]:
        """Get rosary mysteries from text using LLM."""
        self.logger.info("Getting rosary mysteries from text")
        prompt = self.rosary_prompt.replace("{CHRISTIAN_TEXT}", text)
        timeout = httpx.Timeout(30.0, connect=10.0)
        client = openai.OpenAI(http_client=httpx.Client(timeout=timeout),
                               api_key=self.text_llm_api_key,
                               base_url=self.text_llm_base_url)
        messages: List =[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
        ]
        response = self.safe_chat_completion(client, messages,self.temperature,1.0)

        try:
            self.logger.debug(response)
            content = strip_code_guards(str(response.choices[0].message.content), "json")
            self.logger.debug(f"Rosary mysteries: {content}")
            mysteries = json.loads(str(content))
            self.logger.info(f"Found {len(mysteries)} rosary mysteries")
            return mysteries
        except Exception as e:
            self.logger.error(f"Failed to parse rosary mysteries: {e}")
            return []

    def search_artworks(self, day_of_year: int) -> bool:
        """Search artworks using vector similarity."""
        self.logger.info(f"Searching artworks for day {day_of_year} of year {self.year}")
        validate_day_range(self.year, day_of_year, day_of_year)
        month, _ = get_month_and_day(self.year, day_of_year)
        base_query_text = ""
        results = []

        # Read summary file
        summary_file = Path(f"{month}/Day{day_of_year:03d}Summary.txt")
        if not summary_file.exists():
            error_msg = f"Summary file not found: {summary_file}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        with open(summary_file, 'r', encoding='utf-8') as f:
            base_query_text = f.read().strip()
            self.logger.debug(f"Loaded query text from {summary_file}")

        mysteries = self.get_rosary_mysteries(base_query_text)

        if mysteries:
            # Load HNSW index once
            p = hnswlib.Index(space=cast(ArtLocator.SpaceType, self.hnsw_space), dim=self.hnsw_space_dimensions)
            p.load_index(self.hnsw_path)
            self.logger.info(f"Loaded HNSW index from {self.hnsw_path}")


            for mystery in mysteries:
                query_text = base_query_text
                mystery_type = mystery.get("mystery_type", "")
                mystery_name = mystery.get("mystery_name", "")
                if mystery_type or mystery_name:
                    query_text += f"\nMystery type: {mystery_type}"
                    query_text += f"\nMystery name: {mystery_name}"
                    self.logger.debug(f"Searching with mystery: {mystery}")
                    # Get query embedding
                    query_embedding = self.get_query_vector(query_text)

                    # Check for direct matches first
                    direct_matches = self.get_matching_artworks(mystery_type, mystery_name)
                    if direct_matches:
                        self.logger.info(f"Found {len(direct_matches)} direct matches")
                        record_ids = [match['record_id'] for match in direct_matches]

                        # Define a filter: only allow neighbors with even labels
                        def record_id_label_filter(label):
                            return label in record_ids

                        # Find best match by cosine distances
                        labels, distances = p.knn_query([query_embedding], k=1, num_threads=1, filter=record_id_label_filter)
                        self.logger.debug(labels)
                        self.logger.debug(distances)

                        best_match = next(m for m in direct_matches if m['record_id'] == labels[0])
                        if best_match:
                            sanitized_match = {k: v for k, v in best_match.items() if not isinstance(v, bytes)}
                            sanitized_match["cosine_score"] = float(1 - np.ravel(distances)[0])
                            sanitized_match["is_stock_image"] = is_stock_image_url(best_match["image_url"])
                            sanitized_match["generated_caption"] = self.generate_caption(json.dumps(sanitized_match, indent=2),query_text)
                            results.append(sanitized_match)
        else:
            self.logger.info("No rosary mysteries identified...")

        print(json.dumps(results, indent=2))
        return bool(results)

def main() -> None:
    """Main entry point."""
    args = parse_args()
    locator = ArtLocator()
    if locator.search_artworks(args.day):
        sys.exit(0)
    sys.exit(1)

if __name__ == '__main__':
    main()
