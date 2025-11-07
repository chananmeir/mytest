"""
LLM integration via OpenRouter for dynamic NPC conversations
"""
import requests
import json
from typing import Dict, List, Optional
from models.character import Character
from systems.memory import MemorySystem
import config


class LLMHandler:
    """Handles communication with OpenRouter API for NPC dialogue"""

    def __init__(self):
        self.api_url = config.OPENROUTER_API_URL
        self.memory_system = MemorySystem()

        if not config.DEFAULT_API_KEY:
            print("\n⚠️  WARNING: OPENROUTER_API_KEY not set!")
            print("Please create a .env file with your API key.")
            print("See .env.example for the format.\n")

    def _get_character_api_config(self, character: Character) -> tuple:
        """Get API key and model for a specific character"""
        api_key = config.CHARACTER_API_KEYS.get(character.name, config.DEFAULT_API_KEY)
        model = config.CHARACTER_MODELS.get(character.name, config.DEFAULT_MODEL)
        return api_key, model

    def _build_character_context(self, character: Character) -> str:
        """Build context string for the character"""
        context = f"""You are roleplaying as {character.name}, a {character.age}-year-old {character.occupation}.

PERSONALITY: {character.personality}

APPEARANCE: {character.clothing} - {character.clothing_meaning}

CURRENT EMOTIONAL STATE: {character.emotional_state}

RELATIONSHIP WITH PLAYER:
- The player is a 38-year-old family member who recently lost their job and is currently unemployed
- Your rapport with them: {character.rapport}/20 (higher = more trust and warmth)
- Your resistance to influence: {character.resistance}% (how skeptical/defensive you are)

IMPORTANT BEHAVIORAL NOTES:
- Respond naturally as this character would in a family gathering
- Your emotional state affects your tone and receptiveness
- If rapport is low, you may be dismissive or patronizing about their unemployment
- If rapport is high, you show more empathy and support
- React authentically to what the player says
- Don't break character or mention game mechanics
- Keep responses conversational and realistic (2-4 sentences typically)
"""

        # Add relevant memories
        relevant_memories = self.memory_system.retrieve_relevant_memories(
            character,
            count=config.MEMORY_RETRIEVAL_COUNT,
            min_importance=config.MEMORY_IMPORTANCE_THRESHOLD
        )

        if relevant_memories:
            context += "\n" + self.memory_system.format_memories_for_llm(relevant_memories) + "\n"

        # Add context about active PHS if any
        if character.active_phs:
            context += "\nSUBTLE BEHAVIORAL INFLUENCES (roleplay these naturally):\n"
            for phs in character.active_phs:
                context += f"- When {phs.trigger}, you {phs.response}\n"

        return context

    def _build_conversation_history(self, character: Character) -> List[Dict[str, str]]:
        """Build conversation history for context"""
        return character.conversation_history[-config.CONVERSATION_HISTORY_LENGTH:]  # Configurable message count

    def get_character_response(
        self,
        character: Character,
        player_message: str,
        scene_context: str = "",
        record_memory: bool = True
    ) -> Optional[str]:
        """Get a response from the character via LLM"""

        # Get character-specific API config
        api_key, model = self._get_character_api_config(character)

        if not api_key:
            return f"[{character.name} would respond, but API key is not configured]"

        # Build the system prompt with character context (includes memories)
        system_prompt = self._build_character_context(character)

        if scene_context:
            system_prompt += f"\n\nSCENE CONTEXT: {scene_context}"

        # Build messages array
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add conversation history
        for msg in self._build_conversation_history(character):
            messages.append(msg)

        # Add current player message
        messages.append({"role": "user", "content": player_message})

        # Prepare request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        if config.SITE_URL:
            headers["HTTP-Referer"] = config.SITE_URL

        if config.SITE_NAME:
            headers["X-Title"] = f"{config.SITE_NAME} - {character.name}"

        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.8,  # Add some personality variation
            "max_tokens": 300  # Keep responses concise
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

            assistant_message = result['choices'][0]['message']['content']

            # Store in conversation history
            character.conversation_history.append({"role": "user", "content": player_message})
            character.conversation_history.append({"role": "assistant", "content": assistant_message})

            # Record memory if enabled
            if record_memory:
                # Determine importance based on rapport and emotional state
                importance = 5  # Base importance
                if character.emotional_state in ['open', 'relaxed']:
                    importance += 1
                if character.rapport > 10:
                    importance += 1

                self.memory_system.record_conversation(
                    character,
                    speaker="You",
                    message=player_message,
                    importance=importance,
                    emotional_state=character.emotional_state
                )

            return assistant_message

        except requests.exceptions.Timeout:
            return f"[{character.name} seems distracted and doesn't respond immediately]"
        except requests.exceptions.RequestException as e:
            print(f"\n⚠️  API Error: {e}")
            return f"[{character.name} is momentarily lost in thought]"
        except (KeyError, json.JSONDecodeError) as e:
            print(f"\n⚠️  Response parsing error: {e}")
            return f"[{character.name} mumbles something unclear]"

    def get_group_response(
        self,
        characters: List[Character],
        player_message: str,
        scene_context: str = ""
    ) -> Dict[str, str]:
        """Get responses from multiple characters (they may not all respond)"""
        responses = {}

        for character in characters:
            # Not everyone responds to everything - simulate natural conversation flow
            # Higher rapport = more likely to engage
            import random

            engagement_chance = 50 + (character.rapport * 2)

            if random.randint(1, 100) <= engagement_chance:
                response = self.get_character_response(character, player_message, scene_context)
                if response:
                    responses[character.name] = response

        return responses

    def analyze_player_action(
        self,
        action: str,
        character: Character,
        context: str = ""
    ) -> Dict[str, any]:
        """Use LLM to analyze how a player action affects rapport/emotional state"""

        if not self.api_key:
            # Fallback to basic analysis
            return {
                'rapport_change': 0,
                'new_emotional_state': character.emotional_state,
                'reasoning': 'API not configured'
            }

        analysis_prompt = f"""Analyze this social interaction and its effect on the character.

CHARACTER: {character.name}
PERSONALITY: {character.personality}
CURRENT EMOTIONAL STATE: {character.emotional_state}
CURRENT RAPPORT: {character.rapport}/20

PLAYER ACTION: {action}

{context}

Respond with a JSON object:
{{
  "rapport_change": <number between -3 and +3>,
  "new_emotional_state": "<emotional state: neutral/relaxed/open/tense/defensive/hostile>",
  "reasoning": "<brief explanation>"
}}

Consider:
- Was the player empathetic or dismissive?
- Did they build trust or seem manipulative?
- How would this character authentically react?
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": analysis_prompt}],
            "temperature": 0.3,  # More consistent analysis
            "max_tokens": 200
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=20)
            response.raise_for_status()
            result = response.json()

            content = result['choices'][0]['message']['content']

            # Try to parse JSON from response
            # Sometimes LLMs wrap JSON in code blocks
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)

            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                return {
                    'rapport_change': 0,
                    'new_emotional_state': character.emotional_state,
                    'reasoning': 'Could not parse analysis'
                }

        except Exception as e:
            print(f"Analysis error: {e}")
            return {
                'rapport_change': 0,
                'new_emotional_state': character.emotional_state,
                'reasoning': 'Analysis failed'
            }
