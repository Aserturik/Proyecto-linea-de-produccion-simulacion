import math
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum
from collections import deque
import heapq
import streamlit as st
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
class Caja:
    """Representa una caja que contiene caramelos."""
    caramelos: int = 0  # Cantidad de caramelos en la caja (máximo 50)
    tiempo_creacion: float = 0.0
    tiempo_llegada_cola_actual: float = 0.0
    caramelos_items: list = None  # Lista de items de caramelos
    id: int = 0  # Identificador único de la caja

    def __post_init__(self):
        if self.caramelos_items is None:
            self.caramelos_items = []


@dataclass
class Evento:
    tiempo: float
    tipo: str
    data: Any = None


# --- Clase Principal de Simulación ---
class SimulacionLineaProduccion:
    def __init__(
        self,
        sim_time: float,
        buffer1_capacity: int,
        buffer2_capacity: int,
        m1_media_tiempo: float,
        m1_std_dev_tiempo: float,
        m2_media_tiempo: float,
        m2_std_dev_tiempo: float,
        m3_media_tiempo: float,
        m3_std_dev_tiempo: float,
        defect_prob: float,
        random_seed: int,
    ):

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
        self.contador_eventos = 0  # Contador único para desempatar eventos con el mismo tiempo
        self.cola1 = deque()  # FIFO para caramelos esperando en M1
        self.cola2 = deque()  # FIFO para cajas esperando en M2
        self.cola3 = deque()  # FIFO para cajas esperando en M3

        # NUEVO: Acumulador de caramelos para formar cajas
        self.acumulador_caramelos = []  # Lista de caramelos esperando formar caja
        self.caramelos_por_caja = 50  # Constante
        self.contador_cajas = 0  # Para IDs únicos de cajas

        # Estado de las máquinas
        self.estado_m1 = EstadoMaquina.OCIOSA
        self.estado_m2 = EstadoMaquina.OCIOSA
        self.estado_m3 = EstadoMaquina.OCIOSA

        # Items en proceso
        self.item_en_m1: Optional[Item] = None
        self.item_en_m2: Optional[Caja] = None  # Ahora procesa cajas
        self.item_en_m3: Optional[Caja] = None  # Ahora procesa cajas

        # Estadísticas
        self.stats = {
            "producidos_m1": 0,
            "defectos_m1": 0,
            "caramelos_a_buffer1": 0,  # Caramelos no defectuosos producidos por M1
            "cajas_empaquetadas_m2": 0,
            "cajas_selladas_m3": 0,
            "tiempos_sistema_caja": [],
            "wip_buffer1_data": [(0, 0)],  # (tiempo, nivel) - cola1
            "wip_buffer2_data": [(0, 0)],  # (tiempo, nivel) - cola2
            "acumulador_caramelos_data": [(0, 0)],  # (tiempo, cantidad) - acumulador
            "acum_tiempo_cola1": 0.0,
            "acum_tiempo_cola2": 0.0,
            "acum_tiempo_cola3": 0.0,
            "ultimo_cambio_wip": 0.0,
            # Lista de tuplas (tiempo, acumulado de defectos)
            "defectos_m1_tiempo": [],
            # (tiempo, acumulado de cajas selladas por M3)
            "cajas_selladas_m3_tiempo": [],
            "items_perdidos_buffer1": 0,  # NUEVO: contador de items perdidos por buffer1 lleno
            # NUEVO: lista de (tiempo, total perdidos)
            "bloqueos_fuente_tiempo": [],
            # NUEVO: [(tiempo, estado_m1, estado_m2, estado_m3)]
            "estado_maquinas_tiempo": [],
            # NUEVO: [(tiempo, len(cola1), len(cola2), len(cola3))]
            "niveles_colas_tiempo": [],
            # NUEVO: [(tiempo, len(acumulador_caramelos))]
            "acumulador_caramelos_data": [(0, 0)],
        }

        # Generador de números aleatorios
        self.rng = self._inicializar_rng(random_seed)

    def _inicializar_rng(self, seed: int):
        """Inicializa el generador de números aleatorios."""
        # TEMPORAL: Usar generador estándar de Python para debugging
        import random
        random.seed(seed)
        
        class SimpleRandom:
            def random(self):
                return random.random()
            def gauss(self, mu, sigma):
                return random.gauss(mu, sigma)
        
        return SimpleRandom()
        
        # ORIGINAL (comentado temporalmente):
        # rng_instance = ValidatedRandom(seed)
        # return rng_instance

    def _generar_tiempo_exponencial(self, media: float) -> float:
        """Genera un tiempo con distribución exponencial.
        Este método se mantiene por si se necesita para llegadas, pero no para tiempos de proceso.
        """
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

        # Actualizar WIP Buffer 1 (cola1 - caramelos esperando M1)
        wip1_actual = len(self.cola1)
        self.stats["wip_buffer1_data"].append((tiempo_actual, wip1_actual))

        # Actualizar WIP Buffer 2 (cola2 - cajas esperando M2)
        wip2_actual = len(self.cola2)
        self.stats["wip_buffer2_data"].append((tiempo_actual, wip2_actual))

        # Actualizar Acumulador de Caramelos
        acumulador_actual = len(self.acumulador_caramelos)
        self.stats["acumulador_caramelos_data"].append((tiempo_actual, acumulador_actual))

        self.stats["ultimo_cambio_wip"] = tiempo_actual

    def _programar_evento(self, tiempo: float, tipo: str, data: Any = None):
        """Programa un nuevo evento en la lista de eventos."""
        evento = Evento(tiempo, tipo, data)
        # Usar una tupla de 3 elementos: (tiempo, contador_unico, evento)
        # Esto garantiza que nunca haya empates que requieran comparar objetos Evento
        heapq.heappush(self.eventos, (tiempo, self.contador_eventos, evento))
        self.contador_eventos += 1

    def _registrar_estados(self):
        """Registra el estado de las máquinas y los niveles de las colas en el tiempo actual."""
        self.stats["estado_maquinas_tiempo"].append(
            (
                self.reloj,
                self.estado_m1.value,
                self.estado_m2.value,
                self.estado_m3.value,
            )
        )
        self.stats["niveles_colas_tiempo"].append(
            (self.reloj, len(self.cola1), len(self.cola2), len(self.cola3))
        )

    def _formar_caja(self):
        """Forma una caja con 50 caramelos y la envía a cola2 si hay espacio."""
        if len(self.acumulador_caramelos) < self.caramelos_por_caja:
            return
        
        # Verificar si hay espacio en cola2 antes de formar la caja
        if len(self.cola2) >= self.buffer2_capacity:
            # No se puede formar caja porque cola2 está llena
            # M1 debe bloquearse si intenta producir más caramelos
            return False
        
        # Tomar 50 caramelos del acumulador
        caramelos_para_caja = self.acumulador_caramelos[:self.caramelos_por_caja]
        self.acumulador_caramelos = self.acumulador_caramelos[self.caramelos_por_caja:]
        
        # Crear la caja
        nueva_caja = Caja(
            caramelos=self.caramelos_por_caja,
            tiempo_creacion=self.reloj,
            tiempo_llegada_cola_actual=self.reloj,
            caramelos_items=caramelos_para_caja,
            id=self.contador_cajas
        )
        self.contador_cajas += 1
        
        # Agregar a cola2
        self.cola2.append(nueva_caja)
        self._actualizar_wip()
        
        # Si M2 está ociosa, iniciar procesamiento
        if self.estado_m2 in [EstadoMaquina.OCIOSA, EstadoMaquina.INACTIVA_SIN_ENTRADA]:
            self._iniciar_proceso_m2()
        
        return True

    def _iniciar_proceso_m2(self):
        """Inicia el proceso en M2 si hay cajas disponibles."""
        if len(self.cola2) > 0 and self.estado_m2 != EstadoMaquina.PROCESANDO:
            caja_para_procesar = self.cola2.popleft()
            self.item_en_m2 = caja_para_procesar
            self.estado_m2 = EstadoMaquina.PROCESANDO
            tiempo_proceso = self._generar_tiempo_normal(
                self.m2_media_tiempo, self.m2_std_dev_tiempo
            )
            self._programar_evento(
                self.reloj + tiempo_proceso, "FIN_PROCESO_MAQUINA2"
            )
            self._actualizar_wip()

    def _iniciar_proceso_m3(self):
        """Inicia el proceso en M3 si hay cajas disponibles."""
        if len(self.cola3) > 0 and self.estado_m3 != EstadoMaquina.PROCESANDO:
            caja_para_sellar = self.cola3.popleft()
            self.item_en_m3 = caja_para_sellar
            self.estado_m3 = EstadoMaquina.PROCESANDO
            tiempo_proceso = self._generar_tiempo_normal(
                self.m3_media_tiempo, self.m3_std_dev_tiempo
            )
            self._programar_evento(
                self.reloj + tiempo_proceso, "FIN_PROCESO_MAQUINA3"
            )
            # Nota: _actualizar_wip no rastrea cola3 actualmente

    def _manejar_llegada_item_cola1(self):
        """Maneja la llegada de un nuevo item a la cola 1."""
        # Programar próxima llegada (asumiendo llegadas exponenciales por ahora)
        # Si las llegadas también deben ser normales, este método necesitará parámetros de media y std_dev
        # Ejemplo, este parámetro debería venir del constructor si se generaliza
        media_tiempo_llegada = 2.0
        tiempo_entre_llegadas = self._generar_tiempo_exponencial(
            media_tiempo_llegada)
        self._programar_evento(
            self.reloj + tiempo_entre_llegadas, "LLEGADA_ITEM_COLA1")

        nuevo_item = Item(
            tiempo_llegada_sistema=self.reloj,
            tiempo_llegada_cola_actual=self.reloj,
            id=self.stats[
                "producidos_m1"
            ],  # Se usa producidos_m1 para ID, podría ser un contador global de items
        )

        if (
            self.estado_m1 == EstadoMaquina.OCIOSA
        ):  # M1 puede procesar si está ociosa
            self.item_en_m1 = nuevo_item
            self.estado_m1 = EstadoMaquina.PROCESANDO
            tiempo_proceso = self._generar_tiempo_normal(
                self.m1_media_tiempo, self.m1_std_dev_tiempo
            )
            self._programar_evento(
                self.reloj + tiempo_proceso, "FIN_PROCESO_MAQUINA1")
            self._registrar_estados()
        else:
            if len(self.cola1) < self.buffer1_capacity:
                self.cola1.append(nuevo_item)
                self._actualizar_wip()
                self._registrar_estados()
            else:
                # Item perdido por buffer1 lleno
                self.stats["items_perdidos_buffer1"] += 1
                self.stats["bloqueos_fuente_tiempo"].append(
                    (self.reloj, self.stats["items_perdidos_buffer1"])
                )
                self._registrar_estados()
                # Item perdido o fuente bloqueada (no implementado explícitamente el registro de pérdida)
                # print(f"Tiempo {self.reloj}: Item perdido, cola1 llena.")
                pass

    def _manejar_fin_proceso_maquina1(self):
        """Maneja el fin del procesamiento en M1."""
        item_procesado = self.item_en_m1
        self.item_en_m1 = None
        self.stats["producidos_m1"] += 1

        # Verificar si el item es defectuoso
        if self.rng.random() < self.defect_prob:  # CORREGIDO: random() < prob para que ocurra el defecto
            # Item defectuoso
            item_procesado.defectuoso = True
            self.stats["defectos_m1"] += 1
            self.stats["defectos_m1_tiempo"].append(
                (self.reloj, self.stats["defectos_m1"])
            )
        else:
            # Item NO defectuoso
            item_procesado.defectuoso = False
            self.stats["caramelos_a_buffer1"] += 1
            
            # NUEVO: Agregar caramelo al acumulador
            self.acumulador_caramelos.append(item_procesado)
            
            # NUEVO: Verificar si se puede formar una caja
            if len(self.acumulador_caramelos) >= self.caramelos_por_caja:
                caja_formada = self._formar_caja()
                if not caja_formada:
                    # M1 se bloquea porque no puede formar caja (cola2 llena)
                    self.estado_m1 = EstadoMaquina.BLOQUEADA
                    self._registrar_estados()
                    return

        # Intentar procesar el siguiente item de cola1, solo si M1 no está bloqueada
        if self.estado_m1 != EstadoMaquina.BLOQUEADA:
            if len(self.cola1) > 0:
                item_de_cola1 = self.cola1.popleft()
                self.item_en_m1 = item_de_cola1
                self.estado_m1 = EstadoMaquina.PROCESANDO
                tiempo_proceso = self._generar_tiempo_normal(
                    self.m1_media_tiempo, self.m1_std_dev_tiempo
                )
                self._programar_evento(
                    self.reloj + tiempo_proceso, "FIN_PROCESO_MAQUINA1"
                )
                self._actualizar_wip()  # WIP de cola1 cambia
            else:
                self.estado_m1 = EstadoMaquina.OCIOSA

        self._registrar_estados()

    def _manejar_fin_proceso_maquina2(self):
        """Maneja el fin del procesamiento en M2 (empaquetado de caja)."""
        caja_empaquetada = self.item_en_m2  # Ahora es tipo Caja
        self.item_en_m2 = None
        self.estado_m2 = EstadoMaquina.OCIOSA # Establecer M2 a OCIOSA
        self.stats["cajas_empaquetadas_m2"] += 1

        # La caja empaquetada va a cola3 (buffer para M3)
        caja_empaquetada.tiempo_llegada_cola_actual = self.reloj
        self.cola3.append(caja_empaquetada)
        
        # Si M3 está ociosa, iniciar procesamiento
        if self.estado_m3 in [EstadoMaquina.OCIOSA, EstadoMaquina.INACTIVA_SIN_ENTRADA]:
            self._iniciar_proceso_m3()

        # Intentar procesar siguiente caja de cola2
        self._iniciar_proceso_m2()
        
        # Verificar si M1 puede desbloquearse y formar más cajas
        if self.estado_m1 == EstadoMaquina.BLOQUEADA:
            if len(self.acumulador_caramelos) >= self.caramelos_por_caja:
                caja_formada = self._formar_caja()
                if caja_formada:
                    # M1 se desbloquea
                    self.estado_m1 = EstadoMaquina.OCIOSA
                    # Intentar procesar siguiente item de cola1
                    if len(self.cola1) > 0:
                        item_de_cola1 = self.cola1.popleft()
                        self.item_en_m1 = item_de_cola1
                        self.estado_m1 = EstadoMaquina.PROCESANDO
                        tiempo_proceso = self._generar_tiempo_normal(
                            self.m1_media_tiempo, self.m1_std_dev_tiempo
                        )
                        self._programar_evento(
                            self.reloj + tiempo_proceso, "FIN_PROCESO_MAQUINA1"
                        )
                        self._actualizar_wip()

        self._registrar_estados()

    def _manejar_fin_proceso_maquina3(self):
        """Maneja el fin del procesamiento en M3 (sellado de caja)."""
        caja_sellada = self.item_en_m3
        self.item_en_m3 = None
        self.estado_m3 = EstadoMaquina.OCIOSA # Establecer M3 a OCIOSA
        self.stats["cajas_selladas_m3"] += 1

        # Calcular tiempo en sistema basado en el primer caramelo de la caja
        primer_caramelo = caja_sellada.caramelos_items[0]
        tiempo_en_sistema = self.reloj - primer_caramelo.tiempo_llegada_sistema
        self.stats["tiempos_sistema_caja"].append(tiempo_en_sistema)
        self.stats["cajas_selladas_m3_tiempo"].append(
            (self.reloj, self.stats["cajas_selladas_m3"])
        )

        # Intentar procesar siguiente caja de cola3
        self._iniciar_proceso_m3()
        
        # Verificar si M2 puede desbloquearse
        buffer3_capacity = self.buffer2_capacity
        if (
            self.estado_m2 == EstadoMaquina.BLOQUEADA
            and len(self.cola3) < buffer3_capacity
        ):
            caja_bloqueada_m2 = self.item_en_m2
            self.item_en_m2 = None

            caja_bloqueada_m2.tiempo_llegada_cola_actual = self.reloj
            self.cola3.append(caja_bloqueada_m2)

            self.estado_m2 = EstadoMaquina.OCIOSA
            self._iniciar_proceso_m2()

        self._registrar_estados()

    def ejecutar_simulacion(self) -> Dict[str, Any]:
        """Ejecuta la simulación y retorna los resultados."""
        # Programar primer evento de llegada
        # La lógica de _manejar_llegada_item_cola1 programa la siguiente llegada.
        # Necesitamos una llegada inicial.
        self._programar_evento(0.0, "LLEGADA_ITEM_COLA1")

        while self.reloj < self.sim_time and self.eventos:
            tiempo_evento, _, evento_actual = heapq.heappop(self.eventos)

            if (
                tiempo_evento > self.sim_time
            ):  # No procesar eventos más allá del tiempo de simulación
                break

            self.reloj = tiempo_evento

            if evento_actual.tipo == "LLEGADA_ITEM_COLA1":
                self._manejar_llegada_item_cola1()
            elif evento_actual.tipo == "FIN_PROCESO_MAQUINA1":
                self._manejar_fin_proceso_maquina1()
            elif evento_actual.tipo == "FIN_PROCESO_MAQUINA2":
                self._manejar_fin_proceso_maquina2()
            elif evento_actual.tipo == "FIN_PROCESO_MAQUINA3":
                self._manejar_fin_proceso_maquina3()

        # Calcular estadísticas finales
        resultados = self.stats.copy()

        resultados["throughput_cajas_min"] = (
            resultados["cajas_selladas_m3"] /
            self.sim_time if self.sim_time > 0 else 0
        )

        if resultados["tiempos_sistema_caja"]:
            resultados["tiempo_prom_sistema_caja"] = sum(
                resultados["tiempos_sistema_caja"]
            ) / len(resultados["tiempos_sistema_caja"])
        else:
            resultados["tiempo_prom_sistema_caja"] = 0

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
                t2, _ = wip_data[
                    i + 1
                ]  # El nivel usado es w1 durante el intervalo (t2-t1)
                area_total += w1 * (t2 - t1)

            return (
                area_total / tiempo_total_simulacion
                if tiempo_total_simulacion > 0
                else 0.0
            )

        resultados["avg_wip_buffer1"] = calcular_wip_promedio(
            list(resultados["wip_buffer1_data"]), self.sim_time
        )
        resultados["avg_wip_buffer2"] = calcular_wip_promedio(
            list(resultados["wip_buffer2_data"]), self.sim_time
        )

        return resultados


