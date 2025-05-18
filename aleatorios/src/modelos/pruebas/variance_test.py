"""
Módulo que implementa la prueba de Varianza para validar secuencias de números aleatorios.

La prueba de Varianza verifica que la dispersión de los números generados
se ajuste a lo esperado para una distribución uniforme.

Relaciones:
- Consume números generados por implementaciones de PRNG
- Complementa la prueba de promedios (AverageTest)
"""

import numpy as np
from scipy import stats
from typing import List, Optional

class VarianceTest:
    def __init__(self, numbers: List[float], alpha: float = 0.05):
        self.numbers = numbers
        self.n = len(numbers)
        self.variance = 0.0
        self.theoretical_variance = 1/12  # Varianza teórica para distribución uniforme [0,1]
        self.lower_limit = 0.0
        self.upper_limit = 0.0
        self.alpha = alpha
        self.passed = False

    def calculate_variance(self):
        """Calcula la varianza muestral."""
        self.variance = np.var(self.numbers)

    def calculate_limits(self):
        """Calcula los límites de aceptación usando chi cuadrado."""
        df = self.n - 1
        chi_lower = stats.chi2.ppf(self.alpha/2, df)
        chi_upper = stats.chi2.ppf(1 - self.alpha/2, df)
        
        self.lower_limit = (chi_lower / df) * self.theoretical_variance
        self.upper_limit = (chi_upper / df) * self.theoretical_variance

    def evaluate_test(self):
        """Ejecuta la prueba completa."""
        self.calculate_variance()
        self.calculate_limits()
        self.passed = self.lower_limit <= self.variance <= self.upper_limit
