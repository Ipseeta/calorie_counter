# Nutrition Information and Recipe Finder

A Flask web application that provides nutritional information for food items and recipe videos for dishes. The application uses OpenAI's GPT-4 for accurate nutritional analysis and YouTube's API for recipe video suggestions.

## Features

- 🔍 Real-time food item search suggestions
- 📊 Detailed nutritional information including:
  - Calories
  - Protein
  - Fat
  - Carbohydrates
  - Fiber
- 🎥 Automatic recipe video suggestions for dishes
- 📱 Mobile-responsive design
- 💡 AI-powered insights about food items

## Technologies Used

- **Backend:**
  - Flask (Python web framework)
  - OpenAI GPT-4 API
  - YouTube Data API v3
  - Pydantic for data validation

- **Frontend:**
  - HTML5
  - CSS3
  - JavaScript (Vanilla)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/calorie_counter.git
cd calorie_counter
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

4. Run the application and access the API:
```bash
export FLASK_APP=app
flask run
```
Access the application at http://127.0.0.1:5000 in your web browser

## Usage

1. Enter a food item in the search box
2. Specify the quantity and unit of measurement
3. Click "Get Nutrition Info"
4. View the nutritional information and recipe videos (if available)

## API Endpoints

- `GET /`: Main application page
- `GET /get_food_suggestions`: Returns food suggestions for autocomplete
- `POST /calculate_nutrition`: Calculates nutritional information for a given food item

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the GPT-4 API
- YouTube Data API for recipe video integration
- Flask community for the excellent web framework
