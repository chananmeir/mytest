"""
Advanced AI Personality Simulation System

Makes characters feel truly alive through:
- Dynamic personality evolution
- Emergent autonomous behaviors
- Realistic mood and opinion changes
- Long-term memory influence
- Relationship-driven actions
"""

import random
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# PERSONALITY STATE TRACKING
# ============================================================================

@dataclass
class PersonalityState:
    """Tracks the evolving personality state of a character"""
    character_name: str

    # Dynamic traits that evolve over time
    current_mood: str = "neutral"  # Changes frequently
    stress_level: int = 50  # 0-100
    trust_in_player: int = 50  # 0-100 (different from rapport)
    independence_level: int = 50  # 0-100 (how much they think for themselves)

    # Behavioral patterns learned from interactions
    player_influence_awareness: int = 0  # 0-100 (do they suspect manipulation?)
    emotional_vulnerability: int = 50  # 0-100 (current susceptibility)
    resistance_to_change: int = 50  # 0-100 (stubbornness)

    # Current concerns and preoccupations
    active_concerns: List[str] = field(default_factory=list)  # What's on their mind
    current_goals: List[str] = field(default_factory=list)  # What they want
    recent_observations: List[str] = field(default_factory=list)  # What they've noticed

    # Relationship dynamics
    alliance_preferences: Dict[str, int] = field(default_factory=dict)  # Who they prefer
    conflict_targets: List[str] = field(default_factory=list)  # Who they're at odds with

    # Behavioral tendencies (increase/decrease over time)
    assertiveness: int = 50  # 0-100
    openness_to_player: int = 50  # 0-100
    suspicion_tendency: int = 50  # 0-100

    # History tracking
    major_events_witnessed: List[Dict] = field(default_factory=list)
    emotional_history: List[Dict] = field(default_factory=list)  # Track mood over time

    # Autonomous action tracking
    last_autonomous_action_time: Optional[datetime] = None
    autonomous_action_frequency: int = 24  # Hours between actions


@dataclass
class EmergentAction:
    """Represents an autonomous character action"""
    action_id: str
    character_name: str
    action_type: str  # "conversation_initiation", "activity_suggestion", "concern_expression", "alliance_formation", "confrontation"
    description: str
    target_character: Optional[str] = None  # If action involves another character
    trigger_reason: str = ""
    potential_outcomes: List[str] = field(default_factory=list)
    likelihood: int = 50  # 0-100


# ============================================================================
# PERSONALITY SIMULATION ENGINE
# ============================================================================

