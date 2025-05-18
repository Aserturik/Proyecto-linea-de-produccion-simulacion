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

# --- Simulation Configuration ---
SIM_TIME = 24 * 60  # 24 horas en minutos
BUFFER1_CAPACITY = 1000 * 50  # Capacidad de Buffer1 en caramelos
BUFFER2_CAPACITY = 1000  # Capacidad de Buffer2 en cajas
M1_MEAN_TIME = 2  # Tiempo medio de M1 por caramelo (minutos)
M2_MEAN_TIME = 30  # Tiempo medio de M2 por caja de 50 caramelos (minutos)
M3_MEAN_TIME = 15  # Tiempo medio de M3 por caja (minutos)
DEFECT_PROB = 0.02  # Probabilidad de defectos en M1 (2%)

# --- Statistics Dictionary ---
stats = {
    'producidos_m1': 0,
    'defectos_m1': 0,
    'caramelos_a_buffer1': 0,
    'cajas_empaquetadas_m2': 0,
    'cajas_selladas_m3': 0,
    'tiempos_sistema_caja': [], # Tiempo en sistema para cajas (desde entrada a Buffer2 hasta sellado)
    'wip_buffer1_data': [],  # Tuplas (tiempo, nivel) para Buffer1
    'wip_buffer2_data': []   # Tuplas (tiempo, nivel) para Buffer2
}

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
def maquina1(env, rt_instance, buffer1_resource):
    """M1: Genera caramelos y los envía a Buffer1 (con posibles defectos)."""
    while True:
        processing_time = custom_expovariate(rt_instance, M1_MEAN_TIME)
        yield env.timeout(processing_time)
        
        stats['producidos_m1'] += 1
        if rt_instance.random() > DEFECT_PROB:  # Usa el generador custom
            # yield buffer1_resource.put(1) # simpy.Container handles capacity checks
            try:
                yield buffer1_resource.put(1)
                stats['caramelos_a_buffer1'] += 1
            except simpy.Interrupt:
                raise
            except Exception: # Handles container full if not using Interrupts for that
                # print(f"{env.now:.2f}: M1 - Buffer1 lleno. Caramelo perdido o M1 bloqueada.")
                pass # Simpy Container handles blocking automatically.
        else:
            stats['defectos_m1'] += 1

def maquina2(env, rt_instance, buffer1_resource, buffer2_store):
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


        processing_time = custom_expovariate(rt_instance, M2_MEAN_TIME)
        yield env.timeout(processing_time)
        
        caja_id = stats['cajas_empaquetadas_m2']
        # yield buffer2_store.put({'id': caja_id, 'entrada_buffer2': env.now})
        try:
            yield buffer2_store.put({'id': caja_id, 'entrada_buffer2': env.now})
            stats['cajas_empaquetadas_m2'] += 1
        except simpy.Interrupt:
            raise
        except Exception: # Handles store full
            # print(f"{env.now:.2f}: M2 - Buffer2 lleno. Caja perdida o M2 bloqueada.")
            pass # Simpy Store handles blocking automatically.


def maquina3(env, rt_instance, buffer2_store):
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

        
        processing_time = custom_expovariate(rt_instance, M3_MEAN_TIME)
        yield env.timeout(processing_time)
        
        stats['cajas_selladas_m3'] += 1
        tiempo_en_sistema = env.now - caja_data['entrada_buffer2']
        stats['tiempos_sistema_caja'].append(tiempo_en_sistema)

# --- Monitoring Process ---
def monitor_buffers_levels(env, buffer1_resource, buffer2_store, sampling_interval=10):
    """Monitoriza y registra los niveles de los buffers periódicamente."""
    # Muestra inicial en t=0
    stats['wip_buffer1_data'].append((env.now, buffer1_resource.level))
    stats['wip_buffer2_data'].append((env.now, len(buffer2_store.items)))
    
    while True:
        yield env.timeout(sampling_interval)
        stats['wip_buffer1_data'].append((env.now, buffer1_resource.level))
        stats['wip_buffer2_data'].append((env.now, len(buffer2_store.items)))

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

