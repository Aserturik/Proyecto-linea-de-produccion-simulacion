from scipy.stats import chi2
import numpy as np

class ChiTest:
    """
    Clase que implementa la Prueba de Chi-Cuadrado para una secuencia de números generados.
    """
    def __init__(self, ri_values=[], intervals_amount=8, a=8, b=10, alpha: float = 0.05):
        self.ri_values = ri_values          # Lista de números Ri ingresados
        self.ni_values = []                 # Lista de valores ni calculados
        self.a = a                          # Parámetro a para el cálculo de ni
        self.b = b                          # Parámetro b para el cálculo de ni
        self.niMin = 0                      # Valor mínimo de ni
        self.niMax = 0                      # Valor máximo de ni
        self.num_amount = len(ri_values)    # Cantidad total de números Ri
        self.intervals_amount = intervals_amount  # Cantidad de intervalos para la prueba
        self.intervals_values = []          # Límites de los intervalos
        self.frequency_obtained = []        # Frecuencias observadas en cada intervalo
        self.expected_frequency = []        # Frecuencias esperadas en cada intervalo
        self.chi_squared_values = []        # Valores de Chi-Cuadrado para cada intervalo
        self.chiReverse = 0                 # Valor crítico de la prueba de Chi-Cuadrado
        self.sumChi2 = 0                    # Sumatoria de los valores de Chi-Cuadrado
        self.alpha = alpha                  # Store alpha
        self.passed = False                 # Resultado de la prueba (superada o no)

    # Calcula y llena la lista 'ni_values' a partir de los números Ri
    def fillNiValues(self):
        for i in range(self.num_amount):
            value = self.a + (self.b - self.a) * self.ri_values[i]
            self.ni_values.append(value)

    # Ordena la lista de ni_values
    def sortNiArray(self):
        self.ni_values.sort()

    # Obtiene el valor mínimo de ni_values
    def obtainMinNiValue(self):
        self.niMin = min(self.ni_values)
        return self.niMin

    # Obtiene el valor máximo de ni_values
    def obtainMaxNiValue(self):
        self.niMax = max(self.ni_values)
        return self.niMax

    # Llena la lista de límites de intervalos (intervals_values)
    def fillIntervalsValuesArray(self):
        min_value = self.obtainMinNiValue()
        max_value = self.obtainMaxNiValue()
        self.intervals_values.append(min_value)
        for i in range(self.intervals_amount):
            value = round(self.intervals_values[i] + (max_value - min_value) / self.intervals_amount, 5)
            self.intervals_values.append(value)

    # Llena las listas de frecuencias observadas y esperadas
    def fillFrequenciesArrays(self):
        expected_freq = round(float(len(self.ni_values)) / self.intervals_amount, 2)
        for i in range(len(self.intervals_values) - 1):
            counter = 0
            for j in range(len(self.ni_values)):
                if self.ni_values[j] >= self.intervals_values[i] and self.ni_values[j] < self.intervals_values[i + 1]:
                    counter += 1
            self.frequency_obtained.append(counter)
            self.expected_frequency.append(expected_freq)

    # Llena la lista de valores de Chi-Cuadrado para cada intervalo
    def fillChiSquaredValuesArray(self):
        for i in range(len(self.frequency_obtained)):
            value = round(((self.frequency_obtained[i] - self.expected_frequency[i]) ** 2) / self.expected_frequency[i], 2)
            self.chi_squared_values.append(value)

    # Retorna la suma de los valores de Chi-Cuadrado
    def cumulativeChiSquaredValues(self):
        return sum(self.chi_squared_values)

    # Calcula el valor crítico de Chi-Cuadrado para la prueba
    def chi_squared_test_value(self):
        degrees_of_freedom = self.intervals_amount - 1
        chiSquared = chi2(degrees_of_freedom)
        return chiSquared.ppf(1.0 - self.alpha)

    # Realiza la prueba de Chi-Cuadrado
    def checkTest(self):
        self.fillNiValues()
        self.sortNiArray()
        self.fillIntervalsValuesArray()
        self.fillFrequenciesArrays()
        self.fillChiSquaredValuesArray()
        self.chiReverse = self.chi_squared_test_value()
        self.sumChi2 = self.cumulativeChiSquaredValues()
        self.passed = self.sumChi2 <= self.chi_squared_test_value()

if __name__ == "__main__":
    # Solicita al usuario que ingrese los números Ri separados por comas
    user_input = input("Ingresa los números Ri separados por comas: ")
    try:
        ri_values = [float(x.strip()) for x in user_input.split(",")]
    except ValueError:
        print("Error: Asegúrate de ingresar únicamente números separados por comas.")
        exit(1)

    # Solicita opcionalmente la cantidad de intervalos, y los parámetros a y b
    intervals_input = input("Ingresa la cantidad de intervalos (por defecto 8): ")
    try:
        intervals_amount = int(intervals_input) if intervals_input else 8
    except ValueError:
        print("Error: La cantidad de intervalos debe ser un número entero. Se usará 8.")
        intervals_amount = 8

    a_input = input("Ingresa el parámetro a (por defecto 8): ")
    try:
        a = float(a_input) if a_input else 8
    except ValueError:
        print("Error: El parámetro a debe ser numérico. Se usará 8.")
        a = 8

    b_input = input("Ingresa el parámetro b (por defecto 10): ")
    try:
        b = float(b_input) if b_input else 10
    except ValueError:
        print("Error: El parámetro b debe ser numérico. Se usará 10.")
        b = 10

    # Crea la instancia de ChiTest con los valores ingresados y ejecuta la prueba
    test = ChiTest(ri_values=ri_values, intervals_amount=intervals_amount, a=a, b=b)
    test.checkTest()

    # Muestra los resultados en consola
    print("\nValores ni calculados:", test.ni_values)
    print("Intervalos:", test.intervals_values)
    print("Frecuencias Observadas:", test.frequency_obtained)
    print("Frecuencias Esperadas:", test.expected_frequency)
    print("Valores de Chi-Cuadrado en cada intervalo:", test.chi_squared_values)
    print("Sumatoria de Valores Chi2:", test.cumulativeChiSquaredValues())
    print("Valor Crítico de Chi2:", test.chi_squared_test_value())
    print("¿Prueba superada?:", test.passed)