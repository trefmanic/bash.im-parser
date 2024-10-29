#! /usr/bin/env python3
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('quotes.sqlite3')
cursor = conn.cursor()

# Open a plaintext file to write to
with open('output.txt', 'w') as f:
    # Select all rows from the 'quotes' table
    cursor.execute("SELECT text FROM quotes")

    # Iterate over all rows
    rows = cursor.fetchall()
    for row in rows:
        # Write each 'text' field to the file, followed by '%'
        f.write(row[0] + "\n" + "%" + "\n")

# Close the database connection
conn.close()
