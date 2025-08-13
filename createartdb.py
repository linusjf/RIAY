#!/usr/bin/env python3
import csv
import sqlite3
import json
from pathlib import Path
import os
import argparse
import numpy as np
import hnswlib
from typing import Dict, List, Optional, Sequence
from configenv import ConfigEnv
from loggerutil import LoggerFactory
from configconstants import ConfigConstants
from simtools import get_embedding
from hnswlibhelper import recommend_hnsw_params

class ArtDatabaseCreator:
    """Class for creating and managing an SQLite database from art records CSV."""

    def __init__(self, csv_path: Optional[str] = None, db_path: Optional[str] = None) -> None:
        """Initialize with paths, loading from config if not provided."""
        config = ConfigEnv(include_os_env=True)
        self.logger = LoggerFactory.get_logger(name=os.path.basename(__file__),
                                               log_to_file=config.get(ConfigConstants.LOGGING, False))
        self.csv_path = Path(csv_path) if csv_path else Path(config.get(ConfigConstants.ART_RECORDS_CSV, 'artrecords.csv'))
        self.db_path = Path(db_path) if db_path else Path(config.get(ConfigConstants.ART_DATABASE, 'art.db'))
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.field_types = self._load_field_types()
        embeddable_cols = config.get(ConfigConstants.EMBEDDABLE_COLUMNS, "")
        self.embeddable_columns = [col.strip() for col in embeddable_cols.split(",") if col.strip()]
        self.vector_embeddings_dimensions = config.get(ConfigConstants.VECTOR_EMBEDDINGS_MODEL_DIMENSIONS,1024)
        self.logger.debug(f"Initialized ArtDatabaseCreator with csv_path={self.csv_path}, db_path={self.db_path}, embeddable_columns={self.embeddable_columns}")

    def _load_field_types(self) -> Dict[str, str]:
        """Load field types from artrecords.types file."""
        types_path = Path(__file__).parent / 'artrecords.types'
        try:
            with open(types_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading field types: {e}")
            return {}

    def _generate_embedding(self, row: Dict[str, str]) -> bytes:
        """Generate embedding for the specified columns in a row."""
        text_to_embed = ' '.join(str(row.get(col, '')) for col in self.embeddable_columns)
        embedding = get_embedding(text_to_embed)
        return embedding.tobytes()

    def connect(self) -> None:
        """Establish database connection."""
        self.logger.debug(f"Connecting to database at {self.db_path}")
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.logger.info(f"Successfully connected to database at {self.db_path}")

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.logger.debug("Closing database connection")
            self.connection.close()
            self.connection = None
            self.cursor = None
            self.logger.info("Database connection closed")

    def create_table(self) -> None:
        """Create the art_records table if it doesn't exist."""
        self.logger.debug(f"Creating table from CSV file at {self.csv_path}")
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                fieldnames: Optional[Sequence[str]] = csv_reader.fieldnames

                if fieldnames:
                    # Check if table exists and drop it if it does
                    if self.cursor:
                        self.logger.info("Dropping art_records table if it exists...")
                        self.cursor.execute("DROP TABLE if exists art_records")

                    # Use the loaded types for each field
                    columns: List[str] = []
                    columns.append("record_id INTEGER PRIMARY KEY AUTOINCREMENT")
                    for field in fieldnames:
                        if field in self.field_types:
                            columns.append(f"{field} {self.field_types[field]}")
                        else:
                            columns.append(f"{field} TEXT")
                    columns.append("embeddings BLOB")

                    create_table_sql: str = f"""
                    CREATE TABLE art_records (
                        {', '.join(columns)}
                    )
                    """
                    self.logger.debug(f"Create table sql: {create_table_sql}")
                    if self.cursor:
                        self.cursor.execute(create_table_sql)
                    self.logger.info("Successfully created art_records table")
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")
            raise

    def import_data(self) -> int:
        """Import data from CSV into the database."""
        self.logger.debug(f"Importing data from {self.csv_path}")
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                record_count: int = 0

                if csv_reader:
                    row: Dict[str, str]
                    for row in csv_reader:
                        columns: str = ', '.join(row.keys())
                        placeholders: str = ', '.join(['?'] * len(row))
                        embedding = self._generate_embedding(row)
                        sql: str = f"INSERT INTO art_records ({columns}, embeddings) VALUES ({placeholders}, ?)"
                        if self.cursor:
                            self.cursor.execute("SELECT 1 FROM art_records WHERE day_number = ?", (row['day_number'],))
                            if self.cursor.fetchone():
                                 print(f"Duplicate found: {row['day_number']}")
                            self.cursor.execute(sql, tuple(row.values()) + (embedding,))
                            record_count += self.cursor.rowcount

                self.logger.info(f"Successfully imported {record_count} records")
                return record_count
        except Exception as e:
            self.logger.error(f"Error importing data: {e}")
            raise

    def create_hnsw_index(self,no_of_records: int) -> None:
        """Create HNSW index from database embeddings."""
        self.logger.info("Creating HNSW index from database embeddings")
        try:
            if not self.cursor:
                raise RuntimeError("Database cursor not available")

            # Get recommended HNSW parameters
            M, ef_construction = recommend_hnsw_params(no_of_records)

            # Initialize HNSW index
            p = hnswlib.Index(space='cosine', dim=self.vector_embeddings_dimensions)
            p.init_index(max_elements=no_of_records, ef_construction=ef_construction, M=M)

            # Load embeddings from SQLite
            self.cursor.execute("SELECT record_id, embeddings FROM art_records")
            for row_id, emb_blob in self.cursor.fetchall():
                vec = np.frombuffer(emb_blob, dtype=np.float32)
                p.add_items(vec, row_id)

            # Save the index
            index_path = self.db_path.with_suffix('.hnsw')
            p.save_index(str(index_path))
            self.logger.info(f"Saved HNSW index to {index_path}")
        except Exception as e:
            self.logger.error(f"Error creating HNSW index: {e}")
            raise

    def create_database(self) -> None:
        """Main method to create the database and import data."""
        self.logger.info("Starting database creation process")
        try:
            self.connect()
            self.create_table()
            record_count: int = self.import_data()
            self.create_hnsw_index(record_count)
            if self.connection:
                self.connection.commit()
                self.logger.info(f"Successfully created SQLite database at {self.db_path}")
        except Exception as e:
            self.logger.critical(f"Error creating database: {e}")
            raise
        finally:
            self.close()

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Create SQLite database from art records CSV',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--csv',
        help='Path to input CSV file',
        default=None
    )
    parser.add_argument(
        '--db',
        help='Path to output SQLite database',
        default=None
    )
    return parser.parse_args()

if __name__ == '__main__':
    args: argparse.Namespace = parse_args()
    db_creator: ArtDatabaseCreator = ArtDatabaseCreator(csv_path=args.csv, db_path=args.db)
    db_creator.create_database()
