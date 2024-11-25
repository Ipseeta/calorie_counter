from openai import OpenAI
from app.models.nutrition_models import NutritionScores, FoodSuggestions, FoodItem
from app.exceptions.api_exceptions import APIException
from http import HTTPStatus
import base64
from flask import current_app, json
from json.decoder import JSONDecodeError
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
        try:
            image_data = image_file.read()
            
            # First get raw analysis from vision model
            only_vision_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a precise food image analyzer with strict rules:
                            1. Your primary task is to first determine if an image contains food or not
                            2. You must NEVER classify non-food items as food
                            3. If you see any humans, faces, or selfies, immediately return an error
                            4. If you see landscapes, objects, or any non-food items, return an error
                            5. Only proceed with food analysis if you are 100% certain the image contains food"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this image and return ONLY a JSON response in this exact format:
                                    For non-food images:
                                    {"error": "This image does not contain food. Please upload a food image only."}
                                    
                                    For images with people:
                                    {"error": "This appears to be an image containing people. Please upload a food image only."}

                                    For images with landscapes:
                                    {"error": "This appears to be an image containing landscapes. Please upload a food image only."}
                                    
                                    For food images:
                                    {"food_item": "name of food", "quantity": number, "unit": "units/grams/ml/bowl/cup/tbsp/tsp/plate"}
                                    
                                    DO NOT include any additional text or explanation."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"
                                }
                            }
                        ]
                    }
                ],
                response_format={ "type": "json_object" }
            )
            try:
                vision_result = json.loads(only_vision_response.choices[0].message.content)
            except JSONDecodeError as e:
                current_app.logger.error(f"Failed to parse vision API response: {only_vision_response.choices[0].message.content}")
                raise APIException.parse_error()
            # If there's an error, return it directly
            if "error" in vision_result:
                raise APIException.invalid_image(vision_result["error"])
            
            # Format the result using GPT-4 to ensure it matches FoodItem schema
            format_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """Format the provided food analysis into valid JSON with these exact fields:
                            - food_item (string)
                            - quantity (number)
                            - unit (string: one of "units", "grams", "ml", "bowl", "cup", "tbsp", "tsp", "plate")"""
                    },
                    {
                        "role": "user",
                        "content": f"Format this into the required schema: {json.dumps(vision_result)}"
                    }
                ],
                response_format={ "type": "json_object" }
            )
            try:    
                formatted_result = json.loads(format_response.choices[0].message.content)
            except JSONDecodeError as e:
                current_app.logger.error(f"Failed to parse format API response for FoodItem: {format_response.choices[0].message.content}")
                raise APIException.parse_error()
            return FoodItem(**formatted_result)

        except Exception as e:
            current_app.logger.error(f"Error in get_food_item_from_image: {e}")
            raise APIException(
                message=e,
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