import unittest
import logging
import os # For manipulating file paths if needed for test data
import json # For creating temporary test data files if needed
from app.clients.health_inspection_client import MockHealthInspectionClient, SimulatedHealthInspectionClient

# Get the directory where this test script is located
# This helps in reliably finding the 'data' directory relative to 'clients' directory
# when tests are run from the project root.
TEST_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Path to the 'app' directory from '/app/ai_underwriter/tests/clients'
# (assuming tests are run from /app, or sys.path is set up by run_tests.py)
# For SimulatedHealthInspectionClient, the default path is relative to where it's defined or CWD.
# We'll let the client use its default path logic, which should find
# `ai_underwriter/app/clients/data/simulated_health_data.json`
# when tests are run via `python run_tests.py` from the `/app` directory.
# The client's internal path adjustment logic should handle this.

class TestMockHealthInspectionClient(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.client = MockHealthInspectionClient(api_key="test_key_mock")

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_get_data_risky_diner(self):
        data = self.client.get_inspection_data(address="123 Some St", business_name="The Risky Diner")
        self.assertIsNotNone(data)
        self.assertEqual(data["latest_score"], 65)
        self.assertEqual(data["critical_violations_last_year"], 5)
        self.assertEqual(data["source"], "mock_health_department_api_v1") # Updated source in client

    def test_get_data_super_clean_eats(self):
        data = self.client.get_inspection_data(address="456 Clean Ave", business_name="Super Clean Eats")
        self.assertIsNotNone(data)
        self.assertEqual(data["latest_score"], 98)
        self.assertEqual(data["critical_violations_last_year"], 0)
        self.assertEqual(data["source"], "mock_health_department_api_v1")

    def test_get_data_generic_profile(self):
        data = self.client.get_inspection_data(address="789 Generic Rd", business_name="Any Other Cafe")
        self.assertIsNotNone(data)
        self.assertEqual(data["latest_score"], 85)
        self.assertEqual(data["critical_violations_last_year"], 1)
        self.assertEqual(data["source"], "mock_health_department_api_v1")
        self.assertEqual(data["summary_url"], "http://example.com/inspections/generic")

    def test_case_insensitivity_business_name(self):
        data_lower = self.client.get_inspection_data(address="123 Some St", business_name="the risky diner")
        self.assertEqual(data_lower["latest_score"], 65)

        data_upper = self.client.get_inspection_data(address="456 Clean Ave", business_name="SUPER CLEAN EATS")
        self.assertEqual(data_upper["latest_score"], 98)


class TestSimulatedHealthInspectionClient(unittest.TestCase):
    # Using a known bad path to ensure the default good path is tested if this one fails as expected.
    _bad_data_file_path = "non_existent_simulated_health_data.json"
    _test_data_dir = os.path.join(TEST_SCRIPT_DIR, "temp_test_data") # For specific test files
    _valid_temp_data_file = os.path.join(_test_data_dir, "temp_sim_data.json")


    @classmethod
    def setUpClass(cls):
        # Create a temporary valid data file for specific tests if needed
        os.makedirs(cls._test_data_dir, exist_ok=True)
        sample_data = [{
            "establishment_id": "TEMP001", "business_name": "Temporary Test Cafe", "address": "1 Temp St",
            "search_keywords": ["1 temp st"],
            "last_inspection": {"score": 90, "inspection_date": "2023-01-01", "violations": [], "grade": "A", "status": "Pass"},
            "historical_summary": {"critical_violations_last_12_months": 0}
        }]
        with open(cls._valid_temp_data_file, 'w') as f:
            json.dump(sample_data, f)

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary test data file and directory
        if os.path.exists(cls._valid_temp_data_file):
            os.remove(cls._valid_temp_data_file)
        if os.path.exists(cls._test_data_dir):
            os.rmdir(cls._test_data_dir)


    def setUp(self):
        logging.disable(logging.CRITICAL)
        # This client will use the default data_file_path specified in its __init__
        self.client_default_data = SimulatedHealthInspectionClient(base_url="test_base_url", api_key="test_api_key")

        # This client instance is for testing specific data loading scenarios
        self.client_test_data = SimulatedHealthInspectionClient(
            base_url="test_base_url", api_key="test_api_key_temp",
            data_file_path=self._valid_temp_data_file
        )
        self.client_bad_file = SimulatedHealthInspectionClient(
            base_url="test_base_url_bad", api_key="test_api_key_bad",
            data_file_path=self._bad_data_file_path
        )

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_data_loading_success_default_file(self):
        # Tests if the default file 'ai_underwriter/app/clients/data/simulated_health_data.json' loads
        self.assertTrue(len(self.client_default_data.simulated_data) > 0, "Default simulated data should load and not be empty.")
        self.assertEqual(len(self.client_default_data.simulated_data), 3) # Based on the provided JSON

    def test_data_loading_success_specific_test_file(self):
        self.assertTrue(len(self.client_test_data.simulated_data) > 0, "Test specific simulated data should load.")
        self.assertEqual(self.client_test_data.simulated_data[0]["business_name"], "Temporary Test Cafe")


    def test_data_loading_file_not_found(self):
        self.assertEqual(self.client_bad_file.simulated_data, [], "Simulated data should be empty if file not found.")
        # Test the get_inspection_data response when data load failed
        result = self.client_bad_file.get_inspection_data("Any Name", "Any Address")
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("error"), "Simulated data not loaded")

    def test_find_establishment_by_name(self):
        # Using the client with default data
        found_risky = self.client_default_data._find_establishment_data(business_name="The Risky Diner", address="")
        self.assertIsNotNone(found_risky)
        self.assertEqual(found_risky["establishment_id"], "EST_RN001")

        found_clean = self.client_default_data._find_establishment_data(business_name="Super Clean Eats", address="")
        self.assertIsNotNone(found_clean)
        self.assertEqual(found_clean["establishment_id"], "EST_SC002")

    def test_find_establishment_by_address_keyword(self):
        # Using the client with default data
        found_by_addr1 = self.client_default_data._find_establishment_data(business_name="Some Other Name", address="101 Danger Path, Badtown")
        self.assertIsNotNone(found_by_addr1)
        self.assertEqual(found_by_addr1["establishment_id"], "EST_RN001")

        found_by_addr2 = self.client_default_data._find_establishment_data(business_name="Does Not Match", address="Contains 202 Sparkle Ave")
        self.assertIsNotNone(found_by_addr2)
        self.assertEqual(found_by_addr2["establishment_id"], "EST_SC002")

    def test_find_establishment_not_found(self):
        # Using the client with default data
        not_found = self.client_default_data._find_establishment_data(business_name="Unknown Cafe", address="000 Nowhere Dr")
        self.assertIsNone(not_found)

    def test_get_inspection_data_success_risky_diner(self):
        # Using the client with default data
        summary = self.client_default_data.get_inspection_data(business_name="The Risky Diner", address="101 Danger Path")
        self.assertIsNotNone(summary)
        self.assertEqual(summary["latest_score"], 65)
        # critical_violations_last_year should come from historical_summary if present in data
        self.assertEqual(summary["critical_violations_last_year"], 5)
        self.assertEqual(summary["grade"], "C")
        self.assertEqual(summary["source"], "simulated_health_api_v2")

    def test_get_inspection_data_success_super_clean(self):
        summary = self.client_default_data.get_inspection_data(business_name="Super Clean Eats", address="202 Sparkle Ave")
        self.assertIsNotNone(summary)
        self.assertEqual(summary["latest_score"], 98)
        self.assertEqual(summary["critical_violations_last_year"], 0)
        self.assertEqual(summary["grade"], "A")
        self.assertEqual(summary["source"], "simulated_health_api_v2")

    def test_get_inspection_data_average_joes_critical_violations_from_last_inspection(self):
        # Test "Average Joe's Diner" which has 1 critical in last_inspection, but also historical_summary
        # The client logic prefers historical_summary.critical_violations_last_12_months
        summary = self.client_default_data.get_inspection_data(business_name="Average Joe's Diner", address="303 Normal St")
        self.assertIsNotNone(summary)
        self.assertEqual(summary["latest_score"], 85)
        self.assertEqual(summary["critical_violations_last_year"], 1) # From historical_summary
        self.assertEqual(summary["source"], "simulated_health_api_v2")


    def test_get_inspection_data_establishment_not_found_response(self):
        summary = self.client_default_data.get_inspection_data(business_name="Unknown Cafe", address="000 Nowhere Dr")
        self.assertIsNotNone(summary)
        self.assertEqual(summary.get("error"), "Establishment not found")
        self.assertIsNone(summary.get("latest_score"))
        self.assertEqual(summary.get("source"), "simulated_health_api_not_found")

    def test_get_inspection_data_invalid_api_key(self):
        client_invalid_key = SimulatedHealthInspectionClient(base_url="test_url", api_key="INVALID_KEY_TEST")
        summary = client_invalid_key.get_inspection_data("The Risky Diner", "101 Danger Path")
        self.assertIsNotNone(summary)
        self.assertEqual(summary.get("error"), "Invalid API Key")
        self.assertEqual(summary.get("source"), "simulated_health_api_error")

    def test_get_inspection_data_simulated_data_load_failure(self):
        # client_bad_file is already initialized with a non-existent file path
        summary = self.client_bad_file.get_inspection_data("Any Name", "Any Address")
        self.assertIsNotNone(summary)
        self.assertEqual(summary.get("error"), "Simulated data not loaded")
        self.assertEqual(summary.get("source"), "simulated_health_api_internal_error")

if __name__ == '__main__':
    unittest.main()
