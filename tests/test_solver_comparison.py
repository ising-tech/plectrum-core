import unittest

from test import DEMO_DATA_PATH, data as demo_data, solve_with_all_methods


class SolverComparisonTestCase(unittest.TestCase):
    def test_compare_three_solving_methods_with_real_services(self):
        self.assertEqual(DEMO_DATA_PATH, "/Users/jjhao/PycharmProjects/interface_api/dev/Q_norm.csv")
        self.assertEqual(demo_data.shape, (48, 48))

        results = solve_with_all_methods(task_name="probe-cloud-real")

        traditional_result = results["LocalSolver"]
        local_oepo_result = results["LocalOepoSolver"]
        cloud_result = results["CloudSolver"]

        for result in (traditional_result, local_oepo_result, cloud_result):
            self.assertTrue(result.ok)
            self.assertEqual(result.name, "probe-cloud-real")
            self.assertEqual(len(result.spin_config), 48)
            self.assertIsNotNone(result.energy)
            self.assertIsNotNone(result.oepo_time)
            self.assertIsNotNone(result.e2e_time)

        self.assertLess(abs(traditional_result.energy - local_oepo_result.energy), 2.0)
        self.assertLess(abs(traditional_result.energy - cloud_result.energy), 2.0)
        self.assertLess(abs(local_oepo_result.energy - cloud_result.energy), 2.0)


if __name__ == "__main__":
    unittest.main()






