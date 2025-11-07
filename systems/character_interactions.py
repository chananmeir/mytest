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


def generate_character_conversation_llm(char1: Character, char2: Character, location: str, llm_handler) -> Optional[Dict]:
    """
    Use LLM to generate a conversation between two characters

    Args:
        char1: First character
        char2: Second character
        location: Where they are
        llm_handler: LLM handler instance

    Returns:
        Dictionary with conversation details or None if failed
    """
    import config
    import requests

    relationship_score = char1.relationships.get(char2.name, 5)

    # Build prompt for LLM to generate a brief conversation snippet
    prompt = f"""You are narrating a brief background conversation between two characters.

CHARACTER 1: {char1.name}
- Age: {char1.age}
- Occupation: {char1.occupation}
- Personality: {char1.personality}
- Current emotional state: {char1.emotional_state}

CHARACTER 2: {char2.name}
- Age: {char2.age}
- Occupation: {char2.occupation}
- Personality: {char2.personality}
- Current emotional state: {char2.emotional_state}

RELATIONSHIP: {char1.name} and {char2.name} have a relationship score of {relationship_score}/20
LOCATION: {location}

Generate a VERY BRIEF (1-2 sentences) summary of what they're talking about. Make it natural and realistic for their personalities and relationship. Also classify the interaction type.

Respond in this exact format:
TYPE: [friendly/conversation/argument/help]
SUMMARY: [1-2 sentence summary of their conversation]

Example:
TYPE: friendly
SUMMARY: {char1.name} and {char2.name} discussed their plans for the weekend, with {char1.name} suggesting they catch up over coffee."""

    api_key = config.DEFAULT_API_KEY
    if not api_key:
        return None

    try:
        response = requests.post(
            config.OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": config.DEFAULT_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 100
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']

            # Parse response
            lines = content.strip().split('\n')
            interaction_type = 'conversation'
            summary = ''

            for line in lines:
                if line.startswith('TYPE:'):
                    interaction_type = line.replace('TYPE:', '').strip().lower()
                elif line.startswith('SUMMARY:'):
                    summary = line.replace('SUMMARY:', '').strip()

            if summary:
                return {
                    'type': interaction_type,
                    'summary': summary
                }

    except Exception as e:
        print(f"Error generating character conversation: {e}")

    return None
