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
    money_cost: int = 0  # Money cost to perform (for expensive activities)
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

    # ==================== HOME ACTIVITIES ====================

    # Kitchen Activities
    KITCHEN_ACTIVITIES = {
        'cook_together': Activity(
            activity_id='cook_together',
            name='Cook Together',
            description='Prepare a meal together. Great for bonding and subtle suggestions.',
            location='home_kitchen',
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
            location='home_kitchen',
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
            location='home_kitchen',
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
            location='home_kitchen',
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
            location='home_your_room',
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
            location='home_your_room',
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
            location='home_your_room',
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
            location='home_backyard',
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
            location='home_backyard',
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
            location='home_backyard',
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
            location='fitness_center',
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
            location='fitness_center',
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

    # ==================== CITY ACTIVITIES ====================

    # City Park Activities
    PARK_ACTIVITIES = {
        'walk_park': Activity(
            activity_id='walk_park',
            name='Take a Walk',
            description='Walk through the park together. Fresh air and casual conversation.',
            location='city_park',
            duration_minutes=30,
            requires_character='any',
            min_rapport=2,
            activity_type='social',
            rapport_gain=2,
            emotional_outcome='relaxed',
            icon='🚶',
            success_messages=[
                "You walk side by side, enjoying the fresh air and open space.",
                "The peaceful setting makes conversation flow naturally.",
                "Walking together feels easy, comfortable, natural.",
                "They seem more open here, away from the usual places."
            ]
        ),
        'park_picnic': Activity(
            activity_id='park_picnic',
            money_cost=30,
            name='Have a Picnic',
            description='Spread out a blanket and share food. Romantic and relaxed.',
            location='city_park',
            duration_minutes=90,
            requires_character='any',
            min_rapport=8,
            sp_cost=1,
            activity_type='social',
            rapport_gain=3,
            allows_phs=True,
            phs_bonus=10,
            resistance_change=-8,
            emotional_outcome='happy',
            icon='🧺',
            success_messages=[
                "The picnic is lovely. You eat, laugh, and enjoy each other's company.",
                "This feels special. The setting, the food, the time together...",
                "They're completely relaxed, smiling, open.",
                "A perfect moment together in the sunshine."
            ]
        ),
        'park_jog': Activity(
            activity_id='park_jog',
            name='Jog Together',
            description='Go for a run in the park. Good exercise and bonding.',
            location='city_park',
            duration_minutes=45,
            requires_character='any',
            min_rapport=5,
            activity_type='exercise',
            rapport_gain=2,
            emotional_outcome='energized',
            icon='🏃',
            success_messages=[
                "You run together, matching pace, breathing in sync.",
                "The exercise feels good. You encourage each other.",
                "Endorphins and camaraderie. A great combination.",
                "You both feel energized and accomplished."
            ]
        ),
        'bench_talk': Activity(
            activity_id='bench_talk',
            name='Sit and Talk',
            description='Find a quiet bench for a deep conversation.',
            location='city_park',
            duration_minutes=45,
            requires_character='any',
            min_rapport=6,
            activity_type='social',
            rapport_gain=2,
            allows_phs=True,
            phs_bonus=8,
            resistance_change=-5,
            emotional_outcome='open',
            icon='💬',
            success_messages=[
                "The park bench offers privacy and peace for real conversation.",
                "They open up here, away from home and its distractions.",
                "You share thoughts, feelings, stories.",
                "This quiet moment together means a lot."
            ]
        )
    }

    # Coffee Café Activities
    CAFE_ACTIVITIES = {
        'coffee_date': Activity(
            activity_id='coffee_date',
            money_cost=20,
            name='Coffee Date',
            description='Enjoy coffee and pastries together. Intimate setting.',
            location='coffee_cafe',
            duration_minutes=60,
            requires_character='any',
            min_rapport=5,
            activity_type='social',
            rapport_gain=3,
            allows_phs=True,
            phs_bonus=10,
            resistance_change=-5,
            emotional_outcome='relaxed',
            icon='☕',
            success_messages=[
                "The café is cozy, intimate. Perfect for deep conversation.",
                "Coffee and conversation flow equally well.",
                "They're relaxed, engaged, focused on you.",
                "This feels like a real date. The atmosphere is perfect."
            ]
        ),
        'study_together': Activity(
            activity_id='study_together',
            name='Study/Read Together',
            description='Bring books and work quietly together. Comfortable intimacy.',
            location='coffee_cafe',
            duration_minutes=90,
            requires_character='any',
            min_rapport=8,
            activity_type='social',
            rapport_gain=2,
            resistance_change=-3,
            emotional_outcome='relaxed',
            icon='📚',
            success_messages=[
                "You sit across from each other, reading and occasionally chatting.",
                "The comfortable silence speaks volumes about your relationship.",
                "Sharing space without needing to fill it with words. Perfect.",
                "This quiet companionship is deeply satisfying."
            ]
        ),
        'plan_future': Activity(
            activity_id='plan_future',
            name='Plan Things Together',
            description='Discuss dreams, goals, and future plans over coffee.',
            location='coffee_cafe',
            duration_minutes=75,
            requires_character='any',
            min_rapport=10,
            sp_cost=1,
            activity_type='intimate',
            rapport_gain=4,
            allows_phs=True,
            phs_bonus=15,
            resistance_change=-10,
            emotional_outcome='hopeful',
            icon='🔮',
            success_messages=[
                "You talk about the future. Your dreams start to align...",
                "They're excited about possibilities. About doing things together.",
                "The conversation flows from what-ifs to definite plans.",
                "By the end, you both feel like you're on the same path."
            ]
        )
    }

    # Shopping Mall Activities
    MALL_ACTIVITIES = {
        'shop_together': Activity(
            activity_id='shop_together',
            money_cost=50,
            name='Go Shopping',
            description='Browse stores and help them pick things out.',
            location='shopping_mall',
            duration_minutes=120,
            requires_character='any',
            min_rapport=7,
            activity_type='social',
            rapport_gain=3,
            allows_phs=True,
            phs_bonus=12,
            resistance_change=-8,
            emotional_outcome='happy',
            icon='🛍️',
            success_messages=[
                "You walk through the mall together, trying things on and giving opinions.",
                "They value your taste. Your suggestions carry weight.",
                "Shopping together is fun, intimate. They trust your judgment.",
                "By the end, they've bought several things you recommended."
            ]
        ),
        'clothing_shopping': Activity(
            activity_id='clothing_shopping',
            money_cost=100,
            name='Help Pick Outfits',
            description='Help them choose new clothes. Perfect for style suggestions.',
            location='shopping_mall',
            duration_minutes=90,
            requires_character='any',
            min_rapport=10,
            sp_cost=1,
            activity_type='intimate',
            rapport_gain=3,
            allows_phs=True,
            phs_bonus=18,
            resistance_change=-12,
            emotional_outcome='excited',
            icon='👗',
            success_messages=[
                "You help them try on different outfits. They model for you.",
                "Your opinion matters. They're excited by your suggestions.",
                "The dressing room mirrors show them how good your choices look.",
                "They buy everything you picked out. Your influence is clear."
            ]
        ),
        'movie_theater': Activity(
            activity_id='movie_theater',
            money_cost=25,
            name='See a Movie',
            description='Watch a film together at the mall cinema.',
            location='shopping_mall',
            duration_minutes=150,
            requires_character='any',
            min_rapport=5,
            activity_type='entertainment',
            rapport_gain=2,
            allows_phs=True,
            phs_bonus=10,
            emotional_outcome='relaxed',
            icon='🎬',
            success_messages=[
                "The movie is good, but sitting close in the dark is better.",
                "You share popcorn and whispered comments.",
                "The shared experience brings you closer.",
                "Afterward, you discuss the film's themes..."
            ]
        ),
        'food_court': Activity(
            activity_id='food_court',
            name='Grab Food',
            description='Have a casual meal at the food court.',
            location='shopping_mall',
            duration_minutes=45,
            requires_character='any',
            min_rapport=3,
            activity_type='social',
            rapport_gain=1,
            emotional_outcome='happy',
            icon='🍔',
            success_messages=[
                "You grab food and find a table. Easy, casual, fun.",
                "The conversation is light and enjoyable.",
                "Simple time together, but it counts.",
                "They're relaxed and happy in your company."
            ]
        )
    }

    # Grocery Store Activities
    GROCERY_ACTIVITIES = {
        'buy_groceries': Activity(
            activity_id='buy_groceries',
            name='Buy Groceries',
            description='Shop for food and stock up your pantry.',
            location='grocery_store',
            duration_minutes=30,
            requires_character='none',
            activity_type='solo',
            icon='🛒',
            success_messages=[
                "You fill your cart with essentials and check out.",
                "The store is busy, but you get what you need.",
                "A productive shopping trip. Your pantry is stocked."
            ]
        ),
        'grocery_shop_together': Activity(
            activity_id='grocery_shop_together',
            name='Shop for Food Together',
            description='Help them pick groceries. Casual, domestic activity.',
            location='grocery_store',
            duration_minutes=45,
            requires_character='any',
            min_rapport=4,
            activity_type='social',
            rapport_gain=2,
            allows_phs=True,
            phs_bonus=10,
            resistance_change=-5,
            emotional_outcome='relaxed',
            icon='🛍️',
            success_messages=[
                "You walk the aisles together, discussing meal plans.",
                "They ask your opinion on what to buy. Your input matters.",
                "Simple domestic activity, but it feels intimate.",
                "Picking food together makes you feel closer."
            ]
        ),
        'chance_encounter': Activity(
            activity_id='chance_encounter',
            name='Browse the Store',
            description='Walk around. You might run into someone.',
            location='grocery_store',
            duration_minutes=20,
            requires_character='none',
            activity_type='solo',
            icon='👀',
            success_messages=[
                "You browse the aisles, looking at what's on sale.",
                "Just taking your time, enjoying the mundane.",
                "A quiet moment to yourself in a public space."
            ]
        )
    }

    # Restaurant Activities
    RESTAURANT_ACTIVITIES = {
        'dinner_date': Activity(
            activity_id='dinner_date',
            money_cost=80,
            name='Romantic Dinner',
            description='Upscale dinner date. Intimate, special occasion.',
            location='restaurant',
            duration_minutes=120,
            requires_character='any',
            min_rapport=10,
            sp_cost=2,
            activity_type='intimate',
            rapport_gain=5,
            allows_phs=True,
            phs_bonus=15,
            resistance_change=-15,
            emotional_outcome='romantic',
            icon='🍷',
            success_messages=[
                "The restaurant is perfect. Candlelight, good wine, great food.",
                "This feels special. A real date. They're dressed up, beautiful.",
                "The conversation flows as smoothly as the wine.",
                "By dessert, they're leaning close, eyes bright, completely focused on you."
            ]
        ),
        'celebration_dinner': Activity(
            activity_id='celebration_dinner',
            money_cost=60,
            name='Celebrate Together',
            description='Celebrate a milestone or achievement with a nice meal.',
            location='restaurant',
            duration_minutes=90,
            requires_character='any',
            min_rapport=8,
            sp_cost=1,
            activity_type='social',
            rapport_gain=4,
            emotional_outcome='happy',
            icon='🎉',
            success_messages=[
                "You toast to success, happiness, each other.",
                "The celebration feels shared, meaningful.",
                "They're so happy. The good food and company make it perfect.",
                "This moment together is one to remember."
            ]
        ),
        'business_lunch': Activity(
            activity_id='business_lunch',
            money_cost=35,
            name='Business Lunch',
            description='Professional lunch meeting. Good for serious conversations.',
            location='restaurant',
            duration_minutes=60,
            requires_character='any',
            min_rapport=5,
            activity_type='social',
            rapport_gain=2,
            emotional_outcome='focused',
            icon='💼',
            success_messages=[
                "The professional setting lends weight to the conversation.",
                "You discuss important matters over a good meal.",
                "They take you seriously. Your words carry authority here.",
                "A productive lunch. Progress was made."
            ]
        )
    }

    # Fitness Center Activities
    FITNESS_ACTIVITIES = {
        'gym_workout': Activity(
            activity_id='gym_workout',
            name='Workout Together',
            description='Exercise side by side at the gym. Build physical rapport.',
            location='fitness_center',
            duration_minutes=60,
            requires_character='any',
            min_rapport=5,
            activity_type='exercise',
            rapport_gain=2,
            emotional_outcome='energized',
            icon='💪',
            success_messages=[
                "The workout is challenging but you push each other.",
                "Sweating together builds a unique kind of bond.",
                "Physical exertion, mutual encouragement, shared achievement.",
                "You both feel strong and accomplished."
            ]
        ),
        'gym_yoga': Activity(
            activity_id='gym_yoga',
            name='Yoga Class',
            description='Attend yoga class together. Meditative and centering.',
            location='fitness_center',
            duration_minutes=60,
            requires_character='any',
            min_rapport=8,
            activity_type='exercise',
            rapport_gain=2,
            allows_phs=True,
            phs_bonus=12,
            resistance_change=-10,
            emotional_outcome='centered',
            icon='🧘',
            success_messages=[
                "The yoga class is peaceful. Your minds clear together.",
                "Breathing in sync, moving in harmony.",
                "The meditative state makes you both very receptive...",
                "After class, you both feel centered and connected."
            ]
        ),
        'personal_training': Activity(
            activity_id='personal_training',
            name='Personal Training Session',
            description='Train them personally. Authority and physical closeness.',
            location='fitness_center',
            duration_minutes=45,
            requires_character='any',
            min_rapport=10,
            sp_cost=1,
            activity_type='exercise',
            rapport_gain=3,
            allows_phs=True,
            phs_bonus=15,
            resistance_change=-8,
            emotional_outcome='trusting',
            icon='🏋️',
            success_messages=[
                "You guide them through exercises. They follow your instructions completely.",
                "The physical touch while correcting form feels natural, intimate.",
                "They trust you to push them. To know their limits.",
                "By the end, they're exhausted but grateful. You had complete authority."
            ]
        )
    }

    # Combine all activities
    ALL_ACTIVITIES = {
        **KITCHEN_ACTIVITIES,
        **LIVING_ROOM_ACTIVITIES,
        **BEDROOM_ACTIVITIES,
        **BACKYARD_ACTIVITIES,
        **GYM_ACTIVITIES,
        **PARK_ACTIVITIES,
        **CAFE_ACTIVITIES,
        **MALL_ACTIVITIES,
        **GROCERY_ACTIVITIES,
        **RESTAURANT_ACTIVITIES,
        **FITNESS_ACTIVITIES
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

        # Deduct money cost if any
        if activity.money_cost > 0:
            game_state.player.money -= activity.money_cost
            results['changes'].append(f"💵 Spent ${activity.money_cost}")
            results['money_spent'] = activity.money_cost

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
            game_state.player.money += activity.money_reward
            game_state.player.total_money_earned += activity.money_reward
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
            'Ruth': ['cook_together', 'teach_recipe', 'do_dishes', 'garden_together', 'read_together', 'coffee_date', 'study_together', 'dinner_date'],
            'Melanie': ['workout_together', 'yoga_session', 'watch_movie', 'board_game', 'gym_workout', 'gym_yoga', 'personal_training', 'park_jog'],
            'Tom': ['watch_tv', 'play_cards', 'bbq_together', 'watch_movie', 'food_court', 'movie_theater', 'business_lunch'],
            'Dawn': ['organize_closet', 'help_decorate', 'watch_tv', 'play_cards', 'stargaze', 'shop_together', 'clothing_shopping', 'celebration_dinner'],
            'Vanessa': ['organize_closet', 'watch_movie', 'read_together', 'private_talk', 'stargaze', 'clothing_shopping', 'coffee_date', 'dinner_date', 'plan_future'],
            'Derek': ['workout_together', 'play_cards', 'board_game', 'bbq_together', 'gym_workout', 'personal_training', 'park_jog'],
            'Karen': ['garden_together', 'make_coffee', 'private_talk', 'read_together', 'walk_park', 'bench_talk', 'study_together', 'business_lunch']
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

    @staticmethod
    def add_custom_activity(activity: Activity, location_group: str = 'custom'):
        """
        Add a custom activity dynamically (useful for mods/extensions)

        Args:
            activity: Activity object to add
            location_group: Optional group name for organization

        Example:
            >>> custom_activity = Activity(
            ...     activity_id='library_study',
            ...     name='Study at Library',
            ...     description='Research at the library.',
            ...     location='library',
            ...     duration_minutes=120,
            ...     requires_character='any',
            ...     min_rapport=5,
            ...     activity_type='social',
            ...     rapport_gain=2,
            ...     sp_reward=1,
            ...     icon='📚'
            ... )
            >>> ActivitiesSystem.add_custom_activity(custom_activity)
        """
        ActivitiesSystem.ALL_ACTIVITIES[activity.activity_id] = activity

    @staticmethod
    def get_activity_stats() -> Dict[str, int]:
        """Get statistics about activities in the system"""
        stats = {
            'total_activities': len(ActivitiesSystem.ALL_ACTIVITIES),
            'by_location': {},
            'by_type': {}
        }

        for activity in ActivitiesSystem.ALL_ACTIVITIES.values():
            # Count by location
            loc = activity.location
            stats['by_location'][loc] = stats['by_location'].get(loc, 0) + 1

            # Count by type
            atype = activity.activity_type
            stats['by_type'][atype] = stats['by_type'].get(atype, 0) + 1

        return stats


# ==================== EXTENSION GUIDE ====================
"""
HOW TO ADD ACTIVITIES FOR NEW LOCATIONS:

1. Create your new location in systems/location_system.py:

   NEW_LOCATION = Location(
       id='your_location_id',
       name='Your Location Name',
       description='Description',
       location_type='public',  # or 'home', 'work', 'private'
       atmosphere='casual',     # or 'intimate', 'energetic', 'professional', 'formal'
       conversation_modifiers=['relevant', 'topics'],
       opens_at=9,             # Optional: hour (24h format)
       closes_at=21,           # Optional: hour (24h format)
       travel_time_from_home=15  # Minutes to travel
   )

2. Add activities for that location in this file (activities.py):

   # Your Location Activities
   YOUR_LOCATION_ACTIVITIES = {
       'activity_id': Activity(
           activity_id='unique_activity_id',
           name='Activity Display Name',
           description='What the activity involves.',
           location='your_location_id',  # Must match location ID!
           duration_minutes=60,           # How long it takes
           requires_character='any',      # 'any' = need someone, None = solo
           min_rapport=5,                 # Min rapport needed (0-20)
           sp_cost=0,                     # SP to start (0 = free)
           activity_type='social',        # 'social', 'chore', 'exercise', 'entertainment', 'intimate'

           # Outcomes
           rapport_gain=2,                # Rapport gained (0-5 typical)
           money_reward=0,                # $ earned (for chores)
           sp_reward=0,                   # SP earned (rare rewards)
           resistance_change=0,           # Change to resistance (-15 to +5)

           # PHS Mechanics
           allows_phs=False,              # Can plant PHS during?
           phs_bonus=0,                   # Bonus to PHS success % (0-20)
           emotional_outcome=None,        # 'relaxed', 'happy', 'vulnerable', etc.

           # Display
           icon='🎯',                     # Emoji icon
           success_messages=[             # Random messages shown
               "You enjoyed the activity together.",
               "The time spent was valuable."
           ]
       ),
       # Add more activities...
   }

3. Add your activities to ALL_ACTIVITIES dict:

   ALL_ACTIVITIES = {
       **KITCHEN_ACTIVITIES,
       **LIVING_ROOM_ACTIVITIES,
       # ... existing ones ...
       **YOUR_LOCATION_ACTIVITIES,  # Add yours here!
   }

4. (Optional) Add character preferences:

   In get_character_activity_preferences(), add:

   'CharacterName': ['activity_id1', 'activity_id2', ...],

QUICK REFERENCE - Activity Types:
- social: General bonding activities
- chore: Work that earns money
- exercise: Physical activities
- entertainment: Fun, relaxing activities
- intimate: Private, vulnerable, close activities

QUICK REFERENCE - Emotional Outcomes:
- relaxed: Lowers guard, good for PHS
- happy: Positive mood
- vulnerable: Very open, best for PHS
- energized: Pumped up after exercise
- romantic: Date-like atmosphere
- focused: Serious, professional
- trusting: Deep trust established

QUICK REFERENCE - PHS Bonuses:
- +5-8%: Minor bonus (casual settings)
- +10-12%: Good bonus (focused activities)
- +15-18%: Major bonus (intimate/authoritative)
- +20%: Maximum bonus (closet organizing, personal training)

DESIGN TIPS:
- Short activities (10-30m) = lower rewards, good for quick rapport
- Long activities (90-120m) = higher rewards, significant time investment
- Intimate activities should require 8-12+ rapport
- Activities that cost SP should give unique benefits
- Balance: Not every activity needs PHS opportunities
- Variety: Mix social, practical, and intimate activities
- Character fit: Think about which characters would enjoy which activities
"""
