import google.generativeai as genai
import os
import json
import re

# NOTA IMPORTANTE: Esta es la solución de MÁXIMA COMPATIBILIDAD.
# No se usa el argumento 'config' ni se importa ninguna clase de 'types'
# para evitar los errores de compatibilidad en entornos de Streamlit Cloud con SDKs antiguos.
# La generación estructurada se fuerza a través de instrucciones estrictas en el prompt y
# se limpia el texto de la respuesta antes de intentar el parseo JSON.

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generar_guiones_gemini(platform, duration, goal, tone, business):
    
    # 1. System Instruction para guiar a la IA
    system_instruction = (
        f"Eres un guionista experto en contenido corto para {platform}. "
        f"Tu único trabajo es crear 3 guiones creativos y originales para {business}. "
        f"Tu respuesta DEBE ser ÚNICAMENTE el arreglo JSON, sin preámbulos, explicaciones o texto adicional."
    )
    
    # 2. Definición del formato JSON (incluido en el prompt para guiar al modelo)
    json_format_description = """
    El formato de salida debe ser un arreglo JSON con 3 objetos, cada uno con 5 claves:
    1. "Titulo" (string): Un título corto y atractivo.
    2. "Hook" (string): El texto o la acción de inicio (máximo 5 segundos).
    3. "Desarrollo" (string): 3 ideas visuales o acciones clave, separadas por puntos.
    4. "CTA" (string): La llamada a la acción final, clara y atractiva.
    5. "Caption" (string): El texto completo del caption con 5 a 7 hashtags integrados.
    """

    # 3. Prompt de la solicitud del usuario
    user_prompt = f"""
    Instrucciones de formato: {json_format_description}

    Crea 3 guiones creativos y originales de aproximadamente {duration} segundos cada uno.
    El objetivo es: {goal}.
    El tono debe ser {tone}.
    
    Responde ÚNICAMENTE con el arreglo JSON.
    """

    # 4. Llamada a la API (Sin argumento 'config' para máxima compatibilidad)
    model = genai.GenerativeModel(
        "gemini-2.5-flash", 
        system_instruction=system_instruction # Pasamos system_instruction aquí.
    )
    
    response = model.generate_content(user_prompt)
    raw_text = response.text

    # 5. LIMPIEZA DE TEXTO (para solucionar el JSONDecodeError)
    cleaned_text = raw_text.strip()
    
    # Expresión regular para encontrar el bloque JSON (busca el primer '[' hasta el último ']')
    json_match = re.search(r'\[.*\]', cleaned_text, re.DOTALL)

    if json_match:
        # Si encuentra un bloque JSON válido (el arreglo), lo usa
        json_string = json_match.group(0)
    else:
        # Si no lo encuentra, intenta quitar las envolturas comunes de markdown
        json_string = cleaned_text.replace("```json", "").replace("```", "").strip()

    # Devolver el texto crudo y el objeto Python parseado
    return raw_text, json.loads(json_string)