class PersonalitySimulator:
    """Simulates realistic, evolving character personalities"""

    def __init__(self):
        self.personality_states: Dict[str, PersonalityState] = {}
        self.behavioral_memory: Dict[str, List[Dict]] = {}  # Track long-term patterns

    def initialize_personality_state(self, character, game_state) -> PersonalityState:
        """Initialize or retrieve personality state for a character"""
        if character.name not in self.personality_states:
            state = PersonalityState(character_name=character.name)

            # Initialize based on character's base personality
            state.stress_level = self._calculate_initial_stress(character)
            state.trust_in_player = min(character.rapport * 5, 100)
            state.independence_level = self._calculate_independence(character)
            state.emotional_vulnerability = self._calculate_vulnerability(character)
            state.resistance_to_change = character.resistance

            # Set initial goals based on character
            state.current_goals = self._generate_initial_goals(character)

            self.personality_states[character.name] = state

        return self.personality_states[character.name]

    def _calculate_initial_stress(self, character) -> int:
        """Calculate initial stress based on character traits"""
        stress = 50  # Base

        # Trait-based adjustments
        if 'anxious' in character.personality_traits:
            stress += 20
        if 'confident' in character.personality_traits:
            stress -= 15
        if 'perfectionist' in character.personality_traits:
            stress += 15

        # Job-based stress
        if character.occupation in ['Nurse Practitioner', 'Sales Manager']:
            stress += 10

        return max(0, min(100, stress))

    def _calculate_independence(self, character) -> int:
        """Calculate independence level"""
        independence = 50

        if 'assertive' in character.personality_traits:
            independence += 20
        if 'submissive' in character.personality_traits:
            independence -= 20
        if 'leader' in character.personality_traits:
            independence += 15
        if 'follower' in character.personality_traits:
            independence -= 15

        return max(0, min(100, independence))

    def _calculate_vulnerability(self, character) -> int:
        """Calculate emotional vulnerability"""
        vulnerability = 50

        # Emotional state affects vulnerability
        if character.emotional_state in ['sad', 'anxious', 'confused']:
            vulnerability += 20
        elif character.emotional_state in ['confident', 'defensive']:
            vulnerability -= 20

        # High suspicion reduces vulnerability
        vulnerability -= character.suspicion

        return max(0, min(100, vulnerability))

    def _generate_initial_goals(self, character) -> List[str]:
        """Generate initial character goals"""
        # Character-specific goals based on their nature
        goal_templates = {
            'Ruth': ['keep_family_happy', 'avoid_conflict', 'be_helpful'],
            'Tom': ['please_everyone', 'maintain_stability', 'avoid_responsibility'],
            'Dawn': ['maintain_family_harmony', 'preserve_traditions', 'guide_younger_generation'],
            'Melanie': ['succeed_at_career', 'prove_competence', 'maintain_independence'],
            'Derek': ['build_physical_strength', 'gain_respect', 'prove_worth'],
            'Vanessa': ['achieve_success', 'impress_others', 'maintain_status']
        }

        return goal_templates.get(character.name, ['maintain_relationships', 'pursue_happiness'])

    def update_personality_state(self, character, game_state, recent_events: List[Dict]) -> Dict[str, Any]:
        """
        Update personality state based on recent events

        Returns changes that occurred
        """
        state = self.initialize_personality_state(character, game_state)
        changes = {
            'mood_changed': False,
            'stress_changed': False,
            'new_concerns': [],
            'behavioral_shifts': []
        }

        # Process recent events
        for event in recent_events:
            self._process_event_impact(state, character, event, changes)

        # Natural drift over time
        self._apply_natural_drift(state, character, changes)

        # Update derived stats
        self._update_derived_stats(state, character)

        return changes

    def _process_event_impact(self, state: PersonalityState, character, event: Dict, changes: Dict):
        """Process how an event impacts personality"""
        event_type = event.get('type')

        if event_type == 'rapport_change':
            change_amount = event.get('amount', 0)

            # Trust changes with rapport, but not 1:1
            trust_change = int(change_amount * 0.5)
            state.trust_in_player = max(0, min(100, state.trust_in_player + trust_change))

            # Positive interactions reduce stress
            if change_amount > 0:
                state.stress_level = max(0, state.stress_level - abs(change_amount) * 2)
            else:
                state.stress_level = min(100, state.stress_level + abs(change_amount) * 3)
                changes['stress_changed'] = True

        elif event_type == 'phs_planted':
            # Being manipulated (even unknowingly) affects subconscious state
            state.emotional_vulnerability += 5
            state.independence_level = max(0, state.independence_level - 3)

            # Slight increase in influence awareness (unconscious recognition)
            state.player_influence_awareness = min(100, state.player_influence_awareness + 2)

            changes['behavioral_shifts'].append('increased_vulnerability')

        elif event_type == 'phs_detected':
            # Detected manipulation drastically changes personality
            state.player_influence_awareness = min(100, state.player_influence_awareness + 30)
            state.trust_in_player = max(0, state.trust_in_player - 40)
            state.resistance_to_change = min(100, state.resistance_to_change + 20)
            state.suspicion_tendency = min(100, state.suspicion_tendency + 25)

            state.active_concerns.append('player_manipulation_suspected')
            changes['new_concerns'].append('Suspects player manipulation')
            changes['behavioral_shifts'].append('major_trust_loss')

        elif event_type == 'gossip_received':
            # Gossip changes perceptions
            about_who = event.get('about')
            content = event.get('content')

            if about_who == 'player':
                # Negative gossip increases suspicion
                if event.get('sentiment') == 'negative':
                    state.suspicion_tendency += 5
                    state.openness_to_player = max(0, state.openness_to_player - 10)

        elif event_type == 'alliance_formed':
            # Forming alliances shifts behavior
            ally = event.get('with')
            state.alliance_preferences[ally] = state.alliance_preferences.get(ally, 50) + 20
            state.assertiveness = min(100, state.assertiveness + 10)

        elif event_type == 'emotional_state_change':
            old_state = event.get('old_state')
            new_state = event.get('new_state')

            # Track emotional history
            state.emotional_history.append({
                'timestamp': datetime.now().isoformat(),
                'from': old_state,
                'to': new_state
            })

            # Update current mood
            state.current_mood = new_state
            changes['mood_changed'] = True

    def _apply_natural_drift(self, state: PersonalityState, character, changes: Dict):
        """Characters naturally evolve over time"""

        # Stress naturally decreases (people cope)
        if state.stress_level > 30:
            state.stress_level = max(30, state.stress_level - 1)

        # Suspicion fades if no new incidents
        if state.suspicion_tendency > character.suspicion:
            state.suspicion_tendency -= 1

        # Trust slowly rebuilds
        if state.trust_in_player < character.rapport * 5:
            state.trust_in_player = min(100, state.trust_in_player + 1)

        # Emotional vulnerability fluctuates
        if character.emotional_state in ['relaxed', 'happy', 'content']:
            state.emotional_vulnerability = min(100, state.emotional_vulnerability + 2)
        elif character.emotional_state in ['defensive', 'angry']:
            state.emotional_vulnerability = max(0, state.emotional_vulnerability - 5)

    def _update_derived_stats(self, state: PersonalityState, character):
        """Update character stats based on personality state"""

        # High stress increases resistance
        if state.stress_level > 70:
            character.resistance = min(100, character.resistance + 5)

        # Low trust increases suspicion
        if state.trust_in_player < 30:
            character.suspicion = min(100, character.suspicion + 2)

        # High influence awareness makes them more resistant
        if state.player_influence_awareness > 50:
            character.resistance = min(100, character.resistance + state.player_influence_awareness // 10)

    def generate_dynamic_personality_context(self, character, game_state) -> str:
        """
        Generate dynamic personality context for LLM prompts

        This adds real-time personality state to character responses
        """
        state = self.initialize_personality_state(character, game_state)

        context = f"\n=== DYNAMIC PERSONALITY STATE ===\n"

        # Current mental state
        context += f"CURRENT MENTAL STATE:\n"
        context += f"- Mood: {state.current_mood.upper()}\n"
        context += f"- Stress Level: {state.stress_level}/100 "
        if state.stress_level > 70:
            context += "(HIGH STRESS - shorter temper, less patient)\n"
        elif state.stress_level < 30:
            context += "(RELAXED - more open, easier to talk to)\n"
        else:
            context += "(MODERATE)\n"

        # Trust and vulnerability
        context += f"\nTRUST & VULNERABILITY:\n"
        context += f"- Trust in Player: {state.trust_in_player}/100\n"
        context += f"- Emotional Vulnerability: {state.emotional_vulnerability}/100\n"

        if state.player_influence_awareness > 30:
            context += f"- Manipulation Awareness: {state.player_influence_awareness}/100 "
            context += "(You have an unconscious feeling something is off about the player)\n"

        # Current concerns
        if state.active_concerns:
            context += f"\nCURRENT CONCERNS ON YOUR MIND:\n"
            for concern in state.active_concerns[-3:]:  # Last 3 concerns
                context += f"- {concern}\n"

        # Current goals
        if state.current_goals:
            context += f"\nWHAT YOU WANT RIGHT NOW:\n"
            for goal in state.current_goals[:2]:  # Top 2 goals
                context += f"- {goal.replace('_', ' ').title()}\n"

        # Recent observations
        if state.recent_observations:
            context += f"\nRECENT OBSERVATIONS:\n"
            for obs in state.recent_observations[-2:]:
                context += f"- {obs}\n"

        # Alliance preferences
        if state.alliance_preferences:
            top_ally = max(state.alliance_preferences.items(), key=lambda x: x[1])
            if top_ally[1] > 60:
                context += f"\nYou feel particularly close to {top_ally[0]} right now.\n"

        # Conflicts
        if state.conflict_targets:
            context += f"\nYou're currently at odds with: {', '.join(state.conflict_targets)}\n"

        # Behavioral tendencies
        context += f"\nCURRENT BEHAVIORAL TENDENCIES:\n"
        context += f"- Assertiveness: {state.assertiveness}/100\n"
        context += f"- Openness to Player: {state.openness_to_player}/100\n"
        context += f"- Independence: {state.independence_level}/100\n"

        context += "\nAdjust your responses based on these dynamic states!\n"

        return context

    def predict_character_reaction(self, character, action_type: str, game_state) -> Dict[str, Any]:
        """
        Predict how character will react to a specific action

        More sophisticated than simple rapport checks
        """
        state = self.initialize_personality_state(character, game_state)

        # Base reaction influenced by multiple factors
        base_favorability = character.rapport * 5  # 0-100 scale

        # Modify based on personality state
        if state.stress_level > 70:
            base_favorability -= 20  # Stressed = less receptive

        if state.trust_in_player < 30:
            base_favorability -= 30  # Low trust = resistant

        if state.emotional_vulnerability > 70:
            base_favorability += 15  # Vulnerable = more open

        if state.player_influence_awareness > 50:
            base_favorability -= 25  # Suspicious of influence

        # Action-type modifiers
        if action_type == 'hypnosis_attempt':
            if state.independence_level > 70:
                base_favorability -= 30
            if state.resistance_to_change > 70:
                base_favorability -= 20
            if character.emotional_state in ['defensive', 'suspicious']:
                base_favorability -= 40

        elif action_type == 'emotional_support':
            if state.stress_level > 60:
                base_favorability += 25
            if character.emotional_state in ['sad', 'anxious']:
                base_favorability += 20

        elif action_type == 'request_favor':
            if state.trust_in_player > 70:
                base_favorability += 20
            if state.stress_level > 70:
                base_favorability -= 15

        # Calculate final probability
        success_probability = max(0, min(100, base_favorability))

        return {
            'success_probability': success_probability,
            'base_favorability': base_favorability,
            'modifiers': {
                'stress': -20 if state.stress_level > 70 else 0,
                'trust': -30 if state.trust_in_player < 30 else 0,
                'vulnerability': 15 if state.emotional_vulnerability > 70 else 0,
                'awareness': -25 if state.player_influence_awareness > 50 else 0
            },
            'recommendation': self._generate_recommendation(success_probability, state)
        }

    def _generate_recommendation(self, probability: int, state: PersonalityState) -> str:
        """Generate strategic recommendation"""
        if probability > 70:
            return "High chance of success - proceed confidently"
        elif probability > 40:
            if state.stress_level > 60:
                return "Moderate chance - consider reducing their stress first"
            elif state.trust_in_player < 50:
                return "Moderate chance - build more trust before attempting"
            else:
                return "Moderate chance - proceed with caution"
        else:
            if state.player_influence_awareness > 50:
                return "Low chance - they're suspicious. Wait for suspicion to fade"
            elif state.independence_level > 70:
                return "Low chance - they're too independent. Build rapport first"
            else:
                return "Low chance - not recommended at this time"


# ============================================================================
# EMERGENT BEHAVIOR ENGINE
# ============================================================================

class EmergentBehaviorEngine:
    """Generates autonomous character actions based on personality state"""

    def __init__(self, personality_simulator: PersonalitySimulator):
        self.personality_simulator = personality_simulator

    def generate_autonomous_actions(self, character, game_state) -> List[EmergentAction]:
        """
        Generate possible autonomous actions for a character

        Characters will proactively do things based on their state
        """
        state = self.personality_simulator.initialize_personality_state(character, game_state)
        possible_actions = []

        # Check if enough time has passed for autonomous action
        if state.last_autonomous_action_time:
            hours_since_last = (datetime.now() - state.last_autonomous_action_time).total_seconds() / 3600
            if hours_since_last < state.autonomous_action_frequency:
                return []

        # Generate actions based on current state

        # 1. Express concerns if stress is high
        if state.stress_level > 70 and state.trust_in_player > 50:
            possible_actions.append(EmergentAction(
                action_id=f"express_stress_{character.name}",
                character_name=character.name,
                action_type="concern_expression",
                description=f"{character.name} seeks you out to talk about their stress",
                trigger_reason="High stress + trusts player",
                potential_outcomes=[
                    "Opportunity to provide emotional support",
                    "Could plant PHS during vulnerable moment",
                    "Builds rapport if handled well"
                ],
                likelihood=70
            ))

        # 2. Form alliances if suspicious of player
        if state.player_influence_awareness > 60 or character.suspicion > 50:
            # Find potential allies
            from systems.relationship_web import RelationshipWeb

            for other_name, other_char in game_state.characters.items():
                if other_name == character.name:
                    continue

                relationship_score = character.relationships.get(other_name, 5)
                other_suspicion = other_char.suspicion

                if relationship_score > 12 and other_suspicion > 30:
                    possible_actions.append(EmergentAction(
                        action_id=f"alliance_{character.name}_{other_name}",
                        character_name=character.name,
                        action_type="alliance_formation",
                        description=f"{character.name} privately talks to {other_name} about concerns regarding you",
                        target_character=other_name,
                        trigger_reason="Both suspicious of player",
                        potential_outcomes=[
                            "Alliance forms against player",
                            "Increases coordinated resistance",
                            "May lead to intervention"
                        ],
                        likelihood=state.player_influence_awareness
                    ))

        # 3. Initiate conversation with player about goals
        if state.current_goals and state.trust_in_player > 60:
            possible_actions.append(EmergentAction(
                action_id=f"goal_conversation_{character.name}",
                character_name=character.name,
                action_type="conversation_initiation",
                description=f"{character.name} wants to discuss their goals and aspirations with you",
                trigger_reason="High trust + active goals",
                potential_outcomes=[
                    "Learn about character's deeper motivations",
                    "Opportunity for subtle influence",
                    "Strengthens bond"
                ],
                likelihood=65
            ))

        # 4. Confront player if awareness is very high
        if state.player_influence_awareness > 80:
            possible_actions.append(EmergentAction(
                action_id=f"confrontation_{character.name}",
                character_name=character.name,
                action_type="confrontation",
                description=f"{character.name} confronts you about feeling manipulated",
                trigger_reason="Very high manipulation awareness",
                potential_outcomes=[
                    "Major crisis - must handle carefully",
                    "Could lead to game over if mishandled",
                    "Chance to gaslight or come clean"
                ],
                likelihood=90
            ))

        # 5. Suggest activities based on stress/mood
        if state.stress_level > 60 and character.rapport > 8:
            possible_actions.append(EmergentAction(
                action_id=f"activity_suggestion_{character.name}",
                character_name=character.name,
                action_type="activity_suggestion",
                description=f"{character.name} suggests doing something together to relax",
                trigger_reason="High stress + good rapport",
                potential_outcomes=[
                    "Shared activity opportunity",
                    "Natural rapport building",
                    "PHS opportunity in relaxed setting"
                ],
                likelihood=55
            ))

        # 6. Seek emotional support if vulnerable
        if state.emotional_vulnerability > 75 and state.trust_in_player > 65:
            possible_actions.append(EmergentAction(
                action_id=f"seek_support_{character.name}",
                character_name=character.name,
                action_type="emotional_support_seeking",
                description=f"{character.name} comes to you feeling vulnerable and needing support",
                trigger_reason="High vulnerability + high trust",
                potential_outcomes=[
                    "Prime PHS opportunity",
                    "Major rapport gain if supportive",
                    "Deepens emotional bond"
                ],
                likelihood=80
            ))

        # 7. Share observations about family dynamics
        if state.recent_observations and state.openness_to_player > 60:
            possible_actions.append(EmergentAction(
                action_id=f"share_observations_{character.name}",
                character_name=character.name,
                action_type="observation_sharing",
                description=f"{character.name} shares what they've noticed about the family lately",
                trigger_reason="Has observations + open to player",
                potential_outcomes=[
                    "Learn about family dynamics",
                    "Understand relationship web better",
                    "May reveal suspicions"
                ],
                likelihood=50
            ))

        return possible_actions

    def select_action_to_trigger(self, possible_actions: List[EmergentAction]) -> Optional[EmergentAction]:
        """Select which autonomous action should trigger based on likelihood"""
        if not possible_actions:
            return None

        # Weight by likelihood
        total_likelihood = sum(action.likelihood for action in possible_actions)

        if total_likelihood == 0:
            return None

        rand_value = random.randint(0, total_likelihood)
        current_sum = 0

        for action in possible_actions:
            current_sum += action.likelihood
            if rand_value <= current_sum:
                return action

        return possible_actions[-1]

    def execute_autonomous_action(self, action: EmergentAction, game_state) -> Dict[str, Any]:
        """Execute an autonomous action and return results"""
        character = game_state.characters.get(action.character_name)

        if not character:
            return {'success': False, 'error': 'Character not found'}

        result = {
            'success': True,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'narrative': '',
            'game_effects': []
        }

        # Update personality state
        state = self.personality_simulator.personality_states.get(action.character_name)
        if state:
            state.last_autonomous_action_time = datetime.now()

        # Generate narrative and effects based on action type
        if action.action_type == "concern_expression":
            result['narrative'] = f"{character.name} approaches you with a concerned expression. They clearly have something weighing on their mind."
            result['game_effects'].append({
                'type': 'conversation_opportunity',
                'character': character.name,
                'topic': 'stress_and_concerns'
            })

        elif action.action_type == "alliance_formation":
            result['narrative'] = f"You notice {character.name} and {action.target_character} having a private conversation. They stop when they see you."

            # Form alliance
            from systems.relationship_web import RelationshipWeb
            alliance_result = RelationshipWeb.form_alliance(
                character,
                game_state.characters[action.target_character],
                reason="shared_suspicion"
            )

            result['game_effects'].append({
                'type': 'alliance_formed',
                'members': [character.name, action.target_character],
                'reason': 'shared_suspicion'
            })

        elif action.action_type == "conversation_initiation":
            result['narrative'] = f"{character.name} seeks you out. 'Hey, got a minute? I'd like to talk about something.'"
            result['game_effects'].append({
                'type': 'conversation_initiated',
                'character': character.name,
                'mood': 'open'
            })

        elif action.action_type == "confrontation":
            result['narrative'] = f"{character.name}'s expression is serious. 'We need to talk. Something's been bothering me about... us. About how I've been acting around you.'"
            result['game_effects'].append({
                'type': 'crisis_event',
                'crisis_level': 'high',
                'character': character.name
            })

        elif action.action_type == "activity_suggestion":
            result['narrative'] = f"{character.name} suggests, 'Want to do something together? I could use a break.'"
            result['game_effects'].append({
                'type': 'activity_opportunity',
                'character': character.name
            })

        elif action.action_type == "emotional_support_seeking":
            result['narrative'] = f"{character.name} seems vulnerable. 'Can we talk? I'm... not doing great right now.'"
            result['game_effects'].append({
                'type': 'vulnerability_opportunity',
                'character': character.name,
                'phs_bonus': 25
            })

        elif action.action_type == "observation_sharing":
            if state and state.recent_observations:
                obs = random.choice(state.recent_observations)
                result['narrative'] = f"{character.name} mentions, 'Have you noticed {obs}?'"
            else:
                result['narrative'] = f"{character.name} shares some observations about the family."

        return result


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

personality_simulator = PersonalitySimulator()
emergent_behavior_engine = EmergentBehaviorEngine(personality_simulator)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_dynamic_personality_context(character, game_state) -> str:
    """Get dynamic personality context for LLM prompts"""
    return personality_simulator.generate_dynamic_personality_context(character, game_state)


def update_character_personality(character, game_state, recent_events: List[Dict]) -> Dict[str, Any]:
    """Update character personality based on recent events"""
    return personality_simulator.update_personality_state(character, game_state, recent_events)


def predict_reaction(character, action_type: str, game_state) -> Dict[str, Any]:
    """Predict character reaction to action"""
    return personality_simulator.predict_character_reaction(character, action_type, game_state)


def generate_emergent_actions(character, game_state) -> List[EmergentAction]:
    """Generate possible emergent actions"""
    return emergent_behavior_engine.generate_autonomous_actions(character, game_state)


def trigger_emergent_behavior(game_state) -> Optional[Dict[str, Any]]:
    """
    Check all characters and potentially trigger an emergent behavior

    Call this periodically (e.g., on time advancement)
    """
    all_actions = []

    for character in game_state.characters.values():
        actions = generate_emergent_actions(character, game_state)
        all_actions.extend(actions)

    if not all_actions:
        return None

    # Select and execute one action
    selected_action = emergent_behavior_engine.select_action_to_trigger(all_actions)

    if selected_action:
        return emergent_behavior_engine.execute_autonomous_action(selected_action, game_state)

    return None
