from typing import Dict, Any
from dataclasses import dataclass
from flask import current_app
from app.constants.nutrition_constant import (
    NUTRIENT_WEIGHTS,
    MICRONUTRIENTS,
    SCORE_FEEDBACK,
    DEFAULT_SCORE,
    HEALTHY_RANGES
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
        Calculate health score with a refined scoring system (1-10 scale).
        Better balance between positive nutrients and penalties.
        """
        total_score = 0
        counted_nutrients = 0
        try:
            excluded_fields = {'is_valid_food', 'insight', 'is_recipe'}
            
            for nutrient, value in {k: v for k, v in nutrition_info.items() if k not in excluded_fields}.items():
                if isinstance(value, dict):
                    # Handle nested objects (e.g., carbohydrates and fat)
                    for sub_nutrient, sub_value in value.items():
                        if sub_nutrient in HEALTHY_RANGES:
                            min_val, max_val = HEALTHY_RANGES[sub_nutrient]
                            weight = NUTRIENT_WEIGHTS[sub_nutrient]
                            value = cls._get_nutrient_value({sub_nutrient: sub_value}, sub_nutrient)
                            nutrient_score = cls._calculate_nutrient_score(sub_nutrient, value, min_val, max_val, weight, nutrition_info)
                            
                            total_score += nutrient_score * abs(weight)
                            counted_nutrients += abs(weight)
                else:
                    if nutrient in HEALTHY_RANGES:
                        min_val, max_val = HEALTHY_RANGES[nutrient]
                        weight = NUTRIENT_WEIGHTS[nutrient]
                        value = cls._get_nutrient_value({nutrient: value}, nutrient)
                        nutrient_score = cls._calculate_nutrient_score(nutrient, value, min_val, max_val, weight, nutrition_info)
                        
                        total_score += nutrient_score * abs(weight)
                        counted_nutrients += abs(weight)

            if counted_nutrients == 0:
                return HealthScore(**DEFAULT_SCORE)
            
            final_score = round(total_score / counted_nutrients, 1)
            feedback = cls._get_score_feedback(final_score)
            return HealthScore(
                score=final_score,
                color=feedback['color'],
                message=feedback['message']
            )
        except Exception as e:
            current_app.logger.error(f"Error calculating health score: {str(e)}")
            return HealthScore(**DEFAULT_SCORE)

    @classmethod
    def _calculate_nutrient_score(cls, nutrient: str, value: float, min_val: float, max_val: float, weight: float, nutrition_info: Dict[str, Any]) -> float:
        """Calculate score for a single nutrient."""
        # First check if it's a fruit for special handling
        is_fruit = not nutrition_info['is_recipe']
        
        if weight > 0:  # Positive nutrients
            if value < min_val:
                if is_fruit:
                    if nutrient in {'protein', 'fat', 'carbohydrates'}:
                        return 8.0  # Base score for fruits' naturally low macros
                    elif nutrient in {'fiber', 'vitamin_c', 'potassium'}:
                        return max(8.0, (value / min_val) * 10)  # Higher base for key fruit nutrients
                elif cls._is_nutrient_dense(nutrition_info):
                    return max(7.0, (value / min_val) * 10)
                return max((value / min_val) * 6, 1)
            elif value > max_val:
                if is_fruit and nutrient in {'fiber', 'vitamin_c', 'potassium'}:
                    return 8.0  # Good score for abundant nutrients
                return max(6 * (max_val / value), 1)
            else:
                base_score = 5 + ((value - min_val) / (max_val - min_val) * 5)
                # Boost score for fruits meeting fiber/vitamin targets
                if is_fruit and nutrient in {'fiber', 'vitamin_c', 'potassium'}:
                    return min(base_score * 1.5, 10)  # 50% boost for key fruit nutrients
                return base_score
        else:  # Negative nutrients
            if value < min_val:
                return 10
            elif value > max_val:
                if nutrient in {'sugar', 'carbohydrates'} and is_fruit:
                    return 8.5  # Very light penalty for natural fruit sugars/carbs
                ratio = value / max_val
                if ratio > 2:
                    return max(1, 3 * (max_val / value))
                return max(2, 5 * (max_val / value))
            else:
                if nutrient in {'sugar', 'carbohydrates'} and is_fruit:
                    return 9.0  # Almost no penalty for natural fruit sugars within range
                return 10 - ((value - min_val) / (max_val - min_val) * 8)

    @classmethod
    def _is_nutrient_dense(cls, nutrition_info: Dict[str, Any]) -> bool:
        """Check if food is nutrient-dense relative to its calories"""
        calories = cls._get_nutrient_value(nutrition_info, 'calories')
        if calories == 0:
            return False
            
        protein = cls._get_nutrient_value(nutrition_info, 'protein')
        vitamins_present = cls._has_vitamins_minerals(nutrition_info)
        sodium = cls._get_nutrient_value(nutrition_info, 'sodium')
        
        # Check protein density and presence of micronutrients
        protein_density = (protein * 4 / calories) if calories > 0 else 0
        has_good_protein = protein_density > 0.15  # More than 15% protein calories
        has_reasonable_sodium = sodium <= 400
        
        return has_good_protein and vitamins_present and has_reasonable_sodium

    @classmethod
    def _is_quality_protein(cls, nutrition_info: Dict[str, Any]) -> bool:
        """Check if it's a quality protein source with good nutrient density"""
        protein = cls._get_nutrient_value(nutrition_info, 'protein')
        calories = cls._get_nutrient_value(nutrition_info, 'calories')
        sodium = cls._get_nutrient_value(nutrition_info, 'sodium')
        
        # Check protein content, protein-to-calorie ratio, and sodium level
        has_good_protein = protein > 5
        has_good_protein_ratio = (protein * 4 / calories > 0.15) if calories > 0 else False
        has_reasonable_sodium = sodium <= 400  # Not excessive sodium
        
        return has_good_protein and has_good_protein_ratio and has_reasonable_sodium

    @classmethod
    def _is_protein_rich(cls, nutrition_info: Dict[str, Any]) -> bool:
        """Check if food is a good protein source (>5g per serving) and has good protein quality"""
        protein = cls._get_nutrient_value(nutrition_info, 'protein')
        calories = cls._get_nutrient_value(nutrition_info, 'calories')
        
        # Check both absolute protein content and protein-to-calorie ratio
        return protein > 5 and (protein * 4 / calories > 0.15 if calories > 0 else False)

    @classmethod
    def _get_nutrient_value(cls, nutrition_info: Dict[str, Any], nutrient: str) -> float:
        """Extract numeric value from nutrient string, handling nested objects."""
        try:
            value = nutrition_info.get(nutrient)
            
            # Handle nested objects (carbohydrates and fat)
            if isinstance(value, dict):
                value = value.get('total', '0g')
            
            # Convert string to float, removing unit
            return float(''.join(filter(str.isdigit, str(value))) or 0)
        except (ValueError, TypeError, AttributeError):
            current_app.logger.warning(f"Failed to parse numeric value for {nutrient}: '{value}'")
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
        
        return all([
            protein >= 5,  # At least 5g protein
            carbs >= 10,   # At least 10g carbs
            fats >= 3      # At least 3g fats
        ])