"""
Game Master / Narrator System for Family Dynamics RPG

The GM oversees game logic, detects PHS triggers, suggests consequences,
and maintains narrative coherence.
"""
import requests
import json
from typing import Dict, List, Optional, Tuple
import config
from models.character import Character, PostHypnoticSuggestion


class GameMaster:
    """
    The GM/Narrator system that oversees the game.
    Uses LLM to make intelligent decisions about game state and consequences.
    """

    def __init__(self):
        self.api_key = config.GM_API_KEY
        self.model = config.GM_MODEL
        self.api_url = config.OPENROUTER_API_URL

        if not self.api_key:
            print("\n⚠️  WARNING: GM_API_KEY not set! GM features will be limited.")

    def _make_llm_call(self, prompt: str, temperature: float = 0.5) -> Optional[str]:
        """Make an LLM API call"""
        if not self.api_key:
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        if config.SITE_URL:
            headers["HTTP-Referer"] = config.SITE_URL

        if config.SITE_NAME:
            headers["X-Title"] = f"{config.SITE_NAME} - GM"

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 500
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']

        except Exception as e:
            print(f"\n⚠️  GM API Error: {e}")
            return None

    def check_phs_triggers(
        self,
        character: Character,
        current_context: str,
        recent_events: List[str]
    ) -> List[Tuple[PostHypnoticSuggestion, bool]]:
        """
        Check if any PHS should trigger based on current context

        Returns:
            List of (PHS, should_trigger) tuples
        """
        if not character.active_phs:
            return []

        results = []

        for phs in character.active_phs:
            # Build prompt for GM to evaluate
            prompt = f"""You are the Game Master for a psychological RPG.

CHARACTER: {character.name}
EMOTIONAL STATE: {character.emotional_state}

POST-HYPNOTIC SUGGESTION:
Trigger: "{phs.trigger}"
Response: "{phs.response}"
Activation Chance: {phs.calculate_activation_chance()}%

CURRENT CONTEXT:
{current_context}

RECENT EVENTS:
{chr(10).join(f"- {event}" for event in recent_events[-5:])}

QUESTION: Should this post-hypnotic suggestion trigger now?

Consider:
1. Does the current context match the trigger condition?
2. Is the character in an appropriate emotional state?
3. Would triggering feel natural and not forced?
4. Is this a good narrative moment?

Respond with ONLY: YES or NO"""

            response = self._make_llm_call(prompt, temperature=0.3)

            if response and "YES" in response.upper():
                results.append((phs, True))
            else:
                results.append((phs, False))

        return results

    def analyze_conversation_impact(
        self,
        character: Character,
        player_message: str,
        character_response: str,
        scene_context: str
    ) -> Dict[str, any]:
        """
        Analyze how a conversation impacts the character
        Returns rapport change, emotional state change, and memory importance
        """
        prompt = f"""You are the Game Master analyzing a social interaction in a psychological RPG.

CHARACTER: {character.name}
PERSONALITY: {character.personality}
CURRENT EMOTIONAL STATE: {character.emotional_state}
CURRENT RAPPORT WITH PLAYER: {character.rapport}/20

SCENE CONTEXT: {scene_context}

PLAYER SAID: "{player_message}"
CHARACTER RESPONDED: "{character_response}"

Analyze this interaction and respond with JSON:
{{
  "rapport_change": <-3 to +3, how much rapport changed>,
  "new_emotional_state": "<neutral/relaxed/open/tense/defensive/hostile>",
  "memory_importance": <1-10, how memorable is this moment>,
  "reasoning": "<brief explanation>",
  "manipulation_detected": <true/false, did player seem manipulative>
}}

Consider:
- Authenticity vs manipulation
- Emotional resonance
- Character's personality and resistance
- Trust building or breaking"""

        response = self._make_llm_call(prompt, temperature=0.4)

        if not response:
            # Fallback
            return {
                'rapport_change': 0,
                'new_emotional_state': character.emotional_state,
                'memory_importance': 5,
                'reasoning': 'GM unavailable',
                'manipulation_detected': False
            }

        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)

            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {
            'rapport_change': 0,
            'new_emotional_state': character.emotional_state,
            'memory_importance': 5,
            'reasoning': 'Could not parse GM analysis',
            'manipulation_detected': False
        }

    def suggest_consequences(
        self,
        game_state,
        action_description: str,
        affected_characters: List[str]
    ) -> Dict[str, str]:
        """
        Suggest narrative consequences of player actions

        Returns:
            Dict mapping consequence types to descriptions
        """
        character_states = "\n".join([
            f"- {name}: Rapport {char.rapport}, State: {char.emotional_state}"
            for name, char in game_state.characters.items()
            if name in affected_characters
        ])

        prompt = f"""You are the Game Master for a psychological RPG about family dynamics.

PLAYER ACTION: {action_description}

AFFECTED CHARACTERS:
{character_states}

PLAYER SP: {game_state.player.suggestion_points}

Suggest consequences of this action. Respond with JSON:
{{
  "immediate": "<immediate narrative consequence>",
  "relationship": "<how relationships might shift>",
  "long_term": "<potential long-term effects>",
  "risk_level": "<low/medium/high - risk of being seen as manipulative>"
}}

Keep consequences subtle and realistic. This is about slow influence, not magic."""

        response = self._make_llm_call(prompt, temperature=0.6)

        if not response:
            return {
                'immediate': 'The family continues their conversations.',
                'relationship': 'Relationships remain stable.',
                'long_term': 'The effects will become clear over time.',
                'risk_level': 'medium'
            }

        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)

            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {
            'immediate': 'The moment passes.',
            'relationship': 'Subtle shifts occur.',
            'long_term': 'Time will tell.',
            'risk_level': 'medium'
        }

    def generate_scene_summary(
        self,
        scene_name: str,
        key_events: List[str],
        character_changes: Dict[str, Dict]
    ) -> str:
        """Generate a narrative summary of a scene"""
        changes_text = "\n".join([
            f"- {name}: Rapport {changes['rapport_old']}→{changes['rapport_new']}, "
            f"State: {changes['state_old']}→{changes['state_new']}"
            for name, changes in character_changes.items()
        ])

        prompt = f"""You are the Narrator for a psychological RPG about family dynamics.

SCENE: {scene_name}

KEY EVENTS:
{chr(10).join(f"- {event}" for event in key_events)}

CHARACTER CHANGES:
{changes_text}

Write a brief, evocative narrative summary (3-5 sentences) of what happened in this scene.
Focus on:
- The subtle shifts in power dynamics
- The player's growing influence (or lack thereof)
- The emotional undercurrents
- What seeds were planted for future scenes

Write in second person ("You..."). Keep tone slightly noir/psychological."""

        response = self._make_llm_call(prompt, temperature=0.7)

        if not response:
            return f"The scene at {scene_name} concludes. Your influence grows, slowly and surely."

        return response

    def evaluate_phs_quality(
        self,
        character: Character,
        trigger: str,
        response: str
    ) -> Dict[str, any]:
        """
        Evaluate the quality and appropriateness of a proposed PHS

        Returns:
            Dict with success_modifier, warnings, and suggestions
        """
        prompt = f"""You are the Game Master evaluating a post-hypnotic suggestion.

CHARACTER: {character.name}
PERSONALITY: {character.personality}
RESISTANCE: {character.resistance}%
CURRENT RAPPORT: {character.rapport}/20
EMOTIONAL STATE: {character.emotional_state}

PROPOSED PHS:
Trigger: "{trigger}"
Response: "{response}"

Evaluate this PHS and respond with JSON:
{{
  "quality_score": <1-10, how well-crafted is this suggestion>,
  "success_modifier": <-20 to +20, adjustment to base success rate>,
  "warnings": ["<any warnings about this approach>"],
  "suggestions": ["<how to improve this suggestion>"],
  "reasoning": "<brief explanation>"
}}

Consider:
- Is the trigger natural and likely to occur?
- Is the response subtle enough to feel like their own thought?
- Does it fit the character's personality?
- Is it ethically within game boundaries (no harm)?"""

        response = self._make_llm_call(prompt, temperature=0.4)

        if not response:
            return {
                'quality_score': 5,
                'success_modifier': 0,
                'warnings': [],
                'suggestions': [],
                'reasoning': 'GM unavailable'
            }

        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)

            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {
            'quality_score': 5,
            'success_modifier': 0,
            'warnings': [],
            'suggestions': [],
            'reasoning': 'Could not parse evaluation'
        }

    def detect_family_dynamics_shift(
        self,
        game_state
    ) -> Optional[str]:
        """
        Detect if overall family dynamics have significantly shifted
        Returns a narrative description if shift detected
        """
        rapport_summary = "\n".join([
            f"- {name}: Rapport {char.rapport}/20, State: {char.emotional_state}, PHS: {len(char.active_phs)}"
            for name, char in game_state.characters.items()
        ])

        prompt = f"""You are the Game Master for a psychological RPG about family dynamics.

PLAYER STATUS:
- SP: {game_state.player.suggestion_points}
- Total SP Earned: {game_state.player.total_sp_earned}

FAMILY MEMBER STATES:
{rapport_summary}

QUESTION: Has the player's status in the family significantly shifted?
Consider:
- How many people have high rapport (>10)?
- How many people have active PHS?
- Total influence accumulated
- Whether the player is still "lowest status"

If YES, a major shift has occurred, respond with a 2-3 sentence narrative description of the change.
If NO, significant shift yet, respond with: NONE

Be generous - this is about recognizing player progress."""

        response = self._make_llm_call(prompt, temperature=0.6)

        if not response or "NONE" in response.upper():
            return None

        return response
