import unittest

from password_tool import brute_force, password_spray


class PasswordToolTests(unittest.TestCase):
    def test_brute_force_finds_first_matching_candidate(self):
        candidates = ["alpha", "beta", "gamma"]

        self.assertEqual(brute_force(candidates, "beta"), "beta")

    def test_brute_force_returns_none_when_no_candidate_matches(self):
        self.assertIsNone(brute_force(["alpha", "beta"], "gamma"))

    def test_password_spray_returns_every_matching_username(self):
        accounts = {
            "alice": "learning",
            "bob": "different",
            "carol": "learning",
        }

        self.assertEqual(password_spray(accounts, "learning"), ["alice", "carol"])

    def test_password_spray_preserves_no_match_behavior(self):
        self.assertEqual(password_spray({"alice": "different"}, "learning"), [])


if __name__ == "__main__":
    unittest.main()
