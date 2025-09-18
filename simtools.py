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
import os
import numpy as np
from enum import Enum, auto
from fuzzywuzzy import fuzz
from openai import OpenAI
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt
from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory
from typing import Dict, List, Tuple, Optional, Any
from numpy.typing import NDArray

# Load environment variables from config.env
base_dir: str = os.path.dirname(os.path.abspath(__file__))
dotenv_path: str = os.path.join(base_dir, "config.env")
config: ConfigEnv = ConfigEnv(dotenv_path, include_os_env=True)

# Configure logger using LoggerFactory
LOGGING_ENABLED = config.get(ConfigConstants.LOGGING, False)
logger = LoggerFactory.get_logger(
    name=os.path.basename(__file__),
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)

# Constants
ERROR_MESSAGES: Dict[str, str] = {
    "missing_api_key": f"{ConfigConstants.VECTOR_EMBEDDINGS_MODEL_API_KEY} environment variable not set",
    "missing_base_url": f"{ConfigConstants.VECTOR_EMBEDDINGS_BASE_URL} environment variable not set",
    "missing_model": f"{ConfigConstants.VECTOR_EMBEDDINGS_MODEL} environment variable not set",
    "empty_term": "⚠️ Skipping comparison - empty term: '{term_a}' vs '{term_b}'",
    "invalid_mode": "Invalid mode. Must be one of {MatchMode.FUZZY}, {MatchMode.COSINE}, or {MatchMode.HYBRID}",
    "missing_key": "⚠️ Key '{key}' not found in second dictionary"
}

INFO_MESSAGES: Dict[str, str] = {
    "term_comparison": "🔎 Comparing '{term_a}' to '{term_b}' (score: {score})",
    "term_matching": "🧠 Checking for matching terms...",
    "dict_matching": "🧠 Checking for matching dictionary values...",
    "length_mismatch": "⚠️ Warning: Term arrays have different lengths ({len1} vs {len2})",
    "matched_terms": "✅ Matched terms: {matched}",
    "matched_dict": "✅ Matched dictionary values: {matched}"
}

THRESHOLDS: Dict[str, float] = {
    "fuzzy": 70,
    "cosine": 0.7,
    "hybrid": 50
}

VECTOR_EMBEDDINGS_MODEL_API_KEY: Optional[str] = config.get(ConfigConstants.VECTOR_EMBEDDINGS_MODEL_API_KEY)
if not VECTOR_EMBEDDINGS_MODEL_API_KEY:
    logger.error(ERROR_MESSAGES["missing_api_key"])
    raise ValueError(ERROR_MESSAGES["missing_api_key"])

VECTOR_EMBEDDINGS_BASE_URL: Optional[str] = config.get(ConfigConstants.VECTOR_EMBEDDINGS_BASE_URL)
if not VECTOR_EMBEDDINGS_BASE_URL:
    logger.error(ERROR_MESSAGES["missing_base_url"])
    raise ValueError(ERROR_MESSAGES["missing_base_url"])
VECTOR_EMBEDDINGS_MODEL: Optional[str] = config.get(ConfigConstants.VECTOR_EMBEDDINGS_MODEL)
if not VECTOR_EMBEDDINGS_MODEL:
    logger.error(ERROR_MESSAGES["missing_model"])
    raise ValueError(ERROR_MESSAGES["missing_model"])

timeout = httpx.Timeout(30.0, connect=10.0)
embeddings_client: OpenAI = OpenAI(http_client=httpx.Client(timeout=timeout),
    api_key=VECTOR_EMBEDDINGS_MODEL_API_KEY,
    base_url=VECTOR_EMBEDDINGS_BASE_URL,
)

class MatchMode(Enum):
    FUZZY = auto()
    COSINE = auto()
    HYBRID = auto()

def terms_match(term_a: str, term_b: str, mode: MatchMode = MatchMode.FUZZY) -> bool:
    """Check if two terms match based on the specified mode and thresholds.

    Args:
        term_a: First term to compare
        term_b: Second term to compare
        mode: MatchMode enum value (FUZZY, COSINE or HYBRID)

    Returns:
        True if terms match according to thresholds, False otherwise
    """
    score = compare_terms(term_a, term_b, mode)
    if mode == MatchMode.FUZZY:
        return score >= THRESHOLDS["fuzzy"]
    elif mode == MatchMode.COSINE:
        return score >= THRESHOLDS["cosine"]
    else:  # HYBRID
        return score >= THRESHOLDS["hybrid"]

