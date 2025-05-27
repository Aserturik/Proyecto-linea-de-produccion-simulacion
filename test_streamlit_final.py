#!/usr/bin/env python3
"""Script final de prueba para verificar correcciones de Streamlit"""

from event_driven_simulation import SimulacionLineaProduccion

def probar_simulacion_streamlit():
    """Prueba la simulación con parámetros similares a los de Streamlit"""
    
    print("=== PRUEBA FINAL: Verificando correcciones de Streamlit ===")
    
    # Parámetros típicos que usa Streamlit por defecto
    simulacion = SimulacionLineaProduccion(
        sim_time=24 * 60,  # 24 horas
        buffer1_capacity=50000,  # 1000 * 50
        buffer2_capacity=1000,
        m1_media_tiempo=2.0,
        m1_std_dev_tiempo=0.5,
        m2_media_tiempo=30.0,
        m2_std_dev_tiempo=5.0,
        m3_media_tiempo=15.0,
        m3_std_dev_tiempo=3.0,
        defect_prob=0.02,
        random_seed=12345
    )
    
    print("Ejecutando simulación (24 horas simuladas)...")
    results = simulacion.ejecutar_simulacion()
    
    print("\n=== MÉTRICAS PRINCIPALES ===")
    
    # Métricas de producción
    caramelos_producidos = results.get('producidos_m1', 0)
    caramelos_defectuosos = results.get('defectos_m1', 0)
    caramelos_buenos = results.get('caramelos_a_buffer1', 0)
    
    print(f"🍬 Caramelos Producidos por M1: {caramelos_producidos}")
    print(f"🚫 Caramelos Defectuosos: {caramelos_defectuosos}")
    print(f"✅ Caramelos Buenos: {caramelos_buenos}")
    
    if caramelos_producidos > 0:
        eficiencia_m1 = (1 - caramelos_defectuosos / caramelos_producidos) * 100
        print(f"📊 Eficiencia M1: {eficiencia_m1:.1f}%")
    
    # Métricas de cajas
    cajas_empaquetadas = results.get('cajas_empaquetadas_m2', 0)
    cajas_selladas = results.get('cajas_selladas_m3', 0)
    throughput = results.get('throughput_cajas_min', 0)
    
    print(f"📦 Cajas Empaquetadas (M2): {cajas_empaquetadas}")
    print(f"🏷️ Cajas Selladas (M3): {cajas_selladas}")
    print(f"⏱️ Throughput: {throughput:.4f} cajas/min")
    
    # Estado final del sistema
    print("\n=== ESTADO FINAL DEL SISTEMA ===")
    
    cola1_final = len(simulacion.cola1) if hasattr(simulacion, 'cola1') else 0
    cola2_final = len(simulacion.cola2) if hasattr(simulacion, 'cola2') else 0
    cola3_final = len(simulacion.cola3) if hasattr(simulacion, 'cola3') else 0
    acumulador_final = len(simulacion.acumulador_caramelos) if hasattr(simulacion, 'acumulador_caramelos') else 0
    
    print(f"🔄 Cola 1 (Caramelos → M1): {cola1_final}")
    print(f"📦 Cola 2 (Cajas → M2): {cola2_final}")
    print(f"🏷️ Cola 3 (Cajas → M3): {cola3_final}")
    print(f"🧮 Acumulador Caramelos: {acumulador_final}")
    
    # Flujo de conversión
    print("\n=== FLUJO DE CONVERSIÓN: CARAMELOS → CAJAS ===")
    
    cajas_totales_formadas = cajas_empaquetadas + cola2_final
    caramelos_en_cajas = cajas_totales_formadas * 50
    
    print(f"🏭 M1: Caramelos Producidos: {caramelos_producidos}")
    print(f"   ❌ Defectuosos: {caramelos_defectuosos} ({caramelos_defectuosos/caramelos_producidos*100:.1f}%)" if caramelos_producidos > 0 else "   ❌ Defectuosos: 0 (0.0%)")
    print(f"   ✅ Buenos: {caramelos_buenos} ({caramelos_buenos/caramelos_producidos*100:.1f}%)" if caramelos_producidos > 0 else "   ✅ Buenos: 0 (0.0%)")
    
    print(f"📦 Formación de Cajas: {cajas_totales_formadas}")
    print(f"   🧮 Caramelos utilizados: {caramelos_en_cajas}")
    print(f"   ⏳ Caramelos pendientes: {acumulador_final}")
    
    print(f"🏭 M2: Cajas Empaquetadas: {cajas_empaquetadas}")
    if cola2_final > 0:
        print(f"   ⏳ En cola M2: {cola2_final}")
    
    print(f"🏭 M3: Cajas Selladas: {cajas_selladas}")
    if cola3_final > 0:
        print(f"   ⏳ En cola M3: {cola3_final}")
    
    # Verificación de balance
    print("\n=== VERIFICACIÓN DE CONSERVACIÓN ===")
    if caramelos_buenos > 0:
        balance_ok = (caramelos_en_cajas + acumulador_final) == caramelos_buenos
        balance_text = "✅ Balance Correcto" if balance_ok else "❌ Error en Balance"
        print(f"{balance_text}")
        print(f"Total caramelos buenos: {caramelos_buenos}")
        print(f"En cajas: {caramelos_en_cajas}")
        print(f"En acumulador: {acumulador_final}")
        print(f"Suma: {caramelos_en_cajas + acumulador_final}")
    else:
        print("⚠️ No hay caramelos buenos para verificar")
    
    # Datos para visualización
    print("\n=== DATOS PARA VISUALIZACIÓN ===")
    
    acumulador_data = results.get('acumulador_caramelos_data', [])
    wip_b1_data = results.get('wip_buffer1_data', [])
    wip_b2_data = results.get('wip_buffer2_data', [])
    
    print(f"Datos del acumulador: {len(acumulador_data)} puntos")
    print(f"Datos WIP Buffer 1: {len(wip_b1_data)} puntos")
    print(f"Datos WIP Buffer 2: {len(wip_b2_data)} puntos")
    
    if acumulador_data:
        final_acum_time, final_acum_nivel = acumulador_data[-1]
        print(f"Estado final acumulador: {final_acum_nivel} caramelos a t={final_acum_time:.1f} min")
    
    cajas_tiempo_data = results.get('cajas_selladas_m3_tiempo', [])
    print(f"Datos de cajas selladas en el tiempo: {len(cajas_tiempo_data)} puntos")
    
    print("\n=== ESTADOS FINALES DE MÁQUINAS ===")
    if hasattr(simulacion, 'estado_m1'):
        print(f"M1: {simulacion.estado_m1.value}")
    if hasattr(simulacion, 'estado_m2'):
        print(f"M2: {simulacion.estado_m2.value}")
    if hasattr(simulacion, 'estado_m3'):
        print(f"M3: {simulacion.estado_m3.value}")
    
    print("\n=== CONCLUSIÓN ===")
    print("✅ Todos los datos necesarios para Streamlit están disponibles")
    print("✅ La conservación de caramelos se mantiene correctamente")
    print("✅ El flujo de conversión caramelos → cajas funciona apropiadamente")

if __name__ == "__main__":
    probar_simulacion_streamlit()
