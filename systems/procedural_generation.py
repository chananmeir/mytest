"""
Procedural Generation System for Family Dynamics RPG

Adds replayability through:
1. Randomized Character Traits - personality and resistance variations
2. Variable Family Dynamics - randomized starting relationships
3. Procedural Events - expanded random event library
"""
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from models.character import Character, CHARACTERS
import copy


@dataclass
class CharacterVariation:
    """Defines how a character can vary across playthroughs"""
    resistance_min: int
    resistance_max: int
    personality_variants: List[str]
    rapport_modifiers: Dict[str, Tuple[int, int]]  # {char_name: (min, max)}

    def to_dict(self) -> dict:
        return {
            'resistance_min': self.resistance_min,
            'resistance_max': self.resistance_max,
            'personality_variants': self.personality_variants,
            'rapport_modifiers': self.rapport_modifiers
        }


class ProceduralCharacterGenerator:
    """Generates character variations for each playthrough"""

    # Define variation ranges for each character
    CHARACTER_VARIATIONS = {
        'Ruth': CharacterVariation(
            resistance_min=50,
            resistance_max=65,
            personality_variants=[
                'Guilt-driven, loyal, tries to please everyone',  # Original
                'Guilt-driven, loyal, but sometimes stands up for herself',
                'Anxious, loyal, desperately needs approval',
                'Guilt-driven, loyal, quietly resentful underneath'
            ],
            rapport_modifiers={'Tom': (10, 14), 'Melanie': (5, 9), 'Dawn': (9, 13)}
        ),
        'Melanie': CharacterVariation(
            resistance_min=70,
            resistance_max=82,
            personality_variants=[
                'Proud, competent, dismissive of weakness',  # Original
                'Proud, competent, but secretly insecure',
                'Proud, competent, extremely competitive',
                'Proud, competent, burned out but hiding it'
            ],
            rapport_modifiers={'Ruth': (5, 9), 'Derek': (3, 7), 'Karen': (9, 13)}
        ),
        'Tom': CharacterVariation(
            resistance_min=25,
            resistance_max=38,
            personality_variants=[
                'Conflict-avoidant, eager to please, insecure',  # Original
                'Conflict-avoidant, eager to please, passive-aggressive underneath',
                'Conflict-avoidant, people-pleaser, exhausted from it',
                'Conflict-avoidant, eager to please, secretly wishes to be assertive'
            ],
            rapport_modifiers={'Ruth': (10, 14), 'Derek': (6, 10), 'Dawn': (7, 11)}
        ),
        'Dawn': CharacterVariation(
            resistance_min=40,
            resistance_max=52,
            personality_variants=[
                'Matriarch, values harmony, passive-aggressive',  # Original
                'Matriarch, values harmony, manipulative when needed',
                'Matriarch, values tradition, fears losing control',
                'Matriarch, values harmony, deeply lonely underneath'
            ],
            rapport_modifiers={'Karen': (12, 16), 'Tom': (7, 11), 'Ruth': (9, 13)}
        ),
        'Vanessa': CharacterVariation(
            resistance_min=45,
            resistance_max=58,
            personality_variants=[
                'Status-conscious, competitive, insecure beneath',  # Original
                'Status-conscious, competitive, desperately needs validation',
                'Status-conscious, workaholic, success at any cost',
                'Status-conscious, competitive, envious of others\' ease'
            ],
            rapport_modifiers={'Melanie': (3, 7), 'Dawn': (6, 10), 'Derek': (5, 9)}
        ),
        'Derek': CharacterVariation(
            resistance_min=60,
            resistance_max=72,
            personality_variants=[
                'Ego-driven, physical confidence, intellectually insecure',  # Original
                'Ego-driven, physical confidence, overcompensating for something',
                'Ego-driven, gym obsessed, body dysmorphia underneath',
                'Ego-driven, physical confidence, feels threatened by intellect'
            ],
            rapport_modifiers={'Tom': (6, 10), 'Melanie': (3, 7), 'Vanessa': (5, 9)}
        ),
        'Karen': CharacterVariation(
            resistance_min=30,
            resistance_max=42,
            personality_variants=[
                'Rigid, judgmental, needs control, responds to authority',  # Original
                'Rigid, judgmental, extremely anxious underneath',
                'Rigid, judgmental, has obsessive-compulsive tendencies',
                'Rigid, judgmental, desperately lonely and controlling to cope'
            ],
            rapport_modifiers={'Dawn': (12, 16), 'Melanie': (9, 13), 'Tom': (4, 8)}
        )
    }

    @staticmethod
    def generate_character_variation(base_character: Character, seed: Optional[int] = None) -> Character:
        """
        Generate a procedural variation of a character

        Args:
            base_character: The base character template
            seed: Optional random seed for reproducibility

        Returns:
            New Character with randomized traits
        """
        if seed is not None:
            random.seed(seed)

        variation = ProceduralCharacterGenerator.CHARACTER_VARIATIONS.get(base_character.name)

        if not variation:
            # Character has no variations defined, return copy of base
            return copy.deepcopy(base_character)

        # Randomize resistance
        new_resistance = random.randint(variation.resistance_min, variation.resistance_max)

        # Pick random personality variant
        new_personality = random.choice(variation.personality_variants)

        # Create new character with variations
        varied_char = Character(
            name=base_character.name,
            age=base_character.age,
            occupation=base_character.occupation,
            clothing=base_character.clothing,
            clothing_meaning=base_character.clothing_meaning,
            personality=new_personality,
            resistance=new_resistance,
            gender=base_character.gender
        )

        return varied_char

    @staticmethod
    def generate_all_characters(seed: Optional[int] = None) -> Dict[str, Character]:
        """
        Generate all characters with variations

        Args:
            seed: Optional random seed for reproducibility

        Returns:
            Dict of character_name: varied_character
        """
        if seed is not None:
            random.seed(seed)

        varied_characters = {}

        for name, base_char in CHARACTERS.items():
            varied_characters[name] = ProceduralCharacterGenerator.generate_character_variation(
                base_char,
                seed=None  # Let random state flow naturally
            )

        return varied_characters


