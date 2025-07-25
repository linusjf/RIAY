#!/usr/bin/env python
"""
Augmentartdetails.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : augmentartdetails
# @created     : Wednesday Jul 23, 2025 14:51:35 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
Enhances an artwork JSON record by querying an LLM with configurable API settings.
Environment variables required:
- TEXT_LLM_API_KEY
- TEXT_LLM_BASE_URL
- TEXT_LLM_CHAT_ENDPOINT
- TEXT_LLM_MODEL
"""

import sys
import json
import requests
import re
import logging
from typing import Dict, Any, Optional
from configenv import ConfigEnv
from configconstants import ConfigConstants

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure logging to stderr
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.propagate = False

class ArtDetailsAugmenter:
    """Class for augmenting artwork details using LLM APIs."""

    def __init__(self) -> None:
        """Initialize with configuration from environment."""
        self.config = ConfigEnv(include_os_env=True)

    def _get_llm_config(self) -> Dict[str, Optional[str]]:
        """Get required LLM configuration values."""
        return {
            'api_key': self.config.get(ConfigConstants.TEXT_LLM_API_KEY),
            'base_url': self.config.get(ConfigConstants.TEXT_LLM_BASE_URL),
            'endpoint': self.config.get(ConfigConstants.TEXT_LLM_CHAT_ENDPOINT),
            'model': self.config.get(ConfigConstants.TEXT_LLM_MODEL),
            'art_details_prompt': self.config.get(ConfigConstants.ART_DETAILS_AUGMENT_PROMPT)
        }

    def _validate_config(self, config: Dict[str, Optional[str]]) -> None:
        """Validate that all required config values are present."""
        if not all(config.values()):
            error_msg = "Missing required LLM configuration variables"
            logger.error(error_msg)
            raise EnvironmentError(error_msg)

    def _build_llm_payload(self, art_json: Dict[str, Any]) -> Dict[str, Any]:
        """Construct the payload for the LLM API request."""
        config = self._get_llm_config()
        return {
            "model": config['model'],
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that enriches metadata about artworks."},
                {"role": "user", "content": f"{config['art_details_prompt']}\n\nInput JSON:\n{json.dumps(art_json, indent=2)}"}
            ]
        }

    def _clean_output(self, output: str) -> str:
        """Remove markdown code guards from the output."""
        return re.sub(r'^```(?:json)?\s*|\s*```$', '', output, flags=re.MULTILINE).strip()

    def augment_art_details(self, art_json: Dict[str, Any]) -> str:
        """Enhance artwork JSON with additional details from LLM."""
        config = self._get_llm_config()
        self._validate_config(config)

        url = f"{config['base_url'].rstrip('/')}/{config['endpoint'].lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = self._build_llm_payload(art_json)
        logger.info("Sending request to LLM API")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        completion = response.json()
        output = completion['choices'][0]['message']['content']
        return self._clean_output(output)

def main() -> None:
    if sys.stdin.isatty():
        logger.error("Please provide JSON input via stdin.")
        sys.exit(1)

    try:
        input_json = json.load(sys.stdin)
        augmenter = ArtDetailsAugmenter()
        output = augmenter.augment_art_details(input_json)
        print(output)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
