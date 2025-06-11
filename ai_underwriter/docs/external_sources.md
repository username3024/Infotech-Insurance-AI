# External Data Sources and Mocking

The AI Underwriter system is designed to integrate with external data sources to enhance its risk assessment capabilities. In the current version (Phase 2 MVP), these external integrations are implemented using **mock clients**.

## Mock Client Behavior

The mock clients simulate interactions with real external APIs and return predefined data. This allows for development and testing without requiring live API keys or access. The data returned by these mocks directly influences the risk score calculated by the `risk_engine.py`.

### 1. Health Inspection Data (`MockHealthInspectionClient`)

*   **Location:** `ai_underwriter/app/clients/health_inspection_client.py`
*   **Trigger:** Called when an application is submitted via the `POST /applications/submit` endpoint. The client uses the `business_name` and `address` from the application to determine which mock data to return.
*   **Behavior:**
    *   If `business_name` (case-insensitive) is **"The Risky Diner"**:
        *   Returns a profile indicating poor health standards:
            *   `latest_score`: 65
            *   `critical_violations_last_year`: 5
            *   (Other related fields like `last_inspection_date`, `non_critical_violations_last_year`, `summary_url`, `source`)
    *   If `business_name` (case-insensitive) is **"Super Clean Eats"**:
        *   Returns a profile indicating excellent health standards:
            *   `latest_score`: 98
            *   `critical_violations_last_year`: 0
            *   (Other related fields)
    *   For **other business names**:
        *   Returns a generic "average" health profile:
            *   `latest_score`: 85
            *   `critical_violations_last_year`: 1
            *   (Other related fields)
*   **Impact on Risk Score:** The `risk_engine.py` adjusts the score based on `latest_score` and `critical_violations_last_year`. Lower scores and higher violations increase the risk score. A penalty is applied if health data is missing.

### 2. Crime Statistics Data (`MockCrimeStatisticsClient`)

*   **Location:** `ai_underwriter/app/clients/crime_statistics_client.py`
*   **Trigger:** Called when an application is submitted via the `POST /applications/submit` endpoint. The client uses the `address` from the application.
*   **Behavior:**
    *   If `address` (case-insensitive) contains **"123 Main St"**:
        *   Returns a "Low" crime profile including:
            *   `crime_level_area`: "Low"
            *   `safety_score`: 8.5
            *   (Low incident counts for theft, vandalism, assault)
    *   If `address` (case-insensitive) contains **"999 Danger Ave"**:
        *   Returns a "High" crime profile including:
            *   `crime_level_area`: "High"
            *   `safety_score`: 3.2
            *   (High incident counts)
    *   For **other addresses**:
        *   Returns a "Medium" crime profile including:
            *   `crime_level_area`: "Medium"
            *   `safety_score`: 6.5
            *   (Moderate incident counts)
*   **Impact on Risk Score:** The `risk_engine.py` adjusts the score based on `crime_level_area` and `safety_score`. "High" or "Medium" crime levels, and lower safety scores, increase the risk score. A penalty is applied if crime data is missing.

## Future Integration

To connect to live external services, the following steps would typically be involved:

1.  **Identify and Subscribe to Services:** Choose real-world providers for health inspection and crime statistics data.
2.  **Develop New Client Classes:** Create new Python classes in `ai_underwriter/app/clients/` that implement the communication logic (e.g., HTTP requests, authentication, data parsing) for the chosen live APIs. These clients should ideally conform to a similar interface as the mock clients (e.g., a `get_inspection_data` method that returns a dictionary).
3.  **Obtain API Keys:** Securely acquire and store API keys and any other necessary credentials for the live services.
4.  **Configuration Management:** Implement a robust way to manage these API keys, typically using environment variables (e.g., `HEALTH_API_KEY`, `CRIME_API_KEY`) or a configuration file that is not committed to version control.
5.  **Update Client Instantiation:** Modify `ai_underwriter/app/api/application_api.py` to instantiate these new live client classes, passing the configured API keys. Conditional instantiation (e.g., based on an environment setting like `APP_ENV=production` vs. `APP_ENV=development`) could allow switching between mock and live clients.
6.  **Error Handling and Data Mapping:** Implement comprehensive error handling for live API calls (e.g., network issues, API errors, unexpected response formats). Map the data from the live API responses to the structure expected by the `risk_engine.py` (e.g., the fields in `health_inspection_summary` and `crime_statistics_summary`).
7.  **Testing:** Thoroughly test the integration with live APIs, potentially using a staging or sandbox environment provided by the API vendor.
