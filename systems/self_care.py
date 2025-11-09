"""
Self-Care System - Track player's basic needs
Adds realism with hunger, hygiene, energy, and bathroom needs
"""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class SelfCareState:
    """Tracks player's physical needs"""
    hunger: int = 80  # 0 = starving, 100 = stuffed
    hygiene: int = 85  # 0 = filthy, 100 = pristine
    energy: int = 75  # 0 = exhausted, 100 = well-rested
    bladder: int = 20  # 0 = fine, 100 = urgent

    # Tracking when player last did self-care
    last_meal_time: str = "08:00"
    last_shower_time: str = "07:00"
    last_sleep_time: str = "23:00"

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'hunger': self.hunger,
            'hygiene': self.hygiene,
            'energy': self.energy,
            'bladder': self.bladder,
            'last_meal_time': self.last_meal_time,
            'last_shower_time': self.last_shower_time,
            'last_sleep_time': self.last_sleep_time
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SelfCareState':
        """Deserialize from dictionary"""
        return cls(
            hunger=data.get('hunger', 80),
            hygiene=data.get('hygiene', 85),
            energy=data.get('energy', 75),
            bladder=data.get('bladder', 20),
            last_meal_time=data.get('last_meal_time', '08:00'),
            last_shower_time=data.get('last_shower_time', '07:00'),
            last_sleep_time=data.get('last_sleep_time', '23:00')
        )


