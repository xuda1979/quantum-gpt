"""Unit test for the math correctness reward."""

import unittest
from rewards.math_correctness_reward import MathCorrectnessReward

class TestMathCorrectnessReward(unittest.TestCase):
    """
    Test suite for the math correctness reward.
    """
    def test_math_correctness_reward(self):
        """
        Tests the math correctness reward.
        """
        reward_function = MathCorrectnessReward()

        correct_expression = "x**2 - 2*x + 1"
        incorrect_expression = "x**2 - 2*x +"

        rewards = reward_function.get_reward([correct_expression, incorrect_expression])

        self.assertEqual(rewards, [1.0, 0.0])

if __name__ == "__main__":
    unittest.main()
