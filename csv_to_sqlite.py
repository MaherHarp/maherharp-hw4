#!/usr/bin/env python3
"""
CSV to SQLite Converter
Usage: python3 csv_to_sqlite.py data.db input.csv
Creates or updates SQLite database data.db with data from input.csv
"""

import sys
import csv
import sqlite3
import os
from pathlib import Path

def create_table_from_csv(cursor, csv_file_path, table_name):
    """
    Create a table from CSV file and populate it with data.
    
    Args:
        cursor: SQLite database cursor
        csv_file_path: Path to the CSV file
        table_name: Name for the SQLite table
    """
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        # Read the first row to get column names
        reader = csv.reader(csvfile)
        headers = next(reader)
        
        # Sanitize column names for SQL (replace spaces with underscores, remove special chars)
        sanitized_headers = []
        for header in headers:
            # Replace spaces and special characters with underscores
            sanitized = ''.join(c if c.isalnum() else '_' for c in header.strip())
            # Ensure it doesn't start with a number
            if sanitized and sanitized[0].isdigit():
                sanitized = 'col_' + sanitized
            sanitized_headers.append(sanitized)
        
        # Create table with sanitized column names
        columns = ', '.join([f'"{col}" TEXT' for col in sanitized_headers])
        create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns})'
        
        cursor.execute(create_table_sql)
        
        # Clear existing data in the table
        cursor.execute(f'DELETE FROM "{table_name}"')
        
        # Insert data
        columns_str = ', '.join([f'"{col}"' for col in sanitized_headers])
        placeholders_str = ', '.join(['?' for _ in sanitized_headers])
        insert_sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders_str})'
        
        # Reset file pointer to beginning
        csvfile.seek(0)
        next(reader)  # Skip header row
        
        for row in reader:
            # Pad row with empty strings if it has fewer columns than headers
            while len(row) < len(sanitized_headers):
                row.append('')
            # Truncate row if it has more columns than headers
            row = row[:len(sanitized_headers)]
            cursor.execute(insert_sql, row)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 csv_to_sqlite.py data.db input.csv")
        sys.exit(1)
    
    db_path = sys.argv[1]
    csv_path = sys.argv[2]
    
    # Check if CSV file exists
    if not os.path.exists(csv_path):
        print(f"Error: CSV file '{csv_path}' does not exist")
        sys.exit(1)
    
    # Get table name from CSV filename (without .csv extension)
    table_name = Path(csv_path).stem
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table and populate with data
        create_table_from_csv(cursor, csv_path, table_name)
        
        # Commit changes
        conn.commit()
        
        # Get row count for confirmation
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        row_count = cursor.fetchone()[0]
        
        print(f"Successfully created/updated table '{table_name}' with {row_count} rows")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
