import streamlit as st
import json
from typing import List, Dict, Tuple
from enum import Enum
from datetime import datetime

# -----------------------
# Models / Enums
# -----------------------
class BodyType(str, Enum):
    TRIANGLE = "Triangle"
    RECTANGLE = "Rectangle"
    INVERTED_TRIANGLE = "InvertedTriangle"
    NONE = "None"

class OccasionType(str, Enum):
    CASUAL = "casual"
    BUSINESS = "business"
    PARTY = "party"

class ItemCategory(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    DRESS = "dress"

class FitType(str, Enum):
    FITTED = "fitted"
    STRUCTURED = "structured"
    RELAXED = "relaxed"
    SKINNY = "skinny"
    STRAIGHT = "straight"
    BOOT_CUT = "boot-cut"
    A_LINE = "a-line"
    SHAPELESS = "shapeless"
    WIDE_LEG = "wide-leg"

class ClothingItem:
    def __init__(
        self,
        item_id: str,
        category: str,
        subcategory: str,
        fit: str,
        pattern: str,
        tags: List[str],
        color: str = "#3B82F6",
        img: str = None,
    ):
        self.item_id = item_id
        self.category = ItemCategory(category)
        self.subcategory = subcategory
        self.fit = FitType(fit)
        self.pattern = pattern
        self.tags = tags
        self.color = color
        self.img = img or f"https://placehold.co/300x400/{color.lstrip('#')}/FFFFFF?text={self.subcategory.replace(' ','+')}" 

    def as_dict(self):
        return {
            "item_id": self.item_id,
            "category": self.category.value,
            "subcategory": self.subcategory,
            "fit": self.fit.value,
            "pattern": self.pattern,
            "tags": self.tags,
            "color": self.color,
            "img": self.img,
        }

    def __repr__(self):
        return f"{self.subcategory} ({self.fit.value})"

class Outfit:
    def __init__(self, outfit_id: str, items: List[ClothingItem], compatibility_score: float, style_notes: List[str]):
        self.outfit_id = outfit_id
        self.items = items
        self.compatibility_score = compatibility_score
        self.style_notes = style_notes

    def as_dict(self):
        return {
            "outfit_id": self.outfit_id,
            "items": [i.as_dict() for i in self.items],
            "compatibility_score": self.compatibility_score,
            "style_notes": self.style_notes,
        }

# -----------------------
# Sample Inventory Loader
# -----------------------
def load_inventory() -> List[ClothingItem]:
    inventory_data = [
        {"item_id": "1",  "category": "top",    "subcategory": "Fitted Blouse",      "fit": "fitted",    "pattern": "solid", "tags": ["business","casual"], "color": "#3B82F6"},
        {"item_id": "2",  "category": "top",    "subcategory": "Bold Pattern Top",   "fit": "fitted",    "pattern": "bold",  "tags": ["casual","party"],   "color": "#F59E0B"},
        {"item_id": "3",  "category": "top",    "subcategory": "Shapeless Sweater", "fit": "shapeless", "pattern": "solid", "tags": ["casual"],         "color": "#9CA3AF"},
        {"item_id": "4",  "category": "top",    "subcategory": "Structured Blazer", "fit": "structured","pattern": "solid", "tags": ["business"],        "color": "#1F2937"},
        {"item_id": "5",  "category": "top",    "subcategory": "V-Neck Top",         "fit": "fitted",    "pattern": "solid", "tags": ["casual","business"],"color": "#10B981"},
        {"item_id": "11", "category": "bottom", "subcategory": "Skinny Jeans",       "fit": "skinny",    "pattern": "solid", "tags": ["casual","party"],   "color": "#6B7280"},
        {"item_id": "12", "category": "bottom", "subcategory": "Boot-cut Trousers", "fit": "boot-cut",  "pattern": "solid", "tags": ["casual","business"],"color": "#4B5563"},
        {"item_id": "13", "category": "bottom", "subcategory": "A-Line Skirt",       "fit": "a-line",    "pattern": "bold",  "tags": ["casual","party"],   "color": "#EC4899"},
        {"item_id": "14", "category": "bottom", "subcategory": "Wide-Leg Pants",     "fit": "wide-leg",  "pattern": "solid", "tags": ["business","party"], "color": "#064E3B"},
        {"item_id": "15", "category": "bottom", "subcategory": "Straight Trousers",  "fit": "straight",  "pattern": "solid", "tags": ["business"],        "color": "#374151"},
        {"item_id": "21", "category": "dress",  "subcategory": "A-Line Dress",       "fit": "a-line",    "pattern": "bold",  "tags": ["casual","party"],   "color": "#8B5CF6"},
        {"item_id": "22", "category": "dress",  "subcategory": "Sheath Dress",       "fit": "fitted",    "pattern": "solid", "tags": ["business","party"], "color": "#EF4444"},
    ]
    return [ClothingItem(**d) for d in inventory_data]

# -----------------------
# Style Rule Engine
# -----------------------
class StyleRuleEngine:
    def __init__(self):
        self.log_messages: List[str] = []

    def filter_by_occasion(self, items: List[ClothingItem], occasion: OccasionType) -> List[ClothingItem]:
        self.log_messages.append(f"> Filtering for occasion: {occasion.value}...")
        filtered = [item for item in items if occasion.value in item.tags]
        removed = {i.item_id for i in items} - {i.item_id for i in filtered}
        for rid in removed:
            item = next(i for i in items if i.item_id == rid)
            self.log_messages.append(f"> Item {rid} ({item.subcategory}): Filtered (Not for {occasion.value}).")
        return filtered

    def filter_by_user_rules(self, items: List[ClothingItem], body_type: BodyType) -> List[ClothingItem]:
        if body_type == BodyType.NONE:
            self.log_messages.append("> No body type rules applied.")
            return items

        self.log_messages.append(f"> Applying rules for body type: {body_type.value}...")
        filtered_items: List[ClothingItem] = []
        for item in items:
            keep = True
            reason = None

            # Triangle (Type A)
            if body_type == BodyType.TRIANGLE:
                if item.category == ItemCategory.BOTTOM and item.fit == FitType.SKINNY:
                    keep = False
                    reason = "Skinny bottoms not ideal for Triangle"
                if item.category == ItemCategory.TOP and item.fit == FitType.SHAPELESS:
                    keep = False
                    reason = "Shapeless tops not ideal for Triangle"

            # Inverted triangle (Type V)
            elif body_type == BodyType.INVERTED_TRIANGLE:
                if item.category == ItemCategory.TOP and item.pattern == "bold":
                    keep = False
                    reason = "Bold tops add too much volume for InvertedTriangle"
                # prefer A-line/wide bottoms - but keep flexible
                # if item.category == ItemCategory.BOTTOM and item.fit not in [FitType.A_LINE, FitType.WIDE_LEG]:
                #     keep = False
                #     reason = "Prefer A-line/wide bottoms for InvertedTriangle"

            # Rectangle
            elif body_type == BodyType.RECTANGLE:
                if item.category == ItemCategory.DRESS and item.fit != FitType.A_LINE:
                    keep = False
                    reason = "Prefer A-line dresses for Rectangle to create curves"

            if keep:
                filtered_items.append(item)
                self.log_messages.append(f"> Item {item.item_id} ({item.subcategory}): Passed user rules.")
            else:
                self.log_messages.append(f"> Item {item.item_id} ({item.subcategory}): Filtered ({reason}).")

        return filtered_items

# -----------------------
# Outfit Generator
# -----------------------
class OutfitGenerator:
    def __init__(self):
        self.max_generation_attempts = 1000

    def generate_outfits(self, body_type: BodyType, occasion: OccasionType, inventory: List[ClothingItem], max_outfits: int = 3) -> Tuple[List[Outfit], List[str], List[str]]:
        engine = StyleRuleEngine()
        # Stage 1: occasion filter
        occ_filtered = engine.filter_by_occasion(inventory, occasion)
        # Stage 2: user rules
        final_items = engine.filter_by_user_rules(occ_filtered, body_type)
        engine.log_messages.append(f"> Final item pool has {len(final_items)} items.")

        # categorize
        tops = [i for i in final_items if i.category == ItemCategory.TOP]
        bottoms = [i for i in final_items if i.category == ItemCategory.BOTTOM]
        dresses = [i for i in final_items if i.category == ItemCategory.DRESS]

        # generate candidates
        candidates: List[List[ClothingItem]] = []
        if tops and bottoms:
            for t in tops:
                for b in bottoms:
                    candidates.append([t, b])
        # dresses as single-piece outfits
        for d in dresses:
            candidates.append([d])

        engine.log_messages.append(f"> Generated {len(candidates)} candidate outfits.")

        if not candidates:
            return [], engine.log_messages, [it.item_id for it in final_items]

        # score candidates
        scored: List[Outfit] = []
        for idx, cand in enumerate(candidates):
            score = self._calculate_score(cand, body_type)
            notes = self._generate_notes(cand, body_type)
            scored.append(Outfit(f"outfit_{idx+1}", cand, score, notes))

        # sort by score desc
        scored.sort(key=lambda o: o.compatibility_score, reverse=True)
        top = scored[:max_outfits]
        engine.log_messages.append(f"> Returning top {len(top)} outfits.")
        return top, engine.log_messages, [it.item_id for it in final_items]

    def _calculate_score(self, items: List[ClothingItem], body_type: BodyType) -> float:
        base_score = 0.6

        # body-type bonuses
        if body_type != BodyType.NONE:
            for it in items:
                if body_type == BodyType.TRIANGLE:
                    if it.category in [ItemCategory.TOP, ItemCategory.DRESS] and it.fit in [FitType.FITTED, FitType.STRUCTURED]:
                        base_score += 0.15
                    if it.category == ItemCategory.BOTTOM and it.fit in [FitType.STRAIGHT, FitType.BOOT_CUT, FitType.WIDE_LEG]:
                        base_score += 0.1
                elif body_type == BodyType.INVERTED_TRIANGLE:
                    if it.category == ItemCategory.TOP and it.fit in [FitType.RELAXED, FitType.SHAPELESS]:
                        base_score += 0.1
                    if it.category in [ItemCategory.BOTTOM, ItemCategory.DRESS] and it.fit in [FitType.A_LINE, FitType.WIDE_LEG]:
                        base_score += 0.15
                elif body_type == BodyType.RECTANGLE:
                    if it.fit == FitType.A_LINE:
                        base_score += 0.15

        # color variety bonus
        if len(items) > 1 and items[0].color != items[1].color:
            base_score += 0.12

        # pattern handling
        if len(items) > 1:
            has_bold = any(it.pattern == "bold" for it in items)
            all_bold = all(it.pattern == "bold" for it in items)
            if has_bold and not all_bold:
                base_score += 0.08
            if all_bold:
                base_score -= 0.12  # reduce for clashing bold+bold

        # simple fit clash penalty example
        if len(items) > 1 and items[0].fit == FitType.SHAPELESS and items[1].fit == FitType.WIDE_LEG:
            base_score -= 0.08

        # clamp
        return max(0.0, min(1.0, base_score))

    def _generate_notes(self, items: List[ClothingItem], body_type: BodyType) -> List[str]:
        notes = []
        if body_type == BodyType.TRIANGLE:
            notes.append("Highlights the upper body to balance a triangle shape.")
        elif body_type == BodyType.INVERTED_TRIANGLE:
            notes.append("Adds volume to the lower body to balance an inverted triangle.")
        elif body_type == BodyType.RECTANGLE:
            notes.append("Creates definition and curves (A-line recommendations).")
        else:
            notes.append("A classic and versatile combination.")

        if len(items) > 1:
            if items[0].color != items[1].color:
                notes.append(f"The {items[0].color} and {items[1].color} tones complement each other.")
            else:
                notes.append("A chic monochromatic look.")
            notes.append("Follows Rule of 3: consider adding an accessory to complete the look.")
        else:
            notes.append("An elegant one-piece outfit — add shoes or outerwear to complete.")
        return notes

# -----------------------
# Streamlit UI
# -----------------------
def main():
    st.set_page_config(page_title="Outfit Curation Engine", layout="wide")

    st.markdown(
        """
        <style>
          .main-header { font-size: 2.4rem; font-weight:700; text-align:center; color:#111827; margin-bottom:0.25rem; }
          .subheader { text-align:center; color:#6B7280; margin-bottom:1.25rem; }
          .section { padding: 1rem; border-radius: 10px; background: #fff; border: 1px solid #E5E7EB; }
          .score { background:#3B82F6; color:white; padding:6px 10px; border-radius:999px; font-weight:600; }
          .log { background:#111827; color:#e5e7eb; padding:12px; border-radius:8px; font-family: monospace; height:260px; overflow:auto;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # header
    st.markdown('<div class="main-header">Outfit Curation Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Hybrid rule-based + ML-like scoring for curated outfit recommendations</div>', unsafe_allow_html=True)

    # layout
    left, right = st.columns([1, 2.2])

    with left:
        st.markdown("### 1. Inputs")
        body_type = st.selectbox("User Body Type", options=list(BodyType), format_func=lambda x: x.value)
        occasion = st.selectbox("Occasion", options=list(OccasionType), format_func=lambda x: x.value.capitalize())

        if st.button("Curate Outfits", use_container_width=True):
            inventory = load_inventory()
            generator = OutfitGenerator()
            with st.spinner("Curating outfits..."):
                outfits, logs, kept_ids = generator.generate_outfits(body_type, occasion, inventory)
                st.session_state["outfits"] = [o.as_dict() for o in outfits]
                st.session_state["logs"] = logs
                st.session_state["kept_ids"] = set(kept_ids)

        st.markdown("### Filtering & Curation Log")
        logs_content = st.session_state.get("logs", [])
        if not logs_content:
            st.markdown('<div class="log">> Logs will appear here once you run curation.</div>', unsafe_allow_html=True)
        else:
            # render logs
            log_html = "<div class='log'>" + "<br>".join([l.replace('  -', '&nbsp;&nbsp;-') for l in logs_content]) + "</div>"
            st.markdown(log_html, unsafe_allow_html=True)

    with right:
        st.markdown("### 2. Inventory")
        inventory = load_inventory()
        kept_ids = st.session_state.get("kept_ids", None)
        cols = st.columns(4)
        for idx, item in enumerate(inventory):
            col = cols[idx % 4]
            is_filtered = kept_ids is not None and item.item_id not in kept_ids
            card_style = "opacity:0.45; filter:grayscale(100%);" if is_filtered else ""
            with col:
                st.markdown(
                    f"""
                    <div style="border-radius:8px; padding:8px; text-align:center; {card_style}">
                        <img src="{item.img}" style="width:100%; border-radius:6px; object-fit:cover"/>
                        <div style="font-weight:600; margin-top:6px;">{item.subcategory}</div>
                        <div style="color:#6B7280; font-size:0.85rem;">{item.fit.value} • {item.pattern}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("### 3. Curated Outfits")
        outfits_data = st.session_state.get("outfits", [])
        if not outfits_data:
            st.info("Click 'Curate Outfits' to get recommendations.")
        else:
            for i, o in enumerate(outfits_data):
                st.markdown(f"#### Recommendation #{i+1}")
                # layout: images + score + notes
                col1, col2 = st.columns([3, 1])
                with col1:
                    item_cols = st.columns(len(o["items"]))
                    for j, it in enumerate(o["items"]):
                        with item_cols[j]:
                            st.image(it["img"], caption=it["subcategory"])
                with col2:
                    st.markdown(f"<div style='text-align:center;'><div class='score'>{o['compatibility_score']:.3f}</div></div>", unsafe_allow_html=True)
                    st.caption("Compatibility Score")
                st.markdown("**Style Notes:**")
                for note in o["style_notes"]:
                    st.markdown(f"- {note}")

                with st.expander("Show outfit item JSON"):
                    st.code(json.dumps(o, indent=2), language="json")

                st.write("---")

    # footer
    st.markdown("<div style='text-align:center; color:#6B7280; font-size:0.85rem; padding-top:6px;'>Outfit Curation Engine • Demo</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()