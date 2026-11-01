import json
import unittest
from comparison import run_comparison

class ComparisonTests(unittest.TestCase):
    def test_duplicate_test_seed_refused(self):
        for seed in (101, 202):
            with self.assertRaises(ValueError):
                run_comparison(test_seed=seed)

    def test_fixed_cases_and_failure_evidence(self):
        report=run_comparison()
        cases={x['scenario']:x for x in report['cases']}
        self.assertEqual(set(cases), {'clean','noise','mismatch','zero-excitation','continuous'})
        self.assertTrue(cases['clean']['scipy']['passed'])
        self.assertTrue(cases['clean']['baseline']['passed'])
        self.assertFalse(cases['mismatch']['scipy']['passed'])
        self.assertFalse(cases['zero-excitation']['scipy']['passed'])
        self.assertNotEqual(cases['clean']['data_hashes']['train'], cases['clean']['data_hashes']['test'])
        self.assertIsNotNone(cases['clean']['scipy']['test_rmse_m_s'])
        json.dumps(report,allow_nan=False)

    def test_test_seed_does_not_change_fitted_model_or_selection(self):
        first=run_comparison(test_seed=501)
        second=run_comparison(test_seed=777)
        self.assertEqual(first['selection'],second['selection'])
        for left,right in zip(first['cases'], second['cases']):
            self.assertEqual(left['scipy']['fit'],right['scipy']['fit'])
            self.assertEqual(left['baseline']['model'],right['baseline']['model'])
            self.assertNotEqual(left['data_hashes']['test'],right['data_hashes']['test'])

if __name__=='__main__': unittest.main()
