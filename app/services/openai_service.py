from openai import OpenAI
from app.models.nutrition_models import NutritionScores, FoodSuggestions
from app.exceptions.api_exceptions import APIException
from http import HTTPStatus

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
            "Provide nutritional information in JSON format for calories, protein, fat, carbohydrates, fiber, sugar, sodium, vitamin A, vitamin C, calcium, and iron with units based on the specified quantity and unit. "
            "Ensure that values are accurate, consistent, and scaled proportionally from a standard serving size. Include an insightful one-sentence description of the food item"
            "If the food item is a prepared dish/recipe (not a simple ingredient), set is_recipe to true. "
            "If the food item is not a valid food item, set is_valid_food to false. "
            "IMPORTANT: Respond **only** with valid JSON in this exact format without any extra text: "
            '{"calories": <string>, "protein": <string>, "fat": <string>, "carbohydrates": <string>, "fiber": <string>, '
            '"sugar": <string>, "sodium": <string>, "vitamin_a": <string>, "vitamin_c": <string>, "calcium": <string>, '
            '"iron": <string>, "insight": <string>, "is_recipe": <boolean>, "is_valid_food": <boolean>}'
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