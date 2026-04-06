"""Unit test for the code correctness reward."""

import unittest
from rewards.code_correctness_reward import CodeCorrectnessReward

class TestCodeCorrectnessReward(unittest.TestCase):
    """
    Test suite for the code correctness reward.
    """
    def test_code_correctness_reward(self):
        """
        Tests the code correctness reward.
        """
        reward_function = CodeCorrectnessReward("verifiers/tests/add_test_template.py")

        correct_code = "def add(a, b): return a + b"
        incorrect_code = "def add(a, b): return a - b"

        rewards = reward_function.get_reward([correct_code, incorrect_code])

        self.assertEqual(rewards, [1.0, 0.0])

if __name__ == "__main__":
    unittest.main()
