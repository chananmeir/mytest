"""
Memory system for Family Dynamics RPG
Each character maintains memories of interactions that can be retrieved for context
"""
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
import config


@dataclass
class Memory:
    """Represents a single memory for a character"""
    timestamp: str
    memory_type: str  # 'conversation', 'emotional_moment', 'important_event', 'phs_planted', 'phs_triggered'
    content: str
    importance: int  # 1-10, higher = more important
    related_characters: List[str] = field(default_factory=list)
    emotional_context: str = ""  # What emotional state they were in
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for saving"""
        return {
            'timestamp': self.timestamp,
            'memory_type': self.memory_type,
            'content': self.content,
            'importance': self.importance,
            'related_characters': self.related_characters,
            'emotional_context': self.emotional_context,
            'tags': self.tags
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Memory':
        """Create from dictionary"""
        return cls(**data)


class MemorySystem:
    """Manages character memories"""

    @staticmethod
    def create_memory(
        memory_type: str,
        content: str,
        importance: int,
        related_characters: List[str] = None,
        emotional_context: str = "",
        tags: List[str] = None
    ) -> Memory:
        """Create a new memory"""
        return Memory(
            timestamp=datetime.now().isoformat(),
            memory_type=memory_type,
            content=content,
            importance=importance,
            related_characters=related_characters or [],
            emotional_context=emotional_context,
            tags=tags or []
        )

    @staticmethod
    def add_memory_to_character(character, memory: Memory) -> None:
        """Add a memory to a character, respecting max limit"""
        if not hasattr(character, 'memories'):
            character.memories = []

        character.memories.append(memory)

        # Keep only the most recent memories if we exceed the limit
        if len(character.memories) > config.MAX_MEMORIES_PER_CHARACTER:
            # Sort by importance and timestamp, keep top memories
            character.memories.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
            character.memories = character.memories[:config.MAX_MEMORIES_PER_CHARACTER]

    @staticmethod
    def retrieve_relevant_memories(
        character,
        query_context: str = "",
        count: int = None,
        min_importance: int = 0,
        memory_types: List[str] = None
    ) -> List[Memory]:
        """
        Retrieve relevant memories for a character with semantic matching

        Args:
            character: The character to retrieve memories from
            query_context: Optional context to find relevant memories (searches content)
            count: Number of memories to retrieve (default from config)
            min_importance: Minimum importance threshold
            memory_types: Filter by memory types
        """
        if not hasattr(character, 'memories') or not character.memories:
            return []

        count = count or config.MEMORY_RETRIEVAL_COUNT

        # Filter by importance
        filtered = [m for m in character.memories if m.importance >= min_importance]

        # Filter by type if specified
        if memory_types:
            filtered = [m for m in filtered if m.memory_type in memory_types]

        # If query context provided, do semantic matching
        if query_context:
            query_words = set(query_context.lower().split())

            # Score each memory by keyword overlap
            scored_memories = []
            for memory in filtered:
                content_words = set(memory.content.lower().split())
                tags_words = set(' '.join(memory.tags).lower().split())

                # Calculate relevance score
                keyword_overlap = len(query_words & (content_words | tags_words))

                # Combine relevance with importance and recency
                relevance_score = (
                    keyword_overlap * 10 +  # Keyword match is very important
                    memory.importance * 2 +  # Importance matters
                    (1 if memory.timestamp > datetime.now().replace(hour=0, minute=0).isoformat() else 0)  # Recent bonus
                )

                scored_memories.append((relevance_score, memory))

            # Sort by relevance score
            scored_memories.sort(key=lambda x: x[0], reverse=True)
            return [m for _, m in scored_memories[:count]]

        else:
            # No query context - prioritize important and recent memories
            # Combine importance with recency (newer memories get slight boost)
            scored = []
            for memory in filtered:
                recency_boost = 1 if memory.timestamp > datetime.now().replace(hour=0, minute=0).isoformat() else 0
                score = memory.importance * 10 + recency_boost * 5
                scored.append((score, memory))

            scored.sort(key=lambda x: (x[0], x[1].timestamp), reverse=True)
            return [m for _, m in scored[:count]]

    @staticmethod
    def get_recent_memories(character, count: int = 5) -> List[Memory]:
        """Get the most recent memories"""
        if not hasattr(character, 'memories') or not character.memories:
            return []

        # Sort by timestamp (most recent first)
        sorted_memories = sorted(
            character.memories,
            key=lambda m: m.timestamp,
            reverse=True
        )

        return sorted_memories[:count]

    @staticmethod
    def get_important_memories(character, min_importance: int = 7) -> List[Memory]:
        """Get high-importance memories"""
        if not hasattr(character, 'memories') or not character.memories:
            return []

        important = [m for m in character.memories if m.importance >= min_importance]
        important.sort(key=lambda m: m.importance, reverse=True)

        return important

    @staticmethod
    def format_memories_for_llm(memories: List[Memory]) -> str:
        """Format memories as a string for LLM context"""
        if not memories:
            return "No specific memories."

        formatted = "RELEVANT MEMORIES:\n"

        for i, memory in enumerate(memories, 1):
            formatted += f"\n{i}. [{memory.memory_type.upper()}] {memory.content}"

            if memory.emotional_context:
                formatted += f" (You were feeling: {memory.emotional_context})"

            if memory.related_characters:
                formatted += f" [Involved: {', '.join(memory.related_characters)}]"

        return formatted

    @staticmethod
    def record_conversation(
        character,
        speaker: str,
        message: str,
        importance: int = 5,
        emotional_state: str = ""
    ):
        """Helper to record a conversation memory"""
        memory = MemorySystem.create_memory(
            memory_type='conversation',
            content=f"{speaker} said: \"{message}\"",
            importance=importance,
            related_characters=[speaker] if speaker != character.name else [],
            emotional_context=emotional_state or character.emotional_state,
            tags=['conversation']
        )

        MemorySystem.add_memory_to_character(character, memory)

    @staticmethod
    def record_emotional_moment(
        character,
        description: str,
        importance: int = 7,
        related_characters: List[str] = None
    ):
        """Helper to record an emotional moment"""
        memory = MemorySystem.create_memory(
            memory_type='emotional_moment',
            content=description,
            importance=importance,
            related_characters=related_characters or [],
            emotional_context=character.emotional_state,
            tags=['emotional', 'significant']
        )

        MemorySystem.add_memory_to_character(character, memory)

    @staticmethod
    def record_phs_planted(
        character,
        phs_description: str,
        by_who: str = "You"
    ):
        """Helper to record when a PHS was planted"""
        memory = MemorySystem.create_memory(
            memory_type='phs_planted',
            content=f"A subtle suggestion was planted: {phs_description}",
            importance=8,
            related_characters=[by_who],
            emotional_context=character.emotional_state,
            tags=['phs', 'influenced']
        )

        MemorySystem.add_memory_to_character(character, memory)

    @staticmethod
    def record_phs_triggered(
        character,
        phs_description: str,
        reaction: str
    ):
        """Helper to record when a PHS was triggered"""
        memory = MemorySystem.create_memory(
            memory_type='phs_triggered',
            content=f"Felt compelled: {phs_description}. Reacted by: {reaction}",
            importance=9,
            related_characters=[],
            emotional_context=character.emotional_state,
            tags=['phs', 'triggered', 'influenced']
        )

        MemorySystem.add_memory_to_character(character, memory)

    @staticmethod
    def record_important_event(
        character,
        event_description: str,
        importance: int = 8,
        related_characters: List[str] = None
    ):
        """Helper to record an important event"""
        memory = MemorySystem.create_memory(
            memory_type='important_event',
            content=event_description,
            importance=importance,
            related_characters=related_characters or [],
            emotional_context=character.emotional_state,
            tags=['event', 'significant']
        )

        MemorySystem.add_memory_to_character(character, memory)

    @staticmethod
    def record_clothing_change(
        character,
        old_clothing: str,
        new_clothing: str,
        occasion: str = "",
        importance: int = 6
    ):
        """Helper to record a clothing change"""
        content = f"Changed clothes from '{old_clothing}' to '{new_clothing}'"
        if occasion:
            content += f" for {occasion}"

        memory = MemorySystem.create_memory(
            memory_type='important_event',
            content=content,
            importance=importance,
            related_characters=[],
            emotional_context=character.emotional_state,
            tags=['clothing', 'appearance', 'change']
        )

        MemorySystem.add_memory_to_character(character, memory)

    @staticmethod
    def consolidate_memories(character, similarity_threshold: int = 7):
        """
        Consolidate similar memories to prevent redundancy
        Merges memories with similar content and tags
        """
        if not hasattr(character, 'memories') or len(character.memories) < 10:
            return  # Not enough memories to consolidate

        consolidated = []
        processed_indices = set()

        for i, memory1 in enumerate(character.memories):
            if i in processed_indices:
                continue

            # Find similar memories
            similar = [memory1]
            for j, memory2 in enumerate(character.memories[i+1:], start=i+1):
                if j in processed_indices:
                    continue

                # Check similarity based on tags and content words
                tags1 = set(memory1.tags)
                tags2 = set(memory2.tags)
                tag_overlap = len(tags1 & tags2)

                content1_words = set(memory1.content.lower().split())
                content2_words = set(memory2.content.lower().split())
                content_overlap = len(content1_words & content2_words)

                # If similar enough, group them
                if tag_overlap >= 2 and content_overlap >= similarity_threshold:
                    similar.append(memory2)
                    processed_indices.add(j)

            # If found similar memories, consolidate them
            if len(similar) > 1:
                # Take the highest importance and most recent timestamp
                max_importance = max(m.importance for m in similar)
                latest_timestamp = max(m.timestamp for m in similar)

                # Combine unique tags
                combined_tags = list(set(tag for m in similar for tag in m.tags))

                # Create consolidated content
                consolidated_content = f"Multiple related events: {memory1.content}"
                if len(similar) > 2:
                    consolidated_content += f" (and {len(similar)-1} similar moments)"

                # Create consolidated memory
                consolidated_memory = Memory(
                    timestamp=latest_timestamp,
                    memory_type=memory1.memory_type,
                    content=consolidated_content,
                    importance=min(max_importance + 1, 10),  # Boost importance slightly
                    related_characters=list(set(c for m in similar for c in m.related_characters)),
                    emotional_context=memory1.emotional_context,
                    tags=combined_tags
                )

                consolidated.append(consolidated_memory)
                processed_indices.add(i)
            else:
                consolidated.append(memory1)
                processed_indices.add(i)

        # Update character's memories
        character.memories = consolidated

    @staticmethod
    def get_conversation_summary(character, last_n_messages: int = 20) -> str:
        """
        Generate a summary of recent conversation history
        This can be used instead of full conversation history to save tokens
        """
        if not hasattr(character, 'conversation_history') or not character.conversation_history:
            return "No recent conversation."

        recent = character.conversation_history[-last_n_messages:]

        # Count messages by role
        user_count = sum(1 for msg in recent if msg.get('role') == 'user')
        assistant_count = sum(1 for msg in recent if msg.get('role') == 'assistant')

        # Get key themes from conversation
        all_content = ' '.join(msg.get('content', '') for msg in recent)
        words = all_content.lower().split()

        # Simple keyword extraction (filter common words)
        common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'i', 'you', 'me', 'my', 'your',
                        'and', 'or', 'but', 'to', 'in', 'on', 'at', 'for', 'with', 'about'}
        keywords = [w for w in set(words) if len(w) > 4 and w not in common_words]
        top_keywords = sorted(keywords, key=lambda w: words.count(w), reverse=True)[:5]

        summary = f"Recent conversation ({user_count} exchanges): "
        if top_keywords:
            summary += f"Topics discussed: {', '.join(top_keywords)}. "

        # Add emotional context
        summary += f"Your current emotional state: {character.emotional_state}. "
        summary += f"Rapport level: {character.rapport}/20."

        return summary

    @staticmethod
    def analyze_memory_importance(content: str, memory_type: str, emotional_context: str = "") -> int:
        """
        Automatically analyze and suggest importance score for a memory
        Returns: importance score 1-10
        """
        importance = 5  # Base importance

        # Memory type affects base importance
        type_importance = {
            'phs_triggered': 9,
            'phs_planted': 8,
            'important_event': 7,
            'emotional_moment': 7,
            'conversation': 5
        }
        importance = type_importance.get(memory_type, 5)

        # Emotional keywords boost importance
        emotional_keywords = {
            'love', 'hate', 'angry', 'furious', 'ecstatic', 'devastated',
            'betrayed', 'shocked', 'traumatic', 'wonderful', 'terrible'
        }

        content_lower = content.lower()
        if any(keyword in content_lower for keyword in emotional_keywords):
            importance = min(importance + 2, 10)

        # Strong emotional context boosts importance
        strong_emotions = {'furious', 'devastated', 'ecstatic', 'traumatized', 'betrayed'}
        if any(emotion in emotional_context.lower() for emotion in strong_emotions):
            importance = min(importance + 1, 10)

        return importance
