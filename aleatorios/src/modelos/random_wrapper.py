"""
Módulo que provee una interfaz compatible con random usando nuestro generador validado.
"""
from typing import Sequence, TypeVar, List, Any
import math
from .prng import PRNG
from .linear_congruence import LinearCongruenceRandom

T = TypeVar('T')

class RandomWrapper:
    """
    Wrapper que proporciona una interfaz compatible con random usando
    nuestro generador de números pseudoaleatorios validado.
    """
    def __init__(self, seed: int = None):
        self._rng = LinearCongruenceRandom(seed_value=seed)
    
    def seed(self, seed: int) -> None:
        """Establece la semilla del generador."""
        self._rng.seed(seed)
    
    def random(self) -> float:
        """Retorna un número aleatorio en [0.0, 1.0)."""
        return self._rng.random()
    
    def uniform(self, a: float, b: float) -> float:
        """Retorna un número aleatorio N tal que a <= N <= b."""
        return self._rng.uniform(a, b)
    
    def randint(self, a: int, b: int) -> int:
        """Retorna un entero aleatorio N tal que a <= N <= b."""
        return self._rng.randint(a, b)
    
    def choice(self, seq: Sequence[T]) -> T:
        """Retorna un elemento aleatorio de la secuencia."""
        return self._rng.choice(seq)
    
    def choices(self, population: Sequence[T], weights=None, k: int = 1) -> List[T]:
        """
        Retorna k elementos aleatorios de population con reemplazo.
        Si se especifican weights, la selección es ponderada.
        """
        if weights is None:
            return [self.choice(population) for _ in range(k)]
        
        # Normalizar pesos
        total = sum(weights)
        cumweights = []
        cumsum = 0
        for w in weights:
            cumsum += w
            cumweights.append(cumsum / total)
        
        result = []
        for _ in range(k):
            r = self.random()
            for i, cw in enumerate(cumweights):
                if r <= cw:
                    result.append(population[i])
                    break
        return result
    
    def shuffle(self, x: List[Any]) -> None:
        """Mezcla la secuencia x in-place."""
        self._rng.shuffle(x)
    
    def sample(self, population: Sequence[T], k: int) -> List[T]:
        """Retorna k elementos únicos elegidos de population."""
        return self._rng.sample(population, k)

# Crear una instancia global para uso como reemplazo de random
_instance = RandomWrapper()

# Exponer los métodos de la instancia global como funciones del módulo
seed = _instance.seed
random = _instance.random
uniform = _instance.uniform
randint = _instance.randint
choice = _instance.choice
choices = _instance.choices
shuffle = _instance.shuffle
sample = _instance.sample