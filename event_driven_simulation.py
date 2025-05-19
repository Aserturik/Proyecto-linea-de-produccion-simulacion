import math
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
from collections import deque
import heapq

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
                 m1_mean_time: float,
                 m2_mean_time: float,
                 m3_mean_time: float,
                 defect_prob: float,
                 random_seed: int):
        
        # Parámetros de simulación
        self.sim_time = sim_time
        self.buffer1_capacity = buffer1_capacity
        self.buffer2_capacity = buffer2_capacity
        self.m1_mean_time = m1_mean_time
        self.m2_mean_time = m2_mean_time
        self.m3_mean_time = m3_mean_time
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
            'ultimo_cambio_wip': 0.0
        }
        
        # Generador de números aleatorios
        self.rng = self._inicializar_rng(random_seed)
        
    def _inicializar_rng(self, seed: int):
        """Inicializa el generador de números aleatorios."""
        # Por ahora usamos un generador simple, pero debería usar ValidatedRandom
        import random
        rng = random.Random(seed)
        return rng
    
    def _generar_tiempo_exponencial(self, media: float) -> float:
        """Genera un tiempo con distribución exponencial."""
        u = self.rng.random()
        if u == 0:
            u = 1e-9
        return -math.log(u) * media
    
    def _actualizar_wip(self):
        """Actualiza las estadísticas de WIP."""
        tiempo_actual = self.reloj
        tiempo_desde_ultimo = tiempo_actual - self.stats['ultimo_cambio_wip']
        
        # Actualizar WIP Buffer 1
        wip1_actual = len(self.cola1)
        if self.estado_m1 == EstadoMaquina.PROCESANDO:
            wip1_actual += 1
        self.stats['wip_buffer1_data'].append((tiempo_actual, wip1_actual))
        
        # Actualizar WIP Buffer 2
        wip2_actual = len(self.cola2)
        if self.estado_m2 == EstadoMaquina.PROCESANDO:
            wip2_actual += 1
        self.stats['wip_buffer2_data'].append((tiempo_actual, wip2_actual))
        
        self.stats['ultimo_cambio_wip'] = tiempo_actual
    
    def _programar_evento(self, tiempo: float, tipo: str, data: Any = None):
        """Programa un nuevo evento en la lista de eventos."""
        evento = Evento(tiempo, tipo, data)
        heapq.heappush(self.eventos, (tiempo, evento))
    
    def _manejar_llegada_item_cola1(self):
        """Maneja la llegada de un nuevo item a la cola 1."""
        # Programar próxima llegada
        tiempo_entre_llegadas = self._generar_tiempo_exponencial(self.m1_mean_time)
        self._programar_evento(self.reloj + tiempo_entre_llegadas, 'LLEGADA_ITEM_COLA1')
        
        # Crear nuevo item
        nuevo_item = Item(
            tiempo_llegada_sistema=self.reloj,
            tiempo_llegada_cola_actual=self.reloj,
            id=self.stats['producidos_m1']
        )
        
        # Verificar si M1 está ociosa y hay espacio en cola2
        if (self.estado_m1 == EstadoMaquina.OCIOSA and 
            len(self.cola2) < self.buffer2_capacity):
            # Iniciar procesamiento en M1
            self.item_en_m1 = nuevo_item
            self.estado_m1 = EstadoMaquina.PROCESANDO
            tiempo_proceso = self._generar_tiempo_exponencial(self.m1_mean_time)
            self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA1')
        else:
            # Añadir a cola1
            self.cola1.append(nuevo_item)
            self._actualizar_wip()
    
    def _manejar_fin_proceso_maquina1(self):
        """Maneja el fin del procesamiento en M1."""
        item_procesado = self.item_en_m1
        self.item_en_m1 = None
        self.stats['producidos_m1'] += 1
        
        # Verificar si el item es defectuoso
        if self.rng.random() > self.defect_prob:
            self.stats['caramelos_a_buffer1'] += 1
            
            # Verificar si hay espacio en cola2
            if len(self.cola2) < self.buffer2_capacity:
                item_procesado.tiempo_llegada_cola_actual = self.reloj
                self.cola2.append(item_procesado)
                self._actualizar_wip()
                
                # Verificar si M2 está ociosa o inactiva
                if (self.estado_m2 in [EstadoMaquina.OCIOSA, EstadoMaquina.INACTIVA_SIN_ENTRADA] and 
                    len(self.cola2) > 0):
                    item_para_m2 = self.cola2.popleft()
                    self.item_en_m2 = item_para_m2
                    self.estado_m2 = EstadoMaquina.PROCESANDO
                    tiempo_proceso = self._generar_tiempo_exponencial(self.m2_mean_time)
                    self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA2')
                    self._actualizar_wip()
                
                # Intentar procesar otro item de cola1
                if len(self.cola1) > 0:
                    item_de_cola1 = self.cola1.popleft()
                    self.item_en_m1 = item_de_cola1
                    self.estado_m1 = EstadoMaquina.PROCESANDO
                    tiempo_proceso = self._generar_tiempo_exponencial(self.m1_mean_time)
                    self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA1')
                    self._actualizar_wip()
                else:
                    self.estado_m1 = EstadoMaquina.OCIOSA
            else:
                # Cola2 llena, M1 se bloquea
                self.estado_m1 = EstadoMaquina.BLOQUEADA
                self.item_en_m1 = item_procesado
        else:
            self.stats['defectos_m1'] += 1
            # Intentar procesar otro item de cola1
            if len(self.cola1) > 0:
                item_de_cola1 = self.cola1.popleft()
                self.item_en_m1 = item_de_cola1
                self.estado_m1 = EstadoMaquina.PROCESANDO
                tiempo_proceso = self._generar_tiempo_exponencial(self.m1_mean_time)
                self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA1')
                self._actualizar_wip()
            else:
                self.estado_m1 = EstadoMaquina.OCIOSA
    
    def _manejar_fin_proceso_maquina2(self):
        """Maneja el fin del procesamiento en M2."""
        item_procesado = self.item_en_m2
        self.item_en_m2 = None
        self.stats['cajas_empaquetadas_m2'] += 1
        
        # Verificar si hay espacio en cola3
        if len(self.cola3) < self.buffer2_capacity:
            item_procesado.tiempo_llegada_cola_actual = self.reloj
            self.cola3.append(item_procesado)
            self._actualizar_wip()
            
            # Verificar si M3 está ociosa o inactiva
            if (self.estado_m3 in [EstadoMaquina.OCIOSA, EstadoMaquina.INACTIVA_SIN_ENTRADA] and 
                len(self.cola3) > 0):
                item_para_m3 = self.cola3.popleft()
                self.item_en_m3 = item_para_m3
                self.estado_m3 = EstadoMaquina.PROCESANDO
                tiempo_proceso = self._generar_tiempo_exponencial(self.m3_mean_time)
                self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA3')
                self._actualizar_wip()
            
            # Intentar procesar otro item de cola2
            if len(self.cola2) > 0:
                item_de_cola2 = self.cola2.popleft()
                self.item_en_m2 = item_de_cola2
                self.estado_m2 = EstadoMaquina.PROCESANDO
                tiempo_proceso = self._generar_tiempo_exponencial(self.m2_mean_time)
                self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA2')
                self._actualizar_wip()
            else:
                self.estado_m2 = EstadoMaquina.INACTIVA_SIN_ENTRADA
            
            # Comprobar si M1 estaba bloqueada
            if (self.estado_m1 == EstadoMaquina.BLOQUEADA and 
                len(self.cola2) < self.buffer2_capacity):
                item_bloqueado_m1 = self.item_en_m1
                self.item_en_m1 = None
                item_bloqueado_m1.tiempo_llegada_cola_actual = self.reloj
                self.cola2.append(item_bloqueado_m1)
                self.estado_m1 = EstadoMaquina.OCIOSA
                self._actualizar_wip()
                
                # Intentar procesar de cola1
                if len(self.cola1) > 0:
                    item_de_cola1 = self.cola1.popleft()
                    self.item_en_m1 = item_de_cola1
                    self.estado_m1 = EstadoMaquina.PROCESANDO
                    tiempo_proceso = self._generar_tiempo_exponencial(self.m1_mean_time)
                    self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA1')
                    self._actualizar_wip()
        else:
            # Cola3 llena, M2 se bloquea
            self.estado_m2 = EstadoMaquina.BLOQUEADA
            self.item_en_m2 = item_procesado
    
    def _manejar_fin_proceso_maquina3(self):
        """Maneja el fin del procesamiento en M3."""
        item_terminado = self.item_en_m3
        self.item_en_m3 = None
        self.stats['cajas_selladas_m3'] += 1
        
        # Calcular tiempo en sistema
        tiempo_en_sistema = self.reloj - item_terminado.tiempo_llegada_sistema
        self.stats['tiempos_sistema_caja'].append(tiempo_en_sistema)
        
        # Intentar procesar otro item de cola3
        if len(self.cola3) > 0:
            item_de_cola3 = self.cola3.popleft()
            self.item_en_m3 = item_de_cola3
            self.estado_m3 = EstadoMaquina.PROCESANDO
            tiempo_proceso = self._generar_tiempo_exponencial(self.m3_mean_time)
            self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA3')
            self._actualizar_wip()
        else:
            self.estado_m3 = EstadoMaquina.INACTIVA_SIN_ENTRADA
        
        # Comprobar si M2 estaba bloqueada
        if (self.estado_m2 == EstadoMaquina.BLOQUEADA and 
            len(self.cola3) < self.buffer2_capacity):
            item_bloqueado_m2 = self.item_en_m2
            self.item_en_m2 = None
            item_bloqueado_m2.tiempo_llegada_cola_actual = self.reloj
            self.cola3.append(item_bloqueado_m2)
            self.estado_m2 = EstadoMaquina.OCIOSA
            self._actualizar_wip()
            
            # Intentar procesar de cola2
            if len(self.cola2) > 0:
                item_de_cola2 = self.cola2.popleft()
                self.item_en_m2 = item_de_cola2
                self.estado_m2 = EstadoMaquina.PROCESANDO
                tiempo_proceso = self._generar_tiempo_exponencial(self.m2_mean_time)
                self._programar_evento(self.reloj + tiempo_proceso, 'FIN_PROCESO_MAQUINA2')
                self._actualizar_wip()
            else:
                self.estado_m2 = EstadoMaquina.INACTIVA_SIN_ENTRADA
    
    def ejecutar_simulacion(self) -> Dict[str, Any]:
        """Ejecuta la simulación y retorna los resultados."""
        # Programar primer evento de llegada
        self._programar_evento(0.0, 'LLEGADA_ITEM_COLA1')
        
        # Bucle principal de simulación
        while self.reloj < self.sim_time and self.eventos:
            # Obtener próximo evento
            tiempo_evento, evento = heapq.heappop(self.eventos)
            self.reloj = tiempo_evento
            
            # Manejar evento según su tipo
            if evento.tipo == 'LLEGADA_ITEM_COLA1':
                self._manejar_llegada_item_cola1()
            elif evento.tipo == 'FIN_PROCESO_MAQUINA1':
                self._manejar_fin_proceso_maquina1()
            elif evento.tipo == 'FIN_PROCESO_MAQUINA2':
                self._manejar_fin_proceso_maquina2()
            elif evento.tipo == 'FIN_PROCESO_MAQUINA3':
                self._manejar_fin_proceso_maquina3()
        
        # Calcular estadísticas finales
        resultados = self.stats.copy()
        
        # Calcular throughput
        resultados['throughput_cajas_min'] = (
            resultados['cajas_selladas_m3'] / self.sim_time 
            if self.sim_time > 0 else 0
        )
        
        # Calcular tiempo promedio en sistema
        if resultados['tiempos_sistema_caja']:
            resultados['tiempo_prom_sistema_caja'] = (
                sum(resultados['tiempos_sistema_caja']) / 
                len(resultados['tiempos_sistema_caja'])
            )
        else:
            resultados['tiempo_prom_sistema_caja'] = 0
        
        # Calcular WIP promedio
        def calcular_wip_promedio(wip_data):
            if not wip_data:
                return 0.0
            area_total = 0.0
            for i in range(len(wip_data) - 1):
                t1, w1 = wip_data[i]
                t2, w2 = wip_data[i + 1]
                area_total += (t2 - t1) * w1
            return area_total / self.sim_time if self.sim_time > 0 else 0.0
        
        resultados['avg_wip_buffer1'] = calcular_wip_promedio(resultados['wip_buffer1_data'])
        resultados['avg_wip_buffer2'] = calcular_wip_promedio(resultados['wip_buffer2_data'])
        
        return resultados 