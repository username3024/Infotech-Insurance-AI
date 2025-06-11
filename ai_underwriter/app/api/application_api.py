import uuid
import logging
import os # Added
from flask import Blueprint, request, jsonify
from app.models.data_models import RestaurantApplication, RiskAssessmentOutput
from app.core import calculate_risk_score, calculate_premium, make_decision
# Updated to include SimulatedHealthInspectionClient
from app.clients import SimulatedHealthInspectionClient, MockCrimeStatisticsClient

application_bp = Blueprint('application_api', __name__, url_prefix='/applications')
logger = logging.getLogger(__name__)

# In-memory storage for MVP
submitted_applications = {}
assessment_results = {}

# --- Client Instantiation with Environment Variable for API Keys ---
# For SimulatedHealthInspectionClient, an actual key isn't strictly needed for local file access,
# but we implement the pattern. It can use this key for simulated checks if desired.
# The default in os.environ.get() is None, which means the client's __init__ default will be used if env var is missing.
HEALTH_API_KEY_FROM_ENV = os.environ.get('HEALTH_API_KEY')
logger.info(f"HEALTH_API_KEY from environment: {'SET' if HEALTH_API_KEY_FROM_ENV else 'NOT SET'}")


# For MockCrimeStatisticsClient, it's also conceptual as it's a mock.
CRIME_API_KEY_FROM_ENV = os.environ.get('CRIME_API_KEY')
logger.info(f"CRIME_API_KEY from environment: {'SET' if CRIME_API_KEY_FROM_ENV else 'NOT SET'}")

# Instantiate the new SimulatedHealthInspectionClient
# The base_url is also conceptual for the simulated client.
health_inspection_client = SimulatedHealthInspectionClient(
    base_url="http://simulated.healthdept.api", # Example base URL, not used by file-based sim
    api_key=HEALTH_API_KEY_FROM_ENV
    # data_file_path will use its default from __init__
)

# MockCrimeStatisticsClient remains as is, but now uses env var for its key
crime_statistics_client = MockCrimeStatisticsClient(
    api_key=CRIME_API_KEY_FROM_ENV
)
# --- End Client Instantiation ---


