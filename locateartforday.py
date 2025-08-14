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
from typing import cast, Literal, Dict, List, Tuple, Any
from numpy.typing import NDArray
from simtools import get_embedding
from configconstants import ConfigConstants
from configenv import ConfigEnv
from dateutils import is_leap_year,get_month_and_day,validate_day_range

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
        self.year = int(config.get(ConfigConstants.YEAR, 2025))

    def get_query_vector(self, query_text: str) -> NDArray[np.float32]:
        """Generate OpenAI embedding (float32, correct dim)."""
        vec = get_embedding(query_text)
        return vec

    def load_metadata(self, record_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Fetch artwork metadata from SQLite for given IDs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in record_ids)
        cursor.execute(
            f"SELECT record_id, title, artist, date FROM artworks WHERE id IN ({placeholders})",
            record_ids
        )
        rows = cursor.fetchall()
        conn.close()
        # Map ID -> metadata
        return {row[0]: {"title": row[1], "artist": row[2], "year": row[3]} for row in rows}

    def search_artworks(self, day_of_year: int) -> None:
        """Search artworks using vector similarity."""
        validate_day_range(self.year, day_of_year, day_of_year)
        month, day = get_month_and_day(self.year, day_of_year)
        query_text = f"{month} {day}"

        # Get query vector
        query_vec: NDArray[np.float32] = self.get_query_vector(query_text)

        # Load HNSW index
        p = hnswlib.Index(space=cast(ArtLocator.SpaceType, self.hnsw_space), dim=len(query_vec))
        p.load_index(self.hnsw_path)

        # Run search
        labels: NDArray[np.uint64]
        distances: NDArray[np.float32]
        labels, distances = p.knn_query(query_vec, k=self.max_results)

        # Convert labels to metadata
        record_ids: List[int] = labels[0].tolist()
        meta_map: Dict[int, Dict[str, Any]] = self.load_metadata(record_ids)

        print("\nTop matches:")
        for idx, dist in zip(record_ids, distances[0]):
            m = meta_map.get(idx, {})
            print(f"- ID {idx} | {m.get('title','?')} by {m.get('artist','?')} ({m.get('date','?')}) | score={1-dist:.4f}")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Locate art for specific day of year")
    parser.add_argument(
        "day_of_year",
        type=int,
        help="Day of year (1-365 or 1-366 for leap years)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    locator = ArtLocator()
    locator.search_artworks(args.day_of_year)
