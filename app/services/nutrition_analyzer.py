from typing import Dict, Optional
from app.models.nutrition_models import HealthScore
from app.utils.constants import NUTRIENT_RANGES

class NutritionAnalyzer:
    """
    Analyzes nutrition information and calculates health scores
    Uses predefined nutrient ranges for score calculation
    """

    IDEAL_RANGES = NUTRIENT_RANGES

    @staticmethod
    def _extract_numeric_value(value_str: str) -> Optional[float]:
        """
        Extracts numeric value from a string containing units
        Args:
            value_str: String containing numeric value with units
        Returns:
            Float value or None if extraction fails
        """
        try:
            # Extract numeric value from string (remove units)
            return float(''.join(c for c in value_str if c.isdigit() or c == '.'))
        except ValueError:
            return None

    @classmethod
    def calculate_health_score(cls, nutrition_info: Dict[str, str]) -> HealthScore:
        """
        Calculates health score based on nutrition information
        Args:
            nutrition_info: Dictionary containing nutrition values
        Returns:
            HealthScore object with score, message, and color
        """
        # Check if the food is valid first
        if not nutrition_info.get('is_valid_food', True):  # Default to True if not present
            return HealthScore(
                score=0,
                message="Invalid food item. Please enter a valid food.",
                color="#e74c3c"  # Red
            )

        total_score = 0
        total_weight = 0

        # Calculate score for each nutrient
        for nutrient, range_info in cls.IDEAL_RANGES.items():
            if nutrient in nutrition_info:
                value = cls._extract_numeric_value(nutrition_info[nutrient])
                if value is not None:
                    score = 0
                    if value < range_info['min']:
                        score = (value / range_info['min']) * 5
                    elif value > range_info['max']:
                        score = 5 * (range_info['max'] / value)
                    else:
                        score = 5 + ((value - range_info['min']) / 
                                   (range_info['max'] - range_info['min'])) * 5

                    total_score += score * abs(range_info['weight'])
                    total_weight += abs(range_info['weight'])

        # Calculate final score out of 10
        if total_weight == 0:
            final_score = 5  # Default middle score if no valid nutrients
        else:
            final_score = round((total_score / total_weight) * 2) / 2  # Round to nearest 0.5
            final_score = max(1, min(10, final_score))  # Ensure score is between 1 and 10

        return cls._get_health_score_details(final_score)

    @staticmethod
    def _get_health_score_details(score: float) -> HealthScore:
        if score >= 8:
            return HealthScore(
                score=score,
                message="Excellent choice! This food is highly nutritious.",
                color="#2ecc71"  # Green
            )
        elif score >= 6:
            return HealthScore(
                score=score,
                message="Good choice! This food has balanced nutrition.",
                color="#f1c40f"  # Yellow
            )
        elif score >= 4:
            return HealthScore(
                score=score,
                message="Moderate nutritional value. Consider balancing with other healthy foods.",
                color="#e67e22"  # Orange
            )
        else:
            return HealthScore(
                score=score,
                message="This food should be consumed in moderation as part of a balanced diet.",
                color="#e74c3c"  # Red
            ) 