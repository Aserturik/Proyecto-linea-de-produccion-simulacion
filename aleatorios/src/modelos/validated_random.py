from typing import Sequence, TypeVar, List, Any, Optional
import time

from .linear_congruence import LinearCongruenceRandom
from .exceptions import ValidationError
# Importar pruebas estadísticas
from .pruebas.average_test import AverageTest
from .pruebas.chi2_test import ChiTest
from .pruebas.ks_test import KsTest
from .pruebas.variance_test import VarianceTest
from .pruebas.poker_test import PokerTest

T = TypeVar('T')

class ValidatedRandom:
    """
    Generador LCG validado por pruebas estadísticas antes de servir números.
    """
    def __init__(self, seed: Optional[int] = None, batch_size: int = 10000,
                 significance_level: float = 0.05, max_attempts: int = 5):
        self._rng = LinearCongruenceRandom(seed_value=seed)
        self._batch_size = batch_size
        self._alpha = significance_level
        self._max_attempts = max_attempts
        self._validated_batch: List[float] = []
        self._batch_iterator = iter(self._validated_batch)

    def _run_tests(self, numbers: List[float]) -> bool:
        tests = [
            AverageTest(numbers, alpha=self._alpha),
            ChiTest(ri_values=numbers, alpha=self._alpha),
            KsTest(ri_nums=numbers, alpha=self._alpha),
            VarianceTest(numbers, alpha=self._alpha),
            PokerTest(numbers, alpha=self._alpha)
        ]
        for test in tests:
            if hasattr(test, 'checkTest'):
                test.checkTest()
            elif hasattr(test, 'evaluate_test'):
                test.evaluate_test()
            elif hasattr(test, 'check_poker'):
                test.check_poker()
            if not getattr(test, 'passed', False):
                return False
        return True

    def _generate_and_validate_batch(self):
        attempts = 0
        while attempts < self._max_attempts:
            batch = [self._rng.random() for _ in range(self._batch_size)]
            if self._run_tests(batch):
                self._validated_batch = batch
                self._batch_iterator = iter(self._validated_batch)
                return
            attempts += 1
        raise ValidationError(f"No se pudo validar lote después de {self._max_attempts} intentos.")

    def seed(self, value: int) -> None:
        self._rng.seed(value)
        self._validated_batch = []
        self._batch_iterator = iter(self._validated_batch)

    def random(self) -> float:
        try:
            return next(self._batch_iterator)
        except StopIteration:
            self._generate_and_validate_batch()
            return next(self._batch_iterator)

    def randint(self, a: int, b: int) -> int:
        val = self.random()
        scaled = val * (b - a + 1)
        return min(a + int(scaled), b)

    def uniform(self, a: float, b: float) -> float:
        return a + (b - a) * self.random()

    def choice(self, seq: Sequence[T]) -> T:
        if not seq:
            raise IndexError("Secuencia vacía")
        return seq[self.randint(0, len(seq) - 1)]

    def shuffle(self, x: List[Any]) -> None:
        for i in range(len(x)-1, 0, -1):
            j = self.randint(0, i)
            x[i], x[j] = x[j], x[i]

    def sample(self, population: Sequence[T], k: int) -> List[T]:
        if k < 0 or k > len(population):
            raise ValueError("Tamaño de muestra inválido")
        arr = list(population)
        for i in range(k):
            j = self.randint(i, len(arr)-1)
            arr[i], arr[j] = arr[j], arr[i]
        return arr[:k]

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        import math
        u1 = self.random() or 1e-9
        u2 = self.random()
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return mu + z0 * sigma
