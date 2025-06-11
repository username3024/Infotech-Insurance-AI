import logging
from typing import Optional, Dict, Any

class MockHealthInspectionClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        # It's good practice to get a logger specific to the module
        # rather than using logging.info directly if this were a larger app.
        # For now, direct logging.info is fine as per instruction.
        logging.info("MockHealthInspectionClient initialized.")
        if self.api_key:
            logging.info(f"API Key provided: {self.api_key[:4]}... (masked)")


    def get_inspection_data(self, address: str, business_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetches mock health inspection data based on business name and address.
        """
        logger = logging.getLogger(__name__) # Get a module-specific logger
        logger.info(f"Fetching mock health inspection data for '{business_name}' at '{address}'...")

        business_name_lower = business_name.lower()

        if business_name_lower == "the risky diner":
            logger.info(f"Found specific mock data for '{business_name}'.")
            return {
                "latest_score": 65,
                "last_inspection_date": "2023-01-10",
                "critical_violations_last_year": 5,
                "non_critical_violations_last_year": 10,
                "summary_url": "http://example.com/inspections/risky_diner",
                "source": "mock_health_department_api"
            }
        elif business_name_lower == "super clean eats":
            logger.info(f"Found specific mock data for '{business_name}'.")
            return {
                "latest_score": 98,
                "last_inspection_date": "2023-11-20",
                "critical_violations_last_year": 0,
                "non_critical_violations_last_year": 1,
                "summary_url": "http://example.com/inspections/super_clean_eats",
                "source": "mock_health_department_api"
            }
        else:
            logger.info(f"No specific mock data for '{business_name}', returning generic profile.")
            return {
                "latest_score": 85, # Generic average score
                "last_inspection_date": "2023-06-01", # Generic date
                "critical_violations_last_year": 1, # Generic low critical violations
                "non_critical_violations_last_year": 3, # Generic few non-critical
                "summary_url": "http://example.com/inspections/generic",
                "source": "mock_health_department_api"
            }

# Example Usage (not part of the module's direct functionality, but for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    client = MockHealthInspectionClient(api_key="testkey123")

    print("\nFetching for 'The Risky Diner':")
    data_risky = client.get_inspection_data(address="123 Sinister St", business_name="The Risky Diner")
    print(data_risky)

    print("\nFetching for 'Super Clean Eats':")
    data_clean = client.get_inspection_data(address="456 Pristine Ave", business_name="Super Clean Eats")
    print(data_clean)

    print("\nFetching for 'Average Joe's Eatery':")
    data_avg = client.get_inspection_data(address="789 Normal Rd", business_name="Average Joe's Eatery")
    print(data_avg)