def compare_terms(term_a: str, term_b: str, mode: MatchMode = MatchMode.FUZZY) -> float:
    """Compare two terms using the specified mode and return match score.

    Args:
        term_a: First term to compare
        term_b: Second term to compare
        mode: MatchMode enum value (FUZZY, COSINE or HYBRID)
    """
    if not term_a or not term_b:
        logger.warning(ERROR_MESSAGES["empty_term"].format(term_a=term_a, term_b=term_b))
        return 0.0

    score: float = 0.0
    if mode == MatchMode.FUZZY:
        score = fuzz.partial_ratio(term_a.lower(), term_b.lower())
    elif mode == MatchMode.COSINE:
        vec1: np.ndarray = get_embedding(term_a)
        vec2: np.ndarray = get_embedding(term_b)
        score = cosine_similarity(vec1, vec2)
    else:
        fuzzy_score: float = fuzz.partial_ratio(term_a.lower(), term_b.lower()) / 100
        vec1 = get_embedding(term_a)
        vec2 = get_embedding(term_b)
        cosine_score: float = cosine_similarity(vec1, vec2)
        score = fuzzy_score * cosine_score * 100  # Scale back to 0-100 range

    logger.info(INFO_MESSAGES["term_comparison"].format(term_a=term_a, term_b=term_b, score=score))
    return score

def compute_match_terms(
    description_terms: List[str],
    metadata_terms: List[str],
    mode: MatchMode = MatchMode.FUZZY
) -> Tuple[List[str], List[str]]:
    """Compute matching between terms from description and metadata.

    Args:
        description_terms: List of terms from description
        metadata_terms: List of terms from metadata
        mode: MatchMode enum value (FUZZY, COSINE or HYBRID)

    Returns:
        Tuple of (matched_terms, mismatched_terms)
    """
    logger.info(INFO_MESSAGES["term_matching"])

    if len(description_terms) != len(metadata_terms):
        logger.warning(INFO_MESSAGES["length_mismatch"].format(len1=len(description_terms), len2=len(metadata_terms)))
        return ([], [])

    matched: List[str] = []
    mismatched: List[str] = []

    for term_a, term_b in zip(description_terms, metadata_terms):
        score: float = compare_terms(term_a, term_b, mode)
        if ((mode == MatchMode.FUZZY and score >= THRESHOLDS["fuzzy"]) or
            (mode == MatchMode.COSINE and score >= THRESHOLDS["cosine"]) or
            (mode == MatchMode.HYBRID and score >= THRESHOLDS["hybrid"])):
            matched.append(f"{term_a} , {term_b}")
        else:
            mismatched.append(f"{term_a} , {term_b}")

    logger.info(INFO_MESSAGES["matched_terms"].format(matched=matched))
    return (matched, mismatched)

def compute_match_dicts(
    dict1: Dict[str, Any],
    dict2: Dict[str, Any],
    mode: MatchMode = MatchMode.FUZZY
) -> Tuple[List[str], List[str]]:
    """Compute matching between values in two dictionaries.

    Args:
        dict1: First dictionary to compare
        dict2: Second dictionary to compare
        mode: MatchMode enum value (FUZZY, COSINE or HYBRID)

    Returns:
        Tuple of (matched_items, mismatched_items)
    """
    logger.info(INFO_MESSAGES["dict_matching"])

    matched: List[str] = []
    mismatched: List[str] = []

    for key, value1 in dict1.items():
        if key not in dict2:
            logger.warning(ERROR_MESSAGES["missing_key"].format(key=key))
            mismatched.append(f"{key}: {value1} , <missing>")
            continue

        value2: str = dict2[key]
        score: float = compare_terms(value1, value2, mode)
        if ((mode == MatchMode.FUZZY and score >= THRESHOLDS["fuzzy"]) or
            (mode == MatchMode.COSINE and score >= THRESHOLDS["cosine"]) or
            (mode == MatchMode.HYBRID and score >= THRESHOLDS["hybrid"])):
            matched.append(f"{key}: {value1} , {value2}")
        else:
            mismatched.append(f"{key}: {value1} , {value2}")

    logger.info(INFO_MESSAGES["matched_dict"].format(matched=matched))
    return (matched, mismatched)

def get_embedding(text: str) -> NDArray[np.float32]:
    # Add retry logic with exponential backoff
    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    def safe_embedding(text: str):
        return embeddings_client.embeddings.create(
            model=str(VECTOR_EMBEDDINGS_MODEL),
            input=text,
            encoding_format="float"
    )
    """Get text embedding using embeddings client."""
    embeddings = safe_embedding(text)
    return np.array(embeddings.data[0].embedding, dtype=np.float32)

def cosine_similarity(vec1: NDArray[np.float32], vec2: NDArray[np.float32]) -> float:
    """Calculate cosine similarity between two vectors."""
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
