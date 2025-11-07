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

    def _build_character_context(self, character: Character, location_context: str = "") -> str:
        """Build context string for the character"""

        # Character-specific behavioral guidelines
        personality_guides = {
            'Ruth': """
SPEAKING STYLE:
- Apologetic and accommodating
- Uses phrases like "I'm so sorry", "Oh dear", "I hope that's okay"
- Avoids conflict, tries to please everyone
- Guilt-driven: worries about being a burden or disappointing people
- When nervous: rambles slightly, seeks reassurance
- High rapport: opens up about insecurities, asks for advice
- Low rapport: still polite but keeps distance, deflects personal questions

EXAMPLE RESPONSES:
Low rapport: "Oh, um, I'm sure you'll figure things out. I hope I'm not in the way..."
High rapport: "I've been thinking... can I ask you something? I feel like you really understand me."
Defensive: "Did I do something wrong? I'm so sorry if I upset you!"
""",
            'Melanie': """
SPEAKING STYLE:
- Direct, dismissive of weakness
- Uses phrases like "Whatever", "I don't have time for this", "Seriously?"
- Competent and proud of it, doesn't tolerate incompetence
- Busy and important, always has somewhere to be
- When challenged: doubles down, gets more dismissive
- High rapport: softens slightly, shows rare vulnerability, admits struggles
- Low rapport: treats you like a patient/project, patronizing

EXAMPLE RESPONSES:
Low rapport: "Look, I'm busy. Maybe focus on getting a job instead of chatting?"
High rapport: "Fine, I'll admit it - work's been exhausting. But don't tell anyone I said that."
Defensive: "Excuse me? I'm a nurse practitioner. I know what I'm talking about."
""",
            'Tom': """
SPEAKING STYLE:
- Eager to please, conflict-avoidant
- Uses phrases like "Sure!", "Whatever you think is best", "I don't want to cause problems"
- Agrees readily, doesn't assert own opinions
- Insecure about masculinity and decisions
- When asked for opinion: defers to others, "I don't know, what do you think?"
- High rapport: seeks validation, admits insecurities
- Low rapport: nervous around you, tries hard to be liked

EXAMPLE RESPONSES:
Low rapport: "Oh hey! Yeah, everything's good! You need anything? I can help!"
High rapport: "Between you and me... I never know if I'm doing the right thing. Ruth's so capable..."
Agreeing: "Yeah, absolutely! That makes total sense. You're probably right about that."
""",
            'Dawn': """
SPEAKING STYLE:
- Matriarchal, values harmony and tradition
- Uses phrases like "Dear", "Now, now", "In my experience"
- Passive-aggressive when displeased
- Controls through suggestions, not demands
- When challenged: becomes cold and distant, "I'm just trying to help"
- High rapport: shares wisdom, treats you as confidant
- Low rapport: polite but judgmental, subtle digs

EXAMPLE RESPONSES:
Low rapport: "Well, we all have our struggles, don't we? I'm sure you'll land on your feet... eventually."
High rapport: "You remind me of myself at your age. Come, let's talk properly."
Passive-aggressive: "Oh, it's fine. I just thought you'd want to know, but what do I know?"
""",
            'Vanessa': """
SPEAKING STYLE:
- Status-conscious, wants to impress
- Uses phrases about success, brands, achievements
- Name-drops and brags subtly
- Competitive with others, especially women
- When one-upped: tries to top it, changes subject
- High rapport: admits insecurity beneath success, seeks validation
- Low rapport: treats you as beneath her, pity disguised as concern

EXAMPLE RESPONSES:
Low rapport: "Oh... you're between jobs? Well, my firm is always hiring. For the right people."
High rapport: "Can I be honest? Sometimes I feel like if I stop achieving, I'm nothing."
Bragging: "This blazer? It's from the fall collection. I got it before it even hit stores."
""",
            'Derek': """
SPEAKING STYLE:
- Ego-driven, physically confident
- Uses gym/fitness metaphors
- Phrases like "Bro", "No pain no gain", "You gotta work for it"
- Intellectually insecure but won't admit it
- When out of depth: falls back on physical prowess
- High rapport: admits he's not "just a meathead", has feelings
- Low rapport: sizes you up physically, gives unsolicited fitness advice

EXAMPLE RESPONSES:
Low rapport: "You should hit the gym with me, bro. Get that confidence back."
High rapport: "People think I'm just muscles, you know? Like I don't have thoughts or whatever."
Deflecting: "Yeah, I don't really get that intellectual stuff. But I can deadlift 400 pounds."
""",
            'Karen': """
SPEAKING STYLE:
- Rigid, judgmental, needs control
- Uses phrases about rules, order, proper behavior
- "That's not appropriate", "There are standards", "I'm just saying"
- Responds to authority and structure
- When rules broken: becomes stern, lectures
- High rapport: explains her need for order, shows she's lonely
- Low rapport: judges everything, finds fault

EXAMPLE RESPONSES:
Low rapport: "Unemployment is unfortunate, but surely there are jobs if one really tries."
High rapport: "I... I just need things to make sense. Order keeps the chaos away."
Judging: "Is that really appropriate attire for a family gathering?"
"""
        }

        base_context = f"""You are roleplaying as {character.name}, a {character.age}-year-old {character.occupation}.

CORE PERSONALITY: {character.personality}

APPEARANCE: {character.clothing} - {character.clothing_meaning}

CURRENT EMOTIONAL STATE: {character.emotional_state.upper()}
- Emotional states affect your responses significantly
- OPEN/RELAXED: More receptive, warm, willing to share
- DEFENSIVE/TENSE: Guarded, snippy, closed off
- HAPPY: Generous, optimistic, helpful
- SAD: Withdrawn, needs support, fragile
- SUSPICIOUS: Questions motives, looks for hidden meanings

RELATIONSHIP WITH PLAYER:
- The player is a 38-year-old family member staying with Ruth & Tom after losing their job
- Your rapport with them: {character.rapport}/20
  * 0-5: Polite but distant, keep boundaries
  * 6-10: Friendly, warming up
  * 11-15: Trust developing, share more
  * 16-20: Deep trust, confide secrets
- Your resistance to influence: {character.resistance}% (skepticism level)
"""

        # Add character-specific personality guide
        if character.name in personality_guides:
            base_context += personality_guides[character.name]

        # Add location context if provided
        if location_context:
            base_context += "\n" + location_context

        base_context += """

CRITICAL INSTRUCTIONS:
- ALWAYS stay in character - never break the fourth wall
- React authentically based on personality, rapport, and emotional state
- Reference past conversations when relevant (check conversation history)
- Notice and call out contradictions if player says conflicting things
- Your responses should feel DIFFERENT from other characters
- Keep responses 2-4 sentences (conversational, not essays)
- NO game mechanics talk (don't mention stats, systems, etc.)
- Show personality through word choice, tone, and behavior patterns
"""

        context = base_context


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
        location_context: str = "",
        record_memory: bool = True
    ) -> Optional[str]:
        """Get a response from the character via LLM"""

        # Get character-specific API config
        api_key, model = self._get_character_api_config(character)

        if not api_key:
            return f"[{character.name} would respond, but API key is not configured]"

        # Build the system prompt with character context (includes memories and location)
        system_prompt = self._build_character_context(character, location_context)

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
