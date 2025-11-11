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
    try:
        with get_connection() as conn: # Uso del bloque 'with' para la conexión
            with conn.cursor() as cur: # Uso del bloque 'with' para el cursor
                cur.execute("""
                    INSERT INTO leads (name, email, business, platform, duration, goal, tone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, email, business, platform, duration, goal, tone))
            conn.commit()
    except Exception as e:
        # Esto es vital para el debug. Podrías logearlo.
        print(f"Error al guardar el lead en Neon DB: {e}")
        # En una aplicación real, podrías querer levantar el error o manejarlo de otra forma.
        pass # Mantener la ejecución si la BD falla, permitiendo que la IA siga funcionando.
