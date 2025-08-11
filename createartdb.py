import csv
import sqlite3
from pathlib import Path

def create_database(csv_path: Path, db_path: Path) -> None:
    """Create SQLite database from CSV file with day_number as primary key."""
    # Connect to SQLite database (will create if doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read CSV headers to determine table structure
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        fieldnames = csv_reader.fieldnames

        if fieldnames:
            # Create table with day_number as primary key
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS art_records (
                {', '.join(f'{field} TEXT' for field in fieldnames)},
                PRIMARY KEY (day_number)
            )
            """
            cursor.execute(create_table_sql)

            # Insert data from CSV
            for row in csv_reader:
                columns = ', '.join(row.keys())
                placeholders = ', '.join(['?'] * len(row))
                sql = f"INSERT OR REPLACE INTO art_records ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(row.values()))

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Define file paths
    csv_path = Path('artrecords.csv')
    db_path = Path('art.db')

    # Create the database
    create_database(csv_path, db_path)
    print(f"Successfully created SQLite database at {db_path}")
