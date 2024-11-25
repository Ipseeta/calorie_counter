VALID_UNITS = {
    "units",
    "plate",
    "grams",
    "ml",
    "bowl",
    "cup",
    "tbsp",
    "tsp"
}

NUTRIENT_RANGES = {
    'calories': {'min': 100, 'max': 500, 'weight': 1.5},
    'protein': {'min': 5, 'max': 30, 'weight': 2},
    'fat': {'min': 5, 'max': 20, 'weight': 1},
    'carbohydrates': {'min': 15, 'max': 60, 'weight': 1},
    'fiber': {'min': 3, 'max': 10, 'weight': 1.5},
    'sugar': {'min': 0, 'max': 10, 'weight': -1.5},
    'sodium': {'min': 0, 'max': 400, 'weight': -1}
} 