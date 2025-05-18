# Simulación de Línea de Producción con Interfaz Web

Este proyecto simula una línea de producción de caramelos utilizando SimPy. La línea consta de tres máquinas y dos buffers intermedios. La simulación recopila estadísticas sobre la producción, defectos, tiempos en el sistema y niveles de inventario en proceso (WIP).

La simulación puede ser ejecutada directamente desde la línea de comandos (`index.py`) o a través de una interfaz web interactiva construida con Streamlit (`streamlit_app.py`).

## Estructura del Proyecto

*   `index.py`: Script que contiene la lógica principal de la simulación. Puede ser ejecutado directamente para una corrida con parámetros por defecto o importado por otras aplicaciones (como la app de Streamlit).
*   `streamlit_app.py`: Aplicación web desarrollada con Streamlit que proporciona una interfaz gráfica para configurar y ejecutar la simulación definida en `index.py`, visualizando los resultados de forma interactiva.
*   `aleatorios/`: Directorio que contiene la lógica para la generación de números pseudoaleatorios.
    *   `src/modelos/validated_random.py`: Clase `ValidatedRandom` utilizada por la simulación para generar números aleatorios U(0,1).
    *   `test_random_quality.py`: Script para probar la calidad de los generadores de números aleatorios (no se usa directamente en la simulación principal pero es parte del módulo `aleatorios`).
*   `requirements.txt`: Lista de dependencias de Python. Asegúrate de que incluya `simpy`, `numpy`, `tabulate`, `matplotlib`, `streamlit`, y `pandas`.

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
    Asegúrate de que tu entorno virtual esté activado. El archivo `requirements.txt` debería listar todas las dependencias necesarias. Si lo has actualizado para incluir `streamlit` y `pandas` (además de `simpy`, `numpy`, `tabulate`, `matplotlib`), ejecuta:
    ```bash
    pip install -r requirements.txt
    ```
    Si necesitas agregar `streamlit` y `pandas` manualmente:
    ```bash
    pip install streamlit pandas
    ```

## Ejecución

Existen dos formas de ejecutar la simulación:

### 1. Interfaz Web con Streamlit (Recomendado para interactividad)

Con el entorno virtual activado y las dependencias instaladas, puedes lanzar la aplicación web con:

```bash
streamlit run streamlit_app.py
```
Esto abrirá una página en tu navegador donde podrás ajustar los parámetros de la simulación y ver los resultados y gráficos actualizados dinámicamente.

### 2. Directamente desde la Línea de Comandos (`index.py`)

Puedes ejecutar la simulación con un conjunto de parámetros por defecto directamente desde la consola:

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
La simulación se ejecutará con los parámetros por defecto definidos en `index.py`.

## Salida

*   **Streamlit App (`streamlit_app.py`):** Los resultados se muestran de forma interactiva en la interfaz web, incluyendo métricas clave, gráficos de WIP, y la opción de ver las estadísticas detalladas.
*   **Línea de Comandos (`index.py`):** Al finalizar, el script imprimirá en la consola los siguientes resultados:
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

La simulación utiliza la clase `ValidatedRandom` del módulo `aleatorios` (específicamente de `aleatorios/src/modelos/validated_random.py`) para la generación de tiempos de procesamiento y la probabilidad de defectos. En `index.py`, se usa una semilla por defecto para la ejecución desde línea de comandos. En la app de Streamlit, la semilla es configurable a través de la interfaz.
