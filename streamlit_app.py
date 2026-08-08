import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Diseño de Costaneras - Panel de Ingreso",
    page_icon="🏗️",
    layout="wide",
)

# Estilos CSS personalizados para una apariencia técnica y profesional (tarjetas, colores corporativos)
st.markdown(
    """
    <style>
    .main-header {
        font-size: 28px;
        color: #1f4e78;
        font-weight: 700;
        text-align: left;
        border-bottom: 2px solid #1f4e78;
        padding-bottom: 5px;
        margin-bottom: 20px;
    }
    .card {
        background-color: #f8f9fa;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .metric-title {
        font-size: 14px;
        color: #555555;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Título Principal
st.markdown(
    '<div class="main-header">MÓDULO DE DISEÑO DE COSTANERAS — INGRESO DE DATOS</div>',
    unsafe_allow_html=True,
)

# Organización en dos columnas principales: Izquierda (Inputs), Derecha (Esquemas y Resumen Gráfico)
col_inputs, col_visual = st.columns([1.2, 1.8], gap="large")

with col_inputs:
  st.markdown("### 📥 Parámetros de Entrada")

  with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # 1. Datos Geométricos
    st.markdown("#### **1. Geometría de la Estructura**")
    sep_costaneras = st.number_input(
        "Separación costaneras (m)", min_value=0.1, value=1.5, step=0.1
    )
    dist_marcos = st.number_input(
        "Distancia entre marcos, Luz (m)", min_value=1.0, value=6.0, step=0.5
    )
    sep_cerchas = st.number_input(
        "Separación entre cerchas (m)", min_value=1.0, value=6.0, step=0.5
    )
    pendiente_i = st.number_input(
        "Pendiente de techo, i (%)", min_value=0.0, value=7.0, step=0.5
    )
    area_total = st.number_input(
        "Área total techo, A ($m^2$)", min_value=1.0, value=1929.0, step=10.0
    )

    # Cálculo automático del ángulo de techo en grados a partir de la pendiente (%)
    angulo_techo = np.degrees(np.arctan(pendiente_i / 100.0))

    st.markdown("---")

    # 2. Emplazamiento y Ubicación
    st.markdown("#### **2. Emplazamiento y Zona**")
    ubicacion_zona = st.selectbox(
        "Ubicación de zona",
        options=[
            "Concón",
            "Valparaíso",
            "Santiago",
            "Concepción",
            "Antofagasta",
            "Puerto Montt",
        ],
    )
    latitud = st.number_input(
        "Latitud de la estructura (°)", min_value=0.0, value=32.0, step=1.0
    )
    altitud = st.number_input(
        "Altitud de la zona (m.s.n.m)", min_value=0.0, value=50.0, step=5.0
    )

    st.markdown("</div>", unsafe_allow_html=True)

with col_visual:
  st.markdown("### 📊 Esquemas Geométricos y Visualización")

  # Contenedor para mostrar métricas clave calculadas de forma limpia
  m1, m2, m3 = st.columns(3)
  m1.metric(
      label="Ángulo Calculado",
      value=f"{angulo_techo:.2f}°",
      delta="Derivado de i%",
  )
  m2.metric(label="Zona Seleccionada", value=ubicacion_zona)
  m3.metric(label="Altitud", value=f"{altitud} m.s.n.m")

  # --- ESQUEMA 1: Representación Gráfica de la Pendiente del Techo ---
  st.markdown(
      "<div class='card'><b>Esquema 1: Inclinación de Cubierta y"
      " Geometría</b></div>",
      unsafe_allow_html=True,
  )

  # Generar coordenadas para graficar la cercha/techo en 2D con Plotly
  span = dist_marcos  # Luz
  height = span * (pendiente_i / 100.0) / 2.0  # Altura a dos aguas

  x_coords = [0, span / 2, span]
  y_coords = [0, height, 0]

  fig = go.Figure()

  # Dibujar la cercha de techo
  fig.add_trace(
      go.Scatter(
          x=x_coords,
          y=y_coords,
          mode="lines+markers",
          name="Perfil de Cubierta",
          line=dict(color="#1f4e78", width=4),
          marker=dict(size=8),
      )
  )

  # Línea de base (suelo de referencia)
  fig.add_trace(
      go.Scatter(
          x=[0, span],
          y=[0, 0],
          mode="lines",
          name="Línea de Base",
          line=dict(color="gray", width=2, dash="dash"),
      )
  )

  fig.update_layout(
      title=f"Perfil Transversal del Techo (Pendiente: {pendiente_i}%)",
      xaxis_title="Luz / Distancia entre marcos (m)",
      yaxis_title="Altura (m)",
      template="plotly_white",
      height=320,
      margin=dict(l=20, r=20, t=40, b=20),
  )

  st.plotly_chart(fig, use_container_width=True)

  # --- ESQUEMA 2: Distribución de Costaneras ---
  st.markdown(
      "<div class='card'><b>Esquema 2: Modulación y Espaciamiento de"
      " Costaneras</b></div>",
      unsafe_allow_html=True,
  )

  # Crear un gráfico esquemático que muestre la separación de costaneras sobre la pendiente
  num_costaneras = int(span / sep_costaneras) if sep_costaneras > 0 else 5
  x_costaneras = np.linspace(0, span, num_costaneras + 1)
  # Alturas proporcionales en triángulo
  y_costaneras = np.where(
      x_costaneras <= span / 2,
      (2 * height / span) * x_costaneras,
      (2 * height / span) * (span - x_costaneras),
  )

  fig_mod = go.Figure()
  fig_mod.add_trace(
      go.Scatter(
          x=x_costaneras,
          y=y_costaneras,
          mode="markers",
          name="Posición de Costaneras",
          marker=dict(color="orange", size=12, symbol="square"),
      )
  )
  fig_mod.add_trace(
      go.Scatter(
          x=[0, span / 2, span],
          y=[0, height, 0],
          mode="lines",
          name="Pendiente",
          line=dict(color="#333333", width=2),
      )
  )

  fig_mod.update_layout(
      title=(
          f"Distribución Modulada (Separación de Costaneras:"
          f" {sep_costaneras} m)"
      ),
      xaxis_title="Ancho de crujía (m)",
      yaxis_title="Altura (m)",
      template="plotly_white",
      height=280,
      margin=dict(l=20, r=20, t=40, b=20),
  )

  st.plotly_chart(fig_mod, use_container_width=True)
