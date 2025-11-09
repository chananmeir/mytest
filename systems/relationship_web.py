"""
Relationship Web System - Character-to-Character Dynamics
Makes the family truly interconnected and reactive
"""
from typing import Dict, List, Tuple, Optional
import random


class RelationshipWeb:
    """
    Manages character-to-character relationships and social dynamics.
    Characters notice changes in each other, gossip, protect loved ones, etc.
    """

    # Relationship categories (based on score 0-20)
    @staticmethod
    def get_relationship_type(score: int) -> str:
        """Get relationship type from score"""
        if score >= 15:
            return "very_close"  # Family bonds, best friends
        elif score >= 10:
            return "close"       # Good relationship
        elif score >= 5:
            return "neutral"     # Cordial
        else:
            return "distant"     # Strained or distant

    @staticmethod
    def get_protective_threshold(relationship_score: int) -> int:
        """
        How suspicious a character needs to be before someone protects them.
        Higher relationship = lower threshold (quicker to protect)
        """
        if relationship_score >= 15:
            return 20  # Very protective - acts at low suspicion
        elif relationship_score >= 10:
            return 40  # Moderately protective
        elif relationship_score >= 5:
            return 60  # Somewhat protective
        else:
            return 80  # Only protects if very obvious

    @staticmethod
    def calculate_observation_chance(observer, observed) -> int:
        """
        Chance that observer notices changes in observed character.
        Based on relationship strength and observer's personality.
        """
        base_chance = 30

        # Relationship modifier
        relationship_score = observer.relationships.get(observed.name, 5)
        if relationship_score >= 15:
            base_chance += 30  # Very attentive to close relationships
        elif relationship_score >= 10:
            base_chance += 15

        # Personality modifiers
        if "perceptive" in observer.personality.lower() or "observant" in observer.personality.lower():
            base_chance += 20

        if observer.name == "Dawn":  # Matriarch notices everything
            base_chance += 25
        elif observer.name == "Karen":  # Principal watches for rule-breaking
            base_chance += 20
        elif observer.name == "Melanie":  # Nurse notices health/behavior changes
            base_chance += 15

        # If observer is already suspicious of player, they watch more carefully
        if observer.player_suspicion > 30:
            base_chance += 20

        return min(95, base_chance)

    @staticmethod
    def observe_character_changes(observer, observed, change_type: str, change_magnitude: int) -> Optional[Dict]:
        """
        Check if observer notices a change in observed character.

        Args:
            observer: Character who might notice
            observed: Character who changed
            change_type: 'behavior', 'emotional_state', 'rapport_with_player', 'out_of_character'
            change_magnitude: How big the change (0-100)

        Returns:
            Dict with observation details if noticed, None otherwise
        """
        if observer.name == observed.name:
            return None  # Can't observe yourself

        # Calculate if they notice
        observation_chance = RelationshipWeb.calculate_observation_chance(observer, observed)

        # Bigger changes are easier to notice
        if change_magnitude > 50:
            observation_chance += 20
        elif change_magnitude > 30:
            observation_chance += 10

        if random.randint(0, 100) > observation_chance:
            return None  # Didn't notice

        # They noticed! Generate observation
        relationship_score = observer.relationships.get(observed.name, 5)
        relationship_type = RelationshipWeb.get_relationship_type(relationship_score)

        return {
            'observer': observer.name,
            'observed': observed.name,
            'change_type': change_type,
            'change_magnitude': change_magnitude,
            'relationship_type': relationship_type,
            'concern_level': RelationshipWeb._calculate_concern_level(
                observer, observed, change_type, change_magnitude, relationship_score
            ),
            'will_investigate': relationship_score >= 10 and change_magnitude > 40
        }

    @staticmethod
    def _calculate_concern_level(observer, observed, change_type: str,
                                 change_magnitude: int, relationship_score: int) -> str:
        """Calculate how concerned the observer is"""
        base_concern = change_magnitude

        # Close relationships increase concern
        if relationship_score >= 15:
            base_concern += 20
        elif relationship_score >= 10:
            base_concern += 10

        # Certain change types are more concerning
        if change_type == "out_of_character":
            base_concern += 25
        elif change_type == "behavior":
            base_concern += 15

        if base_concern >= 70:
            return "very_concerned"
        elif base_concern >= 50:
            return "concerned"
        elif base_concern >= 30:
            return "curious"
        else:
            return "noted"

    @staticmethod
    def generate_gossip(character1, character2, topic: str, game_state) -> Optional[Dict]:
        """
        Generate gossip between two characters about a topic.

        Args:
            character1: First character (initiator)
            character2: Second character (listener)
            topic: What they're gossiping about
            game_state: Current game state

        Returns:
            Dict with gossip details if it occurs
        """
        # Relationship check - do they gossip with each other?
        relationship_score = character1.relationships.get(character2.name, 5)

        # Close relationships gossip more
        gossip_chance = 30
        if relationship_score >= 15:
            gossip_chance = 70
        elif relationship_score >= 10:
            gossip_chance = 50

        # Some characters gossip more
        if character1.name in ["Dawn", "Karen", "Vanessa"]:  # Known gossipers
            gossip_chance += 20

        if random.randint(0, 100) > gossip_chance:
            return None  # No gossip this time

        # Gossip occurs!
        return {
            'gossiper': character1.name,
            'listener': character2.name,
            'topic': topic,
            'relationship_score': relationship_score,
            'credibility': RelationshipWeb._calculate_gossip_credibility(character1, character2)
        }

    @staticmethod
    def _calculate_gossip_credibility(gossiper, listener) -> int:
        """How much the listener believes the gossiper (0-100)"""
        relationship_score = listener.relationships.get(gossiper.name, 5)

        base_credibility = relationship_score * 5  # 0-100

        # Personality modifiers
        if "trusting" in listener.personality.lower():
            base_credibility += 20
        if "skeptical" in listener.personality.lower() or "dismissive" in listener.personality.lower():
            base_credibility -= 20

        # Known gossipers are less credible
        if gossiper.name in ["Vanessa"]:  # Status-conscious = exaggerates
            base_credibility -= 15

        # Dawn (matriarch) is highly credible
        if gossiper.name == "Dawn":
            base_credibility += 25

        return max(0, min(100, base_credibility))

    @staticmethod
    def spread_suspicion(source_character, target_character, suspicion_reason: str,
                        suspicion_amount: int) -> List[Dict]:
        """
        Source character tells target about suspicions regarding player.
        Suspicion spreads through the social network!

        Returns:
            List of effects from suspicion spreading
        """
        effects = []

        # Check if they would share this
        gossip = RelationshipWeb.generate_gossip(
            source_character, target_character,
            f"suspicious about player: {suspicion_reason}",
            None
        )

        if not gossip:
            return effects  # Didn't share suspicions

        # Suspicion spreads based on credibility
        credibility = gossip['credibility']
        transferred_suspicion = int(suspicion_amount * (credibility / 100))

        # Add suspicion to target
        old_suspicion = target_character.player_suspicion
        target_character.player_suspicion = min(100, target_character.player_suspicion + transferred_suspicion)

        effects.append({
            'type': 'suspicion_spread',
            'from': source_character.name,
            'to': target_character.name,
            'reason': suspicion_reason,
            'amount': transferred_suspicion,
            'credibility': credibility,
            'new_suspicion': target_character.player_suspicion
        })

        return effects

    @staticmethod
    def check_protective_response(protector, protected, threat_level: int) -> Optional[Dict]:
        """
        Check if protector takes action to defend protected character.

        Args:
            protector: Character who might protect
            protected: Character being threatened/manipulated
            threat_level: How serious the threat (0-100)

        Returns:
            Protection action details if they act
        """
        relationship_score = protector.relationships.get(protected.name, 5)
        threshold = RelationshipWeb.get_protective_threshold(relationship_score)

        if threat_level < threshold:
            return None  # Not threatened enough to act

        # They protect!
        protection_strength = relationship_score + (threat_level - threshold)

        action_type = "warning"
        if protection_strength >= 60:
            action_type = "confrontation"  # Directly confront player
        elif protection_strength >= 40:
            action_type = "intervention"   # Step in actively
        elif protection_strength >= 20:
            action_type = "warning"        # Warn player to back off

        return {
            'protector': protector.name,
            'protected': protected.name,
            'action_type': action_type,
            'protection_strength': protection_strength,
            'relationship_score': relationship_score,
            'threat_level': threat_level
        }

    @staticmethod
    def calculate_alliance_strength(char1, char2) -> int:
        """
        Calculate how likely two characters are to team up against player.
        Higher score = more likely to form alliance
        """
        # Mutual relationship strength
        score1 = char1.relationships.get(char2.name, 5)
        score2 = char2.relationships.get(char1.name, 5)
        base_strength = (score1 + score2) // 2

        # Similar suspicion levels increase alliance
        suspicion_diff = abs(char1.player_suspicion - char2.player_suspicion)
        if suspicion_diff < 10:
            base_strength += 20  # Similar suspicions unite

        # Both highly suspicious = strong alliance
        if char1.player_suspicion > 50 and char2.player_suspicion > 50:
            base_strength += 30

        return min(100, base_strength)

    @staticmethod
    def detect_coordinated_resistance(characters: List) -> List[Tuple[str, str, int]]:
        """
        Detect pairs of characters who might coordinate against player.

        Returns:
            List of (char1_name, char2_name, alliance_strength) tuples
        """
        alliances = []

        for i, char1 in enumerate(characters):
            for char2 in characters[i+1:]:
                strength = RelationshipWeb.calculate_alliance_strength(char1, char2)
                if strength >= 50:  # Strong enough to coordinate
                    alliances.append((char1.name, char2.name, strength))

        return sorted(alliances, key=lambda x: x[2], reverse=True)

    @staticmethod
    def generate_relationship_context_for_llm(character, game_state) -> str:
        """
        Generate context about character's relationships for LLM conversations.
        This makes NPCs aware of their social connections.
        """
        lines = []

        # Family relationships
        if character.relationships:
            close_ones = [name for name, score in character.relationships.items() if score >= 10]
            if close_ones:
                lines.append(f"You are close to: {', '.join(close_ones)}.")

        # Character suspicions (who they think is acting weird)
        if character.character_suspicions:
            suspicious_of = [name for name, sus in character.character_suspicions.items() if sus > 30]
            if suspicious_of:
                lines.append(f"You've noticed {', '.join(suspicious_of)} acting strangely lately.")

        # Player suspicion
        if character.player_suspicion > 50:
            lines.append(f"You're very suspicious that the player is manipulating people.")
        elif character.player_suspicion > 30:
            lines.append(f"Something feels off about the player's behavior.")

        return " ".join(lines)

    @staticmethod
    def format_observation_message(observation: Dict) -> str:
        """Format observation into readable message"""
        observer = observation['observer']
        observed = observation['observed']
        change_type = observation['change_type']
        concern = observation['concern_level']

        messages = {
            'behavior': {
                'noted': f"👀 {observer} notices {observed} is acting a bit different.",
                'curious': f"🤔 {observer} thinks {observed}'s behavior is unusual.",
                'concerned': f"😟 {observer} is concerned about {observed}'s strange behavior.",
                'very_concerned': f"⚠️ {observer} is very worried about {observed}!"
            },
            'emotional_state': {
                'noted': f"👀 {observer} notices {observed} seems different emotionally.",
                'curious': f"🤔 {observer} wonders why {observed}'s mood has changed.",
                'concerned': f"😟 {observer} is concerned about {observed}'s emotional state.",
                'very_concerned': f"⚠️ {observer} is very worried about {observed}'s emotions!"
            },
            'rapport_with_player': {
                'noted': f"👀 {observer} notices {observed} and the player are getting along.",
                'curious': f"🤔 {observer} is curious about {observed}'s closeness to the player.",
                'concerned': f"😟 {observer} thinks {observed} is too friendly with the player.",
                'very_concerned': f"⚠️ {observer} is alarmed by {observed}'s attachment to the player!"
            },
            'out_of_character': {
                'noted': f"👀 {observer} thinks that wasn't like {observed} at all.",
                'curious': f"🤔 {observer}: 'That's not like {observed}...'",
                'concerned': f"😟 {observer}: 'Something's wrong with {observed}.'",
                'very_concerned': f"⚠️ {observer}: '{observed} is NOT acting like themselves!'"
            }
        }

        return messages.get(change_type, {}).get(concern, f"{observer} noticed something about {observed}.")

    @staticmethod
    def format_gossip_message(gossip: Dict, effect: Optional[Dict] = None) -> str:
        """Format gossip event into readable message"""
        gossiper = gossip['gossiper']
        listener = gossip['listener']

        if effect and effect['type'] == 'suspicion_spread':
            return (f"💬 {gossiper} tells {listener} about their suspicions. "
                   f"{listener}'s suspicion increased by {effect['amount']}!")
        else:
            return f"💬 {gossiper} confides in {listener}..."

    @staticmethod
    def format_protection_message(protection: Dict) -> str:
        """Format protective action into readable message"""
        protector = protection['protector']
        protected = protection['protected']
        action = protection['action_type']

        messages = {
            'warning': f"⚠️ {protector} warns you: 'Leave {protected} alone.'",
            'intervention': f"🛡️ {protector} steps between you and {protected}!",
            'confrontation': f"🚨 {protector} confronts you: 'Stop manipulating {protected}!'"
        }

        return messages.get(action, f"{protector} defends {protected}")
