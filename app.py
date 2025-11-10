import streamlit as st
from db import save_lead
from ai import generar_guiones_gemini

st.set_page_config(page_title="Asistente Virtual - Active Medios", page_icon="🎥")

st.title("🎬 Asistente Virtual de Active Medios")
st.write("Te ayudaré a crear guiones irresistibles para tus Reels, Shorts o TikToks ✨")

with st.form("lead_form"):
    name = st.text_input("👤 Tu nombre completo")
    email = st.text_input("📧 Tu correo electrónico")
    business = st.text_input("🏢 Nombre de tu negocio o marca")
    platform = st.selectbox("📱 ¿Dónde publicarás tu video?", ["Reel", "TikTok", "Short"])
    duration = st.slider("🎞 Duración aproximada (segundos):", 5, 60, 30)
    goal = st.text_input("🎯 ¿Cuál es el objetivo del video?")
    tone = st.selectbox("🎭 Elige el tono del guion:", ["Divertido", "Profesional", "Emotivo", "Inspirador"])

    submitted = st.form_submit_button("🚀 Generar mis 3 guiones gratis")

if submitted:
    if name and email and business and goal:
        with st.spinner("✨ Creando tus guiones personalizados con IA..."):
            save_lead(name, email, business, platform, duration, goal, tone)
            guiones = generar_guiones_gemini(platform, duration, goal, tone, business)

        st.success("¡Listo! Aquí tienes tus guiones 👇")
        st.markdown(guiones)
        st.markdown(f"[📲 Enviar mi idea por WhatsApp](https://wa.me/573185538833?text=Hola%20soy%20{name}%20quiero%20crear%20mi%20video%20de%20{platform})")

    else:
        st.warning("Por favor completa todos los campos antes de generar tus guiones.")
