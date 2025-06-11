import logging
from typing import Optional, Dict, Any
from app.models.data_models import RestaurantApplication

logger = logging.getLogger(__name__)

def calculate_risk_score(
    application: RestaurantApplication,
    health_data: Optional[Dict[str, Any]] = None,
    crime_data: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculates a simplified risk score for a restaurant application,
    optionally incorporating external health and crime data.
    """
    score = 5.0  # Base score
    logger.info(f"Starting risk score calculation for application {application.application_id} (or business {application.business_name}) with base score: {score}")

    # --- Original Application Data Logic ---
    # Cuisine Type Logic
    cuisine_scores = {
        "sushi": -0.5, "salad bar": -0.5, "cafe": -0.5, "fine dining": -0.2,
        "italian": 0.5, "mexican": 0.5, "chinese": 0.5,
        "steakhouse": 1.5, "fast food": 1.5, "food truck": 1.2, # Added food truck
        "bar": 1.0 # Added generic bar
    }
    cuisine_type_lower = application.cuisine_type.lower() if application.cuisine_type else ""
    cuisine_adjustment = cuisine_scores.get(cuisine_type_lower, 0.0)
    score += cuisine_adjustment
    logger.info(f"Score after cuisine ({application.cuisine_type}): {score} (adjustment: {cuisine_adjustment})")

    # Alcohol Sales Percentage Logic
    alcohol_adjustment = 0.0
    if application.alcohol_sales_percentage is not None:
        if application.alcohol_sales_percentage > 0.5:
            alcohol_adjustment = 1.5
        elif application.alcohol_sales_percentage > 0.25:
            alcohol_adjustment = 0.5
    score += alcohol_adjustment
    logger.info(f"Score after alcohol ({application.alcohol_sales_percentage*100}%): {score} (adjustment: {alcohol_adjustment})")

    # Years in Business Logic
    years_adjustment = 0.0
    if application.years_in_business is not None:
        if application.years_in_business < 2:
            years_adjustment = 1.0
        elif application.years_in_business > 10:
            years_adjustment = -0.5
    score += years_adjustment
    logger.info(f"Score after years in business ({application.years_in_business}): {score} (adjustment: {years_adjustment})")

    # Fire Suppression System Type Logic
    fire_suppression_adjustment = 0.0
    if application.fire_suppression_system_type:
        system_type_lower = application.fire_suppression_system_type.lower()
        if system_type_lower == "none":
            fire_suppression_adjustment = 2.0
        elif system_type_lower == "sprinkler":
            fire_suppression_adjustment = -0.5
        elif any(sub_type in system_type_lower for sub_type in ["ansul", "kitchen hood", "kitchen suppression"]):
            fire_suppression_adjustment = -1.0
    else: # If None or empty, treat as high risk
        fire_suppression_adjustment = 2.0
    score += fire_suppression_adjustment
    logger.info(f"Score after fire suppression ({application.fire_suppression_system_type}): {score} (adjustment: {fire_suppression_adjustment})")

    # Previous Claims Count Logic
    claims_adjustment = 0.0
    if application.previous_claims_count is not None:
        if application.previous_claims_count > 2:
            claims_adjustment = 1.5
        elif application.previous_claims_count >= 1:
            claims_adjustment = 0.5
    score += claims_adjustment
    logger.info(f"Score after previous claims ({application.previous_claims_count}): {score} (adjustment: {claims_adjustment})")

    # --- External Health Data Integration ---
    health_penalty = 0.0
    if health_data:
        logger.info(f"Processing health data: {health_data}")
        latest_health_score = health_data.get("latest_score")
        if isinstance(latest_health_score, (int, float)):
            if latest_health_score < 70:
                health_penalty += 2.0
                logger.info(f"Health penalty increased by 2.0 due to low health score: {latest_health_score}")
            elif latest_health_score < 85:
                health_penalty += 1.0
                logger.info(f"Health penalty increased by 1.0 due to moderate health score: {latest_health_score}")

        critical_violations = health_data.get("critical_violations_last_year")
        if isinstance(critical_violations, int):
            if critical_violations > 3:
                health_penalty += 1.5
                logger.info(f"Health penalty increased by 1.5 due to high critical violations: {critical_violations}")
            elif critical_violations > 0:
                health_penalty += 0.5
                logger.info(f"Health penalty increased by 0.5 due to critical violations: {critical_violations}")
    else:
        logger.info("No health data provided or found for risk scoring.")
        health_penalty = 0.5  # Small penalty if health data is missing
        logger.info(f"Health penalty set to {health_penalty} due to missing health data.")
    score += health_penalty
    logger.info(f"Score after health data integration: {score} (total health penalty: {health_penalty})")

    # --- External Crime Data Integration ---
    crime_penalty = 0.0
    if crime_data:
        logger.info(f"Processing crime data: {crime_data}")
        crime_level = crime_data.get("crime_level_area")
        if crime_level: # Check if crime_level is not None and not an empty string
            if crime_level.lower() == "high":
                crime_penalty += 1.5
                logger.info("Crime penalty increased by 1.5 due to high crime level in area.")
            elif crime_level.lower() == "medium":
                crime_penalty += 0.5
                logger.info("Crime penalty increased by 0.5 due to medium crime level in area.")

        safety_score_val = crime_data.get("safety_score")  # Assuming lower is worse
        if isinstance(safety_score_val, (int, float)):
            if safety_score_val < 4.0:
                crime_penalty += 1.0
                logger.info(f"Crime penalty increased by 1.0 due to low safety score: {safety_score_val}")
            elif safety_score_val < 7.0:
                crime_penalty += 0.5
                logger.info(f"Crime penalty increased by 0.5 due to moderate safety score: {safety_score_val}")
    else:
        logger.info("No crime data provided or found for risk scoring.")
        crime_penalty = 0.25  # Small penalty if crime data is missing
        logger.info(f"Crime penalty set to {crime_penalty} due to missing crime data.")
    score += crime_penalty
    logger.info(f"Score after crime data integration: {score} (total crime penalty: {crime_penalty})")

    final_score = max(1.0, min(score, 10.0))
    logger.info(f"Final capped score for application {application.application_id}: {final_score} (raw score was {score})")
    return final_score
