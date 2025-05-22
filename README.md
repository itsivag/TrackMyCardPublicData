# Credit Card JSON Validator

This repository contains JSON files for credit card data and a validation script to ensure they match the required data model.

## Validation Script

The `validate_credit_card_json.py` script validates credit card JSON files against a predefined data model. It checks for:
- Required fields
- Correct data types
- Valid structure
- No unknown fields

## Requirements

- Python 3.6 or higher

## Usage

To validate a JSON file, run:

```bash
python3 validate_credit_card_json.py <path_to_json_file> [--verbose]
```

### Arguments

- `<path_to_json_file>`: Path to the JSON file you want to validate
- `--verbose` or `-v`: (Optional) Show detailed validation errors

### Examples

1. Basic validation:
```bash
python3 validate_credit_card_json.py india/amex/amex_membership_rewards.json
```

2. Detailed validation with error messages:
```bash
python3 validate_credit_card_json.py india/amex/amex_membership_rewards.json --verbose
```

## Exit Codes

- `0`: Validation successful
- `1`: Validation failed

## JSON Structure

The JSON files should follow this structure:

```json
{
    "id": "string",
    "card": {
        "cardName": "string",
        "cardIssuer": "string",
        "ratings": "string",
        "categories": ["string"],
        "networkType": "string",
        "targetAudience": "string",
        "applyLink": "string"
    },
    "presentation": {
        "decoration": {
            "primaryColor": "integer",
            "secondaryColor": "integer",
            "orientation": "string",
            "cardImage": "string",
            "material": "string",
            "specialFeatures": ["string"]
        },
        "description": "string",
        "highlightFeatures": ["string"],
        "marketingTagline": "string"
    },
    "financials": {
        "fees": {
            "joining": {
                "amount": "string",
                "tax": "string",
                "waiverConditions": ["string"]
            },
            "renewal": {
                "amount": "string",
                "tax": "string",
                "waiverConditions": ["string"]
            },
            "additionalCards": {
                "amount": "string",
                "tax": "string"
            }
        },
        "charges": [
            {
                "type": "string",
                "value": "string",
                "annualizedValue": "string",
                "details": "string",
                "condition": "string"
            }
        ]
    },
    "rewards": {
        "type": "string",
        "structure": [
            {
                "category": "string",
                "rate": "string",
                "details": "string"
            }
        ],
        "caps": {
            "overall": "string",
            "categorySpecific": ["string"]
        },
        "redemptionOptions": [
            {
                "method": "string",
                "description": "string"
            }
        ],
        "excludedCategories": ["string"]
    },
    "benefits": [
        {
            "type": "string",
            "details": [
                {
                    "name": "string",
                    "value": "string",
                    "condition": "string",
                    "expiryPeriod": "string",
                    "locations": "string",
                    "programLink": "string"
                }
            ],
            "totalValue": "string"
        }
    ],
    "eligibility": {
        "ageRequirement": {
            "minimum": "integer",
            "maximum": "integer"
        },
        "incomeRequirement": [
            {
                "employmentType": "string",
                "minimumIncome": "string",
                "preferredIncomeLevel": "string"
            }
        ],
        "creditScore": {
            "minimum": "string",
            "recommended": "string"
        },
        "requiredDocuments": [
            {
                "type": "string",
                "options": ["string"]
            }
        ],
        "residentialStatus": ["string"]
    },
    "applicationProcess": {
        "channels": [
            {
                "type": "string",
                "isAvailable": "boolean",
                "url": "string",
                "details": "string"
            }
        ],
        "processingTime": "string",
        "trackingMethod": "string",
        "instantApproval": {
            "isAvailable": "boolean",
            "conditions": ["string"]
        }
    },
    "customerInsights": {
        "recommendedFor": ["string"],
        "notRecommendedFor": ["string"]
    },
    "customerSupport": {
        "channels": [
            {
                "type": "string",
                "value": "string",
                "availability": "string",
                "responseTime": "string",
                "isAvailable": "boolean"
            }
        ],
        "dedicatedSupport": "boolean"
    },
    "changeLog": [
        {
            "date": "string",
            "type": "string",
            "change": "string"
        }
    ]
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 