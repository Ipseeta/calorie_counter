from typing import Dict, Any
from dataclasses import dataclass
from app.constants.nutrition_constant import (
    NUTRIENT_WEIGHTS,
    DAILY_VALUES,
    MICRONUTRIENTS,
    SCORE_FEEDBACK,
    DEFAULT_SCORE
)

@dataclass
class HealthScore:
    score: float
    color: str
    message: str

class NutritionAnalyzer:
    @classmethod
    def calculate_health_score(cls, nutrition_info: Dict[str, Any]) -> HealthScore:
        """
        Calculate health score based on nutritional values (1-10 scale).
        A higher score indicates better nutritional value.
        """
        try:
            score = 5.0  # Start at neutral score
            
            # Basic nutrient checks (up to +3 points)
            if cls._has_good_protein(nutrition_info):
                score += 1.0
            if cls._has_good_fiber(nutrition_info):
                score += 1.0
            if cls._has_vitamins_minerals(nutrition_info):
                score += 1.0
            
            # Penalty checks (up to -3 points)
            if cls._has_high_sugar(nutrition_info):
                score -= 1.5
            if cls._has_high_sodium(nutrition_info):
                score -= 1.5
            
            # Ensure score stays within 1-10 range
            final_score = max(1, min(10, score))
            feedback = cls._get_score_feedback(final_score)
            
            return HealthScore(
                score=round(final_score, 1),
                color=feedback['color'],
                message=feedback['message']
            )
            
        except Exception as e:
            return HealthScore(**DEFAULT_SCORE)

    @classmethod
    def _has_good_protein(cls, nutrition_info: Dict[str, Any]) -> bool:
        """Check if protein content is good (>15% of daily value)"""
        if 'protein' in nutrition_info:
            protein = cls._extract_numeric_value(nutrition_info['protein'])
            return protein > DAILY_VALUES['protein'] * 0.15
        return False

    @classmethod
    def _has_good_fiber(cls, nutrition_info: Dict[str, Any]) -> bool:
        """Check if fiber content is good (>15% of daily value)"""
        if 'fiber' in nutrition_info:
            fiber = cls._extract_numeric_value(nutrition_info['fiber'])
            return fiber > DAILY_VALUES['fiber'] * 0.15
        return False

    @classmethod
    def _has_vitamins_minerals(cls, nutrition_info: Dict[str, Any]) -> bool:
        """Check if food has significant vitamins/minerals (>15% in any)"""
        for nutrient in MICRONUTRIENTS:
            if nutrient in nutrition_info:
                try:
                    percentage = float(nutrition_info[nutrient].strip('%'))
                    if percentage > 15:
                        return True
                except (ValueError, AttributeError):
                    continue
        return False

    @classmethod
    def _has_high_sugar(cls, nutrition_info: Dict[str, Any]) -> bool:
        """Check if sugar content is high (>30% of daily value)"""
        if 'sugar' in nutrition_info:
            sugar = cls._extract_numeric_value(nutrition_info['sugar'])
            return sugar > DAILY_VALUES['sugar'] * 0.3
        return False

    @classmethod
    def _has_high_sodium(cls, nutrition_info: Dict[str, Any]) -> bool:
        """Check if sodium content is high (>30% of daily value)"""
        if 'sodium' in nutrition_info:
            sodium = cls._extract_numeric_value(nutrition_info['sodium'])
            return sodium > 2300 * 0.3  # 2300mg is typical daily limit
        return False

    @staticmethod
    def _extract_numeric_value(value_str: str) -> float:
        """Extract numeric value from string with unit (e.g., "15g" -> 15)"""
        return float(''.join(char for char in value_str if char.isdigit() or char == '.'))

    @staticmethod
    def _get_score_feedback(score: float) -> Dict[str, str]:
        """Get color and message feedback based on score"""
        for threshold, feedback in sorted(
            SCORE_FEEDBACK.items(),
            key=lambda x: x[0],
            reverse=True
        ):
            if score >= threshold:
                return feedback
        return SCORE_FEEDBACK[0.0]  # Default to lowest threshold 