# Gráficas y análisis adicionales (fuera de la clase de simulación)
def graficar_resultados(resultados: Dict[str, Any]):
    """Genera gráficas de los resultados de la simulación."""
    import pandas as pd
    import plotly.graph_objects as go

    # 1. Producción total y defectos a lo largo del tiempo
    df_produccion = pd.DataFrame(
        resultados["cajas_selladas_m3_tiempo"], columns=[
            "Tiempo", "Cajas Selladas"]
    )
    df_defectos = pd.DataFrame(
        resultados["defectos_m1_tiempo"], columns=["Tiempo", "Defectos"]
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_produccion["Tiempo"],
            y=df_produccion["Cajas Selladas"],
            name="Cajas Selladas",
            line=dict(color="green"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_defectos["Tiempo"],
            y=df_defectos["Defectos"],
            name="Defectos",
            line=dict(color="red"),
        )
    )
    fig.update_layout(
        title="Producción Total y Defectos a lo Largo del Tiempo",
        xaxis_title="Tiempo (minutos)",
        yaxis_title="Cantidad",
        legend_title="Producción",
    )
    st.plotly_chart(fig, use_container_width=True)

    # 2. Tiempos en el sistema por caja
    df_tiempos_sistema = pd.DataFrame(
        resultados["tiempos_sistema_caja"], columns=[
            "Tiempo", "Tiempo en Sistema"]
    )
    fig_tiempos = go.Figure()
    fig_tiempos.add_trace(
        go.Scatter(
            x=df_tiempos_sistema["Tiempo"],
            y=df_tiempos_sistema["Tiempo en Sistema"],
            mode="markers",
            name="Tiempos en Sistema",
        )
    )
    fig_tiempos.update_layout(
        title="Tiempos en el Sistema por Caja",
        xaxis_title="Tiempo (minutos)",
        yaxis_title="Tiempo en Sistema (minutos)",
        legend_title="Tiempos",
    )
    st.plotly_chart(fig_tiempos, use_container_width=True)

    # 3. WIP promedio en Buffer 1 y Buffer 2
    df_wip_buffer1 = pd.DataFrame(
        resultados["wip_buffer1_data"], columns=["Tiempo", "WIP Buffer 1"]
    )
    df_wip_buffer2 = pd.DataFrame(
        resultados["wip_buffer2_data"], columns=["Tiempo", "WIP Buffer 2"]
    )

    fig_wip = go.Figure()
    fig_wip.add_trace(
        go.Scatter(
            x=df_wip_buffer1["Tiempo"],
            y=df_wip_buffer1["WIP Buffer 1"],
            name="WIP Buffer 1",
            line=dict(color="blue"),
        )
    )
    fig_wip.add_trace(
        go.Scatter(
            x=df_wip_buffer2["Tiempo"],
            y=df_wip_buffer2["WIP Buffer 2"],
            name="WIP Buffer 2",
            line=dict(color="orange"),
        )
    )
    fig_wip.update_layout(
        title="WIP Promedio en Buffer 1 y Buffer 2 a lo Largo del Tiempo",
        xaxis_title="Tiempo (minutos)",
        yaxis_title="Cantidad de Items",
        legend_title="Buffers",
    )
    st.plotly_chart(fig_wip, use_container_width=True)

    # 4. Estado de las máquinas a lo largo del tiempo
    estados_maquinas = resultados.get("estado_maquinas_tiempo", [])
    if estados_maquinas:
        df_estados = pd.DataFrame(
            estados_maquinas, columns=["Tiempo", "M1", "M2", "M3"]
        )
        estado_map = {
            "OCIOSA": 0,
            "PROCESANDO": 1,
            "BLOQUEADA": 2,
            "INACTIVA_SIN_ENTRADA": 3,
        }
        for m in ["M1", "M2", "M3"]:
            df_estados[m + "_num"] = df_estados[m].map(estado_map)
        fig_estados = go.Figure()
        colores = ["gray", "lime", "red", "orange"]
        nombres = ["Ociosa", "Procesando", "Bloqueada", "Sin Entrada"]
        for idx, m in enumerate(["M1", "M2", "M3"]):
            fig_estados.add_trace(
                go.Scatter(
                    x=df_estados["Tiempo"],
                    y=[idx] * len(df_estados),
                    mode="markers",
                    marker=dict(
                        color=df_estados[m + "_num"],
                        colorscale=[
                            [0, "gray"],
                            [0.33, "lime"],
                            [0.66, "red"],
                            [1, "orange"],
                        ],
                        cmin=0,
                        cmax=3,
                        size=10,
                        colorbar=dict(
                            title="Estado", tickvals=[0, 1, 2, 3], ticktext=nombres
                        ),
                    ),
                    name=f"Estado {m}",
                    text=df_estados[m],
                )
            )
        fig_estados.update_layout(
            title="Estados de las Máquinas a lo Largo del Tiempo",
            xaxis_title="Tiempo (minutos)",
            yaxis=dict(
                tickvals=[0, 1, 2], ticktext=["M1", "M2", "M3"], title="Máquina"
            ),
            showlegend=False,
        )
        st.plotly_chart(fig_estados, use_container_width=True)

    # 5. Items perdidos por falta de espacio en Buffer 1
    df_items_perdidos = pd.DataFrame(
        resultados["bloqueos_fuente_tiempo"], columns=[
            "Tiempo", "Items Perdidos"]
    )
    fig_items_perdidos = go.Figure()
    fig_items_perdidos.add_trace(
        go.Scatter(
            x=df_items_perdidos["Tiempo"],
            y=df_items_perdidos["Items Perdidos"],
            mode="lines+markers",
            name="Items Perdidos",
        )
    )
    fig_items_perdidos.update_layout(
        title="Items Perdidos por Falta de Espacio en Buffer 1 a lo Largo del Tiempo",
        xaxis_title="Tiempo (minutos)",
        yaxis_title="Cantidad de Items Perdidos",
        legend_title="Eventos",
    )
    st.plotly_chart(fig_items_perdidos, use_container_width=True)

    # 6. Niveles de colas a lo largo del tiempo
    niveles_colas = resultados.get("niveles_colas_tiempo", [])
    if niveles_colas:
        df_colas = pd.DataFrame(
            niveles_colas, columns=["Tiempo", "Cola1", "Cola2", "Cola3"]
        )
        fig_colas = go.Figure()
        fig_colas.add_trace(
            go.Scatter(
                x=df_colas["Tiempo"],
                y=df_colas["Cola1"],
                name="Cola1 (antes M1)",
                line=dict(color="blue"),
            )
        )
        fig_colas.add_trace(
            go.Scatter(
                x=df_colas["Tiempo"],
                y=df_colas["Cola2"],
                name="Cola2 (antes M2)",
                line=dict(color="green"),
            )
        )
        fig_colas.add_trace(
            go.Scatter(
                x=df_colas["Tiempo"],
                y=df_colas["Cola3"],
                name="Cola3 (antes M3)",
                line=dict(color="orange"),
            )
        )
        fig_colas.update_layout(
            title="Niveles de las Colas a lo Largo del Tiempo",
            xaxis_title="Tiempo (minutos)",
            yaxis_title="Cantidad de Items",
            legend_title="Colas",
        )
        st.plotly_chart(fig_colas, use_container_width=True)

    # 7. Promedios y tasas
    col1, col2 = st.columns(2)

    with col1:
        st.metric("📦 Cajas Selladas (Throughput)",
                  resultados.get("cajas_selladas_m3", 0))
        st.metric(
            "⚙️ Promedio Tiempo en Sistema por Caja",
            f"{resultados.get('tiempo_prom_sistema_caja', 0):.2f} min",
        )
        st.metric(
            "📈 Tasa de Producción (Cajas/min)",
            f"{resultados.get('throughput_cajas_min', 0):.2f}",
        )

    with col2:
        st.metric(
            "❌ Items Perdidos por Buffer1 Lleno",
            resultados.get("items_perdidos_buffer1", 0),
        )
        st.metric(
            "⏱️ Tiempo Promedio en Cola 1",
            f"{resultados.get('acum_tiempo_cola1', 0) /
               (len(resultados.get('wip_buffer1_data', [])) - 1):.2f} min",
        )
        st.metric(
            "⏱️ Tiempo Promedio en Cola 2",
            f"{resultados.get('acum_tiempo_cola2', 0) /
               (len(resultados.get('wip_buffer2_data', [])) - 1):.2f} min",
        )

    # 8. Evolución de bloqueos/fuente bloqueada
    bloqueos_fuente = resultados.get("bloqueos_fuente_tiempo", [])
    if bloqueos_fuente:
        df_bloqueos = pd.DataFrame(
            bloqueos_fuente, columns=["Tiempo", "Items Perdidos Acumulados"]
        )
        fig_bloqueos = go.Figure()
        fig_bloqueos.add_trace(
            go.Scatter(
                x=df_bloqueos["Tiempo"],
                y=df_bloqueos["Items Perdidos Acumulados"],
                mode="lines+markers",
                name="Items Perdidos",
            )
        )
        fig_bloqueos.update_layout(
            title="Evolución de Items Perdidos por Buffer1 Lleno",
            xaxis_title="Tiempo (minutos)",
            yaxis_title="Items Perdidos Acumulados",
        )
        st.plotly_chart(fig_bloqueos, use_container_width=True)
        st.plotly_chart(fig_bloqueos, use_container_width=True)
