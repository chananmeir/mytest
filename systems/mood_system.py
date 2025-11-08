"""
Mood System - Emotional state visualization and strategic recommendations
"""

from typing import Dict, Tuple


class MoodSystem:
    """Handles mood visualization and strategic recommendations"""

    # Emoji mapping for emotional states
    MOOD_EMOJIS = {
        'neutral': '😐',
        'relaxed': '😊',
        'tense': '😰',
        'defensive': '😠',
        'open': '💖',
        'hostile': '😡',
        'happy': '😄',
        'sad': '😢',
        'anxious': '😟',
        'confident': '😎',
        'shy': '😳',
        'playful': '😏',
        'suspicious': '🤨',
        'trusting': '🥰',
        'uncomfortable': '😬',
        'pleased': '😌'
    }

    # Strategic recommendations based on emotional state
    MOOD_RECOMMENDATIONS = {
        'open': {
            'advice': '✨ Perfect time to plant a suggestion!',
            'color': 'var(--success-color)',
            'icon': '✓'
        },
        'relaxed': {
            'advice': '✓ Good time to plant suggestions or build rapport',
            'color': 'var(--success-color)',
            'icon': '✓'
        },
        'trusting': {
            'advice': '✨ Excellent state for planting suggestions!',
            'color': 'var(--success-color)',
            'icon': '✓'
        },
        'happy': {
            'advice': '✓ Good mood - suggestions more likely to work',
            'color': 'var(--success-color)',
            'icon': '✓'
        },
        'pleased': {
            'advice': '✓ Receptive state - good time for suggestions',
            'color': 'var(--success-color)',
            'icon': '✓'
        },
        'playful': {
            'advice': '✓ Light mood - good for casual suggestions',
            'color': 'var(--success-color)',
            'icon': '✓'
        },
        'neutral': {
            'advice': '• Build rapport or wait for better mood',
            'color': 'var(--text-secondary)',
            'icon': '•'
        },
        'confident': {
            'advice': '• Neutral state - rapport building recommended',
            'color': 'var(--text-secondary)',
            'icon': '•'
        },
        'shy': {
            'advice': '• Build trust before planting suggestions',
            'color': 'var(--warning-color)',
            'icon': '⚠'
        },
        'tense': {
            'advice': '⚠ Try to relax them first - suggestions harder',
            'color': 'var(--warning-color)',
            'icon': '⚠'
        },
        'anxious': {
            'advice': '⚠ Calm them down before attempting suggestions',
            'color': 'var(--warning-color)',
            'icon': '⚠'
        },
        'uncomfortable': {
            'advice': '⚠ Make them comfortable first',
            'color': 'var(--warning-color)',
            'icon': '⚠'
        },
        'suspicious': {
            'advice': '⚠ Rebuild trust - avoid suggestions for now',
            'color': 'var(--warning-color)',
            'icon': '⚠'
        },
        'defensive': {
            'advice': '✗ Poor time for suggestions - build rapport first',
            'color': 'var(--danger-color)',
            'icon': '✗'
        },
        'hostile': {
            'advice': '✗ Very poor time - focus on damage control',
            'color': 'var(--danger-color)',
            'icon': '✗'
        },
        'sad': {
            'advice': '✗ Comfort them first, avoid suggestions',
            'color': 'var(--danger-color)',
            'icon': '✗'
        }
    }

    @staticmethod
    def get_mood_emoji(emotional_state: str) -> str:
        """Get emoji for emotional state"""
        return MoodSystem.MOOD_EMOJIS.get(emotional_state.lower(), '😐')

    @staticmethod
    def get_mood_recommendation(emotional_state: str) -> Dict[str, str]:
        """Get strategic recommendation for emotional state"""
        return MoodSystem.MOOD_RECOMMENDATIONS.get(
            emotional_state.lower(),
            {
                'advice': '• Observe their mood',
                'color': 'var(--text-secondary)',
                'icon': '•'
            }
        )

    @staticmethod
    def format_mood_display(
        emotional_state: str,
        reason: str = "",
        include_recommendation: bool = True
    ) -> Dict[str, str]:
        """
        Format mood display with emoji, state, reason, and recommendation

        Args:
            emotional_state: Current emotional state
            reason: Why they're in this state
            include_recommendation: Whether to include strategic advice

        Returns:
            Dict with display elements
        """
        emoji = MoodSystem.get_mood_emoji(emotional_state)
        recommendation = MoodSystem.get_mood_recommendation(emotional_state)

        result = {
            'emoji': emoji,
            'state': emotional_state.title(),
            'reason': reason,
            'recommendation_text': recommendation['advice'] if include_recommendation else '',
            'recommendation_color': recommendation['color'] if include_recommendation else '',
            'recommendation_icon': recommendation['icon'] if include_recommendation else ''
        }

        return result

    @staticmethod
    def get_suggestibility_modifier(emotional_state: str) -> int:
        """
        Get suggestibility modifier based on emotional state

        Returns percentage modifier (+/- %)
        """
        modifiers = {
            'open': 15,
            'trusting': 12,
            'relaxed': 8,
            'happy': 8,
            'pleased': 8,
            'playful': 5,
            'neutral': 0,
            'confident': 0,
            'shy': -3,
            'uncomfortable': -5,
            'anxious': -8,
            'tense': -10,
            'suspicious': -12,
            'sad': -10,
            'defensive': -15,
            'hostile': -20
        }

        return modifiers.get(emotional_state.lower(), 0)
