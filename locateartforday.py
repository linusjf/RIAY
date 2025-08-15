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
import openai
from pathlib import Path
from typing import cast, Literal, Dict, List, Tuple, Any
from numpy.typing import NDArray
from simtools import get_embedding
from configconstants import ConfigConstants
from configenv import ConfigEnv
from dateutils import is_leap_year,get_month_and_day,validate_day_range
from loggerutil import LoggerFactory

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
        self.year = int(config.get(ConfigConstants.YEAR, datetime.datetime.now().year))
        self.rosary_prompt = config.get(ConfigConstants.ROSARY_PROMPT)
        self.text_llm_api_key = config.get(ConfigConstants.TEXT_LLM_API_KEY)
        self.text_llm_base_url = config.get(ConfigConstants.TEXT_LLM_BASE_URL)
        self.text_llm_chat_endpoint = config.get(ConfigConstants.TEXT_LLM_CHAT_ENDPOINT)
        self.text_llm_model = config.get(ConfigConstants.TEXT_LLM_MODEL)
        self.logger = LoggerFactory.get_logger(
            name=__name__,
            log_to_file=config.get(ConfigConstants.LOGGING, False)
        )

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
            f"SELECT record_id, title, artist, date FROM art_records WHERE record_id IN ({placeholders})",
            record_ids
        )
        rows = cursor.fetchall()
        conn.close()
        # Map ID -> metadata
        return {row[0]: {"title": row[1], "artist": row[2], "year": row[3]} for row in rows}

    def get_rosary_mysteries(self, text: str) -> List[Dict[str, str]]:
        """Get rosary mysteries from text using LLM."""
        self.logger.info("Getting rosary mysteries from text")
        prompt = self.rosary_prompt.replace("{CHRISTIAN_TEXT}", text)
        client = openai.OpenAI(
            api_key=self.text_llm_api_key,
            base_url=self.text_llm_base_url
        )

        response = client.chat.completions.create(
            model=self.text_llm_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        try:
            mysteries = json.loads(response.choices[0].message.content)
            self.logger.info(f"Found {len(mysteries)} rosary mysteries")
            return mysteries
        except Exception as e:
            self.logger.error(f"Failed to parse rosary mysteries: {e}")
            return []

    def search_artworks(self, day_of_year: int) -> None:
        """Search artworks using vector similarity."""
        self.logger.info(f"Searching artworks for day {day_of_year} of year {self.year}")
        validate_day_range(self.year, day_of_year, day_of_year)
        month, _ = get_month_and_day(self.year, day_of_year)

        # Read summary file
        summary_file = Path(f"{month}/Day{day_of_year:03d}Summary.txt")
        if not summary_file.exists():
            error_msg = f"Summary file not found: {summary_file}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        with open(summary_file, 'r', encoding='utf-8') as f:
            query_text = f.read().strip()
            self.logger.debug(f"Loaded query text from {summary_file}")

        mysteries = self.get_rosary_mysteries(query_text)
        if mysteries:
            for mystery in mysteries:
                query_text += f"\nMystery type: {mystery.get('mystery_type', '')}"
                query_text += f"\nMystery name: {mystery.get('mystery_name', '')}"
            self.logger.debug("Added rosary mysteries to query text")

        # Get query vector
        query_vec: NDArray[np.float32] = self.get_query_vector(query_text)

        # Load HNSW index
        p = hnswlib.Index(space=cast(ArtLocator.SpaceType, self.hnsw_space), dim=len(query_vec))
        p.load_index(self.hnsw_path)
        self.logger.info(f"Loaded HNSW index from {self.hnsw_path}")

        # Run search
        labels: NDArray[np.uint64]
        distances: NDArray[np.float32]
        labels, distances = p.knn_query(query_vec, k=self.max_results)
        self.logger.info(f"Found {len(labels[0])} potential matches")

        # Convert labels to metadata
        record_ids: List[int] = labels[0].tolist()
        meta_map: Dict[int, Dict[str, Any]] = self.load_metadata(record_ids)

        self.logger.info("Top matches:")
        for idx, dist in zip(record_ids, distances[0]):
            m = meta_map.get(idx, {})
            match_info = f"- ID {idx} | {m.get('title','?')} by {m.get('artist','?')} ({m.get('date','?')}) | score={1-dist:.4f}"
            self.logger.info(match_info)
            print(match_info)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Locate art for specific day of year")
    parser.add_argument(
        "day_of_year",
        type=int,
        help="Day of year (1-365 or 1-366 for leap years)"
    )
    args = parser.parse_args()
    current_year = datetime.datetime.now().year
    max_day = 366 if is_leap_year(current_year) else 365
    if not 1 <= args.day_of_year <= max_day:
        parser.error(f"day_of_year must be between 1 and {max_day} for year {current_year}")
    return args

if __name__ == "__main__":
    args = parse_args()
    locator = ArtLocator()
    locator.search_artworks(args.day_of_year)
