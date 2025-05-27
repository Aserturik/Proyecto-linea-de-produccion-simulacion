import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import norm  # Para la PDF de la distribución normal
from event_driven_simulation import SimulacionLineaProduccion

# Default simulation parameters
DEFAULT_SIM_TIME = 24 * 60  # 24 horas en minutos
DEFAULT_BUFFER1_CAPACITY = 1000 * 50
DEFAULT_BUFFER2_CAPACITY = 1000

# Parámetros para Distribución Normal por defecto
DEFAULT_M1_MEDIA_TIEMPO = 2.0  # minutos por caramelo
DEFAULT_M1_STD_DEV_TIEMPO = 0.5  # minutos
DEFAULT_M2_MEDIA_TIEMPO = 30.0  # minutos por caja
DEFAULT_M2_STD_DEV_TIEMPO = 5.0  # minutos
DEFAULT_M3_MEDIA_TIEMPO = 15.0  # minutos por caja
DEFAULT_M3_STD_DEV_TIEMPO = 3.0  # minutos

DEFAULT_DEFECT_PROB = 0.02
DEFAULT_RANDOM_SEED = 12345

st.set_page_config(layout="wide")

st.title("🏭 Simulación de Línea de Producción de Caramelos (Event-Driven)")
st.markdown("""
Esta aplicación permite simular una línea de producción de caramelos usando un enfoque basado en eventos.
Los tiempos de proceso de las máquinas ahora siguen una **Distribución Normal**.
Ajusta los parámetros de la simulación en la barra lateral y haz clic en 'Ejecutar Simulación'.
""")

# Sidebar for parameters
st.sidebar.header("⚙️ Parámetros de Simulación")

sim_time = st.sidebar.number_input(
    "Tiempo de Simulación (minutos)", min_value=1, value=DEFAULT_SIM_TIME, step=60)
buffer1_capacity = st.sidebar.number_input(
    "Capacidad Buffer 1 (caramelos)", min_value=1, value=DEFAULT_BUFFER1_CAPACITY, step=100)
buffer2_capacity = st.sidebar.number_input(
    "Capacidad Buffer 2 (cajas)", min_value=1, value=DEFAULT_BUFFER2_CAPACITY, step=10)

st.sidebar.subheader("Parámetros de Tiempos de Proceso (Distribución Normal)")

# --- Máquina 1 ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Máquina 1 (Producción Caramelos)**")
m1_media_tiempo = st.sidebar.number_input("M1: Media Tiempo Proceso (min/caramelo)",
                                          min_value=0.1, value=DEFAULT_M1_MEDIA_TIEMPO, step=0.1, format="%.2f", key="m1_media")
m1_std_dev_tiempo = st.sidebar.number_input("M1: Desv. Est. Tiempo Proceso (min/caramelo)",
                                            min_value=0.0, value=DEFAULT_M1_STD_DEV_TIEMPO, step=0.05, format="%.2f", key="m1_std")

# --- Máquina 2 ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Máquina 2 (Empaquetado Cajas)**")
m2_media_tiempo = st.sidebar.number_input("M2: Media Tiempo Proceso (min/caja)",
                                          min_value=0.1, value=DEFAULT_M2_MEDIA_TIEMPO, step=0.1, format="%.2f", key="m2_media")
m2_std_dev_tiempo = st.sidebar.number_input("M2: Desv. Est. Tiempo Proceso (min/caja)",
                                            min_value=0.0, value=DEFAULT_M2_STD_DEV_TIEMPO, step=0.1, format="%.2f", key="m2_std")

# --- Máquina 3 ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Máquina 3 (Sellado Cajas)**")
m3_media_tiempo = st.sidebar.number_input("M3: Media Tiempo Proceso (min/caja)",
                                          min_value=0.1, value=DEFAULT_M3_MEDIA_TIEMPO, step=0.1, format="%.2f", key="m3_media")
m3_std_dev_tiempo = st.sidebar.number_input("M3: Desv. Est. Tiempo Proceso (min/caja)",
                                            min_value=0.0, value=DEFAULT_M3_STD_DEV_TIEMPO, step=0.1, format="%.2f", key="m3_std")
st.sidebar.markdown("---")


defect_prob = st.sidebar.slider("Probabilidad de Defecto en M1", min_value=0.0,
                                max_value=1.0, value=DEFAULT_DEFECT_PROB, step=0.001, format="%.3f")
random_seed = st.sidebar.number_input(
    "Semilla Aleatoria", min_value=0, value=DEFAULT_RANDOM_SEED, step=1)

# Visualización de las campanas de Gauss
st.sidebar.header("🔔 Visualización de Distribuciones")


