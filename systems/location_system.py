"""
Location System for Family Dynamics RPG
Manages locations, travel, and character placement based on time
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import time as datetime_time


@dataclass
class Location:
    """Represents a location in the game world"""
    id: str
    name: str
    description: str
    location_type: str  # 'home', 'work', 'public', 'private'

    # What activities/topics are natural here
    atmosphere: str  # 'casual', 'professional', 'intimate', 'energetic', 'formal'
    conversation_modifiers: List[str] = field(default_factory=list)  # Topics that fit this location

    # Time-based availability
    opens_at: Optional[int] = None  # Hour (24h format), None = always open
    closes_at: Optional[int] = None  # Hour (24h format), None = never closes

    # Travel time from home (in minutes)
    travel_time_from_home: int = 0

    # Is this a sub-location of another? (e.g., Kitchen is inside Home)
    parent_location: Optional[str] = None

    def is_open(self, current_hour: int) -> bool:
        """Check if location is accessible at current time"""
        if self.opens_at is None and self.closes_at is None:
            return True

        if self.opens_at is not None and current_hour < self.opens_at:
            return False

        if self.closes_at is not None and current_hour >= self.closes_at:
            return False

        return True

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location_type': self.location_type,
            'atmosphere': self.atmosphere,
            'conversation_modifiers': self.conversation_modifiers,
            'opens_at': self.opens_at,
            'closes_at': self.closes_at,
            'travel_time_from_home': self.travel_time_from_home,
            'parent_location': self.parent_location
        }


# ==================== HOME LOCATIONS ====================

HOME_LOCATIONS = {
    'home_kitchen': Location(
        id='home_kitchen',
        name='Home - Kitchen',
        description='The family kitchen, warm and filled with the aroma of cooking. The heart of the home where everyone gathers.',
        location_type='home',
        atmosphere='casual',
        conversation_modifiers=['family', 'food', 'daily_life', 'domestic'],
        parent_location='home'
    ),

    'home_living_room': Location(
        id='home_living_room',
        name='Home - Living Room',
        description='A cozy living room with comfortable couches and a TV. The family often relaxes here together.',
        location_type='home',
        atmosphere='casual',
        conversation_modifiers=['family', 'entertainment', 'relaxation', 'casual_chat'],
        parent_location='home'
    ),

    'home_dining_room': Location(
        id='home_dining_room',
        name='Home - Dining Room',
        description='The formal dining room where the family shares meals. A place for deeper conversations.',
        location_type='home',
        atmosphere='intimate',
        conversation_modifiers=['family', 'serious_topics', 'bonding', 'meals'],
        parent_location='home'
    ),

    'home_your_room': Location(
        id='home_your_room',
        name='Home - Your Room',
        description='Your private room. A quiet space for reflection or private conversations.',
        location_type='home',
        atmosphere='intimate',
        conversation_modifiers=['personal', 'private', 'intimate', 'vulnerable'],
        parent_location='home'
    ),

    'home_backyard': Location(
        id='home_backyard',
        name='Home - Backyard',
        description='A peaceful backyard with a patio. Fresh air and privacy for one-on-one conversations.',
        location_type='home',
        atmosphere='casual',
        conversation_modifiers=['casual', 'private', 'relaxed', 'outdoor'],
        parent_location='home'
    ),
}


# ==================== WORK LOCATIONS ====================

WORK_LOCATIONS = {
    'ruths_office': Location(
        id='ruths_office',
        name="Ruth's Office",
        description="Ruth's workplace - a busy office environment. She's usually focused on work here.",
        location_type='work',
        atmosphere='professional',
        conversation_modifiers=['work', 'career', 'stress', 'professional'],
        opens_at=8,
        closes_at=18,
        travel_time_from_home=25
    ),

    'fitness_center': Location(
        id='fitness_center',
        name='Fitness Center',
        description="Marcus's gym where he trains clients. Energetic atmosphere, smell of sweat and determination.",
        location_type='work',
        atmosphere='energetic',
        conversation_modifiers=['fitness', 'body', 'health', 'motivation', 'physical'],
        opens_at=6,
        closes_at=22,
        travel_time_from_home=20
    ),

    'elementary_school': Location(
        id='elementary_school',
        name='Elementary School',
        description="Karen's school where she works as principal. Structured, rule-oriented environment.",
        location_type='work',
        atmosphere='formal',
        conversation_modifiers=['education', 'rules', 'responsibility', 'children'],
        opens_at=7,
        closes_at=17,
        travel_time_from_home=15
    ),
}


# ==================== PUBLIC LOCATIONS ====================

PUBLIC_LOCATIONS = {
    'city_park': Location(
        id='city_park',
        name='City Park',
        description='A beautiful park with walking paths, benches, and green spaces. Peaceful and open.',
        location_type='public',
        atmosphere='casual',
        conversation_modifiers=['nature', 'relaxation', 'casual', 'open', 'reflection'],
        travel_time_from_home=10
    ),

    'coffee_cafe': Location(
        id='coffee_cafe',
        name='Downtown Café',
        description='A cozy café with comfortable seating and the smell of fresh coffee. Great for intimate conversations.',
        location_type='public',
        atmosphere='intimate',
        conversation_modifiers=['casual', 'personal', 'deep_conversation', 'relaxed'],
        opens_at=7,
        closes_at=22,
        travel_time_from_home=15
    ),

    'shopping_mall': Location(
        id='shopping_mall',
        name='Shopping Mall',
        description='A busy mall with shops and people. Good for casual encounters and shopping discussions.',
        location_type='public',
        atmosphere='casual',
        conversation_modifiers=['shopping', 'fashion', 'appearance', 'casual', 'public'],
        opens_at=10,
        closes_at=21,
        travel_time_from_home=20
    ),

    'grocery_store': Location(
        id='grocery_store',
        name='Grocery Store',
        description='A local supermarket. People shop for food here. You might run into someone you know.',
        location_type='public',
        atmosphere='casual',
        conversation_modifiers=['food', 'shopping', 'casual', 'daily_life', 'public'],
        opens_at=7,
        closes_at=23,
        travel_time_from_home=10
    ),

    'restaurant': Location(
        id='restaurant',
        name='Nice Restaurant',
        description='An upscale restaurant. Perfect for special conversations and bonding over good food.',
        location_type='public',
        atmosphere='intimate',
        conversation_modifiers=['food', 'intimate', 'special_occasion', 'bonding'],
        opens_at=11,
        closes_at=23,
        travel_time_from_home=25
    ),
}


# ==================== COMBINED DATABASE ====================

ALL_LOCATIONS = {
    **HOME_LOCATIONS,
    **WORK_LOCATIONS,
    **PUBLIC_LOCATIONS
}


# ==================== CHARACTER LOCATION SCHEDULES ====================

# Extended from time_system.py - now includes specific locations
CHARACTER_LOCATION_SCHEDULES = {
    'Ruth': {
        'morning': {
            'location': 'home_kitchen',
            'activity': 'Making breakfast',
            'mood_modifier': 'rushed',
            'availability': 0.6
        },
        'afternoon': {
            'location': 'ruths_office',
            'activity': 'Working at her desk',
            'mood_modifier': 'focused',
            'availability': 0.3
        },
        'evening': {
            'location': 'home_dining_room',
            'activity': 'Preparing dinner',
            'mood_modifier': 'hospitable',
            'availability': 0.9
        },
        'night': {
            'location': 'home_living_room',
            'activity': 'Relaxing with TV',
            'mood_modifier': 'tired',
            'availability': 0.7
        }
    },

    'Tom': {
        'morning': {
            'location': 'home_kitchen',
            'activity': 'Having coffee',
            'mood_modifier': 'groggy',
            'availability': 0.5
        },
        'afternoon': {
            'location': 'ruths_office',  # Works near Ruth
            'activity': 'Fixing computers',
            'mood_modifier': 'focused',
            'availability': 0.2
        },
        'evening': {
            'location': 'home_dining_room',
            'activity': 'At family dinner',
            'mood_modifier': 'avoiding_conflict',
            'availability': 0.8
        },
        'night': {
            'location': 'home_your_room',  # Visits you sometimes
            'activity': 'Chatting casually',
            'mood_modifier': 'relaxed',
            'availability': 0.6
        }
    },

    'Marcus': {
        'morning': {
            'location': 'fitness_center',
            'activity': 'Morning workout',
            'mood_modifier': 'energetic',
            'availability': 0.7
        },
        'afternoon': {
            'location': 'fitness_center',
            'activity': 'Training clients',
            'mood_modifier': 'professional',
            'availability': 0.4
        },
        'evening': {
            'location': 'home_dining_room',
            'activity': 'Eating protein-rich dinner',
            'mood_modifier': 'proud',
            'availability': 0.8
        },
        'night': {
            'location': 'home_living_room',
            'activity': 'Flexing in mirror',
            'mood_modifier': 'confident',
            'availability': 0.6
        }
    },

    'Sophie': {
        'morning': {
            'location': 'coffee_cafe',
            'activity': 'Reading news with coffee',
            'mood_modifier': 'intellectual',
            'availability': 0.6
        },
        'afternoon': {
            'location': 'city_park',
            'activity': 'Reading on a bench',
            'mood_modifier': 'thoughtful',
            'availability': 0.7
        },
        'evening': {
            'location': 'home_dining_room',
            'activity': 'Sharing her insights',
            'mood_modifier': 'analytical',
            'availability': 0.8
        },
        'night': {
            'location': 'home_your_room',
            'activity': 'Deep conversation',
            'mood_modifier': 'open',
            'availability': 0.7
        }
    },

    'Lisa': {
        'morning': {
            'location': 'home_your_room',
            'activity': 'Sleeping in',
            'mood_modifier': 'grumpy',
            'availability': 0.3
        },
        'afternoon': {
            'location': 'shopping_mall',
            'activity': 'Shopping with friends',
            'mood_modifier': 'social',
            'availability': 0.5
        },
        'evening': {
            'location': 'home_dining_room',
            'activity': 'Reluctantly at dinner',
            'mood_modifier': 'bored',
            'availability': 0.7
        },
        'night': {
            'location': 'home_living_room',
            'activity': 'On her phone',
            'mood_modifier': 'distracted',
            'availability': 0.6
        }
    },

    'Rachel': {
        'morning': {
            'location': 'home_backyard',
            'activity': 'Playing outside',
            'mood_modifier': 'playful',
            'availability': 0.8
        },
        'afternoon': {
            'location': 'city_park',
            'activity': 'At the playground',
            'mood_modifier': 'energetic',
            'availability': 0.6
        },
        'evening': {
            'location': 'home_dining_room',
            'activity': 'Excitedly eating',
            'mood_modifier': 'happy',
            'availability': 0.9
        },
        'night': {
            'location': 'home_your_room',
            'activity': 'Bedtime stories',
            'mood_modifier': 'sleepy',
            'availability': 0.7
        }
    },

    'James': {
        'morning': {
            'location': 'home_living_room',
            'activity': 'Playing video games',
            'mood_modifier': 'distracted',
            'availability': 0.5
        },
        'afternoon': {
            'location': 'home_living_room',
            'activity': 'Still gaming',
            'mood_modifier': 'absorbed',
            'availability': 0.3
        },
        'evening': {
            'location': 'home_dining_room',
            'activity': 'Quietly eating',
            'mood_modifier': 'withdrawn',
            'availability': 0.6
        },
        'night': {
            'location': 'home_your_room',
            'activity': 'Gaming on laptop',
            'mood_modifier': 'tired',
            'availability': 0.4
        }
    },
}


def get_location(location_id: str) -> Optional[Location]:
    """Get a location by ID"""
    return ALL_LOCATIONS.get(location_id)


def get_character_location(character_name: str, period: str) -> str:
    """Get the location ID where a character is during a time period"""
    schedule = CHARACTER_LOCATION_SCHEDULES.get(character_name, {})
    period_schedule = schedule.get(period, {})
    return period_schedule.get('location', 'home_living_room')


def get_characters_at_location(location_id: str, period: str) -> List[str]:
    """Get all characters currently at a specific location"""
    characters = []
    for char_name in CHARACTER_LOCATION_SCHEDULES.keys():
        if get_character_location(char_name, period) == location_id:
            characters.append(char_name)
    return characters


def get_available_locations(current_hour: int) -> Dict[str, Location]:
    """Get all locations that are currently open"""
    return {
        loc_id: loc for loc_id, loc in ALL_LOCATIONS.items()
        if loc.is_open(current_hour)
    }


def get_location_context_for_llm(location: Location) -> str:
    """Format location information for LLM context"""
    context = f"\n\nCURRENT LOCATION: {location.name}\n"
    context += f"Setting: {location.description}\n"
    context += f"Atmosphere: {location.atmosphere}\n"

    if location.conversation_modifiers:
        context += f"Natural topics here: {', '.join(location.conversation_modifiers)}\n"

    return context
