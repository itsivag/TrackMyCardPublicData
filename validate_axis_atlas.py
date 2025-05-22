import json
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class CardNetworkType(Enum):
    VISA = "Visa"
    MASTERCARD = "Mastercard"
    RUPAY = "RuPay"
    AMEX = "American Express"

@dataclass
class CardFees:
    amount: str
    tax: str
    waiverConditions: List[str]

@dataclass
class CardCharge:
    type: str
    value: str
    details: str

@dataclass
class RewardStructure:
    category: str
    rate: str
    details: str

@dataclass
class RewardCap:
    category: str
    cap: str

@dataclass
class RedemptionOption:
    method: str
    description: str

@dataclass
class BenefitDetail:
    name: str
    value: str
    condition: str

@dataclass
class Benefit:
    type: str
    details: List[BenefitDetail]
    totalValue: str

@dataclass
class IncomeRequirement:
    employmentType: str
    minimumIncome: str
    preferredIncomeLevel: str

@dataclass
class DocumentRequirement:
    type: str
    options: List[str]

@dataclass
class ApplicationChannel:
    type: str
    isAvailable: bool
    url: Optional[str] = None
    details: Optional[str] = None

@dataclass
class SupportChannel:
    type: str
    value: str
    availability: Optional[str] = None
    responseTime: Optional[str] = None
    isAvailable: Optional[bool] = None

@dataclass
class ChangeLog:
    date: str
    type: str
    change: str

class AxisAtlasValidator:
    def __init__(self, json_data: Dict[str, Any]):
        self.data = json_data
        self.errors = []

    def validate_basic_structure(self) -> bool:
        required_fields = ["id", "card", "presentation", "financials", "rewards", 
                         "benefits", "eligibility", "applicationProcess", 
                         "customerInsights", "customerSupport", "changeLog"]
        
        for field in required_fields:
            if field not in self.data:
                self.errors.append(f"Missing required field: {field}")
                return False
        return True

    def validate_card_info(self) -> bool:
        card = self.data["card"]
        required_fields = ["cardName", "cardIssuer", "ratings", "categories", 
                         "networkType", "targetAudience", "applyLink"]
        
        for field in required_fields:
            if field not in card:
                self.errors.append(f"Missing required field in card: {field}")
                return False

        if card["networkType"] not in [t.value for t in CardNetworkType]:
            self.errors.append(f"Invalid network type: {card['networkType']}")
            return False

        return True

    def validate_presentation(self) -> bool:
        presentation = self.data["presentation"]
        required_fields = ["decoration", "description", "highlightFeatures", "marketingTagline"]
        
        for field in required_fields:
            if field not in presentation:
                self.errors.append(f"Missing required field in presentation: {field}")
                return False

        decoration = presentation["decoration"]
        required_decoration_fields = ["primaryColor", "secondaryColor", "orientation", 
                                    "cardImage", "material", "specialFeatures"]
        
        for field in required_decoration_fields:
            if field not in decoration:
                self.errors.append(f"Missing required field in decoration: {field}")
                return False

        return True

    def validate_financials(self) -> bool:
        financials = self.data["financials"]
        required_fields = ["fees", "charges"]
        
        for field in required_fields:
            if field not in financials:
                self.errors.append(f"Missing required field in financials: {field}")
                return False

        fees = financials["fees"]
        required_fee_types = ["joining", "renewal", "additionalCards"]
        
        for fee_type in required_fee_types:
            if fee_type not in fees:
                self.errors.append(f"Missing required fee type: {fee_type}")
                return False

        return True

    def validate_rewards(self) -> bool:
        rewards = self.data["rewards"]
        required_fields = ["type", "structure", "caps", "redemptionOptions", "excludedCategories"]
        
        for field in required_fields:
            if field not in rewards:
                self.errors.append(f"Missing required field in rewards: {field}")
                return False

        return True

    def validate_benefits(self) -> bool:
        benefits = self.data["benefits"]
        required_benefit_types = ["Welcome", "Travel", "Dining", "Milestone"]
        
        for benefit in benefits:
            if "type" not in benefit or "details" not in benefit or "totalValue" not in benefit:
                self.errors.append("Invalid benefit structure")
                return False

            for detail in benefit["details"]:
                if "name" not in detail or "value" not in detail or "condition" not in detail:
                    self.errors.append("Invalid benefit detail structure")
                    return False

        return True

    def validate_eligibility(self) -> bool:
        eligibility = self.data["eligibility"]
        required_fields = ["ageRequirement", "incomeRequirement", "creditScore", 
                         "requiredDocuments", "residentialStatus"]
        
        for field in required_fields:
            if field not in eligibility:
                self.errors.append(f"Missing required field in eligibility: {field}")
                return False

        return True

    def validate_application_process(self) -> bool:
        process = self.data["applicationProcess"]
        required_fields = ["channels", "processingTime", "trackingMethod", "instantApproval"]
        
        for field in required_fields:
            if field not in process:
                self.errors.append(f"Missing required field in application process: {field}")
                return False

        return True

    def validate_customer_insights(self) -> bool:
        insights = self.data["customerInsights"]
        required_fields = ["recommendedFor", "notRecommendedFor"]
        
        for field in required_fields:
            if field not in insights:
                self.errors.append(f"Missing required field in customer insights: {field}")
                return False

        return True

    def validate_customer_support(self) -> bool:
        support = self.data["customerSupport"]
        required_fields = ["channels", "dedicatedSupport"]
        
        for field in required_fields:
            if field not in support:
                self.errors.append(f"Missing required field in customer support: {field}")
                return False

        return True

    def validate_change_log(self) -> bool:
        change_log = self.data["changeLog"]
        for entry in change_log:
            if "date" not in entry or "type" not in entry or "change" not in entry:
                self.errors.append("Invalid change log entry structure")
                return False

        return True

    def validate(self) -> bool:
        validation_methods = [
            self.validate_basic_structure,
            self.validate_card_info,
            self.validate_presentation,
            self.validate_financials,
            self.validate_rewards,
            self.validate_benefits,
            self.validate_eligibility,
            self.validate_application_process,
            self.validate_customer_insights,
            self.validate_customer_support,
            self.validate_change_log
        ]

        return all(method() for method in validation_methods)

def main():
    parser = argparse.ArgumentParser(description='Validate Axis Bank Atlas credit card JSON data')
    parser.add_argument('json_file', help='Path to the JSON file to validate')
    args = parser.parse_args()

    try:
        with open(args.json_file, 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {args.json_file} not found")
        return 1
    except json.JSONDecodeError:
        print(f"Error: {args.json_file} is not a valid JSON file")
        return 1

    validator = AxisAtlasValidator(json_data)
    if validator.validate():
        print("Validation successful! The JSON data is valid.")
        return 0
    else:
        print("Validation failed. The following errors were found:")
        for error in validator.errors:
            print(f"- {error}")
        return 1

if __name__ == "__main__":
    exit(main()) 