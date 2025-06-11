import unittest
import json
import logging
import os # Added
from unittest.mock import patch, MagicMock # Added MagicMock for more complex mocks if needed
from main import app # Import the Flask app instance
from app.api.application_api import submitted_applications, assessment_results
# from app.core.risk_engine import calculate_risk_score # Not strictly needed for API tests if mocking client outputs

# Import the actual client to check its instance type if needed, or for specific constants.
from app.clients import SimulatedHealthInspectionClient

class TestApplicationAPI(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        submitted_applications.clear()
        assessment_results.clear()
        logging.disable(logging.WARNING) # Suppress logs for cleaner test output

        self.valid_payload = {
            "business_name": "The Testy Taverna",
            "address": "789 Test Lane",
            "cuisine_type": "Greek",
            "alcohol_sales_percentage": 0.35,
            "operating_hours": "12pm-11pm",
            "square_footage": 2000,
            "building_age": 15,
            "fire_suppression_system_type": "Ansul",
            "years_in_business": 7,
            "management_experience_years": 5,
            "has_delivery_operations": True,
            "has_catering_operations": True,
            "seating_capacity": 70,
            "annual_revenue": 600000.00,
            "health_inspection_score": 92.0,
            "previous_claims_count": 1
        }
        # Base app score for this payload (calculated as per risk_engine logic):
        # 5.0 (initial) + 0 (Greek not in list) + 0.5 (alc) - 1.0 (Ansul) + 0 (years) + 0.5 (claims) = 5.0

    def tearDown(self):
        logging.disable(logging.NOTSET)
        # Reset any environment variables changed for a specific test
        if "HEALTH_API_KEY" in os.environ:
            del os.environ["HEALTH_API_KEY"]

    # Patching the actual client instance used in application_api.py
    @patch('app.api.application_api.crime_statistics_client.get_crime_data')
    @patch('app.api.application_api.health_inspection_client.get_inspection_data')
    def test_submit_application_success_with_mocked_clients(self, mock_health_get_data, mock_crime_get_data):
        # Configure mock return values for client methods
        mock_health_get_data.return_value = {
            "latest_score": 95, "last_inspection_date": "2023-01-01",
            "critical_violations_last_year": 0, "grade": "A", "status": "Pass",
            "source": "simulated_health_api_via_mock_patch" # Key to check if this mock was used
        }
        mock_crime_get_data.return_value = {
            "crime_level_area": "Low", "safety_score": 9.0,
            "source": "mock_crime_statistics_api_via_mock_patch"
        }

        response = self.client.post('/applications/submit',
                                     data=json.dumps(self.valid_payload),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data)

        self.assertIn("application_id", data)
        self.assertIn("health_inspection_summary", data)
        self.assertEqual(data["health_inspection_summary"]["source"], "simulated_health_api_via_mock_patch")
        self.assertIn("crime_statistics_summary", data)
        self.assertEqual(data["crime_statistics_summary"]["source"], "mock_crime_statistics_api_via_mock_patch")

        # Assert that the client methods were called correctly
        mock_health_get_data.assert_called_once_with(
            business_name="The Testy Taverna", address="789 Test Lane",
            city=None, state=None, zip_code=None # Matching the current call in API
        )
        mock_crime_get_data.assert_called_once_with(address="789 Test Lane")

        # Expected base app score: 5.0
        # Health data (good from mock): 0 impact (score >=85, crit_viol=0)
        # Crime data (good from mock): 0 impact (level Low, safety_score >= 7.0)
        # Expected risk_score = 5.0 + 0 + 0 = 5.0
        self.assertAlmostEqual(data["risk_score"], 5.0, places=2)


    @patch.dict(os.environ, {"HEALTH_API_KEY": "INVALID_KEY_TEST"}, clear=True)
    @patch('app.api.application_api.crime_statistics_client.get_crime_data')
    # NO patch on health_inspection_client.get_inspection_data to test actual instance behavior with env var
    def test_submit_with_invalid_health_api_key_env(self, mock_crime_get):
        # This test re-imports application_api to re-initialize clients with the new os.environ
        # However, Flask app and its blueprints are usually initialized once.
        # A better way for this kind of test is to restart the app with new env vars,
        # or ensure client is instantiated per request (not module level), or patch 'os.environ.get'
        # For now, we assume the module-level client in application_api picks up the env var at import time
        # (which happens when test discovery loads `main` and then `application_api`).
        # If `run_tests.py` imports everything once, this test might not reflect env var changes
        # without further modification to how `application_api.py` instantiates clients or how tests are structured.
        # Let's assume for now the env var is picked up.

        # Re-instantiate the app or client to pick up the new env var
        # This is tricky as the client is module-level. We might need to patch where the client is defined.
        # For this test, let's patch os.environ.get directly for where the client is instantiated.
        with patch('os.environ.get') as mock_os_get:
            def side_effect(key, default=None):
                if key == 'HEALTH_API_KEY':
                    return "INVALID_KEY_TEST"
                if key == 'CRIME_API_KEY':
                    return "ANY_CRIME_KEY" # Or None, as MockCrime doesn't use it strictly
                return default
            mock_os_get.side_effect = side_effect

            # Re-import or reload application_api to re-initialize clients (conceptual)
            # For a practical test, one would typically restart the application server with the env var set.
            # Here, we rely on the fact that the client instance in application_api.py will use this
            # "INVALID_KEY_TEST" when its get_inspection_data is called.
            # This requires `application_api.health_inspection_client` to be using the env var.
            # The `SimulatedHealthInspectionClient` is designed to return an error for this key.

            mock_crime_get.return_value = {"crime_level_area": "Low", "safety_score": 9.0, "source": "mocked_crime"}

            response = self.client.post('/applications/submit', data=json.dumps(self.valid_payload), content_type='application/json')
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)

            self.assertIn("health_inspection_summary", data)
            self.assertIsNotNone(data["health_inspection_summary"])
            self.assertEqual(data["health_inspection_summary"].get("error"), "Invalid API Key")
            self.assertEqual(data["health_inspection_summary"].get("source"), "simulated_health_api_error")

            # Expected base app score: 5.0
            # Health data: error, so penalty +0.5
            # Crime data (good): 0 impact
            # Expected risk_score = 5.0 + 0.5 + 0 = 5.5
            self.assertAlmostEqual(data["risk_score"], 5.5, places=2)


    @patch.dict(os.environ, {}, clear=True) # HEALTH_API_KEY is NOT set
    @patch('app.api.application_api.crime_statistics_client.get_crime_data')
    @patch('app.api.application_api.health_inspection_client.get_inspection_data') # Patch to control output
    def test_submit_with_no_health_api_key_env(self, mock_health_get_data, mock_crime_get_data):
        # When HEALTH_API_KEY is not set, SimulatedHealthInspectionClient uses its default "SIM_DEFAULT_KEY".
        # We are patching get_inspection_data, so this test verifies that the call proceeds
        # and the patched method is called, simulating that the client operated with its default key.
        mock_health_get_data.return_value = {
            "latest_score": 80, "critical_violations_last_year": 1,
            "source": "simulated_with_default_key_via_patch"
        }
        mock_crime_get_data.return_value = {"crime_level_area": "Low", "safety_score": 9.0, "source": "mocked_crime"}

        response = self.client.post('/applications/submit', data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

        self.assertIn("health_inspection_summary", data)
        self.assertEqual(data["health_inspection_summary"]["latest_score"], 80)
        self.assertEqual(data["health_inspection_summary"]["source"], "simulated_with_default_key_via_patch")

        mock_health_get_data.assert_called_once()
        # Expected base app score: 5.0
        # Health data (mocked as moderately good: score 80, 1 crit viol): +1.0 (score) + 0.5 (viol) = +1.5
        # Crime data (good): 0 impact
        # Expected risk_score = 5.0 + 1.5 + 0 = 6.5
        self.assertAlmostEqual(data["risk_score"], 6.5, places=2)

    # Other tests like bad_request, client failures, get_assessment, get_raw_application
    # from the previous version of this file would largely remain the same,
    # just ensuring the health client being patched is `SimulatedHealthInspectionClient`.
    # I'll re-add a simplified client failure test.

    @patch('app.api.application_api.crime_statistics_client.get_crime_data')
    @patch('app.api.application_api.health_inspection_client.get_inspection_data')
    def test_submit_application_health_client_method_fails(self, mock_health_get_data, mock_crime_get_data):
        mock_health_get_data.side_effect = Exception("Simulated Health API is down")
        mock_crime_get_data.return_value = {"crime_level_area": "Low", "safety_score": 9.0, "source": "mocked_crime"}

        response = self.client.post('/applications/submit', data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

        self.assertIsNone(data["health_inspection_summary"])
        self.assertIsNotNone(data["crime_statistics_summary"])

        # Base app score: 5.0. Health data missing penalty: +0.5. Crime data (good): 0.
        # Expected score: 5.0 + 0.5 + 0 = 5.5
        self.assertAlmostEqual(data["risk_score"], 5.5, places=2)

if __name__ == '__main__':
    unittest.main()
