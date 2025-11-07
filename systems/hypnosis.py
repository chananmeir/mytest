"""
Hypnosis and suggestion system for Family Dynamics RPG
"""
import random
from typing import Optional, Tuple
from models.character import Character, PostHypnoticSuggestion
from models.game_state import GameState
from systems.clothing_effects import ClothingEffects


class HypnosisSystem:
    """Manages hypnotic suggestions and post-hypnotic suggestions"""

    # SP costs for different types of suggestions
    EMOTIONAL_NUDGE_COST = 2
    BEHAVIORAL_PROMPT_COST = 3
    STRONG_ANCHOR_COST_MIN = 4
    STRONG_ANCHOR_COST_MAX = 6

    @staticmethod
    def can_plant_phs(game_state: GameState, target_name: str, required_technique: str = None) -> Tuple[bool, str]:
        """Check if a PHS can be planted on the target"""
        char = game_state.get_character(target_name)

        if not char:
            return False, "Character not found."

        # Check if player knows required hypnosis technique
        if required_technique and not game_state.player.hypnosis_knowledge.knows_technique(required_technique):
            from systems.hypnosis_knowledge import HYPNOSIS_TECHNIQUES
            technique = HYPNOSIS_TECHNIQUES.get(required_technique)
            technique_name = technique.name if technique else required_technique
            return False, f"You don't know '{technique_name}' yet. Learn hypnosis techniques first!"

        if char.rapport < 6:
            return False, f"Rapport too low ({char.rapport}/6 required). Build more trust first."

        if not char.can_accept_phs():
            return False, f"{char.name} is at max capacity for PHS ({len(char.active_phs)}/{char.max_phs})."

        # Check emotional state - defensive/tense states make it harder
        if char.emotional_state in ["defensive", "hostile", "suspicious"]:
            return False, f"{char.name} is {char.emotional_state} - soften their emotional state first."

        return True, "Ready to plant PHS"

    @staticmethod
    def plant_emotional_nudge(
        game_state: GameState,
        target_name: str,
        trigger: str,
        response: str
    ) -> Tuple[bool, str]:
        """Plant an emotional nudge PHS (2 SP) - Requires 'emotional_anchoring' technique"""
        # Check for required technique
        can_plant, message = HypnosisSystem.can_plant_phs(game_state, target_name, 'emotional_anchoring')

        if not can_plant:
            return False, message

        # Get technique bonuses
        sp_reduction, success_bonus = game_state.player.hypnosis_knowledge.get_total_bonuses()
        actual_cost = max(1, HypnosisSystem.EMOTIONAL_NUDGE_COST - sp_reduction)

        if not game_state.spend_sp(actual_cost):
            return False, f"Not enough SP (need {actual_cost}, have {game_state.player.suggestion_points})"

        char = game_state.get_character(target_name)

        # Calculate base success rate based on rapport and resistance
        base_success = 50 + (char.rapport * 2) - (char.resistance // 2) + success_bonus

        # Apply clothing modifier
        clothing_modifier, clothing_desc = ClothingEffects.calculate_outfit_suggestibility(char)
        final_success = ClothingEffects.apply_clothing_modifier_to_success_rate(base_success, clothing_modifier)

        phs = PostHypnoticSuggestion(
            target_name=target_name,
            trigger=trigger,
            response=response,
            success_rate=final_success
        )

        char.add_phs(phs)

        # Build response message
        message = f"PHS planted on {target_name}. Success rate: {final_success}%"
        if clothing_modifier != 0:
            message += f" (base {base_success}%, {clothing_desc})"

        return True, message

    @staticmethod
    def plant_behavioral_prompt(
        game_state: GameState,
        target_name: str,
        trigger: str,
        response: str
    ) -> Tuple[bool, str]:
        """Plant a behavioral prompt PHS (3 SP) - Requires 'embedded_commands' technique"""
        can_plant, message = HypnosisSystem.can_plant_phs(game_state, target_name, 'embedded_commands')

        if not can_plant:
            return False, message

        # Get technique bonuses
        sp_reduction, success_bonus = game_state.player.hypnosis_knowledge.get_total_bonuses()
        actual_cost = max(1, HypnosisSystem.BEHAVIORAL_PROMPT_COST - sp_reduction)

        if not game_state.spend_sp(actual_cost):
            return False, f"Not enough SP (need {actual_cost}, have {game_state.player.suggestion_points})"

        char = game_state.get_character(target_name)

        # Behavioral prompts have slightly lower base success
        base_success = 40 + (char.rapport * 2) - (char.resistance // 2) + success_bonus

        # Apply clothing modifier
        clothing_modifier, clothing_desc = ClothingEffects.calculate_outfit_suggestibility(char)
        final_success = ClothingEffects.apply_clothing_modifier_to_success_rate(base_success, clothing_modifier)

        phs = PostHypnoticSuggestion(
            target_name=target_name,
            trigger=trigger,
            response=response,
            success_rate=final_success
        )

        char.add_phs(phs)

        # Build response message
        message = f"PHS planted on {target_name}. Success rate: {final_success}%"
        if clothing_modifier != 0:
            message += f" (base {base_success}%, {clothing_desc})"

        return True, message

    @staticmethod
    def plant_strong_anchor(
        game_state: GameState,
        target_name: str,
        trigger: str,
        response: str,
        sp_cost: int = 4
    ) -> Tuple[bool, str]:
        """Plant a strong anchored reaction PHS (4-6 SP) - Requires 'post_hypnotic_suggestion' technique"""
        if sp_cost < HypnosisSystem.STRONG_ANCHOR_COST_MIN or sp_cost > HypnosisSystem.STRONG_ANCHOR_COST_MAX:
            return False, f"SP cost must be between {HypnosisSystem.STRONG_ANCHOR_COST_MIN} and {HypnosisSystem.STRONG_ANCHOR_COST_MAX}"

        can_plant, message = HypnosisSystem.can_plant_phs(game_state, target_name, 'post_hypnotic_suggestion')

        if not can_plant:
            return False, message

        # Get technique bonuses
        sp_reduction, success_bonus = game_state.player.hypnosis_knowledge.get_total_bonuses()
        actual_cost = max(1, sp_cost - sp_reduction)

        if not game_state.spend_sp(actual_cost):
            return False, f"Not enough SP (need {actual_cost}, have {game_state.player.suggestion_points})"

        char = game_state.get_character(target_name)

        # Strong anchors have better base success, scales with SP investment
        bonus = (sp_cost - HypnosisSystem.STRONG_ANCHOR_COST_MIN) * 5
        base_success = 45 + bonus + (char.rapport * 2) - (char.resistance // 2) + success_bonus

        # Apply clothing modifier
        clothing_modifier, clothing_desc = ClothingEffects.calculate_outfit_suggestibility(char)
        final_success = ClothingEffects.apply_clothing_modifier_to_success_rate(base_success, clothing_modifier)

        phs = PostHypnoticSuggestion(
            target_name=target_name,
            trigger=trigger,
            response=response,
            success_rate=final_success
        )

        char.add_phs(phs)

        # Build response message
        message = f"Strong PHS planted on {target_name}. Success rate: {final_success}%"
        if clothing_modifier != 0:
            message += f" (base {base_success}%, {clothing_desc})"

        return True, message

    @staticmethod
    def reinforce_phs(game_state: GameState, target_name: str, phs_index: int) -> Tuple[bool, str]:
        """Reinforce an existing PHS (no SP cost, but requires appropriate conversation)"""
        char = game_state.get_character(target_name)

        if not char:
            return False, "Character not found"

        if phs_index >= len(char.active_phs):
            return False, "PHS not found"

        phs = char.active_phs[phs_index]
        phs.reinforce()

        new_chance = phs.calculate_activation_chance()
        return True, f"PHS reinforced. Activation chance now: {new_chance}%"

    @staticmethod
    def check_phs_activation(phs: PostHypnoticSuggestion) -> bool:
        """Check if a PHS activates (called when trigger conditions are met)"""
        activation_chance = phs.calculate_activation_chance()
        roll = random.randint(1, 100)
        return roll <= activation_chance

    @staticmethod
    def build_rapport(
        game_state: GameState,
        target_name: str,
        amount: int,
        reason: str = ""
    ) -> str:
        """Build rapport with a character, possibly earning SP"""
        char = game_state.get_character(target_name)

        if not char:
            return "Character not found"

        old_rapport = char.rapport
        char.add_rapport(amount)
        new_rapport = char.rapport

        message = f"Rapport with {target_name}: {old_rapport} → {new_rapport}"

        if reason:
            message += f" ({reason})"

        # Track rapport gain for goals
        from systems.goal_system import GoalSystem
        goal_messages = GoalSystem.track_rapport_gain(game_state, amount)
        goal_messages.extend(GoalSystem.track_rapport_milestone(game_state, target_name, new_rapport))

        # Award SP for rapport milestones
        milestones = [5, 10, 15, 20]
        for milestone in milestones:
            if old_rapport < milestone <= new_rapport:
                game_state.add_sp(1, f"Rapport milestone with {target_name} ({milestone})")

        # Check for location unlocks triggered by this rapport increase
        from systems.unlock_system import UnlockSystem
        unlock_messages = UnlockSystem.check_rapport_unlock_triggers(target_name, new_rapport, game_state)
        if unlock_messages:
            message += "\n" + "\n".join(unlock_messages)

        # Add goal completion messages
        if goal_messages:
            message += "\n" + "\n".join(goal_messages)

        return message

    @staticmethod
    def change_emotional_state(
        game_state: GameState,
        target_name: str,
        new_state: str,
        reason: str = ""
    ) -> str:
        """Change a character's emotional state"""
        char = game_state.get_character(target_name)

        if not char:
            return "Character not found"

        old_state = char.emotional_state
        char.set_emotional_state(new_state, reason)

        message = f"{target_name}'s state: {old_state} → {new_state}"

        if reason:
            message += f" ({reason})"

        # Award SP for positive emotional shifts
        positive_shifts = [
            ("defensive", "neutral"),
            ("tense", "relaxed"),
            ("hostile", "neutral"),
            ("suspicious", "open")
        ]

        if (old_state, new_state) in positive_shifts:
            game_state.add_sp(1, f"Softened {target_name}'s emotional state")

        return message
