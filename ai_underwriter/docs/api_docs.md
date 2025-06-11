# AI Restaurant Underwriter API Documentation

## Introduction
This document provides detailed information about the API endpoints available in the AI Restaurant Underwriter system. These endpoints allow for the submission of restaurant applications and retrieval of their underwriting assessments. The system now integrates mock external data for health inspections and crime statistics to provide a more comprehensive risk assessment.

---

## Endpoint: Submit Application

*   **Description:** Submits a new restaurant application for automated underwriting assessment. The system calculates a risk score (incorporating mock external data), determines a premium, and makes an initial underwriting decision.
*   **Method:** `POST`
*   **URL:** `/applications/submit`
*   **Request Body (`application/json`):**
    The JSON payload should contain the following fields representing the restaurant's application details:

    *   `business_name: string (required)` - The legal name of the business.
    *   `address: string (required)` - The full physical address of the restaurant.
    *   `cuisine_type: string (required)` - The primary type of cuisine served (e.g., "Italian", "Mexican", "Sushi", "Steakhouse").
    *   `alcohol_sales_percentage: float (required)` - The estimated percentage of total sales derived from alcohol (e.g., 0.25 for 25%). Must be between 0.0 and 1.0.
    *   `operating_hours: string (required)` - The typical operating hours (e.g., "9am-5pm", "6pm-2am").
    *   `square_footage: int (required)` - The total square footage of the restaurant premises. Must be a positive integer.
    *   `building_age: int (required)` - The age of the building in years. Must be a non-negative integer.
    *   `fire_suppression_system_type: string (required)` - Type of fire suppression system in place (e.g., "Ansul", "Sprinkler", "Kitchen Hood System", "None").
    *   `years_in_business: int (required)` - Number of years the current restaurant has been in business. Must be a non-negative integer.
    *   `management_experience_years: int (required)` - Total years of experience of key management in the restaurant industry. Must be a non-negative integer.
    *   `has_delivery_operations: boolean (required)` - Whether the restaurant conducts delivery operations.
    *   `has_catering_operations: boolean (required)` - Whether the restaurant conducts catering operations.
    *   `seating_capacity: int (required)` - The maximum number of patrons that can be seated. Must be a non-negative integer.
    *   `annual_revenue: float (required)` - The latest full year's annual revenue. Must be a non-negative number.
    *   `health_inspection_score: float (required)` - The latest health inspection score reported on the application form.
    *   `previous_claims_count: int (required)` - Number of insurance claims in the past 3-5 years. Must be a non-negative integer.

*   **Success Response (`201 Created`):**
    The response body will be a JSON object representing the `RiskAssessmentOutput`:

    *   `application_id: string` - Unique identifier for the submitted application.
    *   `risk_score: float` - The calculated risk score (e.g., on a 1-10 scale), influenced by application data and mock external data.
    *   `confidence_level: float` - (Placeholder, e.g., 0.75) Confidence in the assessment.
    *   `decision: string` - The underwriting decision (e.g., "Approved", "Declined", "Refer to manual underwriter").
    *   `recommended_premium: float` - The total recommended insurance premium.
    *   `premium_breakdown: object` - Breakdown of the premium:
        *   `general_liability: float` - Portion of premium for general liability.
        *   `property: float` - Portion of premium for property coverage.
    *   `risk_mitigation_recommendations: array of strings` - (Placeholder) Suggestions to mitigate risks.
    *   `required_documentation: array of strings` - (Placeholder) List of documents required to proceed.
    *   `explanation_factors: array of strings` - (Placeholder) Key factors influencing the assessment, may include notes on external data.
    *   `health_inspection_summary: object (optional)` - Contains summary of health inspection data from the mock client. Structure detailed below. Can be `null` if the client call fails or returns no data.
    *   `crime_statistics_summary: object (optional)` - Contains summary of crime statistics data from the mock client. Structure detailed below. Can be `null` if the client call fails or returns no data.

    **`health_inspection_summary` Object Structure:**
    *   `latest_score: number` - The latest health inspection score from the mock source.
    *   `last_inspection_date: string (date)` - Date of the last mock inspection.
    *   `critical_violations_last_year: integer` - Number of critical violations in the last year (mock data).
    *   `non_critical_violations_last_year: integer` - Number of non-critical violations (mock data, if present).
    *   `summary_url: string (url)` - URL to a mock inspection summary (if present).
    *   `source: string` - Indicates the source of the data (e.g., "mock_health_department_api").

    **`crime_statistics_summary` Object Structure:**
    *   `crime_level_area: string` - General crime level in the area (e.g., "Low", "Medium", "High") from mock source.
    *   `theft_incidents_last_year_nearby: integer` - Number of theft incidents (mock data).
    *   `vandalism_incidents_last_year_nearby: integer` - Number of vandalism incidents (mock data).
    *   `assault_incidents_last_year_nearby: integer` - Number of assault incidents (mock data, if present).
    *   `safety_score: number` - An arbitrary safety score for the area (mock data).
    *   `source: string` - Indicates the source of the data (e.g., "mock_crime_statistics_api").

*   **Error Responses:**
    *   `400 Bad Request`: Returned if the request payload is malformed, missing required fields, or contains invalid data types. Response body: `{"error": "description"}`.
    *   `500 Internal Server Error`: Returned if an unexpected error occurs on the server during processing (e.g., an unhandled exception in core logic, though client errors are handled gracefully by proceeding with `null` data).

---

## Endpoint: Get Assessment Results

*   **Description:** Retrieves the full assessment results for a previously submitted application using its unique application ID. This includes any data retrieved from mock external sources.
*   **Method:** `GET`
*   **URL:** `/assessment/<string:application_id>`
*   **Path Parameters:**
    *   `application_id: string (required)` - The unique identifier of the application.
*   **Success Response (`200 OK`):**
    The response body will be a JSON object with the same structure as the success response for `POST /applications/submit` (i.e., the `RiskAssessmentOutput`, including `health_inspection_summary` and `crime_statistics_summary` if they were captured).
*   **Error Responses:**
    *   `404 Not Found`: Returned if no assessment is found for the provided `application_id`. Response body: `{"error": "Assessment not found for this application ID"}`.

---

## Endpoint: Get Original Application Data

*   **Description:** Retrieves the original raw data that was submitted for a specific application. This does **not** include the external data summaries.
*   **Method:** `GET`
*   **URL:** `/applications/<string:application_id>`
*   **Path Parameters:**
    *   `application_id: string (required)` - The unique identifier of the application.
*   **Success Response (`200 OK`):**
    The response body will be a JSON object representing the `RestaurantApplication` data as it was submitted.
*   **Error Responses:**
    *   `404 Not Found`: Returned if no application data is found for the provided `application_id`. Response body: `{"error": "Application not found"}`.

---
For details on the behavior of the mock external clients, see `external_sources.md`.
