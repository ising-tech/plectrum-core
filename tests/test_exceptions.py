"""Tests for plectrum.exceptions."""
import unittest
from plectrum.exceptions import (
    PlectrumError, AuthenticationError, ClientError, TimeoutError,
    ConnectionError, TaskError, MatrixError, ValidationError,
)


class TestExceptionHierarchy(unittest.TestCase):

    def test_all_inherit_from_plectrum_error(self):
        for cls in (AuthenticationError, ClientError, TimeoutError,
                    ConnectionError, TaskError, MatrixError, ValidationError):
            self.assertTrue(issubclass(cls, PlectrumError), f"{cls} not subclass")

    def test_timeout_and_connection_are_client_errors(self):
        self.assertTrue(issubclass(TimeoutError, ClientError))
        self.assertTrue(issubclass(ConnectionError, ClientError))

    def test_plectrum_error_is_exception(self):
        self.assertTrue(issubclass(PlectrumError, Exception))

    def test_custom_message(self):
        err = PlectrumError("custom msg")
        self.assertEqual(err.message, "custom msg")
        self.assertEqual(str(err), "custom msg")

    def test_default_message_from_docstring(self):
        err = AuthenticationError()
        self.assertEqual(err.message, "Authentication failed.")

    def test_cause_chaining(self):
        original = ValueError("bad value")
        try:
            raise ClientError("wrapper") from original
        except ClientError as e:
            self.assertIs(e.__cause__, original)

    def test_each_exception_can_be_raised_and_caught(self):
        for cls in (PlectrumError, AuthenticationError, ClientError, TimeoutError,
                    ConnectionError, TaskError, MatrixError, ValidationError):
            with self.assertRaises(cls):
                raise cls("test")


if __name__ == "__main__":
    unittest.main()
