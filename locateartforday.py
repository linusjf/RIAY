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
#!/usr/bin/env python3
import sqlite3
import numpy as np
import hnswlib
import base64
from openai import OpenAI

class ArtLocator:
    """Class for locating artworks using vector similarity search."""
    
    def __init__(self, db_path="artworks.db", hnsw_path="art.hnsw", 
                 hnsw_space="cosine", max_results=5, model="text-embedding-3-large"):
        """
        Initialize the ArtLocator.
        
        Args:
            db_path: Path to SQLite database
            hnsw_path: Path to HNSW index file
            hnsw_space: Metric space ("cosine", "l2", "ip")
            max_results: Number of top matches to return
            model: OpenAI embedding model name
        """
        self.db_path = db_path
        self.hnsw_path = hnsw_path
        self.hnsw_space = hnsw_space
        self.max_results = max_results
        self.model = model
        self.client = OpenAI()

    def get_query_vector(self, query_text):
        """Generate OpenAI embedding (float32, correct dim)."""
        resp = self.client.embeddings.create(
            model=self.model,
            input=query_text,
            encoding_format="float"  # returns list of floats
        )
        vec = np.array(resp.data[0].embedding, dtype=np.float32)
        return vec

    def load_metadata(self, record_ids):
        """Fetch artwork metadata from SQLite for given IDs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in record_ids)
        cursor.execute(
            f"SELECT id, title, artist, year FROM artworks WHERE id IN ({placeholders})", 
            record_ids
        )
        rows = cursor.fetchall()
        conn.close()
        # Map ID -> metadata
        return {row[0]: {"title": row[1], "artist": row[2], "year": row[3]} for row in rows}

    def search_artworks(self, query_text):
        """Search artworks using vector similarity."""
        # Get query vector
        query_vec = self.get_query_vector(query_text)

        # Load HNSW index
        p = hnswlib.Index(space=self.hnsw_space, dim=len(query_vec))
        p.load_index(self.hnsw_path)

        # Run search
        labels, distances = p.knn_query(query_vec, k=self.max_results)

        # Convert labels to metadata
        record_ids = labels[0].tolist()
        meta_map = self.load_metadata(record_ids)

        print("\nTop matches:")
        for idx, dist in zip(record_ids, distances[0]):
            m = meta_map.get(idx, {})
            print(f"- ID {idx} | {m.get('title','?')} by {m.get('artist','?')} ({m.get('year','?')}) | score={1-dist:.4f}")

if __name__ == "__main__":
    locator = ArtLocator()
    query = input("Enter search query: ")
    locator.search_artworks(query)
