from typing import List, Dict

class RestaurantApplication:
    def __init__(self,
                 application_id: str,
                 business_name: str,
                 address: str,
                 cuisine_type: str,
                 alcohol_sales_percentage: float,
                 operating_hours: str,
                 square_footage: int,
                 building_age: int,
                 fire_suppression_system_type: str,
                 years_in_business: int,
                 management_experience_years: int,
                 has_delivery_operations: bool,
                 has_catering_operations: bool,
                 seating_capacity: int,
                 annual_revenue: float,
                 health_inspection_score: float,
                 previous_claims_count: int):
        self.application_id: str = application_id
        self.business_name: str = business_name
        self.address: str = address
        self.cuisine_type: str = cuisine_type
        self.alcohol_sales_percentage: float = alcohol_sales_percentage
        self.operating_hours: str = operating_hours
        self.square_footage: int = square_footage
        self.building_age: int = building_age
        self.fire_suppression_system_type: str = fire_suppression_system_type
        self.years_in_business: int = years_in_business
        self.management_experience_years: int = management_experience_years
        self.has_delivery_operations: bool = has_delivery_operations
        self.has_catering_operations: bool = has_catering_operations
        self.seating_capacity: int = seating_capacity
        self.annual_revenue: float = annual_revenue
        self.health_inspection_score: float = health_inspection_score
        self.previous_claims_count: int = previous_claims_count

    def to_dict(self) -> Dict:
        return self.__dict__

class RiskAssessmentOutput:
    def __init__(self,
                 application_id: str,
                 risk_score: float,
                 confidence_level: float,
                 decision: str,
                 recommended_premium: float,
                 premium_breakdown: Dict[str, float],
                 risk_mitigation_recommendations: List[str],
                 required_documentation: List[str],
                 explanation_factors: List[str]):
        self.application_id: str = application_id
        self.risk_score: float = risk_score
        self.confidence_level: float = confidence_level
        self.decision: str = decision
        self.recommended_premium: float = recommended_premium
        self.premium_breakdown: Dict[str, float] = premium_breakdown
        self.risk_mitigation_recommendations: List[str] = risk_mitigation_recommendations
        self.required_documentation: List[str] = required_documentation
        self.explanation_factors: List[str] = explanation_factors

    def to_dict(self) -> Dict:
        return self.__dict__
