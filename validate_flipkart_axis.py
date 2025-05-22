import json
import argparse
import sys
from typing import Dict, List, Union, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
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

    def validate_string(self, value: Any, field_name: str) -> None:
        if not isinstance(value, str):
            self.errors.append(ValidationError(field_name, f"Expected string, got {type(value)}"))

    def validate_int(self, value: Any, field_name: str) -> None:
        if not isinstance(value, int):
            self.errors.append(ValidationError(field_name, f"Expected integer, got {type(value)}"))

    def validate_boolean(self, value: Any, field_name: str) -> None:
        if not isinstance(value, bool):
            self.errors.append(ValidationError(field_name, f"Expected boolean, got {type(value)}"))

    def validate_list(self, value: Any, field_name: str) -> None:
        if not isinstance(value, list):
            self.errors.append(ValidationError(field_name, f"Expected list, got {type(value)}"))

    def validate_dict(self, value: Any, field_name: str) -> None:
        if not isinstance(value, dict):
            self.errors.append(ValidationError(field_name, f"Expected dictionary, got {type(value)}"))

    def validate_optional_string(self, value: Any, field_name: str) -> None:
        if value is not None and not isinstance(value, str):
            self.errors.append(ValidationError(field_name, f"Expected string or null, got {type(value)}"))

    def validate_optional_boolean(self, value: Any, field_name: str) -> None:
        if value is not None and not isinstance(value, bool):
            self.errors.append(ValidationError(field_name, f"Expected boolean or null, got {type(value)}"))

    def validate_card_section(self, card: Dict) -> None:
        required_fields = {
            "cardName": str,
            "cardIssuer": str,
            "ratings": str,
            "categories": list,
            "networkType": str,
            "targetAudience": str,
            "applyLink": str
        }
        
        for field, expected_type in required_fields.items():
            if field not in card:
                self.errors.append(ValidationError(f"card.{field}", "Field is missing"))
            elif not isinstance(card[field], expected_type):
                self.errors.append(ValidationError(f"card.{field}", f"Expected {expected_type.__name__}, got {type(card[field])}"))

    def validate_presentation_section(self, presentation: Dict) -> None:
        required_fields = {
            "decoration": dict,
            "description": str,
            "highlightFeatures": list,
            "marketingTagline": str
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
                    if fee_type == "additionalCards":
                        required_fee_fields = ["amount", "tax"]
                    else:
                        required_fee_fields = ["amount", "tax", "waiverConditions"]
                    for field in required_fee_fields:
                        if field not in fee:
                            self.errors.append(ValidationError(f"financials.fees.{fee_type}.{field}", "Field is missing"))
                        elif not isinstance(fee[field], (str if field != "waiverConditions" else list)):
                            self.errors.append(ValidationError(f"financials.fees.{fee_type}.{field}", f"Expected {'string' if field != 'waiverConditions' else 'list'}, got {type(fee[field])}"))

        if "charges" in financials:
            for i, charge in enumerate(financials["charges"]):
                required_fields = ["type", "value"]
                optional_fields = ["annualizedValue", "condition", "details"]
                
                for field in required_fields:
                    if field not in charge:
                        self.errors.append(ValidationError(f"financials.charges[{i}].{field}", "Field is missing"))
                    elif not isinstance(charge[field], str):
                        self.errors.append(ValidationError(f"financials.charges[{i}].{field}", f"Expected string, got {type(charge[field])}"))
                
                for field in optional_fields:
                    if field in charge and not isinstance(charge[field], str):
                        self.errors.append(ValidationError(f"financials.charges[{i}].{field}", f"Expected string or null, got {type(charge[field])}"))

    def check_unknown_fields(self, data: Dict, allowed_fields: Set[str], path: str) -> None:
        """Check for unknown fields in the data."""
        for field in data.keys():
            if field not in allowed_fields:
                self.errors.append(ValidationError(f"{path}.{field}", f"Unknown field not defined in data model"))

    def validate_rewards_structure(self, structure: Dict, path: str) -> None:
        """Validate a single reward structure entry."""
        allowed_fields = {"category", "rate", "details", "partners"}
        self.check_unknown_fields(structure, allowed_fields, path)
        
        required_fields = ["category", "rate", "details"]
        for field in required_fields:
            if field not in structure:
                self.errors.append(ValidationError(f"{path}.{field}", "Field is missing"))
            elif not isinstance(structure[field], str):
                self.errors.append(ValidationError(f"{path}.{field}", f"Expected string, got {type(structure[field])}"))
        
        if "partners" in structure and not isinstance(structure["partners"], list):
            self.errors.append(ValidationError(f"{path}.partners", f"Expected list or null, got {type(structure['partners'])}"))

    def validate_rewards_section(self, rewards: Dict) -> None:
        allowed_fields = {"type", "structure", "caps", "redemptionOptions", "excludedCategories"}
        self.check_unknown_fields(rewards, allowed_fields, "rewards")
        
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
                self.validate_rewards_structure(structure, f"rewards.structure[{i}]")

        if "caps" in rewards:
            caps = rewards["caps"]
            allowed_fields = {"overall", "categorySpecific"}
            self.check_unknown_fields(caps, allowed_fields, "rewards.caps")
            
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
                allowed_fields = {"method", "description"}
                self.check_unknown_fields(option, allowed_fields, f"rewards.redemptionOptions[{i}]")
                
                required_fields = ["method", "description"]
                for field in required_fields:
                    if field not in option:
                        self.errors.append(ValidationError(f"rewards.redemptionOptions[{i}].{field}", "Field is missing"))
                    elif not isinstance(option[field], str):
                        self.errors.append(ValidationError(f"rewards.redemptionOptions[{i}].{field}", f"Expected string, got {type(option[field])}"))

    def validate_benefits_section(self, benefits: List) -> None:
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
                    required_fields = ["name", "value", "condition"]
                    optional_fields = ["expiryPeriod", "locations", "programLink"]
                    
                    for field in required_fields:
                        if field not in detail:
                            self.errors.append(ValidationError(f"benefits[{i}].details[{j}].{field}", "Field is missing"))
                        elif not isinstance(detail[field], str):
                            self.errors.append(ValidationError(f"benefits[{i}].details[{j}].{field}", f"Expected string, got {type(detail[field])}"))
                    
                    for field in optional_fields:
                        if field in detail and not isinstance(detail[field], str):
                            self.errors.append(ValidationError(f"benefits[{i}].details[{j}].{field}", f"Expected string or null, got {type(detail[field])}"))

    def validate_eligibility_section(self, eligibility: Dict) -> None:
        required_fields = {
            "ageRequirement": dict,
            "incomeRequirement": list,
            "creditScore": dict,
            "requiredDocuments": list,
            "residentialStatus": list
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
        
        if "incomeRequirement" in eligibility:
            for i, req in enumerate(eligibility["incomeRequirement"]):
                required_fields = ["employmentType", "minimumIncome", "preferredIncomeLevel"]
                for field in required_fields:
                    if field not in req:
                        self.errors.append(ValidationError(f"eligibility.incomeRequirement[{i}].{field}", "Field is missing"))
                    elif not isinstance(req[field], str):
                        self.errors.append(ValidationError(f"eligibility.incomeRequirement[{i}].{field}", f"Expected string, got {type(req[field])}"))
        
        if "creditScore" in eligibility:
            credit_score = eligibility["creditScore"]
            required_fields = ["minimum", "recommended"]
            for field in required_fields:
                if field not in credit_score:
                    self.errors.append(ValidationError(f"eligibility.creditScore.{field}", "Field is missing"))
                elif not isinstance(credit_score[field], str):
                    self.errors.append(ValidationError(f"eligibility.creditScore.{field}", f"Expected string, got {type(credit_score[field])}"))
        
        if "requiredDocuments" in eligibility:
            for i, doc in enumerate(eligibility["requiredDocuments"]):
                required_fields = ["type", "options"]
                for field in required_fields:
                    if field not in doc:
                        self.errors.append(ValidationError(f"eligibility.requiredDocuments[{i}].{field}", "Field is missing"))
                    elif not isinstance(doc[field], (str if field == "type" else list)):
                        self.errors.append(ValidationError(f"eligibility.requiredDocuments[{i}].{field}", f"Expected {'string' if field == 'type' else 'list'}, got {type(doc[field])}"))

    def validate_application_process(self, process: Dict) -> None:
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
                optional_fields = ["url", "details"]
                
                for field in required_fields:
                    if field not in channel:
                        self.errors.append(ValidationError(f"applicationProcess.channels[{i}].{field}", "Field is missing"))
                    elif not isinstance(channel[field], (str if field == "type" else bool)):
                        self.errors.append(ValidationError(f"applicationProcess.channels[{i}].{field}", f"Expected {'string' if field == 'type' else 'boolean'}, got {type(channel[field])}"))
                
                for field in optional_fields:
                    if field in channel and not isinstance(channel[field], str):
                        self.errors.append(ValidationError(f"applicationProcess.channels[{i}].{field}", f"Expected string or null, got {type(channel[field])}"))
        
        if "instantApproval" in process:
            approval = process["instantApproval"]
            required_fields = ["isAvailable", "conditions"]
            for field in required_fields:
                if field not in approval:
                    self.errors.append(ValidationError(f"applicationProcess.instantApproval.{field}", "Field is missing"))
                elif not isinstance(approval[field], (bool if field == "isAvailable" else list)):
                    self.errors.append(ValidationError(f"applicationProcess.instantApproval.{field}", f"Expected {'boolean' if field == 'isAvailable' else 'list'}, got {type(approval[field])}"))

    def validate_customer_insights(self, insights: Dict) -> None:
        required_fields = {
            "recommendedFor": list,
            "notRecommendedFor": list
        }
        
        for field, expected_type in required_fields.items():
            if field not in insights:
                self.errors.append(ValidationError(f"customerInsights.{field}", "Field is missing"))
            elif not isinstance(insights[field], expected_type):
                self.errors.append(ValidationError(f"customerInsights.{field}", f"Expected {expected_type.__name__}, got {type(insights[field])}"))

    def validate_customer_support(self, support: Dict) -> None:
        required_fields = {
            "channels": list,
            "dedicatedSupport": bool
        }
        
        for field, expected_type in required_fields.items():
            if field not in support:
                self.errors.append(ValidationError(f"customerSupport.{field}", "Field is missing"))
            elif not isinstance(support[field], expected_type):
                self.errors.append(ValidationError(f"customerSupport.{field}", f"Expected {expected_type.__name__}, got {type(support[field])}"))
        
        if "channels" in support:
            for i, channel in enumerate(support["channels"]):
                required_fields = ["type"]
                optional_fields = ["value", "availability", "responseTime", "isAvailable"]
                
                for field in required_fields:
                    if field not in channel:
                        self.errors.append(ValidationError(f"customerSupport.channels[{i}].{field}", "Field is missing"))
                    elif not isinstance(channel[field], str):
                        self.errors.append(ValidationError(f"customerSupport.channels[{i}].{field}", f"Expected string, got {type(channel[field])}"))
                
                for field in optional_fields:
                    if field in channel:
                        if field == "isAvailable" and not isinstance(channel[field], bool):
                            self.errors.append(ValidationError(f"customerSupport.channels[{i}].{field}", f"Expected boolean or null, got {type(channel[field])}"))
                        elif field != "isAvailable" and not isinstance(channel[field], str):
                            self.errors.append(ValidationError(f"customerSupport.channels[{i}].{field}", f"Expected string or null, got {type(channel[field])}"))

    def validate_change_log(self, change_logs: List) -> None:
        if not isinstance(change_logs, list):
            self.errors.append(ValidationError("changeLog", f"Expected list, got {type(change_logs)}"))
            return
        
        for i, log in enumerate(change_logs):
            if not isinstance(log, dict):
                self.errors.append(ValidationError(f"changeLog[{i}]", f"Expected dictionary, got {type(log)}"))
                continue
            
            required_fields = ["date", "type", "change"]
            for field in required_fields:
                if field not in log:
                    self.errors.append(ValidationError(f"changeLog[{i}].{field}", "Field is missing"))
                elif not isinstance(log[field], str):
                    self.errors.append(ValidationError(f"changeLog[{i}].{field}", f"Expected string, got {type(log[field])}"))

    def validate(self) -> List[ValidationError]:
        """Run all validations on the JSON file."""
        if not self.load_json():
            return self.errors

        # Validate top-level fields
        allowed_fields = {
            "id", "card", "presentation", "financials", "rewards", 
            "benefits", "eligibility", "applicationProcess", 
            "customerInsights", "customerSupport", "changeLog"
        }
        self.check_unknown_fields(self.data, allowed_fields, "")
        
        required_fields = {
            "id": str,
            "card": dict,
            "presentation": dict,
            "financials": dict,
            "rewards": dict,
            "benefits": list,
            "eligibility": dict,
            "applicationProcess": dict,
            "customerInsights": dict,
            "customerSupport": dict,
            "changeLog": list
        }
        
        for field, expected_type in required_fields.items():
            if field not in self.data:
                self.errors.append(ValidationError(field, "Field is missing"))
            elif not isinstance(self.data[field], expected_type):
                self.errors.append(ValidationError(field, f"Expected {expected_type.__name__}, got {type(self.data[field])}"))
        
        # Validate each section
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
            self.validate_application_process(self.data["applicationProcess"])
        if "customerInsights" in self.data:
            self.validate_customer_insights(self.data["customerInsights"])
        if "customerSupport" in self.data:
            self.validate_customer_support(self.data["customerSupport"])
        if "changeLog" in self.data:
            self.validate_change_log(self.data["changeLog"])
        
        return self.errors

def main():
    parser = argparse.ArgumentParser(description='Validate credit card JSON files against the Android app data model')
    parser.add_argument('file_path', help='Path to the JSON file to validate')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed validation errors')
    args = parser.parse_args()

    validator = CreditCardValidator(args.file_path)
    errors = validator.validate()
    
    if errors:
        print(f"\nValidation failed for {args.file_path}")
        if args.verbose:
            print("\nDetailed errors:")
            for error in errors:
                print(f"- {error.field}: {error.message}")
        else:
            print(f"Found {len(errors)} validation errors. Use --verbose for details.")
        sys.exit(1)
    else:
        print(f"\nValidation successful for {args.file_path}! All fields are present and have correct data types.")
        sys.exit(0)

if __name__ == "__main__":
    main() 