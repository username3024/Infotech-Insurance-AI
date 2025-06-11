import unittest
import logging
from app.clients.health_inspection_client import MockHealthInspectionClient

class TestMockHealthInspectionClient(unittest.TestCase):

    def setUp(self):
        # Suppress logging during tests unless specifically testing log output
        logging.disable(logging.CRITICAL)
        self.client = MockHealthInspectionClient(api_key="test_key")

    def tearDown(self):
        # Re-enable logging
        logging.disable(logging.NOTSET)

    def test_get_data_risky_diner(self):
        data = self.client.get_inspection_data(address="123 Some St", business_name="The Risky Diner")
        self.assertIsNotNone(data)
        self.assertEqual(data["latest_score"], 65)
        self.assertEqual(data["critical_violations_last_year"], 5)
        self.assertEqual(data["source"], "mock_health_department_api")

    def test_get_data_super_clean_eats(self):
        data = self.client.get_inspection_data(address="456 Clean Ave", business_name="Super Clean Eats")
        self.assertIsNotNone(data)
        self.assertEqual(data["latest_score"], 98)
        self.assertEqual(data["critical_violations_last_year"], 0)
        self.assertEqual(data["source"], "mock_health_department_api")

    def test_get_data_generic_profile(self):
        data = self.client.get_inspection_data(address="789 Generic Rd", business_name="Any Other Cafe")
        self.assertIsNotNone(data)
        self.assertEqual(data["latest_score"], 85) # Generic score
        self.assertEqual(data["critical_violations_last_year"], 1) # Generic violations
        self.assertEqual(data["source"], "mock_health_department_api")
        self.assertEqual(data["summary_url"], "http://example.com/inspections/generic")

    def test_case_insensitivity_business_name(self):
        data_lower = self.client.get_inspection_data(address="123 Some St", business_name="the risky diner")
        self.assertEqual(data_lower["latest_score"], 65)

        data_upper = self.client.get_inspection_data(address="456 Clean Ave", business_name="SUPER CLEAN EATS")
        self.assertEqual(data_upper["latest_score"], 98)

if __name__ == '__main__':
    unittest.main()
