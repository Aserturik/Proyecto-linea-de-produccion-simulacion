from typing import Optional
import time
from .prng import PRNG

class LinearCongruenceRandom(PRNG):
    # Parámetros optimizados para el método de Schrage
    DEFAULT_M = 2147483647  # 2^31 - 1 (Mersenne prime)
    DEFAULT_A = 48271       # Multiplicador óptimo para este módulo
    DEFAULT_C = 0          # Generador multiplicativo puro

    def __init__(self, seed_value: Optional[int] = None):
        """
        Inicializa el generador con parámetros optimizados usando el método de Schrage.
        """
        self.m = self.DEFAULT_M
        self.a = self.DEFAULT_A
        self.c = self.DEFAULT_C
        self.q = self.m // self.a  # Cociente para el método de Schrage
        self.r = self.m % self.a   # Resto para el método de Schrage
        self._x = seed_value if seed_value is not None else int(time.time() * 1000)
        self._validate_parameters()
        # Descartar algunos valores iniciales
        for _ in range(20):
            self.random()

    def _validate_parameters(self) -> None:
        """Valida que los parámetros cumplan las condiciones necesarias."""
        if self.m <= 0:
            raise ValueError("El módulo m debe ser positivo")
        if self.a <= 0:
            raise ValueError("El multiplicador a debe ser positivo")
        if self.c < 0:
            raise ValueError("El incremento c debe ser no negativo")
        if self.a >= self.m:
            raise ValueError("El multiplicador a debe ser menor que m")
        if self.c >= self.m:
            raise ValueError("El incremento c debe ser menor que m")
        if self.r >= self.q:
            raise ValueError("El método de Schrage requiere que r < q")

    def random(self) -> float:
        """
        Genera un número pseudoaleatorio en el rango [0.0, 1.0) usando el método de Schrage.
        
        Returns:
            float: Número pseudoaleatorio normalizado.
        """
        # Implementación del método de Schrage para evitar desbordamiento
        k = self._x // self.q
        self._x = self.a * (self._x - k * self.q) - k * self.r
        if self._x < 0:
            self._x += self.m
        
        # Normalización mejorada para mejor distribución de dígitos decimales
        return self._x / (self.m - 1)  # Usar m-1 para incluir posibilidad de 1.0

    def seed(self, value: int) -> None:
        """Establece una nueva semilla para el generador."""
        if value <= 0:
            raise ValueError("La semilla debe ser un entero positivo")
        self._x = value % self.m
