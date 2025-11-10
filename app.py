import streamlit as st
from db import save_lead
from templates import generate_scripts

st.set_page_config(page_title="Asistente Virtual - Active Medios", page_icon="🎥")

st.title("🤖 Asistente Virtual de Active Medios")
st.write("Te ayudaré a crear guiones atractivos para tus Reels, Shorts o TikToks.")

name = st.text_input("Tu nombre:")
platform = st.selectbox("¿Dónde publicarás tu video?", ["Reel", "TikTok", "Short"])
duration = st.slider("Duración (segundos):", 5, 60, 30)
goal = st.text_input("¿Cuál es el objetivo del video?")
tone = st.selectbox("Elige el tono del guion:", ["Divertido", "Profesional", "Emotivo", "Inspirador"])

if st.button("Generar mis guiones"):
    save_lead(name, platform, duration, goal, tone)
    scripts = generate_scripts(platform, duration, goal, tone)
    st.success("Aquí tienes tus ideas 👇")
    for s in scripts:
        st.write(s)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/57TU_NUMERO?text=Hola%20soy%20{name}%20quiero%20mi%20video%20editado%20de%20{platform})")
