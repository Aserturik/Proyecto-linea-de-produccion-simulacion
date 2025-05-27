#!/usr/bin/env python3
"""
Script de debug detallado para verificar la formación de cajas
"""

from event_driven_simulation import SimulacionLineaProduccion

def test_formacion_cajas_debug():
    """Prueba detallada para verificar la formación de cajas."""
    
    # Crear simulación con parámetros que deberían permitir formar cajas
    sim = SimulacionLineaProduccion(
        sim_time=500.0,  # Más tiempo
        buffer1_capacity=60,  # Más capacidad para caramelos
        buffer2_capacity=10,  # Más capacidad para cajas
        m1_media_tiempo=0.5,  # Más rápido
        m1_std_dev_tiempo=0.05,
        m2_media_tiempo=2.0,
        m2_std_dev_tiempo=0.2,
        m3_media_tiempo=1.5,
        m3_std_dev_tiempo=0.15,
        defect_prob=0.05,  # Menos defectos
        random_seed=12345
    )
    
    print("=== Configuración de la Simulación ===")
    print(f"Tiempo de simulación: {sim.sim_time} minutos")
    print(f"Capacidad buffer1 (caramelos): {sim.buffer1_capacity}")
    print(f"Capacidad buffer2 (cajas): {sim.buffer2_capacity}")
    print(f"Caramelos por caja: {sim.caramelos_por_caja}")
    print(f"Probabilidad de defecto: {sim.defect_prob}")
    print(f"M1 tiempo medio: {sim.m1_media_tiempo} min")
    
    # Ejecutar simulación
    print("\n=== Ejecutando Simulación ===")
    resultados = sim.ejecutar_simulacion()
    
    # Mostrar resultados detallados
    print("\n=== Resultados Detallados ===")
    print(f"Caramelos producidos por M1: {resultados['producidos_m1']}")
    print(f"Caramelos defectuosos: {resultados['defectos_m1']}")
    print(f"Caramelos no defectuosos: {resultados['caramelos_a_buffer1']}")
    print(f"Caramelos en acumulador al final: {len(sim.acumulador_caramelos)}")
    print(f"Cajas empaquetadas por M2: {resultados['cajas_empaquetadas_m2']}")
    print(f"Cajas selladas por M3: {resultados['cajas_selladas_m3']}")
    
    # Cálculos teóricos
    caramelos_teoricos_para_cajas = resultados['caramelos_a_buffer1'] // sim.caramelos_por_caja
    print(f"\nCajas teóricamente posibles: {caramelos_teoricos_para_cajas}")
    
    # Estado final de las colas
    print(f"\n=== Estado Final ===")
    print(f"Cola1 (caramelos esperando M1): {len(sim.cola1)}")
    print(f"Cola2 (cajas esperando M2): {len(sim.cola2)}")
    print(f"Cola3 (cajas esperando M3): {len(sim.cola3)}")
    print(f"Estados finales: M1={sim.estado_m1.value}, M2={sim.estado_m2.value}, M3={sim.estado_m3.value}")
    
    # Verificar información del acumulador
    if hasattr(sim.stats, 'acumulador_caramelos_data'):
        max_acumulador = max([x[1] for x in sim.stats['acumulador_caramelos_data']])
        print(f"Máximo de caramelos en acumulador: {max_acumulador}")
    
    if resultados['cajas_selladas_m3'] > 0:
        print(f"Tiempo promedio en sistema: {resultados['tiempo_prom_sistema_caja']:.2f} min")
    
    return resultados

if __name__ == "__main__":
    resultados = test_formacion_cajas_debug()
