"""Configuration for nutrition analysis"""

from typing import Dict, Any, Tuple

# Score weights for health calculation
NUTRIENT_WEIGHTS: Dict[str, float] = {
    'protein': 1.0,        # Important for nutrition
    'fiber': 0.8,          # Good for digestion
    'sugar': -1.0,         # Minimize sugar
    'added_sugar': -1.0,   # Limit added sugar
    'saturated': -0.8,     # Limit saturated fat
    'trans': -1.0,         # Most harmful fat - weighted as heavily as sugar
    'polyunsaturated': 0.4,# Good fat, moderate positive weight
    'monounsaturated': 0.4,# Good fat, moderate positive weight
    'fat': 0.2,            # Total fat - lower weight as individual fats are counted
    'carbohydrates': 0.4,  # Neutral/moderate importance
    'sodium': -0.6,        # Moderate sodium impact
    'calories': -0.2,      # Slightly negative (excess calories are discouraged)
    'potassium': 0.3,      # Important for heart health
    'calcium': 0.3,        # Important for bones
    'iron': 0.3,           # Important for blood
    'vitamin_a': 0.2,      # Good for eyes
    'vitamin_c': 0.2,      # Good for immune system
    'vitamin_d': 0.2       # Good for bones
}

# Healthy ranges for a single food item (per serving)
HEALTHY_RANGES: Dict[str, Tuple[float, float]] = {
    'calories': (100.0, 300.0),    # 100-300kcal per serving is good
    'protein': (5.0, 20.0),        # 5-20g per serving is healthy
    'fat': (3.0, 15.0),            # 3-15g per serving is reasonable
    'carbohydrates': (10.0, 30.0), # 10-30g per serving is balanced
    'fiber': (2.0, 8.0),           # 2-8g per serving is good
    'sugar': (0.0, 5.0),           # 0-5g per serving is acceptable
    'added_sugar': (0.0, 5.0),     # 0-5g per serving is acceptable
    'saturated': (0.0, 3.0),       # 0-3g per serving is acceptable
    'trans': (0.0, 0.5),           # 0-0.5g per serving is good
    'polyunsaturated': (1.0, 5.0), # 1-5g per serving is good
    'monounsaturated': (1.0, 5.0), # 1-5g per serving is good
    'sodium': (0.0, 400.0),        # 0-400mg per serving is moderate
    'potassium': (100.0, 450.0),   # 100-450mg per serving (good source)
    'calcium': (50.0, 200.0),      # 50-200mg per serving (good source)
    'iron': (2.0, 6.0),            # 2-6mg per serving is good (11-33% DV)
    'vitamin_a': (75.0, 300.0),    # 75-300mcg per serving is good (15-40% DV)
    'vitamin_c': (9.0, 30.0),      # 9-30mg per serving is good (10-33% DV)
    'vitamin_d': (2.0, 5.0)        # 2-5mcg per serving is good (10-25% DV)
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
    8.0: {'color': '#22c55e', 'message': 'Excellent nutritional value!'},
    6.0: {'color': '#3b82f6', 'message': 'Good nutritional value'},
    4.0: {'color': '#eab308', 'message': 'Moderate nutritional value'},
    0.0: {'color': '#ef4444', 'message': 'Limited nutritional value'}
}

# Default values for error cases
DEFAULT_SCORE: Dict[str, Any] = {
    'score': 5.0,
    'color': '#eab308',
    'message': 'Moderate nutritional value (limited data)'
}