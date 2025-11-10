import psycopg2
import os

def get_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port="5432",
        sslmode="require"
    )
    return conn

def save_lead(name, email, business, platform, duration, goal, tone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO leads (name, email, business, platform, duration, goal, tone)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (name, email, business, platform, duration, goal, tone))
    conn.commit()
    cur.close()
    conn.close()
