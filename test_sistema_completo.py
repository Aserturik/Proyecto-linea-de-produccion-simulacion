#!/usr/bin/env python3
"""
Script de prueba final para la nueva lógica de unidades (caramelos a cajas)
"""

from event_driven_simulation import SimulacionLineaProduccion

def test_sistema_completo():
    """Prueba completa del sistema con parámetros balanceados."""
    
    # Parámetros más balanceados para permitir flujo completo
    sim = SimulacionLineaProduccion(
        sim_time=1000.0,  # Tiempo suficiente
        buffer1_capacity=100,  # Buffer generoso para caramelos
        buffer2_capacity=20,   # Buffer generoso para cajas
        m1_media_tiempo=1.0,   # M1: 1 minuto por caramelo
        m1_std_dev_tiempo=0.1,
        m2_media_tiempo=45.0,  # M2: 45 minutos por caja (50 caramelos)
        m2_std_dev_tiempo=5.0,
        m3_media_tiempo=10.0,  # M3: 10 minutos por caja (sellado)
        m3_std_dev_tiempo=1.0,
        defect_prob=0.05,      # 5% defectos
        random_seed=42
    )
    
    print("=== Configuración del Sistema ===")
    print(f"Tiempo de simulación: {sim.sim_time} minutos")
    print(f"M1: {sim.m1_media_tiempo} min/caramelo")
    print(f"M2: {sim.m2_media_tiempo} min/caja ({sim.caramelos_por_caja} caramelos)")
    print(f"M3: {sim.m3_media_tiempo} min/caja (sellado)")
    print(f"Tasa de defectos: {sim.defect_prob*100}%")
    
    # Cálculos teóricos
    print(f"\n=== Análisis Teórico ===")
    tasa_produccion_m1 = 1.0 / sim.m1_media_tiempo  # caramelos/min
    tasa_produccion_m2 = 1.0 / sim.m2_media_tiempo  # cajas/min
    tasa_produccion_m3 = 1.0 / sim.m3_media_tiempo  # cajas/min
    
    print(f"Tasa M1: {tasa_produccion_m1:.3f} caramelos/min")
    print(f"Tasa M2: {tasa_produccion_m2:.3f} cajas/min")
    print(f"Tasa M3: {tasa_produccion_m3:.3f} cajas/min")
    
    # El cuello de botella debería ser M2 en este caso
    tasa_m1_cajas = tasa_produccion_m1 * (1 - sim.defect_prob) / sim.caramelos_por_caja
    print(f"Tasa M1 equivalente en cajas: {tasa_m1_cajas:.3f} cajas/min")
    
    cuello_botella = min(tasa_m1_cajas, tasa_produccion_m2, tasa_produccion_m3)
    print(f"Cuello de botella teórico: {cuello_botella:.3f} cajas/min")
    
    # Ejecutar simulación
    print(f"\n=== Ejecutando Simulación ===")
    resultados = sim.ejecutar_simulacion()
    
    # Mostrar resultados
    print(f"\n=== Resultados ===")
    print(f"Caramelos producidos: {resultados['producidos_m1']}")
    print(f"Caramelos defectuosos: {resultados['defectos_m1']} ({resultados['defectos_m1']/resultados['producidos_m1']*100:.1f}%)")
    print(f"Caramelos válidos: {resultados['caramelos_a_buffer1']}")
    print(f"Cajas empaquetadas (M2): {resultados['cajas_empaquetadas_m2']}")
    print(f"Cajas selladas (M3): {resultados['cajas_selladas_m3']}")
    
    print(f"\n=== Estado Final ===")
    print(f"Caramelos en acumulador: {len(sim.acumulador_caramelos)}")
    print(f"Cajas en cola M2: {len(sim.cola2)}")
    print(f"Cajas en cola M3: {len(sim.cola3)}")
    
    print(f"\n=== Métricas de Rendimiento ===")
    print(f"Throughput real: {resultados['throughput_cajas_min']:.4f} cajas/min")
    print(f"Eficiencia vs teórico: {resultados['throughput_cajas_min']/cuello_botella*100:.1f}%")
    
    if resultados['tiempos_sistema_caja']:
        print(f"Tiempo promedio en sistema: {resultados['tiempo_prom_sistema_caja']:.1f} min")
    
    # Verificaciones
    print(f"\n=== Verificaciones ===")
    cajas_teoricas = resultados['caramelos_a_buffer1'] // sim.caramelos_por_caja
    print(f"Cajas teóricamente posibles: {cajas_teoricas}")
    print(f"Cajas realmente formadas: {resultados['cajas_empaquetadas_m2'] + len(sim.cola2)}")
    
    # Verificar conservación
    caramelos_en_cajas = (resultados['cajas_empaquetadas_m2'] + len(sim.cola2)) * sim.caramelos_por_caja
    caramelos_en_acumulador = len(sim.acumulador_caramelos)
    total_caramelos_contados = caramelos_en_cajas + caramelos_en_acumulador
    
    print(f"Verificación conservación:")
    print(f"  Caramelos válidos: {resultados['caramelos_a_buffer1']}")
    print(f"  En cajas: {caramelos_en_cajas}")
    print(f"  En acumulador: {caramelos_en_acumulador}")
    print(f"  Total contado: {total_caramelos_contados}")
    print(f"  Balance: {'✅ OK' if total_caramelos_contados == resultados['caramelos_a_buffer1'] else '❌ ERROR'}")
    
    return resultados

if __name__ == "__main__":
    resultados = test_sistema_completo()
