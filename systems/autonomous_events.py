"""
Autonomous Events System - Characters act independently based on PHS

This system allows characters to perform actions autonomously when the player
is not directly interacting with them, making PHS feel more alive and impactful.

Key Features:
- Characters trigger their active PHS based on context
- Actions are performed autonomously (clothing changes, mood shifts, etc.)
- Events are recorded and shown to player
- Creates emergent gameplay from planted suggestions
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import random
from datetime import datetime


@dataclass
class AutonomousEvent:
    """Represents an autonomous action taken by a character"""
    character_name: str
    event_type: str  # 'phs_activation', 'mood_change', 'clothing_change', 'action'
    description: str
    timestamp: str
    trigger: str  # What caused this
    is_phs_related: bool = False
    phs_id: Optional[int] = None  # Index of PHS that triggered this
    visibility: str = 'public'  # 'public', 'private', 'subtle'
    icon: str = "🔔"


class AutonomousEventsSystem:
    """Manages autonomous character behaviors and PHS activations"""

    @staticmethod
    def check_autonomous_triggers(game_state, minutes_passed: int) -> List[AutonomousEvent]:
        """
        Check if any characters should perform autonomous actions

        Called when time passes without player interaction.
        Returns list of events that occurred.
        """
        events = []

        for character in game_state.characters.values():
            # Check for PHS-based autonomous actions
            phs_events = AutonomousEventsSystem._check_phs_autonomous_triggers(
                game_state, character, minutes_passed
            )
            events.extend(phs_events)

            # Check for natural behavior changes
            natural_events = AutonomousEventsSystem._check_natural_behaviors(
                game_state, character, minutes_passed
            )
            events.extend(natural_events)

        return events

    @staticmethod
    def _check_phs_autonomous_triggers(game_state, character, minutes_passed: int) -> List[AutonomousEvent]:
        """Check if character's active PHS should trigger autonomously"""
        events = []

        if not hasattr(character, 'active_phs') or not character.active_phs:
            return events

        # Get character's current context
        current_location = game_state.current_location
        current_time = game_state.time_system.current_time
        hour = current_time.hour

        for phs_index, phs in enumerate(character.active_phs):
            # Determine if this PHS should trigger autonomously
            should_trigger = AutonomousEventsSystem._should_phs_trigger_autonomously(
                phs, character, current_location, hour, minutes_passed
            )

            if should_trigger:
                event = AutonomousEventsSystem._execute_autonomous_phs(
                    game_state, character, phs, phs_index
                )
                if event:
                    events.append(event)

        return events

    @staticmethod
    def _should_phs_trigger_autonomously(phs, character, location: str, hour: int, minutes_passed: int) -> bool:
        """Determine if a PHS should trigger based on context"""

        # Base chance increases with activation chance
        base_chance = phs.activation_chance / 100.0

        # Higher chance if more time passed
        time_multiplier = min(minutes_passed / 60.0, 3.0)  # Cap at 3x

        # Check if trigger matches current situation
        trigger_lower = phs.trigger.lower()
        response_lower = phs.response.lower()

        # Context-based triggering
        context_match = False

        # Clothing-related PHS
        if any(keyword in trigger_lower or keyword in response_lower
               for keyword in ['dress', 'wear', 'clothing', 'outfit', 'clothes']):
            # Trigger when getting dressed (morning/evening)
            if hour in [7, 8, 9, 18, 19, 20, 21]:
                context_match = True

        # Location-based PHS
        if 'bedroom' in trigger_lower and 'your_room' in location:
            context_match = True
        if 'kitchen' in trigger_lower and 'kitchen' in location:
            context_match = True
        if 'home' in trigger_lower and location.startswith('home_'):
            context_match = True

        # Time-based PHS
        if 'morning' in trigger_lower and 6 <= hour <= 11:
            context_match = True
        if 'evening' in trigger_lower and 17 <= hour <= 22:
            context_match = True
        if 'night' in trigger_lower and (hour >= 22 or hour <= 5):
            context_match = True

        # Emotional/thinking triggers happen randomly
        if any(keyword in trigger_lower for keyword in ['thinking', 'feel', 'remember', 'alone']):
            context_match = random.random() < 0.3  # 30% chance per check

        # Final probability
        trigger_chance = base_chance * time_multiplier
        if context_match:
            trigger_chance *= 2.0  # Double chance if context matches

        return random.random() < trigger_chance

    @staticmethod
    def _execute_autonomous_phs(game_state, character, phs, phs_index: int) -> Optional[AutonomousEvent]:
        """Execute a PHS autonomously and create event"""

        # Determine what action to take based on PHS response
        response = phs.response.lower()

        event_type = 'phs_activation'
        description = ""
        visibility = 'subtle'
        icon = "✨"

        # Clothing changes
        if any(keyword in response for keyword in ['wear', 'dress', 'put on', 'change into']):
            event_type = 'clothing_change'
            description = f"{character.name} {phs.response}"
            visibility = 'public'  # Visible change
            icon = "👗"

            # Actually change the character's outfit if possible
            AutonomousEventsSystem._apply_clothing_change(character, phs)

        # Emotional changes
        elif any(keyword in response for keyword in ['feel', 'attracted', 'love', 'trust', 'comfortable']):
            event_type = 'mood_change'
            description = f"{character.name} {phs.response}"
            visibility = 'subtle'
            icon = "💭"

            # Adjust character's emotional state
            AutonomousEventsSystem._apply_emotional_change(character, phs)

        # Behavioral actions
        elif any(keyword in response for keyword in ['call', 'visit', 'go to', 'come to', 'message']):
            event_type = 'action'
            description = f"{character.name} {phs.response}"
            visibility = 'public'
            icon = "🚶"

        # Compliance/obedience (internal, not visible)
        elif any(keyword in response for keyword in ['obey', 'listen', 'agree', 'do what']):
            event_type = 'mood_change'
            description = f"{character.name} feels compelled to {phs.response}"
            visibility = 'private'  # Player won't know unless they check
            icon = "🎯"

        # Generic PHS activation
        else:
            description = f"{character.name} {phs.response}"
            visibility = 'subtle'
            icon = "✨"

        # Create the event
        event = AutonomousEvent(
            character_name=character.name,
            event_type=event_type,
            description=description,
            timestamp=game_state.time_system.get_formatted_time(),
            trigger=phs.trigger,
            is_phs_related=True,
            phs_id=phs_index,
            visibility=visibility,
            icon=icon
        )

        # Record in character's memory
        if hasattr(character, 'memories'):
            character.memories.append({
                'type': 'phs_triggered',
                'content': f"Autonomously acted on suggestion: {phs.response}",
                'timestamp': event.timestamp,
                'importance': 6,
                'emotional_context': character.emotional_state
            })

        # Increment reinforcement (gets stronger each time it triggers)
        phs.reinforcements += 1
        if phs.activation_chance < 95:
            phs.activation_chance = min(95, phs.activation_chance + 2)  # +2% each time

        return event

    @staticmethod
    def _apply_clothing_change(character, phs):
        """Apply autonomous clothing change based on PHS"""
        response = phs.response.lower()

        # Extract what they're wearing from the response
        # Examples: "wear something more revealing", "put on the dress", "dress more casually"

        if 'revealing' in response or 'sexy' in response or 'tight' in response:
            # Change to more revealing outfit
            if hasattr(character, 'outfit'):
                from systems.clothing_system import ClothingSystem

                # Find revealing clothing in their wardrobe
                revealing_options = [
                    outfit for outfit in ClothingSystem.get_character_wardrobe(character)
                    if outfit.get('modifier', 0) < -5  # Negative modifier = more suggestible
                ]

                if revealing_options:
                    new_outfit = random.choice(revealing_options)
                    character.outfit = new_outfit
                    character.clothing = new_outfit.get('description', 'Revealing clothing')
                    character.clothing_modifier = new_outfit.get('modifier', -10)

        elif 'casual' in response or 'comfortable' in response:
            # Change to casual outfit
            if hasattr(character, 'outfit'):
                character.clothing = "Casual, comfortable clothes"
                character.clothing_modifier = 0

        elif 'professional' in response or 'formal' in response:
            if hasattr(character, 'outfit'):
                character.clothing = "Professional attire"
                character.clothing_modifier = 5

    @staticmethod
    def _apply_emotional_change(character, phs):
        """Apply autonomous emotional change based on PHS"""
        response = phs.response.lower()

        # Adjust character state based on emotional PHS
        if 'attracted' in response or 'love' in response:
            # Increase rapport slightly
            if hasattr(character, 'rapport'):
                character.rapport = min(20, character.rapport + 1)

            # Adjust emotional state
            if hasattr(character, 'emotional_state'):
                character.emotional_state = 'affectionate'

        elif 'trust' in response or 'comfortable' in response:
            # Reduce resistance slightly
            if hasattr(character, 'resistance'):
                character.resistance = max(0, character.resistance - 2)

            if hasattr(character, 'emotional_state'):
                character.emotional_state = 'relaxed'

        elif 'nervous' in response or 'anxious' in response:
            if hasattr(character, 'emotional_state'):
                character.emotional_state = 'nervous'

    @staticmethod
    def _check_natural_behaviors(game_state, character, minutes_passed: int) -> List[AutonomousEvent]:
        """Check for natural autonomous behaviors (not PHS-related)"""
        events = []

        # Small chance of spontaneous actions
        if random.random() < 0.1:  # 10% chance
            # Character does something based on their personality
            event = AutonomousEventsSystem._generate_natural_behavior(
                game_state, character
            )
            if event:
                events.append(event)

        return events

    @staticmethod
    def _generate_natural_behavior(game_state, character) -> Optional[AutonomousEvent]:
        """Generate a natural (non-PHS) autonomous behavior"""

        current_location = game_state.current_location
        hour = game_state.time_system.current_time.hour

        # Location-based natural behaviors
        natural_actions = []

        if 'kitchen' in current_location:
            natural_actions.extend([
                f"{character.name} is cooking something in the kitchen",
                f"{character.name} is making tea",
                f"{character.name} is cleaning up the kitchen"
            ])

        elif 'living_room' in current_location:
            natural_actions.extend([
                f"{character.name} is watching TV",
                f"{character.name} is reading a book on the couch",
                f"{character.name} is relaxing in the living room"
            ])

        elif 'your_room' in current_location:
            natural_actions.extend([
                f"{character.name} is in their bedroom",
                f"{character.name} is listening to music in their room"
            ])

        # Time-based behaviors
        if 7 <= hour <= 9:
            natural_actions.append(f"{character.name} is having breakfast")
        elif 12 <= hour <= 14:
            natural_actions.append(f"{character.name} is having lunch")
        elif 18 <= hour <= 20:
            natural_actions.append(f"{character.name} is having dinner")

        if not natural_actions:
            return None

        description = random.choice(natural_actions)

        return AutonomousEvent(
            character_name=character.name,
            event_type='action',
            description=description,
            timestamp=game_state.time_system.get_formatted_time(),
            trigger='natural_behavior',
            is_phs_related=False,
            visibility='public',
            icon="👀"
        )

    @staticmethod
    def get_recent_events(game_state, limit: int = 5) -> List[Dict]:
        """Get recent autonomous events for display"""

        # Check if we have stored events
        if not hasattr(game_state, 'autonomous_events'):
            game_state.autonomous_events = []

        # Return most recent events
        return [
            {
                'character': event.character_name,
                'description': event.description,
                'timestamp': event.timestamp,
                'type': event.event_type,
                'icon': event.icon,
                'visibility': event.visibility,
                'is_phs': event.is_phs_related
            }
            for event in sorted(
                game_state.autonomous_events[-limit:],
                key=lambda e: e.timestamp,
                reverse=True
            )
        ]

    @staticmethod
    def add_event_to_log(game_state, event: AutonomousEvent):
        """Add an autonomous event to the game state log"""
        if not hasattr(game_state, 'autonomous_events'):
            game_state.autonomous_events = []

        game_state.autonomous_events.append(event)

        # Keep only last 50 events
        if len(game_state.autonomous_events) > 50:
            game_state.autonomous_events = game_state.autonomous_events[-50:]


# ==================== SPECIFIC PHS TRIGGER SCENARIOS ====================

class PHSScenarios:
    """Pre-defined scenarios for common PHS triggers"""

    @staticmethod
    def create_clothing_scenario(character_name: str, clothing_type: str):
        """Create an event where character changes clothes due to PHS"""
        descriptions = {
            'revealing': f"{character_name} is wearing something more revealing than usual",
            'casual': f"{character_name} changed into casual clothes",
            'sexy': f"{character_name} is dressed in alluring clothing",
            'comfortable': f"{character_name} changed into comfortable loungewear"
        }

        return descriptions.get(clothing_type, f"{character_name} changed their outfit")

    @staticmethod
    def create_mood_scenario(character_name: str, mood: str):
        """Create an event where character's mood changes due to PHS"""
        descriptions = {
            'attracted': f"{character_name} seems more affectionate than usual",
            'nervous': f"{character_name} appears anxious about something",
            'happy': f"{character_name} is in an unusually good mood",
            'compliant': f"{character_name} seems eager to please"
        }

        return descriptions.get(mood, f"{character_name}'s mood has shifted")

    @staticmethod
    def create_action_scenario(character_name: str, action: str):
        """Create an event where character performs an action due to PHS"""
        return f"{character_name} {action}"
