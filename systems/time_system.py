"""
Time and calendar system for Family Dynamics RPG
Characters have schedules, moods change by time of day, realistic progression
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List
import json


@dataclass
class GameTime:
    """Tracks in-game time and date"""
    year: int = 2024
    month: int = 1
    day: int = 15  # Start on a Monday
    hour: int = 18  # Start at 6 PM (dinner time)
    minute: int = 0

    def __post_init__(self):
        self._update_derived()

    def _update_derived(self):
        """Update derived properties"""
        # Create datetime object for easy manipulation
        self._datetime = datetime(self.year, self.month, self.day, self.hour, self.minute)

        # Calculate day of week (0 = Monday, 6 = Sunday)
        self.day_of_week = self._datetime.weekday()
        self.day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][self.day_of_week]

        # Time period for scheduling
        if 5 <= self.hour < 12:
            self.period = 'morning'
        elif 12 <= self.hour < 17:
            self.period = 'afternoon'
        elif 17 <= self.hour < 21:
            self.period = 'evening'
        else:
            self.period = 'night'

        # Is it a weekend?
        self.is_weekend = self.day_of_week >= 5

    def advance_minutes(self, minutes: int) -> Dict[str, any]:
        """Advance time by minutes, return events that occurred"""
        old_period = self.period
        old_day = self.day

        self._datetime += timedelta(minutes=minutes)

        # Update all fields
        self.year = self._datetime.year
        self.month = self._datetime.month
        self.day = self._datetime.day
        self.hour = self._datetime.hour
        self.minute = self._datetime.minute

        self._update_derived()

        # Track what changed
        events = {
            'new_period': self.period != old_period,
            'new_day': self.day != old_day,
            'old_period': old_period,
            'current_period': self.period,
            'messages': []
        }

        if events['new_day']:
            events['messages'].append(f"📅 A new day dawns: {self.day_name}, {self.month}/{self.day}")

        if events['new_period']:
            period_messages = {
                'morning': '🌅 Morning arrives - the house stirs to life',
                'afternoon': '☀️ Afternoon - midday activities',
                'evening': '🌆 Evening falls - time for family gathering',
                'night': '🌙 Night time - things are winding down'
            }
            events['messages'].append(period_messages.get(self.period, ''))

        return events

    def advance_hours(self, hours: int) -> Dict[str, any]:
        """Advance time by hours"""
        return self.advance_minutes(hours * 60)

    def get_formatted_time(self) -> str:
        """Get formatted time string"""
        # 12-hour format
        hour_12 = self.hour if self.hour <= 12 else self.hour - 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        am_pm = 'AM' if self.hour < 12 else 'PM'

        return f"{hour_12}:{self.minute:02d} {am_pm}"

    def get_formatted_date(self) -> str:
        """Get formatted date string"""
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        return f"{self.day_name}, {month_names[self.month]} {self.day}, {self.year}"

    def to_dict(self) -> dict:
        """Convert to dictionary for saving"""
        return {
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'hour': self.hour,
            'minute': self.minute
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'GameTime':
        """Create from dictionary"""
        return cls(**data)


# Character schedules - what they're likely doing at different times
CHARACTER_SCHEDULES = {
    'Ruth': {
        'morning': {
            'location': 'Kitchen',
            'activity': 'Making breakfast',
            'mood_modifier': 'rushed',
            'availability': 0.6
        },
        'afternoon': {
            'location': 'Office',
            'activity': 'Working from home',
            'mood_modifier': 'focused',
            'availability': 0.3
        },
        'evening': {
            'location': 'Dining room',
            'activity': 'Preparing dinner',
            'mood_modifier': 'hospitable',
            'availability': 0.9
        },
        'night': {
            'location': 'Living room',
            'activity': 'Relaxing with TV',
            'mood_modifier': 'tired',
            'availability': 0.7
        }
    },
    'Tom': {
        'morning': {
            'location': 'Home office',
            'activity': 'Getting ready for work',
            'mood_modifier': 'groggy',
            'availability': 0.4
        },
        'afternoon': {
            'location': 'Work',
            'activity': 'At the office',
            'mood_modifier': 'stressed',
            'availability': 0.1
        },
        'evening': {
            'location': 'Dining room',
            'activity': 'At dinner',
            'mood_modifier': 'relaxed',
            'availability': 0.9
        },
        'night': {
            'location': 'Den',
            'activity': 'Reading or browsing',
            'mood_modifier': 'contemplative',
            'availability': 0.6
        }
    },
    'Lisa': {
        'morning': {
            'location': 'Bedroom',
            'activity': 'Sleeping in',
            'mood_modifier': 'grumpy',
            'availability': 0.2
        },
        'afternoon': {
            'location': 'School/College',
            'activity': 'Classes',
            'mood_modifier': 'distracted',
            'availability': 0.1
        },
        'evening': {
            'location': 'Dining room',
            'activity': 'At dinner (reluctantly)',
            'mood_modifier': 'bored',
            'availability': 0.8
        },
        'night': {
            'location': 'Bedroom',
            'activity': 'Texting friends',
            'mood_modifier': 'chatty',
            'availability': 0.9
        }
    },
    'Marcus': {
        'morning': {
            'location': 'Gym',
            'activity': 'Working out',
            'mood_modifier': 'energetic',
            'availability': 0.3
        },
        'afternoon': {
            'location': 'Gym/Work',
            'activity': 'Training clients',
            'mood_modifier': 'confident',
            'availability': 0.2
        },
        'evening': {
            'location': 'Dining room',
            'activity': 'Eating (lots)',
            'mood_modifier': 'hungry',
            'availability': 0.9
        },
        'night': {
            'location': 'Living room',
            'activity': 'Meal prepping',
            'mood_modifier': 'focused',
            'availability': 0.5
        }
    },
    'Sophie': {
        'morning': {
            'location': 'Home office',
            'activity': 'Research and writing',
            'mood_modifier': 'sharp',
            'availability': 0.3
        },
        'afternoon': {
            'location': 'University',
            'activity': 'Teaching/Research',
            'mood_modifier': 'intellectual',
            'availability': 0.1
        },
        'evening': {
            'location': 'Dining room',
            'activity': 'Dinner discussion',
            'mood_modifier': 'analytical',
            'availability': 0.8
        },
        'night': {
            'location': 'Study',
            'activity': 'Reading',
            'mood_modifier': 'contemplative',
            'availability': 0.6
        }
    },
    'Rachel': {
        'morning': {
            'location': 'Bedroom',
            'activity': 'Getting ready for school',
            'mood_modifier': 'playful',
            'availability': 0.5
        },
        'afternoon': {
            'location': 'School',
            'activity': 'At school',
            'mood_modifier': 'energetic',
            'availability': 0.0
        },
        'evening': {
            'location': 'Dining room',
            'activity': 'Dinner time!',
            'mood_modifier': 'excited',
            'availability': 1.0
        },
        'night': {
            'location': 'Bedroom',
            'activity': 'Bedtime',
            'mood_modifier': 'sleepy',
            'availability': 0.3
        }
    },
    'James': {
        'morning': {
            'location': 'Bedroom',
            'activity': 'Still sleeping',
            'mood_modifier': 'sleepy',
            'availability': 0.1
        },
        'afternoon': {
            'location': 'School',
            'activity': 'At school',
            'mood_modifier': 'zoned out',
            'availability': 0.0
        },
        'evening': {
            'location': 'Dining room',
            'activity': 'Eating quietly',
            'mood_modifier': 'quiet',
            'availability': 0.7
        },
        'night': {
            'location': 'Bedroom',
            'activity': 'Gaming',
            'mood_modifier': 'focused',
            'availability': 0.8
        }
    }
}


def get_character_schedule(character_name: str, period: str) -> Dict:
    """Get a character's schedule for a time period"""
    schedule = CHARACTER_SCHEDULES.get(character_name, {})
    return schedule.get(period, {
        'location': 'Unknown',
        'activity': 'Doing something',
        'mood_modifier': 'normal',
        'availability': 0.5
    })


def is_character_available(character_name: str, period: str) -> bool:
    """Check if character is likely available for conversation"""
    schedule = get_character_schedule(character_name, period)
    import random
    return random.random() < schedule.get('availability', 0.5)
