import google.generativeai as genai
import os
import json

# NOTA IMPORTANTE: Se eliminaron todos los argumentos 'config' y 'system_instruction' 
# porque la versión del SDK en su entorno no los soporta. 
# TODAS las instrucciones (rol y formato JSON) ahora van dentro del prompt para 
# máxima compatibilidad.

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generar_guiones_gemini(platform, duration, goal, tone, business):
    
    # TODAS las instrucciones y el formato JSON se pasan en el prompt
    prompt = f"""
    Eres un guionista experto en contenido corto para {platform} y tu único trabajo es crear contenido en formato JSON.
    Crea 3 guiones creativos y originales para el negocio/marca '{business}', cada uno de aproximadamente {duration} segundos.
    El objetivo principal es: {goal}.
    El tono debe ser: {tone}.

    Tu respuesta DEBE ser EXCLUSIVAMENTE un arreglo JSON de 3 objetos. NO incluyas texto explicativo, solo el JSON.
    
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
    
    # Devolver el texto crudo y el objeto Python parseado
    # Advertencia: La robustez del JSON ahora depende 100% de la IA y no del esquema forzado.
    return response.text, json.loads(response.text)
