"""Tests for plectrum.task.template."""
import unittest
from plectrum.task.template import TemplateTask


class TestTemplateTask(unittest.TestCase):

    def test_task_type(self):
        t = TemplateTask(name="t1", template_id=10, gear=2, payload="data")
        self.assertEqual(t.task_type, "template")

    def test_to_dict(self):
        t = TemplateTask(name="t1", template_id=10, gear=2, payload="data")
        d = t.to_dict()
        self.assertEqual(d["task_type"], "template")
        self.assertEqual(d["payload"]["templateId"], 10)
        self.assertEqual(d["payload"]["computerTypeId"], 2)
        self.assertIsNone(d["csv_string"])

    def test_properties(self):
        t = TemplateTask(name="t1", template_id=10, gear=2, payload="data")
        self.assertEqual(t.template_id, 10)
        self.assertEqual(t.gear, 2)
        self.assertEqual(t.payload, "data")

    def test_from_dict(self):
        d = {"payload": {"name": "t2", "templateId": 5, "computerTypeId": 1, "payload": "p"}}
        t = TemplateTask.from_dict(d)
        self.assertEqual(t.name, "t2")
        self.assertEqual(t.template_id, 5)


if __name__ == "__main__":
    unittest.main()
