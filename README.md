# Simulación de Línea de Producción con Interfaz Web

Este proyecto simula una línea de producción de caramelos utilizando SimPy. La línea consta de tres máquinas y dos buffers intermedios. La simulación recopila estadísticas sobre la producción, defectos, tiempos en el sistema y niveles de inventario en proceso (WIP).

La simulación puede ser ejecutada directamente desde la línea de comandos (`event_driven_simulation.py`) o a través de una interfaz web interactiva construida con Streamlit (`event_driven_streamlit_app.py`).

## Estructura del Proyecto

* `event_driven_simulation.py`: Script que contiene la lógica principal de la simulación. Puede ser ejecutado directamente para una corrida con parámetros por defecto o importado por otras aplicaciones (como la app de Streamlit).
* `event_driven_streamlit_app.py`: Aplicación web desarrollada con Streamlit que proporciona una interfaz gráfica para configurar y ejecutar la simulación definida en `event_driven_simulation.py`, visualizando los resultados de forma interactiva.
* `aleatorios/`: Directorio que contiene la lógica para la generación de números pseudoaleatorios.
    * `src/modelos/validated_random.py`: Clase `ValidatedRandom` utilizada por la simulación para generar números aleatorios U(0,1).
    * `test_random_quality.py`: Script para probar la calidad de los generadores de números aleatorios (no se usa directamente en la simulación principal pero es parte del módulo `aleatorios`).
* `requirements.txt`: Lista de dependencias de Python. Asegúrate de que incluya `simpy`, `numpy`, `tabulate`, `matplotlib`, `streamlit`, y `pandas`.

## Requisitos Previos

* Python 3.x
* Un entorno virtual (recomendado)

## Configuración del Entorno

1. **Clonar el repositorio (si aplica):**
    ```bash
    git clone <repository-url>
    cd proyecto-linea-de-produccion-simulacion
    ```

2. **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    ```
    * En Linux/macOS (bash/zsh):
        ```bash
        source venv/bin/activate
        ```
    * En Linux/macOS (fish):
        ```bash
        source venv/bin/activate.fish
        ```
    * En Windows (PowerShell):
        ```ps1
        .\venv\Scripts\Activate.ps1
        ```
    * En Windows (CMD):
        ```bat
        .\venv\Scripts\activate.bat
        ```

3. **Instalar dependencias:**
    Asegúrate de que tu entorno virtual esté activado. El archivo `requirements.txt` debería listar todas las dependencias necesarias. Si lo has actualizado para incluir `streamlit` y `pandas` (además de `simpy`, `numpy`, `tabulate`, `matplotlib`), ejecuta:
    ```bash
    pip install -r requirements.txt
    ```
    Si necesitas agregar `streamlit` y `pandas` manualmente:
    ```bash
    pip install streamlit pandas
    ```

## Consideraciones para la Correcta Ejecución

Para asegurar la correcta ejecución del proyecto, ten en cuenta lo siguiente:

1. **Entorno Virtual Activado:** Antes de ejecutar cualquier script o la aplicación Streamlit, asegúrate de que el entorno virtual (`venv`) esté activado. Esto garantiza que se utilicen las versiones correctas de Python y las dependencias instaladas para el proyecto.
    * Comandos de activación:
        * Linux/macOS (bash/zsh): `source venv/bin/activate`
        * Linux/macOS (fish): `source venv/bin/activate.fish`
        * Windows (PowerShell): `.\\\\venv\\\\Scripts\\\\Activate.ps1`
        * Windows (CMD): `.\\\\venv\\\\Scripts\\\\activate.bat`

2. **Dependencias Instaladas:** Todas las dependencias listadas en `requirements.txt` deben estar instaladas en el entorno virtual. Si has clonado el repositorio recientemente o has modificado el archivo `requirements.txt`, ejecuta:

    ```bash
    pip install -r requirements.txt
    ```

3. **Interdependencia de Scripts:**
    * La aplicación Streamlit (`event_driven_streamlit_app.py`) importa y utiliza la lógica de simulación definida en `event_driven_simulation.py`. Por lo tanto, ambos archivos deben estar presentes en la estructura de directorios esperada.
    * El módulo `aleatorios` es utilizado por `event_driven_simulation.py` para la generación de números aleatorios.

4. **Ejecución de Scripts:**
    * **Streamlit App:** Para la interfaz web, ejecuta `streamlit run event_driven_streamlit_app.py`.
    * **Línea de Comandos:** Para una ejecución directa, utiliza `python event_driven_simulation.py` (o la ruta completa al intérprete del venv como se describe más abajo).

5. **Semilla de Aleatoriedad:**
    * Al ejecutar `event_driven_simulation.py` directamente, se utiliza una semilla por defecto para el generador de números aleatorios, lo que permite obtener resultados reproducibles si no se modifica el código.
    * En la aplicación Streamlit, la semilla es configurable a través de la interfaz de usuario, permitiendo explorar diferentes escenarios o asegurar la reproducibilidad al usar la misma semilla.

6. **Rutas de Archivos:** El proyecto asume una estructura de directorios específica, especialmente para la importación del módulo `aleatorios`. Mover o renombrar archivos o directorios clave podría causar errores de importación.

## Ejecución

Existen dos formas de ejecutar la simulación:

### 1. Interfaz Web con Streamlit (Recomendado para interactividad)

Con el entorno virtual activado y las dependencias instaladas, puedes lanzar la aplicación web con:

```bash
streamlit run event_driven_streamlit_app.py
```

Esto abrirá una página en tu navegador donde podrás ajustar los parámetros de la simulación y ver los resultados y gráficos actualizados dinámicamente.

### 2. Directamente desde la Línea de Comandos (`event_driven_simulation.py`)

Puedes ejecutar la simulación con un conjunto de parámetros por defecto directamente desde la consola:

```bash
python event_driven_simulation.py
```

O, para estar seguro de que se usa el intérprete del entorno virtual:

* En Linux/macOS:

    ```bash
    ./venv/bin/python event_driven_simulation.py
    ```
* En Windows:

    ```bash
    .\\\\venv\\\\Scripts\\\\python.exe event_driven_simulation.py
    ```

La simulación se ejecutará con los parámetros por defecto definidos en `event_driven_simulation.py`.

## Salida

* **Streamlit App (`event_driven_streamlit_app.py`):** Los resultados se muestran de forma interactiva en la interfaz web, incluyendo métricas clave, gráficos de WIP, y la opción de ver las estadísticas detalladas.
* **Línea de Comandos (`event_driven_simulation.py`):** Al finalizar, el script imprimirá en la consola los siguientes resultados:
    * Intentos de producción de caramelos (M1).
    * Caramelos defectuosos (M1).
    * Caramelos buenos enviados a Buffer1.
    * Cajas empaquetadas (M2).
    * Cajas selladas (M3).
    * Throughput (cajas selladas por minuto).
    * Tiempo promedio en sistema por caja.
    * WIP promedio en Buffer1 (caramelos).
    * WIP promedio en Buffer2 (cajas).

## Generación de Números Aleatorios

La simulación utiliza la clase `ValidatedRandom` del módulo `aleatorios` (específicamente de `aleatorios/src/modelos/validated_random.py`) para la generación de tiempos de procesamiento y la probabilidad de defectos. En `event_driven_simulation.py`, se usa una semilla por defecto para la ejecución desde línea de comandos. En la app de Streamlit, la semilla es configurable a través de la interfaz.
