import json
import argparse
import sys
from typing import Dict, List, Union, Any, Optional, Set
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ValidationError:
    field: str
    message: str

class CreditCardValidator:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None
        self.errors = []

    def load_json(self) -> bool:
        """Load and parse the JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                self.data = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.errors.append(ValidationError("JSON", f"Invalid JSON format: {str(e)}"))
            return False
        except FileNotFoundError:
            self.errors.append(ValidationError("File", f"File not found: {self.file_path}"))
            return False
        except Exception as e:
            self.errors.append(ValidationError("File", f"Error reading file: {str(e)}"))
            return False

    def validate_card_section(self, card: Dict) -> None:
        """Validate the card section according to the Kotlin model."""
        required_fields = {
            "cardName": str,
            "cardIssuer": str,
            "networkType": str,
            "ratings": str,
            "categories": list,
            "targetAudience": str,
            "applyLink": str
        }
        
        for field, expected_type in required_fields.items():
            if field not in card:
                self.errors.append(ValidationError(f"card.{field}", "Field is missing"))
            elif not isinstance(card[field], expected_type):
                self.errors.append(ValidationError(f"card.{field}", f"Expected {expected_type.__name__}, got {type(card[field])}"))

    def validate_presentation_section(self, presentation: Dict) -> None:
        """Validate the presentation section."""
        required_fields = {
            "description": str,
            "highlightFeatures": list,
            "marketingTagline": str,
            "decoration": dict
        }
        
        for field, expected_type in required_fields.items():
            if field not in presentation:
                self.errors.append(ValidationError(f"presentation.{field}", "Field is missing"))
            elif not isinstance(presentation[field], expected_type):
                self.errors.append(ValidationError(f"presentation.{field}", f"Expected {expected_type.__name__}, got {type(presentation[field])}"))
        
        if "decoration" in presentation:
            decoration = presentation["decoration"]
            required_decoration_fields = {
                "primaryColor": int,
                "secondaryColor": int,
                "orientation": str,
                "cardImage": str,
                "material": str,
                "specialFeatures": list
            }
            
            for field, expected_type in required_decoration_fields.items():
                if field not in decoration:
                    self.errors.append(ValidationError(f"presentation.decoration.{field}", "Field is missing"))
                elif not isinstance(decoration[field], expected_type):
                    self.errors.append(ValidationError(f"presentation.decoration.{field}", f"Expected {expected_type.__name__}, got {type(decoration[field])}"))

    def validate_financials_section(self, financials: Dict) -> None:
        """Validate the financials section."""
        required_fields = {
            "fees": dict,
            "charges": list
        }
        
        for field, expected_type in required_fields.items():
            if field not in financials:
                self.errors.append(ValidationError(f"financials.{field}", "Field is missing"))
            elif not isinstance(financials[field], expected_type):
                self.errors.append(ValidationError(f"financials.{field}", f"Expected {expected_type.__name__}, got {type(financials[field])}"))
        
        if "fees" in financials:
            fees = financials["fees"]
            required_fee_types = ["joining", "renewal", "additionalCards"]
            for fee_type in required_fee_types:
                if fee_type not in fees:
                    self.errors.append(ValidationError(f"financials.fees.{fee_type}", "Fee type is missing"))
                else:
                    fee = fees[fee_type]
                    required_fee_fields = ["amount", "tax"]
                    if fee_type != "additionalCards":
                        required_fee_fields.append("waiverConditions")
                    for field in required_fee_fields:
                        if field not in fee:
                            self.errors.append(ValidationError(f"financials.fees.{fee_type}.{field}", "Field is missing"))
                        elif not isinstance(fee[field], (str if field != "waiverConditions" else list)):
                            self.errors.append(ValidationError(f"financials.fees.{fee_type}.{field}", f"Expected {'string' if field != 'waiverConditions' else 'list'}, got {type(fee[field])}"))

        if "charges" in financials:
            for i, charge in enumerate(financials["charges"]):
                required_fields = ["type", "value"]
                optional_fields = ["details"]
                
                for field in required_fields:
                    if field not in charge:
                        self.errors.append(ValidationError(f"financials.charges[{i}].{field}", "Field is missing"))
                    elif not isinstance(charge[field], str):
                        self.errors.append(ValidationError(f"financials.charges[{i}].{field}", f"Expected string, got {type(charge[field])}"))
                
                for field in optional_fields:
                    if field in charge and not isinstance(charge[field], str):
                        self.errors.append(ValidationError(f"financials.charges[{i}].{field}", f"Expected string or null, got {type(charge[field])}"))

    def validate_rewards_section(self, rewards: Dict) -> None:
        """Validate the rewards section."""
        required_fields = {
            "type": str,
            "structure": list,
            "caps": dict,
            "redemptionOptions": list,
            "excludedCategories": list
        }
        
        for field, expected_type in required_fields.items():
            if field not in rewards:
                self.errors.append(ValidationError(f"rewards.{field}", "Field is missing"))
            elif not isinstance(rewards[field], expected_type):
                self.errors.append(ValidationError(f"rewards.{field}", f"Expected {expected_type.__name__}, got {type(rewards[field])}"))
        
        if "structure" in rewards:
            for i, structure in enumerate(rewards["structure"]):
                required_fields = ["category", "rate", "details"]
                for field in required_fields:
                    if field not in structure:
                        self.errors.append(ValidationError(f"rewards.structure[{i}].{field}", "Field is missing"))
                    elif not isinstance(structure[field], str):
                        self.errors.append(ValidationError(f"rewards.structure[{i}].{field}", f"Expected string, got {type(structure[field])}"))

        if "caps" in rewards:
            caps = rewards["caps"]
            required_fields = ["overall"]
            for field in required_fields:
                if field not in caps:
                    self.errors.append(ValidationError(f"rewards.caps.{field}", "Field is missing"))
                elif not isinstance(caps[field], str):
                    self.errors.append(ValidationError(f"rewards.caps.{field}", f"Expected string, got {type(caps[field])}"))
            
            if "categorySpecific" in caps and not isinstance(caps["categorySpecific"], list):
                self.errors.append(ValidationError("rewards.caps.categorySpecific", f"Expected list, got {type(caps['categorySpecific'])}"))

        if "redemptionOptions" in rewards:
            for i, option in enumerate(rewards["redemptionOptions"]):
                required_fields = ["method", "description"]
                for field in required_fields:
                    if field not in option:
                        self.errors.append(ValidationError(f"rewards.redemptionOptions[{i}].{field}", "Field is missing"))
                    elif not isinstance(option[field], str):
                        self.errors.append(ValidationError(f"rewards.redemptionOptions[{i}].{field}", f"Expected string, got {type(option[field])}"))

    def validate_benefits_section(self, benefits: List) -> None:
        """Validate the benefits section."""
        if not isinstance(benefits, list):
            self.errors.append(ValidationError("benefits", f"Expected list, got {type(benefits)}"))
            return
        
        for i, benefit in enumerate(benefits):
            if not isinstance(benefit, dict):
                self.errors.append(ValidationError(f"benefits[{i}]", f"Expected dictionary, got {type(benefit)}"))
                continue
            
            required_fields = ["type", "details"]
            optional_fields = ["totalValue"]
            
            for field in required_fields:
                if field not in benefit:
                    self.errors.append(ValidationError(f"benefits[{i}].{field}", "Field is missing"))
                elif not isinstance(benefit[field], (str if field == "type" else list)):
                    self.errors.append(ValidationError(f"benefits[{i}].{field}", f"Expected {'string' if field == 'type' else 'list'}, got {type(benefit[field])}"))
            
            if "totalValue" in benefit and not isinstance(benefit["totalValue"], str):
                self.errors.append(ValidationError(f"benefits[{i}].totalValue", f"Expected string or null, got {type(benefit['totalValue'])}"))
            
            if "details" in benefit:
                for j, detail in enumerate(benefit["details"]):
                    required_fields = ["name", "value"]
                    optional_fields = ["condition"]
                    
                    for field in required_fields:
                        if field not in detail:
                            self.errors.append(ValidationError(f"benefits[{i}].details[{j}].{field}", "Field is missing"))
                        elif not isinstance(detail[field], str):
                            self.errors.append(ValidationError(f"benefits[{i}].details[{j}].{field}", f"Expected string, got {type(detail[field])}"))
                    
                    for field in optional_fields:
                        if field in detail and not isinstance(detail[field], str):
                            self.errors.append(ValidationError(f"benefits[{i}].details[{j}].{field}", f"Expected string or null, got {type(detail[field])}"))

    def validate_eligibility_section(self, eligibility: Dict) -> None:
        """Validate the eligibility section."""
        required_fields = {
            "ageRequirement": dict,
            "incomeRequirement": list,
            "creditScore": dict,
            "requiredDocuments": list,
            "residentialStatus": list,
            "otherCriteria": list
        }
        
        for field, expected_type in required_fields.items():
            if field not in eligibility:
                self.errors.append(ValidationError(f"eligibility.{field}", "Field is missing"))
            elif not isinstance(eligibility[field], expected_type):
                self.errors.append(ValidationError(f"eligibility.{field}", f"Expected {expected_type.__name__}, got {type(eligibility[field])}"))
        
        if "ageRequirement" in eligibility:
            age_req = eligibility["ageRequirement"]
            required_fields = ["minimum", "maximum"]
            for field in required_fields:
                if field not in age_req:
                    self.errors.append(ValidationError(f"eligibility.ageRequirement.{field}", "Field is missing"))
                elif not isinstance(age_req[field], int):
                    self.errors.append(ValidationError(f"eligibility.ageRequirement.{field}", f"Expected integer, got {type(age_req[field])}"))
        
        if "creditScore" in eligibility:
            credit_score = eligibility["creditScore"]
            required_fields = ["minimum", "recommended"]
            for field in required_fields:
                if field not in credit_score:
                    self.errors.append(ValidationError(f"eligibility.creditScore.{field}", "Field is missing"))
                elif not isinstance(credit_score[field], str):
                    self.errors.append(ValidationError(f"eligibility.creditScore.{field}", f"Expected string, got {type(credit_score[field])}"))

    def validate_application_process_section(self, process: Dict) -> None:
        """Validate the application process section."""
        required_fields = {
            "channels": list,
            "processingTime": str,
            "trackingMethod": str,
            "instantApproval": dict
        }
        
        for field, expected_type in required_fields.items():
            if field not in process:
                self.errors.append(ValidationError(f"applicationProcess.{field}", "Field is missing"))
            elif not isinstance(process[field], expected_type):
                self.errors.append(ValidationError(f"applicationProcess.{field}", f"Expected {expected_type.__name__}, got {type(process[field])}"))
        
        if "channels" in process:
            for i, channel in enumerate(process["channels"]):
                required_fields = ["type", "isAvailable"]
                optional_fields = ["details"]
                
                for field in required_fields:
                    if field not in channel:
                        self.errors.append(ValidationError(f"applicationProcess.channels[{i}].{field}", "Field is missing"))
                    elif not isinstance(channel[field], (str if field == "type" else bool)):
                        self.errors.append(ValidationError(f"applicationProcess.channels[{i}].{field}", f"Expected {'string' if field == 'type' else 'boolean'}, got {type(channel[field])}"))
                
                for field in optional_fields:
                    if field in channel and not isinstance(channel[field], str):
                        self.errors.append(ValidationError(f"applicationProcess.channels[{i}].{field}", f"Expected string or null, got {type(channel[field])}"))
        
        if "instantApproval" in process:
            instant_approval = process["instantApproval"]
            required_fields = ["isAvailable"]
            optional_fields = ["conditions"]
            
            for field in required_fields:
                if field not in instant_approval:
                    self.errors.append(ValidationError(f"applicationProcess.instantApproval.{field}", "Field is missing"))
                elif not isinstance(instant_approval[field], bool):
                    self.errors.append(ValidationError(f"applicationProcess.instantApproval.{field}", f"Expected boolean, got {type(instant_approval[field])}"))
            
            for field in optional_fields:
                if field in instant_approval and not isinstance(instant_approval[field], list):
                    self.errors.append(ValidationError(f"applicationProcess.instantApproval.{field}", f"Expected list or null, got {type(instant_approval[field])}"))

    def validate_customer_insights_section(self, insights: Dict) -> None:
        """Validate the customer insights section."""
        required_fields = {
            "recommendedFor": list,
            "notRecommendedFor": list
        }
        
        for field, expected_type in required_fields.items():
            if field not in insights:
                self.errors.append(ValidationError(f"customerInsights.{field}", "Field is missing"))
            elif not isinstance(insights[field], expected_type):
                self.errors.append(ValidationError(f"customerInsights.{field}", f"Expected {expected_type.__name__}, got {type(insights[field])}"))

    def validate(self) -> List[ValidationError]:
        """Validate the entire card data structure."""
        if not self.load_json():
            return self.errors
        
        required_sections = {
            "id": str,
            "card": dict,
            "presentation": dict,
            "financials": dict,
            "rewards": dict,
            "benefits": list,
            "eligibility": dict,
            "applicationProcess": dict,
            "customerInsights": dict
        }
        
        for field, expected_type in required_sections.items():
            if field not in self.data:
                self.errors.append(ValidationError(field, "Section is missing"))
            elif not isinstance(self.data[field], expected_type):
                self.errors.append(ValidationError(field, f"Expected {expected_type.__name__}, got {type(self.data[field])}"))
        
        if "card" in self.data:
            self.validate_card_section(self.data["card"])
        
        if "presentation" in self.data:
            self.validate_presentation_section(self.data["presentation"])
        
        if "financials" in self.data:
            self.validate_financials_section(self.data["financials"])
        
        if "rewards" in self.data:
            self.validate_rewards_section(self.data["rewards"])
        
        if "benefits" in self.data:
            self.validate_benefits_section(self.data["benefits"])
        
        if "eligibility" in self.data:
            self.validate_eligibility_section(self.data["eligibility"])
        
        if "applicationProcess" in self.data:
            self.validate_application_process_section(self.data["applicationProcess"])
        
        if "customerInsights" in self.data:
            self.validate_customer_insights_section(self.data["customerInsights"])
        
        return self.errors

def main():
    parser = argparse.ArgumentParser(description="Validate credit card JSON data")
    parser.add_argument("file", help="Path to the JSON file to validate")
    args = parser.parse_args()
    
    validator = CreditCardValidator(args.file)
    errors = validator.validate()
    
    if errors:
        print(f"\n{args.file} has validation errors:")
        for error in errors:
            print(f"  - {error.message}")
        sys.exit(1)
    else:
        print(f"✓ {args.file} is valid")

if __name__ == "__main__":
    main() 