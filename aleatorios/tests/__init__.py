import sys, os
# Insertar la ruta al directorio 'src' para que Python encuentre el paquete 'modelos'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest

# Aquí se pueden agregar las importaciones de los módulos de prueba

if __name__ == '__main__':
    unittest.main()