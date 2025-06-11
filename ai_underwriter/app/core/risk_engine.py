from app.models.data_models import RestaurantApplication

def calculate_risk_score(application: RestaurantApplication) -> float:
    """
    Calculates a simplified risk score for a restaurant application.
    """
    score = 5.0  # Base score

    # Cuisine Type Logic
    cuisine_scores = {
        "sushi": -0.5, "salad bar": -0.5, "cafe": -0.5,
        "italian": 0.5, "mexican": 0.5, "chinese": 0.5,  # Assuming no heavy deep fry focus
        "steakhouse": 1.5, "fast food": 1.5,  # Typically involve more hazardous cooking
        "fine dining": -0.2
    }
    # Use .get() with a default of 0.0 if cuisine_type is not in the dictionary or is None
    score += cuisine_scores.get(application.cuisine_type.lower() if application.cuisine_type else "", 0.0)

    # Alcohol Sales Percentage Logic
    if application.alcohol_sales_percentage is not None:
        if application.alcohol_sales_percentage > 0.5:
            score += 1.5
        elif application.alcohol_sales_percentage > 0.25:
            score += 0.5

    # Years in Business Logic
    if application.years_in_business is not None:
        if application.years_in_business < 2:
            score += 1.0
        elif application.years_in_business > 10:
            score -= 0.5

    # Fire Suppression System Type Logic
    if application.fire_suppression_system_type: # Check if the string is not None or empty
        system_type_lower = application.fire_suppression_system_type.lower()
        if system_type_lower == "none":
            score += 2.0
        elif system_type_lower == "sprinkler":
            score -= 0.5
        elif "ansul" in system_type_lower or \
             "kitchen hood system" in system_type_lower or \
             "kitchen suppression" in system_type_lower: # Added more robust check
            score -= 1.0
    else: # If None or empty, treat as high risk for this factor
        score += 2.0


    # Previous Claims Count Logic
    if application.previous_claims_count is not None:
        if application.previous_claims_count > 2:
            score += 1.5
        elif application.previous_claims_count >= 1:  # handles 1 or 2
            score += 0.5

    # Ensure score is not below a minimum (e.g., 1.0) and not above a maximum (e.g., 10.0)
    return max(1.0, min(score, 10.0))
