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

# Función para generar gráficas de distribución normal
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

# Gráfica de distribución para M1
st.sidebar.plotly_chart(plot_normal_distribution(
    m1_media_tiempo, m1_std_dev_tiempo, "Distribución Normal M1"), use_container_width=True)

# --- Máquina 2 ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Máquina 2 (Empaquetado Cajas)**")
m2_media_tiempo = st.sidebar.number_input("M2: Media Tiempo Proceso (min/caja)",
                                          min_value=0.1, value=DEFAULT_M2_MEDIA_TIEMPO, step=0.1, format="%.2f", key="m2_media")
m2_std_dev_tiempo = st.sidebar.number_input("M2: Desv. Est. Tiempo Proceso (min/caja)",
                                            min_value=0.0, value=DEFAULT_M2_STD_DEV_TIEMPO, step=0.1, format="%.2f", key="m2_std")

# Gráfica de distribución para M2
st.sidebar.plotly_chart(plot_normal_distribution(
    m2_media_tiempo, m2_std_dev_tiempo, "Distribución Normal M2"), use_container_width=True)

# --- Máquina 3 ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Máquina 3 (Sellado Cajas)**")
m3_media_tiempo = st.sidebar.number_input("M3: Media Tiempo Proceso (min/caja)",
                                          min_value=0.1, value=DEFAULT_M3_MEDIA_TIEMPO, step=0.1, format="%.2f", key="m3_media")
m3_std_dev_tiempo = st.sidebar.number_input("M3: Desv. Est. Tiempo Proceso (min/caja)",
                                            min_value=0.0, value=DEFAULT_M3_STD_DEV_TIEMPO, step=0.1, format="%.2f", key="m3_std")

# Gráfica de distribución para M3
st.sidebar.plotly_chart(plot_normal_distribution(
    m3_media_tiempo, m3_std_dev_tiempo, "Distribución Normal M3"), use_container_width=True)
st.sidebar.markdown("---")


defect_prob = st.sidebar.slider("Probabilidad de Defecto en M1", min_value=0.0,
                                max_value=1.0, value=DEFAULT_DEFECT_PROB, step=0.001, format="%.3f")
random_seed = st.sidebar.number_input(
    "Semilla Aleatoria", min_value=0, value=DEFAULT_RANDOM_SEED, step=1)

# Visualización de la distribución de Bernoulli
st.sidebar.header("🎲 Distribución de Bernoulli (Defectos)")

# Sección explicativa sobre Bernoulli
st.sidebar.markdown(f"""
**Uso en la simulación:** La distribución de Bernoulli se utiliza en la **Máquina 1 (M1)** para determinar si un caramelo producido es defectuoso o no.

**Parámetro actual:** p = {defect_prob:.3f}
""")

