from typing import List, Dict, Set, Tuple
import random
import numpy as np
from models.schemas import *
from services.rule_engine import RuleEngine

class OutfitGenerator:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.max_generation_attempts = 1000
    
    def generate_outfits(self, request: OutfitRequest) -> List[Outfit]:
        """Generate outfits based on user, occasion, and inventory"""
        # Step 1: Filter inventory by body type and occasion
        filtered_items = self.rule_engine.filter_by_body_type(
            request.inventory, request.user_info.body_type
        )
        filtered_items = self.rule_engine.filter_by_occasion(
            filtered_items, request.occasion_info
        )
        
        # Step 2: Categorize items
        categorized_items = self._categorize_items(filtered_items)
        
        # Step 3: Generate outfit combinations
        outfits = []
        attempt = 0
        
        while len(outfits) < request.max_outfits and attempt < self.max_generation_attempts:
            attempt += 1
            
            # Create a candidate outfit
            candidate = self._create_candidate_outfit(categorized_items, request.user_info)
            
            if candidate and self._is_valid_outfit(candidate, request):
                # Score the outfit
                rule_score = self.rule_engine.score_outfit_proportions(candidate, request.user_info)
                ml_score = self._predict_ml_compatibility([
                    self._item_to_dict(item) for item in candidate
                ])
                
                # Combine scores (weighted average)
                final_score = 0.6 * rule_score + 0.4 * ml_score
                
                outfit = Outfit(
                    outfit_id=f"outfit_{len(outfits) + 1}",
                    items=candidate,
                    occasion_type=request.occasion_info.occasion_type,
                    compatibility_score=final_score,
                    style_notes=self._generate_style_notes(candidate, request.user_info),
                    created_at=datetime.now()
                )
                
                outfits.append(outfit)
        
        # Sort by score and return
        outfits.sort(key=lambda x: x.compatibility_score, reverse=True)
        return outfits[:request.max_outfits]
    
    def _categorize_items(self, items: List[ClothingItem]) -> Dict[str, List[ClothingItem]]:
        """Categorize items by type"""
        categorized = {
            'tops': [],
            'bottoms': [],
            'dresses': [],
            'outerwear': [],
            'shoes': [],
            'accessories': []
        }
        
        for item in items:
            if item.category == ItemCategory.TOP:
                categorized['tops'].append(item)
            elif item.category == ItemCategory.BOTTOM:
                categorized['bottoms'].append(item)
            elif item.category == ItemCategory.DRESS:
                categorized['dresses'].append(item)
            elif item.category == ItemCategory.OUTERWEAR:
                categorized['outerwear'].append(item)
            elif item.category == ItemCategory.SHOES:
                categorized['shoes'].append(item)
            elif item.category == ItemCategory.ACCESSORY:
                categorized['accessories'].append(item)
        
        return categorized
    
    def _create_candidate_outfit(self, categorized_items: Dict, user_info: UserInfo) -> List[ClothingItem]:
        """Create a candidate outfit from categorized items"""
        candidate = []
        
        # Decide outfit type: dress or top+bottom
        use_dress = random.random() < 0.3 and categorized_items['dresses']
        
        if use_dress:
            # Select a dress
            dress = random.choice(categorized_items['dresses'])
            candidate.append(dress)
        else:
            # Select top and bottom
            if categorized_items['tops'] and categorized_items['bottoms']:
                top = random.choice(categorized_items['tops'])
                bottom = random.choice(categorized_items['bottoms'])
                candidate.extend([top, bottom])
            else:
                return None
        
        # Add outerwear (optional)
        if categorized_items['outerwear'] and random.random() < 0.4:
            outerwear = random.choice(categorized_items['outerwear'])
            candidate.append(outerwear)
        
        # Add shoes
        if categorized_items['shoes']:
            shoes = random.choice(categorized_items['shoes'])
            candidate.append(shoes)
        
        # Add accessories (optional, 1-2 items)
        if categorized_items['accessories']:
            num_accessories = random.randint(1, 2)
            accessories = random.sample(categorized_items['accessories'], 
                                      min(num_accessories, len(categorized_items['accessories'])))
            candidate.extend(accessories)
        
        return candidate
    
    def _is_valid_outfit(self, outfit: List[ClothingItem], request: OutfitRequest) -> bool:
        """Check if outfit is valid"""
        # Basic checks
        if not outfit:
            return False
        
        # Check for required categories
        categories = {item.category for item in outfit}
        if (ItemCategory.TOP in categories and ItemCategory.BOTTOM in categories) or \
           (ItemCategory.DRESS in categories):
            return True
        
        return False
    
    def _item_to_dict(self, item: ClothingItem) -> Dict:
        """Convert ClothingItem to dictionary for ML model"""
        return {
            'color': item.color.value,
            'category': item.category.value,
            'pattern': item.pattern or 'none',
            'formality_level': self._estimate_formality_level(item),
            'color_intensity': self._estimate_color_intensity(item.color),
            'pattern_intensity': 0.8 if item.pattern else 0.2
        }
    
    def _predict_ml_compatibility(self, items: List[Dict]) -> float:
        """Predict compatibility using a simple heuristic (replace with actual ML model)"""
        # This is a placeholder - in a real implementation, you would use a trained model
        color_score = 0.7
        category_score = 0.8
        formality_score = 0.6
        
        # Simple heuristic based on item properties
        colors = [item['color'] for item in items]
        if len(set(colors)) <= 2:
            color_score = 0.9  # Monochromatic outfits score higher
        
        categories = [item['category'] for item in items]
        if len(categories) >= 3:
            category_score = 0.9  # Outfits with multiple categories score higher
        
        formality_levels = [item['formality_level'] for item in items]
        formality_variance = max(formality_levels) - min(formality_levels)
        if formality_variance < 0.3:
            formality_score = 0.8  # Consistent formality scores higher
        
        return (color_score + category_score + formality_score) / 3
    
    def _estimate_formality_level(self, item: ClothingItem) -> float:
        """Estimate formality level of an item (0-1 scale)"""
        formality_map = {
            FitType.STRUCTURED: 0.9,
            FitType.FITTED: 0.8,
            FitType.STRAIGHT: 0.6,
            FitType.RELAXED: 0.4,
            FitType.OVERSIZED: 0.3,
            FitType.SKINNY: 0.5,
            FitType.BOOT_CUT: 0.5,
            FitType.A_LINE: 0.7
        }
        
        base_formality = formality_map.get(item.fit, 0.5)
        
        # Adjust based on category
        if item.category in [ItemCategory.DRESS, ItemCategory.OUTERWEAR]:
            base_formality += 0.1
        elif item.category == ItemCategory.ACCESSORY:
            base_formality -= 0.1
        
        return max(0.1, min(0.9, base_formality))
    
    def _estimate_color_intensity(self, color: Color) -> float:
        """Estimate color intensity (0-1 scale)"""
        intense_colors = [Color.RED, Color.BLUE, Color.GREEN, Color.PURPLE, Color.PINK, Color.ORANGE]
        neutral_colors = [Color.BLACK, Color.WHITE, Color.GRAY, Color.NAVY, Color.BEIGE, Color.CREAM, Color.BROWN]
        
        if color in intense_colors:
            return 0.8
        elif color in neutral_colors:
            return 0.3
        else:
            return 0.5
    
    def _generate_style_notes(self, outfit: List[ClothingItem], user_info: UserInfo) -> List[str]:
        """Generate style notes for the outfit"""
        notes = []
        
        # Body type specific notes
        if user_info.body_type == BodyType.TRIANGLE:
            notes.append("This outfit helps balance your proportions with emphasis on the upper body")
        elif user_info.body_type == BodyType.INVERTED_TRIANGLE:
            notes.append("This outfit creates balance by adding volume to the lower body")
        elif user_info.body_type == BodyType.RECTANGLE:
            notes.append("This outfit creates the illusion of curves with strategic tailoring")
        
        # Color coordination notes
        colors = [item.color for item in outfit if item.color != Color.PATTERNED]
        if len(set(colors)) <= 2:
            notes.append("Monochromatic color scheme creates a sleek, elongated look")
        else:
            notes.append("Well-coordinated color palette with visual interest")
        
        return notes