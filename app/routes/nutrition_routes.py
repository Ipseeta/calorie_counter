from flask import Blueprint, request, jsonify, current_app
from http import HTTPStatus
from app.services.nutrition_analyzer import NutritionAnalyzer
from app.services.openai_service import OpenAIService
from app.services.youtube_service import YouTubeService
from app.exceptions.api_exceptions import APIException
from typing import Optional, Any
from app.config import Config
from PIL import Image, UnidentifiedImageError

# Blueprint for handling nutrition-related routes
nutrition_bp = Blueprint('nutrition', __name__)
analyzer = NutritionAnalyzer()
openai_service = OpenAIService(api_key=Config.OPENAI_API_KEY)

def validate_input(food_item: Optional[str], quantity: Any, unit: Optional[str]) -> None:
    """
    Validates the input parameters for nutrition calculation
    Args:
        food_item: Name of the food item
        quantity: Amount of food
        unit: Unit of measurement
    Raises:
        APIException: If any validation fails
    """
    if not food_item:
        raise APIException("Food item is required", HTTPStatus.BAD_REQUEST, "validation_error")
    
    try:
        quantity = float(quantity)
        if quantity <= 0:
            raise ValueError
    except (TypeError, ValueError):
        raise APIException("Invalid quantity value", HTTPStatus.BAD_REQUEST, "validation_error")
    
    if not unit:
        raise APIException("Please select a unit of measurement", HTTPStatus.BAD_REQUEST, "validation_error")
    
    valid_units = {"units", "grams", "ml", "bowl", "cup", "tbsp", "tsp", 'plate'}
    if unit not in valid_units:
        raise APIException("Invalid unit of measurement", HTTPStatus.BAD_REQUEST, "validation_error")

@nutrition_bp.route('/get_food_suggestions', methods=['GET'])
def get_food_suggestions():
    """
    Endpoint to fetch food suggestions from OpenAI
    Returns:
        JSON response containing food suggestions
    """
    try:
        suggestions = openai_service.get_food_suggestions()
        return jsonify(suggestions.model_dump())

    except Exception as e:
        raise APIException(
            "Failed to fetch food suggestions",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "food_suggestions_error"
        )

@nutrition_bp.route('/calculate_nutrition', methods=['POST'])
def calculate_nutrition():
    """
    Endpoint to calculate nutrition information for a given food item
    Returns:
        JSON response containing nutrition data, health score, and recipe videos if applicable
    """
    try:
        data = request.get_json()
        if not data:
            raise APIException("No data provided", HTTPStatus.BAD_REQUEST, "validation_error")

        food_item = data.get("food_item", "").lower().strip()
        quantity = data.get("quantity")
        quantity_unit = data.get("unit")

        # Validate input
        validate_input(food_item, quantity, quantity_unit)

        # Get nutrition information
        nutrition_data = openai_service.get_nutrition_info(food_item, quantity, quantity_unit)
        
        # Calculate health score
        health_score = analyzer.calculate_health_score(nutrition_data.model_dump())
        
        # Get recipe URLs if needed
        recipe_urls = None
        youtube_service = YouTubeService(api_key=Config.YOUTUBE_API_KEY)
        video_info_list = None
        if nutrition_data.is_recipe:
            video_info_list = youtube_service.get_recipe_videos(True, food_item)
            if video_info_list:  # Check if videos were found
                recipe_urls = [
                    {
                        "title": video.title,
                        "url": video.url,
                        "id": video.id
                    }
                    for video in video_info_list
                ]
        else:
            video_info_list = youtube_service.get_recipe_videos(False, food_item)
            if video_info_list:
                recipe_urls = [
                    {
                        "title": video.title,
                        "url": video.url,
                        "id": video.id
                    }
                    for video in video_info_list
                ]   
        # Prepare the final response
        response_data = {
            "food_item": food_item,
            "quantity": quantity,
            "unit": quantity_unit,
            "nutrition_info": nutrition_data.model_dump(),
            "insight": nutrition_data.insight,
            "is_recipe": nutrition_data.is_recipe,
            "is_valid_food": nutrition_data.is_valid_food,
            "recipe_urls": recipe_urls,
            "health_score": {
                "score": health_score.score,
                "message": health_score.message,
                "color": health_score.color
            },
            "status": "success"
        }

        return jsonify(response_data)

    except APIException as e:
        raise e
    except Exception as e:
        raise APIException(
            "An unexpected error occurred",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "server_error"
        )

@nutrition_bp.route('/analyze_image', methods=['POST'])
def analyze_image():
    """
    Endpoint to analyze an image and return nutrition information
    Returns:
        JSON response containing nutrition data, health score, and recipe videos if applicable
    """
    try:
        if 'image' not in request.files:
            raise APIException.missing_image()
        
        file = request.files['image']
        if file.filename == '':
            raise APIException.empty_image()
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise APIException.invalid_file_type(file.content_type)
            
        # Validate image can be opened
        try:
            Image.open(file)
            file.seek(0)  # Reset file pointer after checking
        except UnidentifiedImageError:
            raise APIException.invalid_image_format()
        
        # Analyze image with OpenAI using the image data
        # Get food item from image
        food_info = openai_service.get_food_item_from_image(file)
        # Validate input
        validate_input(food_info.food_item, food_info.quantity, food_info.unit)
        # Get nutrition info using existing function
        nutrition_data = openai_service.get_nutrition_info(
            food_info.food_item, 
            float(food_info.quantity), 
            food_info.unit
        )
            
        # Calculate health score
        health_score = analyzer.calculate_health_score(nutrition_data.model_dump())
            
        # Get recipe URLs if needed
        recipe_urls = None
        youtube_service = YouTubeService(api_key=Config.YOUTUBE_API_KEY)
        video_info_list = None
        if nutrition_data.is_recipe:
            video_info_list = youtube_service.get_recipe_videos(True, food_info.food_item)
            if video_info_list:
                recipe_urls = [
                    {
                        "title": video.title,
                        "url": video.url,
                        "id": video.id
                    }
                    for video in video_info_list
                ]
        else:
            video_info_list = youtube_service.get_recipe_videos(False, food_info.food_item)
            if video_info_list:
                recipe_urls = [
                    {
                        "title": video.title,
                        "url": video.url,
                        "id": video.id
                    }
                    for video in video_info_list
                ]   
        # Prepare the final response
        response_data = {
            "food_item": food_info.food_item,
            "quantity": float(food_info.quantity),
            "unit": food_info.unit,
            "nutrition_info": nutrition_data.model_dump(),
            "insight": nutrition_data.insight,
            "is_recipe": nutrition_data.is_recipe,
            "is_valid_food": nutrition_data.is_valid_food,
            "recipe_urls": recipe_urls,
            "health_score": {
                "score": health_score.score,
                "message": health_score.message,
                "color": health_score.color
            },
            "status": "success"
        }
        return jsonify(response_data)
        
    except ValueError as ve:
        raise APIException(
            message=str(ve),
            status_code=400,
            error_type='VALIDATION_ERROR'
        )
    except APIException as ae:
        current_app.logger.error(f"API Exception in analyze_image: {ae}")
        return jsonify(ae.to_dict()), ae.status_code

    except Exception as e:
        current_app.logger.error(f"Unexpected error in analyze_image: {str(e)}")
        error = APIException(
            message="An unexpected error occurred",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_type="INTERNAL_ERROR",
            details={"original_error": str(e)}
        )
        return jsonify(error.to_dict()), error.status_code

