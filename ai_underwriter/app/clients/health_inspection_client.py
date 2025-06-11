import logging
from typing import Optional, Dict, Any, List # Added List
import json # Added
import os # Added

# --- Existing MockHealthInspectionClient ---
class MockHealthInspectionClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__) # Consistent logger naming
        self.logger.info("MockHealthInspectionClient initialized.")
        if self.api_key:
            self.logger.info(f"API Key provided via MockHealthInspectionClient: {self.api_key[:4]}... (masked)")


    def get_inspection_data(self, address: str, business_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetches mock health inspection data based on business name and address.
        This is the older mock client.
        """
        self.logger.info(f"MockHealthInspectionClient: Fetching mock health inspection data for '{business_name}' at '{address}'...")

        business_name_lower = business_name.lower()

        if business_name_lower == "the risky diner":
            self.logger.info(f"MockHealthInspectionClient: Found specific mock data for '{business_name}'.")
            return {
                "latest_score": 65,
                "last_inspection_date": "2023-01-10",
                "critical_violations_last_year": 5, # This matches historical_summary in new data
                "non_critical_violations_last_year": 10,
                "summary_url": "http://example.com/inspections/risky_diner",
                "source": "mock_health_department_api_v1" # Differentiate source
            }
        elif business_name_lower == "super clean eats":
            self.logger.info(f"MockHealthInspectionClient: Found specific mock data for '{business_name}'.")
            return {
                "latest_score": 98,
                "last_inspection_date": "2023-11-20",
                "critical_violations_last_year": 0, # This matches historical_summary
                "non_critical_violations_last_year": 1,
                "summary_url": "http://example.com/inspections/super_clean_eats",
                "source": "mock_health_department_api_v1"
            }
        else:
            self.logger.info(f"MockHealthInspectionClient: No specific mock data for '{business_name}', returning generic profile.")
            return {
                "latest_score": 85,
                "last_inspection_date": "2023-06-01",
                "critical_violations_last_year": 1, # This matches historical_summary for Average Joe's
                "non_critical_violations_last_year": 3,
                "summary_url": "http://example.com/inspections/generic",
                "source": "mock_health_department_api_v1"
            }

# --- New SimulatedHealthInspectionClient ---
class SimulatedHealthInspectionClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None,
                 data_file_path: str = "ai_underwriter/app/clients/data/simulated_health_data.json"):
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url if base_url else "http://simulated-health-api.local" # Default if not provided
        self.api_key = api_key if api_key else "SIM_DEFAULT_KEY" # Default if not provided

        # Adjust path if necessary, assuming script is run from project root /app
        # If run_tests.py adds /app to sys.path, then this relative path from /app should work.
        # For robustness, construct path relative to this file's directory.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file_path = os.path.join(current_dir, "data", os.path.basename(data_file_path))

        self.simulated_data: List[Dict[str, Any]] = []
        self._load_data()
        self.logger.info(f"SimulatedHealthInspectionClient initialized. Base URL: {self.base_url}, Data File: {self.data_file_path}")
        if self.api_key:
             self.logger.info(f"API Key provided via SimulatedHealthInspectionClient: {self.api_key[:4]}... (masked for default or real key)")


    def _load_data(self) -> None:
        try:
            # Ensure path is correct when running from tests or main app
            # If run_tests.py is in /app, and it sets CWD or adds to path correctly,
            # 'ai_underwriter/app/clients/data/simulated_health_data.json' might work directly
            # but making it relative to this file is safer.
            if not os.path.exists(self.data_file_path):
                self.logger.error(f"Simulated data file not found at {self.data_file_path}. Trying alternative common path from project root.")
                # This alternative path assumes the CWD is the project root '/app'
                alt_path = "ai_underwriter/app/clients/data/simulated_health_data.json"
                if os.path.exists(alt_path):
                    self.data_file_path = alt_path
                else:
                    raise FileNotFoundError(f"Could not find data file at {self.data_file_path} or {alt_path}")

            with open(self.data_file_path, 'r') as f:
                self.simulated_data = json.load(f)
            self.logger.info(f"Successfully loaded {len(self.simulated_data)} records from {self.data_file_path}")
        except FileNotFoundError:
            self.logger.error(f"Simulated health data file not found at {self.data_file_path}.")
            self.simulated_data = []
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON from {self.data_file_path}: {e}")
            self.simulated_data = []
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during data loading: {e}", exc_info=True)
            self.simulated_data = []

    def _find_establishment_data(self, business_name: str, address: str) -> Optional[Dict[str, Any]]:
        business_name_lower = business_name.lower()
        address_lower = address.lower()

        for record in self.simulated_data:
            if record.get('business_name', '').lower() == business_name_lower:
                self.logger.debug(f"Found match by business name: {business_name}")
                return record
            # Check search keywords against the full address
            for kw in record.get('search_keywords', []):
                if kw.lower() in address_lower:
                    self.logger.debug(f"Found match by address keyword '{kw}' in '{address}' for {record.get('business_name')}")
                    return record
        self.logger.debug(f"No match found for {business_name} at {address}")
        return None

    def get_inspection_data(self, business_name: str, address: str, city: Optional[str]=None, state: Optional[str]=None, zip_code: Optional[str]=None) -> Optional[Dict[str, Any]]:
        # City, state, zip_code are not used by this simulated client but kept for interface consistency if needed later
        self.logger.info(f"SimulatedHealthInspectionClient: Fetching health data for '{business_name}' at '{address}' (City: {city}, State: {state}, Zip: {zip_code})...")

        if self.api_key == "INVALID_KEY_TEST":
            self.logger.warning("Simulated API key is invalid.")
            return {"error": "Invalid API Key", "source": "simulated_health_api_error"}

        if not self.simulated_data:
            self.logger.warning("No simulated data loaded. Cannot provide health inspection details.")
            return {"error": "Simulated data not loaded", "source": "simulated_health_api_internal_error"}

        establishment_data = self._find_establishment_data(business_name, address)

        if not establishment_data:
            self.logger.info(f"SimulatedHealthInspectionClient: No data found for establishment '{business_name}' in simulated dataset.")
            # To align with how risk engine handles missing data, return None or specific "not found" structure
            # For now, returning None to trigger the "missing data penalty" in risk engine.
            # Or, return a dict that indicates "not found" clearly:
            return {
                "error": "Establishment not found",
                "latest_score": None, # Important for risk engine checks
                "critical_violations_last_year": None, # Important for risk engine checks
                "source": "simulated_health_api_not_found"
            }
            # return None # This would also work if risk engine handles None from client

        last_insp = establishment_data.get("last_inspection", {})
        violations = last_insp.get("violations", [])

        # Calculate critical violations from the *last inspection's* list of violations.
        # The JSON also has "historical_summary.critical_violations_last_12_months" which might be more appropriate.
        # Let's use the historical_summary if available, else count from last inspection.
        historical_summary = establishment_data.get("historical_summary", {})
        critical_violations_count = historical_summary.get("critical_violations_last_12_months")

        if critical_violations_count is None: # Fallback to counting from last inspection
            critical_violations_count = sum(1 for v in violations if v.get("severity") == "Critical")
            self.logger.info(f"Used fallback critical violation count from last inspection: {critical_violations_count}")
        else:
            self.logger.info(f"Used historical critical violation count: {critical_violations_count}")


        summary = {
            "latest_score": last_insp.get("score"),
            "last_inspection_date": last_insp.get("inspection_date"),
            "critical_violations_last_year": critical_violations_count,
            "grade": last_insp.get("grade"),
            "status": last_insp.get("status"),
            "all_violations_count_last_inspection": len(violations), # Example of additional derived data
            "source": "simulated_health_api_v2", # Differentiate source
            "establishment_id_debug": establishment_data.get("establishment_id") # For debugging
        }
        self.logger.info(f"SimulatedHealthInspectionClient: Returning data for '{business_name}': {summary}")
        return summary

# Example Usage (for SimulatedHealthInspectionClient)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG) # Use DEBUG to see more client logs

    # Test Mock Client (Original)
    print("\n--- Testing MockHealthInspectionClient (Original) ---")
    mock_client = MockHealthInspectionClient(api_key="mock_key_123")
    print("Fetching for 'The Risky Diner':")
    data_risky_mock = mock_client.get_inspection_data(address="123 Sinister St", business_name="The Risky Diner")
    print(data_risky_mock)
    print("Fetching for 'Average Joe's Eatery':") # Generic case for mock
    data_avg_mock = mock_client.get_inspection_data(address="789 Normal Rd", business_name="Average Joe's Eatery")
    print(data_avg_mock)

    # Test Simulated Client (New)
    print("\n--- Testing SimulatedHealthInspectionClient (New) ---")
    # The data_file_path will be relative to this file if run directly.
    # For testing, ensure 'data/simulated_health_data.json' is sibling to this file, or adjust path.
    # For app, path will be relative to where app is run or how clients module is found.
    # The __init__ tries to build a path relative to its own location.

    # To test relative pathing from this file:
    # Assuming this file is in app/clients/ and data is in app/clients/data/
    # current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # data_path = os.path.join(current_script_dir, "data", "simulated_health_data.json")
    # print(f"Looking for data file at: {data_path}")

    sim_client = SimulatedHealthInspectionClient(base_url="http://localhost:9999", api_key="sim_key_456")
                                                # data_file_path=data_path) # Use if needed

    if not sim_client.simulated_data:
        print("Simulated data not loaded, client tests will be limited.")

    print("\nFetching for 'The Risky Diner' (Simulated):")
    data_risky_sim = sim_client.get_inspection_data(business_name="The Risky Diner", address="101 Danger Path, Badtown, FS 54321")
    print(data_risky_sim)

    print("\nFetching for 'Super Clean Eats' by address keyword (Simulated):")
    data_clean_sim = sim_client.get_inspection_data(business_name="Something Else", address="202 Sparkle Ave")
    print(data_clean_sim)

    print("\nFetching for 'Average Joe's Diner' (Simulated):")
    data_avg_sim = sim_client.get_inspection_data(business_name="Average Joe's Diner", address="303 Normal St, Midburg, FS 67890")
    print(data_avg_sim)

    print("\nFetching for 'Non Existent Cafe' (Simulated):")
    data_non_existent_sim = sim_client.get_inspection_data(business_name="Non Existent Cafe", address="000 Nowhere Land")
    print(data_non_existent_sim)

    print("\nFetching with Invalid API Key (Simulated):")
    sim_client_invalid_key = SimulatedHealthInspectionClient(api_key="INVALID_KEY_TEST")
    data_invalid_key = sim_client_invalid_key.get_inspection_data(business_name="The Risky Diner", address="101 Danger Path")
    print(data_invalid_key)
