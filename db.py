import psycopg2
import os

# ==============================================================================
# 🚨 🚨 🚨 INSTRUCCIÓN CRÍTICA DE BASE DE DATOS 🚨 🚨 🚨
# El error 'there is no unique or exclusion constraint matching the ON CONFLICT specification'
# ocurre porque la columna 'email' NO es una clave única.
#
# PARA SOLUCIONARLO, DEBES EJECUTAR EL SIGUIENTE COMANDO EN TU CONSOLA DE NEON DB:
#
# ALTER TABLE leads ADD PRIMARY KEY (email);
# 
# Asegúrate también de que la columna 'script_count' exista:
# ALTER TABLE leads ADD COLUMN script_count INT DEFAULT 0;
# ------------------------------------------------------------------------------

def get_connection():
    """Establece y devuelve una conexión a la base de datos Neon."""
    # Los detalles de conexión se obtienen de las variables de entorno de Streamlit
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port="5432",
        sslmode="require"
    )
    return conn

def save_lead(name, normalized_email, business, platform, duration, goal, tone):
    """Guarda los datos adicionales del lead. (Nota: El conteo de uso se maneja en 'is_usage_allowed_and_record')."""
    try:
        with get_connection() as conn: 
            with conn.cursor() as cur:
                # Usamos ON CONFLICT (email) DO UPDATE. Esto requiere que 'email' sea una clave única/primaria.
                cur.execute("""
                    INSERT INTO leads (name, email, business, platform, duration, goal, tone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO UPDATE 
                    SET 
                        name = EXCLUDED.name, 
                        business = EXCLUDED.business,
                        platform = EXCLUDED.platform,
                        duration = EXCLUDED.duration,
                        goal = EXCLUDED.goal,
                        tone = EXCLUDED.tone;
                """, (name, normalized_email, business, platform, duration, goal, tone))
            conn.commit()
    except Exception as e:
        print(f"Error al guardar el lead en Neon DB: {e}")
        # Re-lanzar la excepción para que app.py pueda mostrar una advertencia al usuario.
        raise

def is_usage_allowed_and_record(normalized_email, max_count):
    """
    Verifica el conteo de uso para un email normalizado. 
    Si está permitido, incrementa el contador y retorna True.
    Si excede el límite (max_count), retorna False.
    Si el email no existe, lo crea con un conteo de 1 y retorna True.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Intentar obtener el conteo actual del email normalizado
                cur.execute("SELECT script_count FROM leads WHERE email = %s;", (normalized_email,))
                result = cur.fetchone()

                # Si no existe, el conteo actual es 0. Si existe, tomamos el valor.
                current_count = result[0] if result else 0

                if current_count >= max_count:
                    # Uso no permitido: el límite ya se alcanzó
                    return False
                else:
                    # Uso permitido: registrar/incrementar el uso.
                    new_count = current_count + 1
                    
                    # Insertar un nuevo registro (si no existe) o actualizar el script_count (si ya existe).
                    # Esto solo funciona si 'email' es una clave única.
                    cur.execute("""
                        INSERT INTO leads (email, script_count)
                        VALUES (%s, %s)
                        ON CONFLICT (email) DO UPDATE
                        SET script_count = EXCLUDED.script_count;
                    """, (normalized_email, new_count))
                    
                    conn.commit()
                    return True

    except Exception as e:
        print(f"Error al verificar/grabar uso: {e}")
        # Re-lanzar la excepción para que app.py maneje el fallo de la DB.
        raise
