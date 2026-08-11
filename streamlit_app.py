import numpy as np
import pandas as pd
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

# Estilos CSS
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
        margin-top: 30px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- TABLAS NORMATIVAS (BACKEND) ---
tabla_viento_nch = pd.DataFrame({
    "Angulo": [0, 5, 10, 15, 20, 25, 30, 35, 45, 60],
    "Zona_1": [-0.48, -0.47, -0.45, -0.39, -0.38, -0.36, -0.35, -0.35, -0.35, -0.35],
    "Zona_2": [-0.58, -0.58, -0.55, -0.47, -0.45, -0.43, -0.42, -0.42, -0.42, -0.42],
    "Zona_3": [-0.58, -0.58, -0.55, -0.47, -0.45, -0.43, -0.42, -0.42, -0.42, -0.42]
})

# --- FUNCIÓN AUXILIAR ---
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

# ==========================================
# SECCIÓN 1: INGRESO DE DATOS
# ==========================================
st.markdown('<div class="main-title">DISEÑO DE COSTANERAS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">INGRESO DE DATOS</div>', unsafe_allow_html=True)

col_inputs, col_visual = st.columns([1.2, 1.8], gap="large")

with col_inputs:
    with st.container(border=True):
        st.markdown("#### **1. Geometría de la Estructura**")
        
        sep_costaneras = synced_slider_number("Separación de costaneras [m]", 0.1, 5.0, 1.5, 0.1, "sep_cost")
        dist_marcos = synced_slider_number("Distancia entre marcos [m]", 1.0, 20.0, 6.0, 0.5, "dist_marc")
        ancho_estructura = synced_slider_number("Ancho de estructura [m]", 1.0, 40.0, 10.0, 0.5, "ancho_est")
        
        # NUEVO PARÁMETRO: Largo de estructura
        largo_estructura = synced_slider_number("Largo de estructura [m]", 1.0, 100.0, 24.0, 0.5, "largo_est")
        
        sep_cerchas = synced_slider_number("Separación entre cerchas [m]", 1.0, 20.0, 6.0, 0.5, "sep_cerch")
        pendiente_i = synced_slider_number("Pendiente de techo (i) [%]", 0.0, 100.0, 7.0, 0.5, "pend_tech")
        
        # Por ahora lo mantenemos manual, pero pronto podremos calcularlo automáticamente (Área = Ancho * Largo / cos(angulo))
        area_total = st.number_input("Área total techo, A [m²]", min_value=1.0, value=1929.0, step=10.0)

        # Cálculo automático del ángulo
        angulo_techo = np.degrees(np.arctan(pendiente_i / 100.0))

        st.divider()

        st.markdown("#### **2. Emplazamiento y Zona**")
        st.markdown("Haz clic en cualquier punto del mapa de Chile para establecer la ubicación y altitud.")
        
        m = folium.Map(location=[-33.4569, -70.6482], zoom_start=5)
        m.add_child(folium.LatLngPopup())
        
        map_data = st_folium(m, height=350, use_container_width=True, returned_objects=["last_clicked"])
        
        latitud = -33.4569
        longitud = -70.6482
        altitud_mapa = 50.0
        
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

        modo_altitud = st.radio("Origen de la Altitud", ["Extraer del Mapa", "Ingreso Manual"], horizontal=True)
        
        if modo_altitud == "Extraer del Mapa":
            altitud = st.number_input("Altitud extraída [m.s.n.m]", value=float(altitud_mapa), disabled=True)
        else:
            altitud = st.number_input("Altitud de la zona [m.s.n.m]", min_value=0.0, value=50.0, step=5.0)

