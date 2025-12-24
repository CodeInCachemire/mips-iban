import os
import sqlite3
PATH_DB = "data/history.db"
CREATE_TABLE = "CREATE TABLE IF NOT EXISTS conversion_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, direction TEXT NOT NULL, input TEXT NOT NULL, output TEXT NOT NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);"
INSERT_INTO = "INSERT INTO conversion_logs (direction, input, output) VALUES (?,?,?);"
READ_LAST_10 = "SELECT * FROM conversion_logs ORDER BY created_at DESC LIMIT 20"


def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE)
    conn.commit()
    conn.close()

def log_conversion(direction: str, input_value: str, output_value: str):
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()
    cursor.execute(INSERT_INTO,(direction,input_value,output_value))
    conn.commit()
    conn.close()

def read_conversion():
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()
    cursor.execute(READ_LAST_10)
    data = cursor.fetchall()
    conn.close()
    return data