import unittest
from app.core.decision_engine import make_decision

class TestDecisionEngine(unittest.TestCase):

    # APPROVE_THRESHOLD = 3.5
    # REFER_THRESHOLD = 6.5

    def test_decision_approved(self):
        self.assertEqual(make_decision(2.0), "Approved")
        self.assertEqual(make_decision(3.5), "Approved") # Boundary

    def test_decision_refer(self):
        self.assertEqual(make_decision(3.6), "Refer to manual underwriter")
        self.assertEqual(make_decision(5.0), "Refer to manual underwriter")
        self.assertEqual(make_decision(6.5), "Refer to manual underwriter") # Boundary

    def test_decision_declined(self):
        self.assertEqual(make_decision(6.51), "Declined")
        self.assertEqual(make_decision(8.0), "Declined")
        self.assertEqual(make_decision(10.0), "Declined")


    def test_decision_invalid_score_type(self):
        self.assertEqual(make_decision("not_a_float"), "Error: Invalid risk score type")
        self.assertEqual(make_decision([2.5]), "Error: Invalid risk score type")

    def test_decision_none_score(self):
        self.assertEqual(make_decision(None), "Error: Risk score not provided")

    def test_decision_score_out_of_bounds(self):
        # Although risk_engine caps scores at 1.0-10.0, test decision_engine's safeguard
        self.assertEqual(make_decision(0.5), "Error: Risk score out of expected range (1.0-10.0)")
        self.assertEqual(make_decision(11.0), "Error: Risk score out of expected range (1.0-10.0)")
        # Test edge cases for the check itself
        self.assertNotEqual(make_decision(1.0), "Error: Risk score out of expected range (1.0-10.0)")
        self.assertNotEqual(make_decision(10.0), "Error: Risk score out of expected range (1.0-10.0)")


if __name__ == '__main__':
    unittest.main()
