import json
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import os

class CardNetworkType(Enum):
    VISA = "Visa"
    VISA_INFINITE = "Visa Infinite"
    MASTERCARD = "Mastercard"
    MASTERCARD_WORLD = "Mastercard World"
    RUPAY = "RuPay"
    AMEX = "American Express"
    VISA_MASTERCARD = "Visa/Mastercard"
    VISA_RUPAY = "Visa/RuPay"
    RUPAY_MASTERCARD = "RuPay/Mastercard"

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
    annualizedValue: Optional[str] = None
    condition: Optional[str] = None

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

class CreditCardValidator:
    def __init__(self, json_data: Dict[str, Any]):
        self.data = json_data
        self.errors = []

    def validate_basic_structure(self) -> bool:
        required_fields = ["id", "card", "presentation", "financials", "rewards", 
                         "eligibility", "applicationProcess", 
                         "customerInsights"]
        
        for field in required_fields:
            if field not in self.data:
                self.errors.append(f"Missing required field: {field}")
                return False
        return True

    def validate_card_info(self) -> bool:
        card = self.data["card"]
        required_fields = ["cardName", "cardIssuer", "ratings", "categories", 
                         "networkType", "cardNetwork", "targetAudience", "applyLink"]
        
        for field in required_fields:
            if field not in card:
                self.errors.append(f"Missing required field in card: {field}")
                return False

        # Validate networkType
        if card["networkType"] not in [t.value for t in CardNetworkType]:
            self.errors.append(f"Invalid network type: {card['networkType']}")
            return False

        # Validate cardNetwork
        if not isinstance(card["cardNetwork"], list):
            self.errors.append("cardNetwork must be a list")
            return False

        valid_networks = ["Visa", "Mastercard", "RuPay", "American Express"]
        for network in card["cardNetwork"]:
            if network not in valid_networks:
                self.errors.append(f"Invalid card network: {network}")
                return False

        # Validate networkType matches cardNetwork
        network_type = card["networkType"]
        networks = card["cardNetwork"]
        
        if "/" in network_type:
            # For combined network types
            expected_networks = network_type.split("/")
            if not all(network in networks for network in expected_networks):
                self.errors.append(f"networkType '{network_type}' does not match cardNetwork {networks}")
                return False
        else:
            # For single network types
            if network_type not in networks:
                self.errors.append(f"networkType '{network_type}' does not match cardNetwork {networks}")
                return False

        return True

    def validate_presentation(self) -> bool:
        presentation = self.data["presentation"]
        required_fields = ["decoration", "description", "highlightFeatures", "marketingTagline"]
        
        for field in required_fields:
            if field not in presentation:
                self.errors.append(f"Missing required field in presentation: {field}")
                return False

        # Validate description for co-branded cards
        description = presentation["description"].lower()
        card_name = self.data["card"]["cardName"].lower()
        
        # Check if card is co-branded by looking for multiple issuers in card name
        if " and " in card_name or "&" in card_name:
            if "co-branded" not in description:
                self.errors.append("Description should mention co-branding for co-branded cards")
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
        if "benefits" not in self.data:
            return True  # Benefits are optional

        benefits = self.data["benefits"]
        if not isinstance(benefits, list):
            self.errors.append("Benefits must be a list")
            return False

        for benefit in benefits:
            if not isinstance(benefit, dict):
                self.errors.append("Each benefit must be an object")
                return False

            if "type" not in benefit or "details" not in benefit or "totalValue" not in benefit:
                self.errors.append("Invalid benefit structure")
                return False

            if not isinstance(benefit["details"], list):
                self.errors.append("Benefit details must be a list")
                return False

            for detail in benefit["details"]:
                if not isinstance(detail, dict):
                    self.errors.append("Each benefit detail must be an object")
                    return False

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
        if "customerSupport" not in self.data:
            return True  # Customer support is optional

        support = self.data["customerSupport"]
        required_fields = ["channels", "dedicatedSupport"]
        
        for field in required_fields:
            if field not in support:
                self.errors.append(f"Missing required field in customer support: {field}")
                return False

        return True

    def validate_change_log(self) -> bool:
        if "changeLog" not in self.data:
            return True  # Change log is optional

        change_log = self.data["changeLog"]
        if not isinstance(change_log, list):
            self.errors.append("Change log must be a list")
            return False

        for entry in change_log:
            if not isinstance(entry, dict):
                self.errors.append("Each change log entry must be an object")
                return False

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

def validate_file(file_path: str) -> tuple[bool, List[str]]:
    try:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        return False, [f"Error: File {file_path} not found"]
    except json.JSONDecodeError:
        return False, [f"Error: {file_path} is not a valid JSON file"]

    validator = CreditCardValidator(json_data)
    is_valid = validator.validate()
    return is_valid, validator.errors

def main():
    parser = argparse.ArgumentParser(description='Validate credit card JSON data')
    parser.add_argument('json_file', help='Path to the JSON file to validate')
    args = parser.parse_args()

    is_valid, errors = validate_file(args.json_file)
    if is_valid:
        print(f"Validation successful! The JSON data in {args.json_file} is valid.")
        return 0
    else:
        print(f"Validation failed for {args.json_file}. The following errors were found:")
        for error in errors:
            print(f"- {error}")
        return 1

if __name__ == "__main__":
    exit(main()) 