# --- Main Simulation Function ---
def main():
    # Configurar el tamaño de muestra para RandomTester (puede venir de args)
    sample_size_for_tester = 1000000  # Un valor grande por defecto
    
    if len(sys.argv) > 1:
        try:
            sample_size_for_tester = int(sys.argv[1])
            print(f"Usando tamaño de muestra personalizado para RandomTester: {sample_size_for_tester}")
        except ValueError:
            print(f"Argumento de tamaño de muestra inválido: '{sys.argv[1]}'. Usando por defecto: {sample_size_for_tester}")
            
    print(f"Inicializando RandomTester con sample_size = {sample_size_for_tester}")
    rt_instance = None
    try:
        # ASUNCIÓN CRÍTICA: RandomTester(sample_size) devuelve una instancia
        # con un método .random() que retorna un número U(0,1).
        # rt_instance = RandomTester(sample_size=sample_size_for_tester) # Old instantiation
        rt_instance = ValidatedRandom(seed=12345) # New instantiation with a fixed seed
        print("Usando ValidatedRandom con seed=12345 para la simulación.")

        # Verificar si el método .random() existe para dar un error temprano si no.
        if not hasattr(rt_instance, 'random') or not callable(rt_instance.random):
            print("Error: La instancia de ValidatedRandom no tiene un método 'random()' callable.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error inicializando ValidatedRandom: {e}")
        print("Asegúrese que 'aleatorios.src.modelos.validated_random.ValidatedRandom' se puede instanciar y provee un método '.random()'.")
        sys.exit(1)

    # Entorno de SimPy
    env = simpy.Environment()

    # Crear Buffers
    buffer1 = simpy.Container(env, init=0, capacity=BUFFER1_CAPACITY)
    buffer2 = simpy.Store(env, capacity=BUFFER2_CAPACITY) # Store para items con atributos

    # Iniciar procesos de las máquinas y el monitor
    env.process(maquina1(env, rt_instance, buffer1))
    env.process(maquina2(env, rt_instance, buffer1, buffer2))
    env.process(maquina3(env, rt_instance, buffer2))
    env.process(monitor_buffers_levels(env, buffer1, buffer2, sampling_interval=SIM_TIME/100)) # Muestrear 100 veces

    # Ejecutar la simulación
    print(f"Iniciando simulación por {SIM_TIME} minutos...")
    env.run(until=SIM_TIME)
    print("Simulación finalizada.")

    # --- Calcular y Mostrar Resultados ---
    print("--- Resultados de la Simulación ---")
    
    print(f"Intentos de producción de caramelos (M1): {stats['producidos_m1']}")
    print(f"Caramelos defectuosos (M1): {stats['defectos_m1']}")
    print(f"Caramelos buenos enviados a Buffer1: {stats['caramelos_a_buffer1']}")
    print(f"Cajas empaquetadas (M2): {stats['cajas_empaquetadas_m2']}")
    print(f"Cajas selladas (M3): {stats['cajas_selladas_m3']}")

    throughput_cajas_min = stats['cajas_selladas_m3'] / SIM_TIME if SIM_TIME > 0 else 0
    print(f"Throughput (cajas selladas por minuto): {throughput_cajas_min:.3f}")

    if stats['tiempos_sistema_caja']:
        tiempo_prom_sistema_caja = sum(stats['tiempos_sistema_caja']) / len(stats['tiempos_sistema_caja'])
        print(f"Tiempo promedio en sistema por caja (Buffer2 entrada -> M3 salida): {tiempo_prom_sistema_caja:.2f} min")
    else:
        print("Tiempo promedio en sistema por caja: N/A (no se sellaron cajas)")

    # Calcular WIP promedio usando datos del monitor
    # Asegurar que el último estado del monitor se considera hasta SIM_TIME
    # (Esto se maneja en calculate_time_weighted_average si el último punto está antes de SIM_TIME)
    if stats['wip_buffer1_data'][-1][0] < SIM_TIME:
         stats['wip_buffer1_data'].append((SIM_TIME, stats['wip_buffer1_data'][-1][1]))
    if stats['wip_buffer2_data'][-1][0] < SIM_TIME:
         stats['wip_buffer2_data'].append((SIM_TIME, stats['wip_buffer2_data'][-1][1]))
            
    avg_wip_buffer1 = calculate_time_weighted_average(stats['wip_buffer1_data'], SIM_TIME)
    avg_wip_buffer2 = calculate_time_weighted_average(stats['wip_buffer2_data'], SIM_TIME)
    
    print(f"WIP promedio en Buffer1 (caramelos): {avg_wip_buffer1:.2f}")
    print(f"WIP promedio en Buffer2 (cajas): {avg_wip_buffer2:.2f}")

if __name__ == '__main__':
    main()
