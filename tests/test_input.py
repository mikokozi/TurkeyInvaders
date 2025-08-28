import unittest

from turkey_invaders.input import _names_to_codes


class TestInput(unittest.TestCase):
    def test_letter_binds_both_cases(self):
        codes = _names_to_codes(["x"])  # should include 'x' and 'X'
        self.assertIn(ord('x'), codes)
        self.assertIn(ord('X'), codes)

    def test_enter_maps_to_10_and_13(self):
        codes = _names_to_codes(["ENTER"])  # should include 10 and 13
        self.assertIn(10, codes)
        self.assertIn(13, codes)


if __name__ == "__main__":
    unittest.main()

