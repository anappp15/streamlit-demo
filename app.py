import streamlit as st
from pathlib import Path
from utils_map import load_data, process_data, generate_map, VARS_MEAN

# Diccionario de etiquetas amigables
VAR_LABELS = {
    "radiation_pred": "Radiación solar neta (predicción)",
    "Cloud_Cover_Mean_24h": "Cobertura de nubes (24h)",
    "temperature_2m_C": "Temperatura (°C)",
    "relative_humidity": "Humedad relativa (%)",
    "surface_net_solar_radiation_sum": "Radiación solar (observación)",
    "surface_pressure": "Presión superficial (hPa)",
    "total_precipitation_sum": "Precipitación total (mm)",
    "wind_direction": "Dirección del viento (°)",
    "wind_speed": "Velocidad del viento (m/s)",
    "elevation": "Elevación (m)"
}

st.set_page_config(
    page_title="Mapa Solar Panamá",
    layout="wide"
)

# --- HEADER ---
st.title("☀️ Mapa de Radiación Solar y variables climáticas en Panamá")

st.markdown("""
Esta visualización muestra:
- La radiación solar diaria promedio predichos
- Variables climáticas que influyen en la radiación solar
""")

# --- CONTROLES ---
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    regenerate = st.button("🔄 Regenerar datos")

with col2:
    st.metric(label="Fuente", value="Grupo Kointrol.AI")

with col3:
    # Mostrar etiquetas amigables en el dropdown
    variable_label = st.selectbox(
        "Variable a visualizar:",
        list(VAR_LABELS.values()),
        index=list(VAR_LABELS.keys()).index("radiation_pred")  # por defecto radiación
    )
    # Obtener la clave interna correspondiente
    variable = [k for k, v in VAR_LABELS.items() if v == variable_label][0]

# --- GENERACIÓN / CARGA ---
PROJECT_ROOT = Path(__file__).resolve().parent
df, panama_map_data, gdf_bound = load_data(PROJECT_ROOT)
gdf_bound2 = process_data(df, gdf_bound)

with st.spinner("Cargando mapa interactivo..."):
    fig = generate_map(gdf_bound2, panama_map_data, df, variable)

# --- MOSTRAR MAPA ---
st.plotly_chart(fig, width="stretch", height=750)

# --- FOOTER ---
st.markdown("---")
st.caption("Prototipo Streamlit • Plotly + GeoPandas")