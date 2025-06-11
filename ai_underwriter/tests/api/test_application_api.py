import unittest
import json
import logging
from unittest.mock import patch # Added
from main import app # Import the Flask app instance
# To clear in-memory stores for each test run
from app.api.application_api import submitted_applications, assessment_results
from app.core.risk_engine import calculate_risk_score # For calculating expected score with penalties

class TestApplicationAPI(unittest.TestCase):

    def setUp(self):
        """Set up test client and other test variables."""
        app.testing = True
        self.client = app.test_client()
        # Clear in-memory storage before each test
        submitted_applications.clear()
        assessment_results.clear()
        # Suppress non-critical logs during tests for cleaner output
        logging.disable(logging.WARNING)


        self.valid_payload = {
            "business_name": "The Testy Taverna", # Generic name for external data
            "address": "789 Test Lane", # Generic address for external data
            "cuisine_type": "Greek", # Score impact: +0.5 (assuming Greek is not specifically listed, so 0 from default cuisine list)
            "alcohol_sales_percentage": 0.35, # Score impact: +0.5
            "operating_hours": "12pm-11pm",
            "square_footage": 2000,
            "building_age": 15,
            "fire_suppression_system_type": "Ansul", # Score impact: -1.0
            "years_in_business": 7, # Score impact: 0.0
            "management_experience_years": 5,
            "has_delivery_operations": True,
            "has_catering_operations": True,
            "seating_capacity": 70,
            "annual_revenue": 600000.00,
            "health_inspection_score": 92.0, # Application field, not external mock
            "previous_claims_count": 1 # Score impact: +0.5
        }
        # Base app score for valid_payload: 5.0 (initial) +0 (Greek) +0.5 (alc) -1.0 (Ansul) +0 (years) +0.5 (claims) = 5.0

    def tearDown(self):
        logging.disable(logging.NOTSET) # Re-enable logging

    @patch('app.api.application_api.crime_statistics_client.get_crime_data')
    @patch('app.api.application_api.health_inspection_client.get_inspection_data')
    def test_submit_application_success_with_mocked_clients(self, mock_health_get, mock_crime_get):
        """Test successful application submission with mocked external clients."""
        mock_health_get.return_value = {"latest_score": 95, "critical_violations_last_year": 0, "source": "mocked_health"}
        mock_crime_get.return_value = {"crime_level_area": "Low", "safety_score": 9.0, "source": "mocked_crime"}

        response = self.client.post('/applications/submit',
                                     data=json.dumps(self.valid_payload),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data)

        self.assertIn("application_id", data)
        self.assertIsNotNone(data["application_id"])
        self.assertIn("risk_score", data)
        self.assertIn("decision", data)
        self.assertIn("health_inspection_summary", data)
        self.assertEqual(data["health_inspection_summary"]["source"], "mocked_health")
        self.assertIn("crime_statistics_summary", data)
        self.assertEqual(data["crime_statistics_summary"]["source"], "mocked_crime")

        mock_health_get.assert_called_once_with(address="789 Test Lane", business_name="The Testy Taverna")
        mock_crime_get.assert_called_once_with(address="789 Test Lane")

        # Check that it's stored
        self.assertIn(data["application_id"], submitted_applications)
        self.assertIn(data["application_id"], assessment_results)
        self.assertEqual(assessment_results[data["application_id"]]["health_inspection_summary"]["latest_score"], 95)


    def test_submit_application_bad_request_missing_field(self):
        payload = self.valid_payload.copy()
        del payload["business_name"]
        response = self.client.post('/applications/submit', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_submit_application_bad_request_invalid_data_type(self):
        payload = self.valid_payload.copy()
        payload["alcohol_sales_percentage"] = "not_a_float"
        response = self.client.post('/applications/submit', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue("Invalid application data format" in data["error"])

    @patch('app.api.application_api.crime_statistics_client.get_crime_data')
    @patch('app.api.application_api.health_inspection_client.get_inspection_data')
    def test_submit_application_health_client_fails(self, mock_health_get, mock_crime_get):
        mock_health_get.side_effect = Exception("Health API is down") # Or return None
        # mock_health_get.return_value = None # Alternative way to test failure
        mock_crime_get.return_value = {"crime_level_area": "Low", "safety_score": 9.0, "source": "mocked_crime"}

        response = self.client.post('/applications/submit', data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, 201) # API still succeeds overall
        data = json.loads(response.data)

        self.assertIsNone(data["health_inspection_summary"]) # Should be None as client failed
        self.assertIsNotNone(data["crime_statistics_summary"])

        # Expected base app score: 5.0
        # Health data missing penalty: +0.5
        # Crime data (good): 0 impact
        # Expected risk_score = 5.0 + 0.5 + 0 = 5.5
        self.assertAlmostEqual(data["risk_score"], 5.5, places=2)

    @patch('app.api.application_api.crime_statistics_client.get_crime_data')
    @patch('app.api.application_api.health_inspection_client.get_inspection_data')
    def test_submit_application_crime_client_fails(self, mock_health_get, mock_crime_get):
        mock_health_get.return_value = {"latest_score": 95, "critical_violations_last_year": 0, "source": "mocked_health"}
        mock_crime_get.side_effect = Exception("Crime API is down") # Or return None

        response = self.client.post('/applications/submit', data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

        self.assertIsNotNone(data["health_inspection_summary"])
        self.assertIsNone(data["crime_statistics_summary"])

        # Expected base app score: 5.0
        # Health data (good): 0 impact
        # Crime data missing penalty: +0.25
        # Expected risk_score = 5.0 + 0 + 0.25 = 5.25
        self.assertAlmostEqual(data["risk_score"], 5.25, places=2)

    @patch('app.api.application_api.crime_statistics_client.get_crime_data')
    @patch('app.api.application_api.health_inspection_client.get_inspection_data')
    def test_submit_application_both_clients_fail(self, mock_health_get, mock_crime_get):
        mock_health_get.return_value = None
        mock_crime_get.return_value = None

        response = self.client.post('/applications/submit', data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

        self.assertIsNone(data["health_inspection_summary"])
        self.assertIsNone(data["crime_statistics_summary"])

        # Expected base app score: 5.0
        # Health data missing penalty: +0.5
        # Crime data missing penalty: +0.25
        # Expected risk_score = 5.0 + 0.5 + 0.25 = 5.75
        self.assertAlmostEqual(data["risk_score"], 5.75, places=2)


    @patch('app.api.application_api.crime_statistics_client.get_crime_data')
    @patch('app.api.application_api.health_inspection_client.get_inspection_data')
    def test_get_assessment_success_and_not_found(self, mock_health_get, mock_crime_get):
        mock_health_get.return_value = {"latest_score": 95, "critical_violations_last_year": 0}
        mock_crime_get.return_value = {"crime_level_area": "Low", "safety_score": 9.0}

        submit_response = self.client.post('/applications/submit', data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(submit_response.status_code, 201)
        submit_data = json.loads(submit_response.data)
        app_id = submit_data["application_id"]

        get_response = self.client.get(f'/applications/assessment/{app_id}')
        self.assertEqual(get_response.status_code, 200)
        assessment_data = json.loads(get_response.data)
        self.assertEqual(assessment_data["application_id"], app_id)
        self.assertEqual(assessment_data["risk_score"], submit_data["risk_score"])

        not_found_response = self.client.get('/applications/assessment/nonexistentid')
        self.assertEqual(not_found_response.status_code, 404)

    @patch('app.api.application_api.crime_statistics_client.get_crime_data') # Mock even if not directly used by this endpoint
    @patch('app.api.application_api.health_inspection_client.get_inspection_data') # Mock even if not directly used by this endpoint
    def test_get_raw_application_success_and_not_found(self, mock_health_get, mock_crime_get):
        mock_health_get.return_value = {} # Irrelevant for this test but submit needs it
        mock_crime_get.return_value = {}  # Irrelevant for this test but submit needs it

        submit_response = self.client.post('/applications/submit', data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(submit_response.status_code, 201)
        submit_data = json.loads(submit_response.data)
        app_id = submit_data["application_id"]

        get_response = self.client.get(f'/applications/{app_id}')
        self.assertEqual(get_response.status_code, 200)
        raw_app_data = json.loads(get_response.data)
        self.assertEqual(raw_app_data["application_id"], app_id)
        self.assertEqual(raw_app_data["business_name"], self.valid_payload["business_name"])

        not_found_response = self.client.get('/applications/nonexistentid')
        self.assertEqual(not_found_response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
