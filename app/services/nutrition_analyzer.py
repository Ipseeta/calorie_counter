from typing import Dict, Any
from dataclasses import dataclass
from flask import current_app
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
    DAILY_SODIUM_LIMIT = 2300  # mg
    DAILY_SATURATED_FAT_LIMIT = 20  # g (example value)
    @classmethod
    def calculate_health_score(cls, nutrition_info: Dict[str, Any]) -> HealthScore:
        """
        Calculate health score with a refined scoring system (1-10 scale).
        Better balance between positive nutrients and penalties.
        """
        try:
            score = 5.5  # Start with a neutral score

            # Positive attributes (up to +4.2 points)
            score += cls._get_protein_score(nutrition_info)  # Max 1.5 points
            score += cls._get_fiber_score(nutrition_info)  # Max 1.0 points
            if cls._has_vitamins_minerals(nutrition_info):
                score += 0.7  # Vitamins and minerals
            if cls._is_balanced_meal(nutrition_info):
                score += 1.0  # Balanced macronutrients

            # Penalties (up to -3.5 points max)
            score -= cls._get_sugar_penalty(nutrition_info)  # Scaled penalty
            score -= cls._get_sodium_penalty(nutrition_info)  # Scaled penalty
            score -= cls._get_saturated_fat_penalty(nutrition_info)  # Scaled penalty
            if cls._is_calorie_dense_with_low_nutrients(nutrition_info):
                score -= 0.5  # Minor penalty for poor nutrient density

            # Ensure score is within bounds (1-10)
            final_score = max(1, min(10, score))
            feedback = cls._get_score_feedback(final_score)

            return HealthScore(
                score=round(final_score, 1),
                color=feedback['color'],
                message=feedback['message']
            )

        except Exception as e:
            current_app.logger.error(f"Error calculating health score: {e}")
            return HealthScore(**DEFAULT_SCORE)

    @classmethod
    def _get_protein_score(cls, nutrition_info: Dict[str, Any]) -> float:
        """Scale protein contribution up to 1.5 points."""
        protein = cls._get_nutrient_value(nutrition_info, 'protein')
        return min(protein / (DAILY_VALUES['protein'] * 0.15), 1.5)

    @classmethod
    def _get_fiber_score(cls, nutrition_info: Dict[str, Any]) -> float:
        """Scale fiber contribution up to 1.0 points."""
        fiber = cls._get_nutrient_value(nutrition_info, 'fiber')
        return min(fiber / (DAILY_VALUES['fiber'] * 0.1), 1.0)

    @classmethod
    def _get_sugar_penalty(cls, nutrition_info: Dict[str, Any]) -> float:
        """Gradually scale penalty for sugar."""
        sugar = cls._get_nutrient_value(nutrition_info, 'sugar')
        if sugar > DAILY_VALUES['sugar'] * 0.5:
            return min((sugar - DAILY_VALUES['sugar'] * 0.5) / (DAILY_VALUES['sugar'] * 0.5), 1.5)
        return 0.0

    @classmethod
    def _get_sodium_penalty(cls, nutrition_info: Dict[str, Any]) -> float:
        """Gradually scale penalty for sodium."""
        sodium = cls._get_nutrient_value(nutrition_info, 'sodium')
        if sodium > cls.DAILY_SODIUM_LIMIT * 0.5:
            return min((sodium - cls.DAILY_SODIUM_LIMIT * 0.5) / (cls.DAILY_SODIUM_LIMIT * 0.5), 1.5)
        return 0.0

    @classmethod
    def _get_saturated_fat_penalty(cls, nutrition_info: Dict[str, Any]) -> float:
        """Gradually scale penalty for saturated fats."""
        sat_fats = cls._get_nutrient_value(nutrition_info, 'saturated_fats')
        if sat_fats > cls.DAILY_SATURATED_FAT_LIMIT * 0.1:
            return min((sat_fats - cls.DAILY_SATURATED_FAT_LIMIT * 0.1) / (cls.DAILY_SATURATED_FAT_LIMIT * 0.1), 1.0)
        return 0.0

    @classmethod
    def _is_calorie_dense_with_low_nutrients(cls, nutrition_info: Dict[str, Any]) -> bool:
        """Identify calorie-dense foods with low positive nutrient contributions."""
        calories = cls._get_nutrient_value(nutrition_info, 'calories')
        positive_contributions = sum([
            cls._get_protein_score(nutrition_info) > 0,
            cls._get_fiber_score(nutrition_info) > 0,
            cls._has_vitamins_minerals(nutrition_info)
        ])
        return calories > 400 and positive_contributions < 2

    @classmethod
    def _get_nutrient_value(cls, nutrition_info: Dict[str, Any], nutrient: str) -> float:
        """Extract numeric value for a nutrient or return 0."""
        if nutrient in nutrition_info:
            try:
                return cls._extract_numeric_value(nutrition_info[nutrient])
            except ValueError:
                current_app.logger.warning(f"Invalid numeric value for {nutrient}: {nutrition_info[nutrient]}")
        return 0.0

    @staticmethod
    def _extract_numeric_value(value_str: str) -> float:
        """Extract numeric value from string with unit (e.g., '15g' -> 15)."""
        try:
            return float(''.join(char for char in value_str if char.isdigit() or char == '.'))
        except ValueError:
            current_app.logger.warning(f"Failed to parse numeric value from '{value_str}'")
            return 0.0

    @staticmethod
    def _get_score_feedback(score: float) -> Dict[str, str]:
        """Get color and message feedback based on score."""
        for threshold, feedback in sorted(SCORE_FEEDBACK.items(), key=lambda x: x[0], reverse=True):
            if score >= threshold:
                return feedback
        return SCORE_FEEDBACK[0.0]  # Default to lowest threshold

    @classmethod
    def _has_vitamins_minerals(cls, nutrition_info: Dict[str, Any]) -> bool:
        """Check if food item contains significant vitamins or minerals."""
        for nutrient in MICRONUTRIENTS:
            if cls._get_nutrient_value(nutrition_info, nutrient) > 0:
                return True
        return False

    @classmethod
    def _is_balanced_meal(cls, nutrition_info: Dict[str, Any]) -> bool:
        """Check if the meal has balanced macronutrients."""
        protein = cls._get_nutrient_value(nutrition_info, 'protein')
        carbs = cls._get_nutrient_value(nutrition_info, 'carbohydrates')
        fats = cls._get_nutrient_value(nutrition_info, 'fats')
        
        # Check if all macronutrients are present in reasonable amounts
        return all([
            protein >= 5,  # At least 5g protein
            carbs >= 10,   # At least 10g carbs
            fats >= 3      # At least 3g fats
        ])