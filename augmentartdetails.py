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
"""
#!/usr/bin/env python3
"""
augmentartdetails.py

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
from configenv import ConfigEnv
from configconstants import ConfigConstants

def get_config():
    config = ConfigEnv()
    return config

def query_llm(art_json):
    config = get_config()
    api_key = config.get(ConfigConstants.TEXT_LLM_API_KEY)
    base_url = config.get(ConfigConstants.TEXT_LLM_BASE_URL)
    endpoint = config.get(ConfigConstants.TEXT_LLM_CHAT_ENDPOINT)
    model = config.get(ConfigConstants.TEXT_LLM_MODEL)

    if not all([api_key, base_url, endpoint, model]):
        raise EnvironmentError("Missing required LLM configuration variables")

    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are an art historian AI. Enhance the following JSON object with:
- original_title in the original language (if not present)
- title_language and ISO code
- a 20-word caption summarizing the artwork.

Return a well-formatted JSON object with the new fields added.

Input JSON:
{json.dumps(art_json, indent=2)}
"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that enriches metadata about artworks."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    completion = response.json()
    return completion['choices'][0]['message']['content']

def main():
    if sys.stdin.isatty():
        print("Please provide JSON input via stdin.", file=sys.stderr)
        sys.exit(1)

    try:
        input_json = json.load(sys.stdin)
        output = query_llm(input_json)
        print(output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
