"""
Dialogue System - Contextual dialogue choices with consequences
"""

from typing import Dict, List, Optional, Tuple
from models.character import Character
import random


class DialogueChoice:
    """Represents a single dialogue choice with its consequences"""

    def __init__(
        self,
        choice_id: str,
        text: str,
        choice_type: str,
        rapport_change: int = 0,
        resistance_change: int = 0,
        emotional_state: Optional[str] = None,
        suspicion_change: int = 0,
        triggers_phs_attempt: bool = False,
        phs_difficulty_modifier: int = 0,
        requires_rapport: int = 0,
        sp_cost: int = 0,
        description: str = ""
    ):
        self.choice_id = choice_id
        self.text = text
        self.choice_type = choice_type  # encourage, push, neutral, empathize, challenge, flirt, deflect
        self.rapport_change = rapport_change
        self.resistance_change = resistance_change
        self.emotional_state = emotional_state
        self.suspicion_change = suspicion_change
        self.triggers_phs_attempt = triggers_phs_attempt
        self.phs_difficulty_modifier = phs_difficulty_modifier
        self.requires_rapport = requires_rapport
        self.sp_cost = sp_cost
        self.description = description

    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        return {
            'choice_id': self.choice_id,
            'text': self.text,
            'choice_type': self.choice_type,
            'description': self.description,
            'requires_rapport': self.requires_rapport,
            'sp_cost': self.sp_cost,
            'consequences': {
                'rapport': self.rapport_change,
                'resistance': self.resistance_change,
                'emotional_state': self.emotional_state,
                'suspicion': self.suspicion_change,
                'triggers_phs': self.triggers_phs_attempt
            }
        }


