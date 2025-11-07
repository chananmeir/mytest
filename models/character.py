"""
Character models and definitions for Family Dynamics RPG
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class Character:
    """Represents a character in the game"""
    name: str
    age: int
    occupation: str
    clothing: str
    clothing_meaning: str
    personality: str
    resistance: int  # 0-100, how resistant to hypnotic suggestions
    rapport: int = 0  # 0-20, your influence level with them
    emotional_state: str = "neutral"  # neutral, relaxed, tense, defensive, open, etc.
    emotional_state_reason: str = ""  # Why they're in this emotional state
    gender: str = "male"  # male/female - used for template fallback images
    active_phs: List['PostHypnoticSuggestion'] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)  # With player
    memories: List = field(default_factory=list)  # List of Memory objects
    clothing_history: List[Dict[str, str]] = field(default_factory=list)  # Track clothing changes
    outfit: Dict[str, str] = field(default_factory=dict)  # Visual outfit: {slot: item_id}

    # Character-to-character relationships
    relationships: Dict[str, int] = field(default_factory=dict)  # {character_name: relationship_score 0-20}
    character_interactions: List[Dict[str, str]] = field(default_factory=list)  # History with other characters

    def __post_init__(self):
        """Initialize any computed properties"""
        self.max_phs = self._calculate_max_phs()

        # Record initial clothing if history is empty
        if not self.clothing_history:
            self.clothing_history.append({
                'timestamp': 'initial',
                'clothing': self.clothing,
                'meaning': self.clothing_meaning,
                'occasion': 'default'
            })

        # Initialize outfit if empty
        if not self.outfit:
            from data.clothing_items import DEFAULT_OUTFITS
            self.outfit = DEFAULT_OUTFITS.get(self.name, {'expression': 'neutral'}).copy()

        # Initialize default relationships if empty
        if not self.relationships:
            self.relationships = self._init_default_relationships()

    def _init_default_relationships(self) -> Dict[str, int]:
        """Initialize default family relationships"""
        # These are just defaults - can be modified through gameplay
        defaults = {
            'Ruth': {'Tom': 12, 'Melanie': 7, 'Vanessa': 6, 'Derek': 8},
            'Melanie': {'Ruth': 7, 'Tom': 10, 'Derek': 5, 'Karen': 11},
            'Tom': {'Ruth': 12, 'Melanie': 10, 'Derek': 8, 'Dawn': 9},
            'Dawn': {'Tom': 9, 'Karen': 14, 'Vanessa': 8, 'Ruth': 11},
            'Vanessa': {'Ruth': 6, 'Dawn': 8, 'Melanie': 5, 'Derek': 7},
            'Derek': {'Ruth': 8, 'Tom': 8, 'Melanie': 5, 'Vanessa': 7},
            'Karen': {'Dawn': 14, 'Melanie': 11, 'Tom': 6, 'Vanessa': 4}
        }
        return defaults.get(self.name, {})

    def _calculate_max_phs(self) -> int:
        """Calculate maximum active PHS based on resistance"""
        if 60 <= self.resistance <= 75:
            return 1
        elif 40 <= self.resistance <= 55:
            return 2
        elif 20 <= self.resistance <= 35:
            return 3
        else:
            return 1

    def add_rapport(self, amount: int) -> None:
        """Increase rapport, capped at 20"""
        self.rapport = min(20, self.rapport + amount)

    def reduce_rapport(self, amount: int) -> None:
        """Decrease rapport, minimum 0"""
        self.rapport = max(0, self.rapport - amount)

    def set_emotional_state(self, state: str, reason: str = "") -> None:
        """Change the character's emotional state"""
        self.emotional_state = state
        if reason:
            self.emotional_state_reason = reason

    def can_accept_phs(self) -> bool:
        """Check if character can accept more PHS"""
        return len(self.active_phs) < self.max_phs

    def add_phs(self, phs: 'PostHypnoticSuggestion') -> bool:
        """Add a PHS if there's capacity"""
        if self.can_accept_phs():
            self.active_phs.append(phs)
            return True
        return False

    def update_clothing(self, new_clothing: str, new_meaning: str = "", occasion: str = "") -> None:
        """
        Update character's clothing and record the change

        Args:
            new_clothing: Description of the new clothing
            new_meaning: What the clothing signifies (optional)
            occasion: Why they changed (e.g., "dinner party", "casual day")
        """
        from datetime import datetime

        # If no new meaning provided, keep existing or note it's unknown
        if not new_meaning:
            new_meaning = f"Changed from: {self.clothing_meaning}"

        # Record the change in history
        self.clothing_history.append({
            'timestamp': datetime.now().isoformat(),
            'clothing': new_clothing,
            'meaning': new_meaning,
            'occasion': occasion or 'unspecified'
        })

        # Update current clothing
        old_clothing = self.clothing
        self.clothing = new_clothing
        self.clothing_meaning = new_meaning

        return old_clothing

    def get_clothing_history(self) -> List[Dict[str, str]]:
        """Get the history of clothing changes"""
        return self.clothing_history

    def get_current_clothing_description(self) -> str:
        """Get a formatted description of current clothing"""
        return f"{self.clothing} - {self.clothing_meaning}"

    def update_outfit_item(self, slot: str, item_id: str) -> None:
        """Update a single outfit slot"""
        self.outfit[slot] = item_id

    def get_outfit_item(self, slot: str) -> Optional[str]:
        """Get the item ID for a specific slot"""
        return self.outfit.get(slot)

    def to_dict(self) -> dict:
        """Convert to dictionary for saving"""
        return {
            'name': self.name,
            'age': self.age,
            'occupation': self.occupation,
            'clothing': self.clothing,
            'clothing_meaning': self.clothing_meaning,
            'personality': self.personality,
            'resistance': self.resistance,
            'rapport': self.rapport,
            'emotional_state': self.emotional_state,
            'emotional_state_reason': self.emotional_state_reason,
            'gender': self.gender,
            'active_phs': [phs.to_dict() for phs in self.active_phs],
            'conversation_history': self.conversation_history,
            'memories': [mem.to_dict() if hasattr(mem, 'to_dict') else mem for mem in self.memories],
            'clothing_history': self.clothing_history,
            'outfit': self.outfit,
            'relationships': self.relationships,
            'character_interactions': self.character_interactions
        }


