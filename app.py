import streamlit as st
import json
from db import is_usage_allowed_and_record, save_lead
from ai import generar_guiones_gemini
from google.api_core.exceptions import NotFound 
import os
import re

# --- CONFIGURACIÓN DE LÍMITES Y ADMINISTRADOR ---
# Define la cantidad máxima de guiones GRATUITOS (1 generación = 3 guiones)
MAX_FREE_GENERATIONS = 1 
# Tu correo para hacer bypass a la validación. ¡Asegúrate de definir ADMIN_EMAIL como variable de entorno!
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "musclev@hotmail.com")

# Función de normalización de email para prevenir "fuzzing" (ej: añadir puntos o '+' sub-direcciones)
def normalize_email(email):
    """Normaliza el email para evitar bypass por variación (puntos y sub-direcciones)."""
    email = email.lower().strip()
    
    # Manejar Gmail (quitar puntos y sub-direcciones)
    if email.endswith(('@gmail.com', '@googlemail.com')):
        parts = email.split('@')
        local_part = parts[0]
        domain = '@' + parts[1]
        
        # 1. Quitar el sub-direcionamiento (todo después del primer '+')
        if '+' in local_part:
            local_part = local_part.split('+')[0]
            
        # 2. Quitar todos los puntos
        local_part = local_part.replace('.', '')
        
        email = local_part + domain
        
    # Para otros correos, solo quitar el sub-direcionamiento
    elif '+' in email:
        parts = email.split('@')
        local_part = parts[0]
        domain = '@' + parts[1]
        local_part = local_part.split('+')[0]
        email = local_part + domain
        
    return email

st.set_page_config(page_title="Asistente Virtual - Active Medios", page_icon="🎥", layout="wide")

st.title("🎬 Generador de Guiones Virtual de Active Medios")
st.markdown("Te ayudaré a crear guiones irresistibles para tus Reels, Shorts o TikToks ✨")

# Diseño responsivo para el formulario
col1, col2 = st.columns([1, 1])

with st.form("lead_form"):
    
    with col1:
        st.header("1. Tus Datos")
        name = st.text_input("👤 Tu nombre completo", key="name_input")
        email = st.text_input("📧 Tu correo electrónico", key="email_input")
        business = st.text_input("🏢 Nombre de tu negocio o marca", key="business_input")

    with col2:
        st.header("2. Detalles del Video")
        platform = st.selectbox("📱 ¿Dónde publicarás tu video?", ["Reel", "TikTok", "Short"], key="platform_select")
        duration = st.slider("🎞 Duración aproximada (segundos):", 5, 60, 30, key="duration_slider")
        goal = st.text_input("🎯 ¿Cuál es el objetivo del video? (Ej: Vender un curso, generar interacción, educar)", key="goal_input")
        tone = st.selectbox("🎭 Elige el tono del guion:", ["Divertido", "Profesional", "Emotivo", "Inspirador", "Urgente"], key="tone_select")
    
    # Botón de envío fuera de las columnas
    st.markdown("---")
    submitted = st.form_submit_button("🚀 Generar mis 3 guiones gratis", use_container_width=True)

if submitted:
    if name and email and business and goal:
        
        # Normalizar el email para la validación de uso
        normalized_email = normalize_email(email)
        
        # --- LÓGICA DE VALIDACIÓN Y BYPASS ---
        # Se normaliza también el ADMIN_EMAIL para una comparación correcta
        is_admin = (normalized_email == normalize_email(ADMIN_EMAIL))
        
        # Intentar verificar/registrar uso si no es admin
        if not is_admin:
            try:
                # La función de DB comprueba el límite y, si es permitido, incrementa el contador
                allowed = is_usage_allowed_and_record(normalized_email, MAX_FREE_GENERATIONS)
            except Exception as e:
                # Si la DB falla, se permite la generación para no bloquear al usuario, pero se advierte.
                st.warning(f"⚠️ Error al verificar la base de datos. Se permitirá la generación temporalmente. Detalle: {e}")
                allowed = True 
        else:
            allowed = True
            st.info("🟢 Acceso de administrador detectado. Generación permitida.")

        if not allowed:
            st.error("🔒 Límite de uso gratuito alcanzado para este correo. ¡Contrata el servicio completo para generar guiones ilimitados!")
            st.markdown(f"[📲 Contratar servicio completo de Active Medios](https://wa.me/573185538833?text=Hola,%20quiero%20generar%20m%C3%A1s%20guiones!)")
            st.stop()
        # --- FIN LÓGICA DE VALIDACIÓN ---
        
        # 1. Guardar el Lead (Solo datos, el conteo ya se hizo)
        try:
            save_lead(name, normalized_email, business, platform, duration, goal, tone)
        except Exception as e:
            st.warning(f"⚠️ Atención: No pudimos guardar tus datos en la base de datos (Error DB). Pero, ¡tus guiones se generarán igual! Detalle: {e}")
            
        # 2. Generar Guiones con IA
        with st.spinner("✨ Creando tus guiones personalizados con IA..."):
            try:
                # La función devuelve el texto crudo (no usado) y los datos parseados
                _, guiones_data = generar_guiones_gemini(platform, duration, goal, tone, business)

                st.success("¡Listo! Aquí tienes tus guiones 👇")
                
                # Mostrar los guiones de forma estructurada e interactiva
                for i, guion in enumerate(guiones_data):
                    st.subheader(f"Guion #{i+1}: {guion.get('Titulo', 'Guion sin título')}")
                    
                    st.markdown(f"**Gancho (Hook):** *{guion.get('Hook', 'N/A')}*")
                    st.markdown(f"**Desarrollo Visual:** {guion.get('Desarrollo', 'N/A')}")
                    st.markdown(f"**Llamada a la Acción (CTA):** {guion.get('CTA', 'N/A')}")
                    
                    st.info(f"**Caption Sugerido (Con Hashtags):** {guion.get('Caption', 'N/A')}")
                    st.markdown("---") 

                # CTA Final del servicio
                st.markdown(f"### ¿Necesitas que lo editemos por ti?")
                st.markdown(f"**¡Haz clic aquí para contratar el servicio completo de edición!**")
                st.markdown(f"[📲 Enviar mi idea por WhatsApp a Active Medios](https://wa.me/573185538833?text=Hola%20soy%20{name}%20de%20{business}.%20Me%20encant%C3%B3%20el%20guion%20generado%20para%20{platform}%20y%20quiero%20cotizar%20la%20edici%C3%B3n%20del%20video!)")
                
            except NotFound as e:
                st.error("❌ Error de Conexión de IA: No se pudo encontrar el modelo (Gemini API Key inválida o modelo no disponible). Por favor, verifica tu clave GEMINI_API_KEY.")
            except json.JSONDecodeError:
                st.error("❌ Error de Formato: La IA no devolvió el formato JSON esperado. Por favor, intenta de nuevo con otro objetivo o duración. (La IA pudo haber añadido texto extra a la respuesta).")
            except Exception as e:
                st.error(f"❌ Ocurrió un error inesperado al generar los guiones. Intenta de nuevo. Detalle: {e}")

    else:
        st.warning("Por favor completa todos los campos obligatorios antes de generar tus guiones (Nombre, Email, Negocio, Objetivo).")
