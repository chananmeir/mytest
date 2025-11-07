"""
Trigger Detection System for Post-Hypnotic Suggestions
Automatically detects when PHS triggers are activated and handles their execution
"""
import random
import re
from typing import List, Dict, Optional, Tuple
from models.character import Character, PostHypnoticSuggestion


class TriggerDetector:
    """Detects and processes PHS triggers"""

    # Pattern keywords to match in triggers
    TRIGGER_PATTERNS = {
        # Conversation-related triggers
        'praised': ['praised', 'complimented', 'admired', 'appreciated'],
        'criticized': ['criticized', 'blamed', 'criticized', 'judged'],
        'alone_with': ['alone with', 'just us', 'by ourselves'],
        'talking_to': ['talking to', 'speaking with', 'conversing with', 'chatting with'],
        'sees': ['sees me', 'looks at me', 'notices me'],

        # Activity-related triggers
        'dressing': ['getting dressed', 'changing clothes', 'putting on', 'choosing outfit'],
        'eating': ['eating', 'during meal', 'at dinner', 'at breakfast', 'at lunch'],
        'working': ['at work', 'working', 'in office'],
        'relaxing': ['relaxing', 'resting', 'unwinding'],
        'sleeping': ['going to bed', 'sleeping', 'bedtime'],

        # Time-related triggers
        'morning': ['morning', 'waking up', 'start of day'],
        'evening': ['evening', 'night', 'after dinner'],

        # Emotional state triggers
        'stressed': ['stressed', 'anxious', 'worried'],
        'happy': ['happy', 'pleased', 'content'],
        'tired': ['tired', 'exhausted', 'weary'],

        # Location triggers
        'home': ['at home', 'in house'],
        'kitchen': ['in kitchen', 'in the kitchen'],
        'bedroom': ['in bedroom', 'in their room'],
    }

    @staticmethod
    def check_conversation_triggers(
        character: Character,
        other_character_name: Optional[str],
        message_text: str,
        is_player: bool = False
    ) -> List[Tuple[PostHypnoticSuggestion, int]]:
        """
        Check if any PHS triggers are activated by a conversation

        Args:
            character: The character whose PHS to check
            other_character_name: Who they're talking to (None if player)
            message_text: The text of the conversation
            is_player: Whether talking to the player

        Returns:
            List of (PHS, activation_chance) tuples for triggered suggestions
        """
        triggered = []
        message_lower = message_text.lower()

        for phs in character.active_phs:
            trigger_lower = phs.trigger.lower()
            matched = False

            # Check for direct keyword matches
            if TriggerDetector._contains_pattern(trigger_lower, 'praised') and \
               TriggerDetector._is_praise(message_text):
                matched = True

            elif TriggerDetector._contains_pattern(trigger_lower, 'criticized') and \
                 TriggerDetector._is_criticism(message_text):
                matched = True

            elif TriggerDetector._contains_pattern(trigger_lower, 'alone_with'):
                # Alone with player or specific character
                if is_player or (other_character_name and other_character_name.lower() in trigger_lower):
                    matched = True

            elif TriggerDetector._contains_pattern(trigger_lower, 'talking_to'):
                # Check if trigger mentions the person they're talking to
                if other_character_name and other_character_name.lower() in trigger_lower:
                    matched = True
                elif is_player and ('you' in trigger_lower or 'player' in trigger_lower):
                    matched = True

            # Check for general conversation trigger
            elif 'when talked to' in trigger_lower or 'in conversation' in trigger_lower:
                matched = True

            if matched:
                activation_chance = phs.calculate_activation_chance()
                triggered.append((phs, activation_chance))

        return triggered

    @staticmethod
    def check_activity_triggers(
        character: Character,
        activity: str,
        location: Optional[str] = None
    ) -> List[Tuple[PostHypnoticSuggestion, int]]:
        """
        Check if any PHS triggers are activated by an activity

        Args:
            character: The character whose PHS to check
            activity: What activity they're doing
            location: Where they are (optional)

        Returns:
            List of (PHS, activation_chance) tuples for triggered suggestions
        """
        triggered = []
        activity_lower = activity.lower()

        for phs in character.active_phs:
            trigger_lower = phs.trigger.lower()
            matched = False

            # Check activity patterns
            for pattern_name in ['dressing', 'eating', 'working', 'relaxing', 'sleeping']:
                if TriggerDetector._contains_pattern(trigger_lower, pattern_name):
                    # Check if the activity matches this pattern
                    pattern_keywords = TriggerDetector.TRIGGER_PATTERNS[pattern_name]
                    if any(keyword in activity_lower for keyword in pattern_keywords):
                        matched = True
                        break

            # Check location if specified
            if location:
                location_lower = location.lower()
                if any(loc_word in trigger_lower for loc_word in ['kitchen', 'bedroom', 'home', 'office', 'living room']):
                    if location_lower in trigger_lower or any(keyword in location_lower for keyword in trigger_lower.split()):
                        matched = True

            # Check for generic activity trigger
            if 'when ' in trigger_lower:
                # Extract what comes after "when"
                when_part = trigger_lower.split('when ')[-1].strip()
                # Simple substring match
                if when_part in activity_lower or activity_lower in when_part:
                    matched = True

            if matched:
                activation_chance = phs.calculate_activation_chance()
                triggered.append((phs, activation_chance))

        return triggered

    @staticmethod
    def check_time_triggers(
        character: Character,
        time_period: str
    ) -> List[Tuple[PostHypnoticSuggestion, int]]:
        """
        Check if any PHS triggers are activated by time of day

        Args:
            character: The character whose PHS to check
            time_period: Time period (morning, afternoon, evening, night)

        Returns:
            List of (PHS, activation_chance) tuples for triggered suggestions
        """
        triggered = []
        period_lower = time_period.lower()

        for phs in character.active_phs:
            trigger_lower = phs.trigger.lower()

            if period_lower in trigger_lower or \
               TriggerDetector._contains_pattern(trigger_lower, period_lower):
                activation_chance = phs.calculate_activation_chance()
                triggered.append((phs, activation_chance))

        return triggered

    @staticmethod
    def check_emotional_triggers(
        character: Character,
        emotional_state: str
    ) -> List[Tuple[PostHypnoticSuggestion, int]]:
        """
        Check if any PHS triggers are activated by emotional state

        Args:
            character: The character whose PHS to check
            emotional_state: Their current emotional state

        Returns:
            List of (PHS, activation_chance) tuples for triggered suggestions
        """
        triggered = []
        state_lower = emotional_state.lower()

        for phs in character.active_phs:
            trigger_lower = phs.trigger.lower()

            # Check for emotional state keywords
            if state_lower in trigger_lower:
                activation_chance = phs.calculate_activation_chance()
                triggered.append((phs, activation_chance))

            # Check patterns
            for pattern_name in ['stressed', 'happy', 'tired']:
                if TriggerDetector._contains_pattern(trigger_lower, pattern_name):
                    pattern_keywords = TriggerDetector.TRIGGER_PATTERNS[pattern_name]
                    if any(keyword in state_lower for keyword in pattern_keywords):
                        activation_chance = phs.calculate_activation_chance()
                        triggered.append((phs, activation_chance))
                        break

        return triggered

    @staticmethod
    def attempt_activations(
        triggered: List[Tuple[PostHypnoticSuggestion, int]]
    ) -> List[Dict]:
        """
        Roll for activation of triggered suggestions

        Args:
            triggered: List of (PHS, activation_chance) tuples

        Returns:
            List of activation results with PHS details
        """
        activations = []

        for phs, activation_chance in triggered:
            # Roll for activation
            roll = random.randint(1, 100)

            if roll <= activation_chance:
                activations.append({
                    'target': phs.target_name,
                    'trigger': phs.trigger,
                    'response': phs.response,
                    'activation_chance': activation_chance,
                    'roll': roll,
                    'success': True
                })
            else:
                # Failed activation (for debugging/logging)
                activations.append({
                    'target': phs.target_name,
                    'trigger': phs.trigger,
                    'response': phs.response,
                    'activation_chance': activation_chance,
                    'roll': roll,
                    'success': False
                })

        return activations

    @staticmethod
    def _contains_pattern(trigger: str, pattern_name: str) -> bool:
        """Check if trigger contains any keywords from a pattern"""
        if pattern_name not in TriggerDetector.TRIGGER_PATTERNS:
            return False

        keywords = TriggerDetector.TRIGGER_PATTERNS[pattern_name]
        return any(keyword in trigger for keyword in keywords)

    @staticmethod
    def _is_praise(message: str) -> bool:
        """Detect if a message contains praise"""
        praise_words = [
            'good', 'great', 'excellent', 'wonderful', 'amazing', 'fantastic',
            'love', 'like', 'appreciate', 'admire', 'beautiful', 'smart',
            'talented', 'impressive', 'well done', 'nice', 'perfect', 'proud'
        ]
        message_lower = message.lower()
        return any(word in message_lower for word in praise_words)

    @staticmethod
    def _is_criticism(message: str) -> bool:
        """Detect if a message contains criticism"""
        criticism_words = [
            'wrong', 'bad', 'terrible', 'awful', 'disappointing', 'failure',
            'stupid', 'dumb', 'useless', 'waste', 'mistake', 'error',
            'shouldn\'t', 'can\'t believe', 'ridiculous', 'embarrassing'
        ]
        message_lower = message.lower()
        return any(word in message_lower for word in criticism_words)


def format_activation_message(activation: Dict) -> str:
    """
    Format an activation result into a displayable message

    Args:
        activation: Activation result dictionary

    Returns:
        Formatted message string
    """
    if activation['success']:
        return f"✨ {activation['target']} {activation['response']}"
    else:
        # Only show failed activations in debug mode
        return None
