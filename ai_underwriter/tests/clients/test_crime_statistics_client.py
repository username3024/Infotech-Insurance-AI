import unittest
import logging
from app.clients.crime_statistics_client import MockCrimeStatisticsClient

class TestMockCrimeStatisticsClient(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL) # Suppress logs during tests
        self.client = MockCrimeStatisticsClient(api_key="test_crime_key")

    def tearDown(self):
        logging.disable(logging.NOTSET) # Re-enable logging

    def test_get_data_low_crime_address(self):
        data = self.client.get_crime_data(address="123 Main St, Safeville")
        self.assertIsNotNone(data)
        self.assertEqual(data["crime_level_area"], "Low")
        self.assertEqual(data["theft_incidents_last_year_nearby"], 2)
        self.assertEqual(data["safety_score"], 8.5)
        self.assertEqual(data["source"], "mock_crime_statistics_api")

    def test_get_data_high_crime_address(self):
        data = self.client.get_crime_data(address="Unit A, 999 Danger Ave, Risky City")
        self.assertIsNotNone(data)
        self.assertEqual(data["crime_level_area"], "High")
        self.assertEqual(data["theft_incidents_last_year_nearby"], 25)
        self.assertEqual(data["safety_score"], 3.2)
        self.assertEqual(data["source"], "mock_crime_statistics_api")

    def test_get_data_medium_crime_address_generic(self):
        data = self.client.get_crime_data(address="400 Normal Rd, Anytown")
        self.assertIsNotNone(data)
        self.assertEqual(data["crime_level_area"], "Medium")
        self.assertEqual(data["theft_incidents_last_year_nearby"], 7)
        self.assertEqual(data["safety_score"], 6.5)
        self.assertEqual(data["source"], "mock_crime_statistics_api")

    def test_case_insensitivity_address_keywords(self):
        data_lower = self.client.get_crime_data(address="condo 1, 123 main st, safeville")
        self.assertEqual(data_lower["crime_level_area"], "Low")

        data_upper = self.client.get_crime_data(address="penthouse, 999 DANGER AVE, RISKY CITY")
        self.assertEqual(data_upper["crime_level_area"], "High")

if __name__ == '__main__':
    unittest.main()
