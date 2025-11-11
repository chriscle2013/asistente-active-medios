import google.generativeai as genai
import os
import json
# SOLUCIÓN: Importamos GenerateContentConfig directamente desde types para resolver el error de AttributeError
genai.types.GenerateContentConfig

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generar_guiones_gemini(platform, duration, goal, tone, business):
    # System Instruction para guiar a la IA
    system_instruction = (
        f"Eres un guionista experto en contenido corto para {platform}. "
        f"Tu único trabajo es crear 3 guiones creativos y originales para {business}."
    )
    
    # Prompt de la solicitud del usuario
    user_prompt = f"""
    Crea 3 guiones creativos y originales de aproximadamente {duration} segundos cada uno.
    El objetivo es: {goal}.
    El tono debe ser {tone}.
    
    Debes estructurar tu respuesta EXCLUSIVAMENTE como un arreglo JSON de 3 objetos.
    Cada objeto de guion debe tener las siguientes 5 claves:
    1. "Titulo": Un título corto y atractivo para el guion.
    2. "Hook": El texto o la acción de inicio (máximo 5 segundos).
    3. "Desarrollo": 3 ideas visuales o acciones clave, separadas por puntos.
    4. "CTA": La llamada a la acción final, clara y atractiva.
    5. "Caption": El texto completo del caption con 5 a 7 hashtags integrados.
    """

    # Definición del esquema JSON
    json_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "Titulo": {"type": "string", "description": "Título atractivo para el guion."},
                "Hook": {"type": "string", "description": "Texto o acción inicial."},
                "Desarrollo": {"type": "string", "description": "3 ideas visuales o acciones clave del desarrollo."},
                "CTA": {"type": "string", "description": "Llamada a la acción final."},
                "Caption": {"type": "string", "description": "Texto completo del caption con hashtags integrados."}
            },
            "required": ["Titulo", "Hook", "Desarrollo", "CTA", "Caption"]
        }
    }

    response = genai.GenerativeModel(
        "gemini-2.5-flash", # Modelo corregido y usado para JSON estructurado
        config=GenerateContentConfig( # Usamos GenerateContentConfig importada directamente
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=json_schema
        )
    ).generate_content(user_prompt)
    
    # Devolver el texto crudo y el objeto Python parseado
    return response.text, json.loads(response.text)
