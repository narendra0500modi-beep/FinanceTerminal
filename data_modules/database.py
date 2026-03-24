import sqlite3
import pandas as pd
import os

# 1. Lock down the exact file path using Absolute Paths so Python cannot get confused
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "master_portfolio.db")

def init_db():
    """Creates the database tables if they don't exist yet."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table 1: Clients
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Table 2: Holdings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            ticker TEXT NOT NULL,
            quantity REAL NOT NULL,
            avg_price REAL NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_client(name):
    init_db() # Forces table creation
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clients (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return True, "Client added successfully!"
    except sqlite3.IntegrityError:
        return False, "Client already exists."

def get_clients():
    init_db() # Forces table creation
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM clients", conn)
    conn.close()
    return df

def add_holding(client_id, ticker, quantity, avg_price):
    init_db() # Forces table creation
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO holdings (client_id, ticker, quantity, avg_price) 
        VALUES (?, ?, ?, ?)
    ''', (client_id, ticker.upper(), quantity, avg_price))
    conn.commit()
    conn.close()

def get_client_holdings(client_id):
    init_db() # Forces table creation
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT ticker, quantity, avg_price FROM holdings WHERE client_id = ?", conn, params=(client_id,))
    conn.close()
    return df