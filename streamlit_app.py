import numpy as np
import plotly.graph_objects as go
import streamlit as st
import folium
from folium.plugins import Geocoder
from streamlit_folium import st_folium

# Configuración de la página web
st.set_page_config(
    page_title="Diseño de Costaneras",
    page_icon="🏗️",
    layout="wide",
)

# Estilos CSS con importación de la fuente Inter Display (Light - 300)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter+Display:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter Display', sans-serif;
        font-weight: 300;
    }
    
    .main-title {
        text-align: center;
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .sub-header {
        font-size: 24px;
        font-weight: 600;
        text-align: left;
        border-bottom: 2px solid #4B8BBE;
        padding-bottom: 5px;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- FUNCIÓN AUXILIAR PARA SINCRONIZAR SLIDER Y CAJA NUMÉRICA ---
def synced_slider_number(label, min_val, max_val, default_val, step_val, key_base):
    # Inicializar el valor en el estado de la sesión si no existe
    if key_base not in st.session_state:
        st.session_state[key_base] = default_val
        
    # Callbacks para actualizar mutuamente los widgets
    def update_from_slider():
        st.session_state[key_base] = st.session_state[f"{key_base}_sl"]
    def update_from_num():
        st.session_state[key_base] = st.session_state[f"{key_base}_num"]

    st.markdown(f"**{label}**")
    col1, col2 = st.columns([3, 1]) # Proporción: Slider toma 3/4, Caja toma 1/4
    
    with col1:
        st.slider(
            label, min_value=min_val, max_value=max_val, step=step_val,
            key=f"{key_base}_sl", value=st.session_state[key_base], 
            on_change=update_from_slider, label_visibility="collapsed"
        )
    with col2:
        st.number_input(
            label, min_value=min_val, max_value=max_val, step=step_val,
            key=f"{key_base}_num", value=st.session_state[key_base], 
            on_change=update_from_num, label_visibility="collapsed"
        )
    return st.session_state[key_base]

# Títulos
st.markdown('<div class="main-title">DISEÑO DE COSTANERAS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">INGRESO DE DATOS</div>', unsafe_allow_html=True)

# Organización en dos columnas principales
col_inputs, col_visual = st.columns([1.2, 1.8], gap="large")

with col_inputs:
    st.markdown("### 📥 Parámetros de Entrada")

    with st.container(border=True):
        # 1. Datos Geométricos (Usando la función sincronizada)
        st.markdown("#### **1. Geometría de la Estructura**")
        
        sep_costaneras = synced_slider_number(
            "Separación de costaneras [m]", 0.1, 5.0, 1.5, 0.1, "sep_cost"
        )
        dist_marcos = synced_slider_number(
            "Distancia entre marcos [m]", 1.0, 20.0, 6.0, 0.5, "dist_marc"
        )
        sep_cerchas = synced_slider_number(
            "Separación entre cerchas [m]", 1.0, 20.0, 6.0, 0.5, "sep_cerch"
        )
        pendiente_i = synced_slider_number(
            "Pendiente de techo (i) [%]", 0.0, 100.0, 7.0, 0.5, "pend_tech"
        )
        
        area_total = st.number_input(
            "Área total techo, A [m²]", min_value=1.0, value=1929.0, step=10.0
        )

        # Cálculo automático del ángulo
        angulo_techo = np.degrees(np.arctan(pendiente_i / 100.0))

        st.divider()

        # 2. Emplazamiento y Ubicación con Mapa Interactivo
        st.markdown("#### **2. Emplazamiento y Zona**")
        st.markdown("Haz clic en el mapa o usa la lupa para buscar tu ciudad. Las coordenadas se extraerán automáticamente.")
        
        # Crear mapa centrado en Chile
        m = folium.Map(location=[-33.4569, -70.6482], zoom_start=5)
        # Agregar barra de búsqueda (Geocoder)
        Geocoder(add_marker=True).add_to(m)
        
        # Renderizar mapa en Streamlit y capturar clics
        map_data = st_folium(m, height=350, use_container_width=True)
        
        # Extraer Latitud y Longitud
        latitud = -33.4569
        longitud = -70.6482
        if map_data and map_data.get("last_clicked"):
            latitud = map_data["last_clicked"]["lat"]
            longitud = map_data["last_clicked"]["lng"]
            
        c_lat, c_lon = st.columns(2)
        c_lat.info(f"**Latitud:** {latitud:.4f}°")
        c_lon.info(f"**Longitud:** {longitud:.4f}°")

        altitud = st.number_input(
            "Altitud de la zona [m.s.n.m]", min_value=0.0, value=50.0, step=5.0
        )

with col_visual:
    st.markdown("### 📊 Esquemas Geométricos y Visualización")

    m1, m2, m3 = st.columns(3)
    m1.metric(label="Ángulo Calculado", value=f"{angulo_techo:.2f}°", delta="Derivado de i%")
    m2.metric(label="Latitud", value=f"{latitud:.2f}°")
    m3.metric(label="Altitud", value=f"{altitud} m.s.n.m")

    # --- ESQUEMA 1: Representación Gráfica de la Pendiente del Techo ---
    with st.container(border=True):
        st.markdown("**Esquema 1: Inclinación de Cubierta y Geometría**")

        span = dist_marcos  
        height = span * (pendiente_i / 100.0) / 2.0  

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, span / 2, span], y=[0, height, 0], mode="lines+markers", name="Perfil de Cubierta", line=dict(color="#4B8BBE", width=4), marker=dict(size=8)))
        fig.add_trace(go.Scatter(x=[0, span], y=[0, 0], mode="lines", name="Línea de Base", line=dict(color="gray", width=2, dash="dash")))

        fig.update_layout(title=f"Perfil Transversal del Techo (Pendiente: {pendiente_i}%)", xaxis_title="Luz / Distancia entre marcos [m]", yaxis_title="Altura [m]", template="plotly_dark", height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # --- ESQUEMA 2: Distribución de Costaneras ---
    with st.container(border=True):
        st.markdown("**Esquema 2: Modulación y Espaciamiento de Costaneras**")

        num_costaneras = int(span / sep_costaneras) if sep_costaneras > 0 else 5
        x_costaneras = np.linspace(0, span, num_costaneras + 1)
        y_costaneras = np.where(x_costaneras <= span / 2, (2 * height / span) * x_costaneras, (2 * height / span) * (span - x_costaneras))

        fig_mod = go.Figure()
        fig_mod.add_trace(go.Scatter(x=x_costaneras, y=y_costaneras, mode="markers", name="Posición de Costaneras", marker=dict(color="orange", size=12, symbol="square")))
        fig_mod.add_trace(go.Scatter(x=[0, span / 2, span], y=[0, height, 0], mode="lines", name="Pendiente", line=dict(color="gray", width=2)))

        fig_mod.update_layout(title=f"Distribución Modulada (Separación de Costaneras: {sep_costaneras} m)", xaxis_title="Ancho de crujía [m]", yaxis_title="Altura [m]", template="plotly_dark", height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_mod, use_container_width=True)
