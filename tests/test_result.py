"""Tests for plectrum.result.Result."""
import unittest
from plectrum.result import Result
from plectrum.exceptions import ClientError


class TestResultInit(unittest.TestCase):

    def test_defaults(self):
        r = Result()
        self.assertIsNone(r.energy)
        self.assertTrue(r.ok)
        self.assertIsNone(r.msg)

    def test_properties(self):
        r = Result(energy=-1.5, spin_config=[1, -1], time=0.5,
                   task_id="t1", task_name="n1", ok=True, msg="ok", timestamp=100)
        self.assertEqual(r.energy, -1.5)
        self.assertEqual(r.spin_config, [1, -1])
        self.assertEqual(r.time, 0.5)
        self.assertEqual(r.task_id, "t1")
        self.assertEqual(r.task_name, "n1")
        self.assertTrue(r.ok)
        self.assertEqual(r.msg, "ok")
        self.assertEqual(r.timestamp, 100)


class TestResultToDict(unittest.TestCase):

    def test_round_trip(self):
        r = Result(energy=-1.0, spin_config=[0, 1])
        d = r.to_dict()
        self.assertEqual(d["energy"], -1.0)
        self.assertEqual(d["spin_config"], [0, 1])


class TestResultFromLocal(unittest.TestCase):

    def test_happy_path(self):
        raw = {
            "result": {
                "energy": -2.5,
                "spin_config": [1, -1, 1],
                "isingCalcMs": 1500,
                "taskName": "job1",
                "ok": True,
                "msg": "done",
                "ts": 12345,
            }
        }
        r = Result.from_local(raw, "tid-1")
        self.assertEqual(r.energy, -2.5)
        self.assertEqual(r.time, 1.5)
        self.assertEqual(r.task_id, "tid-1")

    def test_missing_result_key(self):
        raw = {}
        r = Result.from_local(raw, "tid-2")
        self.assertIsNone(r.energy)

    def test_non_dict_raises(self):
        with self.assertRaises(ClientError):
            Result.from_local("not a dict", "tid-3")

    def test_non_numeric_time_raises(self):
        raw = {"result": {"isingCalcMs": "bad"}}
        with self.assertRaises(ClientError) as ctx:
            Result.from_local(raw, "tid-4")
        self.assertIsNotNone(ctx.exception.__cause__)


class TestResultFromCloud(unittest.TestCase):

    def test_happy_path(self):
        raw = {"energy": -3.0, "spin_config": [0, 1], "oepo_time": "0.5s"}
        r = Result.from_cloud(raw, "ctid-1")
        self.assertEqual(r.energy, -3.0)
        self.assertEqual(r.time, 0.5)
        self.assertTrue(r.ok)

    def test_no_oepo_time(self):
        raw = {"energy": -1.0}
        r = Result.from_cloud(raw, "ctid-2")
        self.assertIsNone(r.time)

    def test_non_dict_raises(self):
        with self.assertRaises(ClientError):
            Result.from_cloud([1, 2], "ctid-3")

    def test_bad_oepo_time_format_raises(self):
        raw = {"oepo_time": "not-a-number"}
        with self.assertRaises(ClientError) as ctx:
            Result.from_cloud(raw, "ctid-4")
        self.assertIsNotNone(ctx.exception.__cause__)


class TestResultEq(unittest.TestCase):

    def test_equal(self):
        r1 = Result(energy=-1.0, ok=True)
        r2 = Result(energy=-1.0, ok=True)
        self.assertEqual(r1, r2)

    def test_not_equal(self):
        r1 = Result(energy=-1.0)
        r2 = Result(energy=-2.0)
        self.assertNotEqual(r1, r2)

    def test_not_equal_to_non_result(self):
        r = Result(energy=-1.0)
        self.assertNotEqual(r, {"energy": -1.0})


class TestResultRepr(unittest.TestCase):

    def test_repr(self):
        r = Result(energy=-1.0, time=0.5)
        self.assertIn("-1.0", repr(r))

    def test_str(self):
        r = Result(energy=-1.0, time=0.5)
        self.assertIn("-1.0", str(r))


if __name__ == "__main__":
    unittest.main()
