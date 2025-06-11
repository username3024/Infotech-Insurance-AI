import uuid
from flask import Blueprint, request, jsonify
from app.models.data_models import RestaurantApplication, RiskAssessmentOutput
from app.core import calculate_risk_score, calculate_premium, make_decision

application_bp = Blueprint('application_api', __name__, url_prefix='/applications')

# In-memory storage for MVP
submitted_applications = {}
assessment_results = {}

@application_bp.route('/submit', methods=['POST'])
def submit_application():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # Pre-validation for required fields before creating RestaurantApplication instance
    required_fields = [
        'business_name', 'address', 'cuisine_type', 'alcohol_sales_percentage',
        'operating_hours', 'square_footage', 'building_age', 'fire_suppression_system_type',
        'years_in_business', 'management_experience_years', 'has_delivery_operations',
        'has_catering_operations', 'seating_capacity', 'annual_revenue',
        'health_inspection_score', 'previous_claims_count'
    ]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    application_id = uuid.uuid4().hex
    data['application_id'] = application_id # Add generated ID to data before creating object

    try:
        app_data = RestaurantApplication(**data)
    except TypeError as e:
        return jsonify({"error": f"Invalid application data format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred during application creation: {str(e)}"}), 500

    # Store raw application data
    submitted_applications[application_id] = app_data.to_dict()

    # Perform assessment
    try:
        risk_score = calculate_risk_score(app_data)
        premium_details = calculate_premium(app_data, risk_score)
        decision = make_decision(risk_score)
    except Exception as e:
        # Catch any error during the assessment phase
        return jsonify({"error": f"Error during assessment process: {str(e)}", "application_id": application_id}), 500

    # Construct RiskAssessmentOutput
    assessment_output = RiskAssessmentOutput(
        application_id=app_data.application_id,
        risk_score=risk_score,
        confidence_level=0.8,  # Placeholder for MVP
        decision=decision,
        recommended_premium=premium_details["total_premium"],
        premium_breakdown={
            "general_liability": premium_details["general_liability_premium"],
            "property": premium_details["property_premium"]
        },
        risk_mitigation_recommendations=["Consider further safety training for staff.", "Ensure fire extinguishers are regularly checked."],  # Placeholder
        required_documentation=["Copy of valid business license.", "Latest health inspection report."],  # Placeholder
        explanation_factors=[
            f"Calculated risk score: {risk_score:.2f}",
            f"Decision based on risk score: {decision}",
            f"Cuisine type considered: {app_data.cuisine_type}",
            f"Years in business: {app_data.years_in_business}",
            f"Alcohol sales percentage: {app_data.alcohol_sales_percentage*100}%"
        ]  # Placeholder
    )

    # Store assessment results
    assessment_results[application_id] = assessment_output.to_dict()

    return jsonify(assessment_output.to_dict()), 201

@application_bp.route('/<string:application_id>', methods=['GET'])
def get_application(application_id: str):
    """Retrieves the originally submitted application data."""
    application_data = submitted_applications.get(application_id)
    if application_data:
        return jsonify(application_data), 200
    return jsonify({"error": "Application not found"}), 404

@application_bp.route('/assessment/<string:application_id>', methods=['GET'])
def get_assessment(application_id: str):
    """Retrieves the assessment results for a given application ID."""
    result = assessment_results.get(application_id)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Assessment not found for this application ID"}), 404
