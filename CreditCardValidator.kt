package com.itsivag.cards.model

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.io.File

class CreditCardValidator(private val filePath: String) {
    private val json = Json { 
        ignoreUnknownKeys = false 
        coerceInputValues = false
    }

    data class ValidationError(
        val message: String,
        val path: String = ""
    )

    fun validate(): List<ValidationError> {
        val errors = mutableListOf<ValidationError>()
        
        try {
            val jsonString = File(filePath).readText()
            val jsonObject = json.parseToJsonElement(jsonString).jsonObject
            
            // Validate required top-level fields
            validateRequiredFields(jsonObject, errors)
            
            // Validate card section
            jsonObject["card"]?.jsonObject?.let { cardObject ->
                validateCardSection(cardObject, errors)
            } ?: errors.add(ValidationError("Missing 'card' section", "card"))
            
            // Validate presentation section
            jsonObject["presentation"]?.jsonObject?.let { presentationObject ->
                validatePresentationSection(presentationObject, errors)
            } ?: errors.add(ValidationError("Missing 'presentation' section", "presentation"))
            
            // Validate financials section
            jsonObject["financials"]?.jsonObject?.let { financialsObject ->
                validateFinancialsSection(financialsObject, errors)
            } ?: errors.add(ValidationError("Missing 'financials' section", "financials"))
            
            // Validate rewards section
            jsonObject["rewards"]?.jsonObject?.let { rewardsObject ->
                validateRewardsSection(rewardsObject, errors)
            } ?: errors.add(ValidationError("Missing 'rewards' section", "rewards"))
            
            // Validate benefits section
            jsonObject["benefits"]?.let { benefitsArray ->
                validateBenefitsSection(benefitsArray, errors)
            } ?: errors.add(ValidationError("Missing 'benefits' section", "benefits"))
            
            // Validate eligibility section
            jsonObject["eligibility"]?.jsonObject?.let { eligibilityObject ->
                validateEligibilitySection(eligibilityObject, errors)
            } ?: errors.add(ValidationError("Missing 'eligibility' section", "eligibility"))
            
            // Validate application process section
            jsonObject["applicationProcess"]?.jsonObject?.let { applicationProcessObject ->
                validateApplicationProcessSection(applicationProcessObject, errors)
            } ?: errors.add(ValidationError("Missing 'applicationProcess' section", "applicationProcess"))
            
            // Validate customer insights section
            jsonObject["customerInsights"]?.jsonObject?.let { customerInsightsObject ->
                validateCustomerInsightsSection(customerInsightsObject, errors)
            } ?: errors.add(ValidationError("Missing 'customerInsights' section", "customerInsights"))

            // Validate customer support section
            jsonObject["customerSupport"]?.jsonObject?.let { customerSupportObject ->
                validateCustomerSupportSection(customerSupportObject, errors)
            } ?: errors.add(ValidationError("Missing 'customerSupport' section", "customerSupport"))

            // Validate change log section
            jsonObject["changeLog"]?.let { changeLogArray ->
                validateChangeLogSection(changeLogArray, errors)
            } ?: errors.add(ValidationError("Missing 'changeLog' section", "changeLog"))
            
        } catch (e: Exception) {
            errors.add(ValidationError("Failed to parse JSON: ${e.message}"))
        }
        
        return errors
    }

    private fun validateRequiredFields(jsonObject: JsonObject, errors: MutableList<ValidationError>) {
        if (!jsonObject.containsKey("id")) {
            errors.add(ValidationError("Missing required field 'id'", "id"))
        }
    }

    private fun validateCardSection(cardObject: JsonObject, errors: MutableList<ValidationError>) {
        val requiredFields = listOf("cardName", "cardIssuer", "ratings", "categories", "networkType", "targetAudience", "applyLink")
        
        requiredFields.forEach { field ->
            if (!cardObject.containsKey(field)) {
                errors.add(ValidationError("Missing required field '$field' in card section", "card.$field"))
            }
        }
    }

