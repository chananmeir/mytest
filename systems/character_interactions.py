"""
Character interaction tracking system
Records and manages conversations/interactions between characters
"""
from datetime import datetime
from typing import Dict, List, Optional
from models.character import Character


def record_interaction(
    char1: Character,
    char2: Character,
    interaction_type: str,
    summary: str,
    location: str = None
) -> None:
    """
    Record an interaction between two characters

    Args:
        char1: First character
        char2: Second character
        interaction_type: Type of interaction ('conversation', 'argument', 'friendly', etc.)
        summary: Brief description of what happened
        location: Where it happened (optional)
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Record from char1's perspective
    char1.character_interactions.append({
        'with_character': char2.name,
        'type': interaction_type,
        'summary': summary,
        'location': location,
        'timestamp': timestamp
    })

    # Record from char2's perspective
    char2.character_interactions.append({
        'with_character': char1.name,
        'type': interaction_type,
        'summary': summary,
        'location': location,
        'timestamp': timestamp
    })

    # Update relationships based on interaction
    _update_relationship_from_interaction(char1, char2, interaction_type)


def _update_relationship_from_interaction(char1: Character, char2: Character, interaction_type: str) -> None:
    """Update relationship scores based on interaction type"""
    # Get current relationship scores (default to 5 if not set)
    current_score_1 = char1.relationships.get(char2.name, 5)
    current_score_2 = char2.relationships.get(char1.name, 5)

    # Adjust based on interaction type
    adjustments = {
        'friendly': 1,
        'conversation': 0,  # Neutral
        'argument': -2,
        'help': 2,
        'romantic': 3,
        'conflict': -3
    }

    adjustment = adjustments.get(interaction_type, 0)

    # Update both characters' relationships
    char1.relationships[char2.name] = max(0, min(20, current_score_1 + adjustment))
    char2.relationships[char1.name] = max(0, min(20, current_score_2 + adjustment))


def get_recent_interactions(character: Character, with_character: str = None, limit: int = 10) -> List[Dict]:
    """
    Get recent interactions for a character

    Args:
        character: The character whose interactions to retrieve
        with_character: Optional filter for specific other character
        limit: Maximum number of interactions to return

    Returns:
        List of interaction dictionaries
    """
    interactions = character.character_interactions

    # Filter by specific character if requested
    if with_character:
        interactions = [i for i in interactions if i['with_character'] == with_character]

    # Return most recent first
    return list(reversed(interactions[-limit:]))


def get_relationship_summary(char1: Character, char2: Character) -> Dict:
    """
    Get a summary of the relationship between two characters

    Returns:
        Dictionary with relationship info and recent interactions
    """
    relationship_score = char1.relationships.get(char2.name, 5)

    # Get recent interactions between these two
    interactions = [
        i for i in char1.character_interactions
        if i['with_character'] == char2.name
    ][-5:]  # Last 5 interactions

    return {
        'score': relationship_score,
        'description': _get_relationship_description(relationship_score),
        'recent_interactions': interactions,
        'interaction_count': len([i for i in char1.character_interactions if i['with_character'] == char2.name])
    }


def _get_relationship_description(score: int) -> str:
    """Convert relationship score to description"""
    if score >= 15:
        return 'Very Close'
    elif score >= 10:
        return 'Good Friends'
    elif score >= 5:
        return 'Friendly'
    elif score >= 0:
        return 'Neutral'
    else:
        return 'Hostile'


def simulate_background_interaction(char1: Character, char2: Character, location: str) -> None:
    """
    Simulate a background interaction between two characters at the same location
    Used for ambient world-building
    """
    import random

    # Determine interaction type based on current relationship
    relationship_score = char1.relationships.get(char2.name, 5)

    if relationship_score >= 10:
        # Good friends - positive interactions
        interaction_types = ['friendly', 'conversation', 'help']
        summaries = [
            f"Had a pleasant conversation about daily life",
            f"Shared a laugh together",
            f"Discussed plans for the weekend",
            f"Helped each other with small tasks"
        ]
    elif relationship_score >= 5:
        # Friendly - mostly neutral
        interaction_types = ['conversation', 'friendly']
        summaries = [
            f"Chatted briefly",
            f"Made small talk",
            f"Exchanged pleasantries"
        ]
    else:
        # Neutral or negative - more varied
        interaction_types = ['conversation', 'argument']
        summaries = [
            f"Had a tense conversation",
            f"Briefly acknowledged each other",
            f"Discussed something with some disagreement"
        ]

    interaction_type = random.choice(interaction_types)
    summary = random.choice(summaries)

    record_interaction(char1, char2, interaction_type, summary, location)