with col_visual:
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

        fig.update_layout(title=f"Perfil Transversal del Techo (Pendiente: {pendiente_i}%)", xaxis_title="Ancho de estructura [m]", yaxis_title="Altura [m]", template="plotly_dark", height=320, margin=dict(l=20, r=20, t=40, b=20))
        fig.update_yaxes(nticks=12)
        fig.update_xaxes(nticks=15)
        st.plotly_chart(fig, use_container_width=True)

    # --- ESQUEMA 2: Distribución de Costaneras ---
    with st.container(border=True):
        st.markdown("**Esquema 2: Modulación y Espaciamiento de Costaneras**")
        sep_x = sep_costaneras * np.cos(np.radians(angulo_techo))
        x_left = np.arange(0, span / 2, sep_x).tolist()
        offset_cumbrera = 0.10
        pos_cumbrera_izq = (span / 2) - offset_cumbrera
        
        if len(x_left) > 0 and (pos_cumbrera_izq - x_left[-1]) < 0.20:
            x_left[-1] = pos_cumbrera_izq
        else:
            x_left.append(pos_cumbrera_izq)
            
        x_left = np.array(x_left)
        y_left = (2 * height / span) * x_left
        x_right = span - x_left
        y_right = y_left
        x_costaneras = np.concatenate((x_left, x_right[::-1]))
        y_costaneras = np.concatenate((y_left, y_right[::-1]))

        fig_mod = go.Figure()
        fig_mod.add_trace(go.Scatter(x=x_costaneras, y=y_costaneras, mode="markers", name="Posición de Costaneras", marker=dict(color="orange", size=10, symbol="square")))
        fig_mod.add_trace(go.Scatter(x=[0, span / 2, span], y=[0, height, 0], mode="lines", name="Pendiente", line=dict(color="gray", width=2)))

        fig_mod.update_layout(title=f"Distribución Modulada (Separación de Costaneras: {sep_costaneras} m)", xaxis_title="Ancho de estructura [m]", yaxis_title="Altura [m]", template="plotly_dark", height=280, margin=dict(l=20, r=20, t=40, b=20))
        fig_mod.update_yaxes(nticks=12)
        fig_mod.update_xaxes(nticks=15)
        st.plotly_chart(fig_mod, use_container_width=True)

    # --- ESQUEMA 3: Vista en Planta y Modulación de Marcos ---
    with st.container(border=True):
        st.markdown("**Esquema 3: Vista en Planta (Modulación de Marcos)**")
        
        fig_planta = go.Figure()
        
        # Dibujar Perímetro de la nave
        fig_planta.add_trace(go.Scatter(
            x=[0, largo_estructura, largo_estructura, 0, 0],
            y=[0, 0, ancho_estructura, ancho_estructura, 0],
            mode="lines",
            name="Perímetro",
            line=dict(color="gray", width=2, dash="dash")
        ))
        
        # Generar posiciones de los marcos (basados en dist_marcos)
        num_marcos = int(largo_estructura / dist_marcos) if dist_marcos > 0 else 1
        x_marcos = np.linspace(0, largo_estructura, num_marcos + 1)
        
        # Añadir líneas transversales (Cerchas/Marcos)
        for x_m in x_marcos:
            fig_planta.add_trace(go.Scatter(
                x=[x_m, x_m],
                y=[0, ancho_estructura],
                mode="lines+markers",
                showlegend=False,
                line=dict(color="#4B8BBE", width=3),
                marker=dict(size=6, color="#4B8BBE")
            ))
            
        # Añadir un rastro invisible solo para la leyenda
        fig_planta.add_trace(go.Scatter(
            x=[None], y=[None], mode="lines+markers", name="Marcos / Cerchas", 
            line=dict(color="#4B8BBE", width=3), marker=dict(size=6, color="#4B8BBE")
        ))

        fig_planta.update_layout(
            title=f"Planta de Estructura ({largo_estructura} m x {ancho_estructura} m)",
            xaxis_title="Largo de estructura [m]",
            yaxis_title="Ancho de estructura [m]",
            template="plotly_dark",
            height=320,
            margin=dict(l=20, r=20, t=40, b=20),
            yaxis=dict(scaleanchor="x", scaleratio=1), # Proporción real (escala 1:1)
            xaxis=dict(nticks=15)
        )
        
        st.plotly_chart(fig_planta, use_container_width=True)

