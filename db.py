import psycopg2
import os

# ==============================================================================
# 🚨 🚨 🚨 INSTRUCCIÓN CRÍTICA DE BASE DE DATOS 🚨 🚨 🚨
# El error 'ON CONFLICT' que está experimentando ES UN ERROR DE ESQUEMA DE BASE DE DATOS.
# DEBE ejecutar el siguiente comando en su consola de Neon DB para que el código funcione:
#
# 1. Ejecute: ALTER TABLE leads ADD COLUMN script_count INT DEFAULT 0;
# 2. Ejecute: ALTER TABLE leads ADD PRIMARY KEY (email); <--- ESTO SOLUCIONA EL ERROR.
#
# Si la tabla tiene duplicados en la columna 'email', debe limpiarlos antes de ejecutar el comando de clave primaria.
# ------------------------------------------------------------------------------

def get_connection():
    """Establece y devuelve una conexión a la base de datos Neon."""
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
    """Guarda los datos adicionales del lead."""
    try:
        with get_connection() as conn: 
            with conn.cursor() as cur:
                # Usamos ON CONFLICT (email) DO UPDATE. Requiere que 'email' sea una clave única/primaria.
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
        print(f"Error CRÍTICO al guardar el lead en Neon DB: {e}")
        # El error es crítico y se notifica.
        raise

def is_usage_allowed_and_record(normalized_email, max_count):
    """
    Verifica el conteo de uso para un email normalizado. 
    Si está permitido, incrementa el contador y retorna True.
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
                    
                    # Insertar un nuevo registro o actualizar el script_count.
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
        # Se imprime el error para el diagnóstico
        print(f"Error al verificar/grabar uso. ESTO REQUIERE LA CLAVE PRIMARIA EN 'email': {e}")
        # Re-lanzar la excepción para que app.py maneje el fallo de la DB.
        raise
