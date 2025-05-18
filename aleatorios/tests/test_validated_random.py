import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', '..')))
# Insertar carpeta 'src' en sys.path para importar modelos desde src/modelos

import unittest
from modelos.validated_random import ValidatedRandom
from modelos.exceptions import ValidationError

class TestValidatedRandom(unittest.TestCase):
    def test_basic_random(self):
        rng = ValidatedRandom(seed=42, batch_size=100, max_attempts=1)
        val = rng.random()
        self.assertIsInstance(val, float)
        self.assertGreaterEqual(val, 0.0)
        self.assertLess(val, 1.0)

    def test_randint_uniform_choice(self):
        rng = ValidatedRandom(seed=42, batch_size=100, max_attempts=1)
        i = rng.randint(1, 10)
        self.assertGreaterEqual(i, 1)
        self.assertLessEqual(i, 10)
        u = rng.uniform(5.0, 6.0)
        self.assertGreaterEqual(u, 5.0)
        self.assertLessEqual(u, 6.0)
        seq = [1, 2, 3]
        c = rng.choice(seq)
        self.assertIn(c, seq)

    def test_seed_resets_batch(self):
        rng = ValidatedRandom(seed=123, batch_size=50, max_attempts=1)
        vals1 = [rng.random() for _ in range(10)]
        rng.seed(123)
        vals2 = [rng.random() for _ in range(10)]
        self.assertEqual(vals1, vals2)

    def test_gauss(self):
        rng = ValidatedRandom(seed=0, batch_size=100, max_attempts=1)
        g = rng.gauss(0, 1)
        self.assertIsInstance(g, float)

    def test_validation_error(self):
        rng = ValidatedRandom(seed=0, batch_size=10, max_attempts=0)
        with self.assertRaises(ValidationError):
            rng.random()

if __name__ == '__main__':
    unittest.main()
