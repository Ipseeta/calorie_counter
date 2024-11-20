# Calorie Counter App

A Flask-based web application that provides nutritional information and health scores for food items, along with recipe videos when applicable.

## Features

- 🍎 Get detailed nutrition information for any food item
- 📊 Calculate health scores based on nutritional values
- 🎥 Find recipe videos for dishes
- 📱 Responsive design for mobile and desktop
- 🔍 Auto-suggestions for common Indian dishes
- 📈 Visual health score indicator

## Tech Stack

- **Backend**: Python/Flask
- **Frontend**: HTML, JavaScript, CSS
- **APIs**:
  - OpenAI GPT-4 for nutrition analysis
  - YouTube Data API for recipe videos
- **Dependencies**: See `requirements.txt`

## Project Structure

```
project/
app/
├── models/
│ └── nutrition_models.py # Data models using Pydantic
├── routes/
│ ├── nutrition_routes.py # API endpoint handlers
│ └── page_routes.py # Web page routes
├── services/
│ ├── nutrition_analyzer.py # Health score calculation
│ ├── openai_service.py # OpenAI integration
│ └── youtube_service.py # YouTube API integration
├── static/
│ └── js/
│ └── app.js # Frontend logic
└── templates/
└── index.html # Main application template
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/calorie-counter.git
cd calorie-counter
```

2. Install dependencies:
```bash
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


## 📡 API Endpoints

### Food Suggestions

### GET `/get_food_suggestions`
Returns a list of food suggestions for autocomplete functionality.

### Nutrition Calculation

### POST `/calculate_nutrition`
Calculate nutrition information for a food item.

**Request Body:**
```json
{
    "food_item": "string",
    "quantity": "number",
    "unit": "string"
}
```

**Response:**
```json
{
    "food_item": "string",
    "quantity": "number",
    "unit": "string",
    "nutrition_info": {
        "calories": "string",
        "protein": "string",
        ...
    },
    "health_score": {
        "score": "number",
        "message": "string",
        "color": "string"
    },
    "is_recipe": "boolean",
    "recipe_urls": [
        {
            "url": "string",
            "id": "string",
            "title": "string"
        }
    ]
}
```

## Health Score Calculation

The health score (1-10) is calculated based on:
- Caloric content
- Protein content
- Fat content
- Carbohydrates
- Fiber content
- Sugar content (negative impact)
- Sodium content (negative impact)

Score ranges:
- 8-10: Excellent nutritional value (Green)
- 6-7.9: Good nutritional value (Yellow)
- 4-5.9: Moderate nutritional value (Orange)
- 1-3.9: Limited nutritional value (Red)

## 🛡️ Error Handling

The application handles various error scenarios:

- Invalid input validation
- API service failures
- Data processing errors
- Network connectivity issues

Error responses follow the format:
```json
{
    "error": "string",
    "status_code": "number",
    "error_type": "string"
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI GPT-4o for nutrition analysis
- YouTube Data API for recipe videos
- Flask framework and its community

