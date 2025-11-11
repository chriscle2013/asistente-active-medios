import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generar_guiones_gemini(platform, duration, goal, tone, business):
    prompt = f"""
    Eres un guionista experto en contenido corto para {platform}.
    Crea 3 guiones creativos y originales de aproximadamente {duration} segundos cada uno.
    El objetivo es: {goal}.
    El tono debe ser {tone}.
    El negocio o marca se llama: {business}.
    
    Cada guion debe incluir:
    - Hook de inicio (máximo 5 segundos)
    - Desarrollo (3 ideas visuales o acciones)
    - CTA final atractivo
    - Texto de caption con hashtags integrados (no listados aparte).
    """

    response = genai.GenerativeModel("gemini-2.5-flash").generate_content(prompt)
    return response.text
