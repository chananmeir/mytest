"""
Hypnosis knowledge and skill progression system
"""
from typing import Dict, List, Set
from dataclasses import dataclass, field


@dataclass
class HypnosisTechnique:
    """Represents a hypnosis technique the player can learn"""
    name: str
    description: str
    category: str  # 'basic', 'intermediate', 'advanced', 'master'
    prerequisites: List[str] = field(default_factory=list)  # Names of required techniques
    learning_difficulty: int = 1  # 1-10, how hard to learn
    sp_cost_reduction: int = 0  # Reduces SP cost when planting
    success_rate_bonus: int = 0  # Bonus to PHS success rate

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'prerequisites': self.prerequisites,
            'learning_difficulty': self.learning_difficulty,
            'sp_cost_reduction': self.sp_cost_reduction,
            'success_rate_bonus': self.success_rate_bonus
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'HypnosisTechnique':
        return cls(**data)


# Define all available techniques
HYPNOSIS_TECHNIQUES = {
    # BASIC - Starting techniques
    'observation': HypnosisTechnique(
        name='Observation',
        description='Learn to read body language and emotional cues',
        category='basic',
        prerequisites=[],
        learning_difficulty=1,
        sp_cost_reduction=0,
        success_rate_bonus=5
    ),

    'active_listening': HypnosisTechnique(
        name='Active Listening',
        description='Truly hear what people say and mean',
        category='basic',
        prerequisites=[],
        learning_difficulty=1,
        sp_cost_reduction=0,
        success_rate_bonus=5
    ),

    'mirroring': HypnosisTechnique(
        name='Mirroring',
        description='Subtly mirror body language to build unconscious rapport',
        category='basic',
        prerequisites=['observation'],
        learning_difficulty=2,
        sp_cost_reduction=0,
        success_rate_bonus=5
    ),

    # INTERMEDIATE - Core hypnosis
    'rapport_building': HypnosisTechnique(
        name='Rapport Building',
        description='Consciously create deep connection and trust',
        category='intermediate',
        prerequisites=['active_listening', 'mirroring'],
        learning_difficulty=3,
        sp_cost_reduction=0,
        success_rate_bonus=10
    ),

    'embedded_commands': HypnosisTechnique(
        name='Embedded Commands',
        description='Hide suggestions within normal conversation',
        category='intermediate',
        prerequisites=['rapport_building'],
        learning_difficulty=4,
        sp_cost_reduction=1,
        success_rate_bonus=10
    ),

    'emotional_anchoring': HypnosisTechnique(
        name='Emotional Anchoring',
        description='Link emotions to specific triggers',
        category='intermediate',
        prerequisites=['rapport_building'],
        learning_difficulty=4,
        sp_cost_reduction=0,
        success_rate_bonus=15
    ),

    # ADVANCED - Powerful techniques
    'trance_induction': HypnosisTechnique(
        name='Trance Induction',
        description='Guide someone into a receptive hypnotic state',
        category='advanced',
        prerequisites=['embedded_commands', 'emotional_anchoring'],
        learning_difficulty=6,
        sp_cost_reduction=1,
        success_rate_bonus=15
    ),

    'post_hypnotic_suggestion': HypnosisTechnique(
        name='Post-Hypnotic Suggestion',
        description='Plant suggestions that activate later',
        category='advanced',
        prerequisites=['trance_induction'],
        learning_difficulty=7,
        sp_cost_reduction=2,
        success_rate_bonus=20
    ),

    'pattern_interruption': HypnosisTechnique(
        name='Pattern Interruption',
        description='Break thought patterns to bypass resistance',
        category='advanced',
        prerequisites=['trance_induction'],
        learning_difficulty=6,
        sp_cost_reduction=1,
        success_rate_bonus=15
    ),

    # MASTER - Ultimate techniques
    'conversational_hypnosis': HypnosisTechnique(
        name='Conversational Hypnosis',
        description='Hypnotize without them realizing it',
        category='master',
        prerequisites=['post_hypnotic_suggestion', 'pattern_interruption'],
        learning_difficulty=9,
        sp_cost_reduction=2,
        success_rate_bonus=25
    ),

    'deep_programming': HypnosisTechnique(
        name='Deep Programming',
        description='Create profound behavioral changes',
        category='master',
        prerequisites=['conversational_hypnosis'],
        learning_difficulty=10,
        sp_cost_reduction=3,
        success_rate_bonus=30
    ),
}


