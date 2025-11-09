"""
Goal System - Open-ended objectives, milestones, and achievements
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Goal:
    """Represents a goal or objective"""
    goal_id: str
    goal_name: str
    goal_type: str  # 'daily', 'weekly', 'milestone', 'achievement', 'challenge'
    description: str
    progress: int = 0
    target: int = 1
    completed: bool = False
    reward_sp: int = 0
    reward_description: str = ""
    category: str = "general"  # 'hypnosis', 'relationship', 'exploration', 'stealth'
    repeatable: bool = False
    hidden: bool = False  # Hidden until unlocked


class GoalSystem:
    """Manages goals, achievements, and progression tracking"""

    # Daily Goals (reset every day)
    DAILY_GOALS = {
        'daily_conversation': Goal(
            goal_id='daily_conversation',
            goal_name='Meaningful Conversation',
            goal_type='daily',
            description='Have a conversation with any character',
            target=1,
            reward_sp=1,
            reward_description='+1 SP for daily interaction',
            category='relationship',
            repeatable=True
        ),
        'daily_rapport': Goal(
            goal_id='daily_rapport',
            goal_name='Build Connection',
            goal_type='daily',
            description='Increase rapport by 2+ points with any character',
            target=2,
            reward_sp=1,
            reward_description='+1 SP for building relationships',
            category='relationship',
            repeatable=True
        ),
        'daily_suggestion': Goal(
            goal_id='daily_suggestion',
            goal_name='Plant a Suggestion',
            goal_type='daily',
            description='Successfully plant a post-hypnotic suggestion',
            target=1,
            reward_sp=2,
            reward_description='+2 SP for active hypnosis',
            category='hypnosis',
            repeatable=True
        ),
        'daily_time': Goal(
            goal_id='daily_time',
            goal_name='Pass the Day',
            goal_type='daily',
            description='Advance time by at least 4 hours',
            target=240,  # 240 minutes = 4 hours
            reward_sp=1,
            reward_description='+1 SP for progressing time',
            category='general',
            repeatable=True
        )
    }

    # Weekly Goals (reset every 7 days)
    WEEKLY_GOALS = {
        'weekly_milestone': Goal(
            goal_id='weekly_milestone',
            goal_name='Rapport Milestone',
            goal_type='weekly',
            description='Reach a rapport milestone (5, 10, 15, or 20) with any character',
            target=1,
            reward_sp=3,
            reward_description='+3 SP for relationship milestone',
            category='relationship',
            repeatable=True
        ),
        'weekly_unlock': Goal(
            goal_id='weekly_unlock',
            goal_name='Expand Access',
            goal_type='weekly',
            description='Unlock a new location',
            target=1,
            reward_sp=3,
            reward_description='+3 SP for exploration',
            category='exploration',
            repeatable=True
        ),
        'weekly_reinforce': Goal(
            goal_id='weekly_reinforce',
            goal_name='Strengthen Control',
            goal_type='weekly',
            description='Reinforce 3 existing suggestions',
            target=3,
            reward_sp=2,
            reward_description='+2 SP for maintaining influence',
            category='hypnosis',
            repeatable=True
        ),
        'weekly_stealth': Goal(
            goal_id='weekly_stealth',
            goal_name='Stay Under the Radar',
            goal_type='weekly',
            description='Keep all character suspicion levels below 50%',
            target=1,
            reward_sp=3,
            reward_description='+3 SP for staying undetected',
            category='stealth',
            repeatable=True
        )
    }

    # Achievement Goals (one-time, permanent)
    ACHIEVEMENTS = {
        # Hypnosis Achievements
        'first_suggestion': Goal(
            goal_id='first_suggestion',
            goal_name='First Steps',
            goal_type='achievement',
            description='Plant your first post-hypnotic suggestion',
            target=1,
            reward_sp=2,
            reward_description='🏆 Achievement Unlocked!',
            category='hypnosis'
        ),
        'suggestions_10': Goal(
            goal_id='suggestions_10',
            goal_name='Apprentice Hypnotist',
            goal_type='achievement',
            description='Plant 10 suggestions',
            target=10,
            reward_sp=5,
            reward_description='🏆 Hypnosis Mastery Growing',
            category='hypnosis'
        ),
        'suggestions_50': Goal(
            goal_id='suggestions_50',
            goal_name='Master Hypnotist',
            goal_type='achievement',
            description='Plant 50 suggestions',
            target=50,
            reward_sp=10,
            reward_description='🏆 True Master of Hypnosis',
            category='hypnosis'
        ),
        'first_activation': Goal(
            goal_id='first_activation',
            goal_name='It Works!',
            goal_type='achievement',
            description='Successfully activate a suggestion',
            target=1,
            reward_sp=3,
            reward_description='🏆 Witness Your Power',
            category='hypnosis'
        ),
        'activations_25': Goal(
            goal_id='activations_25',
            goal_name='Puppet Master',
            goal_type='achievement',
            description='Activate 25 suggestions',
            target=25,
            reward_sp=8,
            reward_description='🏆 Strings Attached',
            category='hypnosis'
        ),
        'max_slots': Goal(
            goal_id='max_slots',
            goal_name='Mind Full',
            goal_type='achievement',
            description='Have 3 active PHS on one character',
            target=3,
            reward_sp=5,
            reward_description='🏆 Complete Mental Occupation',
            category='hypnosis'
        ),

        # Relationship Achievements
        'rapport_10_any': Goal(
            goal_id='rapport_10_any',
            goal_name='Trusted Friend',
            goal_type='achievement',
            description='Reach rapport 10 with any character',
            target=10,
            reward_sp=3,
            reward_description='🏆 Building Trust',
            category='relationship'
        ),
        'rapport_20_any': Goal(
            goal_id='rapport_20_any',
            goal_name='Unbreakable Bond',
            goal_type='achievement',
            description='Reach rapport 20 with any character',
            target=20,
            reward_sp=5,
            reward_description='🏆 Complete Trust Achieved',
            category='relationship'
        ),
        'rapport_10_all': Goal(
            goal_id='rapport_10_all',
            goal_name='Social Butterfly',
            goal_type='achievement',
            description='Reach rapport 10 with everyone',
            target=7,  # 7 characters
            reward_sp=10,
            reward_description='🏆 Everyone Trusts You',
            category='relationship'
        ),
        'rapport_20_all': Goal(
            goal_id='rapport_20_all',
            goal_name='Family Favorite',
            goal_type='achievement',
            description='Reach rapport 20 with everyone',
            target=7,
            reward_sp=20,
            reward_description='🏆 Complete Family Influence',
            category='relationship'
        ),

        # Exploration Achievements
        'visit_all_public': Goal(
            goal_id='visit_all_public',
            goal_name='Explorer',
            goal_type='achievement',
            description='Visit all public locations',
            target=5,  # 5 public locations
            reward_sp=3,
            reward_description='🏆 Know the Territory',
            category='exploration'
        ),
        'unlock_all_private': Goal(
            goal_id='unlock_all_private',
            goal_name='All Access Pass',
            goal_type='achievement',
            description='Unlock all private locations',
            target=8,  # 8 private locations
            reward_sp=15,
            reward_description='🏆 Complete Access',
            category='exploration'
        ),
        'meet_everyone': Goal(
            goal_id='meet_everyone',
            goal_name='Social Network',
            goal_type='achievement',
            description='Meet all characters',
            target=7,
            reward_sp=5,
            reward_description='🏆 Full Family Circle',
            category='exploration'
        ),

        # Stealth Achievements
        'low_suspicion_30days': Goal(
            goal_id='low_suspicion_30days',
            goal_name='Shadow Operator',
            goal_type='achievement',
            description='Keep suspicion below 25% for 30 days',
            target=30,
            reward_sp=10,
            reward_description='🏆 Undetected for a Month',
            category='stealth',
            hidden=True
        ),
        'defensive_phs': Goal(
            goal_id='defensive_phs',
            goal_name='Strategic Defense',
            goal_type='achievement',
            description='Use a defensive PHS to lower suspicion',
            target=1,
            reward_sp=5,
            reward_description='🏆 Clever Cover-Up',
            category='stealth'
        ),
        'prevent_confrontation': Goal(
            goal_id='prevent_confrontation',
            goal_name='Crisis Averted',
            goal_type='achievement',
            description='Lower someone\'s suspicion from 80%+ to below 50%',
            target=1,
            reward_sp=8,
            reward_description='🏆 Master Manipulator',
            category='stealth',
            hidden=True
        )
    }

    # Character Milestones (tracked per character)
    CHARACTER_MILESTONES = {
        5: {
            'title': 'Opening Up',
            'description': 'They\'re starting to trust you',
            'reward_sp': 1
        },
        10: {
            'title': 'Trusted Confidant',
            'description': 'Private spaces may become available',
            'reward_sp': 1
        },
        15: {
            'title': 'Deep Connection',
            'description': 'They value your opinion highly',
            'reward_sp': 1
        },
        20: {
            'title': 'Complete Trust',
            'description': 'Maximum rapport achieved',
            'reward_sp': 1
        }
    }

    @staticmethod
    def initialize_goals(game_state) -> None:
        """Initialize goal tracking in game state"""
        if not hasattr(game_state, 'goals'):
            game_state.goals = {
                'daily': {},
                'weekly': {},
                'achievements': {},
                'character_milestones': {},
                'last_daily_reset': game_state.game_time.day,
                'last_weekly_reset': game_state.game_time.day,
                'total_suggestions_planted': 0,
                'total_activations': 0,
                'total_reinforcements': 0,
                'visited_locations': [],
                'low_suspicion_streak': 0
            }

            # Initialize daily goals
            for goal_id, goal_template in GoalSystem.DAILY_GOALS.items():
                game_state.goals['daily'][goal_id] = {
                    'progress': 0,
                    'target': goal_template.target,
                    'completed': False
                }

            # Initialize weekly goals
            for goal_id, goal_template in GoalSystem.WEEKLY_GOALS.items():
                game_state.goals['weekly'][goal_id] = {
                    'progress': 0,
                    'target': goal_template.target,
                    'completed': False
                }

            # Initialize achievements
            for goal_id, goal_template in GoalSystem.ACHIEVEMENTS.items():
                game_state.goals['achievements'][goal_id] = {
                    'progress': 0,
                    'target': goal_template.target,
                    'completed': False,
                    'unlocked': not goal_template.hidden
                }

            # Initialize character milestones
            for char_name in game_state.characters.keys():
                game_state.goals['character_milestones'][char_name] = {
                    'current_rapport': 0,
                    'milestones_reached': []
                }

    @staticmethod
    def check_daily_reset(game_state) -> List[str]:
        """Check if daily goals should reset"""
        messages = []
        current_day = game_state.game_time.day

        if current_day > game_state.goals['last_daily_reset']:
            # Reset daily goals
            for goal_id in game_state.goals['daily']:
                game_state.goals['daily'][goal_id] = {
                    'progress': 0,
                    'target': GoalSystem.DAILY_GOALS[goal_id].target,
                    'completed': False
                }
            game_state.goals['last_daily_reset'] = current_day
            messages.append("📋 Daily goals reset!")

        return messages

    @staticmethod
    def check_weekly_reset(game_state) -> List[str]:
        """Check if weekly goals should reset"""
        messages = []
        current_day = game_state.game_time.day
        days_since_weekly = current_day - game_state.goals['last_weekly_reset']

        if days_since_weekly >= 7:
            # Reset weekly goals
            for goal_id in game_state.goals['weekly']:
                game_state.goals['weekly'][goal_id] = {
                    'progress': 0,
                    'target': GoalSystem.WEEKLY_GOALS[goal_id].target,
                    'completed': False
                }
            game_state.goals['last_weekly_reset'] = current_day
            messages.append("📋 Weekly goals reset!")

        return messages

    @staticmethod
    def update_goal_progress(game_state, goal_id: str, goal_type: str, progress_amount: int = 1) -> Tuple[bool, Optional[str]]:
        """
        Update progress on a goal

        Returns:
            (goal_completed, reward_message)
        """
        GoalSystem.initialize_goals(game_state)

        goal_dict = game_state.goals.get(goal_type, {})
        if goal_id not in goal_dict:
            return (False, None)

        goal_data = goal_dict[goal_id]

        # Don't update if already completed (unless repeatable and reset)
        if goal_data['completed']:
            return (False, None)

        # Update progress
        goal_data['progress'] += progress_amount

        # Check completion
        if goal_data['progress'] >= goal_data['target']:
            goal_data['completed'] = True
            goal_data['progress'] = goal_data['target']  # Cap at target

            # Get goal template for reward info
            if goal_type == 'daily':
                goal_template = GoalSystem.DAILY_GOALS.get(goal_id)
            elif goal_type == 'weekly':
                goal_template = GoalSystem.WEEKLY_GOALS.get(goal_id)
            elif goal_type == 'achievements':
                goal_template = GoalSystem.ACHIEVEMENTS.get(goal_id)
            else:
                return (True, None)

            if goal_template:
                # Award SP
                if goal_template.reward_sp > 0:
                    game_state.add_sp(goal_template.reward_sp, goal_template.goal_name)

                message = f"✨ Goal Complete: {goal_template.goal_name}! {goal_template.reward_description}"
                return (True, message)

        return (False, None)

    @staticmethod
    def track_conversation(game_state) -> List[str]:
        """Track conversation for daily goal"""
        messages = []
        GoalSystem.initialize_goals(game_state)

        completed, msg = GoalSystem.update_goal_progress(game_state, 'daily_conversation', 'daily', 1)
        if completed and msg:
            messages.append(msg)

        return messages

    @staticmethod
    def track_rapport_gain(game_state, amount: int) -> List[str]:
        """Track rapport building for daily goal"""
        messages = []
        GoalSystem.initialize_goals(game_state)

        completed, msg = GoalSystem.update_goal_progress(game_state, 'daily_rapport', 'daily', amount)
        if completed and msg:
            messages.append(msg)

        return messages

    @staticmethod
    def track_suggestion_planted(game_state, character_name: str) -> List[str]:
        """Track suggestion planting for goals and achievements"""
        messages = []
        GoalSystem.initialize_goals(game_state)

        # Increment total counter
        game_state.goals['total_suggestions_planted'] += 1
        total = game_state.goals['total_suggestions_planted']

        # Daily goal
        completed, msg = GoalSystem.update_goal_progress(game_state, 'daily_suggestion', 'daily', 1)
        if completed and msg:
            messages.append(msg)

        # Achievement tracking
        achievements = [
            ('first_suggestion', 1),
            ('suggestions_10', 10),
            ('suggestions_50', 50)
        ]

        for achievement_id, target in achievements:
            if total == target:
                completed, msg = GoalSystem.update_goal_progress(game_state, achievement_id, 'achievements', target)
                if completed and msg:
                    messages.append(msg)

        # Check max slots achievement
        char = game_state.get_character(character_name)
        if char and len(char.active_phs) >= 3:
            completed, msg = GoalSystem.update_goal_progress(game_state, 'max_slots', 'achievements', 3)
            if completed and msg:
                messages.append(msg)

        return messages

    @staticmethod
    def track_suggestion_activated(game_state) -> List[str]:
        """Track suggestion activation for achievements"""
        messages = []
        GoalSystem.initialize_goals(game_state)

        game_state.goals['total_activations'] += 1
        total = game_state.goals['total_activations']

        achievements = [
            ('first_activation', 1),
            ('activations_25', 25)
        ]

        for achievement_id, target in achievements:
            if total == target:
                completed, msg = GoalSystem.update_goal_progress(game_state, achievement_id, 'achievements', target)
                if completed and msg:
                    messages.append(msg)

        return messages

    @staticmethod
    def track_time_advance(game_state, minutes: int) -> List[str]:
        """Track time advancement for daily goal"""
        messages = []
        GoalSystem.initialize_goals(game_state)

        completed, msg = GoalSystem.update_goal_progress(game_state, 'daily_time', 'daily', minutes)
        if completed and msg:
            messages.append(msg)

        return messages

    @staticmethod
    def track_activity(game_state, activity_id: str) -> List[str]:
        """Track activities performed for goals"""
        messages = []
        GoalSystem.initialize_goals(game_state)

        # Track total activities
        if 'total_activities' not in game_state.goals:
            game_state.goals['total_activities'] = 0

        game_state.goals['total_activities'] += 1
        total = game_state.goals['total_activities']

        # Daily activity goal (not in default goals, but could be added)
        completed, msg = GoalSystem.update_goal_progress(game_state, 'daily_activity', 'daily', 1)
        if completed and msg:
            messages.append(msg)

        # Achievement for doing many activities
        if total == 10:
            completed, msg = GoalSystem.update_goal_progress(game_state, 'activities_10', 'achievements', 10)
            if completed and msg:
                messages.append(msg)
        elif total == 50:
            completed, msg = GoalSystem.update_goal_progress(game_state, 'activities_50', 'achievements', 50)
            if completed and msg:
                messages.append(msg)

        return messages

    @staticmethod
    def track_rapport_milestone(game_state, character_name: str, new_rapport: int) -> List[str]:
        """Track rapport milestones"""
        messages = []
        GoalSystem.initialize_goals(game_state)

        char_milestones = game_state.goals['character_milestones'].get(character_name, {})
        old_rapport = char_milestones.get('current_rapport', 0)
        char_milestones['current_rapport'] = new_rapport

        # Check for milestone crossings
        milestones = [5, 10, 15, 20]
        for milestone in milestones:
            if old_rapport < milestone <= new_rapport:
                if milestone not in char_milestones.get('milestones_reached', []):
                    # Record milestone
                    if 'milestones_reached' not in char_milestones:
                        char_milestones['milestones_reached'] = []
                    char_milestones['milestones_reached'].append(milestone)

                    # Get milestone info
                    milestone_info = GoalSystem.CHARACTER_MILESTONES.get(milestone, {})
                    if milestone_info.get('reward_sp', 0) > 0:
                        game_state.add_sp(milestone_info['reward_sp'], f"{character_name}: {milestone_info['title']}")

                    messages.append(f"🌟 Milestone: {character_name} - {milestone_info.get('title', 'Progress')}!")

                    # Weekly goal progress
                    completed, msg = GoalSystem.update_goal_progress(game_state, 'weekly_milestone', 'weekly', 1)
                    if completed and msg:
                        messages.append(msg)

                    # Achievement tracking
                    if new_rapport >= 10:
                        completed, msg = GoalSystem.update_goal_progress(game_state, 'rapport_10_any', 'achievements', 10)
                        if completed and msg:
                            messages.append(msg)

                    if new_rapport >= 20:
                        completed, msg = GoalSystem.update_goal_progress(game_state, 'rapport_20_any', 'achievements', 20)
                        if completed and msg:
                            messages.append(msg)

        # Check "all characters" achievements
        chars_at_10 = sum(1 for cm in game_state.goals['character_milestones'].values() if cm.get('current_rapport', 0) >= 10)
        chars_at_20 = sum(1 for cm in game_state.goals['character_milestones'].values() if cm.get('current_rapport', 0) >= 20)

        if chars_at_10 == 7:
            completed, msg = GoalSystem.update_goal_progress(game_state, 'rapport_10_all', 'achievements', 7)
            if completed and msg:
                messages.append(msg)

        if chars_at_20 == 7:
            completed, msg = GoalSystem.update_goal_progress(game_state, 'rapport_20_all', 'achievements', 7)
            if completed and msg:
                messages.append(msg)

        return messages

    @staticmethod
    def get_goals_summary(game_state) -> Dict:
        """Get summary of all goals for UI display"""
        GoalSystem.initialize_goals(game_state)

        # Daily goals
        daily_goals = []
        for goal_id, goal_template in GoalSystem.DAILY_GOALS.items():
            goal_data = game_state.goals['daily'].get(goal_id, {})
            daily_goals.append({
                'id': goal_id,
                'name': goal_template.goal_name,
                'description': goal_template.description,
                'progress': goal_data.get('progress', 0),
                'target': goal_data.get('target', goal_template.target),
                'completed': goal_data.get('completed', False),
                'category': goal_template.category
            })

        # Weekly goals
        weekly_goals = []
        for goal_id, goal_template in GoalSystem.WEEKLY_GOALS.items():
            goal_data = game_state.goals['weekly'].get(goal_id, {})
            weekly_goals.append({
                'id': goal_id,
                'name': goal_template.goal_name,
                'description': goal_template.description,
                'progress': goal_data.get('progress', 0),
                'target': goal_data.get('target', goal_template.target),
                'completed': goal_data.get('completed', False),
                'category': goal_template.category
            })

        # Achievements
        achievements = []
        for goal_id, goal_template in GoalSystem.ACHIEVEMENTS.items():
            goal_data = game_state.goals['achievements'].get(goal_id, {})

            # Skip hidden achievements that aren't unlocked
            if goal_template.hidden and not goal_data.get('unlocked', False):
                continue

            achievements.append({
                'id': goal_id,
                'name': goal_template.goal_name,
                'description': goal_template.description,
                'progress': goal_data.get('progress', 0),
                'target': goal_data.get('target', goal_template.target),
                'completed': goal_data.get('completed', False),
                'category': goal_template.category,
                'hidden': goal_template.hidden
            })

        # Character milestones
        character_progress = []
        for char_name, milestone_data in game_state.goals['character_milestones'].items():
            current_rapport = milestone_data.get('current_rapport', 0)
            next_milestone = None
            for m in [5, 10, 15, 20]:
                if current_rapport < m:
                    next_milestone = m
                    break

            character_progress.append({
                'character': char_name,
                'current_rapport': current_rapport,
                'next_milestone': next_milestone,
                'milestones_reached': milestone_data.get('milestones_reached', [])
            })

        return {
            'daily_goals': daily_goals,
            'weekly_goals': weekly_goals,
            'achievements': achievements,
            'character_progress': character_progress,
            'stats': {
                'total_suggestions_planted': game_state.goals.get('total_suggestions_planted', 0),
                'total_activations': game_state.goals.get('total_activations', 0),
                'total_reinforcements': game_state.goals.get('total_reinforcements', 0)
            }
        }
