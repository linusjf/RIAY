#!/usr/bin/env python3
"""
Generate captions from text summaries using Text LLM APIs

Usage: generatecaption.py "Text to summarize"
       or
       echo "Text to summarize" | generatecaption.py
Output: JSON caption output to stdout
"""

import os
import sys
import time
import argparse
from typing import Dict, Any
import requests
from configenv import ConfigEnv

VERSION = "1.0.0"
SCRIPT_NAME = os.path.basename(__file__)

class CaptionGenerator:
    """Class for generating captions from text using LLM APIs"""
    
    def __init__(self):
        self.config = ConfigEnv(include_os_env=True)
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate required configuration values"""
        required_vars = [
            "TEXT_LLM_MODEL",
            "TEXT_LLM_API_KEY",
            "TEXT_LLM_BASE_URL",
            "TEXT_LLM_CHAT_ENDPOINT",
            "CAPTION_PROMPT"
        ]
        for var in required_vars:
            if var not in self.config:
                print(f"Error: Missing required configuration variable: {var}", file=sys.stderr)
                sys.exit(1)

    def create_payload(self, summary_content: str) -> Dict[str, Any]:
        """Create the API request payload"""
        return {
            "model": self.config["TEXT_LLM_MODEL"],
            "messages": [
                {
                    "role": "system",
                    "content": self.config["CAPTION_PROMPT"]
                },
                {
                    "role": "user",
                    "content": summary_content
                }
            ],
            "temperature": float(self.config.get("TEMPERATURE", 1))
        }

    def generate_caption(self, summary_content: str) -> str:
        """Generate caption from input text"""
        payload = self.create_payload(summary_content)
        headers = {
            "Authorization": f"Bearer {self.config['TEXT_LLM_API_KEY']}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                f"{self.config['TEXT_LLM_BASE_URL']}{self.config['TEXT_LLM_CHAT_ENDPOINT']}",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            generated_content = response.json()["choices"][0]["message"]["content"]

            # Remove markdown code block markers if present
            return generated_content.replace("```json", "").replace("```", "").strip()

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}", file=sys.stderr)
            sys.exit(1)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate caption JSON from text using Text LLM APIs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to generate caption from (or read from stdin if not provided)",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )
    return parser.parse_args()

def get_summary_content(args: argparse.Namespace) -> str:
    """Get the input text either from args or stdin"""
    if args.text:
        return args.text
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    print("Error: No input text provided", file=sys.stderr)
    sys.exit(1)

def main() -> None:
    """Main function"""
    start_time = time.time()

    args = parse_args()
    summary_content = get_summary_content(args)

    generator = CaptionGenerator()
    caption = generator.generate_caption(summary_content)
    print(caption)

    elapsed_time = time.time() - start_time
    print(f"Generated caption in {elapsed_time:.2f} seconds", file=sys.stderr)

if __name__ == "__main__":
    main()
