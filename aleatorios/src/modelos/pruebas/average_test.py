"""
Módulo que implementa la prueba de promedios para validar secuencias de números aleatorios.

Esta prueba verifica que el promedio de la secuencia se encuentre dentro de los
límites esperados para una distribución uniforme.

Relaciones:
- Consume números generados por implementaciones de PRNG
- Es la prueba más básica, complementa a KsTest y PokerTest
"""

from statistics import mean
from math import sqrt
from scipy.stats import norm
from typing import List, Optional

# Clase que implementa la prueba de promedio para una secuencia de números
class AverageTest:
    # Inicializa la instancia con una lista de números
    def __init__(self, numbers: List[float], alpha: float = 0.05):
        self.numbers = numbers  # Lista de números ingresados
        self.average = 0
        self.alpha = alpha # Use the provided alpha
        self.acceptation = 1 - alpha # Update acceptation based on alpha
        self.passed = False
        self.n = len(numbers)
        self.z = 0.0
        self.upper_limit = 0.0
        self.lower_limit = 0.0

    # Calcula el promedio de la lista de números
    def compute_average(self):
        if self.n:
            self.average = mean(self.numbers)

    # Calcula el valor Z a partir de alpha
    def compute_z(self):
        self.z = norm.ppf(1 - (self.alpha / 2))

    # Calcula el límite superior de la prueba
    def compute_upper_limit(self):
        if self.n > 0:
            self.upper_limit = 0.5 + (self.z * (1 / sqrt(12 * self.n)))

    # Calcula el límite inferior de la prueba
    def compute_lower_limit(self):
        if self.n > 0:
            self.lower_limit = 0.5 - (self.z * (1 / sqrt(12 * self.n)))

    # Realiza todos los cálculos y determina si la prueba se pasa
    def evaluate_test(self):
        self.compute_average()
        self.compute_z()
        self.compute_upper_limit()
        self.compute_lower_limit()
        self.passed = self.lower_limit <= self.average <= self.upper_limit

    # Reinicia los valores de la prueba a sus valores iniciales
    def reset(self):
        self.average = 0
        self.alpha = 0.05
        self.acceptation = 0.95
        self.passed = False
        self.z = 0.0
        self.upper_limit = 0.0
        self.lower_limit = 0.0
