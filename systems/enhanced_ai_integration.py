"""
Enhanced AI Integration for Family Dynamics RPG

Improvements to AI/LLM integration:
1. Narrative Coherence Tracking - GM tracks long-term story arcs and themes
2. Dynamic Dialogue - Characters reference multiple past events in conversations
3. Emotional Memory - Enhanced importance weighting for emotional moments
4. Character Voice Consistency - Validation and correction system
"""
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from models.character import Character
from systems.memory import Memory, MemorySystem
import requests
import config


@dataclass
class NarrativeArc:
    """Tracks a narrative arc/storyline"""
    arc_id: str
    arc_name: str
    theme: str  # Central theme (trust, redemption, family, etc.)
    involved_characters: List[str]
    start_timestamp: str
    key_events: List[str] = field(default_factory=list)
    current_status: str = "active"  # active, resolved, abandoned
    resolution: str = ""
    emotional_tone: str = "neutral"  # positive, negative, neutral, mixed

    def to_dict(self) -> dict:
        return {
            'arc_id': self.arc_id,
            'arc_name': self.arc_name,
            'theme': self.theme,
            'involved_characters': self.involved_characters,
            'start_timestamp': self.start_timestamp,
            'key_events': self.key_events,
            'current_status': self.current_status,
            'resolution': self.resolution,
            'emotional_tone': self.emotional_tone
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NarrativeArc':
        return cls(**data)


@dataclass
class CharacterVoiceProfile:
    """Tracks character voice consistency metrics"""
    character_name: str
    core_phrases: List[str] = field(default_factory=list)  # Signature phrases
    vocabulary_profile: Dict[str, int] = field(default_factory=dict)  # Word frequency
    sentence_length_avg: float = 0.0
    formality_level: int = 5  # 1-10 scale
    emotional_range: List[str] = field(default_factory=list)  # Emotions they express
    consistency_score: float = 100.0  # 0-100, tracks voice drift

    def to_dict(self) -> dict:
        return {
            'character_name': self.character_name,
            'core_phrases': self.core_phrases,
            'vocabulary_profile': self.vocabulary_profile,
            'sentence_length_avg': self.sentence_length_avg,
            'formality_level': self.formality_level,
            'emotional_range': self.emotional_range,
            'consistency_score': self.consistency_score
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CharacterVoiceProfile':
        return cls(**data)


class NarrativeCoherenceTracker:
    """Tracks long-term narrative coherence and story arcs"""

    def __init__(self):
        self.active_arcs: List[NarrativeArc] = []
        self.narrative_themes: List[str] = []  # Overall themes in the story
        self.key_moments: List[Dict] = []  # Watershed moments
        self.gm_api_key = config.GM_API_KEY
        self.gm_model = config.GM_MODEL
        self.api_url = config.OPENROUTER_API_URL

    def _make_gm_call(self, prompt: str, temperature: float = 0.5) -> Optional[str]:
        """Make LLM call using GM credentials"""
        if not self.gm_api_key:
            return None

        headers = {
            "Authorization": f"Bearer {self.gm_api_key}",
            "Content-Type": "application/json"
        }

        if config.SITE_URL:
            headers["HTTP-Referer"] = config.SITE_URL

        if config.SITE_NAME:
            headers["X-Title"] = f"{config.SITE_NAME} - Narrative"

        data = {
            "model": self.gm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 400
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
            print(f"⚠️  Narrative Tracker Error: {e}")
            return None

    def detect_new_arc(self, game_state, recent_events: List[str]) -> Optional[NarrativeArc]:
        """
        Detect if a new narrative arc is beginning

        Args:
            game_state: Current game state
            recent_events: Recent significant events

        Returns:
            NarrativeArc if detected, None otherwise
        """
        if len(recent_events) < 3:
            return None  # Need enough events to detect pattern

        # Build prompt for GM to analyze
        character_states = "\n".join([
            f"- {name}: Rapport {char.rapport}/20, State: {char.emotional_state}"
            for name, char in game_state.characters.items()
        ])

        prompt = f"""You are the Game Master analyzing narrative patterns in a psychological RPG.

RECENT EVENTS:
{chr(10).join(f"{i+1}. {event}" for i, event in enumerate(recent_events[-10:]))}

CHARACTER STATES:
{character_states}

EXISTING ARCS:
{chr(10).join(f"- {arc.arc_name}: {arc.theme}" for arc in self.active_arcs) if self.active_arcs else "None"}

QUESTION: Do these recent events suggest a NEW narrative arc is beginning?

An arc is a connected storyline involving characters where something develops over time.
Examples: "Ruth's Trust Journey", "Melanie's Softening", "Family Reconciliation"

Respond with JSON:
{{
  "new_arc_detected": <true/false>,
  "arc_name": "<short descriptive name>",
  "theme": "<central theme: trust, redemption, conflict, etc>",
  "involved_characters": ["<character names>"],
  "reasoning": "<why you think this is a new arc>"
}}

Only detect a NEW arc if events show a clear pattern/direction."""

        response = self._make_gm_call(prompt, temperature=0.4)

        if not response:
            return None

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())

                if data.get('new_arc_detected'):
                    arc = NarrativeArc(
                        arc_id=f"arc_{len(self.active_arcs)}_{datetime.now().strftime('%Y%m%d%H%M')}",
                        arc_name=data['arc_name'],
                        theme=data['theme'],
                        involved_characters=data['involved_characters'],
                        start_timestamp=datetime.now().isoformat(),
                        key_events=recent_events[-3:]  # Start with recent events
                    )

                    self.active_arcs.append(arc)

                    # Track theme if new
                    if data['theme'] not in self.narrative_themes:
                        self.narrative_themes.append(data['theme'])

                    return arc
        except Exception as e:
            print(f"Error detecting arc: {e}")

        return None

    def update_arc(self, arc_id: str, new_event: str, game_state) -> bool:
        """
        Update an existing arc with a new event

        Returns:
            True if arc updated, False if not found
        """
        arc = next((a for a in self.active_arcs if a.arc_id == arc_id), None)
        if not arc:
            return False

        arc.key_events.append(new_event)

        # Check if arc should be resolved
        if len(arc.key_events) >= 5:
            self._check_arc_resolution(arc, game_state)

        return True

    def _check_arc_resolution(self, arc: NarrativeArc, game_state):
        """Check if an arc has reached resolution"""
        character_states = "\n".join([
            f"- {name}: Rapport {char.rapport}/20, State: {char.emotional_state}"
            for name in arc.involved_characters
            if name in game_state.characters
            for char in [game_state.characters[name]]
        ])

        prompt = f"""You are the Game Master analyzing if a narrative arc has resolved.

ARC: {arc.arc_name}
THEME: {arc.theme}
CHARACTERS: {', '.join(arc.involved_characters)}

KEY EVENTS:
{chr(10).join(f"{i+1}. {event}" for i, event in enumerate(arc.key_events))}

CURRENT CHARACTER STATES:
{character_states}

Has this arc reached a natural resolution (positive or negative)?

Respond with JSON:
{{
  "is_resolved": <true/false>,
  "resolution_type": "<positive/negative/neutral>",
  "resolution_summary": "<1-2 sentence summary>",
  "emotional_tone": "<final tone: positive/negative/bittersweet/neutral>"
}}"""

        response = self._make_gm_call(prompt, temperature=0.4)

        if response:
            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())

                    if data.get('is_resolved'):
                        arc.current_status = "resolved"
                        arc.resolution = data['resolution_summary']
                        arc.emotional_tone = data['emotional_tone']
            except Exception as e:
                print(f"Error checking resolution: {e}")

    def get_narrative_context_for_llm(self, character: Character) -> str:
        """
        Get narrative context to include in character LLM prompts

        Returns:
            Formatted string with relevant narrative context
        """
        if not self.active_arcs:
            return ""

        # Find arcs involving this character
        relevant_arcs = [arc for arc in self.active_arcs if character.name in arc.involved_characters]

        if not relevant_arcs:
            return ""

        context = "\n\nNARRATIVE CONTEXT (roleplay awareness of these ongoing storylines):\n"

        for arc in relevant_arcs:
            if arc.current_status == "active":
                recent_events = arc.key_events[-3:]  # Last 3 events
                context += f"- {arc.arc_name} ({arc.theme}): "
                context += " → ".join(recent_events)
                context += "\n"

        return context

    def identify_key_moment(self, event_description: str, impact_level: int) -> bool:
        """
        Mark an event as a key watershed moment

        Args:
            event_description: What happened
            impact_level: 1-10 scale of importance

        Returns:
            True if recorded as key moment
        """
        if impact_level >= 7:
            self.key_moments.append({
                'timestamp': datetime.now().isoformat(),
                'description': event_description,
                'impact_level': impact_level
            })
            return True
        return False

    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'active_arcs': [arc.to_dict() for arc in self.active_arcs],
            'narrative_themes': self.narrative_themes,
            'key_moments': self.key_moments
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NarrativeCoherenceTracker':
        """Deserialize from save"""
        tracker = cls()
        tracker.active_arcs = [NarrativeArc.from_dict(arc_data) for arc_data in data.get('active_arcs', [])]
        tracker.narrative_themes = data.get('narrative_themes', [])
        tracker.key_moments = data.get('key_moments', [])
        return tracker


class DynamicDialogueEnhancer:
    """Enhances dialogue by referencing multiple past events"""

    @staticmethod
    def build_multi_event_context(character: Character, current_topic: str = "") -> str:
        """
        Build rich context by referencing multiple past events

        Args:
            character: The character
            current_topic: Current conversation topic for relevance

        Returns:
            Formatted string with multi-event references
        """
        if not hasattr(character, 'memories') or not character.memories:
            return ""

        # Get diverse memories (different types)
        emotional_memories = [m for m in character.memories if m.memory_type == 'emotional_moment']
        conversation_memories = [m for m in character.memories if m.memory_type == 'conversation']
        event_memories = [m for m in character.memories if m.memory_type == 'important_event']

        # Build context with variety
        context_parts = []

        # Add important emotional moments (up to 2)
        if emotional_memories:
            sorted_emotional = sorted(emotional_memories, key=lambda m: m.importance, reverse=True)
            for mem in sorted_emotional[:2]:
                context_parts.append(f"[EMOTIONAL] {mem.content} (You felt: {mem.emotional_context})")

        # Add relevant conversations (up to 3)
        if conversation_memories:
            relevant_convos = MemorySystem.retrieve_relevant_memories(
                character,
                query_context=current_topic,
                count=3,
                memory_types=['conversation']
            )
            for mem in relevant_convos:
                context_parts.append(f"[CONVERSATION] {mem.content}")

        # Add significant events (up to 2)
        if event_memories:
            sorted_events = sorted(event_memories, key=lambda m: (m.importance, m.timestamp), reverse=True)
            for mem in sorted_events[:2]:
                context_parts.append(f"[EVENT] {mem.content}")

        if context_parts:
            return "\n\nPAST EXPERIENCES TO NATURALLY REFERENCE:\n" + "\n".join(context_parts) + "\n"

        return ""

    @staticmethod
    def extract_connection_opportunities(memories: List[Memory], current_context: str) -> List[str]:
        """
        Find opportunities to connect current situation to past events

        Returns:
            List of connection prompts like "This reminds you of when..."
        """
        connections = []

        current_words = set(current_context.lower().split())

        for memory in memories:
            # Skip low-importance memories
            if memory.importance < 6:
                continue

            memory_words = set(memory.content.lower().split())
            overlap = current_words & memory_words

            # If significant overlap, suggest connection
            if len(overlap) >= 3:
                connections.append(f"This reminds you of: {memory.content[:100]}")

        return connections[:2]  # Limit to 2 connections


class EmotionalMemoryEnhancer:
    """Enhanced emotional memory system with decay and importance weighting"""

    @staticmethod
    def calculate_emotional_importance(
        content: str,
        emotional_context: str,
        rapport_level: int,
        related_characters: List[str]
    ) -> int:
        """
        Calculate importance score with enhanced emotional weighting

        Returns:
            Importance score 1-10
        """
        base_importance = 5

        # Emotional context boosts
        emotional_intensity = {
            'ecstatic': 3,
            'devastated': 3,
            'furious': 3,
            'betrayed': 3,
            'loved': 3,
            'traumatized': 3,
            'joyful': 2,
            'angry': 2,
            'sad': 2,
            'happy': 2,
            'hurt': 2,
            'anxious': 1,
            'relaxed': 1,
            'open': 1,
            'tense': 1
        }

        emotional_context_lower = emotional_context.lower()
        for emotion, boost in emotional_intensity.items():
            if emotion in emotional_context_lower:
                base_importance += boost
                break

        # Content analysis
        high_impact_words = [
            'always', 'never', 'promise', 'secret', 'confession', 'truth', 'lie',
            'betray', 'trust', 'love', 'hate', 'family', 'forever', 'goodbye'
        ]

        content_lower = content.lower()
        word_matches = sum(1 for word in high_impact_words if word in content_lower)
        base_importance += min(word_matches, 2)  # Max +2 from words

        # Rapport modifier (deeper relationships = more memorable)
        if rapport_level >= 15:
            base_importance += 2
        elif rapport_level >= 10:
            base_importance += 1

        # Multiple characters involved = more significant
        if len(related_characters) >= 3:
            base_importance += 1

        return min(10, base_importance)

    @staticmethod
    def apply_memory_decay(memories: List[Memory], current_time: datetime) -> List[Memory]:
        """
        Apply time-based decay to memory importance

        Emotional memories fade slower than regular ones

        Returns:
            List of memories with updated importance
        """
        decayed_memories = []

        for memory in memories:
            try:
                memory_time = datetime.fromisoformat(memory.timestamp)
                time_diff = current_time - memory_time
                days_old = time_diff.days

                # Different decay rates by type
                if memory.memory_type == 'emotional_moment':
                    decay_rate = 0.1  # Slow decay
                    min_importance = 4  # Don't decay below 4
                elif memory.memory_type in ['phs_triggered', 'phs_planted']:
                    decay_rate = 0.05  # Very slow decay
                    min_importance = 5
                elif memory.memory_type == 'important_event':
                    decay_rate = 0.15  # Medium decay
                    min_importance = 3
                else:  # conversation
                    decay_rate = 0.2  # Faster decay
                    min_importance = 2

                # Calculate decay
                decay_amount = int(days_old * decay_rate)
                new_importance = max(min_importance, memory.importance - decay_amount)

                # Update memory
                memory.importance = new_importance

                # Only keep memories above threshold
                if new_importance >= 2:
                    decayed_memories.append(memory)
            except (ValueError, AttributeError):
                # Invalid timestamp, keep as is
                decayed_memories.append(memory)

        return decayed_memories

    @staticmethod
    def consolidate_emotional_moments(character: Character) -> List[Memory]:
        """
        Consolidate similar emotional moments into stronger memories

        Returns:
            Consolidated list of emotional memories
        """
        emotional_memories = [m for m in character.memories if m.memory_type == 'emotional_moment']

        if len(emotional_memories) < 3:
            return character.memories  # Not enough to consolidate

        # Group by emotional context
        emotion_groups: Dict[str, List[Memory]] = {}

        for mem in emotional_memories:
            emotion = mem.emotional_context
            if emotion not in emotion_groups:
                emotion_groups[emotion] = []
            emotion_groups[emotion].append(mem)

        # Consolidate groups with 3+ similar memories
        consolidated = []
        processed_mem_ids = set()

        for emotion, group in emotion_groups.items():
            if len(group) >= 3:
                # Create consolidated memory
                combined_content = f"Multiple moments of feeling {emotion}: " + "; ".join([
                    m.content[:50] for m in group[:3]
                ])

                consolidated_mem = Memory(
                    timestamp=max(m.timestamp for m in group),
                    memory_type='emotional_moment',
                    content=combined_content,
                    importance=min(10, max(m.importance for m in group) + 1),  # Boost importance
                    related_characters=list(set(c for m in group for c in m.related_characters)),
                    emotional_context=emotion,
                    tags=['consolidated', 'emotional', 'pattern']
                )

                consolidated.append(consolidated_mem)
                processed_mem_ids.update(id(m) for m in group)

        # Keep unconsolidated memories
        for mem in character.memories:
            if id(mem) not in processed_mem_ids:
                consolidated.append(mem)

        return consolidated


class CharacterVoiceValidator:
    """Validates and maintains character voice consistency"""

    def __init__(self):
        self.voice_profiles: Dict[str, CharacterVoiceProfile] = {}
        self.gm_api_key = config.GM_API_KEY
        self.gm_model = config.GM_MODEL
        self.api_url = config.OPENROUTER_API_URL

    def initialize_voice_profile(self, character: Character) -> CharacterVoiceProfile:
        """
        Initialize voice profile for a character based on their personality
        """
        # Define core phrases and patterns for each character
        core_phrases_map = {
            'Ruth': ["I'm sorry", "Oh dear", "I hope", "Is that okay", "I worry"],
            'Melanie': ["Whatever", "Seriously?", "I don't have time", "Look,", "Honestly,"],
            'Tom': ["Sure!", "Whatever you think", "I don't want to", "You're probably right"],
            'Dawn': ["Dear", "Now, now", "In my experience", "I'm just saying", "Well,"],
            'Vanessa': ["Actually,", "I mean,", "You know what", "To be honest", "Like"],
            'Derek': ["Bro", "No pain no gain", "You gotta", "Man,", "That's weak"],
            'Karen': ["That's inappropriate", "There are rules", "I'm just saying", "Proper", "Standards"]
        }

        # Formality levels (1-10)
        formality_map = {
            'Ruth': 6,
            'Melanie': 7,
            'Tom': 5,
            'Dawn': 8,
            'Vanessa': 7,
            'Derek': 3,
            'Karen': 9
        }

        profile = CharacterVoiceProfile(
            character_name=character.name,
            core_phrases=core_phrases_map.get(character.name, []),
            formality_level=formality_map.get(character.name, 5)
        )

        self.voice_profiles[character.name] = profile
        return profile

    def validate_response(
        self,
        character: Character,
        response: str,
        expected_emotional_state: str
    ) -> Tuple[bool, float, List[str]]:
        """
        Validate if a character's response matches their voice

        Returns:
            (is_valid, consistency_score, issues_found)
        """
        if character.name not in self.voice_profiles:
            self.initialize_voice_profile(character)

        profile = self.voice_profiles[character.name]
        issues = []
        score = 100.0

        # Check for core phrase usage
        response_lower = response.lower()
        phrase_found = any(phrase.lower() in response_lower for phrase in profile.core_phrases)

        # Not required, but boost score if found
        if phrase_found:
            score += 5

        # Check sentence length consistency
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        if sentences:
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)

            # Track average over time
            if profile.sentence_length_avg == 0:
                profile.sentence_length_avg = avg_length
            else:
                # Check if significantly different
                diff_ratio = abs(avg_length - profile.sentence_length_avg) / profile.sentence_length_avg

                if diff_ratio > 0.5:  # 50% difference
                    score -= 15
                    issues.append(f"Unusual sentence length: {avg_length:.1f} words (typical: {profile.sentence_length_avg:.1f})")

                # Update rolling average
                profile.sentence_length_avg = (profile.sentence_length_avg * 0.8) + (avg_length * 0.2)

        # Check formality via vocabulary
        informal_markers = ['gonna', 'wanna', 'yeah', 'nah', 'bro', 'dude']
        formal_markers = ['indeed', 'furthermore', 'therefore', 'shall', 'ought']

        informal_count = sum(1 for marker in informal_markers if marker in response_lower)
        formal_count = sum(1 for marker in formal_markers if marker in response_lower)

        if profile.formality_level >= 7 and informal_count > formal_count:
            score -= 10
            issues.append("Too informal for character")
        elif profile.formality_level <= 3 and formal_count > informal_count:
            score -= 10
            issues.append("Too formal for character")

        # Update consistency score
        profile.consistency_score = (profile.consistency_score * 0.9) + (score * 0.1)

        return (score >= 70, score, issues)

    def generate_correction_prompt(self, character: Character, response: str, issues: List[str]) -> str:
        """
        Generate a prompt to correct voice inconsistencies

        Returns:
            Corrected prompt to re-generate response
        """
        profile = self.voice_profiles[character.name]

        correction = f"""The previous response had voice consistency issues:
{chr(10).join(f"- {issue}" for issue in issues)}

{character.name}'s CORE VOICE TRAITS:
- Uses phrases like: {', '.join(profile.core_phrases[:3])}
- Formality level: {profile.formality_level}/10
- Typical sentence length: {profile.sentence_length_avg:.0f} words

Please regenerate the response maintaining {character.name}'s authentic voice and personality."""

        return correction

    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'voice_profiles': {
                name: profile.to_dict()
                for name, profile in self.voice_profiles.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CharacterVoiceValidator':
        """Deserialize from save"""
        validator = cls()
        validator.voice_profiles = {
            name: CharacterVoiceProfile.from_dict(profile_data)
            for name, profile_data in data.get('voice_profiles', {}).items()
        }
        return validator


class EnhancedAIIntegration:
    """
    Main class that integrates all AI enhancements
    """

    def __init__(self):
        self.narrative_tracker = NarrativeCoherenceTracker()
        self.dialogue_enhancer = DynamicDialogueEnhancer()
        self.emotional_memory = EmotionalMemoryEnhancer()
        self.voice_validator = CharacterVoiceValidator()

    def enhance_character_prompt(
        self,
        character: Character,
        base_prompt: str,
        current_topic: str = ""
    ) -> str:
        """
        Enhance character prompt with all AI improvements

        Args:
            character: The character
            base_prompt: Base LLM prompt
            current_topic: Current conversation topic

        Returns:
            Enhanced prompt with narrative, multi-event, and emotional context
        """
        enhanced = base_prompt

        # Add narrative coherence context
        narrative_context = self.narrative_tracker.get_narrative_context_for_llm(character)
        if narrative_context:
            enhanced += narrative_context

        # Add multi-event dialogue context
        multi_event_context = self.dialogue_enhancer.build_multi_event_context(character, current_topic)
        if multi_event_context:
            enhanced += multi_event_context

        return enhanced

    def process_character_response(
        self,
        character: Character,
        response: str,
        expected_emotional_state: str
    ) -> Tuple[str, bool, List[str]]:
        """
        Process and validate character response

        Returns:
            (final_response, needs_regeneration, issues)
        """
        is_valid, score, issues = self.voice_validator.validate_response(
            character, response, expected_emotional_state
        )

        return (response, not is_valid, issues)

    def record_enhanced_memory(
        self,
        character: Character,
        content: str,
        memory_type: str,
        emotional_context: str = "",
        related_characters: List[str] = None
    ) -> Memory:
        """
        Record memory with enhanced emotional importance calculation

        Returns:
            Created Memory object
        """
        importance = self.emotional_memory.calculate_emotional_importance(
            content=content,
            emotional_context=emotional_context or character.emotional_state,
            rapport_level=character.rapport,
            related_characters=related_characters or []
        )

        memory = MemorySystem.create_memory(
            memory_type=memory_type,
            content=content,
            importance=importance,
            related_characters=related_characters or [],
            emotional_context=emotional_context or character.emotional_state
        )

        MemorySystem.add_memory_to_character(character, memory)

        return memory

    def update_narrative(self, game_state, event_description: str, involved_characters: List[str]):
        """
        Update narrative tracking with new event
        """
        # Check for new arcs
        recent_events = [event_description]  # Would normally get from game state
        new_arc = self.narrative_tracker.detect_new_arc(game_state, recent_events)

        if new_arc:
            print(f"\n✨ New narrative arc detected: {new_arc.arc_name}")
            print(f"   Theme: {new_arc.theme}")
            print(f"   Characters: {', '.join(new_arc.involved_characters)}")

        # Update existing arcs
        for arc in self.narrative_tracker.active_arcs:
            if any(char in arc.involved_characters for char in involved_characters):
                arc.key_events.append(event_description)

    def apply_memory_decay(self, character: Character):
        """Apply time-based memory decay to character"""
        current_time = datetime.now()
        character.memories = self.emotional_memory.apply_memory_decay(
            character.memories,
            current_time
        )

    def consolidate_emotional_memories(self, character: Character):
        """Consolidate similar emotional memories"""
        character.memories = self.emotional_memory.consolidate_emotional_moments(character)

    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'narrative_tracker': self.narrative_tracker.to_dict(),
            'voice_validator': self.voice_validator.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EnhancedAIIntegration':
        """Deserialize from save"""
        integration = cls()

        if 'narrative_tracker' in data:
            integration.narrative_tracker = NarrativeCoherenceTracker.from_dict(data['narrative_tracker'])

        if 'voice_validator' in data:
            integration.voice_validator = CharacterVoiceValidator.from_dict(data['voice_validator'])

        return integration