def plot_normal_distribution(mean, std_dev, title):
    if std_dev <= 0:  # La desviación estándar no puede ser cero o negativa para la gráfica
        st.sidebar.warning(
            f"{title}: La desviación estándar debe ser > 0 para graficar.")
        fig = go.Figure()  # Figura vacía
        fig.update_layout(title=title, height=200, showlegend=False)
        return fig

    x_min = mean - 4 * std_dev
    x_max = mean + 4 * std_dev
    # Asegurar que x no sea negativo si media es pequeña
    x = np.linspace(max(0, x_min), x_max, 200)
    y = norm.pdf(x, mean, std_dev)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='PDF'))
    fig.update_layout(
        title=title,
        xaxis_title="Tiempo de Proceso (min)",
        yaxis_title="Densidad de Probabilidad",
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    return fig


st.sidebar.plotly_chart(plot_normal_distribution(
    m1_media_tiempo, m1_std_dev_tiempo, "Distribución M1"), use_container_width=True)
st.sidebar.plotly_chart(plot_normal_distribution(
    m2_media_tiempo, m2_std_dev_tiempo, "Distribución M2"), use_container_width=True)
st.sidebar.plotly_chart(plot_normal_distribution(
    m3_media_tiempo, m3_std_dev_tiempo, "Distribución M3"), use_container_width=True)


# Run simulation button
if st.sidebar.button("🚀 Ejecutar Simulación"):
    # Esta podría ser tu línea 100 aprox.
    st.info(f"Ejecutando simulación con semilla {
            random_seed} por {sim_time} minutos...")

    # ESTA ES LA LLAMADA CORRECTA Y DEBE ESTAR AQUÍ (aprox. línea 101 o 102 en adelante)
    simulacion = SimulacionLineaProduccion(
        sim_time=sim_time,
        buffer1_capacity=buffer1_capacity,
        buffer2_capacity=buffer2_capacity,
        m1_media_tiempo=m1_media_tiempo,
        m1_std_dev_tiempo=m1_std_dev_tiempo,
        m2_media_tiempo=m2_media_tiempo,
        m2_std_dev_tiempo=m2_std_dev_tiempo,
        m3_media_tiempo=m3_media_tiempo,
        m3_std_dev_tiempo=m3_std_dev_tiempo,
        defect_prob=defect_prob,
        random_seed=random_seed
    )
    results = simulacion.ejecutar_simulacion()

    if results:
        st.success("✅ Simulación Finalizada!")

        st.header("📊 Resultados de la Simulación")

        # Métricas principales en columnas
        col1, col2, col3 = st.columns(3)
        col1.metric("🍬 Caramelos Procesados por M1",
                    results.get('producidos_m1', 0))
        col1.metric("🚫 Caramelos Defectuosos (M1)",
                    results.get('defectos_m1', 0))
        col1.metric("✅ Caramelos Buenos a Buffer1",
                    results.get('caramelos_a_buffer1', 0))

        col2.metric("📦 Cajas Empaquetadas (M2)",
                    results.get('cajas_empaquetadas_m2', 0))
        col2.metric("🏷️ Cajas Selladas (M3)",
                    results.get('cajas_selladas_m3', 0))
        col2.metric("⏱️ Throughput (cajas/min)",
                    f"{results.get('throughput_cajas_min', 0):.3f}")

        tiempo_prom_caja = results.get('tiempo_prom_sistema_caja', 0)
        if tiempo_prom_caja == 0 and results.get('cajas_selladas_m3', 0) == 0:
            col3.metric("⏳ Tiempo Prom. Sistema (caja)", "N/A")
        else:
            col3.metric("⏳ Tiempo Prom. Sistema (caja)",
                        f"{tiempo_prom_caja:.2f} min")

        col3.metric("📈 WIP Prom. Buffer 1 (caramelos)", f"{
                    results.get('avg_wip_buffer1', 0):.2f}")
        col3.metric("📉 WIP Prom. Buffer 2 (cajas)", f"{
                    results.get('avg_wip_buffer2', 0):.2f}")

        st.header("📈 Visualizaciones del Sistema")

        # 1. WIP a lo largo del tiempo (subplots)
        fig_wip = make_subplots(rows=2, cols=1,
                                subplot_titles=("Nivel de Buffer 1 (Caramelos)",
                                                "Nivel de Buffer 2 (Cajas)"),
                                vertical_spacing=0.1)

        wip_b1_data = results.get('wip_buffer1_data', [])
        if wip_b1_data:
            df_wip_b1 = pd.DataFrame(wip_b1_data, columns=['Tiempo', 'Nivel'])
            fig_wip.add_trace(
                go.Scatter(x=df_wip_b1['Tiempo'], y=df_wip_b1['Nivel'],
                           name='Buffer 1', line=dict(color='blue')),
                row=1, col=1
            )
            fig_wip.update_yaxes(
                title_text="Cantidad de Caramelos", row=1, col=1)

        wip_b2_data = results.get('wip_buffer2_data', [])
        if wip_b2_data:
            df_wip_b2 = pd.DataFrame(wip_b2_data, columns=['Tiempo', 'Nivel'])
            fig_wip.add_trace(
                go.Scatter(x=df_wip_b2['Tiempo'], y=df_wip_b2['Nivel'],
                           name='Buffer 2', line=dict(color='green')),
                row=2, col=1
            )
            fig_wip.update_yaxes(title_text="Cantidad de Cajas", row=2, col=1)

        fig_wip.update_xaxes(title_text="Tiempo (minutos)", row=2, col=1)
        fig_wip.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig_wip, use_container_width=True)

        # 2. Distribución de tiempos en sistema
        tiempos_sistema = results.get('tiempos_sistema_caja', [])
        if tiempos_sistema:
            fig_tiempos = go.Figure()
            fig_tiempos.add_trace(go.Histogram(
                x=tiempos_sistema,
                name='Tiempo en Sistema',
                nbinsx=30,
                marker_color='purple'
            ))
            fig_tiempos.update_layout(
                title='Distribución de Tiempos en Sistema por Caja',
                xaxis_title='Tiempo (minutos)',
                yaxis_title='Frecuencia',
                showlegend=False  # Era True, pero con un solo trace no es tan necesario
            )
            st.plotly_chart(fig_tiempos, use_container_width=True)

        # --- GRÁFICAS REINCORPORADAS ---

        # 3. Throughput Acumulado (Cajas Selladas M3) - VERSIÓN MEJORADA
        cajas_selladas_tiempo_data = results.get(
            'cajas_selladas_m3_tiempo', [])
        if cajas_selladas_tiempo_data:
            df_throughput = pd.DataFrame(cajas_selladas_tiempo_data, columns=[
                                         'Tiempo', 'Cajas Acumuladas'])
            # Añadir un punto inicial en (0,0) si no existe para que la línea comience desde el origen.
            if not (df_throughput['Tiempo'].iloc[0] == 0 and df_throughput['Cajas Acumuladas'].iloc[0] == 0):
                df_throughput = pd.concat([pd.DataFrame(
                    [{'Tiempo': 0, 'Cajas Acumuladas': 0}]), df_throughput], ignore_index=True)

            # Nombre de variable diferente para evitar colisiones
            fig_throughput_acum = go.Figure()
            fig_throughput_acum.add_trace(go.Scatter(
                x=df_throughput['Tiempo'],
                y=df_throughput['Cajas Acumuladas'],
                mode='lines',  # 'lines+markers' es otra opción
                name='Cajas Selladas Acumuladas',
                line=dict(color='orange')
            ))
            fig_throughput_acum.update_layout(
                title='Throughput Acumulado del Sistema (Cajas Selladas por M3)',
                xaxis_title='Tiempo (minutos)',
                yaxis_title='Número Acumulado de Cajas Selladas',
                showlegend=True
            )
            st.plotly_chart(fig_throughput_acum, use_container_width=True)
        else:
            st.markdown(
                "_(No hay datos de throughput acumulado para mostrar: ninguna caja sellada o datos no registrados)._")

        # 4. Evolución de defectos acumulados
        defectos_tiempo = results.get('defectos_m1_tiempo', [])
        if defectos_tiempo:
            df_defectos = pd.DataFrame(defectos_tiempo, columns=[
                                       "Tiempo", "Defectos Acumulados"])
            if not (df_defectos['Tiempo'].iloc[0] == 0 and df_defectos['Defectos Acumulados'].iloc[0] == 0):
                df_defectos = pd.concat([pd.DataFrame(
                    [{'Tiempo': 0, 'Defectos Acumulados': 0}]), df_defectos], ignore_index=True)

            fig_defectos_acum = go.Figure()
            fig_defectos_acum.add_trace(go.Scatter(
                x=df_defectos["Tiempo"],
                y=df_defectos["Defectos Acumulados"],
                mode='lines',  # 'lines+markers' es otra opción
                name="Defectos acumulados",
                # Color un poco diferente para distinguir
                line=dict(color='crimson')
            ))
            fig_defectos_acum.update_layout(
                title="Evolución Temporal de Defectos Acumulados (M1)",
                xaxis_title="Tiempo (minutos)",
                yaxis_title="Número Acumulado de Defectos"
            )
            st.plotly_chart(fig_defectos_acum, use_container_width=True)

        # Expander para estadísticas detalladas
        with st.expander("📋 Ver Estadísticas Detalladas (Diccionario Completo)"):
            st.json(results)

    else:
        st.error("❌ La simulación falló o no devolvió resultados.")
else:
    st.info("Ajusta los parámetros en la barra lateral y haz clic en 'Ejecutar Simulación' para comenzar.")


st.sidebar.markdown("---")
st.sidebar.markdown(
    "Creado con [Streamlit](https://streamlit.io), [Plotly](https://plotly.com/python/) y [SciPy](https://scipy.org/).")
