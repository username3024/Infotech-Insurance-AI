# AI Restaurant Underwriter

## Purpose
The AI Restaurant Underwriter is a proof-of-concept system designed to automate the risk assessment and premium calculation process for restaurant insurance applications. It aims to provide a quick, data-driven initial assessment for underwriters.

## Architecture
The system is built using a Python Flask backend with the following key components:
*   **Flask API (`app/api/`)**: Handles incoming application submissions and requests for assessment results.
*   **Core Logic (`app/core/`)**:
    *   `risk_engine.py`: Calculates a risk score based on application details.
    *   `premium_calculator.py`: Calculates an estimated insurance premium.
    *   `decision_engine.py`: Makes an underwriting decision (Approve, Refer, Decline) based on the risk score.
*   **Data Models (`app/models/`)**: Defines the structure for application data (`RestaurantApplication`) and assessment output (`RiskAssessmentOutput`).
*   **In-Memory Storage**: For this MVP, submitted applications and assessment results are stored in Python dictionaries in memory.

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory_name>
    ```
    (Replace `<repository_directory_name>` with the actual name of the cloned folder, likely `ai-restaurant-underwriter` or similar if cloned from a Git repo. If working locally, this is the `/app` directory.)

2.  **Create and Activate Virtual Environment:**
    Navigate to the project root directory (e.g., `/app` if that's where `ai_underwriter` and `run_tests.py` are).
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    Ensure your virtual environment is activated. The `requirements.txt` is inside the `ai_underwriter` sub-directory.
    ```bash
    pip install -r ai_underwriter/requirements.txt
    ```

4.  **Run the Application:**
    From the project root directory (`/app`), run:
    ```bash
    python ai_underwriter/main.py
    ```
    The application will typically be available at `http://127.0.0.1:5000/`.

## Running Unit Tests

Unit tests are provided to verify the functionality of core components and API endpoints.

1.  **Ensure Dependencies are Installed** (including any test-specific ones, though none are explicitly added for now beyond Flask and scikit-learn).
2.  **Navigate to the Project Root Directory** (e.g., `/app`).
3.  **Run the Test Suite:**
    ```bash
    python run_tests.py
    ```
    This script will discover and run all tests located in the `ai_underwriter/tests/` directory.

## API Usage Examples

### Submit an Application

*   **Endpoint:** `POST /applications/submit`
*   **Description:** Submits a new restaurant application for underwriting assessment.
*   **`curl` Example:**

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{
        "business_name": "The Gourmet Corner",
        "address": "456 Oak Avenue, Foodville",
        "cuisine_type": "French",
        "alcohol_sales_percentage": 0.40,
        "operating_hours": "6pm-11pm",
        "square_footage": 2200,
        "building_age": 8,
        "fire_suppression_system_type": "Ansul System with Sprinklers",
        "years_in_business": 3,
        "management_experience_years": 7,
        "has_delivery_operations": false,
        "has_catering_operations": true,
        "seating_capacity": 60,
        "annual_revenue": 750000.00,
        "health_inspection_score": 95.0,
        "previous_claims_count": 0
    }' http://localhost:5000/applications/submit
    ```

*   **Example Success Response (201 Created):**

    ```json
    {
        "application_id": "generated_uuid_hex_string",
        "risk_score": 4.75,
        "confidence_level": 0.8,
        "decision": "Refer to manual underwriter",
        "recommended_premium": 3456.25,
        "premium_breakdown": {
            "general_liability": 2375.00,
            "property": 1081.25
        },
        "risk_mitigation_recommendations": [
            "Consider further safety training for staff.",
            "Ensure fire extinguishers are regularly checked."
        ],
        "required_documentation": [
            "Copy of valid business license.",
            "Latest health inspection report."
        ],
        "explanation_factors": [
            "Calculated risk score: 4.75",
            "Decision based on risk score: Refer to manual underwriter",
            "Cuisine type considered: French",
            "Years in business: 3",
            "Alcohol sales percentage: 40.0%"
        ]
    }
    ```
    *(Note: Actual scores, premiums, and explanations will vary based on input and scoring logic.)*

### Other Endpoints

*   **`GET /assessment/<application_id>`**: Retrieves the full assessment output (as shown above) for a given `application_id`.
*   **`GET /applications/<application_id>`**: Retrieves the original raw data submitted for a given `application_id`.

Refer to `ai_underwriter/docs/api_docs.md` for detailed API documentation.