class ProceduralRelationshipGenerator:
    """Generates variable family dynamics for each playthrough"""

    # Define relationship range for each pair
    # Format: (character1, character2): (min_score, max_score)
    RELATIONSHIP_RANGES = {
        ('Ruth', 'Tom'): (10, 15),  # Married couple - generally close
        ('Ruth', 'Melanie'): (4, 10),  # Sisters - can vary widely
        ('Ruth', 'Vanessa'): (3, 9),  # Sisters-in-law
        ('Ruth', 'Dawn'): (8, 14),  # Mother-in-law relationship
        ('Ruth', 'Derek'): (5, 11),  # Brother-in-law
        ('Ruth', 'Karen'): (4, 8),  # Acquaintance through family

        ('Melanie', 'Tom'): (7, 13),  # Brother-in-law, generally okay
        ('Melanie', 'Derek'): (2, 8),  # Can be competitive or friendly
        ('Melanie', 'Karen'): (8, 14),  # Both professionals, respect
        ('Melanie', 'Dawn'): (5, 11),  # Mother relationship
        ('Melanie', 'Vanessa'): (2, 8),  # Sisters - competitive

        ('Tom', 'Derek'): (5, 11),  # Bros but different
        ('Tom', 'Dawn'): (6, 12),  # Mother-in-law
        ('Tom', 'Vanessa'): (4, 8),  # Sister-in-law
        ('Tom', 'Karen'): (3, 7),  # Not much in common

        ('Dawn', 'Karen'): (12, 17),  # Very close friends
        ('Dawn', 'Vanessa'): (6, 12),  # Granddaughter vibes
        ('Dawn', 'Derek'): (5, 9),  # Grandson vibes

        ('Vanessa', 'Derek'): (4, 10),  # Cousins or distant family
        ('Vanessa', 'Karen'): (2, 6),  # Clashing personalities

        ('Derek', 'Karen'): (3, 7),  # Not much overlap
    }

    @staticmethod
    def generate_relationship_matrix(seed: Optional[int] = None) -> Dict[str, Dict[str, int]]:
        """
        Generate randomized relationship matrix for all characters

        Args:
            seed: Optional random seed for reproducibility

        Returns:
            Nested dict: {character: {other_character: relationship_score}}
        """
        if seed is not None:
            random.seed(seed)

        # Initialize matrix
        matrix = {name: {} for name in CHARACTERS.keys()}

        # Generate relationships
        for (char1, char2), (min_score, max_score) in ProceduralRelationshipGenerator.RELATIONSHIP_RANGES.items():
            score = random.randint(min_score, max_score)

            # Set bidirectional relationship
            matrix[char1][char2] = score
            matrix[char2][char1] = score

        return matrix

    @staticmethod
    def apply_relationships_to_characters(characters: Dict[str, Character], relationship_matrix: Dict[str, Dict[str, int]]):
        """
        Apply relationship matrix to character objects

        Args:
            characters: Dict of characters to modify
            relationship_matrix: Relationship scores to apply
        """
        for char_name, char in characters.items():
            if char_name in relationship_matrix:
                char.relationships = relationship_matrix[char_name].copy()