class SelfCareSystem:
    """Manages player's basic needs and self-care actions"""

    # Time costs for actions (in minutes)
    ACTION_TIME_COSTS = {
        # Self-care actions
        'eat_meal': 25,
        'quick_snack': 5,
        'drink_water': 2,
        'use_bathroom': 3,
        'shower': 15,
        'quick_wash': 5,
        'sleep': 480,  # 8 hours
        'nap': 90,  # 1.5 hours

        # Hypnosis study actions
        'read_book': 45,
        'study_technique': 30,
        'practice_technique': 40,
        'research_online': 30,

        # Social actions
        'deep_conversation': 60,
        'casual_chat': 20,
        'plant_suggestion': 15,

        # Activities
        'activity_short': 30,
        'activity_medium': 60,
        'activity_long': 120
    }

    # Decay rates per hour
    DECAY_RATES = {
        'hunger': 8,      # Gets hungry relatively fast
        'hygiene': 2,     # Slowly gets dirty
        'energy': 5,      # Gets tired over the day
        'bladder': 12     # Needs bathroom fairly often
    }

    @staticmethod
    def get_status_emoji(value: int, reverse: bool = False) -> str:
        """Get emoji for status level"""
        if reverse:  # For bladder (lower is better)
            if value >= 80: return '🚨'
            if value >= 60: return '⚠️'
            if value >= 40: return '😐'
            return '✅'
        else:  # For hunger, hygiene, energy (higher is better)
            if value >= 80: return '✅'
            if value >= 60: return '😊'
            if value >= 40: return '😐'
            if value >= 20: return '⚠️'
            return '🚨'

    @staticmethod
    def get_status_color(value: int, reverse: bool = False) -> str:
        """Get color for status level"""
        if reverse:  # For bladder
            if value >= 80: return '#f44336'  # Red (urgent)
            if value >= 60: return '#ff9800'  # Orange
            if value >= 40: return '#ffc107'  # Yellow
            return '#4caf50'  # Green
        else:
            if value >= 80: return '#4caf50'  # Green
            if value >= 60: return '#8bc34a'  # Light green
            if value >= 40: return '#ffc107'  # Yellow
            if value >= 20: return '#ff9800'  # Orange
            return '#f44336'  # Red

    @staticmethod
    def decay_needs(self_care: SelfCareState, hours_passed: float) -> Dict[str, str]:
        """
        Decay all needs based on time passed
        Returns dict of warnings
        """
        warnings = {}

        # Hunger decreases
        old_hunger = self_care.hunger
        self_care.hunger = max(0, self_care.hunger - int(SelfCareSystem.DECAY_RATES['hunger'] * hours_passed))
        if old_hunger > 30 and self_care.hunger <= 30:
            warnings['hunger'] = "🍔 You're getting really hungry..."
        elif old_hunger > 10 and self_care.hunger <= 10:
            warnings['hunger'] = "🚨 You're starving! You need to eat soon!"

        # Hygiene decreases
        old_hygiene = self_care.hygiene
        self_care.hygiene = max(0, self_care.hygiene - int(SelfCareSystem.DECAY_RATES['hygiene'] * hours_passed))
        if old_hygiene > 40 and self_care.hygiene <= 40:
            warnings['hygiene'] = "🚿 You're starting to feel grimy..."
        elif old_hygiene > 20 and self_care.hygiene <= 20:
            warnings['hygiene'] = "⚠️ You really need a shower!"

        # Energy decreases
        old_energy = self_care.energy
        self_care.energy = max(0, self_care.energy - int(SelfCareSystem.DECAY_RATES['energy'] * hours_passed))
        if old_energy > 30 and self_care.energy <= 30:
            warnings['energy'] = "😴 You're getting tired..."
        elif old_energy > 10 and self_care.energy <= 10:
            warnings['energy'] = "💤 You're exhausted! You need sleep!"

        # Bladder increases
        old_bladder = self_care.bladder
        self_care.bladder = min(100, self_care.bladder + int(SelfCareSystem.DECAY_RATES['bladder'] * hours_passed))
        if old_bladder < 70 and self_care.bladder >= 70:
            warnings['bladder'] = "🚻 You need to use the bathroom soon..."
        elif old_bladder < 90 and self_care.bladder >= 90:
            warnings['bladder'] = "🚨 You REALLY need a bathroom!"

        return warnings

    @staticmethod
    def perform_action(game_state, action: str, current_time: str) -> Dict[str, any]:
        """
        Perform a self-care action
        Returns: {'success': bool, 'message': str, 'time_cost': int, 'effects': dict}
        """
        self_care = game_state.player.self_care

        result = {
            'success': False,
            'message': '',
            'time_cost': 0,
            'effects': {}
        }

        if action == 'eat_meal':
            # Check if player has food
            if game_state.player.food_meals <= 0:
                result['message'] = "You're out of meals! You need to go grocery shopping."
                return result

            if self_care.hunger >= 95:
                result['message'] = "You're too full to eat right now!"
                return result

            # Consume a meal from inventory
            game_state.player.food_meals -= 1

            self_care.hunger = min(100, self_care.hunger + 50)
            self_care.energy = min(100, self_care.energy + 5)
            self_care.last_meal_time = current_time
            result['success'] = True
            result['message'] = f"🍽️ You ate a satisfying meal. (+50 hunger, +5 energy)\n📦 Meals remaining: {game_state.player.food_meals}"
            result['time_cost'] = SelfCareSystem.ACTION_TIME_COSTS['eat_meal']
            result['effects'] = {'hunger': 50, 'energy': 5}

        elif action == 'quick_snack':
            # Check if player has snacks
            if game_state.player.food_snacks <= 0:
                result['message'] = "You're out of snacks! You need to go grocery shopping."
                return result

            if self_care.hunger >= 90:
                result['message'] = "You're not hungry enough for a snack."
                return result

            # Consume a snack from inventory
            game_state.player.food_snacks -= 1

            self_care.hunger = min(100, self_care.hunger + 20)
            result['success'] = True
            result['message'] = f"🍎 You grabbed a quick snack. (+20 hunger)\n📦 Snacks remaining: {game_state.player.food_snacks}"
            result['time_cost'] = SelfCareSystem.ACTION_TIME_COSTS['quick_snack']
            result['effects'] = {'hunger': 20}

        elif action == 'drink_water':
            self_care.bladder = min(100, self_care.bladder + 15)
            self_care.energy = min(100, self_care.energy + 2)
            result['success'] = True
            result['message'] = "💧 You drank some water. Refreshing! (+2 energy)"
            result['time_cost'] = SelfCareSystem.ACTION_TIME_COSTS['drink_water']
            result['effects'] = {'energy': 2, 'bladder': 15}

        elif action == 'use_bathroom':
            if self_care.bladder < 30:
                result['message'] = "You don't need to go right now."
                return result
            self_care.bladder = 0
            result['success'] = True
            result['message'] = "🚻 Relief! (-100 bladder)"
            result['time_cost'] = SelfCareSystem.ACTION_TIME_COSTS['use_bathroom']
            result['effects'] = {'bladder': -100}

        elif action == 'shower':
            if self_care.hygiene >= 95:
                result['message'] = "You just showered! You're already clean."
                return result
            self_care.hygiene = 100
            self_care.energy = min(100, self_care.energy + 10)
            self_care.last_shower_time = current_time
            result['success'] = True
            result['message'] = "🚿 You took a refreshing shower. You feel great! (+100 hygiene, +10 energy)"
            result['time_cost'] = SelfCareSystem.ACTION_TIME_COSTS['shower']
            result['effects'] = {'hygiene': 100, 'energy': 10}

        elif action == 'quick_wash':
            self_care.hygiene = min(100, self_care.hygiene + 30)
            result['success'] = True
            result['message'] = "💧 You washed your hands and face. (+30 hygiene)"
            result['time_cost'] = SelfCareSystem.ACTION_TIME_COSTS['quick_wash']
            result['effects'] = {'hygiene': 30}

        elif action == 'sleep':
            if self_care.energy >= 80:
                result['message'] = "You're not tired enough to sleep yet."
                return result
            self_care.energy = 100
            self_care.hunger = max(0, self_care.hunger - 30)  # Get hungry while sleeping
            self_care.hygiene = max(0, self_care.hygiene - 5)
            self_care.last_sleep_time = current_time
            result['success'] = True
            result['message'] = "💤 You got a full night's sleep. (+100 energy, -30 hunger)"
            result['time_cost'] = SelfCareSystem.ACTION_TIME_COSTS['sleep']
            result['effects'] = {'energy': 100, 'hunger': -30, 'hygiene': -5}

        elif action == 'nap':
            if self_care.energy >= 70:
                result['message'] = "You're not tired enough for a nap."
                return result
            self_care.energy = min(100, self_care.energy + 40)
            self_care.hunger = max(0, self_care.hunger - 10)
            result['success'] = True
            result['message'] = "😴 You took a quick nap. (+40 energy, -10 hunger)"
            result['time_cost'] = SelfCareSystem.ACTION_TIME_COSTS['nap']
            result['effects'] = {'energy': 40, 'hunger': -10}

        return result

    @staticmethod
    def get_gameplay_modifiers(self_care: SelfCareState) -> Dict[str, any]:
        """
        Get gameplay modifiers based on self-care state
        Returns bonuses/penalties for various game mechanics
        """
        modifiers = {
            'sp_gain_multiplier': 1.0,
            'rapport_gain_penalty': 0,
            'success_rate_penalty': 0,
            'warnings': []
        }

        # Low hunger penalties
        if self_care.hunger < 20:
            modifiers['sp_gain_multiplier'] *= 0.5  # -50% SP gain
            modifiers['success_rate_penalty'] += 10  # -10% success rate
            modifiers['warnings'].append("🚨 Starving: -50% SP gain, -10% success rate")
        elif self_care.hunger < 40:
            modifiers['sp_gain_multiplier'] *= 0.75  # -25% SP gain
            modifiers['warnings'].append("⚠️ Hungry: -25% SP gain")

        # Low hygiene penalties
        if self_care.hygiene < 30:
            modifiers['rapport_gain_penalty'] += 2  # Harder to build rapport
            modifiers['warnings'].append("🚨 Filthy: People notice... -2 rapport gain")
        elif self_care.hygiene < 50:
            modifiers['rapport_gain_penalty'] += 1
            modifiers['warnings'].append("⚠️ Grimy: -1 rapport gain")

        # Low energy penalties
        if self_care.energy < 15:
            modifiers['sp_gain_multiplier'] *= 0.6  # -40% SP gain
            modifiers['success_rate_penalty'] += 15  # -15% success rate
            modifiers['warnings'].append("💤 Exhausted: -40% SP gain, -15% success rate")
        elif self_care.energy < 30:
            modifiers['sp_gain_multiplier'] *= 0.8  # -20% SP gain
            modifiers['success_rate_penalty'] += 5
            modifiers['warnings'].append("😴 Tired: -20% SP gain, -5% success rate")

        # High bladder penalties
        if self_care.bladder >= 90:
            modifiers['success_rate_penalty'] += 20  # Very distracted!
            modifiers['warnings'].append("🚨 URGENT: Can't focus! -20% success rate")
        elif self_care.bladder >= 70:
            modifiers['success_rate_penalty'] += 10
            modifiers['warnings'].append("🚻 Distracted: -10% success rate")

        return modifiers

    @staticmethod
    def can_perform_action(self_care: SelfCareState, action_type: str) -> tuple[bool, str]:
        """
        Check if player can perform an action given their current state
        Returns: (can_do, reason_if_not)
        """
        # Can't do mentally demanding tasks if exhausted
        if action_type in ['study', 'plant_phs', 'deep_hypnosis']:
            if self_care.energy < 10:
                return False, "💤 You're too exhausted! You need to sleep first."

        # Can't do social interactions if too unhygienic
        if action_type == 'social':
            if self_care.hygiene < 15:
                return False, "🚿 You're too dirty! People will be disgusted. Take a shower first!"

        # Extreme bladder urgency prevents everything
        if self_care.bladder >= 95:
            return False, "🚨 You MUST use the bathroom RIGHT NOW!"

        return True, ""
