"""
Módulo que implementa la prueba de póker para validar secuencias de números aleatorios.

La prueba de póker analiza patrones en los dígitos de los números generados,
clasificándolos en diferentes "manos" como en el juego de póker.

Relaciones:
- Consume números generados por implementaciones de PRNG
- Puede usarse en conjunto con KsTest y AverageTest para validación completa
"""

import numpy as np
import scipy.stats as st
from typing import List, Optional


class PokerTest:

    def __init__(self, ri_nums, alpha: float = 0.05):
        self.ri_nums = ri_nums
        # Probabilidades teóricas para 5 dígitos
        self.prob = [0.3024, 0.504, 0.108, 0.072, 0.009, 0.0045, 0.0001]
        self.oi = [0, 0, 0, 0, 0, 0, 0]
        self.ei = []
        self.eid = []
        self.passed = False
        self.n = len(ri_nums)
        self.total_sum = 0.0
        self.alpha = alpha
        self.chi_reverse = st.chi2.ppf(1 - self.alpha, 6)

    # Realiza la prueba de poker y determina si ha pasado.
    def check_poker(self):
        self.calculate_oi()
        self.calculate_ei()
        self.calculate_eid()
        self.calculate_total_sum()
        if self.total_sum < self.chi_reverse:
            self.passed = True
        else:
            self.passed = False
        return self.passed

    # Calcula la suma total de (oi - ei)^2 / ei para cada mano.
    def calculate_total_sum(self):
        for num in self.eid:
            self.total_sum += num

    # Calcula las frecuencias observadas de cada mano de poker.
    def calculate_oi(self):
        for n in self.ri_nums:
            # Convertir el número a cadena con exactamente 5 dígitos decimales
            num = format(n, '.5f').split('.')[1]
            if len(num) != 5:  # Asegurarse de que tengamos exactamente 5 dígitos
                continue
                
            if self.all_diff(num):
                self.oi[0] += 1
            elif self.all_same(num):
                self.oi[6] += 1
            elif self.four_of_a_kind(num):
                self.oi[5] += 1
            elif self.one_three_of_a_kind_and_one_pair(num):
                self.oi[4] += 1
            elif self.only_three_of_a_kind(num):
                self.oi[3] += 1
            elif self.two_pairs(num):
                self.oi[2] += 1
            elif self.only_one_pair(num):
                self.oi[1] += 1

    def all_diff(self, numstr):
        return len(numstr) == len(set(numstr))

    def all_same(self, numstr):
        return len(set(numstr)) == 1

    def four_of_a_kind(self, numstr):
        count = {}
        for char in numstr:
            count[char] = count.get(char, 0) + 1
        num_quads = sum(1 for freq in count.values() if freq == 4)
        return num_quads == 1

    def two_pairs(self, numstr):
        count = {}
        for char in numstr:
            count[char] = count.get(char, 0) + 1
        num_pairs = sum(1 for freq in count.values() if freq == 2)
        return num_pairs == 2

    def one_three_of_a_kind_and_one_pair(self, numstr):
        count = {}
        for char in numstr:
            count[char] = count.get(char, 0) + 1
        num_pairs = sum(1 for freq in count.values() if freq == 2)
        num_triples = sum(1 for freq in count.values() if freq == 3)
        return num_pairs == 1 and num_triples == 1

    def only_one_pair(self, numstr):
        count = {}
        for char in numstr:
            count[char] = count.get(char, 0) + 1
        num_pairs = sum(1 for freq in count.values() if freq == 2)
        return num_pairs == 1

    def only_three_of_a_kind(self, numstr):
        count = {}
        for char in numstr:
            count[char] = count.get(char, 0) + 1
        num_triples = sum(1 for freq in count.values() if freq == 3)
        return num_triples == 1

    # Calcula las frecuencias esperadas de cada mano de poker.
    def calculate_ei(self):
        for i in range(7):
            self.ei.append(self.prob[i] * self.n)

    # Calcula (oi - ei)^2 / ei para cada mano.
    def calculate_eid(self):
        for i in range(len(self.oi)):
            expected = self.prob[i] * self.n
            if expected != 0:
                self.eid.append(((self.oi[i] - expected) ** 2) / expected)

if __name__ == "__main__":
    # Solicita al usuario que ingrese los números Ri separados por comas
    user_input = input("Ingresa los números Ri separados por comas: ")
    try:
        # Convertir la entrada a una lista de números float
        ri_nums = [float(x.strip()) for x in user_input.split(",")]
    except ValueError:
        print("Error: asegúrate de ingresar únicamente números separados por comas.")
        exit(1)

    # Crea la instancia de PokerTest y ejecuta la prueba
    poker_test = PokerTest(ri_nums)
    passed = poker_test.check_poker()

    # Muestra los resultados en consola
    print("\nNúmeros Ri ingresados:", poker_test.ri_nums)
    print("Frecuencias Observadas (oi):", poker_test.oi)
    print("Frecuencias Esperadas (ei):", poker_test.ei)
    print("Valores calculados ((Oi - Ei)^2/Ei):", poker_test.eid)
    print("Suma Total:", round(poker_test.total_sum, 4))
    print("Valor Crítico de Chi2:", round(poker_test.chi_reverse, 4))
    print("¿Prueba de Poker superada?:", passed)
