from typing import Dict
from app.models.data_models import RestaurantApplication

# Base Rates
BASE_GENERAL_LIABILITY_RATE = 500.0
BASE_PROPERTY_RATE = 300.0

def calculate_premium(application: RestaurantApplication, risk_score: float) -> Dict[str, float]:
    """
    Calculates a simplified insurance premium based on the application and risk score.
    """

    # Handle Potential None Values for Inputs and ensure logical defaults
    alcohol_sales = application.alcohol_sales_percentage if application.alcohol_sales_percentage is not None else 0.0

    # Use a default square footage if it's None, zero, or negative to avoid calculation errors
    sq_footage = application.square_footage if application.square_footage is not None and application.square_footage > 0 else 1000.0

    # Ensure risk_score is not extremely low to prevent near-zero premiums
    # The risk_score from risk_engine is already capped at min 1.0, so this is a safeguard
    effective_risk_score = max(1.0, risk_score)

    # Calculate General Liability Premium
    # Factor in alcohol sales: higher alcohol sales can increase liability risk
    gl_premium = BASE_GENERAL_LIABILITY_RATE * effective_risk_score * (1 + (alcohol_sales * 0.5))

    # Calculate Property Premium
    # Factor in square footage: larger properties may have higher property risk
    # Normalize square footage to a factor (e.g., per 1000 sq ft)
    prop_premium = BASE_PROPERTY_RATE * effective_risk_score * (sq_footage / 1000.0)

    # Calculate Total Premium
    total_premium = gl_premium + prop_premium

    return {
        "total_premium": round(total_premium, 2),
        "general_liability_premium": round(gl_premium, 2),
        "property_premium": round(prop_premium, 2)
    }
