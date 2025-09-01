#!/usr/bin/env python
"""
Verify if an image matches artwork metadata using OpenAI's GPT-4 and semantic vector embedding models.

This module provides ArtworkVerifier class that compares an image's generated description
with provided artwork metadata to determine if they likely represent the same artwork.
"""

import argparse
import base64
import json
import re
import sys
import time
import logging
import os
from typing import Dict, Optional, Tuple, Union, List

from configenv import ConfigEnv
from configconstants import ConfigConstants
from openai import OpenAI
from simtools import MatchMode, compare_terms, compute_match_dicts
from loggerutil import LoggerFactory

# Initialize logger using LoggerFactory
config = ConfigEnv("config.env")
logger = LoggerFactory.get_logger(
    name=os.path.basename(__file__),
    level=logging.INFO,
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)


class ArtworkVerifier:
    """Class for verifying artwork images against metadata using AI models."""

    def __init__(self, config_path: str = 'config.env') -> None:
        """Initialize the verifier with configuration.

        Args:
            config_path: Path to configuration file.
        """
        self.config: ConfigEnv = ConfigEnv(config_path, include_os_env=True)
        self.openai_api_key: Optional[str] = self.config.get(ConfigConstants.OPENAI_API_KEY)
        if not self.openai_api_key:
            logger.error(f"{ConfigConstants.OPENAI_API_KEY} environment variable not set")
            raise ValueError(f"{ConfigConstants.OPENAI_API_KEY} environment variable not set")
        self.client: OpenAI = OpenAI(api_key=self.openai_api_key)

    @staticmethod
    def image_to_bytes(image_path: str) -> bytes:
        """Read image file as bytes.

        Args:
            image_path: Path to the image file.

        Returns:
            The image file content as bytes.
        """
        if '../' in image_path or '..\\' in image_path:
            raise Exception('Invalid file path')
        with open(image_path, "rb") as file:
            return file.read()

    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """Encode image to base64 string.

        Args:
            image_path: Path to the image file.

        Returns:
            Base64 encoded string of the image.
        """
        return base64.b64encode(ArtworkVerifier.image_to_bytes(image_path)).decode("utf-8")

    @staticmethod
    def strip_code_guards(text: str) -> str:
        """Remove markdown code block guards from text.

        Args:
            text: Input text potentially containing markdown code blocks.

        Returns:
            Cleaned text without code block markers.
        """
        text = re.sub(r'```(?:\w+\n)?(.*?)```', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]*)`', r'\1', text)
        return text.strip()

    @staticmethod
    def is_json_string(text: str) -> bool:
        """Check if a string is valid JSON.

        Args:
            text: String to validate as JSON.

        Returns:
            True if the string is valid JSON, False otherwise.
        """
        try:
            json.loads(text)
            return True
        except (ValueError, TypeError):
            return False

    def generate_image_description(self, image_path: str, subject: Optional[str] = None) -> str:
        """Generate image description using OpenAI's GPT-4.

        Args:
            image_path: Path to the image file.
            subject: Optional subject context for the image.

        Returns:
            Generated image description.
        """
        logger.info("🖼️ Generating image description...")
        base64_image: str = self.encode_image_to_base64(image_path)
        prompt: str = self.config.get(ConfigConstants.ART_METADATA_PROMPT, "Describe and interpret this image in detail.")

        if subject:
            prompt = prompt.replace("{}", subject)

        response = self.client.responses.create(
            model="gpt-4o",
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt},{"type": "input_image","image_url": f"data:image/jpeg;base64,{base64_image}"},],}])

        image_description: str = response.output_text
        logger.info(f"🔍 Image Description: {image_description}")
        logger.info(f"🔍 Token usage: {response.usage}")
        return image_description

    @staticmethod
    def parse_arguments() -> argparse.Namespace:
        """Parse and return command line arguments.

        Returns:
            Parsed command line arguments.
        """
        parser = argparse.ArgumentParser(
            description="Verify if an image matches artwork metadata using hosted models."
        )
        parser.add_argument("--image", required=True, help="Path to the image file")
        parser.add_argument("--title", required=True, help="Title of the artwork")
        parser.add_argument("--artist", required=True, help="Artist of the artwork")
        parser.add_argument("--subject", help="Subject of the artwork")
        parser.add_argument("--location", help="Current location of artwork")
        parser.add_argument("--date", help="Date when artwork was created")
        parser.add_argument("--style", help="Style of the artwork")
        parser.add_argument("--medium", help="Medium of the artwork")
        return parser.parse_args()

    @staticmethod
    def create_metadata_text(args: argparse.Namespace) -> Tuple[str, Dict[str, str]]:
        """Create metadata text and dictionary from arguments.

        Args:
            args: Parsed command line arguments.

        Returns:
            Tuple of (metadata text string, metadata dictionary)
        """
        metadata_text: str = ", ".join(filter(None, [
            args.title, args.artist, args.subject, args.location, args.date, args.style, args.medium
        ]))

        metadata_dict: Dict[str, str] = vars(args)
        metadata_dict = {k: v for k, v in metadata_dict.items() if k != 'image'}

        logger.info(f"📋 Metadata text: {metadata_text}")
        logger.info(f"📋 Metadata dict: {metadata_dict}")
        return metadata_text, metadata_dict

    def process_image_description(self, description: str) -> Dict[str, Union[str, float, bool, Dict[str, str]]]:
        """Process the generated image description.

        Args:
            description: Generated image description.

        Returns:
            Dictionary containing processed description data.
        """
        description = self.strip_code_guards(description)
        if not self.is_json_string(description):
            logger.error(f"Error in generating image description: {description}")
            sys.exit(1)

        data: Dict[str, Union[str, float, bool, Dict[str, str]]] = json.loads(description)
        data['subject'] = data['description']
        return data

    def verify(self, args: argparse.Namespace) -> Dict[str, Union[str, float, bool, Dict[str, str]]]:
        """Verify if image matches artwork metadata.

        Args:
            args: Parsed command line arguments.

        Returns:
            Dictionary containing verification results.
        """
        start_time: float = time.time()
        metadata_text: str
        metadata_dict: Dict[str, str]
        metadata_text, metadata_dict = self.create_metadata_text(args)

        try:
            image_description: str = self.generate_image_description(args.image, args.subject)
            image_data: Dict[str, Union[str, float, bool, Dict[str, str]]] = self.process_image_description(image_description)

            image_description_text: str = ", ".join(str(x) for x in [
                image_data['title'],
                image_data['artist'],
                image_data['location'],
                image_data['date'],
                image_data['style'],
                image_data['medium'],
                image_data['description']
            ] if x)
            logger.info(f"Image description: {image_description_text}")

            cosine_score: float = compare_terms(metadata_text, image_description_text, MatchMode.COSINE)
            logger.info(f"Similarity: {cosine_score:.4f}")
            image_data["cosine_score"] = round(cosine_score, 3)

            logger.info("🧠 Checking for matching terms...")
            matched: List[str]
            mismatched: List[str]
            matched, mismatched = compute_match_dicts(metadata_dict, image_data, MatchMode.HYBRID)
            non_empty_count: int = len([v for v in metadata_dict.values() if v])
            is_likely_match: bool = cosine_score >= 0.7 and len(matched) >= non_empty_count // 2

            logger.info(f"🤔 Is likely match? {'Yes' if is_likely_match else 'No'}")
            image_data["is_likely_match"] = is_likely_match
            image_data["matched_terms"] = str(matched)
            image_data["mismatched_terms"] = str(mismatched)

            execution_time: float = time.time() - start_time
            logger.info(f"⏱️ Verified image in {execution_time:.2f} seconds")

            return image_data

        except Exception as error:
            execution_time = time.time() - start_time
            logger.error(f"⏱️ Verification failed: {execution_time:.2f} seconds")
            logger.error(f"❌ Error: {error}")
            raise


def main() -> None:
    """Main function to verify image matches artwork metadata."""
    verifier: ArtworkVerifier = ArtworkVerifier()
    args: argparse.Namespace = verifier.parse_arguments()

    try:
        result: Dict[str, Union[str, float, bool, Dict[str, str]]] = verifier.verify(args)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["is_likely_match"] else 1)
    except Exception:
        sys.exit(2)


if __name__ == "__main__":
    main()
