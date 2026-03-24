"""Tests for plectrum.const."""
import unittest
from plectrum import const


class TestConstants(unittest.TestCase):

    def test_problem_types(self):
        self.assertEqual(const.QUBO_PROBLEM, 1)
        self.assertEqual(const.ISING_PROBLEM, 2)

    def test_gear_modes(self):
        self.assertEqual(const.GEAR_FAST, 0)
        self.assertEqual(const.GEAR_BALANCED, 1)
        self.assertEqual(const.GEAR_PRECISE, 2)

    def test_local_type_strings(self):
        self.assertEqual(const.LOCAL_TYPE_QUBO, "binary")
        self.assertEqual(const.LOCAL_TYPE_ISING, "spin")

    def test_default_hosts(self):
        self.assertEqual(const.DEFAULT_CLOUD_HOST, "https://api.isingq.com")
        self.assertEqual(const.DEFAULT_LOCAL_HOST, "http://192.168.137.100:5001")

    def test_computer_types(self):
        self.assertEqual(const.OEPO_ISING_1601, 1)


if __name__ == "__main__":
    unittest.main()
