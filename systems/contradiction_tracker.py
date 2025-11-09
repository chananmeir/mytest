"""
Contradiction Tracker - Detects and tracks contradictions in player statements
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime


@dataclass
class PlayerStatement:
    """Represents a statement the player made"""
    timestamp: str
    character_told: str  # Which character was told this
    content: str
    topic: str  # General topic (job, feelings, plans, etc.)
    keywords: List[str] = field(default_factory=list)


class ContradictionTracker:
    """Tracks player statements and detects contradictions"""

    # Topic keywords for categorization
    TOPIC_KEYWORDS = {
        'job': ['job', 'work', 'employment', 'career', 'unemployed', 'employed', 'hired', 'fired', 'interview'],
        'feelings': ['feel', 'feeling', 'think', 'believe', 'love', 'hate', 'like', 'dislike', 'enjoy'],
        'plans': ['plan', 'planning', 'will', 'going to', 'intend', 'want', 'hope', 'wish'],
        'past': ['was', 'had', 'used to', 'before', 'previously', 'earlier', 'ago'],
        'family': ['family', 'mother', 'father', 'sister', 'brother', 'relative', 'parent'],
        'relationship': ['relationship', 'dating', 'married', 'single', 'partner', 'boyfriend', 'girlfriend'],
        'opinion': ['opinion', 'think', 'believe', 'view', 'stance', 'position'],
        'health': ['health', 'sick', 'healthy', 'ill', 'feeling', 'pain', 'doctor'],
        'money': ['money', 'rich', 'poor', 'afford', 'expensive', 'cheap', 'broke', 'wealthy'],
        'goals': ['goal', 'ambition', 'dream', 'aspire', 'achieve', 'success']
    }

    # Contradiction patterns (opposing word pairs)
    CONTRADICTION_PAIRS = [
        # Job/Employment
        (['employed', 'working', 'have a job', 'hired'], ['unemployed', 'jobless', 'fired', 'quit']),
        # Feelings/Opinions
        (['love', 'adore', 'enjoy'], ['hate', 'despise', 'dislike']),
        # States
        (['happy', 'content', 'satisfied'], ['unhappy', 'sad', 'dissatisfied']),
        # Relationships
        (['single', 'alone', 'not dating'], ['in a relationship', 'dating', 'have a partner']),
        # Health
        (['healthy', 'well', 'feeling good'], ['sick', 'ill', 'unwell', 'feeling bad']),
        # Money
        (['rich', 'wealthy', 'have money'], ['poor', 'broke', 'no money']),
        # Plans
        (['staying', 'remaining', 'not leaving'], ['leaving', 'going', 'departing']),
        # Agreement
        (['agree', 'support', 'approve'], ['disagree', 'oppose', 'disapprove'])
    ]

    @staticmethod
    def detect_topic(message: str) -> Optional[str]:
        """
        Detect the topic of a message based on keywords

        Args:
            message: The message to analyze

        Returns:
            Topic name or None
        """
        message_lower = message.lower()

        # Check each topic
        for topic, keywords in ContradictionTracker.TOPIC_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic

        return None

    @staticmethod
    def extract_keywords(message: str) -> List[str]:
        """
        Extract meaningful keywords from a message

        Args:
            message: The message to analyze

        Returns:
            List of keywords
        """
        # Common words to ignore
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'i', 'you', 'me', 'my', 'your',
            'and', 'or', 'but', 'to', 'in', 'on', 'at', 'for', 'with', 'about', 'as', 'by',
            'that', 'this', 'it', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'can', 'may', 'might', 'just', 'so', 'than', 'such'
        }

        words = message.lower().split()
        keywords = [w.strip('.,!?"\'') for w in words if w not in stopwords and len(w) > 3]

        return keywords

    @staticmethod
    def check_contradiction(
        new_statement: str,
        previous_statements: List[PlayerStatement],
        same_character_only: bool = False
    ) -> Optional[Tuple[PlayerStatement, str]]:
        """
        Check if a new statement contradicts previous statements

        Args:
            new_statement: The new statement to check
            previous_statements: List of previous player statements
            same_character_only: Only check for contradictions told to the same character

        Returns:
            Tuple of (contradicted_statement, contradiction_type) or None
        """
        # Detect topic of new statement
        new_topic = ContradictionTracker.detect_topic(new_statement)
        new_keywords = set(ContradictionTracker.extract_keywords(new_statement))

        # Filter previous statements by topic
        relevant_statements = []
        for stmt in previous_statements:
            if stmt.topic == new_topic or not new_topic:
                relevant_statements.append(stmt)

        # Check each relevant previous statement
        for prev_stmt in relevant_statements:
            prev_keywords = set(prev_stmt.keywords)

            # Check for contradictory word pairs
            for positive_words, negative_words in ContradictionTracker.CONTRADICTION_PAIRS:
                # Check if new statement has one category and old has the opposite
                new_has_positive = any(word in new_statement.lower() for word in positive_words)
                new_has_negative = any(word in new_statement.lower() for word in negative_words)

                prev_has_positive = any(word in prev_stmt.content.lower() for word in positive_words)
                prev_has_negative = any(word in prev_stmt.content.lower() for word in negative_words)

                # Contradiction detected
                if (new_has_positive and prev_has_negative) or (new_has_negative and prev_has_positive):
                    return (prev_stmt, "opposing_statements")

            # Check for direct keyword contradiction (e.g., "I love X" vs "I hate X")
            # Look for same subject with different modifiers
            keyword_overlap = new_keywords & prev_keywords
            if len(keyword_overlap) >= 2:  # Same subject mentioned
                # Check if sentiment is opposite
                positive_indicators = {'love', 'like', 'enjoy', 'great', 'good', 'yes', 'definitely'}
                negative_indicators = {'hate', 'dislike', 'terrible', 'bad', 'no', 'never', 'not'}

                new_sentiment = (
                    1 if any(word in new_statement.lower() for word in positive_indicators) else
                    -1 if any(word in new_statement.lower() for word in negative_indicators) else 0
                )
                prev_sentiment = (
                    1 if any(word in prev_stmt.content.lower() for word in positive_indicators) else
                    -1 if any(word in prev_stmt.content.lower() for word in negative_indicators) else 0
                )

                if new_sentiment != 0 and prev_sentiment != 0 and new_sentiment != prev_sentiment:
                    return (prev_stmt, "sentiment_contradiction")

        return None

    @staticmethod
    def record_statement(
        game_state,
        character_name: str,
        player_message: str
    ) -> Optional[str]:
        """
        Record a player statement and check for contradictions

        Args:
            game_state: Current game state
            character_name: Which character the player is talking to
            player_message: What the player said

        Returns:
            Contradiction message if detected, None otherwise
        """
        # Get or create statement history
        if not hasattr(game_state.player, 'statement_history'):
            game_state.player.statement_history = []

        # Create new statement
        topic = ContradictionTracker.detect_topic(player_message)
        keywords = ContradictionTracker.extract_keywords(player_message)

        new_statement = PlayerStatement(
            timestamp=datetime.now().isoformat(),
            character_told=character_name,
            content=player_message,
            topic=topic or 'general',
            keywords=keywords
        )

        # Check for contradictions
        contradiction = ContradictionTracker.check_contradiction(
            player_message,
            game_state.player.statement_history,
            same_character_only=False
        )

        # Record the statement
        game_state.player.statement_history.append(new_statement)

        # Limit history size
        if len(game_state.player.statement_history) > 100:
            game_state.player.statement_history = game_state.player.statement_history[-100:]

        # Generate contradiction message if found
        if contradiction:
            prev_stmt, contradiction_type = contradiction

            # Check if the character being told should know about the contradiction
            if prev_stmt.character_told == character_name:
                # Same character - they definitely remember
                return f"CONTRADICTION DETECTED: You previously told {character_name}: \"{prev_stmt.content}\" (on {prev_stmt.timestamp[:10]}). Your current statement seems to contradict this."
            else:
                # Different character - they might not know, but we still flag it for memory
                return f"CONTRADICTION NOTED: You told {prev_stmt.character_told}: \"{prev_stmt.content}\" (on {prev_stmt.timestamp[:10]}), but now you're saying something different to {character_name}."

        return None

    @staticmethod
    def get_statements_to_character(game_state, character_name: str) -> List[PlayerStatement]:
        """
        Get all statements the player made to a specific character

        Args:
            game_state: Current game state
            character_name: Character to filter by

        Returns:
            List of statements told to that character
        """
        if not hasattr(game_state.player, 'statement_history'):
            return []

        return [stmt for stmt in game_state.player.statement_history
                if stmt.character_told == character_name]

    @staticmethod
    def format_contradiction_for_llm(
        contradiction_msg: str,
        character_rapport: int
    ) -> str:
        """
        Format contradiction detection for LLM context

        Args:
            contradiction_msg: The contradiction message
            character_rapport: Current rapport level

        Returns:
            Formatted string for LLM
        """
        if not contradiction_msg:
            return ""

        context = f"\n\n⚠️ PLAYER CONTRADICTION DETECTED:\n{contradiction_msg}\n\n"

        # Add guidance based on rapport
        if character_rapport >= 15:
            context += "RESPONSE GUIDANCE: You trust them, but you're confused. Gently ask for clarification. Don't accuse, but show you remember.\n"
        elif character_rapport >= 8:
            context += "RESPONSE GUIDANCE: You notice the inconsistency. Point it out politely but directly. You expect honesty.\n"
        else:
            context += "RESPONSE GUIDANCE: You catch the contradiction and are skeptical. Call them out on it. This affects your trust.\n"

        return context

    @staticmethod
    def get_recent_statements_summary(game_state, character_name: str, count: int = 5) -> str:
        """
        Get a summary of recent statements told to a character

        Args:
            game_state: Current game state
            character_name: Character to get statements for
            count: Number of recent statements to include

        Returns:
            Formatted summary string
        """
        statements = ContradictionTracker.get_statements_to_character(game_state, character_name)

        if not statements:
            return "No previous claims or statements recorded."

        recent = statements[-count:]

        summary = f"PLAYER'S PREVIOUS STATEMENTS TO YOU:\n"
        for i, stmt in enumerate(recent, 1):
            summary += f"{i}. \"{stmt.content}\" (Topic: {stmt.topic})\n"

        return summary
