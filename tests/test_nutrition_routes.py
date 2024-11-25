import json
import pytest
import os
from unittest.mock import patch, Mock
from PIL import Image
from . import TEST_DATA
from app.exceptions.api_exceptions import APIException

# Get the path to the test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
TEST_IMAGES_DIR = os.path.join(TEST_DATA_DIR, 'images')

class TestNutritionRoutes:
    """Test cases for nutrition-related routes"""

    @patch('app.services.openai_service.OpenAIService.get_food_suggestions')
    def test_get_food_suggestions(self, mock_suggestions, client):
        """Test food suggestions endpoint"""
        # Mock the OpenAI response
        mock_suggestions.return_value = Mock(
            model_dump=lambda: TEST_DATA["expected_responses"]["food_suggestions"]
        )

        response = client.get('/get_food_suggestions')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_calculate_nutrition_validation(self, client):
        """Test nutrition calculation validation errors"""
        test_cases = [
            ({}, {
                "error": "No data provided",
                "error_type": "validation_error",
                "status": "error"
            }),
            ({"quantity": "1", "unit": "units"}, {
                "error": "Food item is required",
                "error_type": "validation_error",
                "status": "error"
            }),
            ({"food_item": "eggs", "quantity": "-1", "unit": "units"}, {
                "error": "Invalid quantity value",
                "error_type": "validation_error",
                "status": "error"
            }),
            ({"food_item": "eggs", "quantity": "1", "unit": "invalid"}, {
                "error": "Invalid unit of measurement",
                "error_type": "validation_error",
                "status": "error"
            })
        ]

        for test_data, expected_response in test_cases:
            try:
                response = client.post(
                    '/calculate_nutrition',
                    json=test_data,
                    content_type='application/json'
                )
                
                if isinstance(response, APIException):
                    actual_response = {
                        "error": response.message,
                        "error_type": response.error_type,
                        "status": "error"
                    }
                else:
                    actual_response = json.loads(response.data)
                
                assert actual_response == expected_response
                
            except APIException as e:
                actual_response = {
                    "error": e.message,
                    "error_type": e.error_type,
                    "status": "error"
                }
                assert actual_response == expected_response

    @patch('app.services.openai_service.OpenAIService.get_food_item_from_image')
    @patch('app.services.openai_service.OpenAIService.get_nutrition_info')
    @patch('app.services.youtube_service.YouTubeService.get_recipe_videos')
    def test_analyze_image_success(self, mock_videos, mock_nutrition, mock_image_analysis, client):
        """Test successful image analysis"""
        # Mock the OpenAI image analysis response
        mock_image_analysis.return_value = Mock(
            food_item="eggs",
            quantity="2",
            unit="units"
        )
        
        # Mock the OpenAI nutrition response
        mock_nutrition.return_value = Mock(
            model_dump=lambda: TEST_DATA["expected_responses"]["nutrition_calculation"]["nutrition_info"],
            insight="Eggs are a versatile and nutrient-rich food, providing high-quality protein and essential vitamins.",
            is_recipe=False,
            is_valid_food=True
        )
        
        # Mock YouTube response
        mock_videos.return_value = [
            Mock(
                title="How to Cook Perfect Eggs",
                url="http://example.com/eggs",
                id="123"
            )
        ]

        # Test image handling
        image_path = os.path.join(TEST_IMAGES_DIR, 'valid_food.jpg')
        if not os.path.exists(image_path):
            img = Image.new('RGB', (100, 100), color='white')
            img.save(image_path)

        with open(image_path, 'rb') as img_file:
            response = client.post(
                '/analyze_image',
                data={'image': (img_file, 'valid_food.jpg')},
                content_type='multipart/form-data'
            )
            
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify response structure
        assert data["food_item"] == "eggs"
        assert data["quantity"] == 2.0
        assert data["unit"] == "units"
        assert "nutrition_info" in data
        assert "health_score" in data
        assert data["health_score"]["color"] == "#3b82f6"
        assert isinstance(data["health_score"]["score"], (int, float))
        assert data["is_valid_food"] is True

    def test_analyze_image_validation(self, client):
        """Test image analysis validation errors"""
        # Test missing image
        response = client.post('/analyze_image')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data.get("error", {}).get("message") == "No image file provided"

        # Test empty image
        empty_image_path = os.path.join(TEST_IMAGES_DIR, 'empty.jpg')
        if not os.path.exists(empty_image_path):
            img = Image.new('RGB', (1, 1), color='white')
            img.save(empty_image_path)

        with open(empty_image_path, 'rb') as img_file:
            response = client.post(
                '/analyze_image',
                data={'image': (img_file, '')}
            )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data.get("error", {}).get("message") == "No selected image file"

        # Test invalid file type
        invalid_file_path = os.path.join(TEST_IMAGES_DIR, 'invalid_format.txt')
        if not os.path.exists(invalid_file_path):
            with open(invalid_file_path, 'w') as f:
                f.write('This is not an image file')

        with open(invalid_file_path, 'rb') as invalid_file:
            response = client.post(
                '/analyze_image',
                data={'image': (invalid_file, 'invalid_format.txt')}
            )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Uploaded file is not an image" in data.get("error", {}).get("message", "")

    @patch('app.services.openai_service.OpenAIService.get_food_item_from_image')
    @patch('app.services.openai_service.OpenAIService.get_nutrition_info')
    @patch('app.services.youtube_service.YouTubeService.get_recipe_videos')
    def test_analyze_image_large_file(self, mock_videos, mock_nutrition, mock_image_analysis, client):
        """Test image analysis with a large file"""
        # Mock the OpenAI image analysis response
        mock_image_analysis.return_value = Mock(
            food_item="large plate of food",
            quantity="1",
            unit="plate"
        )
        
        # Mock the OpenAI nutrition response
        mock_nutrition.return_value = Mock(
            model_dump=lambda: TEST_DATA["expected_responses"]["nutrition_calculation"]["nutrition_info"],
            insight="Large portion size",
            is_recipe=True,
            is_valid_food=True
        )
        
        # Mock YouTube response
        mock_videos.return_value = [
            Mock(title="Recipe 1", url="http://example.com/1", id="123")
        ]

        # Create a large test image
        large_image_path = os.path.join(TEST_IMAGES_DIR, 'large_test.jpg')
        large_img = Image.new('RGB', (2000, 2000), color='red')
        large_img.save(large_image_path, 'JPEG', quality=95)

        try:
            with open(large_image_path, 'rb') as img_file:
                response = client.post(
                    '/analyze_image',
                    data={'image': (img_file, 'large_test.jpg')},
                    content_type='multipart/form-data'
                )
                
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "nutrition_info" in data
            assert "health_score" in data
        finally:
            # Clean up the large test image
            if os.path.exists(large_image_path):
                os.remove(large_image_path)

    @patch('app.services.openai_service.OpenAIService.get_food_item_from_image')
    @patch('app.services.openai_service.OpenAIService.get_nutrition_info')
    @patch('app.services.youtube_service.YouTubeService.get_recipe_videos')
    def test_analyze_real_chicken_breast(self, mock_videos, mock_nutrition, mock_image_analysis, client):
        """Test analysis of a real chicken breast image"""
        
        # Mock the OpenAI image analysis response
        mock_image_analysis.return_value = Mock(
            food_item="chicken breast",
            quantity="1",
            unit="units"
        )
        
        # Mock the OpenAI nutrition response
        nutrition_data = {
            "calories": "165kcal",
            "protein": "31g",
            "fat": {
                "total": "3.6g",
                "saturated": "1g",
                "polyunsaturated": "0.8g",
                "monounsaturated": "1.5g",
                "trans": "0g"
            },
            "carbohydrates": {
                "total": "0g",
                "sugar": "0g",
                "added_sugar": "0g"
            },
            "fiber": "0g",
            "sodium": "74mg",
            "potassium": "387mg",
            "calcium": "15mg",
            "iron": "1mg",
            "vitamin_a": "0IU",
            "vitamin_c": "0mg",
            "vitamin_d": "0IU",
            "sugar": "0g",
            "insight": "Chicken breast is an excellent source of lean protein with low fat content.",
            "is_recipe": False,
            "is_valid_food": True
        }
        
        mock_nutrition.return_value = Mock(
            model_dump=lambda: nutrition_data,
            insight="Chicken breast is an excellent source of lean protein with low fat content.",
            is_recipe=False,
            is_valid_food=True
        )
        
        # Mock YouTube response with cooking videos
        video_data = [
            Mock(
                title="Perfect Grilled Chicken Breast Recipe",
                url="http://example.com/chicken",
                id="123"
            ),
            Mock(
                title="Juicy Baked Chicken Breast",
                url="http://example.com/baked-chicken",
                id="456"
            )
        ]
        mock_videos.return_value = video_data
        print("\nMocked YouTube Response:")
        print(f"Video Data: {[(v.title, v.url) for v in video_data]}")

        # Use a real chicken breast image for testing
        image_path = os.path.join(TEST_IMAGES_DIR, 'chicken_breast.jpg')
        if not os.path.exists(image_path):
            img = Image.new('RGB', (800, 600), color='pink')
            img.save(image_path)
        else:
            print("\nUsing existing test image")

        with open(image_path, 'rb') as img_file:
            response = client.post(
                '/analyze_image',
                data={'image': (img_file, 'chicken_breast.jpg')},
                content_type='multipart/form-data'
            )
            
        data = json.loads(response.data)
        # Verify response structure and content
        assert data["food_item"] == "chicken breast", f"Expected 'chicken breast', got {data.get('food_item')}"
        assert data["quantity"] == 1.0, f"Expected 1.0, got {data.get('quantity')}"
        assert data["unit"] == "units", f"Expected 'units', got {data.get('unit')}"
        assert "nutrition_info" in data, "Missing nutrition_info in response"
        assert "health_score" in data, "Missing health_score in response"
        assert data["is_valid_food"] is True, "Food should be valid"
        
        # Verify nutrition info
        nutrition = data["nutrition_info"]
        assert "calories" in nutrition, "Missing calories in nutrition info"
        assert "protein" in nutrition, "Missing protein in nutrition info"
        assert "fat" in nutrition, "Missing fat in nutrition info"
        assert "carbohydrates" in nutrition, "Missing carbohydrates in nutrition info"
        
        # Verify recipe videos
        print("\nVerifying recipe videos...")
        assert "recipe_urls" in data, "Missing recipe_urls in response"
        assert len(data["recipe_urls"]) == 2, f"Expected 2 recipe videos, got {len(data.get('recipe_urls', []))}"
        assert all(["title" in video and "url" in video for video in data["recipe_urls"]]), "Invalid video data structure"
