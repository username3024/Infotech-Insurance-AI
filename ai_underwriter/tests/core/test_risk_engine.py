import unittest
from app.models.data_models import RestaurantApplication
from app.core.risk_engine import calculate_risk_score

class TestRiskEngine(unittest.TestCase):

    def _create_base_application_data(self, **kwargs):
        """Helper to create a base application with default values that can be overridden."""
        data = {
            "application_id": "test_app_id",
            "business_name": "Testaurant",
            "address": "123 Test St",
            "cuisine_type": "Italian",
            "alcohol_sales_percentage": 0.1,
            "operating_hours": "9am-10pm",
            "square_footage": 1500,
            "building_age": 5,
            "fire_suppression_system_type": "Ansul",
            "years_in_business": 5,
            "management_experience_years": 5,
            "has_delivery_operations": False,
            "has_catering_operations": False,
            "seating_capacity": 50,
            "annual_revenue": 300000.0,
            "health_inspection_score": 90.0,
            "previous_claims_count": 0
        }
        data.update(kwargs)
        return RestaurantApplication(**data)

    def test_low_risk_scenario(self):
        app = self._create_base_application_data(
            cuisine_type="Salad Bar", # Low risk
            alcohol_sales_percentage=0.0, # Low risk
            fire_suppression_system_type="Ansul", # Low risk
            years_in_business=12, # Low risk
            previous_claims_count=0 # Low risk
        )
        score = calculate_risk_score(app)
        self.assertTrue(1.0 <= score <= 3.5, f"Score was {score}") # Expecting a low score

    def test_high_risk_scenario(self):
        app = self._create_base_application_data(
            cuisine_type="Steakhouse", # High risk
            alcohol_sales_percentage=0.6, # High risk
            fire_suppression_system_type="None", # High risk
            years_in_business=1, # High risk
            previous_claims_count=3 # High risk
        )
        score = calculate_risk_score(app)
        self.assertTrue(score > 6.5, f"Score was {score}") # Expecting a high score

    def test_mid_risk_scenario(self):
        # Default base application should be somewhat mid-risk
        app = self._create_base_application_data(
            cuisine_type="Italian",
            alcohol_sales_percentage=0.30, # Moderate
            fire_suppression_system_type="Sprinkler", # Moderate
            years_in_business=3, # Moderate
            previous_claims_count=1 # Moderate
        )
        score = calculate_risk_score(app)
        self.assertTrue(3.0 <= score <= 7.0, f"Score was {score}") # Broader range for mid-tier

    def test_score_boundaries(self):
        # Test with values that should push score to min 1.0
        app_min = self._create_base_application_data(
            cuisine_type="Salad Bar", alcohol_sales_percentage=0.0,
            fire_suppression_system_type="Ansul Kitchen Suppression", years_in_business=20,
            previous_claims_count=0, square_footage=500, building_age=1
        )
        score_min = calculate_risk_score(app_min)
        self.assertEqual(score_min, 1.0, f"Min score was {score_min}")

        # Test with values that should push score to max 10.0
        app_max = self._create_base_application_data(
            cuisine_type="Steakhouse", alcohol_sales_percentage=0.8,
            fire_suppression_system_type="None", years_in_business=1,
            previous_claims_count=5, square_footage=5000, building_age=50
        )
        score_max = calculate_risk_score(app_max)
        self.assertEqual(score_max, 10.0, f"Max score was {score_max}")

    def test_unknown_cuisine(self):
        app = self._create_base_application_data(cuisine_type=" Martian ") # Unknown, spaces for robustness
        score = calculate_risk_score(app)
        # Should not drastically change from base or error out, default 0.0 for cuisine impact
        # Base score 5.0, Italian is +0.5. No cuisine is 0.0. So score should be 0.5 less.
        app_italian = self._create_base_application_data(cuisine_type="Italian")
        score_italian = calculate_risk_score(app_italian)
        self.assertAlmostEqual(score, score_italian - 0.5, delta=0.01)

    def test_fire_suppression_variations(self):
        app_ansul_lower = self._create_base_application_data(fire_suppression_system_type="ansul")
        score_ansul_lower = calculate_risk_score(app_ansul_lower)

        app_ansul_mixed = self._create_base_application_data(fire_suppression_system_type="Ansul System")
        score_ansul_mixed = calculate_risk_score(app_ansul_mixed)
        self.assertAlmostEqual(score_ansul_lower, score_ansul_mixed, delta=0.01)

        app_kitchen_hood = self._create_base_application_data(fire_suppression_system_type="Kitchen Hood System")
        score_kitchen_hood = calculate_risk_score(app_kitchen_hood)
        self.assertAlmostEqual(score_ansul_lower, score_kitchen_hood, delta=0.01)

        app_none = self._create_base_application_data(fire_suppression_system_type="NONE")
        score_none = calculate_risk_score(app_none)
        app_empty = self._create_base_application_data(fire_suppression_system_type="") # Should be treated as None
        score_empty = calculate_risk_score(app_empty)
        self.assertAlmostEqual(score_none, score_empty, delta=0.01)


if __name__ == '__main__':
    unittest.main()
