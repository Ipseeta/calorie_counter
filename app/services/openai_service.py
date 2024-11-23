from openai import OpenAI
from app.models.nutrition_models import NutritionScores, FoodSuggestions, FoodItem
from app.exceptions.api_exceptions import APIException
from http import HTTPStatus
import base64
from flask import current_app

class OpenAIService:
    """
    Service class for interacting with OpenAI API
    Handles food suggestions and nutrition information retrieval
    """

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def get_food_suggestions(self) -> FoodSuggestions:
        """
        Fetches food suggestions using OpenAI
        Returns:
            FoodSuggestions object containing list of food items
        """
        prompt = (
            "Provide a mix of list of top 20 popular dishes eaten in breakfast, lunch, and dinner mostly in Indian households."
            "IMPORTANT: Provide the only the list without any explanation or extra text or numbers"
        )

        response = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format=FoodSuggestions,
            temperature=0.5
        )
        return response.choices[0].message.parsed

    def get_nutrition_info(self, food_item: str, quantity: float, unit: str) -> NutritionScores:
        """
        Gets nutrition information for a food item using OpenAI
        Args:
            food_item: Name of the food item
            quantity: Amount of food
            unit: Unit of measurement
        Returns:
            NutritionScores object containing detailed nutrition information
        """
        system_prompt = (
            "You are a highly accurate and reliable nutritionist providing data from reputable sources, such as the USDA. "
            "Provide nutritional information in JSON format based on the specified quantity and unit, ensuring values are accurate, scaled proportionally from standard serving size. "
            "IMPORTANT: All numeric values should be rounded to the nearest whole number with units (e.g., '19g' instead of '18.7g', '98mg' instead of '98.3mg'). "
            "Include an insightful one-sentence description of the food item. "
            "If the food item is a prepared dish/recipe (not a simple ingredient), set is_recipe to true. "
            "If the food item is not a valid food item, set is_valid_food to false. "
            "IMPORTANT: Respond **only** with valid JSON in this exact format without any extra text: "
            '{"calories": <string>, "protein": <string>, '
            '"fat": {"total": <string>, "saturated": <string>, "trans": <string>, "polyunsaturated": <string>, "monounsaturated": <string>}, '
            '"carbohydrates": {"total": <string>, "dietary_fiber": <string>, "sugar": <string>, "added_sugar": <string>}, '
            '"fiber": <string>, "sugar": <string>, "sodium": <string>, '
            '"vitamin_a": <string>, "vitamin_c": <string>, "vitamin_d": <string>, '
            '"calcium": <string>, "iron": <string>, "potassium": <string>, '
            '"is_recipe": <boolean>, "is_valid_food": <boolean>, "insight": <string>}'
        )

        user_prompt = f"Provide precise nutritional information for {quantity} {unit} of {food_item} based on a standard serving size. Ensure values scale accurately."

        try:
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=NutritionScores,
                temperature=0.3
            )
            return response.choices[0].message.parsed

        except Exception as e:
            raise APIException(
                message="Failed to get nutrition information from OpenAI",
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                error_type="openai_api_error"
            ) 
    def get_food_item_from_image(self, image_file):
        """
        Gets the food item from an image using OpenAI
        """
        # Read the image data
        image_data = image_file.read()
        
        user_prompt = (
            {
                "type": "text", 
                "text": """You are a food image analyzer:
                        If this image contains food, provide:
                            1. The exact name of the food item
                            2. The approximate quantity in a suitable unit ("units", "grams", "ml", "bowl", "cup", "tbsp", "tsp")
                            3. If this is NOT a food image (e.g., selfie, landscape, random image, etc.), respond with:
                            {"error": "This image does not contain food. Please upload a food image."}
                            IMPORTANT: Respond **only** with valid JSON in this exact format without any extra text:
                            {"food_item": <string>, "quantity": <number>, "unit": <string>}
                            The quantity should be a number and the unit should be one of the following: "units", "grams", "ml", "bowl", "cup", "tbsp", "tsp"
                            Format your response exactly like this example:
                            food_item: Apple
                            quantity: 1
                            unit: pieces"""
            },
            {
                "type": "image_url", 
                "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"}
            }
        )
        try:
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                response_format=FoodItem,
                temperature=0.3
            )
            return response.choices[0].message.parsed

        except Exception as e:
            raise APIException(
                message=e.message,
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                error_type="openai_api_error"
            ) 
        
    def validate_food_item(self, food_item: str):
        """
        Validates the food item, quantity, and unit
        """
        current_app.logger.info("In validate_food_item for %s", food_item)
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                 messages=[
                {
                    "role": "system",
                    "content": "You are a food validator. Respond with only 'true' if the input is a valid food item, or 'false' if it's not."
                },
                {
                    "role": "user",
                    "content": f"Is this a valid food item: {food_item}"
                }
            ],
                temperature=0.3
        )
            validation_result = response.choices[0].message.content.strip().lower() == 'true'
            current_app.logger.info("Validation result for %s: %s", food_item, validation_result)
            return validation_result
        except Exception as e:
            print(f"Error in validate_food_item: {e}")
            raise APIException(
                message=str(e),
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                error_type="openai_api_error"
            ) 