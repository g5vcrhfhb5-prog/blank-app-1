import numpy as np
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

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
    if f"{key_base}_sl" not in st.session_state:
        st.session_state[f"{key_base}_sl"] = default_val
    if f"{key_base}_num" not in st.session_state:
        st.session_state[f"{key_base}_num"] = default_val

    def sync_from_slider():
        st.session_state[f"{key_base}_num"] = st.session_state[f"{key_base}_sl"]
        
    def sync_from_num():
        st.session_state[f"{key_base}_sl"] = st.session_state[f"{key_base}_num"]

    st.markdown(f"**{label}**")
    col1, col2 = st.columns([3, 1]) 
    
    with col1:
        st.slider(
            label, min_value=min_val, max_value=max_val, step=step_val,
            key=f"{key_base}_sl", on_change=sync_from_slider, label_visibility="collapsed"
        )
    with col2:
        st.number_input(
            label, min_value=min_val, max_value=max_val, step=step_val,
            key=f"{key_base}_num", on_change=sync_from_num, label_visibility="collapsed"
        )
    return st.session_state[f"{key_base}_num"]


# Títulos
st.markdown('<div class="main-title">DISEÑO DE COSTANERAS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">INGRESO DE DATOS</div>', unsafe_allow_html=True)

# Organización en dos columnas principales
col_inputs, col_visual = st.columns([1.2, 1.8], gap="large")

with col_inputs:
    st.markdown("### 📥 Parámetros de Entrada")

    with st.container(border=True):
        st.markdown("#### **1. Geometría de la Estructura**")
        
        sep_costaneras = synced_slider_number(
            "Separación de costaneras [m]", 0.1, 5.0, 1.5, 0.1, "sep_cost"
        )
        dist_marcos = synced_slider_number(
            "Distancia entre marcos [m]", 1.0, 20.0, 6.0, 0.5, "dist_marc"
        )
        ancho_estructura = synced_slider_number(
            "Ancho de estructura [m]", 1.0, 40.0, 10.0, 0.5, "ancho_est"
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
        st.markdown("Haz clic en cualquier punto del mapa de Chile para establecer la ubicación y altitud.")
        
        m = folium.Map(location=[-33.4569, -70.6482], zoom_start=5)
        m.add_child(folium.LatLngPopup())
        
        map_data = st_folium(m, height=350, use_container_width=True, returned_objects=["last_clicked"])
        
        latitud = -33.4569
        longitud = -70.6482
        altitud_mapa = 500.0
        
        if map_data and map_data.get("last_clicked"):
            latitud = map_data["last_clicked"]["lat"]
            longitud = map_data["last_clicked"]["lng"]
            
            try:
                url = f"https://api.open-meteo.com/v1/elevation?latitude={latitud}&longitude={longitud}"
                resp = requests.get(url).json()
                altitud_mapa = resp['elevation'][0]
            except Exception:
                altitud_mapa = 0.0
            
        c_lat, c_lon = st.columns(2)
        c_lat.info(f"**Latitud:** {latitud:.4f}°")
        c_lon.info(f"**Longitud:** {longitud:.4f}°")

        modo_altitud = st.radio(
            "Origen de la Altitud", 
            ["Extraer del Mapa", "Ingreso Manual"], 
            horizontal=True
        )
        
        if modo_altitud == "Extraer del Mapa":
            altitud = st.number_input(
                "Altitud extraída [m.s.n.m]", value=float(altitud_mapa), disabled=True
            )
        else:
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

        span = ancho_estructura  
        height = span * (pendiente_i / 100.0) / 2.0  

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, span / 2, span], y=[0, height, 0], mode="lines+markers", name="Perfil de Cubierta", line=dict(color="#4B8BBE", width=4), marker=dict(size=8)))
        fig.add_trace(go.Scatter(x=[0, span], y=[0, 0], mode="lines", name="Línea de Base", line=dict(color="gray", width=2, dash="dash")))

        fig.update_layout(
            title=f"Perfil Transversal del Techo (Pendiente: {pendiente_i}%)", 
            xaxis_title="Ancho de estructura [m]", 
            yaxis_title="Altura [m]", 
            template="plotly_dark", 
            height=320, 
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- ESQUEMA 2: Distribución de Costaneras ---
    with st.container(border=True):
        st.markdown("**Esquema 2: Modulación y Espaciamiento de Costaneras**")

        # Separación horizontal real proyectada
        sep_x = sep_costaneras * np.cos(np.radians(angulo_techo))
        
        # Generar posiciones desde el alero (x=0) hacia la cumbrera (x=span/2)
        x_left = np.arange(0, span / 2, sep_x).tolist()
        
        # Asegurar costaneras en la cumbrera (a 10 cm del eje central)
        offset_cumbrera = 0.10
        pos_cumbrera_izq = (span / 2) - offset_cumbrera
        
        # Reemplazar la última costanera si solapa, si no, agregarla
        if len(x_left) > 0 and (pos_cumbrera_izq - x_left[-1]) < 0.20:
            x_left[-1] = pos_cumbrera_izq
        else:
            x_left.append(pos_cumbrera_izq)
            
        x_left = np.array(x_left)
        y_left = (2 * height / span) * x_left
        
        # Reflejar para el lado derecho
        x_right = span - x_left
        y_right = y_left
        
        # Unir ambos lados
        x_costaneras = np.concatenate((x_left, x_right[::-1]))
        y_costaneras = np.concatenate((y_left, y_right[::-1]))

        fig_mod = go.Figure()
        fig_mod.add_trace(go.Scatter(x=x_costaneras, y=y_costaneras, mode="markers", name="Posición de Costaneras", marker=dict(color="orange", size=10, symbol="square")))
        fig_mod.add_trace(go.Scatter(x=[0, span / 2, span], y=[0, height, 0], mode="lines", name="Pendiente", line=dict(color="gray", width=2)))

        fig_mod.update_layout(
            title=f"Distribución Modulada (Separación de Costaneras: {sep_costaneras} m)", 
            xaxis_title="Ancho de estructura [m]", 
            yaxis_title="Altura [m]", 
            template="plotly_dark", 
            height=280, 
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_mod, use_container_width=True)
