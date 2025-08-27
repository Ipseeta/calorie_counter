# 🥗 Calorie Counter App 

A smart Flask application that analyzes nutritional content, provides health scores, and suggests recipe videos for food items, with a special focus on Indian cuisine.

## ✨ Key Features

- 🔍 Instant nutrition analysis for any food item
- 💯 Smart health scoring system (1-10 scale)
- 🎯 Recipe video recommendations
- 🇮🇳 Indian cuisine specialization
- 📱 Mobile-friendly interface
- 🤖 AI-powered analysis using GPT-4o

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI/ML**: OpenAI GPT-4o
- **External APIs**: 
  - OpenAI API
  - YouTube Data API v3

## 🗂️ Project Structure
```
app/
├── constants/      # Constants
├── models/         # Data models
├── routes/         # API endpoints
├── services/       # Business logic
├── static/         # Frontend assets
└── templates/      # HTML templates
```

## 🚀 Quick Start

1. **Clone & Install**
```bash
git clone https://github.com/yourusername/calorie-counter.git
cd calorie-counter
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

4. Run the application:
```bash
python3 wsgi.py
```

## 🔌 API Reference

### Food Analysis
```http
POST /calculate_nutrition
Content-Type: application/json

{
  "food_item": "butter chicken",
  "quantity": 100,
  "unit": "g"
}
```

### Auto-Suggestions
```http
GET /get_food_suggestions
```

## 🎯 Health Score System

Our health score (1-10) considers:
- Protein content (+)
- Fiber content (+)
- Vitamins & minerals (+)
- Sugar content (-)
- Sodium levels (-)

Score interpretation:
- 8-10: Excellent 🟢
- 6-7.9: Good 🟡
- 4-5.9: Fair 🟠
- 1-3.9: Limited 🔴

## 🤝 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest pytest tests/test_nutrition_routes.py -v

# Run with verbose output
pytest -v

# Run specific test case
pytest tests/test_nutrition_routes.py::TestNutritionRoutes::test_analyze_real_chicken_breast -v
```

### Test Structure
```
tests/
├── __init__.py              # Test configurations and shared data
├── conftest.py             # Test fixtures
├── test_nutrition_routes.py # API endpoint tests
└── test_data/              # Test images and mock data
    └── images/
        ├── valid_food.jpg
        ├── chicken_breast.jpg
        └── invalid_format.txt
```

### Key Test Cases
- Food suggestion validation
- Nutrition calculation with various inputs
- Image analysis with real food images
- Error handling and validation
- API response structure verification


## 🤝 Contributing

1. Fork
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit (`git commit -m 'Add NewFeature'`)
4. Push (`git push origin feature/NewFeature`)
5. Open PR


## 🙏 Acknowledgments

- OpenAI team for GPT-4
- YouTube API team
- Flask community
