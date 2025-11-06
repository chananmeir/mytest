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
        Retrieve relevant memories for a character

        Args:
            character: The character to retrieve memories from
            query_context: Optional context to find relevant memories
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

        # Sort by importance and recency
        filtered.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)

        return filtered[:count]

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
