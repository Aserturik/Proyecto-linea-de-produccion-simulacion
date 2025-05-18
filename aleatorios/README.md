# modelos_rng_validated

Generador de números pseudoaleatorios basado en el algoritmo de Congruencia Lineal (LCG) con validación estadística.

## Instalación (modo editable)

```bash
cd /home/alex/repos/python/modelos
pip install -e .
```

## Uso

```python
from modelos import ValidatedRandom, ValidationError

try:
    rng = ValidatedRandom(seed=12345)
    print(rng.random())
    print(rng.randint(1, 100))
    print(rng.gauss(0, 1))
except ValidationError as e:
    print(f"Error de validación: {e}")
```

## Estructura

- `src/modelos/` contiene el paquete principal:
  - `validated_random.py`: Interfaz pública con validación.
  - `linear_congruence.py` y `prng.py`: Implementaciones LCG.
  - `pruebas/`: Pruebas estadísticas internas.
  - `exceptions.py`: Excepciones personalizadas.

- `tests/` contiene las pruebas unitarias:
  - `test_linear_congruence.py`.
  - `test_validated_random.py`.

## Dependencias

- numpy
- scipy