@application_bp.route('/submit', methods=['POST'])
def submit_application():
    data = request.get_json()

    if not data:
        logger.warning("Submit attempt with no input data.")
        return jsonify({"error": "No input data provided"}), 400

    required_fields = [
        'business_name', 'address', 'cuisine_type', 'alcohol_sales_percentage',
        'operating_hours', 'square_footage', 'building_age', 'fire_suppression_system_type',
        'years_in_business', 'management_experience_years', 'has_delivery_operations',
        'has_catering_operations', 'seating_capacity', 'annual_revenue',
        'health_inspection_score', 'previous_claims_count'
    ]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        logger.warning(f"Submit attempt with missing fields: {missing_fields}")
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    application_id = uuid.uuid4().hex
    data_with_id = {**data, 'application_id': application_id}

    try:
        app_data = RestaurantApplication(**data_with_id)
    except TypeError as e:
        logger.error(f"Error creating RestaurantApplication for ID {application_id}: {e}", exc_info=True)
        return jsonify({"error": f"Invalid application data format: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error during application object creation for ID {application_id}: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred during application creation: {str(e)}"}), 500

    submitted_applications[application_id] = app_data.to_dict()
    logger.info(f"Application {application_id} ({app_data.business_name}) stored.")

    logger.info(f"Fetching external data for application ID: {application_id}...")
    health_data_summary = None
    try:
        # SimulatedHealthInspectionClient's get_inspection_data might require city, state, zip
        # For now, passing them as None if not readily available from app_data.
        # Modify if app_data.address needs parsing or if these fields are added to RestaurantApplication.
        health_data_summary = health_inspection_client.get_inspection_data(
            address=app_data.address,
            business_name=app_data.business_name,
            city=None, # Assuming city is not directly in app_data.address for now
            state=None, # Assuming state is not directly in app_data.address
            zip_code=None # Assuming zip is not directly in app_data.address
        )
        logger.info(f"Health data received for {application_id}: {health_data_summary}")
    except Exception as e:
        logger.error(f"Error fetching health inspection data for {application_id}: {e}", exc_info=True)

    crime_data_summary = None
    try:
        crime_data_summary = crime_statistics_client.get_crime_data(
            address=app_data.address
        )
        logger.info(f"Crime data received for {application_id}: {crime_data_summary}")
    except Exception as e:
        logger.error(f"Error fetching crime statistics data for {application_id}: {e}", exc_info=True)

    try:
        logger.info(f"Calculating risk score for {application_id} with external data...")
        risk_score = calculate_risk_score(
            application=app_data,
            health_data=health_data_summary,
            crime_data=crime_data_summary
        )
        logger.info(f"Risk score for {application_id}: {risk_score}")

        premium_details = calculate_premium(app_data, risk_score)
        logger.info(f"Premium details for {application_id}: {premium_details}")

        decision = make_decision(risk_score)
        logger.info(f"Decision for {application_id}: {decision}")

    except Exception as e:
        logger.error(f"Error during assessment process for {application_id}: {e}", exc_info=True)
        return jsonify({"error": f"Error during assessment process: {str(e)}", "application_id": application_id}), 500

    current_explanation_factors = [
            f"Calculated risk score: {risk_score:.2f}",
            f"Decision based on risk score: {decision}",
            f"Cuisine type ({app_data.cuisine_type}) considered.",
            f"Years in business ({app_data.years_in_business}) considered.",
            f"Alcohol sales percentage ({app_data.alcohol_sales_percentage*100}%) considered."
    ]
    if health_data_summary and not health_data_summary.get("error"): # Add factor if data is valid
        current_explanation_factors.append(f"Health score from external source: {health_data_summary.get('latest_score', 'N/A')}")
    elif health_data_summary and health_data_summary.get("error"):
         current_explanation_factors.append(f"Health data error: {health_data_summary.get('error')}")
    if crime_data_summary and not crime_data_summary.get("error"): # Add factor if data is valid
        current_explanation_factors.append(f"Area crime level from external source: {crime_data_summary.get('crime_level_area', 'N/A')}")
    elif crime_data_summary and crime_data_summary.get("error"):
        current_explanation_factors.append(f"Crime data error: {crime_data_summary.get('error')}")


    assessment_output = RiskAssessmentOutput(
        application_id=app_data.application_id,
        risk_score=risk_score,
        confidence_level=0.70,  # Slightly adjusted placeholder
        decision=decision,
        recommended_premium=premium_details.get("total_premium", 0.0), # Ensure default
        premium_breakdown={
            "general_liability": premium_details.get("general_liability_premium", 0.0),
            "property": premium_details.get("property_premium", 0.0)
        },
        risk_mitigation_recommendations=["Review safety protocols.", "Ensure compliance with all local health and safety codes."],
        required_documentation=["Copy of valid business license.", "Proof of latest health inspection if available from external source."],
        explanation_factors=current_explanation_factors,
        health_inspection_summary=health_data_summary,
        crime_statistics_summary=crime_data_summary
    )

    assessment_results[application_id] = assessment_output.to_dict()
    logger.info(f"Assessment for {application_id} completed and stored.")

    return jsonify(assessment_output.to_dict()), 201

@application_bp.route('/<string:application_id>', methods=['GET'])
def get_application(application_id: str):
    logger.info(f"Attempting to retrieve raw application data for ID: {application_id}")
    application_data = submitted_applications.get(application_id)
    if application_data:
        return jsonify(application_data), 200
    logger.warning(f"Raw application data for ID: {application_id} not found.")
    return jsonify({"error": "Application not found"}), 404

@application_bp.route('/assessment/<string:application_id>', methods=['GET'])
def get_assessment(application_id: str):
    logger.info(f"Attempting to retrieve assessment results for ID: {application_id}")
    result = assessment_results.get(application_id)
    if result:
        return jsonify(result), 200
    logger.warning(f"Assessment results for ID: {application_id} not found.")
    return jsonify({"error": "Assessment not found for this application ID"}), 404

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
