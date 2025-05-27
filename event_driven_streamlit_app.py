import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from event_driven_simulation import SimulacionLineaProduccion

# Default simulation parameters
DEFAULT_SIM_TIME = 24 * 60  # 24 horas en minutos
DEFAULT_BUFFER1_CAPACITY = 1000 * 50  # 1000 cajas de 50 caramelos
DEFAULT_BUFFER2_CAPACITY = 1000  # 1000 cajas
DEFAULT_M1_MEAN_TIME = 2.0  # minutos por caramelo
DEFAULT_M2_MEAN_TIME = 30.0  # minutos por caja de 50 caramelos
DEFAULT_M3_MEAN_TIME = 15.0  # minutos por caja
DEFAULT_DEFECT_PROB = 0.02  # 2% de defectos
DEFAULT_RANDOM_SEED = 12345

st.set_page_config(layout="wide")

st.title("🏭 Simulación de Línea de Producción de Caramelos (Event-Driven)")
st.markdown("""
Esta aplicación permite simular una línea de producción de caramelos usando un enfoque basado en eventos.
Ajusta los parámetros de la simulación en la barra lateral y haz clic en 'Ejecutar Simulación'.
""")

# Sidebar for parameters
st.sidebar.header("⚙️ Parámetros de Simulación")

sim_time = st.sidebar.number_input("Tiempo de Simulación (minutos)", min_value=1, value=DEFAULT_SIM_TIME, step=60)
buffer1_capacity = st.sidebar.number_input("Capacidad Buffer 1 (caramelos)", min_value=1, value=DEFAULT_BUFFER1_CAPACITY, step=100)
buffer2_capacity = st.sidebar.number_input("Capacidad Buffer 2 (cajas)", min_value=1, value=DEFAULT_BUFFER2_CAPACITY, step=10)

st.sidebar.subheader("Tiempos Medios de Procesamiento (minutos)")
m1_mean_time = st.sidebar.number_input("M1 (por caramelo)", min_value=0.1, value=DEFAULT_M1_MEAN_TIME, step=0.1, format="%.2f")
m2_mean_time = st.sidebar.number_input("M2 (por caja de 50 caramelos)", min_value=1.0, value=DEFAULT_M2_MEAN_TIME, step=1.0, format="%.2f")
m3_mean_time = st.sidebar.number_input("M3 (por caja)", min_value=1.0, value=DEFAULT_M3_MEAN_TIME, step=1.0, format="%.2f")

defect_prob = st.sidebar.slider("Probabilidad de Defecto en M1", min_value=0.0, max_value=1.0, value=DEFAULT_DEFECT_PROB, step=0.001, format="%.3f")
random_seed = st.sidebar.number_input("Semilla Aleatoria", min_value=0, value=DEFAULT_RANDOM_SEED, step=1)