# ==========================================
# SECCIÓN 2: CÁLCULO DE CARGAS
# ==========================================
st.markdown('<div class="sub-header">CÁLCULO DE CARGAS</div>', unsafe_allow_html=True)

col_cargas_in, col_cargas_out = st.columns([1.2, 1.8], gap="large")

with col_cargas_in:
    with st.expander("🧱 1. Cargas de Peso Propio (Dead)", expanded=False):
        peso_cubierta = st.number_input("Peso propio cubierta [kgf/m²]", min_value=0.0, value=20.0, step=1.0)
        peso_aislacion = st.number_input("Peso aislación [kgf/m²]", min_value=0.0, value=0.0, step=1.0)
        carga_adicional = st.number_input("Carga adicional [kgf/m²]", min_value=0.0, value=0.0, step=1.0)
        peso_costanera_ml = st.number_input("Peso lineal costanera estimada [kgf/m]", min_value=0.0, value=6.67, step=0.1)

    with st.expander("🌧️ 2. Sobrecarga de Techo (Lr)", expanded=False):
        sobrecarga_inicial = st.number_input("Sobrecarga techo inicial, Lo [kgf/m²]", min_value=0.0, value=100.0, step=10.0)
        c1, c2 = st.columns(2)
        red_area = c1.number_input("Reducción por área, R1", min_value=0.0, max_value=1.0, value=0.6, step=0.1)
        red_pendiente = c2.number_input("Reducción por pendiente, R2", min_value=0.0, max_value=1.0, value=0.84, step=0.1)

    with st.expander("❄️ 3. Cargas de Nieve (S)", expanded=False):
        carga_nieve_pg = st.number_input("Carga básica de nieve, pg [kgf/m²]", min_value=0.0, value=25.0, step=5.0)
        c3, c4 = st.columns(2)
        factor_exp_ce = c3.number_input("Factor exposición, Ce", value=1.0, step=0.1)
        factor_term_ct = c4.number_input("Condición térmica, Ct", value=1.0, step=0.1)
        factor_imp_is = st.number_input("Factor de importancia, I (Nieve)", value=1.0, step=0.1)

    with st.expander("💨 4. Cargas de Viento (W)", expanded=True):
        st.markdown("Parámetros y presiones interpoladas automáticamente.")
        c_v1, c_v2 = st.columns(2)
        vel_viento = c_v1.number_input("Velocidad básica, V [m/s]", min_value=0.0, value=35.0, step=1.0)
        cat_exposicion = c_v2.selectbox("Categoría Exposición", options=["B", "C", "D"])
        
        c_v3, c_v4, c_v5 = st.columns(3)
        factor_ajuste_lambda = c_v3.number_input("Factor λ", value=1.56, step=0.01)
        factor_imp_iw = c_v4.number_input("Factor I", value=1.0, step=0.1)
        factor_kzt = c_v5.number_input("Factor Kzt", value=1.0, step=0.1)
        
        st.markdown("---")
        st.markdown(f"**Coeficientes Interpolados para {angulo_techo:.2f}°**")
        
        # INTERPOLACIÓN AUTOMÁTICA DE VIENTO
        presion_z1 = np.interp(angulo_techo, tabla_viento_nch["Angulo"], tabla_viento_nch["Zona_1"])
        presion_z2 = np.interp(angulo_techo, tabla_viento_nch["Angulo"], tabla_viento_nch["Zona_2"])
        presion_z3 = np.interp(angulo_techo, tabla_viento_nch["Angulo"], tabla_viento_nch["Zona_3"])
        
        rz1, rz2, rz3 = st.columns(3)
        rz1.metric("Zona 1", f"{presion_z1:.3f}")
        rz2.metric("Zona 2", f"{presion_z2:.3f}")
        rz3.metric("Zona 3", f"{presion_z3:.3f}")

with col_cargas_out:
    st.info("👈 Ingresa los parámetros de carga a la izquierda. Aquí mostraremos las tablas de presiones finales y diagramas de aplicación de cargas.")
