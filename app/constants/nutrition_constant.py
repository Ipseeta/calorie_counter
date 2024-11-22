"""Configuration for nutrition analysis"""

from typing import Dict, Any

# Nutritional component weights (-1 to 1)
NUTRIENT_WEIGHTS: Dict[str, float] = {
    'protein': 0.15,
    'fiber': 0.15,
    'vitamins_minerals': 0.20,
    'healthy_fats': 0.10,
    'sugar': -0.15,
    'saturated_fat': -0.15,
    'sodium': -0.10
}

# Daily recommended values (in grams or mg)
DAILY_VALUES: Dict[str, float] = {
    'protein': 50,
    'fiber': 28,
    'sugar': 25,
    'saturated_fat': 20,
    'sodium': 2300,
}

# Vitamins and minerals to consider
MICRONUTRIENTS: list[str] = [
    'vitamin_a',
    'vitamin_c',
    'calcium',
    'iron'
]

# Score thresholds and their corresponding feedback
SCORE_FEEDBACK: Dict[float, Dict[str, str]] = {
    8.0: {
        'color': '#22c55e',
        'message': 'Excellent nutritional value!'
    },
    6.0: {
        'color': '#3b82f6',
        'message': 'Good nutritional value'
    },
    4.0: {
        'color': '#eab308',
        'message': 'Moderate nutritional value'
    },
    0.0: {
        'color': '#ef4444',
        'message': 'Limited nutritional value'
    }
}

# Default values for error cases
DEFAULT_SCORE: Dict[str, Any] = {
    'score': 5.0,
    'color': '#eab308',
    'message': 'Moderate nutritional value (limited data)'
} 