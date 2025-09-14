from typing import List, Dict, Set
from models.schemas import *
import numpy as np

class RuleEngine:
    def __init__(self):
        self.body_type_rules = self._load_body_type_rules()
        self.occasion_rules = self._load_occasion_rules()
        self.proportion_rules = self._load_proportion_rules()
    
    def _load_body_type_rules(self) -> Dict[BodyType, Dict]:
        return {
            BodyType.TRIANGLE: {
                "top_fit": [FitType.FITTED, FitType.STRUCTURED],
                "bottom_fit": [FitType.STRAIGHT, FitType.BOOT_CUT],
                "dress_fit": [FitType.A_LINE],
                "recommended_colors": {
                    "top": [Color.PATTERNED, Color.RED, Color.BLUE, Color.GREEN],
                    "bottom": [Color.BLACK, Color.NAVY, Color.GRAY, Color.BROWN]
                },
                "avoid_fits": {
                    "top": [FitType.OVERSIZED, FitType.RELAXED],
                    "bottom": [FitType.SKINNY]
                },
                "fabric_weight": {
                    "top": ["light", "medium"],
                    "bottom": ["medium"]
                }
            },
            BodyType.INVERTED_TRIANGLE: {
                "top_fit": [FitType.RELAXED],
                "bottom_fit": [FitType.A_LINE, FitType.WIDE_LEG],
                "dress_fit": [FitType.A_LINE],
                "recommended_colors": {
                    "top": [Color.BLACK, Color.NAVY, Color.GRAY],
                    "bottom": [Color.PATTERNED, Color.RED, Color.BLUE]
                },
                "avoid_fits": {
                    "top": [FitType.STRUCTURED],
                    "bottom": [FitType.SKINNY, FitType.STRAIGHT]
                },
                "fabric_weight": {
                    "top": ["light"],
                    "bottom": ["medium", "heavy"]
                }
            },
            BodyType.RECTANGLE: {
                "top_fit": [FitType.FITTED, FitType.STRUCTURED],
                "bottom_fit": [FitType.A_LINE, FitType.BOOT_CUT],
                "dress_fit": [FitType.A_LINE],
                "recommended_colors": {
                    "top": [Color.PATTERNED, Color.RED, Color.BLUE],
                    "bottom": [Color.PATTERNED, Color.GREEN, Color.PURPLE]
                },
                "avoid_fits": {
                    "top": [FitType.OVERSIZED],
                    "bottom": [FitType.SKINNY]
                },
                "fabric_weight": {
                    "top": ["light", "medium"],
                    "bottom": ["medium"]
                }
            }
        }
    
    def _load_occasion_rules(self) -> Dict[OccasionType, Dict]:
        return {
            OccasionType.CASUAL: {
                "allowed_fits": [FitType.RELAXED, FitType.STRAIGHT],
                "fabric_weights": ["light", "medium"],
                "color_intensity": "medium",
                "pattern_intensity": "medium"
            },
            OccasionType.BUSINESS: {
                "allowed_fits": [FitType.STRUCTURED, FitType.FITTED],
                "fabric_weights": ["medium"],
                "color_intensity": "low",
                "pattern_intensity": "low"
            },
            OccasionType.PARTY: {
                "allowed_fits": [FitType.FITTED, FitType.STRUCTURED],
                "fabric_weights": ["light", "medium"],
                "color_intensity": "high",
                "pattern_intensity": "high"
            }
        }
    
    def _load_proportion_rules(self) -> Dict:
        return {
            "rule_of_3": True,
            "top_bottom_balance": True,
            "feature_emphasis": True
        }
    
    def filter_by_body_type(self, items: List[ClothingItem], body_type: BodyType) -> List[ClothingItem]:
        """Filter items based on body type rules"""
        filtered_items = []
        rules = self.body_type_rules.get(body_type, {})
        
        for item in items:
            if self._is_item_compatible(item, rules):
                filtered_items.append(item)
        
        return filtered_items
    
    def _is_item_compatible(self, item: ClothingItem, rules: Dict) -> bool:
        """Check if an item is compatible with given rules"""
        # Check fit compatibility
        if item.category in [ItemCategory.TOP, ItemCategory.DRESS, ItemCategory.OUTERWEAR]:
            if "avoid_fits" in rules and item.fit in rules["avoid_fits"].get("top", []):
                return False
            if "top_fit" in rules and item.fit not in rules["top_fit"]:
                return False
        
        if item.category == ItemCategory.BOTTOM:
            if "avoid_fits" in rules and item.fit in rules["avoid_fits"].get("bottom", []):
                return False
            if "bottom_fit" in rules and item.fit not in rules["bottom_fit"]:
                return False
        
        # Check color compatibility
        if "recommended_colors" in rules:
            if item.category in [ItemCategory.TOP, ItemCategory.DRESS, ItemCategory.OUTERWEAR]:
                if item.color not in rules["recommended_colors"].get("top", []):
                    return False
            elif item.category == ItemCategory.BOTTOM:
                if item.color not in rules["recommended_colors"].get("bottom", []):
                    return False
        
        # Check fabric weight
        if "fabric_weight" in rules:
            if item.category in [ItemCategory.TOP, ItemCategory.DRESS]:
                if item.weight not in rules["fabric_weight"].get("top", []):
                    return False
            elif item.category == ItemCategory.BOTTOM:
                if item.weight not in rules["fabric_weight"].get("bottom", []):
                    return False
        
        return True
    
    def filter_by_occasion(self, items: List[ClothingItem], occasion: OccasionInfo) -> List[ClothingItem]:
        """Filter items based on occasion rules"""
        filtered_items = []
        rules = self.occasion_rules.get(occasion.occasion_type, {})
        
        for item in items:
            if self._is_item_occasion_compatible(item, rules, occasion):
                filtered_items.append(item)
        
        return filtered_items
    
    def _is_item_occasion_compatible(self, item: ClothingItem, rules: Dict, occasion: OccasionInfo) -> bool:
        """Check if item is suitable for the occasion"""
        # Check fit
        if "allowed_fits" in rules and item.fit not in rules["allowed_fits"]:
            return False
        
        # Check fabric weight based on weather
        if occasion.weather == WeatherCondition.HOT and item.weight == "heavy":
            return False
        if occasion.weather == WeatherCondition.COLD and item.weight == "light":
            return False
        
        # Check formality level
        if occasion.occasion_type == OccasionType.BUSINESS and item.category == ItemCategory.TOP:
            if item.subcategory not in ["shirt", "blouse", "button-down"]:
                return False
        
        return True
    
    def score_outfit_proportions(self, outfit: List[ClothingItem], user_info: UserInfo) -> float:
        """Score outfit based on proportion rules"""
        score = 1.0
        
        # Rule of 3s - count distinct elements
        elements = set()
        for item in outfit:
            if item.pattern:
                elements.add(f"pattern_{item.pattern}")
            if item.color != Color.PATTERNED:
                elements.add(f"color_{item.color}")
            elements.add(f"category_{item.category}")
        
        if len(elements) < 3:
            score *= 0.7  # Penalize for insufficient elements
        
        # Top vs bottom balance
        tops = [item for item in outfit if item.category in [ItemCategory.TOP, ItemCategory.DRESS, ItemCategory.OUTERWEAR]]
        bottoms = [item for item in outfit if item.category == ItemCategory.BOTTOM]
        
        if tops and bottoms:
            top_volume = self._estimate_volume(tops[0], user_info)
            bottom_volume = self._estimate_volume(bottoms[0], user_info)
            
            # Avoid matching wide tops with wide bottoms
            if top_volume > 0.7 and bottom_volume > 0.7:
                score *= 0.6
            # Good balance: wide top with narrow bottom or vice versa
            elif abs(top_volume - bottom_volume) > 0.3:
                score *= 1.2
        
        return score
    
    def _estimate_volume(self, item: ClothingItem, user_info: UserInfo) -> float:
        """Estimate visual volume of an item (0-1 scale)"""
        volume = 0.5  # Base volume
        
        # Adjust based on fit
        if item.fit in [FitType.OVERSIZED, FitType.RELAXED]:
            volume += 0.3
        elif item.fit in [FitType.FITTED, FitType.SKINNY]:
            volume -= 0.3
        
        # Adjust based on fabric weight
        if item.weight == "heavy":
            volume += 0.2
        elif item.weight == "light":
            volume -= 0.2
        
        return max(0.1, min(0.9, volume))