class DialogueSystem:
    """Manages contextual dialogue choices and consequences"""

    # Context-based choice templates
    CONTEXT_CHOICES = {
        'insecurity': [
            DialogueChoice(
                choice_id='encourage',
                text='You look amazing!',
                choice_type='encourage',
                rapport_change=2,
                emotional_state='pleased',
                description='Genuine encouragement (+Rapport, improves mood)'
            ),
            DialogueChoice(
                choice_id='push',
                text='You SHOULD wear it.',
                choice_type='push',
                triggers_phs_attempt=True,
                phs_difficulty_modifier=10,
                suspicion_change=5,
                description='Assertive push (PHS attempt, risky if fails)'
            ),
            DialogueChoice(
                choice_id='neutral',
                text="It's up to you.",
                choice_type='neutral',
                description='Safe, no change'
            )
        ],
        'conflict': [
            DialogueChoice(
                choice_id='empathize',
                text="I understand how you feel.",
                choice_type='empathize',
                rapport_change=2,
                emotional_state='relaxed',
                description='Empathetic response (+Rapport, calms them)'
            ),
            DialogueChoice(
                choice_id='challenge',
                text="Maybe you're overreacting?",
                choice_type='challenge',
                rapport_change=-1,
                emotional_state='defensive',
                suspicion_change=3,
                description='Challenge them (-Rapport, may make defensive)'
            ),
            DialogueChoice(
                choice_id='deflect',
                text="Let's talk about something else.",
                choice_type='deflect',
                description='Avoid the topic (safe)'
            )
        ],
        'vulnerability': [
            DialogueChoice(
                choice_id='support',
                text="I'm here for you.",
                choice_type='empathize',
                rapport_change=3,
                resistance_change=-5,
                emotional_state='open',
                description='Deep support (+3 Rapport, -Resistance, opens them up)'
            ),
            DialogueChoice(
                choice_id='exploit',
                text="You can trust me with anything...",
                choice_type='push',
                resistance_change=-10,
                triggers_phs_attempt=True,
                phs_difficulty_modifier=15,
                suspicion_change=8,
                requires_rapport=10,
                sp_cost=1,
                description='Exploit vulnerability (High reward, high risk, requires 10+ rapport)'
            ),
            DialogueChoice(
                choice_id='lighten',
                text="Hey, it'll be okay!",
                choice_type='neutral',
                rapport_change=1,
                description='Lighten the mood (+1 Rapport)'
            )
        ],
        'attraction': [
            DialogueChoice(
                choice_id='flirt',
                text="You look really good today.",
                choice_type='flirt',
                rapport_change=2,
                resistance_change=-3,
                emotional_state='playful',
                requires_rapport=8,
                description='Subtle flirtation (+Rapport, -Resistance, requires 8+ rapport)'
            ),
            DialogueChoice(
                choice_id='bold_flirt',
                text="I've been thinking about you...",
                choice_type='flirt',
                rapport_change=4,
                resistance_change=-8,
                emotional_state='open',
                suspicion_change=5,
                requires_rapport=15,
                sp_cost=1,
                description='Bold advance (+4 Rapport, -8 Resistance, risky, requires 15+ rapport)'
            ),
            DialogueChoice(
                choice_id='friendly',
                text="It's nice spending time with you.",
                choice_type='neutral',
                rapport_change=1,
                description='Keep it friendly (+1 Rapport)'
            )
        ],
        'request': [
            DialogueChoice(
                choice_id='agree',
                text="Of course, I'll help!",
                choice_type='encourage',
                rapport_change=2,
                description='Agree to help (+2 Rapport)'
            ),
            DialogueChoice(
                choice_id='condition',
                text="I'll help if you do something for me...",
                choice_type='push',
                rapport_change=1,
                triggers_phs_attempt=True,
                phs_difficulty_modifier=5,
                suspicion_change=3,
                requires_rapport=8,
                description='Conditional help (PHS attempt, requires 8+ rapport)'
            ),
            DialogueChoice(
                choice_id='decline',
                text="Sorry, I can't right now.",
                choice_type='neutral',
                rapport_change=-1,
                description='Politely decline (-1 Rapport)'
            )
        ],
        'gossip': [
            DialogueChoice(
                choice_id='join',
                text="Oh really? Tell me more!",
                choice_type='encourage',
                rapport_change=1,
                description='Join the gossip (+1 Rapport)'
            ),
            DialogueChoice(
                choice_id='defend',
                text="Maybe we shouldn't talk about them.",
                choice_type='challenge',
                rapport_change=-1,
                emotional_state='neutral',
                description='Defend the target (-1 Rapport with gossiper)'
            ),
            DialogueChoice(
                choice_id='redirect',
                text="Have you talked to them about it?",
                choice_type='neutral',
                rapport_change=1,
                description='Redirect constructively (+1 Rapport)'
            )
        ],
        'suspicious': [
            DialogueChoice(
                choice_id='deflect_charm',
                text="You're reading too much into it!",
                choice_type='deflect',
                suspicion_change=-5,
                requires_rapport=10,
                description='Deflect with charm (-5 Suspicion, requires 10+ rapport)'
            ),
            DialogueChoice(
                choice_id='gaslight',
                text="That's not what happened at all...",
                choice_type='push',
                suspicion_change=-10,
                triggers_phs_attempt=True,
                phs_difficulty_modifier=20,
                requires_rapport=15,
                sp_cost=2,
                description='Attempt to gaslight (High risk/reward, requires 15+ rapport, 2 SP)'
            ),
            DialogueChoice(
                choice_id='honest',
                text="You're right to be concerned.",
                choice_type='neutral',
                suspicion_change=5,
                rapport_change=2,
                description='Be honest (+2 Rapport, +5 Suspicion)'
            )
        ],
        'praise': [
            DialogueChoice(
                choice_id='accept',
                text="Thank you, that means a lot.",
                choice_type='neutral',
                rapport_change=1,
                description='Accept gracefully (+1 Rapport)'
            ),
            DialogueChoice(
                choice_id='reciprocate',
                text="You're amazing too!",
                choice_type='encourage',
                rapport_change=2,
                resistance_change=-3,
                description='Reciprocate warmly (+2 Rapport, -3 Resistance)'
            ),
            DialogueChoice(
                choice_id='redirect',
                text="I learned from watching you.",
                choice_type='encourage',
                rapport_change=3,
                resistance_change=-5,
                emotional_state='pleased',
                description='Flattering redirection (+3 Rapport, -5 Resistance, pleases them)'
            )
        ]
    }

    # Character personality modifiers affect which choices appear
    CHARACTER_CONTEXT_PREFERENCES = {
        'Ruth': ['insecurity', 'vulnerability', 'request', 'praise'],
        'Melanie': ['conflict', 'challenge', 'praise'],
        'Tom': ['insecurity', 'request', 'praise', 'vulnerability'],
        'Dawn': ['conflict', 'gossip', 'request'],
        'Vanessa': ['attraction', 'praise', 'gossip'],
        'Derek': ['challenge', 'attraction', 'praise'],
        'Karen': ['conflict', 'suspicious', 'request']
    }

    @staticmethod
    def detect_context(
        character: Character,
        player_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[str]:
        """
        Detect the context of the conversation to provide relevant choices

        Args:
            character: The character being talked to
            player_message: What the player just said
            conversation_history: Recent conversation history

        Returns:
            Context type or None
        """
        player_lower = player_message.lower()

        # Check recent character messages for context clues
        recent_character_messages = []
        for msg in conversation_history[-3:]:
            if msg.get('role') == 'assistant':
                recent_character_messages.append(msg.get('content', '').lower())

        combined_context = ' '.join(recent_character_messages)

        # Suspicion detection (high priority)
        if character.player_suspicion > 40:
            suspicious_words = ['strange', 'weird', 'odd', 'suspicious', 'acting different', 'changed']
            if any(word in combined_context for word in suspicious_words):
                return 'suspicious'

        # Vulnerability detection
        vulnerability_words = ['scared', 'worried', 'don\'t know', 'insecure', 'afraid', 'confused', 'lost']
        if any(word in combined_context for word in vulnerability_words):
            return 'vulnerability'

        # Insecurity detection
        insecurity_words = ['should i', 'do i look', 'am i', 'what if', 'i\'m not sure']
        if any(phrase in combined_context for phrase in insecurity_words):
            return 'insecurity'

        # Conflict detection
        conflict_words = ['angry', 'upset', 'mad', 'frustrated', 'annoyed', 'bothering']
        if any(word in combined_context for word in conflict_words):
            return 'conflict'

        # Request detection
        request_words = ['can you', 'would you', 'will you', 'could you', 'help me', 'need']
        if any(phrase in combined_context for phrase in request_words):
            return 'request'

        # Gossip detection
        gossip_words = ['did you hear', 'have you noticed', 'she/he', 'they\'ve been']
        if any(phrase in combined_context for phrase in gossip_words):
            return 'gossip'

        # Praise detection
        praise_words = ['thank you', 'you\'re great', 'appreciate', 'you\'ve been', 'you\'re amazing']
        if any(phrase in combined_context for phrase in praise_words):
            return 'praise'

        # Attraction context (only if high rapport)
        if character.rapport >= 10:
            attraction_words = ['like you', 'enjoy', 'fun', 'spending time']
            if any(phrase in combined_context for phrase in attraction_words):
                return 'attraction'

        return None

    @staticmethod
    def get_contextual_choices(
        character: Character,
        context: str,
        current_rapport: int
    ) -> List[DialogueChoice]:
        """
        Get dialogue choices for the detected context

        Args:
            character: The character
            context: Detected context type
            current_rapport: Current rapport level

        Returns:
            List of available dialogue choices
        """
        if context not in DialogueSystem.CONTEXT_CHOICES:
            return []

        all_choices = DialogueSystem.CONTEXT_CHOICES[context]

        # Filter choices based on rapport requirements
        available_choices = []
        for choice in all_choices:
            if choice.requires_rapport <= current_rapport:
                available_choices.append(choice)

        return available_choices

    @staticmethod
    def should_offer_choices(
        character: Character,
        conversation_history: List[Dict[str, str]]
    ) -> bool:
        """
        Determine if dialogue choices should be offered

        Choices appear:
        - Every 3-5 messages
        - When specific contexts are detected
        - When character emotional state is optimal
        """
        # Don't offer choices too frequently
        history_length = len(conversation_history)
        if history_length < 2:
            return False

        # Offer choices more frequently with higher rapport
        frequency = max(3, 7 - (character.rapport // 5))

        # Random chance based on frequency
        should_offer = (history_length % frequency) == 0

        # Always offer during key emotional states
        key_states = ['open', 'relaxed', 'vulnerable', 'playful', 'suspicious']
        if character.emotional_state in key_states:
            should_offer = True

        return should_offer

    @staticmethod
    def apply_choice_consequences(
        choice: DialogueChoice,
        character: Character,
        game_state
    ) -> Dict[str, any]:
        """
        Apply the consequences of a dialogue choice

        Args:
            choice: The selected dialogue choice
            character: The character
            game_state: Game state for broader effects

        Returns:
            Dict with results of applying consequences
        """
        results = {
            'rapport_changed': False,
            'resistance_changed': False,
            'emotional_state_changed': False,
            'suspicion_changed': False,
            'phs_triggered': False,
            'messages': []
        }

        # Apply rapport change
        if choice.rapport_change != 0:
            old_rapport = character.rapport
            if choice.rapport_change > 0:
                character.add_rapport(choice.rapport_change)
            else:
                character.reduce_rapport(abs(choice.rapport_change))

            new_rapport = character.rapport
            if old_rapport != new_rapport:
                results['rapport_changed'] = True
                results['old_rapport'] = old_rapport
                results['new_rapport'] = new_rapport

                change_text = f"+{choice.rapport_change}" if choice.rapport_change > 0 else str(choice.rapport_change)
                results['messages'].append(f"Rapport with {character.name}: {change_text} ({new_rapport}/20)")

        # Apply resistance change
        if choice.resistance_change != 0:
            old_resistance = character.resistance
            character.resistance = max(0, min(100, character.resistance + choice.resistance_change))
            new_resistance = character.resistance

            if old_resistance != new_resistance:
                results['resistance_changed'] = True
                results['old_resistance'] = old_resistance
                results['new_resistance'] = new_resistance

                change_text = f"{choice.resistance_change:+d}"
                results['messages'].append(f"{character.name}'s resistance: {change_text}% ({new_resistance}%)")

        # Apply emotional state change
        if choice.emotional_state:
            old_state = character.emotional_state
            character.set_emotional_state(
                choice.emotional_state,
                reason=f"Your words made them feel {choice.emotional_state}"
            )

            if old_state != choice.emotional_state:
                results['emotional_state_changed'] = True
                results['old_emotional_state'] = old_state
                results['new_emotional_state'] = choice.emotional_state
                results['messages'].append(f"{character.name} is now {choice.emotional_state}")

        # Apply suspicion change
        if choice.suspicion_change != 0:
            old_suspicion = character.player_suspicion
            character.player_suspicion = max(0, min(100, character.player_suspicion + choice.suspicion_change))
            new_suspicion = character.player_suspicion

            if old_suspicion != new_suspicion:
                results['suspicion_changed'] = True
                results['old_suspicion'] = old_suspicion
                results['new_suspicion'] = new_suspicion

                if choice.suspicion_change > 0:
                    results['messages'].append(f"⚠️ {character.name}'s suspicion increased by {choice.suspicion_change}")
                else:
                    results['messages'].append(f"✓ {character.name}'s suspicion decreased by {abs(choice.suspicion_change)}")

        # Track if PHS attempt should be triggered
        if choice.triggers_phs_attempt:
            results['phs_triggered'] = True
            results['phs_difficulty_modifier'] = choice.phs_difficulty_modifier

        return results

    @staticmethod
    def generate_choice_prompt(
        choice: DialogueChoice,
        character_name: str
    ) -> str:
        """
        Generate the actual dialogue text that the player says when choosing this option

        This is used to feed into the LLM for the character's response
        """
        return f"{choice.text}"

    @staticmethod
    def get_character_response_context(
        choice: DialogueChoice,
        character: Character
    ) -> str:
        """
        Generate additional context for LLM based on the dialogue choice

        This helps the LLM understand the intent behind the choice
        """
        context_hints = {
            'encourage': f"The player is being encouraging and supportive. Respond warmly.",
            'push': f"The player is being assertive and directive. This might feel slightly pushy.",
            'neutral': f"The player is being neutral and safe. Respond naturally.",
            'empathize': f"The player is showing empathy and understanding. Respond with appreciation.",
            'challenge': f"The player is challenging your perspective. You might feel defensive.",
            'flirt': f"The player is being flirtatious. Respond based on your rapport ({character.rapport}/20) and emotional state.",
            'deflect': f"The player is deflecting or changing the subject. Respond accordingly."
        }

        return context_hints.get(choice.choice_type, "")
