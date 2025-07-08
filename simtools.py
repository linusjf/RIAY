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
from dotenv import load_dotenv

# Load environment variables from config.env
# This gets the path of THIS file, no matter how it's imported
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, "config.env")
load_dotenv(dotenv_path=dotenv_path)

VECTOR_EMBEDDINGS_MODEL_API_KEY = os.getenv("VECTOR_EMBEDDINGS_MODEL_API_KEY")
if not VECTOR_EMBEDDINGS_MODEL_API_KEY:
    raise ValueError("VECTOR_EMBEDDINGS_MODEL_API_KEY environment variable not set")

VECTOR_EMBEDDINGS_BASE_URL = os.getenv("VECTOR_EMBEDDINGS_BASE_URL", "")
if not VECTOR_EMBEDDINGS_BASE_URL:
    raise ValueError("VECTOR_EMBEDDINGS_BASE_URL environment variable not set")
VECTOR_EMBEDDINGS_MODEL = os.getenv("VECTOR_EMBEDDINGS_MODEL", "")
if not VECTOR_EMBEDDINGS_MODEL:
    raise ValueError("VECTOR_EMBEDDINGS_MODEL environment variable not set")

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
        print(f"  ⚠️ Skipping comparison - empty term: '{term_a}' vs '{term_b}'", file=sys.stderr)
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
        raise ValueError(f"Invalid mode. Must be one of {MatchMode.FUZZY}, {MatchMode.COSINE}, or {MatchMode.HYBRID}")

    print(f"  🔎 Comparing '{term_a}' to '{term_b}' (score: {score})", file=sys.stderr)
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
    print("🧠 Checking for matching terms...", file=sys.stderr)

    if len(description_terms) != len(metadata_terms):
        print(f"⚠️ Warning: Term arrays have different lengths ({len(description_terms)} vs {len(metadata_terms)})", file=sys.stderr)
        return ([], [])

    matched = []
    mismatched = []

    for term_a, term_b in zip(description_terms, metadata_terms):
        score = compare_terms(term_a, term_b, mode)
        if ((mode == MatchMode.FUZZY and score >= 70) or
            (mode == MatchMode.COSINE and score >= 0.7) or
            (mode == MatchMode.HYBRID and score >= 50)):
            matched.append(f"{term_a} , {term_b}")
        else:
            mismatched.append(f"{term_a} , {term_b}")

    print(f"✅ Matched terms: {matched}", file=sys.stderr)
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
    print("🧠 Checking for matching dictionary values...", file=sys.stderr)

    matched = []
    mismatched = []

    for key, value1 in dict1.items():
        if key not in dict2:
            print(f"  ⚠️ Key '{key}' not found in second dictionary", file=sys.stderr)
            mismatched.append(f"{key}: {value1} , <missing>")
            continue

        value2 = dict2[key]
        score = compare_terms(value1, value2, mode)
        if ((mode == MatchMode.FUZZY and score >= 70) or
            (mode == MatchMode.COSINE and score >= 0.7) or
            (mode == MatchMode.HYBRID and score >= 50)):
            matched.append(f"{key}: {value1} , {value2}")
        else:
            mismatched.append(f"{key}: {value1} , {value2}")

    print(f"✅ Matched dictionary values: {matched}", file=sys.stderr)
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
