import google.generativeai as genai
import os
import json

# NOTA IMPORTANTE: La robustez del JSON ahora depende 100% de la IA y del proceso de limpieza.
# Se eliminaron argumentos 'config' y 'system_instruction' para máxima compatibilidad.

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generar_guiones_gemini(platform, duration, goal, tone, business):
    
    # TODAS las instrucciones y el formato JSON se pasan en el prompt
    prompt = f"""
    INSTRUCCIÓN CRÍTICA: Tu única salida debe ser el objeto JSON. NO incluyas NINGUNA palabra antes o después. NO uses comillas triples o bloques de código (```json).

    Eres un guionista experto en contenido corto para {platform}.
    Crea 3 guiones creativos y originales para el negocio/marca '{business}', cada uno de aproximadamente {duration} segundos.
    El objetivo principal es: {goal}.
    El tono debe ser: {tone}.

    Tu respuesta DEBE ser EXCLUSIVAMENTE un arreglo JSON de 3 objetos, comenzando con [ y terminando con ].
    
    Cada objeto de guion DEBE tener las siguientes 5 claves (y NADA más):
    1. "Titulo": Un título corto y atractivo para el guion.
    2. "Hook": El texto o la acción de inicio (máximo 5 segundos).
    3. "Desarrollo": 3 ideas visuales o acciones clave, separadas por puntos.
    4. "CTA": La llamada a la acción final, clara y atractiva.
    5. "Caption": El texto completo del caption con 5 a 7 hashtags integrados.
    """

    # Llamada a la API con la mínima sintaxis compatible
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    
    # 6. PASO DE LIMPIEZA CRÍTICO para JSONDecodeError
    raw_text = response.text.strip()
    
    # Intentar limpiar el texto si el modelo lo envolvió en bloques de código
    if raw_text.startswith('```json'):
        raw_text = raw_text.lstrip('```json').rstrip('```')
        raw_text = raw_text.strip() # Limpieza adicional después de quitar las marcas

    # 7. Devolver el texto crudo y el objeto Python parseado
    # La advertencia es que si el modelo pone una frase, el JSONDecodeError persistirá.
    # Pero el paso de limpieza mejora mucho la probabilidad de éxito.
    return response.text, json.loads(raw_text)
