import streamlit as st
from src.map_generator import generate_and_save_map

st.set_page_config(
    page_title="Mapa Solar Panamá",
    layout="wide"
)

st.title("☀️ Prototipo – Mapa de Radiación Solar en Panamá")

st.markdown("""
Este es un **prototipo funcional** del dashboard.
- Usa datos agregados por **corregimiento**
- Muestra radiación solar estimada
- Cachea el mapa para mayor rendimiento
""")

# --- CONTROLES ---
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    regenerate = st.button("🔄 Regenerar mapa")

with col2:
    st.metric(label="Fuente", value="Predicción + Datos meteorológicos")

# --- GENERACIÓN / CARGA ---
with st.spinner("Cargando mapa interactivo..."):
    html_path = generate_and_save_map(force_regeneration=regenerate)

# --- MOSTRAR MAPA ---
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

st.components.v1.html(
    html_content,
    height=750,
    scrolling=False
)

# --- FOOTER ---
st.markdown("---")
st.caption("Prototipo Streamlit • Plotly + GeoPandas")
