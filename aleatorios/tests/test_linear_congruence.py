import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', '..')))
# Insertar carpeta 'src' en sys.path para importar modelos desde src/modelos

import unittest
from modelos.linear_congruence import LinearCongruenceRandom
from modelos.pruebas.chi2_test import ChiTest
from modelos.pruebas.ks_test import KsTest
from modelos.pruebas.variance_test import VarianceTest
from modelos.pruebas.poker_test import PokerTest

class TestLinearCongruenceRandom(unittest.TestCase):
    def setUp(self):
        """
        Configura el generador de números aleatorios para todas las pruebas.
        
        Parámetros:
            seed_value: 12345 - Semilla inicial para reproducibilidad
            n_samples: 10000 - Cantidad de muestras para las pruebas estadísticas
        """
        self.rng = LinearCongruenceRandom(seed_value=12345)
        self.n_samples = 10000
        self.significance_level = 0.05

    def test_range(self):
        """
        Verifica que los números generados estén en el rango [0,1).
        
        Realiza 1000 iteraciones comprobando que:
        - Cada número sea >= 0.0
        - Cada número sea < 1.0
        """
        generated_numbers = [self.rng.random() for _ in range(1000)]
        for num in generated_numbers:
            self.assertGreaterEqual(num, 0.0)
            self.assertLess(num, 1.0)
        
        # Verificar valores extremos
        min_value = min(generated_numbers)
        max_value = max(generated_numbers)
        self.assertGreaterEqual(min_value, 0.0, "El valor mínimo debe ser mayor o igual a 0")
        self.assertLess(max_value, 1.0, "El valor máximo debe ser menor que 1")

    def test_chi_squared(self):
        """
        Prueba chi-cuadrado para verificar la uniformidad de la distribución.
        
        Utiliza 10000 muestras y verifica:
        - La distribución de frecuencias en intervalos
        - Nivel de significancia: 0.05
        - Ho: La distribución es uniforme
        """
        numbers = [self.rng.random() for _ in range(self.n_samples)]
        test = ChiTest(ri_values=numbers)
        test.checkTest()
        self.assertTrue(test.passed, "La prueba Chi-cuadrado falló - la distribución no es uniforme")

    def test_ks(self):
        """
        Prueba Kolmogorov-Smirnov para uniformidad de la distribución.
        
        Utiliza 10000 muestras y verifica:
        - La máxima diferencia entre la distribución teórica y la empírica
        - Nivel de significancia: 0.05
        - Ho: La distribución es uniforme
        """
        numbers = [self.rng.random() for _ in range(self.n_samples)]
        test = KsTest(ri_nums=numbers)
        test.checkTest()
        self.assertTrue(test.passed, "La prueba KS falló - la distribución no es uniforme")

    def test_variance(self):
        """
        Prueba de varianza para verificar la dispersión de los números.
        
        Utiliza 10000 muestras y verifica:
        - La varianza se encuentre dentro de los límites aceptables
        - Para una distribución U(0,1), la varianza teórica es 1/12 ≈ 0.0833
        - Nivel de significancia: 0.05
        """
        numbers = [self.rng.random() for _ in range(self.n_samples)]
        test = VarianceTest(numbers)
        test.evaluate_test()
        self.assertTrue(test.passed, "La prueba de varianza falló - la dispersión no es adecuada")

    def test_poker(self):
        """
        Prueba de poker para verificar la independencia entre números.
        
        Utiliza 10000 muestras y verifica:
        - Analiza patrones en los dígitos de los números generados
        - Compara las frecuencias observadas con las esperadas
        - Nivel de significancia: 0.05
        - Ho: Los dígitos son independientes entre sí
        
        Notas:
        - La prueba utiliza la clasificación de manos de poker para evaluar la independencia
        - Se espera que las frecuencias observadas sigan una distribución chi-cuadrado
        """
        numbers = [self.rng.random() for _ in range(self.n_samples)]
        test = PokerTest(numbers)
        test.check_poker()
        self.assertTrue(test.passed, "La prueba de poker falló - los números no son independientes")

    def test_seed_reproducibility(self):
        """
        Verifica que la misma semilla produzca la misma secuencia de números.
        
        Compara:
        - Dos generadores inicializados con la misma semilla (12345)
        - Verifica 1000 números generados consecutivamente
        - Los números deben ser exactamente iguales en ambas secuencias
        """
        rng1 = LinearCongruenceRandom(seed_value=12345)
        rng2 = LinearCongruenceRandom(seed_value=12345)
        
        numbers1 = [rng1.random() for _ in range(1000)]
        numbers2 = [rng2.random() for _ in range(1000)]
        
        self.assertEqual(numbers1, numbers2, "Las secuencias no son idénticas para la misma semilla")

if __name__ == '__main__':
    unittest.main()
