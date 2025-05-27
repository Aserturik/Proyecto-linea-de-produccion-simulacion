import math
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
from collections import deque
import heapq
import random # Asegúrate que esta línea esté si no usas ValidatedRandom abajo

# Si tienes 'aleatorios.src.modelos.validated_random.ValidatedRandom', descomenta la siguiente línea:
from aleatorios.src.modelos.validated_random import ValidatedRandom

# --- Enums ---
class EstadoMaquina(Enum):
    OCIOSA = "OCIOSA"
    PROCESANDO = "PROCESANDO"
    BLOQUEADA = "BLOQUEADA"
    INACTIVA_SIN_ENTRADA = "INACTIVA_SIN_ENTRADA"

# --- Data Classes ---
@dataclass
class Item:
    tiempo_llegada_sistema: float
    tiempo_llegada_cola_actual: float
    id: int = 0  # Identificador único del item
    defectuoso: bool = False  # Para items de M1

@dataclass
class Evento:
    tiempo: float
    tipo: str
    data: Any = None

# --- Clase Principal de Simulación ---
class SimulacionLineaProduccion:
    def __init__(self,
                 sim_time: float,
                 buffer1_capacity: int,
                 buffer2_capacity: int,
                 m1_media_tiempo: float, # Renombrado/reutilizado para claridad
                 m1_std_dev_tiempo: float,
                 m2_media_tiempo: float, # Renombrado/reutilizado para claridad
                 m2_std_dev_tiempo: float,
                 m3_media_tiempo: float, # Renombrado/reutilizado para claridad
                 m3_std_dev_tiempo: float,
                 defect_prob: float,
                 random_seed: int):

        # Parámetros de simulación
        self.sim_time = sim_time
        self.buffer1_capacity = buffer1_capacity
        self.buffer2_capacity = buffer2_capacity

        # Parámetros de tiempo de proceso para M1
        self.m1_media_tiempo = m1_media_tiempo
        self.m1_std_dev_tiempo = m1_std_dev_tiempo

        # Parámetros de tiempo de proceso para M2
        self.m2_media_tiempo = m2_media_tiempo
        self.m2_std_dev_tiempo = m2_std_dev_tiempo

        # Parámetros de tiempo de proceso para M3
        self.m3_media_tiempo = m3_media_tiempo
        self.m3_std_dev_tiempo = m3_std_dev_tiempo

        self.defect_prob = defect_prob

        # Estado de la simulación
        self.reloj = 0.0
        self.eventos = []  # Lista priorizada de eventos
        self.cola1 = deque()  # FIFO para items esperando en M1
        self.cola2 = deque()  # FIFO para items esperando en M2
        self.cola3 = deque()  # FIFO para items esperando en M3

        # Estado de las máquinas
        self.estado_m1 = EstadoMaquina.OCIOSA
        self.estado_m2 = EstadoMaquina.OCIOSA
        self.estado_m3 = EstadoMaquina.OCIOSA

        # Items en proceso
        self.item_en_m1: Optional[Item] = None
        self.item_en_m2: Optional[Item] = None
        self.item_en_m3: Optional[Item] = None

        # Estadísticas
        self.stats = {
            'producidos_m1': 0,
            'defectos_m1': 0,
            'caramelos_a_buffer1': 0,
            'cajas_empaquetadas_m2': 0,
            'cajas_selladas_m3': 0,
            'tiempos_sistema_caja': [],
            'wip_buffer1_data': [(0, 0)],  # (tiempo, nivel)
            'wip_buffer2_data': [(0, 0)],  # (tiempo, nivel)
            'acum_tiempo_cola1': 0.0,
            'acum_tiempo_cola2': 0.0,
            'acum_tiempo_cola3': 0.0,
            'ultimo_cambio_wip': 0.0,
            'defectos_m1_tiempo': [],  # Lista de tuplas (tiempo, acumulado de defectos)
            'cajas_selladas_m3_tiempo': [], # (tiempo, acumulado de cajas selladas por M3)
        }

        # Generador de números aleatorios
        self.rng = self._inicializar_rng(random_seed)

    def _inicializar_rng(self, seed: int):
        """Inicializa el generador de números aleatorios."""
        # Si tienes ValidatedRandom, reemplaza la siguiente línea:
        # Ejemplo: self.rng = ValidatedRandom(seed)
        # Por ahora, se usa el generador estándar de Python:
        rng_instance = ValidatedRandom(seed)
        return rng_instance

    def _generar_tiempo_exponencial(self, media: float) -> float:
        """Genera un tiempo con distribución exponencial.
           Este método se mantiene por si se necesita para llegadas, pero no para tiempos de proceso."""
        u = self.rng.random()
        if u == 0:
            u = 1e-9
        return -math.log(u) * media

    def _generar_tiempo_normal(self, media: float, desviacion_estandar: float) -> float:
        """Genera un tiempo con distribución normal, asegurando que no sea negativo."""
        tiempo_generado = self.rng.gauss(media, desviacion_estandar)
        return max(0, tiempo_generado)

    def _actualizar_wip(self):
        """Actualiza las estadísticas de WIP."""
        tiempo_actual = self.reloj
        # tiempo_desde_ultimo = tiempo_actual - self.stats['ultimo_cambio_wip'] # No usado actualmente

        # Actualizar WIP Buffer 1
        wip1_actual = len(self.cola1)
        # La lógica original sumaba +1 si M1 estaba procesando,
        # pero los buffers suelen medir solo lo que está en cola.
        # Ajustar según la definición deseada de WIP.
        # Por ahora, se mantiene la lógica de cola.
        self.stats['wip_buffer1_data'].append((tiempo_actual, wip1_actual))

        # Actualizar WIP Buffer 2
        wip2_actual = len(self.cola2)
        self.stats['wip_buffer2_data'].append((tiempo_actual, wip2_actual))

        self.stats['ultimo_cambio_wip'] = tiempo_actual

    def _programar_evento(self, tiempo: float, tipo: str, data: Any = None):
        """Programa un nuevo evento en la lista de eventos."""
        evento = Evento(tiempo, tipo, data)
        heapq.heappush(self.eventos, (tiempo, evento))

    def _manejar_llegada_item_cola1(self):
        """Maneja la llegada de un nuevo item a la cola 1."""
        # Programar próxima llegada (asumiendo llegadas exponenciales por ahora)
        # Si las llegadas también deben ser normales, este método necesitará parámetros de media y std_dev
        media_tiempo_llegada = 2.0 # Ejemplo, este parámetro debería venir del constructor si se generaliza
        tiempo_entre_llegadas = self._generar_tiempo_exponencial(media_tiempo_llegada)
        self._programar_evento(self.reloj + tiempo_entre_llegadas, 'LLEGADA_ITEM_COLA1')

        nuevo_item = Item(
            tiempo_llegada_sistema=self.reloj,
            tiempo_llegada_cola_actual=self.reloj,
            id=self.stats['producidos_m1'] # Se usa producidos_m1 para ID, podría ser un contador global de items
        )

        if (self.estado_m1 == EstadoMaquina.OCIOSA and
            len(self.cola2) < self.buffer2_capacity): # Asumiendo que M1 alimenta cola2 directamente (lógica actual)
            self.item_en_m1 = nuevo_item
            self.estado_m1 = EstadoMaquina.PROCESANDO
            tiempo_proceso = self._generar_tiempo_normal(self.m1_media_tiempo, self.m1_std_dev_tiempo)
            self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA1')
        else:
            if len(self.cola1) < self.buffer1_capacity:
                self.cola1.append(nuevo_item)
                self._actualizar_wip()
            else:
                # Item perdido o fuente bloqueada (no implementado explícitamente el registro de pérdida)
                # print(f"Tiempo {self.reloj}: Item perdido, cola1 llena.")
                pass


    def _manejar_fin_proceso_maquina1(self):
        """Maneja el fin del procesamiento en M1."""
        item_procesado = self.item_en_m1
        self.item_en_m1 = None
        self.stats['producidos_m1'] += 1

        # Verificar si el item es defectuoso
        if self.rng.random() >= self.defect_prob: # Corrección: random() < prob es para evento que ocurre
            item_procesado.defectuoso = False
            self.stats['caramelos_a_buffer1'] += 1

            if len(self.cola2) < self.buffer2_capacity:
                item_procesado.tiempo_llegada_cola_actual = self.reloj
                self.cola2.append(item_procesado)
                self._actualizar_wip()

                if (self.estado_m2 in [EstadoMaquina.OCIOSA, EstadoMaquina.INACTIVA_SIN_ENTRADA] and
                    len(self.cola2) > 0):
                    item_para_m2 = self.cola2.popleft()
                    self.item_en_m2 = item_para_m2
                    self.estado_m2 = EstadoMaquina.PROCESANDO
                    tiempo_proceso = self._generar_tiempo_normal(self.m2_media_tiempo, self.m2_std_dev_tiempo)
                    self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA2')
                    self._actualizar_wip() # WIP de cola2 cambia

            else: # Cola2 llena, M1 se bloquea
                self.estado_m1 = EstadoMaquina.BLOQUEADA
                self.item_en_m1 = item_procesado # M1 retiene el item
                # No se añade a cola1, ya que M1 lo tiene
                return # No intentar tomar más de cola1 si M1 está bloqueada

        else: # Item defectuoso
            item_procesado.defectuoso = True
            self.stats['defectos_m1'] += 1
            self.stats['defectos_m1_tiempo'].append((self.reloj, self.stats['defectos_m1']))
            # El item defectuoso simplemente desaparece del sistema por ahora

        # Intentar procesar el siguiente item de cola1, solo si M1 no está bloqueada
        if self.estado_m1 != EstadoMaquina.BLOQUEADA:
            if len(self.cola1) > 0:
                item_de_cola1 = self.cola1.popleft()
                self.item_en_m1 = item_de_cola1
                self.estado_m1 = EstadoMaquina.PROCESANDO
                tiempo_proceso = self._generar_tiempo_normal(self.m1_media_tiempo, self.m1_std_dev_tiempo)
                self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA1')
                self._actualizar_wip() # WIP de cola1 cambia
            else:
                self.estado_m1 = EstadoMaquina.OCIOSA


    def _manejar_fin_proceso_maquina2(self):
        """Maneja el fin del procesamiento en M2."""
        item_procesado = self.item_en_m2
        self.item_en_m2 = None
        self.stats['cajas_empaquetadas_m2'] += 1

        # Asumiendo que cola3 es el buffer antes de M3 y tiene una capacidad (no definida en __init__ aún)
        # Por ahora, usaré self.buffer2_capacity para cola3 como un placeholder,
        # idealmente debería ser self.buffer3_capacity
        # Si no hay buffer3_capacity, podemos asumir que es ilimitada o usar una existente.
        # Por consistencia con el código original que usa buffer2_capacity para cola3:
        buffer3_simulated_capacity = self.buffer2_capacity # Placeholder

        if len(self.cola3) < buffer3_simulated_capacity:
            item_procesado.tiempo_llegada_cola_actual = self.reloj
            self.cola3.append(item_procesado)
            # self._actualizar_wip() # Necesitaría wip_buffer3_data

            if (self.estado_m3 in [EstadoMaquina.OCIOSA, EstadoMaquina.INACTIVA_SIN_ENTRADA] and
                len(self.cola3) > 0):
                item_para_m3 = self.cola3.popleft()
                self.item_en_m3 = item_para_m3
                self.estado_m3 = EstadoMaquina.PROCESANDO
                tiempo_proceso = self._generar_tiempo_normal(self.m3_media_tiempo, self.m3_std_dev_tiempo)
                self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA3')
                # self._actualizar_wip() # WIP de cola3 cambia
        else: # Cola3 llena, M2 se bloquea
            self.estado_m2 = EstadoMaquina.BLOQUEADA
            self.item_en_m2 = item_procesado # M2 retiene el item
            # No intentar tomar más de cola2 si M2 está bloqueada

        # Intentar procesar el siguiente item de cola2, solo si M2 no está bloqueada
        if self.estado_m2 != EstadoMaquina.BLOQUEADA:
            if len(self.cola2) > 0:
                item_de_cola2 = self.cola2.popleft()
                self.item_en_m2 = item_de_cola2
                self.estado_m2 = EstadoMaquina.PROCESANDO
                tiempo_proceso = self._generar_tiempo_normal(self.m2_media_tiempo, self.m2_std_dev_tiempo)
                self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA2')
                self._actualizar_wip() # WIP de cola2 cambia
            else:
                self.estado_m2 = EstadoMaquina.INACTIVA_SIN_ENTRADA # OCIOSA si no hay distinción

        # Comprobar si M1 estaba bloqueada y ahora hay espacio en cola2
        if (self.estado_m1 == EstadoMaquina.BLOQUEADA and
            len(self.cola2) < self.buffer2_capacity):
            item_bloqueado_m1 = self.item_en_m1 # Este es el item que M1 no pudo poner en cola2
            self.item_en_m1 = None # M1 ya no lo tiene

            item_bloqueado_m1.tiempo_llegada_cola_actual = self.reloj
            self.cola2.append(item_bloqueado_m1) # Ponerlo en cola2
            self._actualizar_wip() # WIP de cola2 cambia

            # M1 ahora está ociosa y puede intentar tomar de cola1
            self.estado_m1 = EstadoMaquina.OCIOSA
            if len(self.cola1) > 0:
                item_de_cola1 = self.cola1.popleft()
                self.item_en_m1 = item_de_cola1
                self.estado_m1 = EstadoMaquina.PROCESANDO
                tiempo_proceso_m1 = self._generar_tiempo_normal(self.m1_media_tiempo, self.m1_std_dev_tiempo)
                self._programar_evento(self.reloj + tiempo_proceso_m1, 'FIN_PROCESO_MAQUINA1')
                self._actualizar_wip() # WIP de cola1 cambia
            # else: M1 queda OCIOSA


    def _manejar_fin_proceso_maquina3(self):
        """Maneja el fin del procesamiento en M3."""
        item_terminado = self.item_en_m3
        self.item_en_m3 = None
        self.stats['cajas_selladas_m3'] += 1

        tiempo_en_sistema = self.reloj - item_terminado.tiempo_llegada_sistema
        self.stats['tiempos_sistema_caja'].append(tiempo_en_sistema)
        self.stats['cajas_selladas_m3_tiempo'].append((self.reloj, self.stats['cajas_selladas_m3']))

        # Intentar procesar otro item de cola3
        if len(self.cola3) > 0:
            item_de_cola3 = self.cola3.popleft()
            self.item_en_m3 = item_de_cola3
            self.estado_m3 = EstadoMaquina.PROCESANDO
            tiempo_proceso = self._generar_tiempo_normal(self.m3_media_tiempo, self.m3_std_dev_tiempo)
            self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA3')
            # self._actualizar_wip() # Si se mide wip_buffer3_data
        else:
            self.estado_m3 = EstadoMaquina.INACTIVA_SIN_ENTRADA # O OCIOSA

        # Comprobar si M2 estaba bloqueada y ahora hay espacio en cola3
        # Usando buffer3_simulated_capacity de nuevo
        buffer3_simulated_capacity = self.buffer2_capacity # Placeholder
        if (self.estado_m2 == EstadoMaquina.BLOQUEADA and
            len(self.cola3) < buffer3_simulated_capacity):
            item_bloqueado_m2 = self.item_en_m2
            self.item_en_m2 = None

            item_bloqueado_m2.tiempo_llegada_cola_actual = self.reloj
            self.cola3.append(item_bloqueado_m2)
            # self._actualizar_wip() # Si se mide wip_buffer3_data

            self.estado_m2 = EstadoMaquina.OCIOSA # M2 ahora está ociosa
            if len(self.cola2) > 0:
                item_de_cola2 = self.cola2.popleft()
                self.item_en_m2 = item_de_cola2
                self.estado_m2 = EstadoMaquina.PROCESANDO
                tiempo_proceso_m2 = self._generar_tiempo_normal(self.m2_media_tiempo, self.m2_std_dev_tiempo)
                self._programar_evento(self.reloj + tiempo_proceso_m2, 'FIN_PROCESO_MAQUINA2')
                self._actualizar_wip() # WIP de cola2 cambia
            else:
                self.estado_m2 = EstadoMaquina.INACTIVA_SIN_ENTRADA


    def ejecutar_simulacion(self) -> Dict[str, Any]:
        """Ejecuta la simulación y retorna los resultados."""
        # Programar primer evento de llegada
        # La lógica de _manejar_llegada_item_cola1 programa la siguiente llegada.
        # Necesitamos una llegada inicial.
        self._programar_evento(0.0, 'LLEGADA_ITEM_COLA1')

        while self.reloj < self.sim_time and self.eventos:
            tiempo_evento, evento_actual = heapq.heappop(self.eventos)

            if tiempo_evento > self.sim_time: # No procesar eventos más allá del tiempo de simulación
                break

            self.reloj = tiempo_evento

            if evento_actual.tipo == 'LLEGADA_ITEM_COLA1':
                self._manejar_llegada_item_cola1()
            elif evento_actual.tipo == 'FIN_PROCESO_MAQUINA1':
                self._manejar_fin_proceso_maquina1()
            elif evento_actual.tipo == 'FIN_PROCESO_MAQUINA2':
                self._manejar_fin_proceso_maquina2()
            elif evento_actual.tipo == 'FIN_PROCESO_MAQUINA3':
                self._manejar_fin_proceso_maquina3()

        # Calcular estadísticas finales
        resultados = self.stats.copy()

        resultados['throughput_cajas_min'] = (
            resultados['cajas_selladas_m3'] / self.sim_time
            if self.sim_time > 0 else 0
        )

        if resultados['tiempos_sistema_caja']:
            resultados['tiempo_prom_sistema_caja'] = (
                sum(resultados['tiempos_sistema_caja']) /
                len(resultados['tiempos_sistema_caja'])
            )
        else:
            resultados['tiempo_prom_sistema_caja'] = 0

        def calcular_wip_promedio(wip_data, tiempo_total_simulacion):
            if not wip_data or tiempo_total_simulacion == 0:
                return 0.0
            
            # Asegurarse que el último punto de datos de WIP llegue hasta el final de la simulación
            # para un cálculo correcto del área.
            last_time, last_wip_level = wip_data[-1]
            if last_time < tiempo_total_simulacion:
                 wip_data.append((tiempo_total_simulacion, last_wip_level))

            area_total = 0.0
            for i in range(len(wip_data) - 1):
                t1, w1 = wip_data[i]
                t2, _ = wip_data[i+1] # El nivel usado es w1 durante el intervalo (t2-t1)
                area_total += w1 * (t2 - t1)
            
            return area_total / tiempo_total_simulacion if tiempo_total_simulacion > 0 else 0.0

        resultados['avg_wip_buffer1'] = calcular_wip_promedio(list(resultados['wip_buffer1_data']), self.sim_time)
        resultados['avg_wip_buffer2'] = calcular_wip_promedio(list(resultados['wip_buffer2_data']), self.sim_time)

        return resultados