    private fun validatePresentationSection(presentationObject: JsonObject, errors: MutableList<ValidationError>) {
        val requiredFields = listOf("decoration", "description", "highlightFeatures", "marketingTagline")
        
        requiredFields.forEach { field ->
            if (!presentationObject.containsKey(field)) {
                errors.add(ValidationError("Missing required field '$field' in presentation section", "presentation.$field"))
            }
        }

        presentationObject["decoration"]?.jsonObject?.let { decorationObject ->
            val requiredDecorationFields = listOf("primaryColor", "secondaryColor", "orientation", "cardImage", "material", "specialFeatures")
            requiredDecorationFields.forEach { field ->
                if (!decorationObject.containsKey(field)) {
                    errors.add(ValidationError("Missing required field '$field' in decoration section", "presentation.decoration.$field"))
                }
            }
        }
    }

    private fun validateFinancialsSection(financialsObject: JsonObject, errors: MutableList<ValidationError>) {
        val requiredFields = listOf("fees", "charges")
        
        requiredFields.forEach { field ->
            if (!financialsObject.containsKey(field)) {
                errors.add(ValidationError("Missing required field '$field' in financials section", "financials.$field"))
            }
        }

        // Validate fees structure
        financialsObject["fees"]?.jsonObject?.let { feesObject ->
            val requiredFeeTypes = listOf("joining", "renewal", "additionalCards")
            requiredFeeTypes.forEach { feeType ->
                if (!feesObject.containsKey(feeType)) {
                    errors.add(ValidationError("Missing required fee type '$feeType'", "financials.fees.$feeType"))
                } else {
                    val feeObject = feesObject[feeType]?.jsonObject
                    if (feeObject != null) {
                        val requiredFeeFields = listOf("amount", "tax")
                        requiredFeeFields.forEach { field ->
                            if (!feeObject.containsKey(field)) {
                                errors.add(ValidationError("Missing required field '$field' in $feeType fee", "financials.fees.$feeType.$field"))
                            }
                        }
                        
                        // Validate waiverConditions for joining and renewal
                        if ((feeType == "joining" || feeType == "renewal") && !feeObject.containsKey("waiverConditions")) {
                            errors.add(ValidationError("Missing required field 'waiverConditions' in $feeType fee", "financials.fees.$feeType.waiverConditions"))
                        }
                    }
                }
            }
        }

        // Validate charges array
        financialsObject["charges"]?.let { chargesArray ->
            if (chargesArray.toString() == "[]") {
                errors.add(ValidationError("Charges array cannot be empty", "financials.charges"))
            } else {
                chargesArray.jsonArray.forEachIndexed { index, element ->
                    val chargeObject = element.jsonObject
                    val requiredChargeFields = listOf("type", "value")
                    requiredChargeFields.forEach { field ->
                        if (!chargeObject.containsKey(field)) {
                            errors.add(ValidationError("Missing required field '$field' in charge at index $index", "financials.charges[$index].$field"))
                        }
                    }
                }
            }
        }
    }

    private fun validateRewardsSection(rewardsObject: JsonObject, errors: MutableList<ValidationError>) {
        val requiredFields = listOf("type", "structure", "caps", "redemptionOptions", "excludedCategories")
        
        requiredFields.forEach { field ->
            if (!rewardsObject.containsKey(field)) {
                errors.add(ValidationError("Missing required field '$field' in rewards section", "rewards.$field"))
            }
        }

        // Validate structure array
        rewardsObject["structure"]?.let { structureArray ->
            if (structureArray.toString() == "[]") {
                errors.add(ValidationError("Rewards structure cannot be empty", "rewards.structure"))
            } else {
                structureArray.jsonArray.forEachIndexed { index, element ->
                    val structureObject = element.jsonObject
                    val requiredStructureFields = listOf("category", "rate", "details")
                    requiredStructureFields.forEach { field ->
                        if (!structureObject.containsKey(field)) {
                            errors.add(ValidationError("Missing required field '$field' in rewards structure at index $index", "rewards.structure[$index].$field"))
                        }
                    }
                }
            }
        }

        // Validate caps
        rewardsObject["caps"]?.jsonObject?.let { capsObject ->
            val requiredCapsFields = listOf("overall")
            requiredCapsFields.forEach { field ->
                if (!capsObject.containsKey(field)) {
                    errors.add(ValidationError("Missing required field '$field' in caps", "rewards.caps.$field"))
                }
            }
        }

        // Validate redemption options
        rewardsObject["redemptionOptions"]?.let { redemptionOptionsArray ->
            if (redemptionOptionsArray.toString() == "[]") {
                errors.add(ValidationError("Redemption options cannot be empty", "rewards.redemptionOptions"))
            } else {
                redemptionOptionsArray.jsonArray.forEachIndexed { index, element ->
                    val optionObject = element.jsonObject
                    val requiredOptionFields = listOf("method", "description")
                    requiredOptionFields.forEach { field ->
                        if (!optionObject.containsKey(field)) {
                            errors.add(ValidationError("Missing required field '$field' in redemption option at index $index", "rewards.redemptionOptions[$index].$field"))
                        }
                    }
                }
            }
        }
    }

