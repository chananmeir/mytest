"""
Clothing Effects System
Calculates how a character's outfit affects their suggestibility and resistance
"""

from typing import Dict, Tuple, Optional
from models.character import Character


class ClothingEffects:
    """Calculates gameplay effects of character outfits"""

    # Tag-based modifiers
    TAG_MODIFIERS = {
        # Revealing/vulnerable tags increase suggestibility
        'revealing': 5,
        'sexy': 4,
        'bold': 3,
        'provocative': 6,

        # Protective/formal tags decrease suggestibility
        'formal': -4,
        'professional': -5,
        'modest': -3,
        'conservative': -4,

        # Neutral/comfort
        'casual': 1,
        'comfortable': 1,
        'elegant': -2,
        'athletic': 0,
    }

    @staticmethod
    def calculate_outfit_suggestibility(character: Character) -> Tuple[int, str]:
        """
        Calculate suggestibility modifier from character's outfit

        Args:
            character: Character with outfit dict

        Returns:
            (modifier_percentage, description)
            modifier is +/- percentage to add to success rates
            description explains why
        """
        from data.clothing_items import get_clothing_item

        if not character.outfit:
            return (0, "No outfit data")

        total_modifier = 0
        modifier_reasons = []

        # Track overall outfit properties
        total_coverage = 0
        total_formality = 0
        item_count = 0
        all_tags = []

        # Analyze each clothing item in the outfit
        slots_to_check = ['bra', 'panties', 'top', 'bottom', 'dress', 'outerwear']

        for slot in slots_to_check:
            item_id = character.outfit.get(slot)
            if not item_id:
                continue

            item = get_clothing_item(item_id)
            if not item:
                continue

            # Accumulate stats
            total_coverage += item.coverage
            total_formality += item.formality
            item_count += 1
            all_tags.extend(item.tags)

        if item_count == 0:
            return (0, "No outfit information")

        # Calculate averages
        avg_coverage = total_coverage / item_count
        avg_formality = total_formality / item_count

        # Coverage modifier (lower coverage = more vulnerable)
        if avg_coverage < 40:
            coverage_mod = 15
            modifier_reasons.append("very revealing")
        elif avg_coverage < 60:
            coverage_mod = 8
            modifier_reasons.append("somewhat revealing")
        elif avg_coverage > 80:
            coverage_mod = -5
            modifier_reasons.append("fully covered")
        else:
            coverage_mod = 0

        total_modifier += coverage_mod

        # Formality modifier (formal = professional armor)
        if avg_formality > 70:
            formality_mod = -8
            modifier_reasons.append("very formal")
        elif avg_formality > 50:
            formality_mod = -4
            modifier_reasons.append("professional")
        elif avg_formality < 30:
            formality_mod = 5
            modifier_reasons.append("casual")
        else:
            formality_mod = 0

        total_modifier += formality_mod

        # Tag-based modifiers
        tag_modifier = 0
        significant_tags = []

        for tag, modifier in ClothingEffects.TAG_MODIFIERS.items():
            if tag in all_tags:
                tag_modifier += modifier
                if abs(modifier) >= 3:
                    significant_tags.append(tag)

        total_modifier += tag_modifier

        if significant_tags:
            modifier_reasons.extend(significant_tags[:2])  # Add up to 2 significant tags

        # Generate description
        if total_modifier > 10:
            desc = f"Very suggestible outfit (+{total_modifier}%): {', '.join(modifier_reasons)}"
        elif total_modifier > 0:
            desc = f"Suggestible outfit (+{total_modifier}%): {', '.join(modifier_reasons)}"
        elif total_modifier < -5:
            desc = f"Protected outfit ({total_modifier}%): {', '.join(modifier_reasons)}"
        else:
            desc = f"Neutral outfit ({total_modifier}%)"

        return (total_modifier, desc)

    @staticmethod
    def get_outfit_description(character: Character) -> str:
        """
        Get a natural language description of the character's outfit

        Args:
            character: Character with outfit dict

        Returns:
            Description string
        """
        from data.clothing_items import get_clothing_item

        if not character.outfit:
            return character.clothing

        outfit_parts = []

        # Check for dress first (overrides top/bottom)
        dress_id = character.outfit.get('dress')
        if dress_id:
            dress = get_clothing_item(dress_id)
            if dress:
                outfit_parts.append(dress.name)
        else:
            # Separate top and bottom
            top_id = character.outfit.get('top')
            if top_id:
                top = get_clothing_item(top_id)
                if top:
                    outfit_parts.append(top.name)

            bottom_id = character.outfit.get('bottom')
            if bottom_id:
                bottom = get_clothing_item(bottom_id)
                if bottom:
                    outfit_parts.append(bottom.name)

        # Add outerwear if present
        outerwear_id = character.outfit.get('outerwear')
        if outerwear_id:
            outerwear = get_clothing_item(outerwear_id)
            if outerwear:
                outfit_parts.append(outerwear.name)

        # Add accessories
        for slot in ['necklace', 'earrings']:
            acc_id = character.outfit.get(slot)
            if acc_id:
                acc = get_clothing_item(acc_id)
                if acc:
                    outfit_parts.append(acc.name)

        if outfit_parts:
            return f"wearing {', '.join(outfit_parts)}"
        else:
            return character.clothing

    @staticmethod
    def apply_clothing_modifier_to_success_rate(
        base_success_rate: int,
        clothing_modifier: int
    ) -> int:
        """
        Apply clothing modifier to a success rate, with clamping

        Args:
            base_success_rate: Base success rate (0-100)
            clothing_modifier: Modifier from clothing (-20 to +20 typically)

        Returns:
            Modified success rate, clamped to 5-95
        """
        modified = base_success_rate + clothing_modifier
        return max(5, min(95, modified))
