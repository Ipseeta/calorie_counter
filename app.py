# app.py
from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI, APIError, OpenAIError, RateLimitError, APIConnectionError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_calories', methods=['POST'])
def calculate_calories():
    data = request.get_json()
    print(data)
    food_item = data.get("food_item").lower()
    quantity = data.get("quantity")
    quantityUnit = data.get("unit")

    try:
        # Query OpenAI for calorie information
        prompt = f"How many calories are in {quantity} {quantityUnit} of {food_item}?"
        print(f"Sending prompt to OpenAI: {prompt}")
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.3
        )

        calories_text = response.choices[0].message.content.strip()
        response_data = {
            "food_item": food_item,
            "quantity": quantity,
            "calories_info": calories_text,
            "status": "success"
        }

    except APIError as api_error:
        print(f"OpenAI API Error: {str(api_error)}")
        response_data = {
            "error": "Our AI service is temporarily unavailable. Please try again later.",
            "status": "error",
            "error_type": "api_error"
        }
        
    except RateLimitError as e:
        print(f"Rate limit exceeded: {str(e)}")
        response_data = {
            "error": "We've hit our rate limit. Please try again in a few moments.",
            "status": "error",
            "error_type": "rate_limit"
        }
        
    except APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {str(e)}")
        response_data = {
            "error": "Unable to connect to our AI service. Please check your internet connection.",
            "status": "error",
            "error_type": "connection_error"
        }
        
    except ValueError as ve:
        print(f"Value Error: {str(ve)}")
        response_data = {
            "error": "Invalid input provided. Please check your values and try again.",
            "status": "error",
            "error_type": "validation_error"
        }
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        response_data = {
            "error": "An unexpected error occurred. Please try again later.",
            "status": "error",
            "error_type": "unknown_error"
        }

    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True)
