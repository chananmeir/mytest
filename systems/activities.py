"""
Activities System - Location-specific activities beyond just talking
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import random


@dataclass
class Activity:
    """Represents an activity that can be performed"""
    activity_id: str
    name: str
    description: str
    location: str  # Which location this activity is available at
    duration_minutes: int  # How long the activity takes
    requires_character: Optional[str] = None  # Character must be present
    min_rapport: int = 0  # Minimum rapport with character
    sp_cost: int = 0  # SP cost to initiate
    max_participants: int = 2  # How many can do this together
    activity_type: str = "social"  # social, chore, exercise, entertainment, intimate

    # Outcomes
    rapport_gain: int = 0  # Base rapport gain
    money_reward: int = 0  # Money earned (for chores)
    sp_reward: int = 0  # SP earned
    resistance_change: int = 0  # Change to resistance

    # Special mechanics
    allows_phs: bool = False  # Can plant PHS during this activity
    phs_bonus: int = 0  # Bonus to PHS success rate during this activity
    emotional_outcome: Optional[str] = None  # Emotional state after activity

    # Flavor
    icon: str = "🎯"  # Emoji icon
    success_messages: List[str] = None  # Random success messages

    def __post_init__(self):
        if self.success_messages is None:
            self.success_messages = [f"You enjoyed {self.name} together."]


class ActivitiesSystem:
    """Manages all activities in the game"""

    # Kitchen Activities
    KITCHEN_ACTIVITIES = {
        'cook_together': Activity(
            activity_id='cook_together',
            name='Cook Together',
            description='Prepare a meal together. Great for bonding and subtle suggestions.',
            location='kitchen',
            duration_minutes=45,
            requires_character='any',
            min_rapport=3,
            activity_type='social',
            rapport_gain=2,
            allows_phs=True,
            phs_bonus=10,
            emotional_outcome='relaxed',
            icon='🍳',
            success_messages=[
                "You work together seamlessly, chopping vegetables and sharing stories.",
                "The kitchen fills with delicious aromas as you cook side by side.",
                "They seem relaxed and open as you prepare the meal together.",
                "Cooking together feels natural, comfortable. They laugh at your jokes."
            ]
        ),
        'make_coffee': Activity(
            activity_id='make_coffee',
            name='Make Coffee',
            description='Brew coffee and chat. Quick rapport building.',
            location='kitchen',
            duration_minutes=10,
            requires_character='any',
            min_rapport=0,
            activity_type='social',
            rapport_gain=1,
            icon='☕',
            success_messages=[
                "You share a quiet moment over coffee.",
                "The warm drink and conversation feels comfortable.",
                "They appreciate you making coffee for them."
            ]
        ),
        'teach_recipe': Activity(
            activity_id='teach_recipe',
            name='Teach a Recipe',
            description='Show them a special recipe. They\'re focused on your words...',
            location='kitchen',
            duration_minutes=60,
            requires_character='any',
            min_rapport=8,
            sp_cost=1,
            activity_type='social',
            rapport_gain=3,
            allows_phs=True,
            phs_bonus=15,
            resistance_change=-10,
            emotional_outcome='open',
            icon='📖',
            success_messages=[
                "They hang on your every word as you explain the recipe.",
                "Their focus is entirely on you. They trust your guidance completely.",
                "You demonstrate each step carefully. They follow your lead without question.",
                "By the end, they're eager to try more of your suggestions."
            ]
        ),
        'do_dishes': Activity(
            activity_id='do_dishes',
            name='Help with Dishes',
            description='Wash dishes together. Builds appreciation.',
            location='kitchen',
            duration_minutes=20,
            requires_character='any',
            min_rapport=0,
            activity_type='chore',
            rapport_gain=1,
            money_reward=5,
            icon='🧼',
            success_messages=[
                "They appreciate you helping with the chores.",
                "Working together makes the task go quickly.",
                "You chat comfortably while washing dishes."
            ]
        )
    }

    # Living Room Activities
    LIVING_ROOM_ACTIVITIES = {
        'watch_tv': Activity(
            activity_id='watch_tv',
            name='Watch TV Together',
            description='Watch a show. Relax together, plant subliminal suggestions.',
            location='home_living_room',
            duration_minutes=30,
            requires_character='any',
            min_rapport=2,
            activity_type='entertainment',
            rapport_gain=1,
            allows_phs=True,
            phs_bonus=8,
            emotional_outcome='relaxed',
            icon='📺',
            success_messages=[
                "You watch TV side by side, making comments about the show.",
                "They lean back, relaxed. Their guard is down.",
                "During commercial breaks, you chat casually about the show's themes...",
                "The shared experience brings you closer together."
            ]
        ),
        'watch_movie': Activity(
            activity_id='watch_movie',
            name='Watch a Movie',
            description='Settle in for a full movie. Long bonding session, good for deep rapport.',
            location='home_living_room',
            duration_minutes=120,
            requires_character='any',
            min_rapport=5,
            activity_type='entertainment',
            rapport_gain=3,
            allows_phs=True,
            phs_bonus=12,
            resistance_change=-5,
            emotional_outcome='relaxed',
            icon='🎬',
            success_messages=[
                "Two hours of shared entertainment. You feel much closer now.",
                "The movie's themes give you plenty to discuss afterward...",
                "They're completely absorbed in the film. So receptive...",
                "By the end, they're leaning against you comfortably."
            ]
        ),
        'play_cards': Activity(
            activity_id='play_cards',
            name='Play Cards',
            description='Friendly card game. Can make small bets.',
            location='home_living_room',
            duration_minutes=30,
            requires_character='any',
            min_rapport=3,
            activity_type='entertainment',
            rapport_gain=2,
            money_reward=10,
            icon='🃏',
            success_messages=[
                "You win a few hands. They owe you one...",
                "The friendly competition is fun. You're both laughing.",
                "Cards and conversation flow easily.",
                "They're having a great time. The atmosphere is light and playful."
            ]
        ),
        'board_game': Activity(
            activity_id='board_game',
            name='Play Board Game',
            description='Longer strategic game. Great bonding time.',
            location='home_living_room',
            duration_minutes=60,
            requires_character='any',
            min_rapport=5,
            activity_type='entertainment',
            rapport_gain=2,
            sp_reward=1,
            icon='🎲',
            success_messages=[
                "The game is engaging and brings you together.",
                "Strategic thinking, playful banter, and quality time.",
                "You both get competitive in a fun way.",
                "The shared challenge strengthens your bond."
            ]
        ),
        'read_together': Activity(
            activity_id='read_together',
            name='Read Together',
            description='Share a book or magazine. Quiet intimacy.',
            location='home_living_room',
            duration_minutes=45,
            requires_character='any',
            min_rapport=8,
            activity_type='social',
            rapport_gain=2,
            resistance_change=-3,
            emotional_outcome='relaxed',
            icon='📚',
            success_messages=[
                "Quiet reading side by side feels intimate.",
                "You occasionally read passages aloud to each other.",
                "The peaceful atmosphere is deeply comfortable.",
                "This quiet time together means a lot."
            ]
        )
    }

    # Bedroom Activities
    BEDROOM_ACTIVITIES = {
        'organize_closet': Activity(
            activity_id='organize_closet',
            name='Help Organize Closet',
            description='Go through their wardrobe. Perfect for clothing suggestions.',
            location='bedroom',
            duration_minutes=60,
            requires_character='any',
            min_rapport=10,
            sp_cost=1,
            activity_type='intimate',
            rapport_gain=3,
            allows_phs=True,
            phs_bonus=20,
            resistance_change=-15,
            emotional_outcome='open',
            icon='👗',
            success_messages=[
                "You go through their clothes together, suggesting what looks good...",
                "They try on different outfits for your opinion. They value your input.",
                "Discussing their wardrobe feels personal, intimate.",
                "By the end, they're excited to wear what you suggested."
            ]
        ),
        'help_decorate': Activity(
            activity_id='help_decorate',
            name='Help Decorate Room',
            description='Rearrange and personalize their space. Deep bonding.',
            location='bedroom',
            duration_minutes=90,
            requires_character='any',
            min_rapport=12,
            activity_type='intimate',
            rapport_gain=4,
            sp_reward=2,
            resistance_change=-10,
            emotional_outcome='happy',
            icon='🖼️',
            success_messages=[
                "Working on their personal space together feels special.",
                "They trust your design suggestions completely.",
                "The room looks great. They're so happy with your help.",
                "This level of intimacy and trust means everything."
            ]
        ),
        'private_talk': Activity(
            activity_id='private_talk',
            name='Private Conversation',
            description='Deep, personal conversation in private. Very intimate.',
            location='bedroom',
            duration_minutes=45,
            requires_character='any',
            min_rapport=8,
            activity_type='intimate',
            rapport_gain=3,
            allows_phs=True,
            phs_bonus=10,
            resistance_change=-8,
            emotional_outcome='vulnerable',
            icon='💭',
            success_messages=[
                "Away from others, they open up completely.",
                "The privacy makes this conversation deeply personal.",
                "They share things they wouldn't tell anyone else.",
                "This level of vulnerability and trust is profound."
            ]
        )
    }

    # Backyard Activities
    BACKYARD_ACTIVITIES = {
        'garden_together': Activity(
            activity_id='garden_together',
            name='Work in Garden',
            description='Plant flowers, pull weeds. Peaceful and meditative.',
            location='backyard',
            duration_minutes=60,
            requires_character='any',
            min_rapport=5,
            activity_type='chore',
            rapport_gain=2,
            money_reward=15,
            allows_phs=True,
            phs_bonus=8,
            emotional_outcome='relaxed',
            icon='🌱',
            success_messages=[
                "Working with the earth is calming. You both relax into the rhythm.",
                "The garden work is meditative. They're very receptive...",
                "You chat easily while tending the plants.",
                "The physical work together builds a comfortable camaraderie."
            ]
        ),
        'bbq_together': Activity(
            activity_id='bbq_together',
            name='BBQ Together',
            description='Grill food outdoors. Casual, fun atmosphere.',
            location='backyard',
            duration_minutes=90,
            requires_character='any',
            min_rapport=7,
            activity_type='social',
            rapport_gain=3,
            emotional_outcome='happy',
            icon='🍖',
            success_messages=[
                "Grilling together is fun and relaxed.",
                "The smell of BBQ, cold drinks, easy conversation...",
                "They're having a great time. The casual atmosphere is perfect.",
                "This feels like real quality time together."
            ]
        ),
        'stargaze': Activity(
            activity_id='stargaze',
            name='Stargaze Together',
            description='Look at stars and talk. Very romantic and intimate.',
            location='backyard',
            duration_minutes=60,
            requires_character='any',
            min_rapport=12,
            activity_type='intimate',
            rapport_gain=4,
            allows_phs=True,
            phs_bonus=15,
            resistance_change=-12,
            emotional_outcome='vulnerable',
            icon='⭐',
            success_messages=[
                "Under the stars, everything feels more intimate.",
                "The darkness and beauty of the night sky opens them up.",
                "You talk about dreams, hopes, fears... deep things.",
                "This moment feels magical. They're completely open to you."
            ]
        )
    }

    # Gym Activities (if gym location exists)
    GYM_ACTIVITIES = {
        'workout_together': Activity(
            activity_id='workout_together',
            name='Exercise Together',
            description='Work out side by side. Good for Derek.',
            location='gym',
            duration_minutes=60,
            requires_character='any',
            min_rapport=5,
            activity_type='exercise',
            rapport_gain=2,
            emotional_outcome='energized',
            icon='💪',
            success_messages=[
                "The workout is challenging but satisfying.",
                "Exercising together builds camaraderie.",
                "You push each other to work harder.",
                "The endorphins make you both feel great."
            ]
        ),
        'yoga_session': Activity(
            activity_id='yoga_session',
            name='Yoga Session',
            description='Relaxing yoga together. Very receptive state.',
            location='gym',
            duration_minutes=45,
            requires_character='any',
            min_rapport=8,
            activity_type='exercise',
            rapport_gain=2,
            allows_phs=True,
            phs_bonus=12,
            resistance_change=-10,
            emotional_outcome='relaxed',
            icon='🧘',
            success_messages=[
                "The yoga poses are calming and centering.",
                "Their mind is clear and receptive. Perfect state...",
                "Breathing together, moving together. Very meditative.",
                "The session leaves you both feeling peaceful and connected."
            ]
        )
    }

    # Combine all activities
    ALL_ACTIVITIES = {
        **KITCHEN_ACTIVITIES,
        **LIVING_ROOM_ACTIVITIES,
        **BEDROOM_ACTIVITIES,
        **BACKYARD_ACTIVITIES,
        **GYM_ACTIVITIES
    }

    @staticmethod
    def get_available_activities(
        location: str,
        character_present: Optional[str],
        rapport: int,
        player_sp: int
    ) -> List[Activity]:
        """
        Get activities available at current location

        Args:
            location: Current location ID
            character_present: Character at location (or None)
            rapport: Rapport with character
            player_sp: Player's current SP

        Returns:
            List of available activities
        """
        available = []

        for activity in ActivitiesSystem.ALL_ACTIVITIES.values():
            # Check location
            if activity.location != location:
                continue

            # Check if requires character
            if activity.requires_character == 'any' and not character_present:
                continue

            # Check rapport requirement
            if character_present and rapport < activity.min_rapport:
                continue

            # Check SP cost
            if activity.sp_cost > player_sp:
                continue

            available.append(activity)

        return available

    @staticmethod
    def perform_activity(
        activity: Activity,
        character,
        game_state
    ) -> Dict:
        """
        Perform an activity and return outcomes

        Args:
            activity: The activity being performed
            character: Character participating
            game_state: Current game state

        Returns:
            Dict with activity results
        """
        results = {
            'success': True,
            'activity_name': activity.name,
            'duration': activity.duration_minutes,
            'message': random.choice(activity.success_messages),
            'changes': []
        }

        # Apply rapport gain
        if activity.rapport_gain > 0:
            from systems.hypnosis import HypnosisSystem
            old_rapport = character.rapport
            rapport_msg = HypnosisSystem.build_rapport(
                game_state,
                character.name,
                activity.rapport_gain,
                f"from {activity.name}"
            )
            results['changes'].append(rapport_msg)
            results['rapport_gained'] = activity.rapport_gain

        # Apply resistance change
        if activity.resistance_change != 0:
            old_resistance = character.resistance
            character.resistance = max(0, min(100, character.resistance + activity.resistance_change))
            results['changes'].append(
                f"{character.name}'s resistance: {activity.resistance_change:+d}% ({character.resistance}%)"
            )

        # Apply emotional outcome
        if activity.emotional_outcome:
            from systems.hypnosis import HypnosisSystem
            emotion_msg = HypnosisSystem.change_emotional_state(
                game_state,
                character.name,
                activity.emotional_outcome,
                f"from {activity.name}"
            )
            results['changes'].append(emotion_msg)

        # Award money
        if activity.money_reward > 0:
            game_state.player.suggestion_points += activity.money_reward
            results['changes'].append(f"💵 Earned ${activity.money_reward}")
            results['money_earned'] = activity.money_reward

        # Award SP
        if activity.sp_reward > 0:
            game_state.add_sp(activity.sp_reward, f"from {activity.name}")
            results['changes'].append(f"✨ Gained {activity.sp_reward} SP")
            results['sp_earned'] = activity.sp_reward

        # Track for goals
        from systems.goal_system import GoalSystem
        goal_messages = GoalSystem.track_activity(game_state, activity.activity_id)
        results['changes'].extend(goal_messages)

        # Note PHS opportunity
        if activity.allows_phs:
            results['phs_opportunity'] = True
            results['phs_bonus'] = activity.phs_bonus
            results['changes'].append(
                f"💡 Perfect moment for a suggestion (+{activity.phs_bonus}% success)"
            )

        # Record memory
        from systems.memory import MemorySystem
        memory_content = f"Did '{activity.name}' together. {results['message']}"
        MemorySystem.record_important_event(
            character,
            memory_content,
            importance=6,
            related_characters=['Player']
        )

        return results

    @staticmethod
    def get_character_activity_preferences(character_name: str) -> List[str]:
        """
        Get activities a specific character especially enjoys

        Args:
            character_name: Name of character

        Returns:
            List of preferred activity IDs
        """
        preferences = {
            'Ruth': ['cook_together', 'teach_recipe', 'do_dishes', 'garden_together', 'read_together'],
            'Melanie': ['workout_together', 'yoga_session', 'watch_movie', 'board_game'],
            'Tom': ['watch_tv', 'play_cards', 'bbq_together', 'watch_movie'],
            'Dawn': ['organize_closet', 'help_decorate', 'watch_tv', 'play_cards', 'stargaze'],
            'Vanessa': ['organize_closet', 'watch_movie', 'read_together', 'private_talk', 'stargaze'],
            'Derek': ['workout_together', 'play_cards', 'board_game', 'bbq_together'],
            'Karen': ['garden_together', 'make_coffee', 'private_talk', 'read_together']
        }

        return preferences.get(character_name, [])

    @staticmethod
    def get_activity_by_id(activity_id: str) -> Optional[Activity]:
        """Get activity by its ID"""
        return ActivitiesSystem.ALL_ACTIVITIES.get(activity_id)

    @staticmethod
    def get_activities_by_location(location: str) -> List[Activity]:
        """Get all activities for a specific location"""
        return [
            activity for activity in ActivitiesSystem.ALL_ACTIVITIES.values()
            if activity.location == location
        ]