    private fun validateBenefitsSection(benefitsArray: JsonObject, errors: MutableList<ValidationError>) {
        if (benefitsArray.toString() == "[]") {
            errors.add(ValidationError("Benefits array cannot be empty", "benefits"))
        } else {
            benefitsArray.jsonArray.forEachIndexed { index, element ->
                val benefitObject = element.jsonObject
                val requiredBenefitFields = listOf("type", "details")
                requiredBenefitFields.forEach { field ->
                    if (!benefitObject.containsKey(field)) {
                        errors.add(ValidationError("Missing required field '$field' in benefit at index $index", "benefits[$index].$field"))
                    }
                }

                // Validate benefit details
                benefitObject["details"]?.let { detailsArray ->
                    if (detailsArray.toString() == "[]") {
                        errors.add(ValidationError("Benefit details cannot be empty", "benefits[$index].details"))
                    } else {
                        detailsArray.jsonArray.forEachIndexed { detailIndex, detailElement ->
                            val detailObject = detailElement.jsonObject
                            val requiredDetailFields = listOf("name", "value", "condition")
                            requiredDetailFields.forEach { field ->
                                if (!detailObject.containsKey(field)) {
                                    errors.add(ValidationError("Missing required field '$field' in benefit detail at index $detailIndex", "benefits[$index].details[$detailIndex].$field"))
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    private fun validateEligibilitySection(eligibilityObject: JsonObject, errors: MutableList<ValidationError>) {
        val requiredFields = listOf("ageRequirement", "incomeRequirement", "creditScore", "requiredDocuments", "residentialStatus")
        
        requiredFields.forEach { field ->
            if (!eligibilityObject.containsKey(field)) {
                errors.add(ValidationError("Missing required field '$field' in eligibility section", "eligibility.$field"))
            }
        }

        // Validate age requirement
        eligibilityObject["ageRequirement"]?.jsonObject?.let { ageRequirementObject ->
            val requiredAgeFields = listOf("minimum", "maximum")
            requiredAgeFields.forEach { field ->
                if (!ageRequirementObject.containsKey(field)) {
                    errors.add(ValidationError("Missing required field '$field' in age requirement", "eligibility.ageRequirement.$field"))
                }
            }
        }

        // Validate income requirement
        eligibilityObject["incomeRequirement"]?.let { incomeRequirementArray ->
            if (incomeRequirementArray.toString() == "[]") {
                errors.add(ValidationError("Income requirement array cannot be empty", "eligibility.incomeRequirement"))
            } else {
                incomeRequirementArray.jsonArray.forEachIndexed { index, element ->
                    val incomeObject = element.jsonObject
                    val requiredIncomeFields = listOf("employmentType", "minimumIncome", "preferredIncomeLevel")
                    requiredIncomeFields.forEach { field ->
                        if (!incomeObject.containsKey(field)) {
                            errors.add(ValidationError("Missing required field '$field' in income requirement at index $index", "eligibility.incomeRequirement[$index].$field"))
                        }
                    }
                }
            }
        }

        // Validate credit score
        eligibilityObject["creditScore"]?.jsonObject?.let { creditScoreObject ->
            val requiredCreditScoreFields = listOf("minimum", "recommended")
            requiredCreditScoreFields.forEach { field ->
                if (!creditScoreObject.containsKey(field)) {
                    errors.add(ValidationError("Missing required field '$field' in credit score", "eligibility.creditScore.$field"))
                }
            }
        }

        // Validate required documents
        eligibilityObject["requiredDocuments"]?.let { documentsArray ->
            if (documentsArray.toString() == "[]") {
                errors.add(ValidationError("Required documents array cannot be empty", "eligibility.requiredDocuments"))
            } else {
                documentsArray.jsonArray.forEachIndexed { index, element ->
                    val documentObject = element.jsonObject
                    val requiredDocumentFields = listOf("type", "options")
                    requiredDocumentFields.forEach { field ->
                        if (!documentObject.containsKey(field)) {
                            errors.add(ValidationError("Missing required field '$field' in required document at index $index", "eligibility.requiredDocuments[$index].$field"))
                        }
                    }
                }
            }
        }
    }

    private fun validateApplicationProcessSection(applicationProcessObject: JsonObject, errors: MutableList<ValidationError>) {
        val requiredFields = listOf("channels", "processingTime", "trackingMethod", "instantApproval")
        
        requiredFields.forEach { field ->
            if (!applicationProcessObject.containsKey(field)) {
                errors.add(ValidationError("Missing required field '$field' in application process section", "applicationProcess.$field"))
            }
        }

        // Validate channels
        applicationProcessObject["channels"]?.let { channelsArray ->
            if (channelsArray.toString() == "[]") {
                errors.add(ValidationError("Channels array cannot be empty", "applicationProcess.channels"))
            } else {
                channelsArray.jsonArray.forEachIndexed { index, element ->
                    val channelObject = element.jsonObject
                    val requiredChannelFields = listOf("type", "isAvailable")
                    requiredChannelFields.forEach { field ->
                        if (!channelObject.containsKey(field)) {
                            errors.add(ValidationError("Missing required field '$field' in channel at index $index", "applicationProcess.channels[$index].$field"))
                        }
                    }
                }
            }
        }

        // Validate instant approval
        applicationProcessObject["instantApproval"]?.jsonObject?.let { instantApprovalObject ->
            val requiredInstantApprovalFields = listOf("isAvailable", "conditions")
            requiredInstantApprovalFields.forEach { field ->
                if (!instantApprovalObject.containsKey(field)) {
                    errors.add(ValidationError("Missing required field '$field' in instant approval", "applicationProcess.instantApproval.$field"))
                }
            }
        }
    }

    private fun validateCustomerInsightsSection(customerInsightsObject: JsonObject, errors: MutableList<ValidationError>) {
        val requiredFields = listOf("recommendedFor", "notRecommendedFor")
        
        requiredFields.forEach { field ->
            if (!customerInsightsObject.containsKey(field)) {
                errors.add(ValidationError("Missing required field '$field' in customer insights section", "customerInsights.$field"))
            }
        }
    }

    private fun validateCustomerSupportSection(customerSupportObject: JsonObject, errors: MutableList<ValidationError>) {
        val requiredFields = listOf("channels", "dedicatedSupport")
        
        requiredFields.forEach { field ->
            if (!customerSupportObject.containsKey(field)) {
                errors.add(ValidationError("Missing required field '$field' in customer support section", "customerSupport.$field"))
            }
        }

        // Validate support channels
        customerSupportObject["channels"]?.let { channelsArray ->
            if (channelsArray.toString() == "[]") {
                errors.add(ValidationError("Support channels array cannot be empty", "customerSupport.channels"))
            } else {
                channelsArray.jsonArray.forEachIndexed { index, element ->
                    val channelObject = element.jsonObject
                    val requiredChannelFields = listOf("type")
                    requiredChannelFields.forEach { field ->
                        if (!channelObject.containsKey(field)) {
                            errors.add(ValidationError("Missing required field '$field' in support channel at index $index", "customerSupport.channels[$index].$field"))
                        }
                    }
                }
            }
        }
    }

    private fun validateChangeLogSection(changeLogArray: JsonObject, errors: MutableList<ValidationError>) {
        if (changeLogArray.toString() == "[]") {
            errors.add(ValidationError("Change log array cannot be empty", "changeLog"))
        } else {
            changeLogArray.jsonArray.forEachIndexed { index, element ->
                val changeLogObject = element.jsonObject
                val requiredChangeLogFields = listOf("date", "type", "change")
                requiredChangeLogFields.forEach { field ->
                    if (!changeLogObject.containsKey(field)) {
                        errors.add(ValidationError("Missing required field '$field' in change log at index $index", "changeLog[$index].$field"))
                    }
                }
            }
        }
    }
} 