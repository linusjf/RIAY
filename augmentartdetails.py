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

import os
import sys
import json
import requests
import re
from typing import Dict, Any, Optional
from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory

class ArtDetailsAugmenter:
    """Class for augmenting artwork details using LLM APIs."""

    def __init__(self) -> None:
        """Initialize with configuration from environment."""
        self.config = ConfigEnv(include_os_env=True)
        self.logger = LoggerFactory.get_logger(
            name=os.path.basename(__file__),
            log_to_file=self.config.get(ConfigConstants.LOGGING, False)
        )

    def _get_llm_config(self) -> Dict[str, Optional[str]]:
        """Get required LLM configuration values."""
        llm_config: Dict[str, Optional[str]] = {
            'api_key': self.config.get(ConfigConstants.TEXT_LLM_API_KEY),
            'base_url': self.config.get(ConfigConstants.TEXT_LLM_BASE_URL),
            'endpoint': self.config.get(ConfigConstants.TEXT_LLM_CHAT_ENDPOINT),
            'model': self.config.get(ConfigConstants.TEXT_LLM_MODEL),
            'art_details_prompt': self.config.get(ConfigConstants.ART_DETAILS_AUGMENT_PROMPT)
        }
        self.logger.info(llm_config)
        return llm_config

    def _validate_config(self, config: Dict[str, Optional[str]]) -> None:
        """Validate that all required config values are present."""
        if not all(config.values()):
            error_msg = "Missing required LLM configuration variables"
            self.logger.error(error_msg)
            raise EnvironmentError(error_msg)

    def _build_llm_payload(self, art_json: Dict[str, Any]) -> Dict[str, Any]:
        """Construct the payload for the LLM API request."""
        config = self._get_llm_config()
        llm_payload: Dict[str, Any] = {
            "model": config['model'],
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that enriches metadata about artworks."},
                {"role": "user", "content": f"{config['art_details_prompt']}\n\nInput JSON:\n{json.dumps(art_json, indent=2)}"}
            ]
        }
        self.logger.info(llm_payload)
        return llm_payload

    def _clean_output(self, output: str) -> str:
        """Remove markdown code guards from the output."""
        return re.sub(r'^```(?:json)?\s*|\s*```$', '', output, flags=re.MULTILINE).strip()

    def augment_art_details(self, art_json: Dict[str, Any]) -> str:
        """Enhance artwork JSON with additional details from LLM."""
        config = self._get_llm_config()
        self._validate_config(config)

        url = f"{str(config['base_url']).rstrip('/')}/{str(config['endpoint']).lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = self._build_llm_payload(art_json)
        self.logger.info("Sending request to LLM API")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        completion = response.json()
        output = completion['choices'][0]['message']['content']
        return self._clean_output(output)

def main() -> None:
    try:
        if sys.stdin.isatty():
            logger = LoggerFactory.get_logger(
                name=__name__,
                log_to_file=ConfigEnv().get(ConfigConstants.LOGGING, False)
            )
            logger.error("Please provide JSON input via stdin.")
            sys.exit(1)

        input_json = json.load(sys.stdin)
        augmenter = ArtDetailsAugmenter()
        output = augmenter.augment_art_details(input_json)
        print(output)
    except Exception as e:
        logger = LoggerFactory.get_logger(
            name=os.path.basename(__file__),
            log_to_file=ConfigEnv().get(ConfigConstants.LOGGING, False)
        )
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
