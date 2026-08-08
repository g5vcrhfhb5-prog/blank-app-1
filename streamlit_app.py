import streamlit as st
import pandas as pd
import math

# Configuración de la página
st.set_page_config(page_title="App Diseño Estructural", layout="wide")

st.title("Plataforma de Diseño: Perfiles y Cargas")
st.markdown("Esta aplicación permite evaluar las propiedades geométricas de perfiles de acero conformado en frío y calcular las combinaciones de carga normativas (AISC 360 - ASD).")

# ==========================================
# 1. FUNCIONES DE CÁLCULO DE PERFILES Z
# ==========================================
@st.cache_data
def calcular_propiedades_z(h, b, c, t):
    hw = h - t
    bf = b - t
    cl = c - t/2

    segments = [
        (0, -hw/2, 0, hw/2, t),
        (0, hw/2, bf, hw/2, t),
        (bf, hw/2, bf, hw/2 - cl, t),
        (0, -hw/2, -bf, -hw/2, t),
        (-bf, -hw/2, -bf, -hw/2 + cl, t)
    ]

    A_tot = 0; Ix = 0; Iy = 0
    for x1, y1, x2, y2, th in segments:
        length = math.hypot(x2 - x1, y2 - y1)
        A_tot += length * th
        dx = x2 - x1
        dy = y2 - y1
        Ix += th * length * (y1**2 + y1*dy + (dy**2)/3)
        Iy += th * length * (x1**2 + x1*dx + (dx**2)/3)

    A_cm2 = A_tot / 100.0
    peso = A_cm2 * 0.785
    Ix_cm4 = Ix / 10000.0
    Iy_cm4 = Iy / 10000.0
    Wx_cm3 = Ix_cm4 / (h / 20.0)
    Wy_cm3 = Iy_cm4 / (b / 10.0)
    
    return A_cm2, peso, Ix_cm4, Iy_cm4, Wx_cm3, Wy_cm3

# Base de datos de Perfiles Z
perfiles_z = [
    ("Z 100x50x15x2", 100, 50, 15, 2), ("Z 100x50x15x3", 100, 50, 15, 3),
    ("Z 125x50x15x2", 125, 50, 15, 2), ("Z 125x50x15x3", 125, 50, 15, 3),
    ("Z 150x50x15x2", 150, 50, 15, 2), ("Z 150x50x15x3", 150, 50, 15, 3),
    ("Z 175x75x20x2", 175, 75, 20, 2), ("Z 175x75x20x3", 175, 75, 20, 3),
    ("Z 200x75x20x2", 200, 75, 20, 2), ("Z 200x75x20x3", 200, 75, 20, 3),
    ("Z 250x75x20x2", 250, 75, 20, 2), ("Z 250x75x20x3", 250, 75, 20, 3)
]

datos_z = []
for p in perfiles_z:
    nombre, h, b, c, t = p
    A, peso, Ix, Iy, Wx, Wy = calcular_propiedades_z(h, b, c, t)
    datos_z.append({
        "Perfil": nombre, "H (mm)": h, "B (mm)": b, "t (mm)": t, 
        "Peso (kg/m)": round(peso, 2), "Ix (cm4)": round(Ix, 2), 
        "Iy (cm4)": round(Iy, 2), "Wx (cm3)": round(Wx, 2)
    })
df_z = pd.DataFrame(datos_z)

# ==========================================
# ESTRUCTURA DE LA APP EN PESTAÑAS
# ==========================================
tab1, tab2 = st.tabs(["🏗️ Catálogo de Perfiles", "📊 Análisis de Cargas (ASD)"])

with tab1:
    st.header("Propiedades de Perfiles Conformados en Frío")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Seleccionar Perfil Z")
        perfil_seleccionado = st.selectbox("Elige un perfil:", df_z['Perfil'])
        detalle = df_z[df_z['Perfil'] == perfil_seleccionado].iloc[0]
        
        st.write(f"**Dimensiones:** H={detalle['H (mm)']} mm, B={detalle['B (mm)']} mm, t={detalle['t (mm)']} mm")
        st.write(f"**Peso Lineal:** {detalle['Peso (kg/m)']} kg/m")
        st.write(f"**Inercia X-X ($I_x$):** {detalle['Ix (cm4)']} cm⁴")
        st.write(f"**Inercia Y-Y ($I_y$):** {detalle['Iy (cm4)']} cm⁴")
        st.write(f"**Módulo Resistente ($W_x$):** {detalle['Wx (cm3)']} cm³")
        
    with col2:
        st.subheader("Eficiencia: Peso vs Módulo Resistente ($W_x$)")
        st.scatter_chart(df_z, x="Peso (kg/m)", y="Wx (cm3)", color="Perfil", height=300)
    
    st.dataframe(df_z, use_container_width=True)

