# Decision Thresholds
APPROVE_THRESHOLD = 3.5
REFER_THRESHOLD = 6.5
# Risk score is expected to be between 1.0 and 10.0 from risk_engine.py

def make_decision(risk_score: float) -> str:
    """
    Makes an underwriting decision based on the provided risk score.
    """
    if risk_score is None:
        return "Error: Risk score not provided"

    if not isinstance(risk_score, (int, float)):
        return "Error: Invalid risk score type"

    # Ensure risk_score is within expected bounds for decision making,
    # though risk_engine already caps it. This is a safeguard.
    if not (1.0 <= risk_score <= 10.0):
        # This case should ideally not be reached if risk_score comes from calculate_risk_score
        return "Error: Risk score out of expected range (1.0-10.0)"

    if risk_score <= APPROVE_THRESHOLD:
        return "Approved"
    elif risk_score <= REFER_THRESHOLD:
        return "Refer to manual underwriter"
    else:  # risk_score > REFER_THRESHOLD
        return "Declined"
