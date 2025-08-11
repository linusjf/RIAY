import csv
import sqlite3
from pathlib import Path
import os
import argparse
from typing import Dict, List, Optional, Any, Tuple
from configenv import ConfigEnv
from loggerutil import LoggerFactory
from configconstants import ConfigConstants

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
        self.field_types: Dict[str, str] = {
            'ISO_code': 'TEXT',
            'artist': 'TEXT',
            'caption': 'TEXT',
            'date': 'TEXT',
            'day_number': 'INTEGER',
            'description': 'TEXT',
            'image_filepath': 'TEXT',
            'image_url': 'TEXT',
            'location': 'TEXT',
            'medium': 'TEXT',
            'mystery_name': 'TEXT',
            'mystery_type': 'TEXT',
            'original_title': 'TEXT',
            'style': 'TEXT',
            'subject': 'TEXT',
            'title': 'TEXT',
            'title_language': 'TEXT',
            'title_language_iso': 'TEXT'
        }
        self.logger.debug(f"Initialized ArtDatabaseCreator with csv_path={self.csv_path}, db_path={self.db_path}")

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
                fieldnames: Optional[List[str]] = csv_reader.fieldnames

                if fieldnames:
                    # Use the predefined types for each field
                    columns: List[str] = []
                    for field in fieldnames:
                        if field in self.field_types:
                            columns.append(f"{field} {self.field_types[field]}")
                        else:
                            columns.append(f"{field} TEXT")  # Default to TEXT if field not in types

                    create_table_sql: str = f"""
                    CREATE TABLE IF NOT EXISTS art_records (
                        {', '.join(columns)},
                        PRIMARY KEY (day_number)
                    )
                    """
                    self.logger.debug(f"Create table sql: {create_table_sql}")
                    if self.cursor:
                        self.cursor.execute(create_table_sql)
                    self.logger.info("Successfully created art_records table")
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")
            raise

    def import_data(self) -> None:
        """Import data from CSV into the database."""
        self.logger.debug(f"Importing data from {self.csv_path}")
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                record_count: int = 0

                for row in Dict[str, str] in csv_reader:
                    columns: str = ', '.join(row.keys())
                    placeholders: str = ', '.join(['?'] * len(row))
                    sql: str = f"INSERT OR REPLACE INTO art_records ({columns}) VALUES ({placeholders})"
                    self.logger.debug(f"Insert table sql: {sql}")
                    if self.cursor:
                        self.cursor.execute(sql, tuple(row.values()))
                    record_count += 1

                self.logger.info(f"Successfully imported {record_count} records")
        except Exception as e:
            self.logger.error(f"Error importing data: {e}")
            raise

    def create_database(self) -> None:
        """Main method to create the database and import data."""
        self.logger.info("Starting database creation process")
        try:
            self.connect()
            self.create_table()
            self.import_data()
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
