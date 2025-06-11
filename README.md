# AI Restaurant Underwriter

## Purpose
The AI Restaurant Underwriter is a proof-of-concept system designed to automate the risk assessment and premium calculation process for restaurant insurance applications. It aims to provide a quick, data-driven initial assessment for underwriters.

## Architecture & Features
The system is built using a Python Flask backend with the following key components:
*   **Flask API (`app/api/`)**: Handles incoming application submissions and requests for assessment results.
*   **Core Logic (`app/core/`)**:
    *   `risk_engine.py`: Calculates a risk score based on application details and integrated external data.
    *   `premium_calculator.py`: Calculates an estimated insurance premium.
    *   `decision_engine.py`: Makes an underwriting decision (Approve, Refer, Decline) based on the risk score.
*   **Data Models (`app/models/`)**: Defines the structure for application data (`RestaurantApplication`) and assessment output (`RiskAssessmentOutput`).
*   **External Data Integration (`app/clients/`)**:
    *   Integrates external data for Public Health Inspections using `SimulatedHealthInspectionClient`, which reads from a local JSON data file (`simulated_health_data.json`).
    *   Integrates mock external data for Crime Statistics using `MockCrimeStatisticsClient`.
    *   These clients enhance risk assessment.
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

4.  **Run the Application (Development Mode):**
    From the project root directory (`/app`), run:
    ```bash
    python ai_underwriter/main.py
    ```
    The application will typically be available at `http://127.0.0.1:5000/`.

    To run with specific API key configurations for the simulated clients (examples):
    ```bash
    # To run with a specific (though mostly conceptual for simulated client) health API key:
    HEALTH_API_KEY="YOUR_TEST_KEY" python ai_underwriter/main.py

    # To test the invalid key behavior for the simulated health client:
    HEALTH_API_KEY="INVALID_KEY_TEST" python ai_underwriter/main.py
    ```

## Configuration

### External API Keys
*   The system demonstrates a pattern for using API keys via environment variables.
*   **Health Inspection Client (`SimulatedHealthInspectionClient`):**
    *   Reads the `HEALTH_API_KEY` environment variable.
    *   While this client loads data from a local JSON file and doesn't strictly need a key for access, it uses this variable to demonstrate the pattern.
    *   If `HEALTH_API_KEY` is set to `"INVALID_KEY_TEST"`, the client will simulate an API key error, which can be useful for testing error handling. Other key values are logged but do not gate access to the local file data.
    *   If `HEALTH_API_KEY` is not set, the client uses an internal default key ("SIM_DEFAULT_KEY").
*   **Crime Statistics Client (`MockCrimeStatisticsClient`):**
    *   Reads the `CRIME_API_KEY` environment variable. This is currently conceptual as the mock client doesn't perform validation against it.
*   Refer to `ai_underwriter/docs/external_sources.md` for more details on client behavior and future integration with live services.

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
*   **Description:** Submits a new restaurant application for underwriting assessment, including fetching data from simulated/mock external sources.
*   **`curl` Example:** (Payload remains the same as previous phase)

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
        "risk_score": 5.1, // Example, will vary based on inputs and external data
        "confidence_level": 0.7, // Example
        "decision": "Refer to manual underwriter", // Example
        "recommended_premium": 3980.00, // Example
        "premium_breakdown": {
            "general_liability": 2750.00,
            "property": 1230.00
        },
        "risk_mitigation_recommendations": [ /* ... */ ],
        "required_documentation": [ /* ... */ ],
        "explanation_factors": [ /* ... */ ],
        "health_inspection_summary": { // Populated by SimulatedHealthInspectionClient
            "latest_score": 85, // Or specific if "The Risky Diner" / "Super Clean Eats" submitted
            "last_inspection_date": "2023-08-20",
            "critical_violations_last_year": 1,
            "grade": "B",
            "status": "Pass",
            "source": "simulated_health_api_v2",
            "establishment_id_debug": "EST_AV003" // Example for "Average Joe's Diner"
        },
        "crime_statistics_summary": { // Populated by MockCrimeStatisticsClient
            "crime_level_area": "Medium", // Or specific if address matches mock
            "theft_incidents_last_year_nearby": 7,
            "vandalism_incidents_last_year_nearby": 3,
            "assault_incidents_last_year_nearby": 2,
            "safety_score": 6.5,
            "source": "mock_crime_statistics_api"
        }
    }
    ```
    *(Note: Actual scores, external data, premiums, and explanations will vary.)*

### Other Endpoints

*   **`GET /assessment/<application_id>`**: Retrieves the full assessment output (including external data summaries) for a given `application_id`.
*   **`GET /applications/<application_id>`**: Retrieves the original raw data submitted for a given `application_id`.

Refer to `ai_underwriter/docs/api_docs.md` for detailed API documentation and `ai_underwriter/docs/external_sources.md` for client behavior.
