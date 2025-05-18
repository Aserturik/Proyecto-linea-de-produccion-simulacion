import sys
import os
import simpy
import math

# Add the 'aleatorios' directory to sys.path
# This allows importing 'test_random_quality' and ensures its internal imports work
# (e.g., 'from src.modelos...' will resolve to 'aleatorios/src/modelos...')
current_script_dir = os.path.dirname(os.path.abspath(__file__))
aleatorios_dir_path = os.path.join(current_script_dir, 'aleatorios')
if aleatorios_dir_path not in sys.path:
    sys.path.insert(0, aleatorios_dir_path)

# Now we can import from test_random_quality
# The RandomTester class needs its own imports (numpy, tabulate, matplotlib, src.modelos...) 
# to be resolved correctly. Adding aleatorios_dir_path to sys.path handles 'src.modelos...'.
# The user needs to ensure numpy, tabulate, and matplotlib are installed.
try:
    # from test_random_quality import RandomTester # Old import
    from src.modelos.validated_random import ValidatedRandom # New import
except ImportError as e:
    print(f"Error importing ValidatedRandom: {e}")
    print("Please ensure that the 'aleatorios/src/modelos/validated_random.py' file exists and all dependencies are installed.")
    print("Expected structure includes: ./aleatorios/src/modelos/validated_random.py")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during import: {e}")
    sys.exit(1)

# Default simulation parameters (can be overridden when calling run_simulation)
DEFAULT_SIM_TIME = 24 * 60
DEFAULT_BUFFER1_CAPACITY = 1000 * 50
DEFAULT_BUFFER2_CAPACITY = 1000
DEFAULT_M1_MEAN_TIME = 2.0
DEFAULT_M2_MEAN_TIME = 30.0
DEFAULT_M3_MEAN_TIME = 15.0
DEFAULT_DEFECT_PROB = 0.02
DEFAULT_RANDOM_SEED = 12345

# --- Custom Random Variate Generation ---
def custom_expovariate(rt_instance, mean_time):
    """Genera un valor de una distribución exponencial usando rt_instance.random()."""
    if mean_time <= 0:
        raise ValueError("El tiempo medio para custom_expovariate debe ser positivo.")
    # Asume que rt_instance.random() devuelve U(0,1)
    u = rt_instance.random()
    if u == 0:  # Evitar math.log(0)
        u = 1e-9 # Un número muy pequeño pero positivo
    return -math.log(u) * mean_time

# --- SimPy Processes (Máquinas) ---
# Note: stats is now passed as an argument
def maquina1(env, rt_instance, buffer1_resource, m1_mean_time_param, defect_prob_param, stats_dict):
    """M1: Genera caramelos y los envía a Buffer1 (con posibles defectos)."""
    while True:
        processing_time = custom_expovariate(rt_instance, m1_mean_time_param)
        yield env.timeout(processing_time)
        
        stats_dict['producidos_m1'] += 1
        if rt_instance.random() > defect_prob_param:
            try:
                yield buffer1_resource.put(1)
                stats_dict['caramelos_a_buffer1'] += 1
            except simpy.Interrupt:
                raise
            except Exception: # Handles container full if not using Interrupts for that
                # print(f"{env.now:.2f}: M1 - Buffer1 lleno. Caramelo perdido o M1 bloqueada.")
                pass # Simpy Container handles blocking automatically.
        else:
            stats_dict['defectos_m1'] += 1

def maquina2(env, rt_instance, buffer1_resource, buffer2_store, m2_mean_time_param, stats_dict):
    """M2: Toma 50 caramelos de Buffer1, empaqueta y envía caja a Buffer2."""
    while True:
        # Espera a tener 50 caramelos
        # yield buffer1_resource.get(50) # simpy.Container handles capacity checks
        try:
            yield buffer1_resource.get(50)
        except simpy.Interrupt:
            raise
        except Exception: # Handles container empty if not using Interrupts
            # This part should ideally not be reached if M1 feeds it.
            # print(f"{env.now:.2f}: M2 - Esperando caramelos en Buffer1.")
            pass # Simpy Container handles waiting automatically.


        processing_time = custom_expovariate(rt_instance, m2_mean_time_param)
        yield env.timeout(processing_time)
        
        caja_id = stats_dict['cajas_empaquetadas_m2']
        # yield buffer2_store.put({'id': caja_id, 'entrada_buffer2': env.now})
        try:
            yield buffer2_store.put({'id': caja_id, 'entrada_buffer2': env.now})
            stats_dict['cajas_empaquetadas_m2'] += 1
        except simpy.Interrupt:
            raise
        except Exception: # Handles store full
            # print(f"{env.now:.2f}: M2 - Buffer2 lleno. Caja perdida o M2 bloqueada.")
            pass # Simpy Store handles blocking automatically.