with tab2:
    st.header("Cálculo y Combinaciones de Carga (AISC 360 - ASD)")
    
    # Entradas de usuario
    st.subheader("1. Parámetros Geométricos y Cargas Elementales")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        separacion = st.number_input("Separación costaneras (m)", value=1.5, step=0.1)
        luz = st.number_input("Luz de la costanera (m)", value=6.0, step=0.5)
    with c2:
        peso_cubierta = st.number_input("Peso Cubierta (kgf/m²)", value=20.0)
        peso_costanera = st.number_input("Peso Costanera (kgf/m)", value=6.2)
    with c3:
        sobrecarga = st.number_input("Sobrecarga Lr (kgf/m²)", value=50.0)
        nieve = st.number_input("Nieve S (kgf/m²)", value=0.0)
    with c4:
        viento_p = st.number_input("Viento Presión W+ (kgf/m²)", value=52.0)
        viento_s = st.number_input("Viento Succión W- (kgf/m²)", value=-39.0)

    # Cálculo de cargas lineales
    D = (peso_cubierta * separacion) + peso_costanera
    Lr = sobrecarga * separacion
    S = nieve * separacion
    W_pres = viento_p * separacion
    W_succ = viento_s * separacion

    st.write("---")
    st.markdown("### 2. Cargas Lineales sobre la Costanera (kgf/m)")
    cc1, cc2, cc3, cc4 = st.columns(4)
    cc1.metric("Muerta (D)", f"{D:.2f} kgf/m")
    cc2.metric("Sobrecarga (Lr)", f"{Lr:.2f} kgf/m")
    cc3.metric("Nieve (S)", f"{S:.2f} kgf/m")
    cc4.metric("Viento (W+ / W-)", f"{W_pres:.2f} / {W_succ:.2f}")

    # Combinaciones
    st.write("---")
    st.markdown("### 3. Combinaciones Críticas (Factor de Viento = 0.75)")
    
    comb = {
        "ASD 1: D": [D, 0],
        "ASD 2: D + Lr": [D + Lr, 0],
        "ASD 3: D + S": [D + S, 0],
        "ASD 4: D + 0.75W (Presión)": [D + 0.75 * W_pres, 0],
        "ASD 5: D + 0.75W (Succión)": [0, D + 0.75 * W_succ],
        "ASD 6a: D + 0.75Lr + 0.75W+": [D + 0.75 * Lr + 0.75 * W_pres, 0],
        "ASD 6b: D + 0.75Lr + 0.75W-": [0, D + 0.75 * Lr + 0.75 * W_succ],
        "ASD 7: 0.6D + 0.75W (Levantamiento)": [0, 0.6 * D + 0.75 * W_succ],
    }

    df_comb = pd.DataFrame.from_dict(comb, orient='index', columns=['Carga Gravedad (+) [kgf/m]', 'Carga Alzamiento (-) [kgf/m]'])
    
    st.dataframe(df_comb.style.highlight_max(subset=['Carga Gravedad (+) [kgf/m]'], color='lightgreen')
                             .highlight_min(subset=['Carga Alzamiento (-) [kgf/m]'], color='lightcoral'), 
                 use_container_width=True)

    max_pos = df_comb['Carga Gravedad (+) [kgf/m]'].max()
    max_neg = df_comb['Carga Alzamiento (-) [kgf/m]'].min()

    st.success(f"📌 **Carga Crítica de Diseño hacia abajo (Flexión Positiva):** {max_pos:.2f} kgf/m")
    if max_neg < 0:
        st.error(f"⚠️ **Carga Crítica de Alzamiento (Flexión Negativa / Succión):** {max_neg:.2f} kgf/m")
    else:
        st.info("No hay fuerzas netas de alzamiento para estas combinaciones.")
