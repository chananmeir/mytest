"""
Money and Gift System - Economy, shopping, and gift-giving mechanics
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import random


@dataclass
class Gift:
    """Represents a gift that can be bought and given"""
    gift_id: str
    name: str
    description: str
    cost: int  # $ cost to purchase
    category: str  # 'clothing', 'comfort', 'luxury', 'practical', 'romantic'

    # Effects when given
    rapport_gain: int = 0
    resistance_change: int = 0
    trust_gain: int = 0  # Builds trust
    emotional_outcome: Optional[str] = None

    # Special effects
    suggestibility_bonus: int = 0  # Permanent suggestibility modifier
    unlocks_content: Optional[str] = None  # Unlocks special scenes/options

    # Display
    icon: str = "🎁"
    success_messages: List[str] = None

    def __post_init__(self):
        if self.success_messages is None:
            self.success_messages = [f"They appreciate the {self.name}."]


@dataclass
class Job:
    """Represents a job opportunity to earn money"""
    job_id: str
    name: str
    description: str
    duration_minutes: int
    pay: int  # Money earned
    sp_cost: int = 0  # SP cost to perform (0 = free)
    requires_skill_level: str = "novice"  # Skill level required

    # Outcomes
    energy_cost: int = 0  # Future: fatigue system
    reputation_gain: int = 0  # Future: reputation system

    # Display
    icon: str = "💼"
    success_messages: List[str] = None

    def __post_init__(self):
        if self.success_messages is None:
            self.success_messages = [f"You completed {self.name} and earned ${self.pay}."]


@dataclass
class GroceryItem:
    """Represents food/groceries that can be purchased"""
    item_id: str
    name: str
    description: str
    cost: int  # $ cost to purchase
    category: str  # 'meal', 'snack', 'bulk'

    # What you get
    meals_qty: int = 0  # How many meals this provides
    snacks_qty: int = 0  # How many snacks this provides

    # Display
    icon: str = "🛒"

    def __post_init__(self):
        pass


class MoneySystem:
    """Manages money, shopping, gifts, and economy"""

    # ==================== GIFT CATALOG ====================

    # Cheap Gifts ($10-30)
    CHEAP_GIFTS = {
        'flowers': Gift(
            gift_id='flowers',
            name='Bouquet of Flowers',
            description='A beautiful arrangement. Simple but thoughtful.',
            cost=15,
            category='romantic',
            rapport_gain=2,
            icon='💐',
            success_messages=[
                "Their face lights up when they see the flowers.",
                "They smile and find a vase to put them in.",
                "A sweet gesture that they clearly appreciate."
            ]
        ),
        'chocolates': Gift(
            gift_id='chocolates',
            name='Box of Chocolates',
            description='Quality chocolates. A classic gift.',
            cost=20,
            category='comfort',
            rapport_gain=2,
            emotional_outcome='happy',
            icon='🍫',
            success_messages=[
                "They can't resist trying one immediately.",
                "Their favorite! You remembered well.",
                "Sweet treats for someone sweet."
            ]
        ),
        'coffee': Gift(
            gift_id='coffee',
            name='Fancy Coffee Beans',
            description='Premium coffee. Perfect for coffee lovers.',
            cost=25,
            category='practical',
            rapport_gain=1,
            trust_gain=1,
            icon='☕',
            success_messages=[
                "Perfect! They've been wanting to try this blend.",
                "They immediately want to brew a cup.",
                "A practical gift that shows you pay attention."
            ]
        ),
        'candle': Gift(
            gift_id='candle',
            name='Scented Candle',
            description='Relaxing scents. Creates a calming atmosphere.',
            cost=18,
            category='comfort',
            rapport_gain=1,
            emotional_outcome='relaxed',
            icon='🕯️',
            success_messages=[
                "They love the scent. So relaxing.",
                "They light it immediately. The room fills with fragrance.",
                "A small touch of luxury for their space."
            ]
        ),
        'book': Gift(
            gift_id='book',
            name='Bestselling Novel',
            description='A popular book you think they\'ll enjoy.',
            cost=30,
            category='comfort',
            rapport_gain=2,
            trust_gain=1,
            icon='📚',
            success_messages=[
                "They've been wanting to read this!",
                "A thoughtful choice that shows you know their tastes.",
                "They promise to discuss it with you once they finish."
            ]
        )
    }

    # Medium Gifts ($50-100)
    MEDIUM_GIFTS = {
        'casual_outfit': Gift(
            gift_id='casual_outfit',
            name='Casual Outfit',
            description='A cute, comfortable outfit. Slightly revealing.',
            cost=60,
            category='clothing',
            rapport_gain=3,
            resistance_change=-5,
            suggestibility_bonus=3,
            icon='👗',
            success_messages=[
                "They love the style! It's perfect for them.",
                "They try it on immediately. It fits great.",
                "Your fashion sense is impressive. They trust your taste."
            ]
        ),
        'jewelry': Gift(
            gift_id='jewelry',
            name='Delicate Jewelry',
            description='A necklace or bracelet. Elegant and personal.',
            cost=80,
            category='romantic',
            rapport_gain=4,
            trust_gain=2,
            emotional_outcome='touched',
            icon='💎',
            success_messages=[
                "They're touched by such a personal gift.",
                "They put it on immediately and admire it.",
                "A gift they'll treasure and wear often."
            ]
        ),
        'perfume': Gift(
            gift_id='perfume',
            name='Designer Perfume',
            description='A sophisticated scent. Intimate and personal.',
            cost=75,
            category='luxury',
            rapport_gain=3,
            resistance_change=-3,
            emotional_outcome='confident',
            icon='🌸',
            success_messages=[
                "They spray a bit on their wrist. Intoxicating.",
                "A scent they'll associate with you now.",
                "Such a personal, intimate gift."
            ]
        ),
        'workout_gear': Gift(
            gift_id='workout_gear',
            name='Workout Clothes',
            description='Fitted athletic wear. Functional and flattering.',
            cost=65,
            category='clothing',
            rapport_gain=2,
            suggestibility_bonus=2,
            icon='🏃',
            success_messages=[
                "Perfect for the gym! Comfortable and stylish.",
                "They can't wait to work out in it.",
                "Supportive in their fitness goals."
            ]
        ),
        'spa_set': Gift(
            gift_id='spa_set',
            name='Luxury Spa Set',
            description='Bath products for pampering. Relaxing and sensual.',
            cost=70,
            category='comfort',
            rapport_gain=3,
            resistance_change=-5,
            emotional_outcome='relaxed',
            icon='🛁',
            success_messages=[
                "They're so excited to use these!",
                "A chance to relax and think of you.",
                "Self-care that you're encouraging."
            ]
        )
    }

    # Expensive Gifts ($150-300)
    EXPENSIVE_GIFTS = {
        'designer_dress': Gift(
            gift_id='designer_dress',
            name='Designer Dress',
            description='A stunning, form-fitting dress. Elegant and revealing.',
            cost=200,
            category='clothing',
            rapport_gain=5,
            resistance_change=-10,
            suggestibility_bonus=8,
            emotional_outcome='confident',
            unlocks_content='special_date',
            icon='👗',
            success_messages=[
                "Their eyes widen. This is expensive and beautiful.",
                "They try it on. It's perfect. You have excellent taste.",
                "They feel amazing in it. They want to wear it for you.",
                "A transformative gift. They see themselves differently now."
            ]
        ),
        'lingerie_set': Gift(
            gift_id='lingerie_set',
            name='Elegant Lingerie',
            description='Beautiful, delicate lingerie. Very intimate gift.',
            cost=150,
            category='clothing',
            rapport_gain=6,
            resistance_change=-15,
            suggestibility_bonus=10,
            emotional_outcome='desired',
            unlocks_content='intimate_scenes',
            icon='💋',
            success_messages=[
                "They blush deeply. This is very intimate.",
                "They can't believe you bought this for them.",
                "A line has been crossed. The relationship has changed.",
                "They promise to model it for you sometime..."
            ]
        ),
        'tech_gift': Gift(
            gift_id='tech_gift',
            name='Latest Tech Gadget',
            description='High-end electronics. Impressive and expensive.',
            cost=250,
            category='luxury',
            rapport_gain=6,
            trust_gain=5,
            icon='📱',
            success_messages=[
                "This is way too much! But they're thrilled.",
                "You really care about them to spend this much.",
                "A generous gift that shows your commitment.",
                "They can't stop thanking you."
            ]
        ),
        'vacation': Gift(
            gift_id='vacation',
            name='Weekend Getaway',
            description='A trip together. Romantic and memorable.',
            cost=300,
            category='romantic',
            rapport_gain=8,
            resistance_change=-20,
            emotional_outcome='romantic',
            unlocks_content='vacation_scenes',
            icon='✈️',
            success_messages=[
                "A weekend away together? They're ecstatic!",
                "Uninterrupted time together. Just you two.",
                "This will bring you so much closer.",
                "They're already planning what to pack."
            ]
        )
    }

    # Combine all gifts
    ALL_GIFTS = {
        **CHEAP_GIFTS,
        **MEDIUM_GIFTS,
        **EXPENSIVE_GIFTS
    }

    # ==================== GROCERY CATALOG ====================

    GROCERIES = {
        # Individual meals/snacks
        'single_meal': GroceryItem(
            item_id='single_meal',
            name='Ready Meal',
            description='A single prepared meal. Quick and convenient.',
            cost=8,
            category='meal',
            meals_qty=1,
            icon='🍱'
        ),
        'snack_pack': GroceryItem(
            item_id='snack_pack',
            name='Snack Pack',
            description='A pack of 3 snacks. Chips, granola bars, fruit.',
            cost=5,
            category='snack',
            snacks_qty=3,
            icon='🍿'
        ),

        # Bulk purchases (better value)
        'meal_pack_5': GroceryItem(
            item_id='meal_pack_5',
            name='Meal Pack (5)',
            description='5 prepared meals. Saves time and money.',
            cost=30,  # $6 each (save $2 per meal)
            category='bulk',
            meals_qty=5,
            icon='🍽️'
        ),
        'meal_pack_10': GroceryItem(
            item_id='meal_pack_10',
            name='Meal Pack (10)',
            description='10 prepared meals. Best value for meal prep.',
            cost=50,  # $5 each (save $3 per meal)
            category='bulk',
            meals_qty=10,
            icon='📦'
        ),
        'snack_box': GroceryItem(
            item_id='snack_box',
            name='Snack Box (12)',
            description='A variety box of 12 snacks. Stock up!',
            cost=15,  # $1.25 each (save money on bulk)
            category='bulk',
            snacks_qty=12,
            icon='🎁'
        ),

        # Weekly groceries
        'weekly_groceries': GroceryItem(
            item_id='weekly_groceries',
            name='Weekly Groceries',
            description='A full week of meals and snacks. 7 meals + 10 snacks.',
            cost=60,
            category='bulk',
            meals_qty=7,
            snacks_qty=10,
            icon='🛒'
        ),
    }

    # ==================== JOB OPPORTUNITIES ====================

    JOBS = {
        'odd_jobs': Job(
            job_id='odd_jobs',
            name='Odd Jobs',
            description='Help neighbors with various tasks. Quick money.',
            duration_minutes=60,
            pay=30,
            icon='🔧',
            success_messages=[
                "A few hours of work for some quick cash.",
                "Handyman work pays the bills.",
                "Honest work, honest pay."
            ]
        ),
        'food_delivery': Job(
            job_id='food_delivery',
            name='Food Delivery',
            description='Deliver food orders around town.',
            duration_minutes=120,
            pay=60,
            icon='🚗',
            success_messages=[
                "A few hours of driving and delivering. Good tips today!",
                "Steady work. Puts money in the bank.",
                "The gig economy provides."
            ]
        ),
        'retail_shift': Job(
            job_id='retail_shift',
            name='Retail Shift',
            description='Work a shift at a local store.',
            duration_minutes=240,
            pay=100,
            icon='🏪',
            success_messages=[
                "A full shift done. Tiring but necessary.",
                "Retail isn't glamorous but it pays.",
                "Another day, another dollar."
            ]
        ),
        'tutoring': Job(
            job_id='tutoring',
            name='Private Tutoring',
            description='Tutor students. Use your knowledge.',
            duration_minutes=90,
            pay=75,
            requires_skill_level='intermediate',
            icon='📖',
            success_messages=[
                "Helping students learn and earning money. Win-win.",
                "Your skills are valuable. People will pay for them.",
                "Teaching is rewarding in more ways than one."
            ]
        ),
        'freelance': Job(
            job_id='freelance',
            name='Freelance Work',
            description='Online freelance projects. Work from anywhere.',
            duration_minutes=180,
            pay=120,
            requires_skill_level='intermediate',
            icon='💻',
            success_messages=[
                "Completed a project remotely. Solid pay.",
                "The freedom of freelancing has its perks.",
                "Your expertise is in demand."
            ]
        ),
        'consulting': Job(
            job_id='consulting',
            name='Consultation Session',
            description='Professional consulting. Premium pay.',
            duration_minutes=120,
            pay=200,
            sp_cost=1,
            requires_skill_level='expert',
            icon='💼',
            success_messages=[
                "Your advice is worth good money.",
                "Consulting pays very well when you're skilled.",
                "People seek your expertise and pay premium rates."
            ]
        )
    }

    # ==================== METHODS ====================

    @staticmethod
    def get_gifts_in_budget(max_cost: int) -> List[Gift]:
        """Get all gifts the player can afford"""
        return [gift for gift in MoneySystem.ALL_GIFTS.values() if gift.cost <= max_cost]

    @staticmethod
    def get_gifts_by_category(category: str) -> List[Gift]:
        """Get gifts by category"""
        return [gift for gift in MoneySystem.ALL_GIFTS.values() if gift.category == category]

    @staticmethod
    def give_gift(game_state, character_name: str, gift: Gift) -> Dict:
        """
        Give a gift to a character

        Returns dict with results
        """
        from systems.hypnosis import HypnosisSystem

        character = game_state.get_character(character_name)
        if not character:
            return {'success': False, 'error': 'Character not found'}

        # Check if player can afford it
        if game_state.player.money < gift.cost:
            return {'success': False, 'error': 'Not enough money'}

        # Deduct cost
        game_state.player.money -= gift.cost

        results = {
            'success': True,
            'gift_name': gift.name,
            'message': random.choice(gift.success_messages),
            'changes': []
        }

        # Apply rapport gain
        if gift.rapport_gain > 0:
            rapport_msg = HypnosisSystem.build_rapport(
                game_state,
                character_name,
                gift.rapport_gain,
                f"from receiving {gift.name}"
            )
            results['changes'].append(rapport_msg)

        # Apply resistance change
        if gift.resistance_change != 0:
            character.resistance = max(0, min(100, character.resistance + gift.resistance_change))
            results['changes'].append(
                f"{character.name}'s resistance: {gift.resistance_change:+d}% ({character.resistance}%)"
            )

        # Apply trust gain
        if gift.trust_gain > 0:
            results['changes'].append(f"Trust increased by {gift.trust_gain}")

        # Apply emotional outcome
        if gift.emotional_outcome:
            emotion_msg = HypnosisSystem.change_emotional_state(
                game_state,
                character_name,
                gift.emotional_outcome,
                f"from receiving {gift.name}"
            )
            results['changes'].append(emotion_msg)

        # Apply permanent suggestibility bonus
        if gift.suggestibility_bonus > 0:
            # Add to character's clothing effects or create permanent modifier
            results['changes'].append(
                f"✨ Permanent suggestibility +{gift.suggestibility_bonus}% when wearing this!"
            )

        # Unlock special content
        if gift.unlocks_content:
            results['changes'].append(
                f"🔓 Unlocked: {gift.unlocks_content.replace('_', ' ').title()}"
            )

        # Record memory
        from systems.memory import MemorySystem
        memory_content = f"You gave them {gift.name}. {results['message']}"
        MemorySystem.record_important_event(
            character,
            memory_content,
            importance=7,
            related_characters=['Player']
        )

        return results

    @staticmethod
    def buy_groceries(game_state, grocery_item: GroceryItem) -> Dict:
        """
        Buy groceries to stock up on food

        Returns dict with results
        """
        # Check if player can afford it
        if game_state.player.money < grocery_item.cost:
            return {'success': False, 'error': 'Not enough money'}

        # Deduct cost
        game_state.player.money -= grocery_item.cost

        # Add food to inventory
        game_state.player.food_meals += grocery_item.meals_qty
        game_state.player.food_snacks += grocery_item.snacks_qty

        results = {
            'success': True,
            'item_name': grocery_item.name,
            'message': f"Purchased {grocery_item.name}!",
            'changes': []
        }

        # Report what was added
        if grocery_item.meals_qty > 0:
            results['changes'].append(f"🍽️ +{grocery_item.meals_qty} meals (now {game_state.player.food_meals})")
        if grocery_item.snacks_qty > 0:
            results['changes'].append(f"🍿 +{grocery_item.snacks_qty} snacks (now {game_state.player.food_snacks})")

        results['changes'].append(f"💰 Spent ${grocery_item.cost} (${game_state.player.money} remaining)")

        return results

    @staticmethod
    def do_job(game_state, job: Job) -> Dict:
        """
        Perform a job to earn money

        Returns dict with results
        """
        # Check SP cost
        if job.sp_cost > game_state.player.suggestion_points:
            return {'success': False, 'error': 'Not enough SP'}

        # Deduct SP if needed
        if job.sp_cost > 0:
            game_state.player.suggestion_points -= job.sp_cost

        # Earn money
        game_state.player.money += job.pay
        game_state.player.total_money_earned += job.pay

        # Advance time and get warnings
        time_warnings = game_state.advance_time_with_needs(job.duration_minutes)
        time_msgs = list(time_warnings.values())

        results = {
            'success': True,
            'job_name': job.name,
            'pay': job.pay,
            'message': random.choice(job.success_messages),
            'duration': job.duration_minutes,
            'changes': [
                f"💵 Earned ${job.pay}",
                f"💰 Total money: ${game_state.player.money}",
                *time_msgs
            ]
        }

        return results

    @staticmethod
    def add_money(game_state, amount: int, reason: str = ""):
        """Add money to player with tracking"""
        game_state.player.money += amount
        if amount > 0:
            game_state.player.total_money_earned += amount

    @staticmethod
    def spend_money(game_state, amount: int) -> bool:
        """
        Spend money (returns False if not enough)
        """
        if game_state.player.money >= amount:
            game_state.player.money -= amount
            return True
        return False

    @staticmethod
    def get_money_status(game_state) -> Dict:
        """Get player's financial status"""
        return {
            'current_money': game_state.player.money,
            'total_earned': game_state.player.total_money_earned,
            'can_afford_basic': game_state.player.money >= 20,
            'can_afford_medium': game_state.player.money >= 50,
            'can_afford_expensive': game_state.player.money >= 150,
            'needs_money': game_state.player.money < 50
        }
