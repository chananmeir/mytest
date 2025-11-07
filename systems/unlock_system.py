"""
Progressive Unlock System - Manages character and location availability
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class UnlockCondition:
    """Represents a condition that must be met to unlock something"""
    condition_type: str  # 'rapport', 'event', 'time', 'quest', 'suspicion'
    target: Optional[str] = None  # Character name for rapport/suspicion checks
    value: int = 0  # Threshold value (rapport level, days, etc.)
    event_id: Optional[str] = None  # Specific event that unlocks
    quest_id: Optional[str] = None  # Quest completion requirement
    multiple_targets: Optional[Dict[str, int]] = None  # For "both Ruth AND Tom" conditions


@dataclass
class UnlockableLocation:
    """Defines a location with unlock conditions"""
    location_id: str
    location_name: str
    is_public: bool  # Public = always accessible, Private = needs unlock
    unlock_conditions: List[UnlockCondition] = field(default_factory=list)
    category: str = "house"  # house, external, special
    owner: Optional[str] = None  # Character who owns this private space
    description: str = ""


@dataclass
class UnlockableCharacter:
    """Defines when a character becomes available"""
    character_name: str
    category: str  # 'core', 'extended_family', 'neighbor', 'work', 'social'
    introduction_week: int  # Which game week they're introduced
    introduction_event: str  # Event that introduces them
    unlock_conditions: List[UnlockCondition] = field(default_factory=list)


class UnlockSystem:
    """Manages progression and unlocks"""

    # Define all locations with their unlock conditions
    LOCATIONS = {
        # PUBLIC HOUSE LOCATIONS (Always accessible)
        'kitchen': UnlockableLocation(
            location_id='kitchen',
            location_name='Kitchen',
            is_public=True,
            category='house',
            description='Family kitchen with dining area'
        ),
        'living_room': UnlockableLocation(
            location_id='living_room',
            location_name='Living Room',
            is_public=True,
            category='house',
            description='Comfortable family room with TV'
        ),
        'dining_room': UnlockableLocation(
            location_id='dining_room',
            location_name='Dining Room',
            is_public=True,
            category='house',
            description='Where the family gathers for meals'
        ),
        'backyard': UnlockableLocation(
            location_id='backyard',
            location_name='Backyard',
            is_public=True,
            category='house',
            description='Outdoor space with garden'
        ),
        'hallway': UnlockableLocation(
            location_id='hallway',
            location_name='Hallway',
            is_public=True,
            category='house',
            description='Main hallway of the house'
        ),

        # PRIVATE BEDROOMS (Rapport-based unlock)
        'ruth_bedroom': UnlockableLocation(
            location_id='ruth_bedroom',
            location_name="Ruth's Bedroom",
            is_public=False,
            category='house',
            owner='Ruth',
            unlock_conditions=[
                UnlockCondition(condition_type='rapport', target='Ruth', value=10),
                UnlockCondition(condition_type='suspicion', target='Ruth', value=60)  # Max 60% suspicion
            ],
            description="Ruth's private bedroom"
        ),
        'tom_bedroom': UnlockableLocation(
            location_id='tom_bedroom',
            location_name="Tom's Office/Den",
            is_public=False,
            category='house',
            owner='Tom',
            unlock_conditions=[
                UnlockCondition(condition_type='rapport', target='Tom', value=8),
                UnlockCondition(condition_type='suspicion', target='Tom', value=60)
            ],
            description="Tom's home office space"
        ),
        'melanie_bedroom': UnlockableLocation(
            location_id='melanie_bedroom',
            location_name="Melanie's Bedroom",
            is_public=False,
            category='external',
            owner='Melanie',
            unlock_conditions=[
                UnlockCondition(condition_type='rapport', target='Melanie', value=12),
                UnlockCondition(condition_type='event', event_id='visit_melanie_house')
            ],
            description="Melanie's bedroom at her house"
        ),
        'dawn_sewing_room': UnlockableLocation(
            location_id='dawn_sewing_room',
            location_name="Dawn's Sewing Room",
            is_public=False,
            category='house',
            owner='Dawn',
            unlock_conditions=[
                UnlockCondition(condition_type='rapport', target='Dawn', value=15),
                UnlockCondition(condition_type='event', event_id='dawn_invites_sewing_room')
            ],
            description="Dawn's private creative space"
        ),

        # SPECIAL/HIGH SECURITY LOCATIONS
        'master_bedroom': UnlockableLocation(
            location_id='master_bedroom',
            location_name='Master Bedroom',
            is_public=False,
            category='house',
            owner='Ruth',
            unlock_conditions=[
                UnlockCondition(
                    condition_type='rapport',
                    target='Ruth',
                    value=18,
                    multiple_targets={'Ruth': 18, 'Tom': 15}  # Both required
                ),
                UnlockCondition(condition_type='event', event_id='invited_master_bedroom')
            ],
            description='Ruth and Tom\'s master bedroom'
        ),
        'vanessa_apartment': UnlockableLocation(
            location_id='vanessa_apartment',
            location_name="Vanessa's Apartment",
            is_public=False,
            category='external',
            owner='Vanessa',
            unlock_conditions=[
                UnlockCondition(condition_type='quest', quest_id='help_vanessa_move'),
                UnlockCondition(condition_type='rapport', target='Vanessa', value=12)
            ],
            description="Vanessa's upscale apartment"
        ),
        'derek_gym': UnlockableLocation(
            location_id='derek_gym',
            location_name="Derek's Gym",
            is_public=False,
            category='external',
            owner='Derek',
            unlock_conditions=[
                UnlockCondition(condition_type='event', event_id='derek_invites_gym'),
                UnlockCondition(condition_type='rapport', target='Derek', value=10)
            ],
            description='The gym where Derek trains clients'
        ),
        'karen_office': UnlockableLocation(
            location_id='karen_office',
            location_name="Karen's Office",
            is_public=False,
            category='external',
            owner='Karen',
            unlock_conditions=[
                UnlockCondition(condition_type='event', event_id='visit_karen_school'),
                UnlockCondition(condition_type='rapport', target='Karen', value=10)
            ],
            description="Karen's office at the elementary school"
        )
    }

    # Define character introduction schedule
    CHARACTERS = {
        'Ruth': UnlockableCharacter(
            character_name='Ruth',
            category='core',
            introduction_week=0,  # Available from start
            introduction_event='game_start',
            unlock_conditions=[]  # No conditions - always available
        ),
        'Tom': UnlockableCharacter(
            character_name='Tom',
            category='core',
            introduction_week=0,
            introduction_event='game_start',
            unlock_conditions=[]
        ),
        'Melanie': UnlockableCharacter(
            character_name='Melanie',
            category='extended_family',
            introduction_week=2,
            introduction_event='family_dinner_week2',
            unlock_conditions=[
                UnlockCondition(condition_type='time', value=7)  # 7 days = week 2
            ]
        ),
        'Dawn': UnlockableCharacter(
            character_name='Dawn',
            category='extended_family',
            introduction_week=2,
            introduction_event='family_dinner_week2',
            unlock_conditions=[
                UnlockCondition(condition_type='time', value=7)
            ]
        ),
        'Vanessa': UnlockableCharacter(
            character_name='Vanessa',
            category='extended_family',
            introduction_week=3,
            introduction_event='family_gathering_week3',
            unlock_conditions=[
                UnlockCondition(condition_type='time', value=14)  # 14 days = week 3
            ]
        ),
        'Derek': UnlockableCharacter(
            character_name='Derek',
            category='extended_family',
            introduction_week=3,
            introduction_event='family_gathering_week3',
            unlock_conditions=[
                UnlockCondition(condition_type='time', value=14)
            ]
        ),
        'Karen': UnlockableCharacter(
            character_name='Karen',
            category='extended_family',
            introduction_week=4,
            introduction_event='karen_visit',
            unlock_conditions=[
                UnlockCondition(condition_type='time', value=21),  # 21 days = week 4
                UnlockCondition(condition_type='rapport', target='Dawn', value=10)  # Know Dawn well
            ]
        )
    }

    @staticmethod
    def check_unlock_condition(condition: UnlockCondition, game_state) -> Tuple[bool, str]:
        """
        Check if a single unlock condition is met

        Returns:
            (is_met, reason_if_not_met)
        """
        if condition.condition_type == 'rapport':
            char = game_state.get_character(condition.target)
            if not char:
                return (False, f"Character {condition.target} not found")

            if char.rapport >= condition.value:
                return (True, "")
            else:
                return (False, f"Need {condition.value} rapport with {condition.target} (currently {char.rapport})")

        elif condition.condition_type == 'suspicion':
            char = game_state.get_character(condition.target)
            if not char:
                return (True, "")  # If character doesn't exist, suspicion check passes

            # Suspicion condition is a MAX - must be BELOW the value
            if char.player_suspicion < condition.value:
                return (True, "")
            else:
                return (False, f"{condition.target} is too suspicious of you ({char.player_suspicion}% >= {condition.value}%)")

        elif condition.condition_type == 'time':
            days_passed = game_state.game_time.day
            if days_passed >= condition.value:
                return (True, "")
            else:
                days_remaining = condition.value - days_passed
                return (False, f"Available in {days_remaining} days")

        elif condition.condition_type == 'event':
            # Check if event has been triggered
            if hasattr(game_state, 'completed_events'):
                if condition.event_id in game_state.completed_events:
                    return (True, "")
            return (False, f"Requires event: {condition.event_id}")

        elif condition.condition_type == 'quest':
            # Check if quest is completed
            if hasattr(game_state, 'completed_quests'):
                if condition.quest_id in game_state.completed_quests:
                    return (True, "")
            return (False, f"Requires quest: {condition.quest_id}")

        return (False, "Unknown condition type")

    @staticmethod
    def is_location_unlocked(location_id: str, game_state) -> Tuple[bool, List[str]]:
        """
        Check if a location is unlocked

        Returns:
            (is_unlocked, list_of_reasons_if_locked)
        """
        if location_id not in UnlockSystem.LOCATIONS:
            return (False, ["Location not found"])

        location = UnlockSystem.LOCATIONS[location_id]

        # Public locations are always unlocked
        if location.is_public:
            return (True, [])

        # Check all unlock conditions
        unmet_reasons = []
        all_met = True

        for condition in location.unlock_conditions:
            # Handle multiple targets (AND condition)
            if condition.multiple_targets:
                for target_name, target_value in condition.multiple_targets.items():
                    temp_condition = UnlockCondition(
                        condition_type='rapport',
                        target=target_name,
                        value=target_value
                    )
                    is_met, reason = UnlockSystem.check_unlock_condition(temp_condition, game_state)
                    if not is_met:
                        all_met = False
                        unmet_reasons.append(reason)
            else:
                is_met, reason = UnlockSystem.check_unlock_condition(condition, game_state)
                if not is_met:
                    all_met = False
                    unmet_reasons.append(reason)

        return (all_met, unmet_reasons)

    @staticmethod
    def is_character_unlocked(character_name: str, game_state) -> Tuple[bool, List[str]]:
        """
        Check if a character is unlocked/available

        Returns:
            (is_unlocked, list_of_reasons_if_locked)
        """
        if character_name not in UnlockSystem.CHARACTERS:
            # Character not in unlock system = always available (for backward compatibility)
            return (True, [])

        character_unlock = UnlockSystem.CHARACTERS[character_name]

        unmet_reasons = []
        all_met = True

        for condition in character_unlock.unlock_conditions:
            is_met, reason = UnlockSystem.check_unlock_condition(condition, game_state)
            if not is_met:
                all_met = False
                unmet_reasons.append(reason)

        return (all_met, unmet_reasons)

    @staticmethod
    def get_available_locations(game_state) -> List[Dict]:
        """
        Get all locations that are currently unlocked

        Returns:
            List of location dicts with unlock status
        """
        available = []

        for loc_id, location in UnlockSystem.LOCATIONS.items():
            is_unlocked, reasons = UnlockSystem.is_location_unlocked(loc_id, game_state)

            available.append({
                'id': loc_id,
                'name': location.location_name,
                'is_public': location.is_public,
                'is_unlocked': is_unlocked,
                'category': location.category,
                'owner': location.owner,
                'description': location.description,
                'unlock_reasons': reasons if not is_unlocked else []
            })

        return available

    @staticmethod
    def get_available_characters(game_state) -> List[Dict]:
        """
        Get all characters that are currently unlocked

        Returns:
            List of character dicts with unlock status
        """
        available = []

        for char_name, char_unlock in UnlockSystem.CHARACTERS.items():
            is_unlocked, reasons = UnlockSystem.is_character_unlocked(char_name, game_state)

            available.append({
                'name': char_name,
                'category': char_unlock.category,
                'introduction_week': char_unlock.introduction_week,
                'is_unlocked': is_unlocked,
                'unlock_reasons': reasons if not is_unlocked else []
            })

        return available

    @staticmethod
    def get_next_unlock_preview(game_state) -> List[Dict]:
        """
        Show what's coming next (upcoming unlocks)

        Returns:
            List of upcoming unlocks sorted by proximity
        """
        upcoming = []

        # Check locked locations
        for loc_id, location in UnlockSystem.LOCATIONS.items():
            is_unlocked, reasons = UnlockSystem.is_location_unlocked(loc_id, game_state)

            if not is_unlocked:
                upcoming.append({
                    'type': 'location',
                    'name': location.location_name,
                    'requirements': reasons,
                    'owner': location.owner
                })

        # Check locked characters
        for char_name, char_unlock in UnlockSystem.CHARACTERS.items():
            is_unlocked, reasons = UnlockSystem.is_character_unlocked(char_name, game_state)

            if not is_unlocked:
                upcoming.append({
                    'type': 'character',
                    'name': char_name,
                    'introduction_week': char_unlock.introduction_week,
                    'requirements': reasons
                })

        return upcoming

    @staticmethod
    def trigger_location_unlock_check(location_id: str, game_state) -> Tuple[bool, str]:
        """
        Check if location just became unlocked and return unlock message

        Returns:
            (newly_unlocked, unlock_message)
        """
        is_unlocked, reasons = UnlockSystem.is_location_unlocked(location_id, game_state)

        if is_unlocked:
            location = UnlockSystem.LOCATIONS.get(location_id)
            if location and not location.is_public:
                return (True, f"🔓 {location.location_name} is now accessible!")

        return (False, "")

    @staticmethod
    def check_rapport_unlock_triggers(character_name: str, new_rapport: int, game_state) -> List[str]:
        """
        Check if reaching this rapport level unlocks any locations

        Returns:
            List of unlock messages
        """
        unlock_messages = []

        for loc_id, location in UnlockSystem.LOCATIONS.items():
            if location.owner == character_name:
                # Check if this location is now unlocked
                is_unlocked, reasons = UnlockSystem.is_location_unlocked(loc_id, game_state)

                if is_unlocked:
                    # Check if it was just unlocked by checking rapport exactly
                    for condition in location.unlock_conditions:
                        if condition.condition_type == 'rapport' and condition.target == character_name:
                            if new_rapport == condition.value:
                                unlock_messages.append(
                                    f"🔓 {location.location_name} unlocked! {character_name} trusts you enough to invite you."
                                )

        return unlock_messages
