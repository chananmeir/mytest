"""
Advanced Hypnosis Mechanics for Family Dynamics RPG

Includes:
- Combo Suggestions (chained PHS)
- Conflicting Suggestions (internal conflict)
- Group Hypnosis
- Resistance Breaking mini-games
- Mastery Level tracking
"""
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from models.character import Character, PostHypnoticSuggestion
from models.game_state import GameState


@dataclass
class ComboSuggestion:
    """Represents a chain of connected PHS that trigger each other"""
    combo_id: str
    combo_name: str
    phs_chain: List[Dict[str, any]] = field(default_factory=list)  # [{target, trigger, response, next_trigger}]
    combo_bonus: int = 15  # Success rate bonus for full combo
    activated_steps: List[bool] = field(default_factory=list)
    is_complete: bool = False

    def add_to_chain(self, target: str, trigger: str, response: str, next_trigger: Optional[str] = None):
        """Add a PHS to the combo chain"""
        self.phs_chain.append({
            'target': target,
            'trigger': trigger,
            'response': response,
            'next_trigger': next_trigger
        })
        self.activated_steps.append(False)

    def activate_step(self, step_index: int) -> bool:
        """Mark a step as activated, check if combo is complete"""
        if step_index < len(self.activated_steps):
            self.activated_steps[step_index] = True

            # Check if all steps are activated
            if all(self.activated_steps):
                self.is_complete = True
                return True
        return False

    def get_completion_percent(self) -> int:
        """Get percentage of combo completed"""
        if not self.activated_steps:
            return 0
        return int((sum(self.activated_steps) / len(self.activated_steps)) * 100)

    def to_dict(self) -> dict:
        """Convert to dictionary for saving"""
        return {
            'combo_id': self.combo_id,
            'combo_name': self.combo_name,
            'phs_chain': self.phs_chain,
            'combo_bonus': self.combo_bonus,
            'activated_steps': self.activated_steps,
            'is_complete': self.is_complete
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ComboSuggestion':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class ConflictingPHS:
    """Tracks contradictory suggestions causing internal conflict"""
    character_name: str
    phs_pair: Tuple[int, int]  # Indices of conflicting PHS
    conflict_type: str  # 'direct_contradiction', 'emotional_conflict', 'behavioral_clash'
    conflict_level: int = 0  # 0-100, increases as both PHS trigger
    breakdown_threshold: int = 80

    def increase_conflict(self, amount: int = 10):
        """Increase conflict level"""
        self.conflict_level = min(100, self.conflict_level + amount)

    def is_near_breakdown(self) -> bool:
        """Check if character is near mental breakdown"""
        return self.conflict_level >= self.breakdown_threshold

    def to_dict(self) -> dict:
        return {
            'character_name': self.character_name,
            'phs_pair': list(self.phs_pair),
            'conflict_type': self.conflict_type,
            'conflict_level': self.conflict_level,
            'breakdown_threshold': self.breakdown_threshold
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ConflictingPHS':
        """Create from dictionary"""
        data['phs_pair'] = tuple(data['phs_pair'])
        return cls(**data)


@dataclass
class MasteryLevel:
    """Tracks player's mastery in different hypnosis areas"""
    total_phs_planted: int = 0
    successful_activations: int = 0
    failed_activations: int = 0
    reinforcements_done: int = 0
    combos_completed: int = 0
    group_sessions_done: int = 0
    resistance_breaks: int = 0

    # Calculated mastery levels (0-10 scale)
    def get_overall_mastery(self) -> int:
        """Calculate overall mastery level (0-10)"""
        total_actions = (self.total_phs_planted +
                        self.successful_activations +
                        self.reinforcements_done +
                        self.combos_completed * 3 +
                        self.group_sessions_done * 2 +
                        self.resistance_breaks * 2)

        # Mastery thresholds
        if total_actions >= 200:
            return 10  # Master
        elif total_actions >= 150:
            return 9
        elif total_actions >= 120:
            return 8
        elif total_actions >= 90:
            return 7
        elif total_actions >= 65:
            return 6
        elif total_actions >= 45:
            return 5
        elif total_actions >= 30:
            return 4
        elif total_actions >= 20:
            return 3
        elif total_actions >= 10:
            return 2
        elif total_actions >= 5:
            return 1
        else:
            return 0  # Novice

    def get_success_rate(self) -> float:
        """Get success rate percentage"""
        total = self.successful_activations + self.failed_activations
        if total == 0:
            return 0.0
        return (self.successful_activations / total) * 100

    def get_mastery_bonuses(self) -> Tuple[int, int]:
        """Get bonuses based on mastery level (sp_reduction, success_bonus)"""
        mastery = self.get_overall_mastery()

        # SP reduction (max 3 at level 10)
        sp_reduction = min(3, mastery // 3)

        # Success rate bonus (max 20% at level 10)
        success_bonus = min(20, mastery * 2)

        return sp_reduction, success_bonus

    def to_dict(self) -> dict:
        return {
            'total_phs_planted': self.total_phs_planted,
            'successful_activations': self.successful_activations,
            'failed_activations': self.failed_activations,
            'reinforcements_done': self.reinforcements_done,
            'combos_completed': self.combos_completed,
            'group_sessions_done': self.group_sessions_done,
            'resistance_breaks': self.resistance_breaks
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'MasteryLevel':
        return cls(**data)


class AdvancedHypnosisSystem:
    """Advanced hypnosis mechanics"""

    # Combo creation costs
    COMBO_BASE_COST = 8  # SP to create a combo chain
    COMBO_PER_STEP_COST = 2  # Additional SP per step

    # Group hypnosis costs
    GROUP_BASE_COST = 10
    GROUP_PER_PERSON_COST = 4

    # Resistance breaking
    RESISTANCE_BREAK_COST = 5
    RESISTANCE_BREAK_AMOUNT = 10  # How much resistance is reduced

    @staticmethod
    def create_combo_suggestion(
        game_state: GameState,
        combo_name: str,
        chain_steps: List[Dict[str, any]]
    ) -> Tuple[bool, str, Optional[ComboSuggestion]]:
        """
        Create a combo suggestion chain

        Args:
            game_state: Current game state
            combo_name: Name for this combo
            chain_steps: List of dicts with 'target', 'trigger', 'response', 'next_trigger'

        Example chain:
        [
            {'target': 'Ruth', 'trigger': 'when she feels guilty',
             'response': 'defend you to others', 'next_trigger': 'Ruth defends you'},
            {'target': 'Tom', 'trigger': 'Ruth defends you',
             'response': 'agree with Ruth', 'next_trigger': 'Tom agrees'},
            {'target': 'Dawn', 'trigger': 'Tom agrees',
             'response': 'reconsider her judgment of you'}
        ]
        """
        # Validate chain
        if len(chain_steps) < 2:
            return False, "Combo must have at least 2 steps", None

        if len(chain_steps) > 5:
            return False, "Combo cannot exceed 5 steps", None

        # Calculate cost
        total_cost = AdvancedHypnosisSystem.COMBO_BASE_COST + (len(chain_steps) * AdvancedHypnosisSystem.COMBO_PER_STEP_COST)

        if game_state.player.suggestion_points < total_cost:
            return False, f"Not enough SP (need {total_cost}, have {game_state.player.suggestion_points})", None

        # Check if all targets are available and rapport is sufficient
        from systems.hypnosis import HypnosisSystem

        for step in chain_steps:
            target_name = step['target']
            can_plant, msg = HypnosisSystem.can_plant_phs(game_state, target_name)
            if not can_plant:
                return False, f"Cannot plant on {target_name}: {msg}", None

        # Create combo
        combo_id = f"combo_{len(game_state.player.hypnosis_knowledge.learned_techniques)}_{random.randint(1000, 9999)}"
        combo = ComboSuggestion(combo_id=combo_id, combo_name=combo_name)

        # Add each step to chain and plant the PHS
        for i, step in enumerate(chain_steps):
            target_name = step['target']
            trigger = step['trigger']
            response = step['response']
            next_trigger = step.get('next_trigger')

            # Add to combo
            combo.add_to_chain(target_name, trigger, response, next_trigger)

            # Plant the PHS with combo bonus
            char = game_state.get_character(target_name)
            base_success = 40 + (char.rapport * 2) - (char.resistance // 2) + combo.combo_bonus

            phs = PostHypnoticSuggestion(
                target_name=target_name,
                trigger=trigger,
                response=response,
                success_rate=min(95, base_success),
                phs_type="combo_chain"
            )

            char.add_phs(phs)

        # Spend SP
        game_state.spend_sp(total_cost)

        # Track mastery
        if hasattr(game_state.player, 'mastery_level'):
            game_state.player.mastery_level.total_phs_planted += len(chain_steps)

        message = f"✨ Combo '{combo_name}' created with {len(chain_steps)} steps! Cost: {total_cost} SP"
        message += f"\nCombo bonus: +{combo.combo_bonus}% success rate on all steps"

        return True, message, combo

    @staticmethod
    def plant_conflicting_suggestions(
        game_state: GameState,
        target_name: str,
        phs1: Dict[str, str],
        phs2: Dict[str, str]
    ) -> Tuple[bool, str, Optional[ConflictingPHS]]:
        """
        Plant two contradictory suggestions in the same person

        Args:
            target_name: Who to plant on
            phs1: First suggestion {'trigger': '...', 'response': '...'}
            phs2: Conflicting suggestion {'trigger': '...', 'response': '...'}

        Example:
            phs1 = {'trigger': 'when talking about family', 'response': 'speak warmly about you'}
            phs2 = {'trigger': 'when thinking about trust', 'response': 'feel suspicious of you'}
        """
        from systems.hypnosis import HypnosisSystem

        char = game_state.get_character(target_name)
        if not char:
            return False, "Character not found", None

        # Check if character can handle 2 more PHS
        if len(char.active_phs) + 2 > char.max_phs:
            return False, f"{target_name} doesn't have capacity for 2 more PHS", None

        # Plant both suggestions
        success1, msg1 = HypnosisSystem.plant_behavioral_prompt(
            game_state, target_name, phs1['trigger'], phs1['response']
        )

        if not success1:
            return False, f"Failed to plant first PHS: {msg1}", None

        success2, msg2 = HypnosisSystem.plant_behavioral_prompt(
            game_state, target_name, phs2['trigger'], phs2['response']
        )

        if not success2:
            return False, f"Failed to plant second PHS: {msg2}", None

        # Create conflict tracker
        phs_index_1 = len(char.active_phs) - 2
        phs_index_2 = len(char.active_phs) - 1

        # Determine conflict type
        conflict_type = AdvancedHypnosisSystem._determine_conflict_type(
            phs1['response'], phs2['response']
        )

        conflict = ConflictingPHS(
            character_name=target_name,
            phs_pair=(phs_index_1, phs_index_2),
            conflict_type=conflict_type
        )

        message = f"⚠️  Conflicting suggestions planted on {target_name}!"
        message += f"\nConflict type: {conflict_type.replace('_', ' ').title()}"
        message += f"\n⚠️  Warning: As conflict increases, {target_name} may experience confusion, stress, or breakdown"

        return True, message, conflict

    @staticmethod
    def _determine_conflict_type(response1: str, response2: str) -> str:
        """Determine what type of conflict exists between two responses"""
        response1_lower = response1.lower()
        response2_lower = response2.lower()

        # Emotional conflict keywords
        emotional_positive = ['love', 'trust', 'warmth', 'kindness', 'happy', 'support']
        emotional_negative = ['suspicious', 'angry', 'hostile', 'distrust', 'fear', 'avoid']

        has_positive = any(word in response1_lower or word in response2_lower for word in emotional_positive)
        has_negative = any(word in response1_lower or word in response2_lower for word in emotional_negative)

        if has_positive and has_negative:
            return 'emotional_conflict'

        # Behavioral clash keywords
        action_approach = ['approach', 'seek', 'talk', 'engage', 'share', 'tell']
        action_avoid = ['avoid', 'distance', 'ignore', 'hide', 'withdraw', 'leave']

        has_approach = any(word in response1_lower or word in response2_lower for word in action_approach)
        has_avoid = any(word in response1_lower or word in response2_lower for word in action_avoid)

        if has_approach and has_avoid:
            return 'behavioral_clash'

        return 'direct_contradiction'

    @staticmethod
    def perform_group_hypnosis(
        game_state: GameState,
        targets: List[str],
        shared_trigger: str,
        individual_responses: Dict[str, str]
    ) -> Tuple[bool, str, int]:
        """
        Perform group hypnosis session on multiple people simultaneously

        Args:
            targets: List of character names
            shared_trigger: Common trigger for all
            individual_responses: {character_name: their_response}

        Returns:
            (success, message, num_successfully_planted)
        """
        if len(targets) < 2:
            return False, "Group hypnosis requires at least 2 targets", 0

        if len(targets) > 4:
            return False, "Group hypnosis limited to 4 people maximum", 0

        # Calculate cost
        total_cost = AdvancedHypnosisSystem.GROUP_BASE_COST + (len(targets) * AdvancedHypnosisSystem.GROUP_PER_PERSON_COST)

        if game_state.player.suggestion_points < total_cost:
            return False, f"Not enough SP (need {total_cost}, have {game_state.player.suggestion_points})", 0

        # Check if all targets are present and available
        from systems.hypnosis import HypnosisSystem

        available_targets = []
        failed_targets = []

        for target_name in targets:
            can_plant, msg = HypnosisSystem.can_plant_phs(game_state, target_name)
            if can_plant:
                available_targets.append(target_name)
            else:
                failed_targets.append((target_name, msg))

        if len(available_targets) < 2:
            return False, "Not enough valid targets for group hypnosis", 0

        # Group hypnosis has reduced success rate but affects multiple people
        # Success rate decreases with group size
        group_penalty = (len(available_targets) - 1) * 10  # -10% per additional person

        successfully_planted = 0
        results = []

        for target_name in available_targets:
            char = game_state.get_character(target_name)
            response = individual_responses.get(target_name, "feel more open to your influence")

            # Calculate success with group penalty
            base_success = 35 + (char.rapport * 2) - (char.resistance // 2) - group_penalty
            final_success = max(20, min(85, base_success))  # Clamp between 20-85%

            phs = PostHypnoticSuggestion(
                target_name=target_name,
                trigger=shared_trigger,
                response=response,
                success_rate=final_success,
                phs_type="group_hypnosis"
            )

            char.add_phs(phs)
            successfully_planted += 1
            results.append(f"  • {target_name}: {final_success}% success rate")

        # Spend SP
        game_state.spend_sp(total_cost)

        # Track mastery
        if hasattr(game_state.player, 'mastery_level'):
            game_state.player.mastery_level.total_phs_planted += successfully_planted
            game_state.player.mastery_level.group_sessions_done += 1

        message = f"🎯 Group Hypnosis performed on {successfully_planted} people!"
        message += f"\nShared Trigger: '{shared_trigger}'"
        message += f"\nGroup penalty: -{group_penalty}% success rate"
        message += "\n\nResults:\n" + "\n".join(results)

        if failed_targets:
            message += f"\n\n⚠️  Could not include: {', '.join([t[0] for t in failed_targets])}"

        return True, message, successfully_planted

    @staticmethod
    def initiate_resistance_breaking(
        game_state: GameState,
        target_name: str,
        approach: str = "rapport"
    ) -> Tuple[bool, str, int]:
        """
        Initiate a resistance-breaking mini-game

        Args:
            target_name: Who to work on
            approach: 'rapport' (slow, safe), 'pressure' (fast, risky), 'manipulation' (medium)

        Returns:
            (success, message, resistance_reduced)
        """
        char = game_state.get_character(target_name)
        if not char:
            return False, "Character not found", 0

        if char.resistance <= 10:
            return False, f"{target_name} has minimal resistance already", 0

        # Cost check
        if game_state.player.suggestion_points < AdvancedHypnosisSystem.RESISTANCE_BREAK_COST:
            return False, f"Not enough SP (need {AdvancedHypnosisSystem.RESISTANCE_BREAK_COST})", 0

        # Different approaches have different success rates and consequences
        approaches = {
            'rapport': {
                'success_rate': 70,
                'reduction': AdvancedHypnosisSystem.RESISTANCE_BREAK_AMOUNT,
                'suspicion_risk': 5,
                'rapport_change': 1,
                'description': 'Build deep trust through genuine connection'
            },
            'pressure': {
                'success_rate': 85,
                'reduction': AdvancedHypnosisSystem.RESISTANCE_BREAK_AMOUNT + 5,
                'suspicion_risk': 25,
                'rapport_change': -1,
                'description': 'Apply psychological pressure to overwhelm defenses'
            },
            'manipulation': {
                'success_rate': 75,
                'reduction': AdvancedHypnosisSystem.RESISTANCE_BREAK_AMOUNT,
                'suspicion_risk': 15,
                'rapport_change': 0,
                'description': 'Use subtle manipulation techniques'
            }
        }

        if approach not in approaches:
            approach = 'rapport'

        method = approaches[approach]

        # Roll for success
        roll = random.randint(1, 100)
        success = roll <= method['success_rate']

        if success:
            # Reduce resistance
            old_resistance = char.resistance
            char.resistance = max(10, char.resistance - method['reduction'])
            actual_reduction = old_resistance - char.resistance

            # Apply rapport change
            if method['rapport_change'] > 0:
                char.add_rapport(method['rapport_change'])
            elif method['rapport_change'] < 0:
                char.reduce_rapport(abs(method['rapport_change']))

            # Spend SP
            game_state.spend_sp(AdvancedHypnosisSystem.RESISTANCE_BREAK_COST)

            # Track mastery
            if hasattr(game_state.player, 'mastery_level'):
                game_state.player.mastery_level.resistance_breaks += 1

            # Risk of suspicion
            if random.randint(1, 100) <= method['suspicion_risk']:
                char.player_suspicion = min(100, char.player_suspicion + 5)
                suspicion_msg = f"\n⚠️  {target_name} seems slightly suspicious (+5 suspicion)"
            else:
                suspicion_msg = ""

            message = f"✓ Resistance Breaking successful!"
            message += f"\nApproach: {approach.title()} - {method['description']}"
            message += f"\n{target_name}'s resistance: {old_resistance} → {char.resistance} (-{actual_reduction})"
            message += suspicion_msg

            return True, message, actual_reduction
        else:
            # Failed attempt
            char.player_suspicion = min(100, char.player_suspicion + method['suspicion_risk'])

            message = f"✗ Resistance Breaking failed!"
            message += f"\n{target_name} resisted your attempt and became more suspicious (+{method['suspicion_risk']} suspicion)"
            message += f"\nYou lost {AdvancedHypnosisSystem.RESISTANCE_BREAK_COST} SP with no benefit"

            game_state.spend_sp(AdvancedHypnosisSystem.RESISTANCE_BREAK_COST)

            return False, message, 0

    @staticmethod
    def get_mastery_level_description(mastery_level: int) -> str:
        """Get description for mastery level"""
        descriptions = {
            0: "Novice - Just beginning your journey",
            1: "Initiate - Learning the basics",
            2: "Apprentice - Developing skills",
            3: "Practitioner - Competent in fundamentals",
            4: "Adept - Skilled practitioner",
            5: "Expert - Highly skilled",
            6: "Advanced Expert - Exceptional ability",
            7: "Master - Near mastery",
            8: "Grand Master - Among the best",
            9: "Legendary - Rare mastery",
            10: "Transcendent Master - Peak achievement"
        }
        return descriptions.get(mastery_level, "Unknown")
