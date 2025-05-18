#!/usr/bin/env python
"""
Pruebas de calidad para el generador de números aleatorios de congruencia lineal.

Este script prueba la calidad del generador y valida que cumple con las pruebas estadísticas.
"""

import sys
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
from src.modelos.linear_congruence import LinearCongruenceRandom
from src.modelos.validated_random import ValidatedRandom
from src.modelos.pruebas.chi_square_test import ChiSquareTest
from src.modelos.pruebas.ks_test import KsTest
from src.modelos.pruebas.variance_test import VarianceTest
from src.modelos.pruebas.poker_test import PokerTest
from src.modelos.pruebas.average_test import AverageTest

class RandomTester:
    """Clase para probar la calidad del generador de números aleatorios."""
    
    def __init__(self, sample_size=10000, num_tests=3):
        """Inicializa el probador con tamaño de muestra y número de pruebas."""
        self.sample_size = sample_size
        self.num_tests = num_tests
        self.results = []
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas configuradas."""
        print("="*60)
        print(f"PRUEBA DE CALIDAD DEL GENERADOR DE NÚMEROS ALEATORIOS")
        print(f"Tamaño de muestra: {self.sample_size}, Número de pruebas: {self.num_tests}")
        print("="*60)
        
        # Resultados por cada tipo de generador
        validated_results = {"passed": 0, "total": self.num_tests * 5}  # 5 pruebas por cada ejecución
        direct_results = {"passed": 0, "total": self.num_tests * 5}
        
        for i in range(self.num_tests):
            seed = (i + 1) * 12345
            print(f"\n[Prueba #{i+1}] Semilla: {seed}")
            
            # Probar generador validado
            print("\n--- Probando ValidatedRandom ---")
            validated_pass_count = self.test_validated_generator(seed)
            validated_results["passed"] += validated_pass_count
            
            # Probar generador directo
            print("\n--- Probando LinearCongruenceRandom ---")
            direct_pass_count = self.test_direct_generator(seed)
            direct_results["passed"] += direct_pass_count

        # Mostrar resultados finales
        print("\n" + "="*30 + " RESULTADOS FINALES " + "="*30)
        print(f"ValidatedRandom: {validated_results['passed']}/{validated_results['total']} pruebas exitosas ({validated_results['passed']/validated_results['total']*100:.1f}%)")
        print(f"LinearCongruenceRandom: {direct_results['passed']}/{direct_results['total']} pruebas exitosas ({direct_results['passed']/direct_results['total']*100:.1f}%)")
        
        # Demostrar características adicionales
        self.demo_features()
        
        # Generar gráficos para visualizar la distribución
        self.generate_distribution_plots()

    def test_validated_generator(self, seed):
        """Prueba el generador validado con la semilla dada."""
        try:
            rng = ValidatedRandom(seed)
            numbers = [rng.random() for _ in range(self.sample_size)]
            return self.run_statistical_tests(numbers, "Validado")
        except Exception as e:
            print(f"Error al probar ValidatedRandom: {e}")
            return 0

    def test_direct_generator(self, seed):
        """Prueba el generador directo con la semilla dada."""
        try:
            rng = LinearCongruenceRandom(seed)
            numbers = [rng.random() for _ in range(self.sample_size)]
            return self.run_statistical_tests(numbers, "Directo")
        except Exception as e:
            print(f"Error al probar LinearCongruenceRandom: {e}")
            return 0

    def run_statistical_tests(self, numbers, prefix):
        """Ejecuta todas las pruebas estadísticas en los números generados."""
        # Calcular estadísticas básicas
        mean = np.mean(numbers)
        variance = np.var(numbers)
        min_val = min(numbers)
        max_val = max(numbers)
        
        print(f"  Media: {mean:.6f} (Teórica: 0.5)")
        print(f"  Varianza: {variance:.6f} (Teórica: 0.0833)")
        print(f"  Rango: [{min_val:.6f}, {max_val:.6f}]")
        
        # Ejecutar pruebas estadísticas
        print("\n  Pruebas estadísticas:")
        
        # 1. Chi-cuadrado
        chi_test = ChiSquareTest(numbers)
        chi_passed = chi_test.evaluate_test()
        chi_value = chi_test.chi_square
        chi_critical = chi_test.critical_value
        
        # 2. KS
        ks_test = KsTest(numbers)
        ks_test.checkTest()
        ks_passed = ks_test.passed
        dmax = ks_test.d_max
        dmax_critical = ks_test.d_max_p
        
        # 3. Varianza
        var_test = VarianceTest(numbers)
        var_passed = var_test.evaluate_test()
        variance_value = var_test.variance
        var_limits = (var_test.lower_limit, var_test.upper_limit)
        
        # 4. Póker
        poker_test = PokerTest(numbers)
        poker_passed = poker_test.check_poker()
        poker_value = poker_test.total_sum
        poker_critical = poker_test.chi_reverse
        
        # 5. Media
        avg_test = AverageTest(numbers)
        avg_passed = avg_test.evaluate_test()
        avg_value = avg_test.get_average()
        avg_limits = (avg_test.get_lower_limit(), avg_test.get_upper_limit())
        
        # Tabla de resultados
        results = [
            ["Chi-cuadrado", "PASÓ ✓" if chi_passed else "FALLÓ ✗", f"{chi_value:.4f}", f"{chi_critical:.4f}"],
            ["K-S", "PASÓ ✓" if ks_passed else "FALLÓ ✗", f"{dmax:.4f}", f"{dmax_critical:.4f}"],
            ["Varianza", "PASÓ ✓" if var_passed else "FALLÓ ✗", f"{variance_value:.4f}", f"[{var_limits[0]:.4f}, {var_limits[1]:.4f}]"],
            ["Póker", "PASÓ ✓" if poker_passed else "FALLÓ ✗", f"{poker_value:.4f}", f"{poker_critical:.4f}"],
            ["Media", "PASÓ ✓" if avg_passed else "FALLÓ ✗", f"{avg_value:.4f}", f"[{avg_limits[0]:.4f}, {avg_limits[1]:.4f}]"]
        ]
        
        # Mostrar tabla
        print(tabulate(results, headers=["Prueba", "Resultado", "Valor", "Crítico/Límites"], tablefmt="grid"))
        
        # Resultado global
        all_passed = chi_passed and ks_passed and var_passed and poker_passed and avg_passed
        pass_count = sum([chi_passed, ks_passed, var_passed, poker_passed, avg_passed])
        print(f"\n  Resultado global: {pass_count}/5 pruebas pasadas")
        print(f"  {prefix}: {'TODAS LAS PRUEBAS PASARON ✓' if all_passed else 'ALGUNAS PRUEBAS FALLARON ✗'}")
        
        return pass_count

    def demo_features(self):
        """Demuestra características adicionales del generador."""
        print("\n" + "="*30 + " DEMOSTRACIÓN DE CARACTERÍSTICAS " + "="*30)
        
        # Crear generador con semilla fija para reproducibilidad
        rng = ValidatedRandom(12345)
        
        # 1. Números en rango [0,1)
        print("\n[1] 5 números aleatorios en [0,1):")
        for i in range(5):
            print(f"  {rng.random():.8f}")
        
        # 2. Enteros en un rango
        print("\n[2] Simulación de 10 tiradas de dado (1-6):")
        dice_freq = [0] * 6
        for i in range(10):
            roll = rng.randint(1, 6)
            dice_freq[roll-1] += 1
            print(f"  Tirada {i+1}: {roll}")
        
        print("\n  Frecuencias de cada valor:")
        for i, freq in enumerate(dice_freq):
            print(f"  {i+1}: {freq} {'*' * freq}")
        
        # 3. Números en rango personalizado
        print("\n[3] 5 números en rango uniforme [10, 20]:")
        for i in range(5):
            print(f"  {rng.uniform(10, 20):.4f}")
        
        # 4. Números con distribución normal
        print("\n[4] 5 números con distribución normal (µ=50, σ=10):")
        for i in range(5):
            print(f"  {rng.gauss(50, 10):.4f}")
        
        # 5. Selección aleatoria
        opciones = ["Rojo", "Verde", "Azul", "Amarillo", "Negro"]
        print(f"\n[5] Selección aleatoria de {opciones}:")
        for i in range(5):
            print(f"  Elección {i+1}: {rng.choice(opciones)}")
        
        # 6. Reproducibilidad con semillas iguales
        print("\n[6] Prueba de reproducibilidad (misma semilla = misma secuencia):")
        rng1 = LinearCongruenceRandom(54321)
        rng2 = LinearCongruenceRandom(54321)
        
        for i in range(5):
            val1 = rng1.random()
            val2 = rng2.random()
            print(f"  {val1:.8f} vs {val2:.8f}: {'Iguales ✓' if abs(val1-val2) < 1e-10 else 'Diferentes ✗'}")

    def generate_distribution_plots(self):
        """Genera gráficos de distribución para comparación visual."""
        try:
            # Crear generadores
            print("\nGenerando gráficos de distribución...")
            validated_rng = ValidatedRandom(12345)
            direct_rng = LinearCongruenceRandom(12345)
            
            # Generar muestras
            validated_nums = [validated_rng.random() for _ in range(100000)]
            direct_nums = [direct_rng.random() for _ in range(100000)]
            
            # Configurar gráfico
            plt.figure(figsize=(15, 10))
            
            # Histograma para ValidatedRandom
            plt.subplot(2, 2, 1)
            plt.hist(validated_nums, bins=50, alpha=0.7, color='blue')
            plt.title('Distribución de ValidatedRandom')
            plt.xlabel('Valor')
            plt.ylabel('Frecuencia')
            
            # Histograma para LinearCongruenceRandom
            plt.subplot(2, 2, 2)
            plt.hist(direct_nums, bins=50, alpha=0.7, color='green')
            plt.title('Distribución de LinearCongruenceRandom')
            plt.xlabel('Valor')
            plt.ylabel('Frecuencia')
            
            # QQ Plot para ValidatedRandom
            plt.subplot(2, 2, 3)
            validated_sorted = np.sort(validated_nums)
            n = len(validated_sorted)
            expected = np.linspace(0, 1, n, endpoint=False)  # Uniforme en [0,1)
            plt.scatter(expected, validated_sorted, s=1, alpha=0.5)
            plt.plot([0, 1], [0, 1], 'r--')  # Línea de 45 grados
            plt.title('QQ-Plot ValidatedRandom vs Uniforme')
            plt.xlabel('Teórico')
            plt.ylabel('Observado')
            
            # QQ Plot para LinearCongruenceRandom
            plt.subplot(2, 2, 4)
            direct_sorted = np.sort(direct_nums)
            plt.scatter(expected, direct_sorted, s=1, alpha=0.5)
            plt.plot([0, 1], [0, 1], 'r--')  # Línea de 45 grados
            plt.title('QQ-Plot LinearCongruenceRandom vs Uniforme')
            plt.xlabel('Teórico')
            plt.ylabel('Observado')
            
            # Guardar gráfico
            plt.tight_layout()
            plt.savefig('random_distribution_plots.png')
            print("Gráficos guardados en 'random_distribution_plots.png'")
        except Exception as e:
            print(f"Error al generar gráficos: {e}")


if __name__ == '__main__':
    # Tamaño de muestra por defecto
    sample_size = 10000
    
    # Permitir especificar tamaño de muestra por línea de comandos
    if len(sys.argv) > 1:
        try:
            sample_size = int(sys.argv[1])
        except ValueError:
            print(f"Tamaño de muestra inválido: {sys.argv[1]}, usando {sample_size}")
    
    # Ejecutar pruebas
    tester = RandomTester(sample_size=sample_size)
    tester.run_all_tests()