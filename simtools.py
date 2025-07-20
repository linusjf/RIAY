#!/usr/bin/env python
"""
Similarity tools for art image verification.
Contains functions for text matching and semantic similarity.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : simtools
# @created     : Wednesday Jun 25, 2025 12:45:50 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import sys
import os
import numpy as np
from enum import Enum, auto
from fuzzywuzzy import fuzz
from openai import OpenAI
from configenv import ConfigEnv
from configconstants import ConfigConstants

# Constants
ERROR_MESSAGES = {
    "missing_api_key": f"{ConfigConstants.VECTOR_EMBEDDINGS_MODEL_API_KEY} environment variable not set",
    "missing_base_url": f"{ConfigConstants.VECTOR_EMBEDDINGS_BASE_URL} environment variable not set",
    "missing_model": f"{ConfigConstants.VECTOR_EMBEDDINGS_MODEL} environment variable not set",
    "empty_term": "  ⚠️ Skipping comparison - empty term: '{term_a}' vs '{term_b}'",
    "invalid_mode": "Invalid mode. Must be one of {MatchMode.FUZZY}, {MatchMode.COSINE}, or {MatchMode.HYBRID}",
    "missing_key": "  ⚠️ Key '{key}' not found in second dictionary"
}

INFO_MESSAGES = {
    "term_comparison": "  🔎 Comparing '{term_a}' to '{term_b}' (score: {score})",
    "term_matching": "🧠 Checking for matching terms...",
    "dict_matching": "🧠 Checking for matching dictionary values...",
    "length_mismatch": "⚠️ Warning: Term arrays have different lengths ({len1} vs {len2})",
    "matched_terms": "✅ Matched terms: {matched}",
    "matched_dict": "✅ Matched dictionary values: {matched}"
}

THRESHOLDS = {
    "fuzzy": 70,
    "cosine": 0.7,
    "hybrid": 50
}

# Load environment variables from config.env
# This gets the path of THIS file, no matter how it's imported
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, "config.env")
config  = ConfigEnv(dotenv_path, include_os_env=True)

VECTOR_EMBEDDINGS_MODEL_API_KEY = config.get(ConfigConstants.VECTOR_EMBEDDINGS_MODEL_API_KEY)
if not VECTOR_EMBEDDINGS_MODEL_API_KEY:
    raise ValueError(ERROR_MESSAGES["missing_api_key"])

VECTOR_EMBEDDINGS_BASE_URL = config.get(ConfigConstants.VECTOR_EMBEDDINGS_BASE_URL)
if not VECTOR_EMBEDDINGS_BASE_URL:
    raise ValueError(ERROR_MESSAGES["missing_base_url"])
VECTOR_EMBEDDINGS_MODEL = config.get(ConfigConstants.VECTOR_EMBEDDINGS_MODEL)
if not VECTOR_EMBEDDINGS_MODEL:
    raise ValueError(ERROR_MESSAGES["missing_model"])

deepinfra_client = OpenAI(
    api_key=VECTOR_EMBEDDINGS_MODEL_API_KEY,
    base_url=VECTOR_EMBEDDINGS_BASE_URL,
)

class MatchMode(Enum):
    FUZZY = auto()
    COSINE = auto()
    HYBRID = auto()

def compare_terms(term_a, term_b, mode=MatchMode.FUZZY):
    """Compare two terms using the specified mode and return match score.

    Args:
        term_a: First term to compare
        term_b: Second term to compare
        mode: MatchMode enum value (FUZZY, COSINE or HYBRID)
    """
    if not term_a or not term_b:
        print(ERROR_MESSAGES["empty_term"].format(term_a=term_a, term_b=term_b), file=sys.stderr)
        return 0

    if mode == MatchMode.FUZZY:
        score = fuzz.partial_ratio(term_a.lower(), term_b.lower())
    elif mode == MatchMode.COSINE:
        vec1 = get_embedding(term_a)
        vec2 = get_embedding(term_b)
        score = cosine_similarity(vec1, vec2)
    elif mode == MatchMode.HYBRID:
        fuzzy_score = fuzz.partial_ratio(term_a.lower(), term_b.lower()) / 100
        vec1 = get_embedding(term_a)
        vec2 = get_embedding(term_b)
        cosine_score = cosine_similarity(vec1, vec2)
        score = fuzzy_score * cosine_score * 100  # Scale back to 0-100 range
    else:
        raise ValueError(ERROR_MESSAGES["invalid_mode"].format(MatchMode=MatchMode))

    print(INFO_MESSAGES["term_comparison"].format(term_a=term_a, term_b=term_b, score=score), file=sys.stderr)
    return score

def compute_match_terms(description_terms, metadata_terms, mode=MatchMode.FUZZY):
    """Compute matching between terms from description and metadata.

    Args:
        description_terms: List of terms from description
        metadata_terms: List of terms from metadata
        mode: MatchMode enum value (FUZZY, COSINE or HYBRID)

    Returns:
        Tuple of (matched_terms, mismatched_terms)
    """
    print(INFO_MESSAGES["term_matching"], file=sys.stderr)

    if len(description_terms) != len(metadata_terms):
        print(INFO_MESSAGES["length_mismatch"].format(len1=len(description_terms), len2=len(metadata_terms)), file=sys.stderr)
        return ([], [])

    matched = []
    mismatched = []

    for term_a, term_b in zip(description_terms, metadata_terms):
        score = compare_terms(term_a, term_b, mode)
        if ((mode == MatchMode.FUZZY and score >= THRESHOLDS["fuzzy"]) or
            (mode == MatchMode.COSINE and score >= THRESHOLDS["cosine"]) or
            (mode == MatchMode.HYBRID and score >= THRESHOLDS["hybrid"])):
            matched.append(f"{term_a} , {term_b}")
        else:
            mismatched.append(f"{term_a} , {term_b}")

    print(INFO_MESSAGES["matched_terms"].format(matched=matched), file=sys.stderr)
    return (matched, mismatched)

def compute_match_dicts(dict1, dict2, mode=MatchMode.FUZZY):
    """Compute matching between values in two dictionaries.

    Args:
        dict1: First dictionary to compare
        dict2: Second dictionary to compare
        mode: MatchMode enum value (FUZZY, COSINE or HYBRID)

    Returns:
        Tuple of (matched_items, mismatched_items)
    """
    print(INFO_MESSAGES["dict_matching"], file=sys.stderr)

    matched = []
    mismatched = []

    for key, value1 in dict1.items():
        if key not in dict2:
            print(ERROR_MESSAGES["missing_key"].format(key=key), file=sys.stderr)
            mismatched.append(f"{key}: {value1} , <missing>")
            continue

        value2 = dict2[key]
        score = compare_terms(value1, value2, mode)
        if ((mode == MatchMode.FUZZY and score >= THRESHOLDS["fuzzy"]) or
            (mode == MatchMode.COSINE and score >= THRESHOLDS["cosine"]) or
            (mode == MatchMode.HYBRID and score >= THRESHOLDS["hybrid"])):
            matched.append(f"{key}: {value1} , {value2}")
        else:
            mismatched.append(f"{key}: {value1} , {value2}")

    print(INFO_MESSAGES["matched_dict"].format(matched=matched), file=sys.stderr)
    return (matched, mismatched)

def get_embedding(text):
    """Get text embedding using deepinfra client."""
    embeddings = deepinfra_client.embeddings.create(
        model=VECTOR_EMBEDDINGS_MODEL,
        input=text,
        encoding_format="float"
    )
    return np.array(embeddings.data[0].embedding)

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
