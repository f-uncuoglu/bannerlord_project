import mysql.connector
import sys
import os
import re  # <-- Import the regular expression module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def init_database():
    """Initialize the database with schema and data"""
    
    print("Connecting to MySQL...")
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    cursor = conn.cursor()
    
    print("Creating tables...")
    # Read and execute schema
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
        # Split by semicolon and execute each statement
        for statement in schema.split(';'):
            if statement.strip():
                cursor.execute(statement)
    
    conn.commit()
    print("✓ Tables created successfully!")
    
    
    print("Inserting item types and items...")
    with open('database/items_data.sql', 'r', encoding='utf-8') as f:
        items_sql = f.read()
        for statement in items_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
    conn.commit()

    print("Inserting data...")
    # Read and execute data inserts
    with open('database/bannerlord_troops.sql', 'r', encoding='utf-8') as f:
        data_sql = f.read()
        
        # --- START FIX ---
        # Remove all SQL line comments (--) before splitting
        data_sql = re.sub(r'--.*', '', data_sql)
        
        # Split by semicolon and execute each statement
        for statement in data_sql.split(';'):
            # Now we only need to check if the statement is not just whitespace
            if statement.strip():
                try:
                    cursor.execute(statement)
                except mysql.connector.Error as err:
                    # Print a more helpful error message
                    print(f"\n--- ERROR EXECUTING STATEMENT ---")
                    print(f"Error: {err}")
                    print(f"Failed Statement (truncated): {statement.strip()[:200]}...")
                    print(f"-----------------------------------\n")
        # --- END FIX ---
    
    conn.commit()
    print("✓ Data inserted successfully!")
    
    # Verify data
    cursor.execute("SELECT COUNT(*) FROM Troops")
    troop_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Cultures")
    culture_count = cursor.fetchone()[0]
    
    print(f"\n{'='*50}")
    print(f"Database initialized successfully!")
    print(f"{'='*50}")
    print(f"Cultures: {culture_count}")
    print(f"Troops: {troop_count}")  # <-- This should now show the correct count
    print(f"{'='*50}\n")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)