class ProceduralEventLibrary:
    """Expanded library of procedural random events"""

    @staticmethod
    def generate_medical_emergency_event(character_name: str) -> 'DynamicEvent':
        """Generate a medical emergency event"""
        from systems.dynamic_events import DynamicEvent, EventOption

        emergencies = [
            {
                'title': f"{character_name}'s Medical Emergency",
                'description': f"{character_name} suddenly clutches their chest and collapses! They need help NOW!",
                'severity': 'critical',
                'icon': '🚑'
            },
            {
                'title': f"Allergic Reaction",
                'description': f"{character_name} is having a severe allergic reaction to something they ate!",
                'severity': 'high',
                'icon': '⚠️'
            },
            {
                'title': f"Accident in the Home",
                'description': f"{character_name} fell and may have broken something. They're in pain!",
                'severity': 'high',
                'icon': '🤕'
            },
            {
                'title': f"Sudden Illness",
                'description': f"{character_name} is burning up with fever and seems disoriented.",
                'severity': 'medium',
                'icon': '🤒'
            }
        ]

        emergency = random.choice(emergencies)

        event = DynamicEvent(
            event_id=f"medical_emergency_{character_name.lower()}_{random.randint(1000,9999)}",
            event_type="crisis",
            title=emergency['title'],
            description=emergency['description'],
            icon=emergency['icon'],
            primary_character=character_name,
            observers=[c for c in CHARACTERS.keys() if c != character_name][:3],
            duration_minutes=20,
            urgency_level="critical",
            pressure=True,
            weight=5,
            one_time=False,
            options=[
                EventOption(
                    option_id="help_immediately",
                    text="Drop everything and help them immediately",
                    rapport_changes={character_name: 5, **{obs: 2 for obs in [c for c in CHARACTERS.keys() if c != character_name][:2]}},
                    emotional_state_changes={character_name: "grateful"},
                    sp_gain=3,
                    social_effect="Everyone sees you stepped up in crisis",
                    observers=[c for c in CHARACTERS.keys() if c != character_name][:3],
                    success_text=f"You help {character_name}. They're shaken but okay. Everyone respects your quick action."
                ),
                EventOption(
                    option_id="call_ambulance",
                    text="Call 911 while others help",
                    rapport_changes={character_name: 2},
                    sp_gain=1,
                    social_effect="Practical response",
                    success_text="Emergency services arrive quickly. You did the right thing."
                ),
                EventOption(
                    option_id="use_crisis_for_phs",
                    text="Help them, but use their vulnerable state...",
                    requires_sp=4,
                    sp_cost=4,
                    allows_phs=True,
                    phs_target=character_name,
                    phs_success_bonus=25,
                    phs_detection_risk=60,
                    suspicion_changes={obs: 10 for obs in [c for c in CHARACTERS.keys() if c != character_name][:2]},
                    social_effect="Others might notice your opportunism",
                    observers=[c for c in CHARACTERS.keys() if c != character_name][:2],
                    success_text=f"In their vulnerable moment, {character_name} is very suggestible...",
                    failure_text="Someone notices you're being manipulative during a crisis!"
                ),
                EventOption(
                    option_id="freeze",
                    text="Freeze up - you don't know what to do!",
                    rapport_changes={character_name: -3, **{obs: -2 for obs in [c for c in CHARACTERS.keys() if c != character_name][:2]}},
                    emotional_state_changes={character_name: "disappointed"},
                    success_text="Others step in while you stand there helpless. They remember this."
                )
            ]
        )

        return event

    @staticmethod
    def generate_financial_crisis_event(character_name: str) -> 'DynamicEvent':
        """Generate a financial crisis event"""
        from systems.dynamic_events import DynamicEvent, EventOption

        crises = [
            {
                'title': f"{character_name}'s Job Loss",
                'description': f"{character_name} just got laid off. They're devastated and panicking about money.",
                'money_amount': 500
            },
            {
                'title': f"Unexpected Bill",
                'description': f"{character_name} received a huge unexpected bill - their car broke down.",
                'money_amount': 300
            },
            {
                'title': f"Rent Crisis",
                'description': f"{character_name} can't make rent this month. They're facing eviction.",
                'money_amount': 800
            },
            {
                'title': f"Medical Bills",
                'description': f"{character_name} has massive medical bills they can't pay.",
                'money_amount': 1000
            }
        ]

        crisis = random.choice(crises)

        event = DynamicEvent(
            event_id=f"financial_crisis_{character_name.lower()}_{random.randint(1000,9999)}",
            event_type="crisis",
            title=crisis['title'],
            description=crisis['description'],
            icon="💸",
            primary_character=character_name,
            duration_minutes=40,
            urgency_level="high",
            weight=8,
            options=[
                EventOption(
                    option_id="lend_money",
                    text=f"Offer to lend them ${crisis['money_amount']}",
                    requires_sp=None,
                    money_cost=crisis['money_amount'],
                    rapport_changes={character_name: 6},
                    emotional_state_changes={character_name: "grateful"},
                    sp_gain=2,
                    social_effect=f"{character_name} will remember your generosity",
                    success_text=f"{character_name} tears up. 'I'll pay you back, I promise. Thank you so much.'"
                ),
                EventOption(
                    option_id="emotional_support",
                    text="Offer emotional support and advice (no money)",
                    rapport_changes={character_name: 3},
                    sp_gain=1,
                    success_text=f"You help {character_name} work through their options. They appreciate having someone to talk to."
                ),
                EventOption(
                    option_id="use_desperation",
                    text="They're desperate... use this vulnerability",
                    requires_rapport=6,
                    sp_cost=3,
                    allows_phs=True,
                    phs_target=character_name,
                    phs_success_bonus=30,
                    phs_detection_risk=50,
                    social_effect="Exploiting their desperation",
                    success_text=f"{character_name} is so stressed they'll agree to anything...",
                    failure_text="They realize you're trying to manipulate them in their time of need!"
                ),
                EventOption(
                    option_id="dismiss",
                    text="'Everyone has money problems. You'll figure it out.'",
                    rapport_changes={character_name: -4},
                    emotional_state_changes={character_name: "hurt"},
                    success_text=f"{character_name} looks crushed. They won't forget your coldness."
                )
            ]
        )

        return event

    @staticmethod
    def generate_surprise_visitor_event() -> 'DynamicEvent':
        """Generate a surprise visitor event"""
        from systems.dynamic_events import DynamicEvent, EventOption

        visitors = [
            {
                'name': "An Ex-Partner",
                'description': "Someone's ex shows up unexpectedly at the door, causing tension.",
                'whose': random.choice(list(CHARACTERS.keys()))
            },
            {
                'name': "A Debt Collector",
                'description': "A debt collector is looking for someone in the family.",
                'whose': random.choice(list(CHARACTERS.keys()))
            },
            {
                'name': "Old Friend",
                'description': "An old friend from high school shows up unannounced.",
                'whose': random.choice(list(CHARACTERS.keys()))
            },
            {
                'name': "Estranged Relative",
                'description': "A family member no one has seen in years suddenly appears.",
                'whose': 'Family'
            }
        ]

        visitor = random.choice(visitors)

        event = DynamicEvent(
            event_id=f"surprise_visitor_{random.randint(1000,9999)}",
            event_type="visitor",
            title=f"Surprise Visitor: {visitor['name']}",
            description=visitor['description'],
            icon="🚪",
            primary_character=visitor['whose'] if visitor['whose'] != 'Family' else None,
            observers=list(CHARACTERS.keys())[:4],
            duration_minutes=45,
            urgency_level="high",
            weight=10,
            options=[
                EventOption(
                    option_id="welcome_them",
                    text="Be welcoming and hospitable",
                    rapport_changes={visitor['whose']: 3} if visitor['whose'] != 'Family' else {},
                    sp_gain=1,
                    social_effect="Family sees you're diplomatic",
                    observers=list(CHARACTERS.keys())[:3],
                    success_text="The tension eases a bit. Your hospitality is noted."
                ),
                EventOption(
                    option_id="protective",
                    text=f"Be protective of {visitor['whose'] if visitor['whose'] != 'Family' else 'the family'}",
                    requires_rapport=8,
                    rapport_changes={visitor['whose']: 5} if visitor['whose'] != 'Family' else {c: 2 for c in list(CHARACTERS.keys())[:3]},
                    sp_gain=2,
                    social_effect="You show loyalty",
                    success_text=f"Your protective stance is appreciated."
                ),
                EventOption(
                    option_id="gather_info",
                    text="Observe and gather information (strategic patience)",
                    sp_gain=3,
                    time_cost=20,
                    success_text="You learn valuable information about family dynamics by watching reactions."
                ),
                EventOption(
                    option_id="make_awkward",
                    text="Ask uncomfortable questions to create chaos",
                    rapport_changes={c: -2 for c in list(CHARACTERS.keys())[:3]},
                    sp_gain=1,
                    social_effect="You're causing unnecessary drama",
                    success_text="Awkward silence fills the room. Everyone is uncomfortable."
                )
            ]
        )

        return event

    @staticmethod
    def generate_scandal_event(character_name: str) -> 'DynamicEvent':
        """Generate a character scandal event"""
        from systems.dynamic_events import DynamicEvent, EventOption

        scandals = [
            {
                'title': f"{character_name}'s Secret Exposed",
                'description': f"Someone found out {character_name} has been lying about something significant...",
                'secret_type': 'lie'
            },
            {
                'title': f"Caught in the Act",
                'description': f"{character_name} was caught doing something they shouldn't have been doing.",
                'secret_type': 'caught'
            },
            {
                'title': f"Rumor Spreads",
                'description': f"A damaging rumor about {character_name} is spreading through the family.",
                'secret_type': 'rumor'
            },
            {
                'title': f"Old Mistake Resurfaces",
                'description': f"Something from {character_name}'s past has come back to haunt them.",
                'secret_type': 'past'
            }
        ]

        scandal = random.choice(scandals)

        event = DynamicEvent(
            event_id=f"scandal_{character_name.lower()}_{random.randint(1000,9999)}",
            event_type="crisis",
            title=scandal['title'],
            description=scandal['description'],
            icon="😱",
            primary_character=character_name,
            observers=[c for c in CHARACTERS.keys() if c != character_name][:4],
            duration_minutes=30,
            urgency_level="high",
            weight=12,
            options=[
                EventOption(
                    option_id="defend_them",
                    text=f"Publicly defend {character_name}",
                    requires_rapport=10,
                    rapport_changes={character_name: 7, **{obs: -1 for obs in [c for c in CHARACTERS.keys() if c != character_name][:2]}},
                    emotional_state_changes={character_name: "grateful"},
                    sp_gain=2,
                    social_effect=f"You show unwavering loyalty to {character_name}",
                    observers=[c for c in CHARACTERS.keys() if c != character_name][:4],
                    success_text=f"{character_name} will never forget that you stood by them."
                ),
                EventOption(
                    option_id="stay_neutral",
                    text="Stay neutral and avoid getting involved",
                    success_text="You keep your distance from the drama. Smart or cowardly?"
                ),
                EventOption(
                    option_id="investigate",
                    text="Investigate to find out the truth",
                    sp_gain=3,
                    time_cost=25,
                    success_text="You uncover interesting information that gives you leverage..."
                ),
                EventOption(
                    option_id="exploit_scandal",
                    text="Use their vulnerability to plant deep suggestions",
                    requires_sp=5,
                    sp_cost=5,
                    allows_phs=True,
                    phs_target=character_name,
                    phs_success_bonus=35,
                    phs_detection_risk=70,
                    suspicion_changes={obs: 15 for obs in [c for c in CHARACTERS.keys() if c != character_name][:2]},
                    social_effect="Exploiting someone's lowest moment",
                    observers=[c for c in CHARACTERS.keys() if c != character_name][:3],
                    success_text=f"In their shame and vulnerability, {character_name} is completely open to suggestion...",
                    failure_text="Someone calls you out for taking advantage of their crisis!"
                ),
                EventOption(
                    option_id="pile_on",
                    text="'I always knew something was off about you...'",
                    rapport_changes={character_name: -8, **{obs: -3 for obs in [c for c in CHARACTERS.keys() if c != character_name][:2]}},
                    suspicion_changes={obs: 5 for obs in [c for c in CHARACTERS.keys() if c != character_name][:2]},
                    social_effect="You show you're willing to kick someone when they're down",
                    success_text=f"{character_name} looks devastated. The family is shocked at your cruelty."
                )
            ]
        )

        return event


