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

    # Suspicion tracking
    player_suspicion: int = 0  # 0-100, how much they suspect the player is manipulating people
    character_suspicions: Dict[str, int] = field(default_factory=dict)  # {character_name: suspicion_level 0-100}

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
            'character_interactions': self.character_interactions,
            'player_suspicion': self.player_suspicion,
            'character_suspicions': self.character_suspicions
        }


@dataclass
class PostHypnoticSuggestion:
    """Represents a planted post-hypnotic suggestion"""
    target_name: str
    trigger: str
    response: str
    success_rate: int  # Base success percentage
    reinforcements: int = 0  # Number of times reinforced
    phs_type: str = "behavioral_prompt"  # behavioral_prompt, emotional_nudge, compliance_trigger, defensive
    defensive_target: Optional[str] = None  # For defensive type: who to defend player to
    suspicion_reduction: int = 0  # For defensive type: how much suspicion to reduce

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
            'reinforcements': self.reinforcements,
            'phs_type': self.phs_type,
            'defensive_target': self.defensive_target,
            'suspicion_reduction': self.suspicion_reduction
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

    # Grocery Store Staff
    'Emma': Character(
        name='Emma',
        age=22,
        occupation='Grocery Store Cashier',
        clothing='Store uniform, name tag, ponytail',
        clothing_meaning='Young, approachable, friendly service worker',
        personality='Bubbly, talkative, easily trusts people, naive',
        resistance=32,
        gender='female'
    ),
    'Michael': Character(
        name='Michael',
        age=45,
        occupation='Grocery Store Manager',
        clothing='Button-down shirt, slacks, manager badge',
        clothing_meaning='Professional authority, takes job seriously',
        personality='Stressed, overworked, values efficiency, secretly lonely',
        resistance=58,
        gender='male'
    ),
    'Sofia': Character(
        name='Sofia',
        age=28,
        occupation='Produce Section Worker',
        clothing='Apron, fitness watch, athletic build',
        clothing_meaning='Health-conscious, takes pride in fresh food',
        personality='Health nut, judgmental about food choices, helpful',
        resistance=48,
        gender='female'
    ),

    # Neighbors
    'Jessica': Character(
        name='Jessica',
        age=32,
        occupation='Stay-at-Home Mom',
        clothing='Yoga pants, oversized sweater, messy bun',
        clothing_meaning='Comfortable but frazzled, always rushing',
        personality='Gossipy, knows everyone\'s business, needs validation',
        resistance=42,
        gender='female'
    ),
    'David': Character(
        name='David',
        age=41,
        occupation='Divorced Dad / Accountant',
        clothing='Business casual, tired eyes, wedding ring tan line',
        clothing_meaning='Still adjusting to single life',
        personality='Lonely, desperate for connection, vulnerable',
        resistance=28,
        gender='male'
    ),
    'Amber': Character(
        name='Amber',
        age=25,
        occupation='Bartender',
        clothing='Trendy club wear, heavy makeup, confident posture',
        clothing_meaning='Wants attention, party lifestyle',
        personality='Wild, impulsive, hides insecurity with boldness',
        resistance=55,
        gender='female'
    ),
    'Robert': Character(
        name='Robert',
        age=58,
        occupation='Retired Professor',
        clothing='Cardigan, slacks, reading glasses on chain',
        clothing_meaning='Academic, traditional, wise elder',
        personality='Intellectual, patient, sees through manipulation, curious',
        resistance=72,
        gender='male'
    ),
    'Chloe': Character(
        name='Chloe',
        age=19,
        occupation='College Student',
        clothing='Hoodie, jeans, backpack, casual sneakers',
        clothing_meaning='Student life, still figuring herself out',
        personality='Naive, eager to please authority, wants to be liked',
        resistance=30,
        gender='female'
    ),

    # Gym/Fitness
    'Tyler': Character(
        name='Tyler',
        age=29,
        occupation='Personal Trainer',
        clothing='Tight athletic wear, protein shaker, muscular',
        clothing_meaning='Body is his brand, confidence through fitness',
        personality='Motivating, competitive, shallow but well-meaning',
        resistance=62,
        gender='male'
    ),
    'Ashley': Character(
        name='Ashley',
        age=34,
        occupation='Yoga Instructor',
        clothing='Yoga pants, sports bra, zen jewelry',
        clothing_meaning='Spiritual, flexible in body and mind',
        personality='Calm, open-minded, suggestible to "energy" talk',
        resistance=38,
        gender='female'
    ),
    'Jake': Character(
        name='Jake',
        age=26,
        occupation='Bodybuilder / Supplement Sales',
        clothing='Tank top, gym shorts, excessive cologne',
        clothing_meaning='Ego wrapped in muscles',
        personality='Arrogant, insecure underneath, needs constant validation',
        resistance=68,
        gender='male'
    ),
    'Mia': Character(
        name='Mia',
        age=23,
        occupation='Fitness Influencer',
        clothing='Color-coordinated workout sets, always camera-ready',
        clothing_meaning='Life is content, appearance is everything',
        personality='Energetic, superficial, craves attention and followers',
        resistance=52,
        gender='female'
    ),

    # Café/Social
    'Olivia': Character(
        name='Olivia',
        age=21,
        occupation='Barista / Art Student',
        clothing='Vintage band tee, apron, dyed hair, piercings',
        clothing_meaning='Artistic, alternative, nonconformist',
        personality='Creative, dreamy, easily influenced by "deep" conversations',
        resistance=35,
        gender='female'
    ),
    'Ethan': Character(
        name='Ethan',
        age=37,
        occupation='Freelance Writer',
        clothing='Rumpled shirt, laptop bag, coffee stains',
        clothing_meaning='Struggling artist, disheveled intellectual',
        personality='Cynical, lonely, overthinks everything, seeking meaning',
        resistance=64,
        gender='male'
    ),
    'Isabella': Character(
        name='Isabella',
        age=30,
        occupation='Librarian',
        clothing='Glasses, cardigans, book-themed jewelry',
        clothing_meaning='Quiet intelligence, loves order and stories',
        personality='Shy, bookish, opens up about literature, trusting once comfortable',
        resistance=40,
        gender='female'
    ),
    'Noah': Character(
        name='Noah',
        age=27,
        occupation='Musician / Barista',
        clothing='Band merch, skinny jeans, guitar case nearby',
        clothing_meaning='Artist trying to make it, passionate',
        personality='Passionate, emotional, dramatic, seeks validation for art',
        resistance=44,
        gender='male'
    ),

    # Mall/Shopping
    'Sophia': Character(
        name='Sophia',
        age=35,
        occupation='Fashion Boutique Owner',
        clothing='Designer outfit, immaculate style, jewelry',
        clothing_meaning='Image is business, perfection required',
        personality='Stylish, judgmental, values appearances, surprisingly insecure',
        resistance=70,
        gender='female'
    ),
    'Liam': Character(
        name='Liam',
        age=24,
        occupation='Electronics Store Clerk',
        clothing='Store polo, jeans, gaming merch accessories',
        clothing_meaning='Tech nerd, casual geek culture',
        personality='Nerdy, enthusiastic about tech, socially awkward',
        resistance=36,
        gender='male'
    ),
    'Ava': Character(
        name='Ava',
        age=29,
        occupation='Beauty Consultant',
        clothing='Perfect makeup, fashionable, name brand everything',
        clothing_meaning='Beauty is power and confidence',
        personality='Confident, flirty, uses charm to sell, actually quite sharp',
        resistance=56,
        gender='female'
    ),

    # Professional/Work
    'Daniel': Character(
        name='Daniel',
        age=42,
        occupation='Corporate Lawyer',
        clothing='Expensive suit, luxury watch, briefcase',
        clothing_meaning='Success, power, intimidation',
        personality='Ambitious, analytical, hard to fool, respects power',
        resistance=78,
        gender='male'
    ),
    'Emma_R': Character(
        name='Emma_R',
        age=38,
        occupation='Family Doctor',
        clothing='Professional but warm, stethoscope, kind eyes',
        clothing_meaning='Approachable authority, caregiver',
        personality='Caring, empathetic, tired from work, needs someone to lean on',
        resistance=46,
        gender='female'
    ),
    'William': Character(
        name='William',
        age=33,
        occupation='High School Teacher',
        clothing='Casual professional, somewhat worn out',
        clothing_meaning='Dedicated but underpaid, stressed',
        personality='Patient, idealistic, exhausted, yearns for appreciation',
        resistance=40,
        gender='male'
    ),
    'Madison': Character(
        name='Madison',
        age=31,
        occupation='Real Estate Agent',
        clothing='Sharp blazer, heels, confident smile',
        clothing_meaning='Sales mode always on, persuasive',
        personality='Persuasive, charming, competitive, hides vulnerability',
        resistance=60,
        gender='female'
    ),

    # Service Workers
    'Lucas': Character(
        name='Lucas',
        age=26,
        occupation='Delivery Driver',
        clothing='Company shirt, shorts, always moving',
        clothing_meaning='Working class, hustling',
        personality='Friendly, hustler mentality, dreams bigger, easy-going',
        resistance=34,
        gender='male'
    ),
    'Grace': Character(
        name='Grace',
        age=28,
        occupation='Restaurant Waitress',
        clothing='Uniform, apron, comfortable shoes, tired smile',
        clothing_meaning='Service with a smile, working hard',
        personality='Bubbly but tired, people-pleaser, needs encouragement',
        resistance=38,
        gender='female'
    ),
    'Henry': Character(
        name='Henry',
        age=50,
        occupation='Handyman',
        clothing='Work clothes, tool belt, practical boots',
        clothing_meaning='Blue collar pride, gets things done',
        personality='Practical, no-nonsense, secretly appreciates being needed',
        resistance=54,
        gender='male'
    ),

    # Random Encounters
    'Zoe': Character(
        name='Zoe',
        age=24,
        occupation='Street Artist',
        clothing='Paint-splattered clothes, creative chaos',
        clothing_meaning='Free spirit, rejects conventions',
        personality='Free-spirited, spontaneous, open to new experiences',
        resistance=42,
        gender='female'
    ),
    'Ryan': Character(
        name='Ryan',
        age=36,
        occupation='Police Officer',
        clothing='Uniform or casual authority clothes',
        clothing_meaning='Law and order, protective',
        personality='Protective, suspicious of manipulation, values honesty',
        resistance=74,
        gender='male'
    ),
    'Natalie': Character(
        name='Natalie',
        age=40,
        occupation='Social Worker',
        clothing='Professional casual, warm demeanor',
        clothing_meaning='Approachable helper, empathetic',
        personality='Empathetic, sees through lies, wants to help people',
        resistance=66,
        gender='female'
    ),
    'Alex': Character(
        name='Alex',
        age=32,
        occupation='Photographer',
        clothing='Artistic casual, camera always nearby',
        clothing_meaning='Observer, captures moments',
        personality='Observant, quiet, notices details others miss, creative',
        resistance=50,
        gender='male'
    ),
}


def get_character(name: str) -> Optional[Character]:
    """Get a character by name"""
    return CHARACTERS.get(name)


def get_all_characters() -> Dict[str, Character]:
    """Get all characters"""
    return CHARACTERS
