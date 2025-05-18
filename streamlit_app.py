import streamlit as st
import pandas as pd
import numpy as np # Required by index.py or its submodules

# Import the simulation function and defaults from index.py
# Ensure index.py is in the same directory or Python path
try:
    from index import run_simulation, DEFAULT_SIM_TIME, DEFAULT_BUFFER1_CAPACITY, \
                      DEFAULT_BUFFER2_CAPACITY, DEFAULT_M1_MEAN_TIME, \
                      DEFAULT_M2_MEAN_TIME, DEFAULT_M3_MEAN_TIME, \
                      DEFAULT_DEFECT_PROB, DEFAULT_RANDOM_SEED
except ImportError as e:
    st.error(f"Error importing from index.py: {e}")
    st.error("Asegúrate de que 'index.py' esté en el mismo directorio que 'streamlit_app.py'.")
    st.stop()

st.set_page_config(layout="wide")

st.title("🏭 Simulación de Línea de Producción de Caramelos")
st.markdown("""
Esta aplicación permite simular una línea de producción de caramelos y visualizar sus métricas de rendimiento.
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
    
    results = run_simulation(
        sim_time_param=sim_time,
        buffer1_cap_param=buffer1_capacity,
        buffer2_cap_param=buffer2_capacity,
        m1_mean_time_param=m1_mean_time,
        m2_mean_time_param=m2_mean_time,
        m3_mean_time_param=m3_mean_time,
        defect_prob_param=defect_prob,
        random_seed_param=random_seed
    )

    if results:
        st.success("✅ Simulación Finalizada!")
        
        st.header("📊 Resultados de la Simulación")
        
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

        st.subheader("Inventario en Proceso (WIP) a lo Largo del Tiempo")
        
        # WIP Buffer 1
        wip_b1_data = results.get('wip_buffer1_data', [])
        if wip_b1_data:
            df_wip_b1 = pd.DataFrame(wip_b1_data, columns=['Tiempo', 'Nivel Buffer 1'])
            df_wip_b1.set_index('Tiempo', inplace=True)
            st.line_chart(df_wip_b1['Nivel Buffer 1'])
        else:
            st.caption("No hay datos de WIP para Buffer 1.")

        # WIP Buffer 2
        wip_b2_data = results.get('wip_buffer2_data', [])
        if wip_b2_data:
            df_wip_b2 = pd.DataFrame(wip_b2_data, columns=['Tiempo', 'Nivel Buffer 2'])
            df_wip_b2.set_index('Tiempo', inplace=True)
            st.line_chart(df_wip_b2['Nivel Buffer 2'])
        else:
            st.caption("No hay datos de WIP para Buffer 2.")

        with st.expander("📋 Ver Estadísticas Detalladas (Diccionario Completo)"):
            st.json(results) # Display the full results dictionary

    else:
        st.error("❌ La simulación falló o no devolvió resultados.")
else:
    st.info("Ajusta los parámetros en la barra lateral y haz clic en 'Ejecutar Simulación' para comenzar.")

st.sidebar.markdown("---_" * 3)
st.sidebar.markdown("Creado con [Streamlit](https://streamlit.io) y SimPy.") 