class ProceduralGameMode:
    """Main procedural generation manager"""

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize procedural mode

        Args:
            seed: Optional seed for reproducible generation
        """
        self.seed = seed if seed is not None else random.randint(1, 1000000)
        self.original_seed = self.seed

    def initialize_procedural_game(self) -> Tuple[Dict[str, Character], List['DynamicEvent']]:
        """
        Initialize a full procedural game

        Returns:
            (characters_dict, initial_events_list)
        """
        random.seed(self.seed)

        # 1. Generate varied characters
        characters = ProceduralCharacterGenerator.generate_all_characters()

        # 2. Generate relationship matrix
        relationships = ProceduralRelationshipGenerator.generate_relationship_matrix()

        # 3. Apply relationships to characters
        ProceduralRelationshipGenerator.apply_relationships_to_characters(characters, relationships)

        # 4. Generate initial event pool (mix of procedural events)
        initial_events = []

        # Add 2-3 random medical emergencies
        for _ in range(random.randint(2, 3)):
            char_name = random.choice(list(CHARACTERS.keys()))
            initial_events.append(ProceduralEventLibrary.generate_medical_emergency_event(char_name))

        # Add 2-3 financial crises
        for _ in range(random.randint(2, 3)):
            char_name = random.choice(list(CHARACTERS.keys()))
            initial_events.append(ProceduralEventLibrary.generate_financial_crisis_event(char_name))

        # Add 1-2 surprise visitors
        for _ in range(random.randint(1, 2)):
            initial_events.append(ProceduralEventLibrary.generate_surprise_visitor_event())

        # Add 2-4 scandals
        for _ in range(random.randint(2, 4)):
            char_name = random.choice(list(CHARACTERS.keys()))
            initial_events.append(ProceduralEventLibrary.generate_scandal_event(char_name))

        return characters, initial_events

    def get_procedural_summary(self, characters: Dict[str, Character]) -> str:
        """
        Get a summary of the procedural variations for this playthrough

        Returns:
            Formatted string with variation details
        """
        summary = f"\n{'='*70}\n"
        summary += f"PROCEDURAL PLAYTHROUGH (Seed: {self.original_seed})\n"
        summary += f"{'='*70}\n\n"

        summary += "CHARACTER VARIATIONS:\n"
        summary += "-" * 70 + "\n"

        for name, char in sorted(characters.items()):
            base_char = CHARACTERS[name]
            summary += f"\n{name}:\n"
            summary += f"  Resistance: {char.resistance}% "
            summary += f"(base: {base_char.resistance}%, range: {char.resistance - base_char.resistance:+d})\n"
            summary += f"  Personality: {char.personality}\n"

            if name in ProceduralCharacterGenerator.CHARACTER_VARIATIONS:
                # Show relationship variations
                variation = ProceduralCharacterGenerator.CHARACTER_VARIATIONS[name]
                summary += f"  Key Relationships:\n"
                for other, score in sorted(char.relationships.items())[:3]:
                    if other in variation.rapport_modifiers:
                        min_r, max_r = variation.rapport_modifiers[other]
                        summary += f"    - {other}: {score}/20 (range: {min_r}-{max_r})\n"

        summary += "\n" + "="*70 + "\n"
        summary += "💡 TIP: Every playthrough is different! Adapt your strategy.\n"
        summary += "="*70 + "\n"

        return summary

    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'seed': self.seed,
            'original_seed': self.original_seed
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ProceduralGameMode':
        """Deserialize from save"""
        mode = cls(seed=data.get('seed'))
        mode.original_seed = data.get('original_seed', mode.seed)
        return mode
