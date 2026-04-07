import unittest
import time
import os
import tempfile
from verifiers.code_verifier import CodeVerifier


class TestCodeVerifierRobustness(unittest.TestCase):
    def test_infinite_loop(self):
        # Create a dummy test file
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            f.write("if __name__ == '__main__': pass")
            test_file_path = f.name

        try:
            verifier = CodeVerifier(test_file_path)

            # Infinite loop code
            code = "while True: pass"

            start_time = time.time()
            result = verifier.verify(code)
            end_time = time.time()

            # Should return False
            self.assertFalse(result)

            # Check duration - should be at least 5 seconds (timeout)
            duration = end_time - start_time
            self.assertGreaterEqual(duration, 5.0)
            self.assertLess(duration, 10.0)  # margin

        finally:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)

    def test_syntax_error(self):
        # Create a dummy test file
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            f.write("pass")
            test_file_path = f.name

        try:
            verifier = CodeVerifier(test_file_path)
            code = "def foo(:"  # Syntax error
            result = verifier.verify(code)
            self.assertFalse(result)
        finally:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)


if __name__ == "__main__":
    unittest.main()
