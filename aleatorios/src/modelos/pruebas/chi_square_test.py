"""
Módulo que implementa la prueba de Chi Cuadrado para validar secuencias de números aleatorios.

La prueba Chi Cuadrado evalúa la uniformidad de la distribución de números
comparando las frecuencias observadas con las esperadas.

Descripción detallada:
- Propósito: Validar la hipótesis de uniformidad en una secuencia de números aleatorios
- Funcionamiento: Divide el rango de números en intervalos y compara frecuencias
- Hipótesis nula (H0): Los números siguen una distribución uniforme
- Hipótesis alternativa (H1): Los números no siguen una distribución uniforme
- Nivel de significancia predeterminado: 0.05 (5%)
"""

import numpy as np
from scipy import stats
from typing import List, Optional

class ChiSquareTest:
    """
    Implementa la prueba estadística Chi Cuadrado para evaluar uniformidad.

    Atributos:
        numbers (List[float]): Secuencia de números a evaluar
        n_intervals (int): Número de intervalos para la prueba
        n (int): Cantidad total de números
        intervals (List[tuple]): Lista de tuplas con los límites de cada intervalo
        observed_freq (List[int]): Frecuencias observadas en cada intervalo
        expected_freq (float): Frecuencia esperada para cada intervalo
        chi_square (float): Estadístico chi cuadrado calculado
        critical_value (float): Valor crítico de la distribución chi cuadrado
        alpha (float): Nivel de significancia de la prueba
        passed (bool): Resultado de la prueba
    """
    def __init__(self, numbers: List[float], n_intervals: int = 10):
        self.numbers = numbers
        self.n = len(numbers)
        self.n_intervals = n_intervals
        self.intervals = []
        self.observed_freq = []
        self.expected_freq = self.n / self.n_intervals
        self.chi_square = 0.0
        self.critical_value = 0.0
        self.alpha = 0.05
        self.passed = False

    def calculate_intervals(self):
        """
        Calcula los intervalos para la prueba.

        Divide el rango de números en n_intervals intervalos de igual tamaño.
        Cada intervalo se almacena como una tupla (límite_inferior, límite_superior).
        """
        min_val = min(self.numbers)
        max_val = max(self.numbers)
        interval_size = (max_val - min_val) / self.n_intervals
        for i in range(self.n_intervals):
            lower = min_val + i * interval_size
            upper = lower + interval_size
            self.intervals.append((lower, upper))

    def calculate_frequencies(self):
        """
        Calcula las frecuencias observadas en cada intervalo.

        Recorre la lista de números y cuenta cuántos caen en cada intervalo.
        El último intervalo incluye su límite superior para incluir el valor máximo.
        """
        self.observed_freq = [0] * self.n_intervals
        for num in self.numbers:
            for i, (lower, upper) in enumerate(self.intervals):
                if lower <= num < upper or (i == self.n_intervals - 1 and num == upper):
                    self.observed_freq[i] += 1
                    break

    def calculate_chi_square(self):
        """
        Calcula el estadístico chi cuadrado.

        Utiliza la fórmula: Σ((O - E)²/E) donde:
        O: Frecuencia observada
        E: Frecuencia esperada
        """
        self.chi_square = sum(
            ((observed - self.expected_freq) ** 2) / self.expected_freq
            for observed in self.observed_freq
        )

    def calculate_critical_value(self):
        """
        Calcula el valor crítico de chi cuadrado.

        Utiliza la distribución chi cuadrado con (n_intervals - 1) grados de libertad
        y el nivel de significancia alpha para determinar el valor crítico.
        """
        df = self.n_intervals - 1
        self.critical_value = stats.chi2.ppf(1 - self.alpha, df)

    def evaluate_test(self):
        """
        Ejecuta la prueba completa de Chi Cuadrado.

        Proceso:
        1. Calcula los intervalos
        2. Determina las frecuencias observadas
        3. Calcula el estadístico chi cuadrado
        4. Obtiene el valor crítico
        5. Compara y determina si la prueba es exitosa
        """
        self.calculate_intervals()
        self.calculate_frequencies()
        self.calculate_chi_square()
        self.calculate_critical_value()
        self.passed = self.chi_square <= self.critical_value
