"""
Dynamic Random Events System
Adds unpredictable gameplay elements that create emergent stories
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import random
from datetime import datetime


@dataclass
class EventOption:
    """A choice the player can make in response to an event"""
    option_id: str
    text: str

    # Requirements
    requires_rapport: Optional[int] = None
    requires_sp: Optional[int] = None
    requires_skill_level: Optional[int] = None

    # Costs
    sp_cost: int = 0
    money_cost: int = 0
    time_cost: int = 0  # Minutes

    # Direct effects
    rapport_changes: Dict[str, int] = field(default_factory=dict)  # {character: change}
    emotional_state_changes: Dict[str, str] = field(default_factory=dict)  # {character: new_state}
    suspicion_changes: Dict[str, int] = field(default_factory=dict)  # {character: change}
    sp_gain: int = 0
    money_gain: int = 0

    # PHS opportunities
    allows_phs: bool = False
    phs_target: Optional[str] = None
    phs_success_bonus: int = 0
    phs_detection_risk: int = 0  # 0-100, chance of being caught

    # Social effects
    social_effect: Optional[str] = None  # Description of social consequence
    observers: List[str] = field(default_factory=list)  # Who witnesses this choice

    # Advanced effects
    triggers_follow_up_event: Optional[str] = None
    unlocks_opportunity: Optional[str] = None

    # Outcome text
    success_text: str = ""
    failure_text: str = ""

    # Success chance (if applicable)
    success_chance: int = 100  # 0-100


@dataclass
class DynamicEvent:
    """A random event that occurs during gameplay"""
    event_id: str
    event_type: str  # 'encounter', 'initiated', 'opportunity', 'crisis', 'visitor', 'memory_trigger'

    # Basic info
    title: str
    description: str
    icon: str = "🎲"

    # Participants
    primary_character: Optional[str] = None
    secondary_characters: List[str] = field(default_factory=list)
    observers: List[str] = field(default_factory=list)

    # Timing
    duration_minutes: int = 0  # How long the event takes
    window_expires_in: Optional[int] = None  # For opportunities (minutes)

    # Trigger conditions
    min_rapport: Dict[str, int] = field(default_factory=dict)  # {character: min_rapport}
    max_rapport: Dict[str, int] = field(default_factory=dict)
    min_suspicion: Dict[str, int] = field(default_factory=dict)
    max_suspicion: Dict[str, int] = field(default_factory=dict)
    required_emotional_states: Dict[str, List[str]] = field(default_factory=dict)
    required_location: Optional[str] = None
    required_time_period: Optional[str] = None
    alliance_strength_threshold: Optional[int] = None

    # Player choices
    options: List[EventOption] = field(default_factory=list)

    # Metadata
    weight: int = 10  # Higher = more likely
    cooldown_hours: int = 24  # How long before this event can trigger again
    one_time: bool = False  # Can only happen once

    # Context
    urgency_level: str = "normal"  # 'low', 'normal', 'high', 'critical'
    pressure: bool = False  # Must respond quickly

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'primary_character': self.primary_character,
            'secondary_characters': self.secondary_characters,
            'observers': self.observers,
            'duration_minutes': self.duration_minutes,
            'window_expires_in': self.window_expires_in,
            'options': [
                {
                    'option_id': opt.option_id,
                    'text': opt.text,
                    'requires_rapport': opt.requires_rapport,
                    'requires_sp': opt.requires_sp,
                    'sp_cost': opt.sp_cost,
                    'allows_phs': opt.allows_phs,
                    'phs_success_bonus': opt.phs_success_bonus,
                    'social_effect': opt.social_effect
                }
                for opt in self.options
            ],
            'urgency_level': self.urgency_level,
            'pressure': self.pressure
        }


class DynamicEventSystem:
    """
    Manages dynamic random events that create unpredictable gameplay moments
    """

    @staticmethod
    def calculate_event_probability(game_state, event_type: str = None) -> Dict[str, int]:
        """
        Calculate probability of different event types occurring

        Returns:
            Dict mapping event_type to probability (0-100)
        """
        probabilities = {
            'encounter': 20,
            'initiated': 15,
            'opportunity': 10,
            'crisis': 5,
            'visitor': 8,
            'memory_trigger': 12
        }

        # Modifiers based on game state

        # High suspicion increases crisis events
        avg_suspicion = sum(char.player_suspicion for char in game_state.characters.values()) / len(game_state.characters)
        if avg_suspicion > 50:
            probabilities['crisis'] += 15
            probabilities['visitor'] += 10  # Confrontational visits

        # Strong rapport increases character-initiated events
        strong_rapport_count = sum(1 for char in game_state.characters.values() if char.rapport >= 10)
        probabilities['initiated'] += strong_rapport_count * 5

        # Alliances increase coordinated events
        from systems.social_dynamics import SocialDynamics
        alliances = SocialDynamics.check_alliances(game_state)
        if alliances:
            probabilities['crisis'] += len(alliances) * 10
            probabilities['visitor'] += len(alliances) * 8

        # Active PHS increases memory trigger events
        total_phs = sum(len(char.active_phs) for char in game_state.characters.values())
        probabilities['memory_trigger'] += total_phs * 3

        # Time since last event (encourage variety)
        if hasattr(game_state, 'last_event_time'):
            time_since = game_state.game_time.total_minutes - game_state.last_event_time
            if time_since > 120:  # 2+ hours
                for event_type in probabilities:
                    probabilities[event_type] = int(probabilities[event_type] * 1.5)

        # Normalize to 0-100
        for event_type in probabilities:
            probabilities[event_type] = min(100, probabilities[event_type])

        return probabilities

    @staticmethod
    def should_trigger_event(game_state) -> Tuple[bool, Optional[str]]:
        """
        Determine if an event should trigger

        Returns:
            (should_trigger, event_type)
        """
        probabilities = DynamicEventSystem.calculate_event_probability(game_state)

        # Overall chance any event triggers
        base_chance = 25  # 25% on each time advancement check

        # Roll for event
        if random.randint(0, 100) > base_chance:
            return False, None

        # Choose event type based on weighted probabilities
        event_types = list(probabilities.keys())
        weights = list(probabilities.values())

        chosen_type = random.choices(event_types, weights=weights, k=1)[0]

        return True, chosen_type

    @staticmethod
    def check_event_conditions(event: DynamicEvent, game_state) -> Tuple[bool, Optional[str]]:
        """
        Check if event's trigger conditions are met

        Returns:
            (can_trigger, failure_reason)
        """
        # Check cooldown
        if hasattr(game_state, 'event_history'):
            for past_event in game_state.event_history:
                if past_event['event_id'] == event.event_id:
                    time_since = game_state.game_time.total_minutes - past_event['triggered_at']
                    if time_since < event.cooldown_hours * 60:
                        return False, "On cooldown"

        # Check one-time
        if event.one_time and hasattr(game_state, 'completed_events'):
            if event.event_id in game_state.completed_events:
                return False, "Already completed"

        # Check rapport requirements
        for char_name, min_rap in event.min_rapport.items():
            char = game_state.characters.get(char_name)
            if not char or char.rapport < min_rap:
                return False, f"Insufficient rapport with {char_name}"

        for char_name, max_rap in event.max_rapport.items():
            char = game_state.characters.get(char_name)
            if not char or char.rapport > max_rap:
                return False, f"Too much rapport with {char_name}"

        # Check suspicion requirements
        for char_name, min_sus in event.min_suspicion.items():
            char = game_state.characters.get(char_name)
            if not char or char.player_suspicion < min_sus:
                return False, f"Insufficient suspicion from {char_name}"

        # Check emotional states
        for char_name, required_states in event.required_emotional_states.items():
            char = game_state.characters.get(char_name)
            if not char or char.emotional_state not in required_states:
                return False, f"{char_name} not in required emotional state"

        # Check location
        if event.required_location:
            if game_state.player.current_location != event.required_location:
                return False, "Wrong location"

        # Check time period
        if event.required_time_period:
            if game_state.game_time.period != event.required_time_period:
                return False, "Wrong time period"

        # Check alliance strength
        if event.alliance_strength_threshold:
            from systems.social_dynamics import SocialDynamics
            alliances = SocialDynamics.check_alliances(game_state)
            max_strength = max([a['alliance_strength'] for a in alliances], default=0)
            if max_strength < event.alliance_strength_threshold:
                return False, "No strong enough alliances"

        return True, None

    @staticmethod
    def get_available_events(game_state, event_type: str, event_library: Dict[str, DynamicEvent]) -> List[DynamicEvent]:
        """
        Get all events of a type that can currently trigger
        """
        available = []

        for event_id, event in event_library.items():
            if event.event_type != event_type:
                continue

            can_trigger, reason = DynamicEventSystem.check_event_conditions(event, game_state)
            if can_trigger:
                available.append(event)

        return available

    @staticmethod
    def select_event(available_events: List[DynamicEvent]) -> Optional[DynamicEvent]:
        """
        Select one event from available events based on weight
        """
        if not available_events:
            return None

        weights = [event.weight for event in available_events]
        return random.choices(available_events, weights=weights, k=1)[0]

    @staticmethod
    def trigger_event(game_state, event: DynamicEvent) -> Dict:
        """
        Trigger an event and return event data
        """
        # Record event in history
        if not hasattr(game_state, 'event_history'):
            game_state.event_history = []

        game_state.event_history.append({
            'event_id': event.event_id,
            'triggered_at': game_state.game_time.total_minutes,
            'timestamp': datetime.now().isoformat()
        })

        # Update last event time
        game_state.last_event_time = game_state.game_time.total_minutes

        # For opportunity windows, set expiration
        if event.window_expires_in:
            game_state.active_opportunity = {
                'event_id': event.event_id,
                'expires_at': game_state.game_time.total_minutes + event.window_expires_in
            }

        return {
            'success': True,
            'event': event.to_dict()
        }

    @staticmethod
    def respond_to_event(game_state, event_id: str, option_id: str,
                        event_library: Dict[str, DynamicEvent]) -> Dict:
        """
        Process player's response to an event

        Returns:
            Dict with outcome details
        """
        event = event_library.get(event_id)
        if not event:
            return {'success': False, 'error': 'Event not found'}

        # Find the chosen option
        option = None
        for opt in event.options:
            if opt.option_id == option_id:
                option = opt
                break

        if not option:
            return {'success': False, 'error': 'Invalid option'}

        # Check requirements
        if option.requires_rapport:
            if event.primary_character:
                char = game_state.characters.get(event.primary_character)
                if char and char.rapport < option.requires_rapport:
                    return {'success': False, 'error': f'Need {option.requires_rapport} rapport'}

        if option.requires_sp and game_state.player.suggestion_points < option.requires_sp:
            return {'success': False, 'error': f'Need {option.requires_sp} SP'}

        # Pay costs
        if option.sp_cost > 0:
            game_state.player.suggestion_points -= option.sp_cost

        if option.money_cost > 0:
            game_state.player.money -= option.money_cost

        # Apply effects
        messages = []

        # Rapport changes
        for char_name, change in option.rapport_changes.items():
            char = game_state.characters.get(char_name)
            if char:
                old_rapport = char.rapport
                if change > 0:
                    char.add_rapport(change)
                else:
                    char.reduce_rapport(abs(change))
                messages.append(f"Rapport with {char_name}: {old_rapport} → {char.rapport}")

        # Emotional state changes
        for char_name, new_state in option.emotional_state_changes.items():
            char = game_state.characters.get(char_name)
            if char:
                old_state = char.emotional_state
                char.set_emotional_state(new_state, f"Event: {event.title}")
                messages.append(f"{char_name} is now {new_state} (was {old_state})")

        # Suspicion changes
        for char_name, change in option.suspicion_changes.items():
            char = game_state.characters.get(char_name)
            if char:
                old_sus = char.player_suspicion
                char.player_suspicion = max(0, min(100, char.player_suspicion + change))
                if change != 0:
                    messages.append(f"{char_name}'s suspicion: {old_sus} → {char.player_suspicion}")

        # SP gain
        if option.sp_gain > 0:
            game_state.player.suggestion_points += option.sp_gain
            messages.append(f"Gained {option.sp_gain} SP")

        # Money gain
        if option.money_gain > 0:
            game_state.player.money += option.money_gain
            messages.append(f"Gained ${option.money_gain}")

        # Social effects (integrate with relationship web)
        if option.social_effect and option.observers:
            messages.append(f"📢 {option.social_effect}")

            # Observers notice
            from systems.social_dynamics import SocialDynamics
            for observer_name in option.observers:
                observer = game_state.characters.get(observer_name)
                if observer and event.primary_character:
                    primary = game_state.characters.get(event.primary_character)
                    if primary:
                        # They observe the interaction
                        from systems.relationship_web import RelationshipWeb
                        observation = RelationshipWeb.observe_character_changes(
                            observer, primary, 'behavior', 30
                        )
                        if observation:
                            msg = RelationshipWeb.format_observation_message(observation)
                            messages.append(msg)

        # Advance time
        if option.time_cost > 0:
            game_state.game_time.advance_minutes(option.time_cost)

        # Mark event as completed
        if event.one_time:
            if not hasattr(game_state, 'completed_events'):
                game_state.completed_events = set()
            game_state.completed_events.add(event_id)

        # Clear active opportunity if this was one
        if hasattr(game_state, 'active_opportunity'):
            if game_state.active_opportunity.get('event_id') == event_id:
                game_state.active_opportunity = None

        # Determine success (if option has success chance)
        success = True
        outcome_text = option.success_text

        if option.success_chance < 100:
            roll = random.randint(0, 100)
            success = roll <= option.success_chance
            outcome_text = option.success_text if success else option.failure_text

        return {
            'success': True,
            'outcome': outcome_text,
            'messages': messages,
            'option_success': success,
            'allows_phs': option.allows_phs,
            'phs_target': option.phs_target,
            'phs_success_bonus': option.phs_success_bonus if success else 0,
            'triggers_follow_up': option.triggers_follow_up_event if success else None
        }

    @staticmethod
    def check_opportunity_expiration(game_state) -> Optional[str]:
        """
        Check if an active opportunity has expired

        Returns:
            Message if opportunity expired, None otherwise
        """
        if not hasattr(game_state, 'active_opportunity') or not game_state.active_opportunity:
            return None

        opp = game_state.active_opportunity
        if game_state.game_time.total_minutes >= opp['expires_at']:
            event_id = opp['event_id']
            game_state.active_opportunity = None
            return f"⏰ Opportunity '{event_id}' has expired!"

        return None

    @staticmethod
    def format_event_notification(event: DynamicEvent) -> str:
        """Format event as notification message"""
        urgency_icons = {
            'low': '💬',
            'normal': '🎲',
            'high': '⚡',
            'critical': '🚨'
        }

        icon = urgency_icons.get(event.urgency_level, event.icon)

        message = f"{icon} **{event.title}**\n{event.description}"

        if event.window_expires_in:
            message += f"\n⏰ This opportunity expires in {event.window_expires_in} minutes!"

        if event.pressure:
            message += "\n⚠️ Quick decision required!"

        return message
