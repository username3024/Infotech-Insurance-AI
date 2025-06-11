import unittest
from app.models.data_models import RestaurantApplication
from app.core.premium_calculator import calculate_premium

class TestPremiumCalculator(unittest.TestCase):

    def _create_base_application_data(self, **kwargs):
        """Helper to create a base application with default values that can be overridden."""
        data = {
            "application_id": "test_prem_id",
            "business_name": "Premium Test Cafe",
            "address": "456 Test Ave",
            "cuisine_type": "Cafe",
            "alcohol_sales_percentage": 0.05,
            "operating_hours": "7am-3pm",
            "square_footage": 800,
            "building_age": 3,
            "fire_suppression_system_type": "Sprinkler",
            "years_in_business": 3,
            "management_experience_years": 2,
            "has_delivery_operations": False,
            "has_catering_operations": False,
            "seating_capacity": 20,
            "annual_revenue": 150000.0,
            "health_inspection_score": 95.0,
            "previous_claims_count": 0
        }
        data.update(kwargs)
        return RestaurantApplication(**data)

    def test_calculate_premium_low_risk(self):
        app = self._create_base_application_data()
        risk_score = 2.0  # Low risk score

        premiums = calculate_premium(app, risk_score)

        self.assertIn("total_premium", premiums)
        self.assertIn("general_liability_premium", premiums)
        self.assertIn("property_premium", premiums)

        # BASE_GL = 500, BASE_PROP = 300
        # alcohol_sales = 0.05, sq_footage = 800
        # expected_gl = 500 * 2.0 * (1 + 0.05 * 0.5) = 1000 * 1.025 = 1025.0
        # expected_prop = 300 * 2.0 * (800 / 1000.0) = 600 * 0.8 = 480.0
        # expected_total = 1025.0 + 480.0 = 1505.0

        self.assertAlmostEqual(premiums["general_liability_premium"], 1025.0, places=2)
        self.assertAlmostEqual(premiums["property_premium"], 480.0, places=2)
        self.assertAlmostEqual(premiums["total_premium"], 1505.0, places=2)

    def test_calculate_premium_high_risk(self):
        app = self._create_base_application_data(
            alcohol_sales_percentage=0.6,
            square_footage=3000
        )
        risk_score = 8.0  # High risk score

        premiums = calculate_premium(app, risk_score)

        # expected_gl = 500 * 8.0 * (1 + 0.6 * 0.5) = 4000 * 1.3 = 5200.0
        # expected_prop = 300 * 8.0 * (3000 / 1000.0) = 2400 * 3.0 = 7200.0
        # expected_total = 5200.0 + 7200.0 = 12400.0

        self.assertAlmostEqual(premiums["general_liability_premium"], 5200.0, places=2)
        self.assertAlmostEqual(premiums["property_premium"], 7200.0, places=2)
        self.assertAlmostEqual(premiums["total_premium"], 12400.0, places=2)

    def test_calculate_premium_with_none_values(self):
        app = self._create_base_application_data(
            alcohol_sales_percentage=None, # Should default to 0.0
            square_footage=None # Should default to 1000.0
        )
        risk_score = 5.0 # Mid risk

        premiums = calculate_premium(app, risk_score)

        # alcohol_sales = 0.0, sq_footage = 1000
        # expected_gl = 500 * 5.0 * (1 + 0.0 * 0.5) = 2500 * 1.0 = 2500.0
        # expected_prop = 300 * 5.0 * (1000 / 1000.0) = 1500 * 1.0 = 1500.0
        # expected_total = 2500.0 + 1500.0 = 4000.0

        self.assertAlmostEqual(premiums["general_liability_premium"], 2500.0, places=2)
        self.assertAlmostEqual(premiums["property_premium"], 1500.0, places=2)
        self.assertAlmostEqual(premiums["total_premium"], 4000.0, places=2)

    def test_calculate_premium_zero_sq_footage(self):
        app = self._create_base_application_data(square_footage=0) # Should default to 1000.0
        risk_score = 3.0

        premiums = calculate_premium(app, risk_score)

        # alcohol_sales = 0.05, sq_footage = 1000 (defaulted)
        # expected_gl = 500 * 3.0 * (1 + 0.05 * 0.5) = 1500 * 1.025 = 1537.5
        # expected_prop = 300 * 3.0 * (1000 / 1000.0) = 900 * 1.0 = 900.0
        # expected_total = 1537.5 + 900.0 = 2437.5

        self.assertAlmostEqual(premiums["property_premium"], 900.0, places=2)
        self.assertAlmostEqual(premiums["total_premium"], 2437.5, places=2)

if __name__ == '__main__':
    unittest.main()
