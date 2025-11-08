"""
Suspicion System - Manages risk and consequences of hypnosis
"""

from typing import Dict, List, Tuple, Optional
from models.character import Character, PostHypnoticSuggestion


class SuspicionSystem:
    """Handles suspicion mechanics and out-of-character detection"""

    # Personality trait keywords for detection
    PERSONALITY_TRAITS = {
        'Ruth': {
            'core_traits': ['guilt-driven', 'loyal', 'tries to please everyone', 'people-pleaser'],
            'out_of_character': ['selfish', 'demanding', 'confrontational', 'aggressive', 'rude']
        },
        'Melanie': {
            'core_traits': ['proud', 'competent', 'dismissive', 'independent', 'in control'],
            'out_of_character': ['submissive', 'weak', 'needy', 'helpless', 'emotional', 'dependent']
        },
        'Tom': {
            'core_traits': ['conflict-avoidant', 'eager to please', 'insecure', 'passive', 'quiet'],
            'out_of_character': ['assertive', 'dominant', 'confident', 'confrontational', 'demanding']
        },
        'Dawn': {
            'core_traits': ['matriarch', 'values harmony', 'passive-aggressive', 'tradition', 'control'],
            'out_of_character': ['rebellious', 'chaotic', 'disrespectful', 'reckless']
        },
        'Vanessa': {
            'core_traits': ['status-conscious', 'competitive', 'success', 'image'],
            'out_of_character': ['humble', 'careless about appearance', 'failure', 'giving up']
        },
        'Derek': {
            'core_traits': ['ego-driven', 'physical confidence', 'body pride', 'showing off'],
            'out_of_character': ['insecure about body', 'hiding', 'timid', 'physically weak']
        },
        'Karen': {
            'core_traits': ['rigid', 'judgmental', 'needs control', 'rules', 'order'],
            'out_of_character': ['breaking rules', 'chaotic', 'permissive', 'carefree', 'messy']
        }
    }

    # Clothing changes that look suspicious
    SUSPICIOUS_CLOTHING_CHANGES = {
        'Ruth': ['revealing', 'sexy', 'inappropriate', 'bold'],
        'Melanie': ['submissive', 'overly feminine', 'impractical'],
        'Tom': ['flashy', 'attention-seeking', 'bold'],
        'Dawn': ['modern', 'trendy', 'youthful', 'revealing'],
        'Vanessa': ['cheap', 'casual', 'sloppy'],
        'Derek': ['covered up', 'baggy', 'hiding body'],
        'Karen': ['casual', 'messy', 'revealing', 'inappropriate']
    }

    @staticmethod
    def detect_out_of_character_behavior(character: Character, phs: PostHypnoticSuggestion) -> Tuple[bool, int]:
        """
        Detect if a PHS response is out of character

        Args:
            character: The character with active PHS
            phs: The post-hypnotic suggestion

        Returns:
            (is_suspicious, suspicion_increase_amount)
        """
        if character.name not in SuspicionSystem.PERSONALITY_TRAITS:
            return (False, 0)

        response_lower = phs.response.lower()
        trigger_lower = phs.trigger.lower()

        traits = SuspicionSystem.PERSONALITY_TRAITS[character.name]
        out_of_character_words = traits['out_of_character']

        # Check if response contains out-of-character keywords
        ooc_count = sum(1 for word in out_of_character_words if word in response_lower)

        if ooc_count > 0:
            # Severity based on how many OOC traits are violated
            base_suspicion = 10
            severity_multiplier = min(ooc_count, 3)  # Cap at 3x
            suspicion_increase = base_suspicion * severity_multiplier

            # Reduce suspicion if character has high rapport (they trust the player)
            rapport_reduction = character.rapport * 2  # Up to -40 at max rapport
            final_suspicion = max(5, suspicion_increase - rapport_reduction)

            return (True, final_suspicion)

        # Check for suspicious clothing changes
        if 'wear' in response_lower or 'dress' in response_lower or 'clothing' in response_lower:
            suspicious_words = SuspicionSystem.SUSPICIOUS_CLOTHING_CHANGES.get(character.name, [])
            clothing_ooc_count = sum(1 for word in suspicious_words if word in response_lower)

            if clothing_ooc_count > 0:
                suspicion = 15 - (character.rapport * 2)
                return (True, max(5, suspicion))

        return (False, 0)

    @staticmethod
    def increase_character_suspicion(
        observer: Character,
        target_character_name: str,
        suspicion_amount: int
    ) -> str:
        """
        Increase an observer's suspicion about another character acting weird

        Args:
            observer: Character who notices the weird behavior
            target_character_name: Who is acting weird
            suspicion_amount: How much to increase

        Returns:
            Message describing the suspicion change
        """
        if target_character_name not in observer.character_suspicions:
            observer.character_suspicions[target_character_name] = 0

        old_suspicion = observer.character_suspicions[target_character_name]
        observer.character_suspicions[target_character_name] = min(100, old_suspicion + suspicion_amount)
        new_suspicion = observer.character_suspicions[target_character_name]

        # Generate message based on suspicion level
        if new_suspicion >= 80:
            return f"{observer.name} is very concerned about {target_character_name}'s strange behavior..."
        elif new_suspicion >= 50:
            return f"{observer.name} has noticed {target_character_name} acting differently lately."
        elif new_suspicion >= 25:
            return f"{observer.name} seems curious about changes in {target_character_name}."
        else:
            return f"{observer.name} raises an eyebrow at {target_character_name}'s behavior."

    @staticmethod
    def increase_player_suspicion(
        character: Character,
        suspicion_amount: int,
        reason: str = ""
    ) -> Tuple[str, bool]:
        """
        Increase a character's suspicion that the PLAYER is manipulating people

        Args:
            character: Character becoming suspicious of player
            suspicion_amount: How much to increase
            reason: Why suspicion increased

        Returns:
            (message, is_confrontation_triggered)
        """
        old_suspicion = character.player_suspicion
        character.player_suspicion = min(100, old_suspicion + suspicion_amount)
        new_suspicion = character.player_suspicion

        # Check for confrontation threshold
        confrontation = False
        if new_suspicion >= 90:
            confrontation = True

        # Generate message
        if new_suspicion >= 90:
            message = f"⚠️ {character.name} is convinced you're manipulating the family! {reason}"
        elif new_suspicion >= 70:
            message = f"⚠️ {character.name} strongly suspects you're behind the strange behavior. {reason}"
        elif new_suspicion >= 50:
            message = f"⚠️ {character.name} is starting to suspect you might be involved. {reason}"
        elif new_suspicion >= 25:
            message = f"{character.name} finds it odd that you're around when people act strange. {reason}"
        else:
            message = f"{character.name} notices something unusual. {reason}"

        return (message, confrontation)

    @staticmethod
    def apply_defensive_phs(
        defender: Character,
        target_character: Character,
        reduction_amount: int
    ) -> str:
        """
        Apply a defensive PHS that lowers suspicion

        Args:
            defender: Character defending the player
            target_character: Character whose suspicion is being lowered
            reduction_amount: How much to reduce suspicion

        Returns:
            Message describing the defense
        """
        old_suspicion = target_character.player_suspicion
        target_character.player_suspicion = max(0, old_suspicion - reduction_amount)
        new_suspicion = target_character.player_suspicion

        # Also reduce character_suspicions if they exist
        if defender.name in target_character.character_suspicions:
            target_character.character_suspicions[defender.name] = max(
                0,
                target_character.character_suspicions[defender.name] - (reduction_amount // 2)
            )

        reduction = old_suspicion - new_suspicion
        if reduction > 0:
            return f"✅ {defender.name} defended you to {target_character.name}, reducing their suspicion by {reduction}!"
        else:
            return f"{defender.name} tried to defend you, but {target_character.name} wasn't suspicious."

    @staticmethod
    def decay_suspicion_over_time(character: Character, time_passed_hours: int = 1) -> List[str]:
        """
        Gradually decay suspicion as time passes

        Args:
            character: Character whose suspicion decays
            time_passed_hours: How many hours have passed

        Returns:
            List of messages about suspicion decay
        """
        messages = []

        # Player suspicion decay (slower)
        if character.player_suspicion > 0:
            decay_amount = max(1, time_passed_hours // 4)  # 1 point per 4 hours
            old_suspicion = character.player_suspicion
            character.player_suspicion = max(0, character.player_suspicion - decay_amount)

            if old_suspicion >= 50 and character.player_suspicion < 50:
                messages.append(f"{character.name} is becoming less suspicious of you.")

        # Character suspicion decay (faster - people forget about others' behavior)
        for target_name in list(character.character_suspicions.keys()):
            if character.character_suspicions[target_name] > 0:
                decay_amount = max(2, time_passed_hours // 2)  # 2 points per 2 hours
                old_value = character.character_suspicions[target_name]
                character.character_suspicions[target_name] = max(0, old_value - decay_amount)

                # Remove from dict if it reaches 0
                if character.character_suspicions[target_name] == 0:
                    del character.character_suspicions[target_name]

        return messages

    @staticmethod
    def calculate_evidence_against_player(
        game_state,
        character: Character
    ) -> int:
        """
        Calculate how much evidence points to the player being responsible

        Factors:
        - Multiple people acting strange (player is common factor)
        - High rapport with affected people (means alone time)
        - Failed PHS attempts (they "snapped out of it")

        Returns:
            Suspicion amount to add
        """
        evidence = 0

        # Count how many other characters are acting out of character
        strange_behavior_count = 0
        for other_char in game_state.characters.values():
            if other_char.name != character.name:
                # Check if they have active PHS
                if len(other_char.active_phs) > 0:
                    strange_behavior_count += 1

        # If multiple people are affected, player is common factor
        if strange_behavior_count >= 3:
            evidence += 20
        elif strange_behavior_count >= 2:
            evidence += 10

        return evidence

    @staticmethod
    def get_suspicion_status(character: Character) -> Dict:
        """
        Get formatted suspicion status for UI display

        Returns:
            Dict with suspicion level, color, icon, and warning
        """
        suspicion = character.player_suspicion

        if suspicion >= 90:
            return {
                'level': suspicion,
                'status': 'CRITICAL',
                'color': 'var(--danger-color)',
                'icon': '🚨',
                'warning': 'Confrontation imminent!',
                'bar_color': '#ff0000'
            }
        elif suspicion >= 70:
            return {
                'level': suspicion,
                'status': 'VERY HIGH',
                'color': 'var(--danger-color)',
                'icon': '⚠️',
                'warning': 'Strongly suspects you',
                'bar_color': '#ff4444'
            }
        elif suspicion >= 50:
            return {
                'level': suspicion,
                'status': 'HIGH',
                'color': 'var(--warning-color)',
                'icon': '⚠️',
                'warning': 'Getting suspicious',
                'bar_color': '#ffaa00'
            }
        elif suspicion >= 25:
            return {
                'level': suspicion,
                'status': 'MODERATE',
                'color': 'var(--warning-color)',
                'icon': '👁️',
                'warning': 'Watching you',
                'bar_color': '#ffdd00'
            }
        elif suspicion > 0:
            return {
                'level': suspicion,
                'status': 'LOW',
                'color': 'var(--text-secondary)',
                'icon': '👀',
                'warning': 'Slightly suspicious',
                'bar_color': '#888888'
            }
        else:
            return {
                'level': 0,
                'status': 'NONE',
                'color': 'var(--success-color)',
                'icon': '✓',
                'warning': 'Trusting',
                'bar_color': '#00ff00'
            }
