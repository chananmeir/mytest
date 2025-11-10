"""
Event System - Manages story events, character introductions, and triggers
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class GameEvent:
    """Represents a story event in the game"""
    event_id: str
    event_name: str
    event_type: str  # 'character_intro', 'story', 'unlock', 'special'
    description: str
    dialogue: List[Dict[str, str]]  # List of {speaker, text} dicts
    triggers_on_day: Optional[int] = None  # Auto-trigger on this day
    one_time: bool = True  # Only trigger once
    unlocks_characters: List[str] = None  # Characters unlocked by this event
    unlocks_locations: List[str] = None  # Locations unlocked by this event


class EventSystem:
    """Handles game events and character introductions"""

    # Define all events
    EVENTS = {
        'game_start': GameEvent(
            event_id='game_start',
            event_name='Moving In',
            event_type='story',
            description='You move in with Ruth and Tom to get back on your feet.',
            dialogue=[
                {'speaker': 'System', 'text': 'You\'ve just moved in with your cousin Ruth and her husband Tom. They\'ve been kind enough to let you stay while you get back on your feet.'},
                {'speaker': 'Ruth', 'text': 'Make yourself at home! We\'re happy to have you here.'},
                {'speaker': 'Tom', 'text': 'Yeah, stay as long as you need. We\'ve got plenty of space.'}
            ],
            one_time=True,
            unlocks_characters=['Ruth', 'Tom']
        ),

        'family_dinner_week2': GameEvent(
            event_id='family_dinner_week2',
            event_name='Family Dinner',
            event_type='character_intro',
            description='Ruth has invited some family over for dinner.',
            dialogue=[
                {'speaker': 'System', 'text': 'It\'s been a week since you moved in. Ruth has invited family over for dinner tonight.'},
                {'speaker': 'Ruth', 'text': 'My sister Melanie and our mom Dawn are coming over for dinner. It\'ll be nice for everyone to meet you properly!'},
                {'speaker': 'System', 'text': 'Later that evening...'},
                {'speaker': 'Dawn', 'text': 'So you\'re the one staying with Ruth and Tom! It\'s lovely to meet you. Ruth speaks very highly of you.'},
                {'speaker': 'Melanie', 'text': 'Hey. I\'m Melanie, Ruth\'s sister. I work at the hospital downtown.'},
                {'speaker': 'System', 'text': 'You spend the evening getting to know Dawn and Melanie over dinner.'}
            ],
            triggers_on_day=7,
            one_time=True,
            unlocks_characters=['Melanie', 'Dawn']
        ),

        'family_gathering_week3': GameEvent(
            event_id='family_gathering_week3',
            event_name='Extended Family Gathering',
            event_type='character_intro',
            description='More family members stop by for a weekend visit.',
            dialogue=[
                {'speaker': 'System', 'text': 'Another weekend at Ruth and Tom\'s house. More family members are stopping by.'},
                {'speaker': 'Vanessa', 'text': 'Hi everyone! Sorry I\'m late - traffic was awful. Oh, you must be the cousin I\'ve heard about!'},
                {'speaker': 'Ruth', 'text': 'Vanessa is our cousin. She works in marketing at a big firm downtown.'},
                {'speaker': 'Derek', 'text': 'Hey, I\'m Derek - Vanessa\'s brother. Personal trainer. You look like you could use a gym buddy.'},
                {'speaker': 'System', 'text': 'The afternoon is filled with family conversation and catching up.'}
            ],
            triggers_on_day=14,
            one_time=True,
            unlocks_characters=['Vanessa', 'Derek']
        ),

        'karen_visit': GameEvent(
            event_id='karen_visit',
            event_name='Dawn\'s Friend Visits',
            event_type='character_intro',
            description='Dawn brings her friend Karen to meet the family.',
            dialogue=[
                {'speaker': 'System', 'text': 'Dawn has brought a friend over to meet everyone.'},
                {'speaker': 'Dawn', 'text': 'I hope you don\'t mind - I brought my dear friend Karen. We\'ve known each other for years.'},
                {'speaker': 'Karen', 'text': 'Hello. Dawn has told me so much about her family. I\'m a school principal, so I appreciate organized households like this.'},
                {'speaker': 'Ruth', 'text': 'Karen is always welcome here! She practically family at this point.'},
                {'speaker': 'System', 'text': 'Karen seems reserved but polite.'}
            ],
            triggers_on_day=21,
            one_time=True,
            unlocks_characters=['Karen']
        ),

        # Location unlock events
        'visit_melanie_house': GameEvent(
            event_id='visit_melanie_house',
            event_name='Visit Melanie\'s Place',
            event_type='unlock',
            description='Melanie invites you to her house.',
            dialogue=[
                {'speaker': 'Melanie', 'text': 'Hey, want to come over to my place sometime? I could use some company.'},
                {'speaker': 'System', 'text': 'You can now visit Melanie at her house.'}
            ],
            one_time=True,
            unlocks_locations=['melanie_bedroom']
        ),

        'dawn_invites_sewing_room': GameEvent(
            event_id='dawn_invites_sewing_room',
            event_name='Dawn\'s Sewing Room',
            event_type='unlock',
            description='Dawn shows you her sewing room.',
            dialogue=[
                {'speaker': 'Dawn', 'text': 'Would you like to see my sewing room? I\'m quite proud of it. I don\'t show it to just anyone.'},
                {'speaker': 'System', 'text': 'Dawn has invited you to her private creative space.'}
            ],
            one_time=True,
            unlocks_locations=['dawn_sewing_room']
        ),

        'invited_master_bedroom': GameEvent(
            event_id='invited_master_bedroom',
            event_name='Deepening Trust',
            event_type='unlock',
            description='Ruth and Tom trust you completely.',
            dialogue=[
                {'speaker': 'Ruth', 'text': 'You know, you\'re really part of the family now. Our home is your home.'},
                {'speaker': 'Tom', 'text': 'Yeah, make yourself comfortable anywhere. We trust you completely.'},
                {'speaker': 'System', 'text': 'You now have access to their private bedroom.'}
            ],
            one_time=True,
            unlocks_locations=['master_bedroom']
        ),

        'derek_invites_gym': GameEvent(
            event_id='derek_invites_gym',
            event_name='Gym Invitation',
            event_type='unlock',
            description='Derek invites you to work out at his gym.',
            dialogue=[
                {'speaker': 'Derek', 'text': 'Yo, you should come check out my gym sometime. I\'ll show you around.'},
                {'speaker': 'System', 'text': 'You can now visit Derek at his gym.'}
            ],
            one_time=True,
            unlocks_locations=['derek_gym']
        ),

        'visit_karen_school': GameEvent(
            event_id='visit_karen_school',
            event_name='School Visit',
            event_type='unlock',
            description='Karen invites you to see her workplace.',
            dialogue=[
                {'speaker': 'Karen', 'text': 'If you\'re ever in the area, feel free to stop by my school. I\'d be happy to show you around.'},
                {'speaker': 'System', 'text': 'You can now visit Karen at her school office.'}
            ],
            one_time=True,
            unlocks_locations=['karen_office']
        )
    }

    @staticmethod
    def check_time_triggered_events(game_state) -> List[GameEvent]:
        """
        Check if any events should be triggered based on game time

        Returns:
            List of events that should trigger
        """
        current_day = game_state.game_time.day
        events_to_trigger = []

        for event_id, event in EventSystem.EVENTS.items():
            # Skip if already completed
            if event.one_time and event_id in game_state.completed_events:
                continue

            # Check if day-based trigger
            if event.triggers_on_day is not None:
                if current_day >= event.triggers_on_day:
                    events_to_trigger.append(event)

        return events_to_trigger

    @staticmethod
    def trigger_event(event_id: str, game_state) -> Tuple[bool, Dict]:
        """
        Trigger an event and apply its effects

        Returns:
            (success, event_data)
        """
        if event_id not in EventSystem.EVENTS:
            return (False, {'error': 'Event not found'})

        event = EventSystem.EVENTS[event_id]

        # Check if already completed
        if event.one_time and event_id in game_state.completed_events:
            return (False, {'error': 'Event already completed'})

        # Mark as completed
        game_state.completed_events.append(event_id)

        # Unlock characters
        if event.unlocks_characters:
            for char_name in event.unlocks_characters:
                if char_name not in game_state.unlocked_characters:
                    game_state.unlocked_characters.append(char_name)

        # Unlock locations
        if event.unlocks_locations:
            for loc_id in event.unlocks_locations:
                if loc_id not in game_state.unlocked_locations:
                    game_state.unlocked_locations.append(loc_id)

        # Return event data for display
        return (True, {
            'event_id': event.event_id,
            'event_name': event.event_name,
            'event_type': event.event_type,
            'description': event.description,
            'dialogue': event.dialogue,
            'unlocks_characters': event.unlocks_characters or [],
            'unlocks_locations': event.unlocks_locations or []
        })

    @staticmethod
    def get_pending_events(game_state) -> List[Dict]:
        """
        Get all events that haven't been triggered yet but could be

        Returns:
            List of pending event summaries
        """
        current_day = game_state.game_time.day
        pending = []

        for event_id, event in EventSystem.EVENTS.items():
            # Skip completed
            if event.one_time and event_id in game_state.completed_events:
                continue

            # Check if available
            if event.triggers_on_day is not None:
                days_until = event.triggers_on_day - current_day
                if days_until > 0:
                    pending.append({
                        'event_id': event.event_id,
                        'event_name': event.event_name,
                        'event_type': event.event_type,
                        'description': event.description,
                        'days_until': days_until
                    })

        return pending

    @staticmethod
    def format_event_dialogue(event_data: Dict) -> str:
        """
        Format event dialogue for display

        Returns:
            Formatted dialogue string
        """
        lines = []
        lines.append(f"=== {event_data['event_name']} ===\n")
        lines.append(f"{event_data['description']}\n")

        for dialogue in event_data['dialogue']:
            speaker = dialogue['speaker']
            text = dialogue['text']

            if speaker == 'System':
                lines.append(f"\n{text}\n")
            else:
                lines.append(f"{speaker}: \"{text}\"")

        # Show unlocks
        if event_data.get('unlocks_characters'):
            lines.append(f"\n✨ New characters available: {', '.join(event_data['unlocks_characters'])}")

        if event_data.get('unlocks_locations'):
            lines.append(f"\n🔓 New locations unlocked: {', '.join(event_data['unlocks_locations'])}")

        return '\n'.join(lines)