def maquina3(env, rt_instance, buffer2_store, m3_mean_time_param, stats_dict):
    """M3: Toma cajas de Buffer2, las sella y calcula métricas."""
    while True:
        # caja_data = yield buffer2_store.get()
        try:
            caja_data = yield buffer2_store.get()
        except simpy.Interrupt:
            raise
        except Exception: # Handles store empty
            # print(f"{env.now:.2f}: M3 - Esperando cajas en Buffer2.")
            pass # Simpy Store handles waiting automatically.

        
        processing_time = custom_expovariate(rt_instance, m3_mean_time_param)
        yield env.timeout(processing_time)
        
        stats_dict['cajas_selladas_m3'] += 1
        tiempo_en_sistema = env.now - caja_data['entrada_buffer2']
        stats_dict['tiempos_sistema_caja'].append(tiempo_en_sistema)

# --- Monitoring Process ---
# Note: stats is now passed as an argument
def monitor_buffers_levels(env, buffer1_resource, buffer2_store, stats_dict, sampling_interval=10):
    """Monitoriza y registra los niveles de los buffers periódicamente."""
    # Muestra inicial en t=0
    stats_dict['wip_buffer1_data'].append((env.now, buffer1_resource.level))
    stats_dict['wip_buffer2_data'].append((env.now, len(buffer2_store.items)))
    
    while True:
        yield env.timeout(sampling_interval)
        stats_dict['wip_buffer1_data'].append((env.now, buffer1_resource.level))
        stats_dict['wip_buffer2_data'].append((env.now, len(buffer2_store.items)))

# --- Helper for Statistics Calculation ---
def calculate_time_weighted_average(data_points, total_duration):
    """Calcula el promedio ponderado en el tiempo para una serie de (tiempo, valor)."""
    if not data_points or total_duration == 0:
        return 0.0

    weighted_sum = 0.0
    for i in range(len(data_points)):
        current_time, current_level = data_points[i]
        duration_at_current_level = 0.0

        if i + 1 < len(data_points):
            next_time, _ = data_points[i+1]
            duration_at_current_level = next_time - current_time
        else:
            # Último punto de datos, su nivel se mantiene hasta total_duration
            if current_time <= total_duration:
                 duration_at_current_level = total_duration - current_time
        
        if duration_at_current_level < 0: # Seguridad, no debería ocurrir
            duration_at_current_level = 0

        weighted_sum += current_level * duration_at_current_level
        
    return weighted_sum / total_duration if total_duration > 0 else 0.0

