import unittest
from bench import evaluate, suite
from roboidf import Parameters
class BenchTests(unittest.TestCase):
    def test_suite(self):
        result=suite()
        self.assertTrue(result['passed'])
        self.assertEqual(len(result['cases']),3)
        self.assertTrue(result['zero_excitation_rejected'])
    def test_bad_model_fails(self):
        self.assertFalse(evaluate(Parameters(1,.2),Parameters(8,3),91)['passed'])
    def test_exact_model_passes(self):
        p=Parameters(2,.4)
        self.assertTrue(evaluate(p,p,91)['passed'])
    def test_deterministic(self):
        self.assertEqual(suite(),suite())

    def test_zero_damping(self):
        p=Parameters(2,0)
        self.assertTrue(evaluate(p,p,91)['passed'])
    def test_divergent_model_fails(self):
        self.assertFalse(evaluate(Parameters(1e-300,1),Parameters(2,.4),91)['passed'])
