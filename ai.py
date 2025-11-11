import google.generativeai as genai
import os
import json # Importar json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generar_guiones_gemini(platform, duration, goal, tone, business):
    # ... (tu prompt actual)

    prompt = f"""
    Eres un guionista experto en contenido corto para {platform}.
    Crea 3 guiones creativos y originales de aproximadamente {duration} segundos cada uno.
    El objetivo es: {goal}.
    El tono debe ser {tone}.
    El negocio o marca se llama: {business}.
    
    Cada guion debe ser devuelto en formato JSON como un arreglo de 3 objetos, cada uno con las siguientes claves: "Titulo", "Hook", "Desarrollo", "CTA", y "Caption".
    """

    response = genai.GenerativeModel(
        "gemini-2.5-flash", # Usar gemini-2.5-flash
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Titulo": {"type": "string"},
                        "Hook": {"type": "string"},
                        "Desarrollo": {"type": "string"},
                        "CTA": {"type": "string"},
                        "Caption": {"type": "string"}
                    },
                    "required": ["Titulo", "Hook", "Desarrollo", "CTA", "Caption"]
                }
            }
        )
    ).generate_content(prompt)
    
    # Devolver el objeto JSON parseado y el texto original si se necesita
    return response.text, json.loads(response.text)
