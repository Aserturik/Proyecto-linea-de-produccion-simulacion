# Simulación de Línea de Producción

Este proyecto simula una línea de producción de caramelos utilizando SimPy. La línea consta de tres máquinas y dos buffers intermedios. La simulación recopila estadísticas sobre la producción, defectos, tiempos en el sistema y niveles de inventario en proceso (WIP).

## Estructura del Proyecto

*   `index.py`: Script principal que configura y ejecuta la simulación de la línea de producción.
*   `aleatorios/`: Directorio que contiene la lógica para la generación de números pseudoaleatorios.
    *   `src/modelos/validated_random.py`: Clase `ValidatedRandom` utilizada por la simulación para generar números aleatorios U(0,1).
    *   `test_random_quality.py`: Script para probar la calidad de los generadores de números aleatorios (no se usa directamente en la simulación principal pero es parte del módulo `aleatorios`).
*   `requirements.txt`: Lista de dependencias de Python.

## Requisitos Previos

*   Python 3.x
*   Un entorno virtual (recomendado)

## Configuración del Entorno

1.  **Clonar el repositorio (si aplica):**
    ```bash
    git clone <repository-url>
    cd proyecto-linea-de-produccion-simulacion
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    ```
    *   En Linux/macOS (bash/zsh):
        ```bash
        source venv/bin/activate
        ```
    *   En Linux/macOS (fish):
        ```bash
        source venv/bin/activate.fish
        ```
    *   En Windows (PowerShell):
        ```ps1
        .\venv\Scripts\Activate.ps1
        ```
    *   En Windows (CMD):
        ```bat
        .\venv\Scripts\activate.bat
        ```

3.  **Instalar dependencias:**
    Asegúrate de que tu entorno virtual esté activado, luego ejecuta:
    ```bash
    pip install -r requirements.txt
    ```
    Esto instalará `simpy`, `numpy`, `tabulate`, y `matplotlib`.

## Ejecución de la Simulación

Con el entorno virtual activado y las dependencias instaladas, puedes ejecutar la simulación con el siguiente comando:

```bash
python index.py
```

O, para estar seguro de que se usa el intérprete del entorno virtual:

*   En Linux/macOS:
    ```bash
    ./venv/bin/python index.py
    ```
*   En Windows:
    ```bash
    .\venv\Scripts\python.exe index.py
    ```

La simulación se ejecutará por un tiempo definido en `SIM_TIME` dentro de `index.py` (actualmente 24 horas en minutos de simulación).

## Salida

Al finalizar, el script imprimirá en la consola los siguientes resultados de la simulación:
*   Intentos de producción de caramelos (M1).
*   Caramelos defectuosos (M1).
*   Caramelos buenos enviados a Buffer1.
*   Cajas empaquetadas (M2).
*   Cajas selladas (M3).
*   Throughput (cajas selladas por minuto).
*   Tiempo promedio en sistema por caja.
*   WIP promedio en Buffer1 (caramelos).
*   WIP promedio en Buffer2 (cajas).

## Generación de Números Aleatorios

La simulación utiliza la clase `ValidatedRandom` del módulo `aleatorios` (específicamente de `aleatorios/src/modelos/validated_random.py`) para la generación de tiempos de procesamiento y la probabilidad de defectos. Actualmente, se inicializa con una semilla fija (`seed=12345`) en `index.py` para asegurar la reproducibilidad de los resultados.
