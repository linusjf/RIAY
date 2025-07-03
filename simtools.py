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
load_dotenv('config.env')
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_TOKEN")
if not DEEPINFRA_API_KEY:
    raise ValueError("DEEPINFRA_TOKEN environment variable not set")

deepinfra_client = OpenAI(
    api_key=DEEPINFRA_API_KEY,
    base_url="https://api.deepinfra.com/v1/openai",
)

class MatchMode(Enum):
    FUZZY = auto()
    COSINE = auto()

def compare_terms(term_a, term_b, mode):
    """Compare two terms using the specified mode and return match score.
    
    Args:
        term_a: First term to compare
        term_b: Second term to compare
        mode: MatchMode enum value (FUZZY or COSINE)
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
    else:
        raise ValueError(f"Invalid mode. Must be either {MatchMode.FUZZY} or {MatchMode.COSINE}")
    
    print(f"  🔎 Comparing '{term_a}' to '{term_b}' (score: {score})", file=sys.stderr)
    return score

def compute_match_terms(description_terms, metadata_terms, mode=MatchMode.FUZZY):
    """Compute matching between terms from description and metadata.
    
    Args:
        description_terms: List of terms from description
        metadata_terms: List of terms from metadata
        mode: MatchMode enum value (FUZZY or COSINE)
    """
    print("🧠 Checking for matching terms...", file=sys.stderr)
    matched = []
    
    for term_a, term_b in zip(description_terms, metadata_terms):
        score = compare_terms(term_a, term_b, mode)
        if ((mode == MatchMode.FUZZY and score >= 70) or 
            (mode == MatchMode.COSINE and score >= 0.7)):
            matched.append(f"{term_a} , {term_b}")
    
    print(f"✅ Matched terms: {matched}", file=sys.stderr)
    return matched

def get_embedding(text):
    """Get text embedding using deepinfra client."""
    embeddings = deepinfra_client.embeddings.create(
        model="thenlper/gte-large",
        input=text,
        encoding_format="float"
    )
    return np.array(embeddings.data[0].embedding)

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
