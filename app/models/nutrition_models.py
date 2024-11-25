from pydantic import BaseModel
from typing import List, Optional

class FatDetails(BaseModel):
    total: Optional[str]
    saturated: Optional[str]
    trans: Optional[str]
    polyunsaturated: Optional[str]
    monounsaturated: Optional[str]

class CarbohydrateDetails(BaseModel):
    total: Optional[str]
    sugar: Optional[str]
    added_sugar: Optional[str]

class NutritionScores(BaseModel):
    """Model for nutrition information including macros and micronutrients"""
    calories: str
    protein: str
    fat: FatDetails
    carbohydrates: CarbohydrateDetails
    fiber: str
    sugar: str
    sodium: str
    vitamin_a: str
    vitamin_c: str
    vitamin_d: str
    calcium: str
    iron: str
    potassium: str
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