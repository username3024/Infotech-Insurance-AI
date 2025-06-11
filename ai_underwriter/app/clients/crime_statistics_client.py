import logging
from typing import Optional, Dict, Any

class MockCrimeStatisticsClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__) # Use a logger specific to this module
        self.logger.info("MockCrimeStatisticsClient initialized.")
        if self.api_key:
            self.logger.info(f"API Key provided: {self.api_key[:4]}... (masked)")

    def get_crime_data(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Fetches mock crime statistics based on keywords in the address.
        """
        self.logger.info(f"Fetching mock crime statistics for address: {address}...")

        address_lower = address.lower() # For case-insensitive matching

        if "123 main st" in address_lower:
            self.logger.info(f"Found specific mock crime data for address containing '123 Main St'.")
            return {
                "crime_level_area": "Low",
                "theft_incidents_last_year_nearby": 2,
                "vandalism_incidents_last_year_nearby": 0,
                "assault_incidents_last_year_nearby": 1, # Added another metric for variety
                "safety_score": 8.5,  # Arbitrary score
                "source": "mock_crime_statistics_api"
            }
        elif "999 danger ave" in address_lower:
            self.logger.info(f"Found specific mock crime data for address containing '999 Danger Ave'.")
            return {
                "crime_level_area": "High",
                "theft_incidents_last_year_nearby": 25,
                "vandalism_incidents_last_year_nearby": 10,
                "assault_incidents_last_year_nearby": 7, # Added another metric
                "safety_score": 3.2,
                "source": "mock_crime_statistics_api"
            }
        else:
            self.logger.info(f"No specific mock crime data for address '{address}', returning generic profile.")
            return {
                "crime_level_area": "Medium",
                "theft_incidents_last_year_nearby": 7,
                "vandalism_incidents_last_year_nearby": 3,
                "assault_incidents_last_year_nearby": 2, # Added another metric
                "safety_score": 6.5,
                "source": "mock_crime_statistics_api"
            }

# Example Usage (not part of the module's direct functionality, but for testing)
if __name__ == '__main__':
    # Ensure basic logging is configured to see output from the client
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    client = MockCrimeStatisticsClient(api_key="testkey456")

    print("\nFetching for '123 Main St, Anytown':")
    data_low = client.get_crime_data(address="123 Main St, Anytown")
    print(data_low)

    print("\nFetching for 'Apartment 5B, 999 Danger Ave':")
    data_high = client.get_crime_data(address="Apartment 5B, 999 Danger Ave")
    print(data_high)

    print("\nFetching for '404 Safe Pl, Suburbia':")
    data_medium = client.get_crime_data(address="404 Safe Pl, Suburbia")
    print(data_medium)