@dataclass
class PostHypnoticSuggestion:
    """Represents a planted post-hypnotic suggestion"""
    target_name: str
    trigger: str
    response: str
    success_rate: int  # Base success percentage
    reinforcements: int = 0  # Number of times reinforced

    def calculate_activation_chance(self) -> int:
        """Calculate current activation chance"""
        return min(100, self.success_rate + (self.reinforcements * 5))

    def reinforce(self) -> None:
        """Reinforce the suggestion, increasing success rate"""
        self.reinforcements += 1

    def to_dict(self) -> dict:
        """Convert to dictionary for saving"""
        return {
            'target_name': self.target_name,
            'trigger': self.trigger,
            'response': self.response,
            'success_rate': self.success_rate,
            'reinforcements': self.reinforcements
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PostHypnoticSuggestion':
        """Create from dictionary"""
        return cls(**data)


# Character Database
CHARACTERS = {
    'Ruth': Character(
        name='Ruth',
        age=40,
        occupation='Office Manager',
        clothing='Casual but coordinated. Soft colors.',
        clothing_meaning='Tries to look "put together." Likes appearing stable.',
        personality='Guilt-driven, loyal, tries to please everyone',
        resistance=55,
        gender='female'
    ),
    'Melanie': Character(
        name='Melanie',
        age=35,
        occupation='Nurse Practitioner',
        clothing='Scrubs or athletic-wear, hair tied high, smartwatch',
        clothing_meaning='Efficiency, self-importance',
        personality='Proud, competent, dismissive of weakness',
        resistance=75,
        gender='female'
    ),
    'Tom': Character(
        name='Tom',
        age=42,
        occupation='IT Technician',
        clothing='Plain polo and jeans. Practical shoes.',
        clothing_meaning='Tries not to stand out',
        personality='Conflict-avoidant, eager to please, insecure',
        resistance=30,
        gender='male'
    ),
    'Dawn': Character(
        name='Dawn',
        age=68,
        occupation='Retired Teacher',
        clothing='Floral prints, pearls, tidy cardigan',
        clothing_meaning='Tradition + control',
        personality='Matriarch, values harmony, passive-aggressive',
        resistance=45,
        gender='female'
    ),
    'Vanessa': Character(
        name='Vanessa',
        age=37,
        occupation='Marketing Executive',
        clothing='Trendy blazer, expensive shoes',
        clothing_meaning='Wants everyone to notice success',
        personality='Status-conscious, competitive, insecure beneath',
        resistance=50,
        gender='female'
    ),
    'Derek': Character(
        name='Derek',
        age=33,
        occupation='Personal Trainer',
        clothing='Fitted t-shirt, gym shorts, branded sneakers',
        clothing_meaning='Body pride = identity',
        personality='Ego-driven, physical confidence, intellectually insecure',
        resistance=65,
        gender='male'
    ),
    'Karen': Character(
        name='Karen',
        age=44,
        occupation='Elementary School Principal',
        clothing='Clean, structured, modest blouse & slacks',
        clothing_meaning='Rules. Order. Judgment.',
        personality='Rigid, judgmental, needs control, responds to authority',
        resistance=35,
        gender='female'
    ),
}


def get_character(name: str) -> Optional[Character]:
    """Get a character by name"""
    return CHARACTERS.get(name)


def get_all_characters() -> Dict[str, Character]:
    """Get all characters"""
    return CHARACTERS
