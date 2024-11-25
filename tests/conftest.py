import os
import sys
import pytest
from flask import Flask
from dotenv import load_dotenv
from app.routes.nutrition_routes import nutrition_bp  # Import your blueprint

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
load_dotenv()

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'DEBUG': False,
        'SERVER_NAME': 'localhost.localdomain',
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY')
    })
    
    # Register the nutrition blueprint
    app.register_blueprint(nutrition_bp, url_prefix='/')
    
    # Create application context
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    # Clean up
    ctx.pop()

@pytest.fixture(scope='session')
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def mock_openai_response():
    """Mock response for OpenAI API calls"""
    return {
        "food_item": "2 eggs",
        "nutrition_info": {
            "calories": "140",
            "protein": "12",
            "fat": {
                "total": "10",
                "saturated": "3"
            },
            "carbohydrates": "1",
            "sodium": "140",
            "potassium": "140"
        },
        "insight": "Good source of protein",
        "is_recipe": False,
        "is_valid_food": True
    }
    

    # Create application context
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    # Clean up
    ctx.pop()

@pytest.fixture(scope='session')
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def app_context(app):
    """Create an application context"""
    with app.app_context():
        yield