# --- Main Simulation Function (Refactored) ---
def run_simulation(
    sim_time_param=DEFAULT_SIM_TIME,
    buffer1_cap_param=DEFAULT_BUFFER1_CAPACITY,
    buffer2_cap_param=DEFAULT_BUFFER2_CAPACITY,
    m1_mean_time_param=DEFAULT_M1_MEAN_TIME,
    m2_mean_time_param=DEFAULT_M2_MEAN_TIME,
    m3_mean_time_param=DEFAULT_M3_MEAN_TIME,
    defect_prob_param=DEFAULT_DEFECT_PROB,
    random_seed_param=DEFAULT_RANDOM_SEED
):
    """Ejecuta la simulación de la línea de producción con parámetros configurables."""

    # Initialize statistics dictionary for this run
    current_stats = {
        'producidos_m1': 0,
        'defectos_m1': 0,
        'caramelos_a_buffer1': 0,
        'cajas_empaquetadas_m2': 0,
        'cajas_selladas_m3': 0,
        'tiempos_sistema_caja': [], # Tiempo en sistema para cajas (desde entrada a Buffer2 hasta sellado)
        'wip_buffer1_data': [],  # Tuplas (tiempo, nivel) para Buffer1
        'wip_buffer2_data': []   # Tuplas (tiempo, nivel) para Buffer2
    }

    rt_instance = None
    try:
        # ASUNCIÓN CRÍTICA: RandomTester(sample_size) devuelve una instancia
        # con un método .random() que retorna un número U(0,1).
        # rt_instance = RandomTester(sample_size=sample_size_for_tester) # Old instantiation
        rt_instance = ValidatedRandom(seed=random_seed_param)
        print("Usando ValidatedRandom con seed=" + str(random_seed_param) + " para la simulación.")

        # Verificar si el método .random() existe para dar un error temprano si no.
        if not hasattr(rt_instance, 'random') or not callable(rt_instance.random):
            print("Error: La instancia de ValidatedRandom no tiene un método 'random()' callable.")
            return None # Indicate failure
            
    except Exception as e:
        print(f"Error inicializando ValidatedRandom: {e}")
        print("Asegúrese que 'aleatorios.src.modelos.validated_random.ValidatedRandom' se puede instanciar y provee un método '.random()'.")
        return None # Indicate failure

    # Entorno de SimPy
    env = simpy.Environment()

    # Crear Buffers
    buffer1 = simpy.Container(env, init=0, capacity=buffer1_cap_param)
    buffer2 = simpy.Store(env, capacity=buffer2_cap_param) # Store para items con atributos

    # Iniciar procesos de las máquinas y el monitor
    env.process(maquina1(env, rt_instance, buffer1, m1_mean_time_param, defect_prob_param, current_stats))
    env.process(maquina2(env, rt_instance, buffer1, buffer2, m2_mean_time_param, current_stats))
    env.process(maquina3(env, rt_instance, buffer2, m3_mean_time_param, current_stats))
    env.process(monitor_buffers_levels(env, buffer1, buffer2, current_stats, sampling_interval=sim_time_param/100)) # Muestrear 100 veces

    # Ejecutar la simulación
    print(f"Iniciando simulación por {sim_time_param} minutos...")
    env.run(until=sim_time_param)
    print("Simulación finalizada.")

    # --- Calculate Results ---
    results = {}
    results['raw_stats'] = current_stats.copy() # Store the collected stats

    results['throughput_cajas_min'] = current_stats['cajas_selladas_m3'] / sim_time_param if sim_time_param > 0 else 0

    if current_stats['tiempos_sistema_caja']:
        results['tiempo_prom_sistema_caja'] = sum(current_stats['tiempos_sistema_caja']) / len(current_stats['tiempos_sistema_caja'])
    else:
        results['tiempo_prom_sistema_caja'] = 0 # Or 'N/A' - handle in UI

    # Ensure last data point for WIP calculation
    if current_stats['wip_buffer1_data'] and current_stats['wip_buffer1_data'][-1][0] < sim_time_param:
         current_stats['wip_buffer1_data'].append((sim_time_param, current_stats['wip_buffer1_data'][-1][1]))
    elif not current_stats['wip_buffer1_data'] and sim_time_param >= 0: # Handle empty data case
         current_stats['wip_buffer1_data'].append((0, 0)) # Start with 0 level at t=0
         if sim_time_param > 0 : current_stats['wip_buffer1_data'].append((sim_time_param, 0))


    if current_stats['wip_buffer2_data'] and current_stats['wip_buffer2_data'][-1][0] < sim_time_param:
         current_stats['wip_buffer2_data'].append((sim_time_param, current_stats['wip_buffer2_data'][-1][1]))
    elif not current_stats['wip_buffer2_data'] and sim_time_param >=0: # Handle empty data case
         current_stats['wip_buffer2_data'].append((0, 0)) # Start with 0 level at t=0
         if sim_time_param > 0 : current_stats['wip_buffer2_data'].append((sim_time_param, 0))
            
    results['avg_wip_buffer1'] = calculate_time_weighted_average(current_stats['wip_buffer1_data'], sim_time_param)
    results['avg_wip_buffer2'] = calculate_time_weighted_average(current_stats['wip_buffer2_data'], sim_time_param)
    
    # Add all individual stats to results for easier access in Streamlit
    results.update(current_stats)

    return results

if __name__ == '__main__':
    print("Ejecutando simulación con parámetros por defecto...")
    # Use the default parameters defined at the top of the file
    simulation_results = run_simulation(
        sim_time_param=DEFAULT_SIM_TIME,
        buffer1_cap_param=DEFAULT_BUFFER1_CAPACITY,
        buffer2_cap_param=DEFAULT_BUFFER2_CAPACITY,
        m1_mean_time_param=DEFAULT_M1_MEAN_TIME,
        m2_mean_time_param=DEFAULT_M2_MEAN_TIME,
        m3_mean_time_param=DEFAULT_M3_MEAN_TIME,
        defect_prob_param=DEFAULT_DEFECT_PROB,
        random_seed_param=DEFAULT_RANDOM_SEED
    )

    if simulation_results:
        print("--- Resultados de la Simulación (desde __main__) ---")
        print(f"Intentos de producción de caramelos (M1): {simulation_results['producidos_m1']}")
        print(f"Caramelos defectuosos (M1): {simulation_results['defectos_m1']}")
        print(f"Caramelos buenos enviados a Buffer1: {simulation_results['caramelos_a_buffer1']}")
        print(f"Cajas empaquetadas (M2): {simulation_results['cajas_empaquetadas_m2']}")
        print(f"Cajas selladas (M3): {simulation_results['cajas_selladas_m3']}")
        print(f"Throughput (cajas selladas por minuto): {simulation_results['throughput_cajas_min']:.3f}")
        if simulation_results['tiempos_sistema_caja']:
             print(f"Tiempo promedio en sistema por caja: {simulation_results['tiempo_prom_sistema_caja']:.2f} min")
        else:
             print(f"Tiempo promedio en sistema por caja: N/A (no se sellaron cajas)")
        print(f"WIP promedio en Buffer1 (caramelos): {simulation_results['avg_wip_buffer1']:.2f}")
        print(f"WIP promedio en Buffer2 (cajas): {simulation_results['avg_wip_buffer2']:.2f}")
        # print(f"WIP Buffer 1 Data: {simulation_results['wip_buffer1_data']}") # For debugging
        # print(f"WIP Buffer 2 Data: {simulation_results['wip_buffer2_data']}") # For debugging
    else:
        print("La simulación no pudo generar resultados.")
