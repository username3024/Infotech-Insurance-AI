# External Data Sources and Client Behavior

The AI Underwriter system is designed to integrate with external data sources to enhance its risk assessment capabilities. In the current version, this is primarily achieved using simulated and mock clients.

## Client Implementations

### 1. Health Inspection Data (`SimulatedHealthInspectionClient`)

*   **Location:** `ai_underwriter/app/clients/health_inspection_client.py` (contains `SimulatedHealthInspectionClient`)
*   **Data Source:** Loads its data from `ai_underwriter/app/clients/data/simulated_health_data.json`. This file contains sample detailed health inspection records for a few predefined restaurants.
*   **Trigger:** Called by the API when an application is submitted. It uses the `business_name`, `address` (and optionally `city`, `state`, `zip_code`, though these are not strictly used by the current file-based lookup) from the application.
*   **Lookup Logic:**
    1.  Attempts to find a record by exact case-insensitive match on `business_name`.
    2.  If no match, it iterates through records and checks if any `search_keywords` (defined in the JSON for each record) are present in the provided `address` (case-insensitive).
    3.  If no match is found, it returns a specific "Establishment not found" response.
*   **API Key (`HEALTH_API_KEY` Environment Variable):**
    *   The client constructor accepts an `api_key`. In `application_api.py`, this is read from the `HEALTH_API_KEY` environment variable.
    *   If `HEALTH_API_KEY` is set to the specific string `"INVALID_KEY_TEST"`, the client's `get_inspection_data` method will return an error dictionary `{"error": "Invalid API Key", "source": "simulated_health_api_error"}`. This is for testing the API key error handling flow.
    *   For any other key value (or if the key is not set, in which case the client uses its internal default "SIM_DEFAULT_KEY"), the client proceeds to load and return data from the JSON file. The key itself is not used to gate access to the local file beyond the "INVALID_KEY_TEST" check.
*   **Output Transformation:**
    *   If a record is found, the client transforms the detailed data from `simulated_health_data.json` into a simpler `health_inspection_summary` dictionary. This summary includes:
        *   `latest_score`
        *   `last_inspection_date`
        *   `critical_violations_last_year` (derived from `historical_summary` in JSON, or calculated from `last_inspection.violations` as a fallback)
        *   `grade`
        *   `status`
        *   `source` (e.g., "simulated_health_api_v2")
        *   `establishment_id_debug` (for traceability)
*   **Impact on Risk Score:** The `risk_engine.py` uses `latest_score` and `critical_violations_last_year` from this summary to adjust the risk score. Penalties apply if data is missing or an error (like invalid API key) is indicated.

#### Structure of `simulated_health_data.json`
This JSON file contains a list of objects. Each object represents a restaurant's health inspection record and includes fields like:
*   `establishment_id: string`
*   `business_name: string`
*   `address: string`
*   `search_keywords: array of strings` (for address matching)
*   `last_inspection: object` containing:
    *   `inspection_id: string`
    *   `inspection_date: string (date)`
    *   `score: number`
    *   `grade: string`
    *   `status: string`
    *   `violations: array of objects` (each with `violation_code`, `description`, `severity`)
*   `historical_summary: object` (e.g., `critical_violations_last_12_months: integer`)
*   `data_source_details: object` (metadata about the simulated data)

### 2. Crime Statistics Data (`MockCrimeStatisticsClient`)

*   **Location:** `ai_underwriter/app/clients/crime_statistics_client.py`
*   **Data Source:** Returns hardcoded data based on address keywords.
*   **Trigger:** Called by the API when an application is submitted, using the `address`.
*   **API Key (`CRIME_API_KEY` Environment Variable):**
    *   The client constructor accepts an `api_key` (read from `CRIME_API_KEY` in `application_api.py`), but the current `MockCrimeStatisticsClient` does not use this key for any validation or logic; it's a placeholder for the pattern.
*   **Behavior:**
    *   If `address` (case-insensitive) contains **"123 Main St"**: Returns a "Low" crime profile.
    *   If `address` (case-insensitive) contains **"999 Danger Ave"**: Returns a "High" crime profile.
    *   For **other addresses**: Returns a "Medium" crime profile.
*   **Output Structure:** The returned dictionary includes `crime_level_area`, `theft_incidents_last_year_nearby`, `vandalism_incidents_last_year_nearby`, `assault_incidents_last_year_nearby`, `safety_score`, and `source`.
*   **Impact on Risk Score:** The `risk_engine.py` uses `crime_level_area` and `safety_score` to adjust the risk score. Penalties apply if data is missing.

## Future Integration with Live Services

To connect to live external services, the following steps would typically be involved:

1.  **Identify and Subscribe to Services:** Choose real-world providers for health inspection and crime statistics data.
2.  **Develop New Client Classes:** Create new Python classes in `ai_underwriter/app/clients/` that implement the communication logic (e.g., HTTP requests, authentication, data parsing) for the chosen live APIs. These clients should ideally conform to a similar interface as the `SimulatedHealthInspectionClient` or `MockCrimeStatisticsClient` (e.g., a `get_inspection_data` method that returns a dictionary in the expected `health_inspection_summary` or `crime_statistics_summary` format).
3.  **Obtain API Keys:** Securely acquire and store API keys and any other necessary credentials for the live services.
4.  **Configuration Management:** Implement a robust way to manage these API keys, typically using environment variables (e.g., `PROD_HEALTH_API_KEY`, `PROD_CRIME_API_KEY`).
5.  **Update Client Instantiation:** Modify `ai_underwriter/app/api/application_api.py` to instantiate these new live client classes, passing the configured API keys. Conditional instantiation (e.g., based on an environment setting like `APP_ENV=production` vs. `APP_ENV=development`) could allow switching between simulated/mock and live clients.
6.  **Error Handling and Data Mapping:** Implement comprehensive error handling for live API calls (e.g., network issues, API errors, rate limits, unexpected response formats). Map the data from the live API responses to the structure expected by the `risk_engine.py`.
7.  **Testing:** Thoroughly test the integration with live APIs, potentially using a staging or sandbox environment provided by the API vendor.
