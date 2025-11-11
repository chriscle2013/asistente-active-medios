import google.generativeai as genai
import os
import json

# NOTA IMPORTANTE: La configuración se pasa como un diccionario simple (dict) a generate_content() 
# para garantizar la compatibilidad con versiones antiguas del SDK, solucionando el error sobre 'config' 
# no ser un argumento esperado en GenerativeModel.init().

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generar_guiones_gemini(platform, duration, goal, tone, business):
    
    # 1. Definición del esquema JSON para la salida estructurada
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
    
    # 2. System Instruction para guiar a la IA
    system_instruction = (
        f"Eres un guionista experto en contenido corto para {platform}. "
        f"Tu único trabajo es crear 3 guiones creativos y originales para {business}. Responde únicamente con el objeto JSON solicitado."
    )
    
    # 3. Prompt de la solicitud del usuario
    user_prompt = f"""
    Crea 3 guiones creativos y originales de aproximadamente {duration} segundos cada uno.
    El objetivo es: {goal}.
    El tono debe ser {tone}.
    
    Debes estructurar tu respuesta EXCLUSIVAMENTE como un arreglo JSON de 3 objetos, siguiendo el esquema proporcionado.
    """

    # 4. Configuración pasada como un DICCIONARIO
    generation_config = {
        "system_instruction": system_instruction,
        "response_mime_type": "application/json",
        "response_schema": json_schema
    }

    # 5. Llamada a la API (CORRECCIÓN FINAL: config se pasa a generate_content, no a GenerativeModel)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    response = model.generate_content(
        user_prompt, 
        config=generation_config # <-- El argumento 'config' se mueve aquí.
    )
    
    # Devolver el texto crudo y el objeto Python parseado
    return response.text, json.loads(response.text)
