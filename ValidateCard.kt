package com.itsivag.cards.model

fun main() {
    val validator = CreditCardValidator("india/axis/flipkart_axis.json")
    val errors = validator.validate()
    
    if (errors.isEmpty()) {
        println("✓ Flipkart Axis card JSON is valid")
    } else {
        println("✗ Flipkart Axis card JSON has validation errors:")
        errors.forEach { error ->
            println("  - ${error.path}: ${error.message}")
        }
    }
} 