# Gráfica simple de Bernoulli
def plot_bernoulli_distribution(p):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Bueno', 'Defectuoso'],
        y=[1-p, p],
        marker_color=['green', 'red'],
        name='Probabilidad'
    ))
    fig.update_layout(
        title=f"Distribución de Bernoulli (p = {p:.3f})",
        xaxis_title="Resultado",
        yaxis_title="Probabilidad",
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    return fig

st.sidebar.plotly_chart(plot_bernoulli_distribution(defect_prob), use_container_width=True)

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
        
        # Columna 1: Producción de Caramelos (M1)
        col1.metric("🍬 Caramelos Producidos por M1",
                    results.get('producidos_m1', 0))
        col1.metric("🚫 Caramelos Defectuosos",
                    results.get('defectos_m1', 0))
        col1.metric("✅ Caramelos Buenos",
                    results.get('caramelos_a_buffer1', 0))
        
        # Mostrar eficiencia de M1
        if results.get('producidos_m1', 0) > 0:
            eficiencia_m1 = (1 - results.get('defectos_m1', 0) / results.get('producidos_m1', 1)) * 100
            col1.metric("📊 Eficiencia M1", f"{eficiencia_m1:.1f}%")

        # Columna 2: Procesamiento de Cajas (M2 y M3)
        col2.metric("📦 Cajas Empaquetadas (M2)",
                    results.get('cajas_empaquetadas_m2', 0))
        col2.metric("🏷️ Cajas Selladas (M3)",
                    results.get('cajas_selladas_m3', 0))
        col2.metric("⏱️ Throughput (cajas/min)",
                    f"{results.get('throughput_cajas_min', 0):.4f}")
        
        # Caramelos en acumulador (nueva métrica)
        acumulador_final = len(simulacion.acumulador_caramelos) if hasattr(simulacion, 'acumulador_caramelos') else 0
        col2.metric("🧮 Caramelos en Acumulador", acumulador_final)

        # Columna 3: Tiempos y WIP
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
        
        # Nuevas métricas de conversión
        caramelos_buenos = results.get('caramelos_a_buffer1', 0)
        cajas_teoricas = caramelos_buenos // 50 if caramelos_buenos > 0 else 0
        col3.metric("🎯 Cajas Teóricamente Posibles", cajas_teoricas)

        st.header("📈 Visualizaciones del Sistema")

        # Resumen de Estado Final del Sistema
        st.subheader("🎯 Estado Final del Sistema")
        col_estado1, col_estado2, col_estado3, col_estado4 = st.columns(4)
        
        # Estado de las colas al final
        cola1_final = len(simulacion.cola1) if hasattr(simulacion, 'cola1') else 0
        cola2_final = len(simulacion.cola2) if hasattr(simulacion, 'cola2') else 0
        cola3_final = len(simulacion.cola3) if hasattr(simulacion, 'cola3') else 0
        acumulador_final = len(simulacion.acumulador_caramelos) if hasattr(simulacion, 'acumulador_caramelos') else 0
        
        col_estado1.metric("🔄 Cola 1 (Caramelos → M1)", cola1_final)
        col_estado2.metric("📦 Cola 2 (Cajas → M2)", cola2_final)
        col_estado3.metric("🏷️ Cola 3 (Cajas → M3)", cola3_final)
        col_estado4.metric("🧮 Acumulador Caramelos", acumulador_final)
        
        # Estados de las máquinas al final
        if hasattr(simulacion, 'estado_m1'):
            estados_finales = f"M1: {simulacion.estado_m1.value} | M2: {simulacion.estado_m2.value} | M3: {simulacion.estado_m3.value}"
            st.info(f"**Estados Finales de Máquinas:** {estados_finales}")

        # 1. WIP y Acumulador a lo largo del tiempo (3 subplots)
        fig_wip = make_subplots(rows=3, cols=1,
                                subplot_titles=("Nivel de Buffer 1 (Caramelos esperando M1)",
                                                "Nivel de Buffer 2 (Cajas esperando M2)",
                                                "Acumulador de Caramelos (para formar cajas)"),
                                vertical_spacing=0.08)

        wip_b1_data = results.get('wip_buffer1_data', [])
        if wip_b1_data:
            df_wip_b1 = pd.DataFrame(wip_b1_data, columns=['Tiempo', 'Nivel'])
            fig_wip.add_trace(
                go.Scatter(x=df_wip_b1['Tiempo'], y=df_wip_b1['Nivel'],
                           name='Buffer 1', line=dict(color='blue')),
                row=1, col=1
            )
            fig_wip.update_yaxes(
                title_text="Caramelos", row=1, col=1)

        wip_b2_data = results.get('wip_buffer2_data', [])
        if wip_b2_data:
            df_wip_b2 = pd.DataFrame(wip_b2_data, columns=['Tiempo', 'Nivel'])
            fig_wip.add_trace(
                go.Scatter(x=df_wip_b2['Tiempo'], y=df_wip_b2['Nivel'],
                           name='Buffer 2', line=dict(color='green')),
                row=2, col=1
            )
            fig_wip.update_yaxes(title_text="Cajas", row=2, col=1)

        # Nueva gráfica del acumulador
        acumulador_data = results.get('acumulador_caramelos_data', [])
        if acumulador_data:
            df_acumulador = pd.DataFrame(acumulador_data, columns=['Tiempo', 'Nivel'])
            fig_wip.add_trace(
                go.Scatter(x=df_acumulador['Tiempo'], y=df_acumulador['Nivel'],
                           name='Acumulador', line=dict(color='orange')),
                row=3, col=1
            )
            fig_wip.update_yaxes(title_text="Caramelos", row=3, col=1)
            
            # Línea horizontal en y=50 para mostrar el límite para formar caja
            fig_wip.add_hline(y=50, line_dash="dash", line_color="red", 
                             annotation_text="Límite para formar caja (50)", row=3, col=1)

        fig_wip.update_xaxes(title_text="Tiempo (minutos)", row=3, col=1)
        fig_wip.update_layout(height=800, showlegend=True)
        st.plotly_chart(fig_wip, use_container_width=True)

        # Nueva visualización: Flujo de Conversión de Unidades
        st.subheader("🔄 Flujo de Conversión: Caramelos → Cajas")
        
        # Crear diagrama de flujo con métricas
        col_flujo1, col_flujo2, col_flujo3, col_flujo4 = st.columns(4)
        
        caramelos_producidos = results.get('producidos_m1', 0)
        caramelos_defectuosos = results.get('defectos_m1', 0)
        caramelos_buenos = results.get('caramelos_a_buffer1', 0)
        cajas_empaquetadas = results.get('cajas_empaquetadas_m2', 0)
        cajas_selladas = results.get('cajas_selladas_m3', 0)
        
        # Calcular caramelos utilizados en cajas (incluyendo las que están en cola2)
        cajas_totales_formadas = cajas_empaquetadas + cola2_final
        caramelos_en_cajas = cajas_totales_formadas * 50
        
        with col_flujo1:
            st.metric("🏭 M1: Caramelos Producidos", caramelos_producidos)
            if caramelos_producidos > 0:
                st.caption(f"❌ Defectuosos: {caramelos_defectuosos} ({caramelos_defectuosos/caramelos_producidos*100:.1f}%)")
                st.caption(f"✅ Buenos: {caramelos_buenos} ({caramelos_buenos/caramelos_producidos*100:.1f}%)")
        
        with col_flujo2:
            st.metric("📦 Formación de Cajas", f"{cajas_totales_formadas}")
            st.caption(f"🧮 Caramelos utilizados: {caramelos_en_cajas}")
            st.caption(f"⏳ Caramelos pendientes: {acumulador_final}")
        
        with col_flujo3:
            st.metric("🏭 M2: Cajas Empaquetadas", cajas_empaquetadas)
            if cola2_final > 0:
                st.caption(f"⏳ En cola M2: {cola2_final}")
        
        with col_flujo4:
            st.metric("🏭 M3: Cajas Selladas", cajas_selladas)
            if cola3_final > 0:
                st.caption(f"⏳ En cola M3: {cola3_final}")
        
        # Verificación de balance
        if caramelos_buenos > 0:
            balance_ok = (caramelos_en_cajas + acumulador_final) == caramelos_buenos
            balance_text = "✅ Balance Correcto" if balance_ok else "❌ Error en Balance"
            st.info(f"**Verificación de Conservación:** {balance_text} - Total caramelos buenos: {caramelos_buenos} = En cajas: {caramelos_en_cajas} + En acumulador: {acumulador_final}")

        # --- GRÁFICAS REINCORPORADAS ---

        # 2. Throughput Acumulado (Cajas Selladas M3) - VERSIÓN MEJORADA
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

        # 3. Evolución de defectos acumulados
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
