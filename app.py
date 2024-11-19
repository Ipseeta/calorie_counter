# app.py
from flask import Flask, render_template, request, jsonify
import os
import json
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from dotenv import load_dotenv
from pydantic import BaseModel
from googleapiclient.discovery import build
from typing import Optional, Any
from http import HTTPStatus

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the expected response schema using Pydantic for nutrition scores
class NutritionScores(BaseModel):
    calories: str
    protein: str
    fat: str
    carbohydrates: str
    fiber: str
    sugar: str
    sodium: str
    vitamin_a: str
    vitamin_c: str
    calcium: str
    iron: str
    is_recipe: bool
    insight: str

# Define the expected response schema using Pydantic for food suggestions
class FoodSuggestions(BaseModel):
    suggestions: list[str]

# Custom exception class for API errors
class APIException(Exception):
    def __init__(self, message: str, status_code: int, error_type: str):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(self.message)

# Error handler for API exceptions
@app.errorhandler(APIException)
def handle_api_exception(error):
    response = {
        "error": error.message,
        "status": "error",
        "error_type": error.error_type
    }
    return jsonify(response), error.status_code

# Function to validate input
def validate_input(food_item: Optional[str], quantity: Any, unit: Optional[str]) -> None:
    if not food_item:
        raise APIException("Food item is required", HTTPStatus.BAD_REQUEST, "validation_error")
    
    try:
        quantity = float(quantity)
        if quantity <= 0:
            raise ValueError
    except (TypeError, ValueError):
        raise APIException("Invalid quantity value", HTTPStatus.BAD_REQUEST, "validation_error")
    
    valid_units = {"units", "grams", "ml", "bowl", "cup", "tbsp", "tsp"}
    if unit not in valid_units:
        raise APIException("Invalid unit of measurement", HTTPStatus.BAD_REQUEST, "validation_error")

@app.route('/')
def index():
    return render_template('index.html')

# Route for fetching food suggestions
@app.route('/get_food_suggestions', methods=['GET'])
def get_food_suggestions():
    try:
        prompt = (
            "Provide a mix of list of top 20 popular dishes eaten in breakfast, lunch, and dinner mostly in Indian households."
            "IMPORTANT: Provide the only the list without any explanation or extra text or numbers"
        )

        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format=FoodSuggestions,
            temperature=0.5
        )

        # Process the response content and convert to JSON
        suggestions_dict = response.choices[0].message.parsed
        print(f"Food suggestions received from OpenAI: {suggestions_dict}")
        # Convert Pydantic model to dict before jsonifying
        return suggestions_dict.model_dump()

    except Exception as e:
        app.logger.error(f"Error fetching food suggestions: {str(e)}")
        raise APIException(
            "Failed to fetch food suggestions",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "food_suggestions_error"
        )

# Route for calculating nutrition
@app.route('/calculate_nutrition', methods=['POST'])
def calculate_nutrition():
    try:
        data = request.get_json()
        if not data:
            raise APIException("No data provided", HTTPStatus.BAD_REQUEST, "validation_error")

        food_item = data.get("food_item", "").lower().strip()
        quantity = data.get("quantity")
        quantity_unit = data.get("unit")

        # Validate input
        validate_input(food_item, quantity, quantity_unit)

        # Construct prompts for OpenAI API
        system_prompt = (
            "You are a highly accurate and reliable nutritionist providing data from reputable sources, such as the USDA. "
            "Provide nutritional information in JSON format for calories, protein, fat, carbohydrates, fiber, sugar, sodium, vitamin A, vitamin C, calcium, and iron with units based on the specified quantity and unit. "
            "Ensure that values are accurate, consistent, and scaled proportionally from a standard serving size. Include an insightful one-sentence description of the food item"
            "If the food item is a prepared dish/recipe (not a simple ingredient), set is_recipe to true. "
            "IMPORTANT: Respond **only** with valid JSON in this exact format without any extra text: "
            '{"calories": <string>, "protein": <string>, "fat": <string>, "carbohydrates": <string>, "fiber": <string>, "sugar": <string>, "sodium": <string>, "vitamin_a": <string>, "vitamin_c": <string>, "calcium": <string>, "iron": <string>, "insight": <string>, "is_recipe": <boolean>}'
        )

        user_prompt = f"Provide precise nutritional information for {quantity} {quantity_unit} of {food_item} based on a standard serving size. Ensure values scale accurately."

        print(f"User prompt: {user_prompt}")

        # Call OpenAI API with the constructed prompts
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format=NutritionScores
        )

        # Process the response content and convert to JSON
        nutrition_data = response.choices[0].message.parsed
        
         # After getting nutrition_data, if it's a recipe, fetch YouTube links
        recipe_urls = None
        if nutrition_data.is_recipe:
            recipe_urls = get_youtube_links(food_item)
        
        # Prepare the final response
        response_data = {
            "food_item": food_item,
            "quantity": quantity,
            "unit": quantity_unit,
            "nutrition_info": nutrition_data.model_dump(),
            "insight": nutrition_data.insight,
            "is_recipe": nutrition_data.is_recipe,
            "recipe_urls": recipe_urls,
            "status": "success"
        }
        #print(f"Received response: {response_data}")
    except json.JSONDecodeError as je:
        raise APIException(
            "Invalid JSON format in request",
            HTTPStatus.BAD_REQUEST,
            "json_decode_error"
        )
    except (APIError, RateLimitError) as api_error:
        raise APIException(
            "OpenAI service temporarily unavailable",
            HTTPStatus.SERVICE_UNAVAILABLE,
            "openai_api_error"
        )
    except APIConnectionError:
        raise APIException(
            "Could not connect to OpenAI service",
            HTTPStatus.BAD_GATEWAY,
            "connection_error"
        )
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        raise APIException(
            "An unexpected error occurred",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "server_error"
        )

    return jsonify(response_data)

# Function to fetch YouTube links for recipes
def get_youtube_links(food_item: str, max_results: int = 10) -> Optional[list]:
    if not os.environ.get('YOUTUBE_API_KEY'):
        app.logger.error("YouTube API key not found")
        return None

    try:
        youtube = build('youtube', 'v3', 
                       developerKey=os.environ.get('YOUTUBE_API_KEY'))
        
        search_response = youtube.search().list(
            q=f"how to make {food_item} recipe",
            part='id,snippet',
            maxResults=max_results,
            type='video',
            regionCode='IN'
        ).execute()

        if not search_response.get('items'):
            app.logger.warning(f"No videos found for {food_item}")
            return None

        videos = [{
            'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            'id': item['id']['videoId'],
            'title': item['snippet']['title']
        } for item in search_response['items']]
        
        return videos

    except Exception as e:
        app.logger.error(f"YouTube API error: {str(e)}")
        return None

if __name__ == "__main__":
    app.run(debug=True)
