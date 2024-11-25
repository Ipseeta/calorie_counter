# Test data for nutrition routes
TEST_DATA = {
    "expected_responses": {
        "food_suggestions": {
            "suggestions": [
                "Grilled chicken breast with vegetables",
                "Quinoa salad with avocado",
                "Greek yogurt with berries"
            ]
        },
        "nutrition_calculation": {
            "food_item": "eggs",
            "quantity": "2",
            "unit": "units",
            "nutrition_info": {
                "calories": "143kcal",
                "protein": "12g",
                "fat": {
                    "total": "10g",
                    "saturated": "3g",
                    "polyunsaturated": "2g",
                    "monounsaturated": "4g",
                    "trans": "0g"
                },
                "carbohydrates": {
                    "total": "1g",
                    "sugar": "1g",
                    "added_sugar": "0g"
                },
                "fiber": "0g",
                "sodium": "124mg",
                "potassium": "138mg",
                "calcium": "56mg",
                "iron": "2mg",
                "vitamin_a": "270IU",
                "vitamin_c": "0mg",
                "vitamin_d": "82IU",
                "sugar": "1g",
                "insight": "Eggs are a versatile and nutrient-rich food, providing high-quality protein and essential vitamins.",
                "is_recipe": False,
                "is_valid_food": True
            },
            "health_score": {
                "score": 7.7,
                "message": "Good nutritional value",
                "color": "#3b82f6"
            },
            "insight": "Eggs are a versatile and nutrient-rich food, providing high-quality protein and essential vitamins.",
            "is_recipe": False,
            "is_valid_food": True
        }
    }
}

# Constants for testing
VALID_FILE_TYPES = {"image/jpeg", "image/png", "image/jpg"}