# Run simulation button
if st.sidebar.button("🚀 Ejecutar Simulación"):
    st.info(f"Ejecutando simulación con semilla {random_seed} por {sim_time} minutos...")
    
    # Crear y ejecutar simulación
    simulacion = SimulacionLineaProduccion(
        sim_time=sim_time,
        buffer1_capacity=buffer1_capacity,
        buffer2_capacity=buffer2_capacity,
        m1_mean_time=m1_mean_time,
        m2_mean_time=m2_mean_time,
        m3_mean_time=m3_mean_time,
        defect_prob=defect_prob,
        random_seed=random_seed
    )
    
    results = simulacion.ejecutar_simulacion()

    if results:
        st.success("✅ Simulación Finalizada!")
        
        st.header("📊 Resultados de la Simulación")
        
        # Métricas principales en columnas
        col1, col2, col3 = st.columns(3)
        col1.metric("🍬 Caramelos Producidos (M1)", results.get('producidos_m1', 0))
        col1.metric("🚫 Caramelos Defectuosos (M1)", results.get('defectos_m1', 0))
        col1.metric("✅ Caramelos Buenos a Buffer1", results.get('caramelos_a_buffer1', 0))
        
        col2.metric("📦 Cajas Empaquetadas (M2)", results.get('cajas_empaquetadas_m2', 0))
        col2.metric("🏷️ Cajas Selladas (M3)", results.get('cajas_selladas_m3', 0))
        col2.metric("⏱️ Throughput (cajas/min)", f"{results.get('throughput_cajas_min', 0):.3f}")

        tiempo_prom_caja = results.get('tiempo_prom_sistema_caja', 0)
        if tiempo_prom_caja == 0 and results.get('cajas_selladas_m3', 0) == 0:
            col3.metric("⏳ Tiempo Prom. Sistema (caja)", "N/A")
        else:
            col3.metric("⏳ Tiempo Prom. Sistema (caja)", f"{tiempo_prom_caja:.2f} min")
        
        col3.metric("📈 WIP Prom. Buffer 1 (caramelos)", f"{results.get('avg_wip_buffer1', 0):.2f}")
        col3.metric("📉 WIP Prom. Buffer 2 (cajas)", f"{results.get('avg_wip_buffer2', 0):.2f}")

        # Gráficos mejorados con Plotly
        st.header("📈 Visualizaciones del Sistema")

        # 1. WIP a lo largo del tiempo (subplots)
        fig_wip = make_subplots(rows=2, cols=1, 
                               subplot_titles=("Nivel de Buffer 1 (Caramelos)", 
                                             "Nivel de Buffer 2 (Cajas)"),
                               vertical_spacing=0.1)
        
        # WIP Buffer 1
        wip_b1_data = results.get('wip_buffer1_data', [])
        if wip_b1_data:
            df_wip_b1 = pd.DataFrame(wip_b1_data, columns=['Tiempo', 'Nivel'])
            fig_wip.add_trace(
                go.Scatter(x=df_wip_b1['Tiempo'], y=df_wip_b1['Nivel'],
                          name='Buffer 1', line=dict(color='blue')),
                row=1, col=1
            )
            fig_wip.update_yaxes(title_text="Cantidad de Caramelos", row=1, col=1)
        
        # WIP Buffer 2
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
                showlegend=True
            )
            st.plotly_chart(fig_tiempos, use_container_width=True)

        # 3. Throughput acumulado
        if wip_b2_data:
            df_wip_b2 = pd.DataFrame(wip_b2_data, columns=['Tiempo', 'Nivel'])
            df_wip_b2['Throughput_Acumulado'] = df_wip_b2['Nivel'].cumsum()
            
            fig_throughput = go.Figure()
            fig_throughput.add_trace(go.Scatter(
                x=df_wip_b2['Tiempo'],
                y=df_wip_b2['Throughput_Acumulado'],
                name='Throughput Acumulado',
                line=dict(color='orange')
            ))
            fig_throughput.update_layout(
                title='Throughput Acumulado del Sistema',
                xaxis_title='Tiempo (minutos)',
                yaxis_title='Cajas Procesadas',
                showlegend=True
            )
            st.plotly_chart(fig_throughput, use_container_width=True)

        # 4. Tasa de defectos
        if results.get('producidos_m1', 0) > 0:
            defectos = results.get('defectos_m1', 0)
            buenos = results.get('caramelos_a_buffer1', 0)
            
            fig_defectos = go.Figure(data=[go.Pie(
                labels=['Defectuosos', 'Buenos'],
                values=[defectos, buenos],
                hole=.3,
                marker_colors=['red', 'green']
            )])
            fig_defectos.update_layout(
                title='Distribución de Calidad de Caramelos',
                showlegend=True
            )
            st.plotly_chart(fig_defectos, use_container_width=True)
        
        # 5. Evolución de defectos acumulados
        defectos_tiempo = results.get('defectos_m1_tiempo', [])
        if defectos_tiempo:
            df_defectos = pd.DataFrame(defectos_tiempo, columns=["Tiempo", "Defectos Acumulados"])
            fig_defectos_acum = go.Figure()
            fig_defectos_acum.add_trace(go.Scatter(
                x=df_defectos["Tiempo"],
                y=df_defectos["Defectos Acumulados"],
                mode='lines+markers',
                name="Defectos acumulados",
                line=dict(color='red')
            ))
            fig_defectos_acum.update_layout(
                title="Evolución Temporal de Defectos",
                xaxis_title="Tiempo (minutos)",
                yaxis_title="Número Acumulado de Defectos"
            )
            st.plotly_chart(fig_defectos_acum, use_container_width=True)


        with st.expander("📋 Ver Estadísticas Detalladas (Diccionario Completo)"):
            st.json(results)

    else:
        st.error("❌ La simulación falló o no devolvió resultados.")
else:
    st.info("Ajusta los parámetros en la barra lateral y haz clic en 'Ejecutar Simulación' para comenzar.")

st.sidebar.markdown("---" * 3)
st.sidebar.markdown("Creado con [Streamlit](https://streamlit.io) y [Plotly](https://plotly.com/python/).") 