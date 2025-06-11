# AI Restaurant Underwriter

## Purpose
The AI Restaurant Underwriter is a proof-of-concept system designed to automate the risk assessment and premium calculation process for restaurant insurance applications. It aims to provide a quick, data-driven initial assessment for underwriters.

## Architecture & Features
The system is built using a Python Flask backend with the following key components:
*   **Flask API (`app/api/`)**: Handles incoming application submissions and requests for assessment results.
*   **Core Logic (`app/core/`)**:
    *   `risk_engine.py`: Calculates a risk score based on application details.
    *   `premium_calculator.py`: Calculates an estimated insurance premium.
    *   `decision_engine.py`: Makes an underwriting decision (Approve, Refer, Decline) based on the risk score.
*   **Data Models (`app/models/`)**: Defines the structure for application data (`RestaurantApplication`) and assessment output (`RiskAssessmentOutput`).
*   **External Data Integration (`app/clients/`)**: Integrates mock external data for Public Health Inspections and Crime Statistics to enhance risk assessment. For this MVP, these are mock clients returning predefined data.
*   **In-Memory Storage**: For this MVP, submitted applications and assessment results are stored in Python dictionaries in memory.

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory_name>
    ```
    (Replace `<repository_directory_name>` with the actual name of the cloned folder. If working locally, this is the `/app` directory where `ai_underwriter` and `run_tests.py` reside.)

2.  **Create and Activate Virtual Environment:**
    Navigate to the project root directory (e.g., `/app`).
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

## Configuration

### External API Keys
*   Currently, the system uses **mock clients** for external data (Health Inspections, Crime Statistics), so no real API keys are required for operation.
*   If connecting to live external services in the future, API keys would typically be configured via environment variables (e.g., `HEALTH_API_KEY`, `CRIME_API_KEY`). These are notionally passed to client constructors in `ai_underwriter/app/api/application_api.py` but are placeholders for now. Refer to `ai_underwriter/docs/external_sources.md` for more details on mock behavior and future integration.

## Running Unit Tests

Unit tests are provided to verify the functionality of core components, API endpoints, and client integrations.

1.  **Ensure Dependencies are Installed.**
2.  **Navigate to the Project Root Directory** (e.g., `/app`).
3.  **Run the Test Suite:**
    ```bash
    python run_tests.py
    ```
    This script will discover and run all tests located in the `ai_underwriter/tests/` directory.

## API Usage Examples

### Submit an Application

*   **Endpoint:** `POST /applications/submit`
*   **Description:** Submits a new restaurant application for underwriting assessment, including fetching mock external data.
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
        "risk_score": 5.25, // Example, will vary
        "confidence_level": 0.75,
        "decision": "Refer to manual underwriter", // Example
        "recommended_premium": 4015.62, // Example
        "premium_breakdown": {
            "general_liability": 2812.50,
            "property": 1203.12
        },
        "risk_mitigation_recommendations": [
            "Review safety protocols.",
            "Ensure compliance with all local health and safety codes."
        ],
        "required_documentation": [
            "Copy of valid business license.",
            "Proof of latest health inspection."
        ],
        "explanation_factors": [
            "Calculated risk score: 5.25",
            "Decision based on risk score: Refer to manual underwriter",
            "Cuisine type (French) considered.",
            // ... more factors
            "Health score from external source: 85", // Example from generic mock
            "Area crime level from external source: Medium" // Example from generic mock
        ],
        "health_inspection_summary": {
            "latest_score": 85,
            "last_inspection_date": "2023-06-01",
            "critical_violations_last_year": 1,
            "non_critical_violations_last_year": 3,
            "summary_url": "http://example.com/inspections/generic",
            "source": "mock_health_department_api"
        },
        "crime_statistics_summary": {
            "crime_level_area": "Medium",
            "theft_incidents_last_year_nearby": 7,
            "vandalism_incidents_last_year_nearby": 3,
            "assault_incidents_last_year_nearby": 2,
            "safety_score": 6.5,
            "source": "mock_crime_statistics_api"
        }
    }
    ```
    *(Note: Actual scores, external data, premiums, and explanations will vary based on input and mock client logic.)*

### Other Endpoints

*   **`GET /assessment/<application_id>`**: Retrieves the full assessment output (including external data summaries) for a given `application_id`.
*   **`GET /applications/<application_id>`**: Retrieves the original raw data submitted for a given `application_id`.

Refer to `ai_underwriter/docs/api_docs.md` for detailed API documentation and `ai_underwriter/docs/external_sources.md` for mock client behavior.
