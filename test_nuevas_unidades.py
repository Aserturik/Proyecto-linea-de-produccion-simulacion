#!/usr/bin/env python3
"""
Script de prueba para verificar la nueva lógica de unidades (caramelos a cajas)
"""

from event_driven_simulation import SimulacionLineaProduccion

def test_formacion_cajas():
    """Prueba básica para verificar la formación de cajas."""
    
    # Crear simulación con parámetros simples
    sim = SimulacionLineaProduccion(
        sim_time=100.0,
        buffer1_capacity=10,
        buffer2_capacity=5,
        m1_media_tiempo=1.0,
        m1_std_dev_tiempo=0.1,
        m2_media_tiempo=2.0,
        m2_std_dev_tiempo=0.2,
        m3_media_tiempo=1.5,
        m3_std_dev_tiempo=0.15,
        defect_prob=0.1,  # 10% de defectos
        random_seed=12345
    )
    
    print("=== Configuración de la Simulación ===")
    print(f"Tiempo de simulación: {sim.sim_time} minutos")
    print(f"Capacidad buffer1 (caramelos): {sim.buffer1_capacity}")
    print(f"Capacidad buffer2 (cajas): {sim.buffer2_capacity}")
    print(f"Caramelos por caja: {sim.caramelos_por_caja}")
    print(f"Probabilidad de defecto: {sim.defect_prob}")
    
    # Ejecutar simulación
    print("\n=== Ejecutando Simulación ===")
    resultados = sim.ejecutar_simulacion()
    
    # Mostrar resultados
    print("\n=== Resultados ===")
    print(f"Caramelos producidos por M1: {resultados['producidos_m1']}")
    print(f"Caramelos defectuosos: {resultados['defectos_m1']}")
    print(f"Caramelos no defectuosos: {resultados['caramelos_a_buffer1']}")
    print(f"Cajas empaquetadas por M2: {resultados['cajas_empaquetadas_m2']}")
    print(f"Cajas selladas por M3: {resultados['cajas_selladas_m3']}")
    
    # Verificaciones de lógica
    print(f"\n=== Verificaciones ===")
    caramelos_teoricos_en_cajas = resultados['cajas_selladas_m3'] * sim.caramelos_por_caja
    print(f"Caramelos teóricos en cajas selladas: {caramelos_teoricos_en_cajas}")
    
    if resultados['cajas_selladas_m3'] > 0:
        eficiencia = (caramelos_teoricos_en_cajas / resultados['caramelos_a_buffer1']) * 100
        print(f"Eficiencia de conversión: {eficiencia:.2f}%")
    
    print(f"Throughput de cajas: {resultados['throughput_cajas_min']:.4f} cajas/min")
    
    if resultados['tiempos_sistema_caja']:
        print(f"Tiempo promedio en sistema: {resultados['tiempo_prom_sistema_caja']:.2f} min")
    
    # Verificar que la lógica es consistente
    assert resultados['producidos_m1'] >= resultados['caramelos_a_buffer1'], "Error: más caramelos buenos que producidos"
    assert resultados['cajas_empaquetadas_m2'] >= resultados['cajas_selladas_m3'], "Error: más cajas selladas que empaquetadas"
    
    print("\n✅ Todas las verificaciones pasaron!")
    
    return resultados

if __name__ == "__main__":
    resultados = test_formacion_cajas()
