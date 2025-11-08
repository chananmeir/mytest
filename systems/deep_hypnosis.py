"""
Deep Hypnosis System - Advanced trance induction and depth mechanics

Implements:
- Multiple induction techniques (PMR, eye fixation, confusion, breathing)
- Character-specific vulnerabilities to different methods
- Trance depth levels (light, medium, deep)
- Fractionation mechanics (in/out cycles for deeper effects)
- Depth-based suggestion strength
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random
from enum import Enum


class InductionTechnique(Enum):
    """Available hypnosis induction techniques"""
    PROGRESSIVE_RELAXATION = "progressive_relaxation"
    EYE_FIXATION = "eye_fixation"
    CONFUSION = "confusion"
    BREATHING_FOCUS = "breathing_focus"
    CONVERSATIONAL = "conversational"


class TranceDep(Enum):
    """Trance depth levels"""
    NONE = 0
    LIGHT = 1
    MEDIUM = 2
    DEEP = 3


@dataclass
class InductionMethod:
    """Defines an induction technique"""
    technique: InductionTechnique
    name: str
    description: str
    base_success_rate: float  # 0.0 to 1.0
    depth_gain: int  # How much depth it adds
    sp_cost: int
    duration_minutes: int
    icon: str
    flavor_text: str
    unlock_requirement: str = "none"  # Skill level required


@dataclass
class TranceState:
    """Tracks a character's current trance state"""
    is_in_trance: bool = False
    current_depth: int = 0  # 0-100
    max_depth_reached: int = 0  # Highest depth ever reached
    fractionation_count: int = 0  # Times put in and out of trance
    fractionation_multiplier: float = 1.0  # Depth gain multiplier
    last_induction_technique: Optional[InductionTechnique] = None
    trance_history: List[Dict] = field(default_factory=list)  # History of inductions

    def get_depth_level(self) -> TranceDep:
        """Get the current trance depth level"""
        if not self.is_in_trance or self.current_depth == 0:
            return TranceDep.NONE
        elif self.current_depth <= 33:
            return TranceDep.LIGHT
        elif self.current_depth <= 66:
            return TranceDep.MEDIUM
        else:
            return TranceDep.DEEP

    def get_depth_name(self) -> str:
        """Get human-readable depth name"""
        level = self.get_depth_level()
        if level == TranceDep.NONE:
            return "Awake"
        elif level == TranceDep.LIGHT:
            return "Light Trance"
        elif level == TranceDep.MEDIUM:
            return "Medium Trance"
        elif level == TranceDep.DEEP:
            return "Deep Trance"
        return "Unknown"


