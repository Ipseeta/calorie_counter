from pydantic import BaseModel
from typing import List

class NutritionScores(BaseModel):
    """Model for nutrition information including macros and micronutrients"""
    calories: str
    protein: str
    fat: str
    carbohydrates: str
    fiber: str
    sugar: str
    sodium: str
    vitamin_a: str
    vitamin_c: str
    calcium: str
    iron: str
    is_recipe: bool
    is_valid_food: bool
    insight: str

class FoodSuggestions(BaseModel):
    """Model for food suggestions response"""
    suggestions: List[str]

class VideoInfo(BaseModel):
    """Model for YouTube video information"""
    url: str
    id: str
    title: str 

class HealthScore(BaseModel):
    """Model for health score calculation results"""
    score: float
    message: str
    color: str

class FoodItem(BaseModel):
    """Model for food item information"""
    food_item: str
    quantity: float
    unit: str