import unittest
import json
from main import app # Import the Flask app instance
# To clear in-memory stores for each test run
from app.api.application_api import submitted_applications, assessment_results

class TestApplicationAPI(unittest.TestCase):

    def setUp(self):
        """Set up test client and other test variables."""
        app.testing = True
        self.client = app.test_client()
        # Clear in-memory storage before each test
        submitted_applications.clear()
        assessment_results.clear()

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

    def test_submit_application_success(self):
        """Test successful application submission and assessment."""
        response = self.client.post('/applications/submit',
                                     data=json.dumps(self.valid_payload),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

        self.assertIn("application_id", data)
        self.assertIsNotNone(data["application_id"])
        self.assertIn("risk_score", data)
        self.assertIn("decision", data)
        self.assertIn("recommended_premium", data)
        self.assertIn("premium_breakdown", data)
        self.assertIn("general_liability", data["premium_breakdown"])
        self.assertIn("property", data["premium_breakdown"])

        # Check that it's stored
        self.assertIn(data["application_id"], submitted_applications)
        self.assertIn(data["application_id"], assessment_results)

    def test_submit_application_bad_request_missing_field(self):
        """Test application submission with a missing required field."""
        payload = self.valid_payload.copy()
        del payload["business_name"]

        response = self.client.post('/applications/submit',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertTrue("Missing required fields" in data["error"] or "Missing required field" in data["error"])

    def test_submit_application_bad_request_invalid_data_type(self):
        """Test application submission with an invalid data type for a field."""
        payload = self.valid_payload.copy()
        payload["alcohol_sales_percentage"] = "not_a_float"

        response = self.client.post('/applications/submit',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        # This should ideally be caught by RestaurantApplication's type hints if strict,
        # or by the creation process. The error message might vary.
        # The current implementation of RestaurantApplication does not do strict type checking at runtime by itself.
        # The TypeError in application_api.py's try-except for RestaurantApplication(**data) will catch it.
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertTrue("Invalid application data format" in data["error"])


    def test_get_assessment_success_and_not_found(self):
        """Test retrieving an assessment successfully and handling not found."""
        # First, submit an application
        submit_response = self.client.post('/applications/submit',
                                           data=json.dumps(self.valid_payload),
                                           content_type='application/json')
        self.assertEqual(submit_response.status_code, 201)
        submit_data = json.loads(submit_response.data)
        app_id = submit_data["application_id"]

        # Test successful retrieval
        get_response = self.client.get(f'/applications/assessment/{app_id}')
        self.assertEqual(get_response.status_code, 200)
        assessment_data = json.loads(get_response.data)
        self.assertEqual(assessment_data["application_id"], app_id)
        self.assertEqual(assessment_data["risk_score"], submit_data["risk_score"])

        # Test not found
        not_found_response = self.client.get('/applications/assessment/nonexistentid')
        self.assertEqual(not_found_response.status_code, 404)
        not_found_data = json.loads(not_found_response.data)
        self.assertIn("error", not_found_data)
        self.assertEqual(not_found_data["error"], "Assessment not found for this application ID")

    def test_get_raw_application_success_and_not_found(self):
        """Test retrieving raw application data successfully and handling not found."""
        # First, submit an application
        submit_response = self.client.post('/applications/submit',
                                           data=json.dumps(self.valid_payload),
                                           content_type='application/json')
        self.assertEqual(submit_response.status_code, 201)
        submit_data = json.loads(submit_response.data)
        app_id = submit_data["application_id"]

        # Test successful retrieval of raw data
        get_response = self.client.get(f'/applications/{app_id}')
        self.assertEqual(get_response.status_code, 200)
        raw_app_data = json.loads(get_response.data)
        self.assertEqual(raw_app_data["application_id"], app_id)
        self.assertEqual(raw_app_data["business_name"], self.valid_payload["business_name"])

        # Test not found for raw data
        not_found_response = self.client.get('/applications/nonexistentid')
        self.assertEqual(not_found_response.status_code, 404)
        not_found_data = json.loads(not_found_response.data)
        self.assertIn("error", not_found_data)
        self.assertEqual(not_found_data["error"], "Application not found")

if __name__ == '__main__':
    unittest.main()
