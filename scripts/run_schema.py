import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import DB_CONFIG
import mysql.connector

with open('db_schema.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# Connect using DB_CONFIG from db.py
conn = None
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    # Split statements by semicolon and execute individually
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        try:
            cursor.execute(stmt)
        except Exception as e:
            # print statement for debugging but continue
            print(f"Statement failed: {e}\nSQL: {stmt}")
    conn.commit()
    print('DB_SCHEMA_APPLIED')
except Exception as exc:
    print('DB_SCHEMA_ERROR:', exc)
finally:
    if conn:
        conn.close()
