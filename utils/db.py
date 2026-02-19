import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Get connection URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in environment")

# Create a connection pool (min 1, max 10 connections)
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,
    dsn=DATABASE_URL,
    sslmode='require'  # already in URL, but can be explicit
)

def get_connection():
    return connection_pool.getconn()

def return_connection(conn):
    connection_pool.putconn(conn)

def init_db():
    """Create farmers table if it doesn't exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            mobile VARCHAR(10) UNIQUE NOT NULL,
            email VARCHAR(100),
            state VARCHAR(50) NOT NULL,
            district VARCHAR(50) NOT NULL,
            crop VARCHAR(50) NOT NULL,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    return_connection(conn)

def save_farmer(name, mobile, email, state, district, crop):
    """Insert or update farmer record (upsert on mobile conflict)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO farmers (name, mobile, email, state, district, crop)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (mobile) DO UPDATE SET
            name = EXCLUDED.name,
            email = EXCLUDED.email,
            state = EXCLUDED.state,
            district = EXCLUDED.district,
            crop = EXCLUDED.crop,
            registered_at = CURRENT_TIMESTAMP;
    """, (name, mobile, email, state, district, crop))
    conn.commit()
    cur.close()
    return_connection(conn)

def get_farmer_by_mobile(mobile):
    """Retrieve farmer by mobile number (returns dict or None)."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM farmers WHERE mobile = %s;", (mobile,))
    result = cur.fetchone()
    cur.close()
    return_connection(conn)
    return result