# app.py
from flask import Flask, render_template, request, jsonify
import os
import json
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, Field

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the expected response schema using Pydantic
class NutritionScores(BaseModel):
    calories: float = Field(..., ge=0.0)
    protein: float = Field(..., ge=0.0)
    fat: float = Field(..., ge=0.0)
    carbohydrates: float = Field(..., ge=0.0)
    fiber: float = Field(..., ge=0.0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_food_suggestions', methods=['GET'])
def get_food_suggestions():
    try:
        # Modified prompt for food suggestions
        prompt = (
            "Provide a list of top 20 popular dishes from a variety of cuisines around the world, including some well-known Indian dishes. "
            "IMPORTANT:Provide the list as plain text, with each dish name separated by a comma. "
            "Examples should include a mix of popular dishes from Western, Asian, Mediterranean, and Indian cuisines, without any extra text."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
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
            "Ensure that values are accurate, consistent, and scaled proportionally from a standard serving size. "
            "IMPORTANT: Respond ONLY with valid JSON in this exact format without any extra text: "
            '{"calories": <number>, "protein": <number>, "fat": <number>, "carbohydrates": <number>, "fiber": <number>}'
        )

        user_prompt = f"Provide precise nutritional information for {quantity} {quantity_unit} of {food_item} based on a standard serving size. Ensure values scale accurately."

        print(f"User prompt: {user_prompt}")

        # Call OpenAI API with the constructed prompts
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=50,
            temperature=0.3
        )

        # Process the response content and convert to JSON
        nutrition_text = response.choices[0].message.content.strip()
        print(f"Received response: {nutrition_text}")

        # Parse JSON response from OpenAI
        nutrition_data = json.loads(nutrition_text)

        # Validate the JSON response with Pydantic
        scores = NutritionScores(**nutrition_data)

        # Prepare the final response
        response_data = {
            "food_item": food_item,
            "quantity": quantity,
            "unit": quantity_unit,
            "nutrition_info": scores.model_dump(),
            "status": "success"
        }
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

if __name__ == "__main__":
    app.run(debug=True)
