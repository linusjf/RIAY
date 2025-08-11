import csv
import sqlite3
from pathlib import Path
from configenv import ConfigEnv

class ArtDatabaseCreator:
    """Class for creating and managing an SQLite database from art records CSV."""
    
    def __init__(self, csv_path: Path = None, db_path: Path = None):
        """Initialize with paths, loading from config if not provided."""
        config = ConfigEnv()
        self.csv_path = csv_path or Path(config.get('ART_RECORDS_CSV', 'artrecords.csv'))
        self.db_path = db_path or Path(config.get('ART_DATABASE', 'art.db'))
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        """Establish database connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def create_table(self) -> None:
        """Create the art_records table if it doesn't exist."""
        with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            fieldnames = csv_reader.fieldnames

            if fieldnames:
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS art_records (
                    {', '.join(f'{field} TEXT' for field in fieldnames)},
                    PRIMARY KEY (day_number)
                )
                """
                self.cursor.execute(create_table_sql)

    def import_data(self) -> None:
        """Import data from CSV into the database."""
        with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            
            for row in csv_reader:
                columns = ', '.join(row.keys())
                placeholders = ', '.join(['?'] * len(row))
                sql = f"INSERT OR REPLACE INTO art_records ({columns}) VALUES ({placeholders})"
                self.cursor.execute(sql, tuple(row.values())

    def create_database(self) -> None:
        """Main method to create the database and import data."""
        try:
            self.connect()
            self.create_table()
            self.import_data()
            self.connection.commit()
            print(f"Successfully created SQLite database at {self.db_path}")
        except Exception as e:
            print(f"Error creating database: {e}")
        finally:
            self.close()

if __name__ == '__main__':
    db_creator = ArtDatabaseCreator()
    db_creator.create_database()
