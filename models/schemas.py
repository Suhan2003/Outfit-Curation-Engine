from enum import Enum
from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

class BodyType(str, Enum):
    TRIANGLE = "triangle"
    RECTANGLE = "rectangle"
    HOURGLASS = "hourglass"
    INVERTED_TRIANGLE = "inverted_triangle"
    OVAL = "oval"

class SkinTone(str, Enum):
    FAIR = "fair"
    LIGHT = "light"
    MEDIUM = "medium"
    OLIVE = "olive"
    TAN = "tan"
    BROWN = "brown"
    DARK = "dark"

class OccasionType(str, Enum):
    CASUAL = "casual"
    BUSINESS = "business"
    FORMAL = "formal"
    PARTY = "party"
    GLAMOROUS = "glamorous"

class WeatherCondition(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COOL = "cool"
    COLD = "cold"
    RAINY = "rainy"

class ItemCategory(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    DRESS = "dress"
    OUTERWEAR = "outerwear"
    SHOES = "shoes"
    ACCESSORY = "accessory"

class FitType(str, Enum):
    SLIM = "slim"
    REGULAR = "regular"
    WIDE_LEG = "wide_leg"
    FITTED = "fitted"
    STRUCTURED = "structured"
    RELAXED = "relaxed"
    OVERSIZED = "oversized"
    SKINNY = "skinny"
    STRAIGHT = "straight"
    BOOT_CUT = "boot_cut"
    A_LINE = "a_line"

class Color(str, Enum):
    BLACK = "black"
    WHITE = "white"
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    PURPLE = "purple"
    PINK = "pink"
    ORANGE = "orange"
    BROWN = "brown"
    GRAY = "gray"
    NAVY = "navy"
    BEIGE = "beige"
    CREAM = "cream"
    PATTERNED = "patterned"

class UserInfo(BaseModel):
    user_id: str
    body_type: BodyType
    skin_tone: SkinTone
    height_cm: float
    weight_kg: Optional[float] = None
    shoulder_cm: Optional[float] = None
    bust_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    preferences: Optional[Dict[str, List[str]]] = None

class OccasionInfo(BaseModel):
    occasion_type: OccasionType
    weather: WeatherCondition
    time_of_day: str
    location: Optional[str] = None
    formality_level: int = Field(ge=1, le=5)

class ClothingItem(BaseModel):
    item_id: str
    category: ItemCategory
    subcategory: str
    color: Color
    pattern: Optional[str] = None
    fabric: str
    weight: str
    fit: FitType
    brand: Optional[str] = None
    size: str
    attributes: Dict[str, Union[str, List[str]]]
    image_url: Optional[str] = None
    created_at: datetime

class Outfit(BaseModel):
    outfit_id: str
    items: List[ClothingItem]
    occasion_type: OccasionType
    compatibility_score: float
    style_notes: List[str]
    created_at: datetime

class OutfitRequest(BaseModel):
    user_info: UserInfo
    occasion_info: OccasionInfo
    inventory: List[ClothingItem]
    max_outfits: int = 5