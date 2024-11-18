# app.py
from flask import Flask, render_template, request, jsonify
import os
import json
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
import requests
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the expected response schema using Pydantic
class NutritionScores(BaseModel):
    calories: float
    protein: float
    fat: float
    carbohydrates: float
    fiber: float
    is_recipe: bool
    insight: str

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_food_suggestions', methods=['GET'])
def get_food_suggestions():
    try:
        # Modified prompt for food suggestions
        prompt = (
            "Provide a list of top 20 popular Indian dishes eaten in breakfast, lunch, and dinner."
            "IMPORTANT:Provide the list as plain text, with each dish name separated by a comma. "
            "Examples should include a mix of popular dishes from Western, Asian, Mediterranean, and Indian cuisines, without any extra text or full stops."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5
        )

        food_suggestions_text = response.choices[0].message.content.strip()
        dishes = [dish.strip() for dish in food_suggestions_text.split(',')]
        print(f"Food suggestions received from OpenAI: {dishes}")

        return jsonify({"suggestions": dishes})

    except Exception as e:
        print(f"Error fetching food suggestions: {e}")
        return jsonify({"error": "Could not retrieve food suggestions"}), 500

@app.route('/calculate_nutrition', methods=['POST'])
def calculate_nutrition():
    data = request.get_json()
    food_item = data.get("food_item").lower()
    quantity = data.get("quantity", 100)
    quantity_unit = data.get("unit", "g")

    try:
        # Construct prompts for OpenAI API
        system_prompt = (
            "You are a highly accurate and reliable nutritionist providing data from reputable sources, such as the USDA. "
            "Provide nutritional information in JSON format for calories, protein, fat, carbohydrates, and fiber based on the specified quantity and unit. "
            "Ensure that values are accurate, consistent, and scaled proportionally from a standard serving size. Include an insightful one-sentence description of the food item"
            "If the food item is a prepared dish/recipe (not a simple ingredient), set is_recipe to true. "
            "IMPORTANT: Respond **only** with valid JSON in this exact format without any extra text: "
            '{"calories": <number>, "protein": <number>, "fat": <number>, "carbohydrates": <number>, "fiber": <number>, "insight": <string>, "is_recipe": <boolean>}'
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
        print(f"JSON decode error: {je}")
        response_data = {
            "error": "Invalid response format from AI service",
            "status": "error",
            "error_type": "json_decode_error"
        }  
    except (APIError, RateLimitError, APIConnectionError) as api_error:
        print(f"API error: {api_error}")
        response_data = {
            "error": "Our AI service is temporarily unavailable. Please try again later.",
            "status": "error",
            "error_type": "api_error"
        }
    except ValidationError as ve:
        print(f"Validation error: {ve}")
        response_data = {
            "error": "Invalid response format received from AI.",
            "status": "error",
            "error_type": "validation_error"
        }
    except ValueError as ve:
        print(f"Value error: {ve}")
        response_data = {
            "error": "Invalid input. Please check your values.",
            "status": "error",
            "error_type": "input_error"
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        response_data = {
            "error": "An unexpected error occurred. Please try again.",
            "status": "error",
            "error_type": "unknown_error"
        }

    return jsonify(response_data)

def get_youtube_links(food_item, max_results=10):
    try:
        youtube = build('youtube', 'v3', 
                       developerKey=os.environ.get('YOUTUBE_API_KEY'))
        
        search_response = youtube.search().list(
            q=f"how to make {food_item} recipe",
            part='id,snippet',  # Added snippet to get video titles
            maxResults=max_results,
            type='video'
        ).execute()

        videos = []
        if search_response.get('items'):
            for item in search_response['items']:
                video_id = item['id']['videoId']
                video_title = item['snippet']['title']
                videos.append({
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'id': video_id,
                    'title': video_title
                })
            return videos
        
        return None
    except Exception as e:
        print(f"Error fetching YouTube links: {e}")
        return None

if __name__ == "__main__":
    app.run(debug=True)
