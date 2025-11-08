"""
Social Dynamics Integration
Automatically tracks character changes and triggers social responses
"""
from typing import List, Dict, Optional
import random
from systems.relationship_web import RelationshipWeb


class SocialDynamics:
    """
    Integrates relationship web into gameplay.
    Automatically triggers observations, gossip, and protective behaviors.
    """

    @staticmethod
    def on_phs_activation(game_state, character_with_phs, phs) -> List[str]:
        """
        Called when a PHS activates. Check if other characters notice.

        Returns:
            List of message strings describing social reactions
        """
        messages = []

        # Determine how out-of-character this behavior is
        ooc_magnitude = SocialDynamics._calculate_ooc_magnitude(character_with_phs, phs)

        # Check each other character for observations
        for char_name, char in game_state.characters.items():
            if char.name == character_with_phs.name:
                continue

            # Check if they observe this
            observation = RelationshipWeb.observe_character_changes(
                observer=char,
                observed=character_with_phs,
                change_type='out_of_character',
                change_magnitude=ooc_magnitude
            )

            if observation:
                # They noticed!
                msg = RelationshipWeb.format_observation_message(observation)
                messages.append(msg)

                # Increase observer's suspicion of the observed character
                if char.name not in char.character_suspicions:
                    char.character_suspicions[char.name] = 0

                suspicion_increase = ooc_magnitude // 5
                char.character_suspicions[character_with_phs.name] = min(
                    100,
                    char.character_suspicions.get(character_with_phs.name, 0) + suspicion_increase
                )

                # If very concerned, might gossip immediately
                if observation['concern_level'] in ['concerned', 'very_concerned']:
                    gossip_msgs = SocialDynamics._trigger_immediate_gossip(
                        game_state, char, character_with_phs, f"acting strange"
                    )
                    messages.extend(gossip_msgs)

                # Check for protective response
                protection_msgs = SocialDynamics._check_protection(
                    game_state, observation, ooc_magnitude
                )
                messages.extend(protection_msgs)

        return messages

    @staticmethod
    def on_rapport_increase(game_state, character, old_rapport, new_rapport) -> List[str]:
        """
        Called when player's rapport with a character increases significantly.
        Others might notice and get jealous/suspicious.
        """
        messages = []

        # Only trigger if significant change
        rapport_change = new_rapport - old_rapport
        if rapport_change < 3:
            return messages

        # Check for observations
        for char_name, char in game_state.characters.items():
            if char.name == character.name:
                continue

            observation = RelationshipWeb.observe_character_changes(
                observer=char,
                observed=character,
                change_type='rapport_with_player',
                change_magnitude=rapport_change * 10  # Scale to 0-100
            )

            if observation:
                msg = RelationshipWeb.format_observation_message(observation)
                messages.append(msg)

                # Jealousy/suspicion based on their relationship
                relationship_score = char.relationships.get(character.name, 5)

                # Close relationships might get protective
                if relationship_score >= 10:
                    char.player_suspicion = min(100, char.player_suspicion + rapport_change * 2)
                    if char.player_suspicion > 40:
                        messages.append(
                            f"⚠️ {char.name} is watching your relationship with {character.name} closely."
                        )

        return messages

    @staticmethod
    def on_emotional_state_change(game_state, character, old_state, new_state) -> List[str]:
        """
        Called when character's emotional state changes.
        Close relationships notice emotional shifts.
        """
        messages = []

        # Calculate magnitude based on state change severity
        severity_map = {
            'defensive': 80,
            'hostile': 90,
            'open': 60,
            'vulnerable': 70,
            'relaxed': 40,
            'neutral': 20,
            'tense': 50
        }

        old_severity = severity_map.get(old_state, 30)
        new_severity = severity_map.get(new_state, 30)
        magnitude = abs(new_severity - old_severity)

        # Only significant changes get noticed
        if magnitude < 20:
            return messages

        for char_name, char in game_state.characters.items():
            if char.name == character.name:
                continue

            observation = RelationshipWeb.observe_character_changes(
                observer=char,
                observed=character,
                change_type='emotional_state',
                change_magnitude=magnitude
            )

            if observation:
                msg = RelationshipWeb.format_observation_message(observation)
                messages.append(msg)

        return messages

    @staticmethod
    def trigger_gossip_session(game_state) -> List[str]:
        """
        Randomly trigger gossip between characters.
        Called periodically (e.g., when player advances time).

        Returns:
            List of gossip messages
        """
        messages = []

        # Get all characters
        characters = list(game_state.characters.values())

        # Try 2-3 gossip attempts
        num_attempts = random.randint(2, 3)

        for _ in range(num_attempts):
            if len(characters) < 2:
                break

            # Pick two random characters
            char1, char2 = random.sample(characters, 2)

            # What are they gossiping about?
            topic = SocialDynamics._choose_gossip_topic(game_state, char1)

            if not topic:
                continue

            gossip = RelationshipWeb.generate_gossip(char1, char2, topic, game_state)

            if gossip:
                # Gossip occurred - apply effects
                if 'player' in topic.lower() and char1.player_suspicion > 20:
                    # Spreading suspicion about player
                    effects = RelationshipWeb.spread_suspicion(
                        char1, char2,
                        topic,
                        char1.player_suspicion // 2
                    )

                    for effect in effects:
                        msg = RelationshipWeb.format_gossip_message(gossip, effect)
                        messages.append(msg)

                elif 'strange' in topic.lower():
                    # Gossiping about another character
                    msg = RelationshipWeb.format_gossip_message(gossip)
                    messages.append(msg)

        return messages

    @staticmethod
    def check_alliances(game_state) -> List[Dict]:
        """
        Check for character alliances forming against player.

        Returns:
            List of alliance dictionaries
        """
        characters = [char for char in game_state.characters.values()
                     if char.player_suspicion > 30]

        if len(characters) < 2:
            return []

        alliances = RelationshipWeb.detect_coordinated_resistance(characters)

        # Format as dicts
        result = []
        for char1_name, char2_name, strength in alliances:
            result.append({
                'character1': char1_name,
                'character2': char2_name,
                'alliance_strength': strength,
                'threat_level': 'high' if strength > 70 else 'medium'
            })

        return result

    @staticmethod
    def get_relationship_context_for_conversation(character, game_state) -> str:
        """
        Get relationship context to include in LLM prompts.
        Makes NPCs aware of their social connections.
        """
        return RelationshipWeb.generate_relationship_context_for_llm(character, game_state)

    # --- Helper Methods ---

    @staticmethod
    def _calculate_ooc_magnitude(character, phs) -> int:
        """
        Calculate how out-of-character a PHS-triggered behavior is.
        Higher resistance = more obvious when they act against it.
        """
        base_magnitude = character.resistance

        # Stronger PHS types are more obvious
        phs_type_magnitude = {
            'compliance_trigger': 80,  # Very obvious
            'behavioral_prompt': 60,   # Noticeable
            'emotional_nudge': 30,     # Subtle
            'defensive': 20            # Hard to notice
        }

        type_modifier = phs_type_magnitude.get(phs.phs_type, 50)

        # Average the two
        magnitude = (base_magnitude + type_modifier) // 2

        return min(100, magnitude)

    @staticmethod
    def _trigger_immediate_gossip(game_state, concerned_character,
                                   strange_character, reason) -> List[str]:
        """
        When someone is very concerned, they immediately tell someone close.
        """
        messages = []

        # Find their closest relationship
        if not concerned_character.relationships:
            return messages

        closest = max(concerned_character.relationships.items(), key=lambda x: x[1])
        closest_name, closest_score = closest

        if closest_score < 8:  # Not close enough to confide in
            return messages

        closest_char = game_state.characters.get(closest_name)
        if not closest_char:
            return messages

        # Generate gossip
        gossip = {
            'gossiper': concerned_character.name,
            'listener': closest_char.name,
            'topic': f"{strange_character.name} {reason}",
            'relationship_score': closest_score,
            'credibility': 70
        }

        # Spread suspicion
        if concerned_character.player_suspicion > 20:
            effects = RelationshipWeb.spread_suspicion(
                concerned_character,
                closest_char,
                f"{strange_character.name} is acting strange",
                concerned_character.player_suspicion // 3
            )

            for effect in effects:
                msg = RelationshipWeb.format_gossip_message(gossip, effect)
                messages.append(msg)

        return messages

    @staticmethod
    def _check_protection(game_state, observation, threat_level) -> List[str]:
        """
        Check if observer takes protective action.
        """
        messages = []

        observer = game_state.characters.get(observation['observer'])
        observed = game_state.characters.get(observation['observed'])

        if not observer or not observed:
            return messages

        # Check for protective response
        protection = RelationshipWeb.check_protective_response(
            observer, observed, threat_level
        )

        if protection:
            msg = RelationshipWeb.format_protection_message(protection)
            messages.append(msg)

            # Protective actions increase player suspicion
            if protection['action_type'] == 'warning':
                observer.player_suspicion = min(100, observer.player_suspicion + 10)
            elif protection['action_type'] == 'intervention':
                observer.player_suspicion = min(100, observer.player_suspicion + 20)
            elif protection['action_type'] == 'confrontation':
                observer.player_suspicion = min(100, observer.player_suspicion + 30)

        return messages

    @staticmethod
    def _choose_gossip_topic(game_state, character) -> Optional[str]:
        """
        Choose what a character might gossip about.
        """
        topics = []

        # Suspicious about player?
        if character.player_suspicion > 30:
            topics.append(f"the player's strange behavior")

        # Suspicious about other characters?
        if character.character_suspicions:
            for char_name, suspicion in character.character_suspicions.items():
                if suspicion > 30:
                    topics.append(f"{char_name} acting strange")

        # General topics (fallback)
        topics.extend([
            "family dynamics",
            "recent events",
            "concerns about the family"
        ])

        return random.choice(topics) if topics else None

    @staticmethod
    def format_alliance_warning(alliance: Dict) -> str:
        """Format alliance formation into warning message"""
        char1 = alliance['character1']
        char2 = alliance['character2']
        strength = alliance['alliance_strength']
        threat = alliance['threat_level']

        if threat == 'high':
            return f"🚨 WARNING: {char1} and {char2} are working together against you! (Alliance: {strength}%)"
        else:
            return f"⚠️ {char1} and {char2} seem to be talking about you... (Alliance: {strength}%)"
