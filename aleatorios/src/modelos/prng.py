"""
Módulo base para generadores de números pseudoaleatorios (PRNG).

Este módulo define la interfaz base que deben implementar todos los generadores
de números pseudoaleatorios en el sistema. Proporciona métodos útiles que construyen
sobre el método básico random().

Relaciones:
- Es la clase base para implementaciones específicas de PRNGs
- Sus números generados son consumidos por los módulos de prueba (AverageTest, KsTest, PokerTest)
"""

from abc import ABC, abstractmethod
from typing import List, Any, Optional, Sequence
import math

class PRNG(ABC):
    """Clase base abstracta para generadores de números pseudoaleatorios."""
    
    @abstractmethod
    def seed(self, value: int) -> None:
        """Establece la semilla del generador."""
        pass
    
    @abstractmethod
    def random(self) -> float:
        """Retorna un número float aleatorio en el rango [0.0, 1.0)."""
        pass

    def randint(self, a: int, b: int) -> int:
        """Retorna un entero aleatorio N tal que a <= N <= b."""
        return a + int(self.random() * (b - a + 1))

    def uniform(self, a: float, b: float) -> float:
        """Retorna un número float aleatorio N tal que a <= N <= b."""
        return a + (b - a) * self.random()

    def choice(self, seq: Sequence[Any]) -> Any:
        """Retorna un elemento aleatorio de la secuencia no vacía."""
        if not seq:
            raise IndexError("No se puede elegir de una secuencia vacía")
        return seq[self.randint(0, len(seq) - 1)]

    def shuffle(self, x: List[Any]) -> None:
        """Mezcla la lista x in-place."""
        for i in reversed(range(1, len(x))):
            j = self.randint(0, i)
            x[i], x[j] = x[j], x[i]

    def sample(self, population: Sequence[Any], k: int) -> List[Any]:
        """Retorna k elementos únicos elegidos de la población."""
        if k < 0:
            raise ValueError("El tamaño de la muestra debe ser no negativo")
        n = len(population)
        if k > n:
            raise ValueError("El tamaño de la muestra no puede ser mayor que el de la población")
        
        result = list(population)
        for i in range(k):
            j = self.randint(i, n - 1)
            result[i], result[j] = result[j], result[i]
        return result[:k]

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Retorna un número aleatorio con distribución normal."""
        # Implementación del método Box-Muller
        u1 = self.random()
        u2 = self.random()
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return mu + z0 * sigma