class DeepHypnosisSystem:
    """Manages deep hypnosis mechanics"""

    # Define all induction techniques
    INDUCTION_TECHNIQUES = {
        InductionTechnique.PROGRESSIVE_RELAXATION: InductionMethod(
            technique=InductionTechnique.PROGRESSIVE_RELAXATION,
            name="Progressive Muscle Relaxation",
            description="Guide them to relax each muscle group, one by one, inducing a calm, receptive state.",
            base_success_rate=0.75,
            depth_gain=20,
            sp_cost=1,
            duration_minutes=20,
            icon="🧘",
            flavor_text="Starting with your toes, feel the tension melting away...",
            unlock_requirement="none"
        ),
        InductionTechnique.EYE_FIXATION: InductionMethod(
            technique=InductionTechnique.EYE_FIXATION,
            name="Eye Fixation",
            description="Have them focus on a fixed point until their eyes grow heavy and their mind drifts.",
            base_success_rate=0.70,
            depth_gain=25,
            sp_cost=1,
            duration_minutes=15,
            icon="👁️",
            flavor_text="Focus on this point... watch how it seems to shift...",
            unlock_requirement="none"
        ),
        InductionTechnique.CONFUSION: InductionMethod(
            technique=InductionTechnique.CONFUSION,
            name="Confusion Technique",
            description="Overwhelm their conscious mind with complex patterns, allowing the subconscious to take over.",
            base_success_rate=0.60,
            depth_gain=35,
            sp_cost=2,
            duration_minutes=25,
            icon="🌀",
            flavor_text="Think about not thinking about what you're thinking...",
            unlock_requirement="intermediate"
        ),
        InductionTechnique.BREATHING_FOCUS: InductionMethod(
            technique=InductionTechnique.BREATHING_FOCUS,
            name="Breathing Focus",
            description="Sync their breathing with suggestions, each breath taking them deeper.",
            base_success_rate=0.80,
            depth_gain=18,
            sp_cost=1,
            duration_minutes=12,
            icon="💨",
            flavor_text="Breathe in deeply... and out... deeper with each breath...",
            unlock_requirement="none"
        ),
        InductionTechnique.CONVERSATIONAL: InductionMethod(
            technique=InductionTechnique.CONVERSATIONAL,
            name="Conversational Hypnosis",
            description="Subtly guide them into trance through normal conversation and embedded commands.",
            base_success_rate=0.65,
            depth_gain=15,
            sp_cost=2,
            duration_minutes=30,
            icon="💬",
            flavor_text="You know how sometimes you just... relax without realizing...",
            unlock_requirement="advanced"
        )
    }

    # Character vulnerabilities to techniques (will be set per character)
    DEFAULT_VULNERABILITIES = {
        InductionTechnique.PROGRESSIVE_RELAXATION: 1.0,
        InductionTechnique.EYE_FIXATION: 1.0,
        InductionTechnique.CONFUSION: 1.0,
        InductionTechnique.BREATHING_FOCUS: 1.0,
        InductionTechnique.CONVERSATIONAL: 1.0
    }

    @staticmethod
    def initialize_trance_state(character):
        """Initialize trance state for a character"""
        if not hasattr(character, 'trance_state'):
            character.trance_state = TranceState()

        # Set character-specific vulnerabilities if not set
        if not hasattr(character, 'technique_vulnerabilities'):
            character.technique_vulnerabilities = DeepHypnosisSystem._generate_vulnerabilities(character)

    @staticmethod
    def _generate_vulnerabilities(character) -> Dict[InductionTechnique, float]:
        """Generate character-specific vulnerabilities to techniques"""
        # Base vulnerabilities
        vulns = DeepHypnosisSystem.DEFAULT_VULNERABILITIES.copy()

        # Personality-based adjustments
        personality = character.personality.lower() if hasattr(character, 'personality') else ""

        # Analytical/logical types more vulnerable to confusion
        if any(trait in personality for trait in ['analytical', 'logical', 'professional']):
            vulns[InductionTechnique.CONFUSION] = 1.3
            vulns[InductionTechnique.CONVERSATIONAL] = 1.2

        # Anxious/nervous types more vulnerable to relaxation
        if any(trait in personality for trait in ['anxious', 'nervous', 'tense']):
            vulns[InductionTechnique.PROGRESSIVE_RELAXATION] = 1.4
            vulns[InductionTechnique.BREATHING_FOCUS] = 1.3

        # Creative/artistic types more vulnerable to fixation
        if any(trait in personality for trait in ['creative', 'artistic', 'imaginative']):
            vulns[InductionTechnique.EYE_FIXATION] = 1.3
            vulns[InductionTechnique.CONVERSATIONAL] = 1.2

        # Athletic/physical types respond well to body-focused methods
        if any(trait in personality for trait in ['athletic', 'physical', 'active']):
            vulns[InductionTechnique.PROGRESSIVE_RELAXATION] = 1.25

        # Add some random variation
        for technique in vulns:
            vulns[technique] *= random.uniform(0.9, 1.1)

        return vulns

    @staticmethod
    def attempt_induction(game_state, character_name: str, technique: InductionTechnique) -> Dict:
        """Attempt to induce or deepen trance using a specific technique"""
        character = game_state.characters.get(character_name)
        if not character:
            return {'success': False, 'error': 'Character not found'}

        # Initialize trance state
        DeepHypnosisSystem.initialize_trance_state(character)

        # Get the induction method
        method = DeepHypnosisSystem.INDUCTION_TECHNIQUES.get(technique)
        if not method:
            return {'success': False, 'error': 'Invalid technique'}

        # Check SP cost
        if game_state.player.suggestion_points < method.sp_cost:
            return {'success': False, 'error': f'Not enough SP (need {method.sp_cost})'}

        # Check skill level requirement
        player_skill = game_state.player.hypnosis_knowledge.skill_level
        if not DeepHypnosisSystem._meets_skill_requirement(player_skill, method.unlock_requirement):
            return {'success': False, 'error': f'Requires {method.unlock_requirement} skill level'}

        # Calculate success chance
        base_chance = method.base_success_rate

        # Apply character vulnerability
        vulnerability_multiplier = character.technique_vulnerabilities.get(technique, 1.0)

        # Apply resistance
        resistance_modifier = (100 - character.resistance) / 100.0

        # Apply rapport bonus
        rapport_bonus = character.rapport * 0.02  # +2% per rapport

        # Apply fractionation bonus (if already been in trance before)
        fractionation_bonus = character.trance_state.fractionation_multiplier - 1.0

        # Calculate final success chance
        success_chance = base_chance * vulnerability_multiplier * resistance_modifier
        success_chance += rapport_bonus + fractionation_bonus
        success_chance = min(0.95, success_chance)  # Cap at 95%

        # Attempt induction
        success = random.random() < success_chance

        results = {
            'success': success,
            'technique': method.name,
            'technique_enum': technique.value,
            'changes': [],
            'messages': []
        }

        if success:
            # Deduct SP
            game_state.player.suggestion_points -= method.sp_cost

            # Calculate depth gain
            depth_gain = method.depth_gain

            # Apply fractionation multiplier
            depth_gain = int(depth_gain * character.trance_state.fractionation_multiplier)

            # Apply to character
            old_depth = character.trance_state.current_depth
            character.trance_state.current_depth = min(100, character.trance_state.current_depth + depth_gain)
            character.trance_state.is_in_trance = True
            character.trance_state.last_induction_technique = technique

            # Update max depth reached
            if character.trance_state.current_depth > character.trance_state.max_depth_reached:
                character.trance_state.max_depth_reached = character.trance_state.current_depth

            # Record in history
            character.trance_state.trance_history.append({
                'technique': technique.value,
                'depth_before': old_depth,
                'depth_after': character.trance_state.current_depth,
                'timestamp': game_state.time_system.get_formatted_datetime()
            })

            # Get depth level
            depth_level = character.trance_state.get_depth_level()

            results['depth_gain'] = depth_gain
            results['new_depth'] = character.trance_state.current_depth
            results['depth_level'] = character.trance_state.get_depth_name()
            results['messages'].append(f"✨ {method.name} successful!")
            results['messages'].append(f"💫 Trance depth: {character.trance_state.current_depth}% ({character.trance_state.get_depth_name()})")
            results['changes'].append(f"Trance depth +{depth_gain}% (now {character.trance_state.current_depth}%)")

            # Special messages for depth milestones
            if depth_level == TranceDep.LIGHT and old_depth == 0:
                results['messages'].append(f"{character.name}'s eyes begin to glaze over... they're entering a light trance.")
            elif depth_level == TranceDep.MEDIUM and old_depth <= 33:
                results['messages'].append(f"{character.name}'s breathing slows... they're falling deeper into a medium trance.")
            elif depth_level == TranceDep.DEEP and old_depth <= 66:
                results['messages'].append(f"{character.name} is completely relaxed and receptive... they're in a deep trance!")

            # Advance time
            game_state.game_time.advance_minutes(method.duration_minutes)
            results['time_passed'] = method.duration_minutes

        else:
            # Failed induction
            results['messages'].append(f"❌ {method.name} failed - {character.name} resisted.")
            results['messages'].append(f"💭 {character.name} seems distracted or uncomfortable with this approach.")

            # Still advance time (wasted time)
            game_state.game_time.advance_minutes(method.duration_minutes // 2)
            results['time_passed'] = method.duration_minutes // 2

        return results

    @staticmethod
    def wake_from_trance(game_state, character_name: str) -> Dict:
        """Wake a character from trance (for fractionation)"""
        character = game_state.characters.get(character_name)
        if not character:
            return {'success': False, 'error': 'Character not found'}

        DeepHypnosisSystem.initialize_trance_state(character)

        if not character.trance_state.is_in_trance:
            return {'success': False, 'error': 'Character is not in trance'}

        # Record depth before waking
        depth_before_wake = character.trance_state.current_depth

        # Wake them up
        character.trance_state.is_in_trance = False

        # Increase fractionation count
        character.trance_state.fractionation_count += 1

        # Increase fractionation multiplier (each wake/sleep cycle makes them more suggestible)
        character.trance_state.fractionation_multiplier += 0.15  # +15% per fractionation
        character.trance_state.fractionation_multiplier = min(2.5, character.trance_state.fractionation_multiplier)  # Cap at 2.5x

        # Depth partially retained (they remember being in trance)
        character.trance_state.current_depth = int(depth_before_wake * 0.4)  # Retain 40% of depth

        results = {
            'success': True,
            'messages': [
                f"👁️ {character.name} opens their eyes and awakens from trance.",
                f"🔄 Fractionation count: {character.trance_state.fractionation_count}",
                f"⚡ Fractionation multiplier: {character.trance_state.fractionation_multiplier:.1f}x",
                f"💭 When you put them back under, they'll go even deeper..."
            ],
            'fractionation_count': character.trance_state.fractionation_count,
            'fractionation_multiplier': character.trance_state.fractionation_multiplier,
            'depth_retained': character.trance_state.current_depth
        }

        # Advance time (waking takes a moment)
        game_state.game_time.advance_minutes(2)

        return results

    @staticmethod
    def plant_deep_suggestion(game_state, character_name: str, trigger: str, response: str) -> Dict:
        """Plant a PHS with depth-modified effectiveness"""
        character = game_state.characters.get(character_name)
        if not character:
            return {'success': False, 'error': 'Character not found'}

        DeepHypnosisSystem.initialize_trance_state(character)

        if not character.trance_state.is_in_trance:
            return {'success': False, 'error': 'Character must be in trance to plant deep suggestions'}

        # Get depth level
        depth = character.trance_state.current_depth
        depth_level = character.trance_state.get_depth_level()

        # Calculate effectiveness based on depth
        if depth_level == TranceDep.LIGHT:
            # Light trance: Simple suggestions only, lower activation chance
            base_activation = 30
            suggestion_types_allowed = ['simple', 'surface']
        elif depth_level == TranceDep.MEDIUM:
            # Medium trance: Behavioral changes, good activation chance
            base_activation = 50
            suggestion_types_allowed = ['simple', 'surface', 'behavioral']
        elif depth_level == TranceDep.DEEP:
            # Deep trance: Core personality shifts, very high activation chance
            base_activation = 70
            suggestion_types_allowed = ['simple', 'surface', 'behavioral', 'personality', 'core']
        else:
            return {'success': False, 'error': 'Not deep enough for suggestions'}

        # Apply fractionation bonus to activation chance
        activation_chance = base_activation + (character.trance_state.fractionation_count * 3)  # +3% per fractionation
        activation_chance = min(95, activation_chance)

        # Use existing hypnosis system to plant the PHS
        from systems.hypnosis import HypnosisSystem

        # Plant with modified activation chance
        result = HypnosisSystem.plant_phs(
            game_state,
            character_name,
            trigger,
            response,
            base_activation_chance=activation_chance
        )

        if result.get('success'):
            result['messages'].insert(0, f"🌀 Deep {character.trance_state.get_depth_name()} allows powerful suggestion...")
            result['depth_bonus'] = activation_chance - base_activation

        return result

    @staticmethod
    def get_available_techniques(game_state) -> List[Dict]:
        """Get list of available induction techniques based on skill level"""
        player_skill = game_state.player.hypnosis_knowledge.skill_level

        available = []
        for technique, method in DeepHypnosisSystem.INDUCTION_TECHNIQUES.items():
            if DeepHypnosisSystem._meets_skill_requirement(player_skill, method.unlock_requirement):
                available.append({
                    'technique': technique.value,
                    'name': method.name,
                    'description': method.description,
                    'icon': method.icon,
                    'sp_cost': method.sp_cost,
                    'duration': method.duration_minutes,
                    'depth_gain': method.depth_gain,
                    'flavor_text': method.flavor_text
                })

        return available

    @staticmethod
    def get_character_vulnerabilities(character) -> Dict:
        """Get character's vulnerabilities to each technique"""
        DeepHypnosisSystem.initialize_trance_state(character)

        vulns = {}
        for technique, multiplier in character.technique_vulnerabilities.items():
            method = DeepHypnosisSystem.INDUCTION_TECHNIQUES.get(technique)
            if method:
                vulns[technique.value] = {
                    'name': method.name,
                    'multiplier': round(multiplier, 2),
                    'effectiveness': DeepHypnosisSystem._get_effectiveness_label(multiplier)
                }

        return vulns

    @staticmethod
    def _get_effectiveness_label(multiplier: float) -> str:
        """Get effectiveness label from multiplier"""
        if multiplier >= 1.3:
            return "Very Effective"
        elif multiplier >= 1.1:
            return "Effective"
        elif multiplier >= 0.9:
            return "Normal"
        else:
            return "Less Effective"

    @staticmethod
    def _meets_skill_requirement(player_skill: str, requirement: str) -> bool:
        """Check if player meets skill requirement"""
        skill_levels = ['none', 'novice', 'intermediate', 'advanced', 'expert']

        if requirement == 'none':
            return True

        try:
            player_level = skill_levels.index(player_skill.lower())
            required_level = skill_levels.index(requirement.lower())
            return player_level >= required_level
        except ValueError:
            return True

    @staticmethod
    def decay_trance_depth(character, minutes_passed: int):
        """Naturally decay trance depth over time when not reinforced"""
        if not hasattr(character, 'trance_state') or not character.trance_state.is_in_trance:
            return

        # Decay rate: 5% per hour when not actively maintaining trance
        decay_amount = (minutes_passed / 60) * 5

        character.trance_state.current_depth = max(0, character.trance_state.current_depth - decay_amount)

        # If depth reaches 0, wake them up
        if character.trance_state.current_depth <= 0:
            character.trance_state.is_in_trance = False
