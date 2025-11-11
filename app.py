import streamlit as st
from db import save_lead
from ai import generar_guiones_gemini
import json
from google.api_core.exceptions import NotFound # Importar para manejar errores de API específicos

st.set_page_config(page_title="Asistente Virtual - Active Medios", page_icon="🎥", layout="centered")

# --- Estilos de la aplicación ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: 700;
        color: #FF4B4B; /* Un color vibrante para Streamlit */
        text-align: center;
        margin-bottom: 0.5em;
    }
    .stForm {
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #FF4B4B;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #e63946;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🎬 Asistente Virtual de Active Medios</p>', unsafe_allow_html=True)
st.write("Te ayudaré a crear guiones irresistibles para tus Reels, Shorts o TikToks ✨. ¡Comienza a generar leads hoy!")

# --- Formulario de Lead Generation ---
with st.form("lead_form"):
    st.subheader("Paso 1: ¡Cuéntanos sobre tu idea!")
    
    # Datos de Contacto (Lead)
    name = st.text_input("👤 Tu nombre completo", key="name")
    email = st.text_input("📧 Tu correo electrónico", key="email")
    business = st.text_input("🏢 Nombre de tu negocio o marca", key="business")
    
    st.subheader("Paso 2: Especificaciones del Video")
    
    # Parámetros del Script
    platform = st.selectbox("📱 ¿Dónde publicarás tu video?", ["Reel", "TikTok", "Short"], key="platform")
    duration = st.slider("🎞 Duración aproximada (segundos):", 5, 60, 30, key="duration")
    goal = st.text_input("🎯 ¿Cuál es el objetivo del video? (Ej: Vender un curso, generar tráfico al web, etc.)", key="goal")
    tone = st.selectbox("🎭 Elige el tono del guion:", ["Divertido", "Profesional", "Emotivo", "Inspirador", "Intrigante"], key="tone")

    submitted = st.form_submit_button("🚀 Generar mis 3 guiones gratis")

# --- Lógica de Procesamiento ---
if submitted:
    if not (name and email and business and goal):
        st.warning("⚠️ Por favor completa todos los campos de contacto y la meta del video antes de generar tus guiones.")
    else:
        # Intentar primero guardar el lead
        try:
            # La función save_lead tiene manejo de excepciones interno.
            save_lead(name, email, business, platform, duration, goal, tone)
        except Exception:
             # Si falla la BD, imprimimos el error en consola, pero permitimos que la IA continúe
            pass

        # Generar guiones con la IA
        with st.spinner("✨ Creando tus guiones personalizados con IA..."):
            try:
                # La función ahora devuelve el texto crudo y el objeto JSON parseado
                guiones_raw, guiones_data = generar_guiones_gemini(platform, duration, goal, tone, business)
                
                # --- Presentación de Resultados ---
                st.success("¡Listo! Aquí tienes tus 3 guiones irresistiblemente creados con IA. ¡Comencemos a grabar! 👇")
                st.markdown("---")

                if isinstance(guiones_data, list):
                    for i, guion in enumerate(guiones_data):
                        st.markdown(f"### 💡 Guion Sugerido #{i+1}: {guion.get('Titulo', 'Sin título')}")
                        
                        # Usar columns para un layout más limpio
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Gancho (Hook):**")
                            st.write(f"_{guion.get('Hook', 'N/A')}_")
                        with col2:
                            st.markdown(f"**Llamada a la Acción (CTA):**")
                            st.write(f"_{guion.get('CTA', 'N/A')}_")
                        
                        st.markdown(f"**Desarrollo y Acciones Visuales:**")
                        st.info(guion.get('Desarrollo', 'N/A'))
                        
                        st.markdown(f"**📝 Caption con Hashtags:**")
                        st.code(guion.get('Caption', 'N/A'), language='markdown')
                        st.markdown("---") # Separador visual
                else:
                    # En caso de que la IA no devuelva el JSON esperado, mostramos el texto crudo
                    st.warning("La IA no pudo devolver el formato estructurado. Mostrando el texto generado:")
                    st.markdown(guiones_raw)

                # CTA final de servicio
                whatsapp_message = f"Hola, soy {name} de {business}. Me encantaron los guiones que generó el asistente, quiero cotizar la edición del video para {platform}."
                whatsapp_url = f"https://wa.me/573185538833?text={whatsapp_message.replace(' ', '%20').replace('á', '%C3%A1').replace('é', '%C3%A9').replace('í', '%C3%AD').replace('ó', '%C3%B3').replace('ú', '%C3%BA').replace('ñ', '%C3%B1')}"
                st.markdown(f"""
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="{whatsapp_url}" target="_blank">
                            <button style="background-color: #25D366; color: white; font-weight: bold; border-radius: 10px; padding: 12px 25px; border: none; cursor: pointer; font-size: 1.1em;">
                                📲 ¡Sí, quiero cotizar la edición de mi video!
                            </button>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
                
            # Manejo de excepciones de la API de Gemini
            except NotFound as e:
                st.error(f"❌ Error de Conexión de IA (Modelo No Encontrado): Esto sucede si la clave API no es válida o si el modelo ('gemini-2.5-flash') no está accesible. Revisa tu GEMINI_API_KEY. Detalle: {e}")
            except json.JSONDecodeError:
                st.error("❌ Error de Formato: La IA no devolvió el formato JSON esperado. Por favor, intenta de nuevo o contacta al soporte.")
            except Exception as e:
                st.error(f"❌ Ocurrió un error inesperado al generar los guiones. Intenta de nuevo. Detalle: {e}")