class HypnosisKnowledge:
    """Tracks the player's hypnosis knowledge and skills"""

    def __init__(self):
        self.known_techniques: Set[str] = set()
        self.learning_progress: Dict[str, int] = {}  # technique_name: progress (0-100)
        self.practice_sessions: int = 0
        self.books_read: List[str] = []
        self.skill_level: str = 'novice'  # novice, learner, practitioner, expert, master

    def learn_technique(self, technique_name: str) -> bool:
        """Learn a technique (if prerequisites met)"""
        if technique_name not in HYPNOSIS_TECHNIQUES:
            return False

        technique = HYPNOSIS_TECHNIQUES[technique_name]

        # Check prerequisites
        for prereq in technique.prerequisites:
            if prereq not in self.known_techniques:
                return False

        self.known_techniques.add(technique_name)
        self._update_skill_level()
        return True

    def knows_technique(self, technique_name: str) -> bool:
        """Check if player knows a technique"""
        return technique_name in self.known_techniques

    def can_learn_technique(self, technique_name: str) -> tuple[bool, str]:
        """Check if player can learn a technique"""
        if technique_name not in HYPNOSIS_TECHNIQUES:
            return False, "Technique not found"

        if technique_name in self.known_techniques:
            return False, "Already learned"

        technique = HYPNOSIS_TECHNIQUES[technique_name]

        for prereq in technique.prerequisites:
            if prereq not in self.known_techniques:
                prereq_name = HYPNOSIS_TECHNIQUES[prereq].name
                return False, f"Requires: {prereq_name}"

        return True, "Ready to learn"

    def add_learning_progress(self, technique_name: str, amount: int) -> int:
        """Add progress toward learning a technique"""
        if technique_name not in self.learning_progress:
            self.learning_progress[technique_name] = 0

        self.learning_progress[technique_name] = min(100, self.learning_progress[technique_name] + amount)

        # Auto-learn when reaching 100%
        if self.learning_progress[technique_name] >= 100:
            if self.learn_technique(technique_name):
                del self.learning_progress[technique_name]
                return 100

        return self.learning_progress[technique_name]

    def _update_skill_level(self):
        """Update overall skill level based on techniques known"""
        count = len(self.known_techniques)

        if count >= 10:
            self.skill_level = 'master'
        elif count >= 7:
            self.skill_level = 'expert'
        elif count >= 5:
            self.skill_level = 'practitioner'
        elif count >= 2:
            self.skill_level = 'learner'
        else:
            self.skill_level = 'novice'

    def get_available_techniques(self) -> List[HypnosisTechnique]:
        """Get techniques that can be learned"""
        available = []

        for name, technique in HYPNOSIS_TECHNIQUES.items():
            if name not in self.known_techniques:
                can_learn, _ = self.can_learn_technique(name)
                if can_learn:
                    available.append(technique)

        return available

    def get_technique_bonus(self, technique_name: str) -> tuple[int, int]:
        """Get SP reduction and success bonus for a technique"""
        if technique_name in self.known_techniques:
            technique = HYPNOSIS_TECHNIQUES[technique_name]
            return technique.sp_cost_reduction, technique.success_rate_bonus
        return 0, 0

    def get_total_bonuses(self) -> tuple[int, int]:
        """Get total SP reduction and success bonus from all known techniques"""
        total_sp_reduction = 0
        total_success_bonus = 0

        for tech_name in self.known_techniques:
            technique = HYPNOSIS_TECHNIQUES[tech_name]
            total_sp_reduction += technique.sp_cost_reduction
            total_success_bonus += technique.success_rate_bonus

        return total_sp_reduction, total_success_bonus

    def to_dict(self) -> dict:
        """Convert to dictionary for saving"""
        return {
            'known_techniques': list(self.known_techniques),
            'learning_progress': self.learning_progress,
            'practice_sessions': self.practice_sessions,
            'books_read': self.books_read,
            'skill_level': self.skill_level
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'HypnosisKnowledge':
        """Create from dictionary"""
        knowledge = cls()
        knowledge.known_techniques = set(data.get('known_techniques', []))
        knowledge.learning_progress = data.get('learning_progress', {})
        knowledge.practice_sessions = data.get('practice_sessions', 0)
        knowledge.books_read = data.get('books_read', [])
        knowledge.skill_level = data.get('skill_level', 'novice')
        return knowledge


# Books and learning resources
LEARNING_RESOURCES = {
    'introduction_to_hypnosis': {
        'title': 'Introduction to Hypnosis',
        'description': 'A beginner\'s guide to understanding hypnotic principles',
        'teaches': ['observation', 'active_listening'],
        'progress_per_read': 50,
        'location': 'library'
    },

    'the_art_of_rapport': {
        'title': 'The Art of Rapport',
        'description': 'Building deep connections through mirroring and empathy',
        'teaches': ['mirroring', 'rapport_building'],
        'progress_per_read': 40,
        'location': 'library'
    },

    'embedded_commands_manual': {
        'title': 'Embedded Commands Manual',
        'description': 'Advanced language patterns for covert persuasion',
        'teaches': ['embedded_commands'],
        'progress_per_read': 35,
        'location': 'bookstore'
    },

    'emotional_alchemy': {
        'title': 'Emotional Alchemy',
        'description': 'Transform and anchor emotional states',
        'teaches': ['emotional_anchoring'],
        'progress_per_read': 35,
        'location': 'online'
    },

    'trance_states': {
        'title': 'Trance States and Induction',
        'description': 'Professional techniques for inducing hypnotic trance',
        'teaches': ['trance_induction', 'pattern_interruption'],
        'progress_per_read': 30,
        'location': 'specialty_shop'
    },

    'conversational_hypnosis_mastery': {
        'title': 'Conversational Hypnosis Mastery',
        'description': 'The ultimate guide to covert influence',
        'teaches': ['post_hypnotic_suggestion', 'conversational_hypnosis'],
        'progress_per_read': 25,
        'location': 'hidden'
    },

    'deep_programming_secrets': {
        'title': 'Deep Programming Secrets',
        'description': 'Forbidden techniques for profound behavioral change',
        'teaches': ['deep_programming'],
        'progress_per_read': 20,
        'location': 'secret'
    },
}
