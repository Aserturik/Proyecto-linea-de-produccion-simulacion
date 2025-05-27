#!/usr/bin/env python3
"""Script de debug para verificar los datos que recibe Streamlit"""

from event_driven_simulation import SimulacionLineaProduccion

def main():
    print("=== DEBUG STREAMLIT: Verificando datos de la simulación ===")
    
    # Crear simulación con parámetros simples
    simulacion = SimulacionLineaProduccion(
        sim_time=60,  # 1 hora
        buffer1_capacity=1000,
        buffer2_capacity=50,
        m1_media_tiempo=2.0,
        m1_std_dev_tiempo=0.5,
        m2_media_tiempo=30.0,
        m2_std_dev_tiempo=5.0,
        m3_media_tiempo=15.0,
        m3_std_dev_tiempo=3.0,
        defect_prob=0.05,
        random_seed=12345
    )
    
    print("Ejecutando simulación...")
    results = simulacion.ejecutar_simulacion()
    
    print("\n=== CLAVES DISPONIBLES EN RESULTS ===")
    for key in sorted(results.keys()):
        value = results[key]
        if isinstance(value, list) and len(value) > 0:
            print(f"{key}: lista con {len(value)} elementos - primer elemento: {value[0]}")
        else:
            print(f"{key}: {value}")
    
    print("\n=== VERIFICANDO ACCESO AL ACUMULADOR ===")
    
    # Verificar acceso directo al objeto simulación
    if hasattr(simulacion, 'acumulador_caramelos'):
        print(f"simulacion.acumulador_caramelos: {len(simulacion.acumulador_caramelos)} elementos")
        print(f"Contenido: {simulacion.acumulador_caramelos[:5]}...")  # Mostrar primeros 5
    else:
        print("ERROR: simulacion.acumulador_caramelos NO EXISTE")
    
    # Verificar datos del acumulador en results
    acumulador_data = results.get('acumulador_caramelos_data', [])
    print(f"results['acumulador_caramelos_data']: {len(acumulador_data)} elementos")
    if acumulador_data:
        print(f"Primeros elementos: {acumulador_data[:5]}")
        print(f"Últimos elementos: {acumulador_data[-5:]}")
    
    print("\n=== VERIFICANDO COLAS FINALES ===")
    if hasattr(simulacion, 'cola1'):
        print(f"Cola 1 final: {len(simulacion.cola1)} elementos")
    if hasattr(simulacion, 'cola2'):
        print(f"Cola 2 final: {len(simulacion.cola2)} elementos")
    if hasattr(simulacion, 'cola3'):
        print(f"Cola 3 final: {len(simulacion.cola3)} elementos")
    
    print("\n=== VERIFICANDO ESTADOS DE MÁQUINAS ===")
    if hasattr(simulacion, 'estado_m1'):
        print(f"Estado M1: {simulacion.estado_m1}")
    if hasattr(simulacion, 'estado_m2'):
        print(f"Estado M2: {simulacion.estado_m2}")
    if hasattr(simulacion, 'estado_m3'):
        print(f"Estado M3: {simulacion.estado_m3}")

if __name__ == "__main__":
    main()
