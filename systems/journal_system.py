"""
Journal and Tracking System - Keep track of progress with characters

Helps players remember who they've done what with through:
- Personal journal entries
- Character dossiers with full history
- PHS tracking and effectiveness
- Relationship timeline
- Secrets and vulnerabilities discovered
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class JournalEntry:
    """A player-written journal entry"""
    entry_id: str
    timestamp: str
    entry_type: str  # 'general', 'character_note', 'goal', 'observation', 'phs_note'
    character_name: Optional[str] = None
    title: str = ""
    content: str = ""
    tags: List[str] = field(default_factory=list)
    is_important: bool = False
    icon: str = "📝"


@dataclass
class DossierEntry:
    """Auto-tracked entry in character dossier"""
    timestamp: str
    entry_type: str  # 'milestone', 'phs', 'secret', 'vulnerability', 'conversation', 'event'
    title: str
    description: str
    importance: int = 5  # 1-10
    icon: str = "📌"
    metadata: Dict = field(default_factory=dict)  # Additional data (PHS stats, etc.)


class JournalSystem:
    """Manages player journal and character dossiers"""

    @staticmethod
    def create_journal_entry(game_state, entry_type: str, content: str,
                           character_name: Optional[str] = None,
                           title: str = "", tags: List[str] = None,
                           is_important: bool = False) -> JournalEntry:
        """Create a new journal entry"""

        # Generate entry ID
        if not hasattr(game_state, 'journal_entry_counter'):
            game_state.journal_entry_counter = 0
        game_state.journal_entry_counter += 1
        entry_id = f"entry_{game_state.journal_entry_counter}"

        # Get icon based on type
        icons = {
            'general': '📝',
            'character_note': '👤',
            'goal': '🎯',
            'observation': '👁️',
            'phs_note': '✨'
        }
        icon = icons.get(entry_type, '📝')

        entry = JournalEntry(
            entry_id=entry_id,
            timestamp=game_state.time_system.get_formatted_datetime(),
            entry_type=entry_type,
            character_name=character_name,
            title=title,
            content=content,
            tags=tags or [],
            is_important=is_important,
            icon=icon
        )

        # Add to journal
        if not hasattr(game_state, 'journal_entries'):
            game_state.journal_entries = []
        game_state.journal_entries.append(entry)

        return entry

    @staticmethod
    def get_journal_entries(game_state, character_name: Optional[str] = None,
                           entry_type: Optional[str] = None,
                           limit: int = 50) -> List[Dict]:
        """Get journal entries, optionally filtered"""

        if not hasattr(game_state, 'journal_entries'):
            return []

        entries = game_state.journal_entries

        # Filter by character
        if character_name:
            entries = [e for e in entries if e.character_name == character_name]

        # Filter by type
        if entry_type:
            entries = [e for e in entries if e.entry_type == entry_type]

        # Sort by timestamp (newest first)
        entries = sorted(entries,
                        key=lambda e: e.timestamp,
                        reverse=True)

        # Limit results
        entries = entries[:limit]

        # Convert to dict for JSON
        return [
            {
                'entry_id': e.entry_id,
                'timestamp': e.timestamp,
                'type': e.entry_type,
                'character': e.character_name,
                'title': e.title,
                'content': e.content,
                'tags': e.tags,
                'is_important': e.is_important,
                'icon': e.icon
            }
            for e in entries
        ]

    @staticmethod
    def delete_journal_entry(game_state, entry_id: str) -> bool:
        """Delete a journal entry"""
        if not hasattr(game_state, 'journal_entries'):
            return False

        original_count = len(game_state.journal_entries)
        game_state.journal_entries = [
            e for e in game_state.journal_entries
            if e.entry_id != entry_id
        ]

        return len(game_state.journal_entries) < original_count

    @staticmethod
    def get_character_dossier(game_state, character_name: str) -> Dict:
        """Get comprehensive dossier for a character"""

        character = game_state.characters.get(character_name)
        if not character:
            return {'error': 'Character not found'}

        # Initialize dossier tracking if needed
        if not hasattr(character, 'dossier_entries'):
            character.dossier_entries = []

        # Compile dossier information
        dossier = {
            'character_name': character_name,
            'basic_info': {
                'age': character.age,
                'occupation': character.occupation,
                'personality': character.personality,
                'first_met': getattr(character, 'first_met_time', 'Unknown')
            },
            'current_status': {
                'rapport': character.rapport,
                'resistance': character.resistance,
                'emotional_state': character.emotional_state,
                'suspicion_level': getattr(character, 'suspicion_level', 0),
                'outfit': getattr(character, 'clothing', 'Unknown'),
                'clothing_effect': getattr(character, 'clothing_modifier', 0)
            },
            'relationship_timeline': JournalSystem._build_relationship_timeline(character),
            'phs_tracking': JournalSystem._build_phs_tracking(character),
            'conversations': JournalSystem._get_key_conversations(character),
            'secrets_discovered': JournalSystem._get_secrets(character),
            'vulnerabilities': JournalSystem._get_vulnerabilities(character),
            'goals': JournalSystem._get_character_goals(game_state, character_name),
            'statistics': JournalSystem._get_character_statistics(character),
            'dossier_entries': JournalSystem._get_dossier_entries(character)
        }

        return dossier

    @staticmethod
    def _build_relationship_timeline(character) -> List[Dict]:
        """Build timeline of key relationship moments"""
        timeline = []

        # First meeting
        if hasattr(character, 'first_met_time'):
            timeline.append({
                'timestamp': character.first_met_time,
                'event': 'First Meeting',
                'description': f"Met {character.name} for the first time",
                'icon': '👋',
                'importance': 10
            })

        # Rapport milestones
        rapport_milestones = [
            (5, 'Acquaintance', '🤝'),
            (10, 'Friend', '😊'),
            (15, 'Close Friend', '💙'),
            (20, 'Maximum Rapport', '💖')
        ]

        for threshold, label, icon in rapport_milestones:
            if character.rapport >= threshold:
                timeline.append({
                    'timestamp': 'Unknown',  # Would need to track this
                    'event': f'{label} Status Achieved',
                    'description': f'Reached {threshold} rapport with {character.name}',
                    'icon': icon,
                    'importance': threshold // 2
                })

        # Sort by importance
        timeline.sort(key=lambda e: e.get('importance', 5), reverse=True)

        return timeline

    @staticmethod
    def _build_phs_tracking(character) -> Dict:
        """Build comprehensive PHS tracking data"""

        if not hasattr(character, 'active_phs'):
            return {
                'total_planted': 0,
                'currently_active': 0,
                'total_activations': 0,
                'success_rate': 0,
                'active_suggestions': []
            }

        active_phs = character.active_phs or []
        total_activations = sum(phs.reinforcements for phs in active_phs)
        avg_success_rate = sum(phs.activation_chance for phs in active_phs) / max(len(active_phs), 1)

        # Track removed/completed PHS
        total_planted = getattr(character, 'total_phs_planted', len(active_phs))

        return {
            'total_planted': total_planted,
            'currently_active': len(active_phs),
            'total_activations': total_activations,
            'success_rate': round(avg_success_rate, 1),
            'active_suggestions': [
                {
                    'trigger': phs.trigger,
                    'response': phs.response,
                    'activation_chance': phs.activation_chance,
                    'reinforcements': phs.reinforcements,
                    'type': JournalSystem._detect_phs_type(phs)
                }
                for phs in active_phs
            ]
        }

    @staticmethod
    def _detect_phs_type(phs) -> str:
        """Detect PHS type from trigger/response"""
        response = phs.response.lower()

        if any(kw in response for kw in ['wear', 'dress', 'clothing']):
            return 'Behavioral - Clothing'
        elif any(kw in response for kw in ['feel', 'attracted', 'love']):
            return 'Emotional Nudge'
        elif any(kw in response for kw in ['obey', 'agree', 'listen']):
            return 'Compliance Trigger'
        elif any(kw in response for kw in ['call', 'visit', 'come']):
            return 'Behavioral - Action'
        else:
            return 'General Suggestion'

    @staticmethod
    def _get_key_conversations(character) -> List[Dict]:
        """Get summaries of important conversations"""

        conversations = []

        # Get from memories
        if hasattr(character, 'memories'):
            conv_memories = [
                m for m in character.memories
                if m.get('type') in ['conversation', 'important_event']
            ]

            # Sort by importance, take top 10
            conv_memories.sort(key=lambda m: m.get('importance', 0), reverse=True)

            for memory in conv_memories[:10]:
                conversations.append({
                    'timestamp': memory.get('timestamp', 'Unknown'),
                    'content': memory.get('content', ''),
                    'importance': memory.get('importance', 5),
                    'emotional_context': memory.get('emotional_context', 'neutral')
                })

        return conversations

    @staticmethod
    def _get_secrets(character) -> List[Dict]:
        """Get secrets discovered about character"""

        secrets = []

        # Check for secret memories
        if hasattr(character, 'memories'):
            secret_memories = [
                m for m in character.memories
                if 'secret' in m.get('type', '').lower() or
                   'secret' in m.get('content', '').lower()
            ]

            for memory in secret_memories:
                secrets.append({
                    'secret': memory.get('content', ''),
                    'discovered': memory.get('timestamp', 'Unknown'),
                    'importance': memory.get('importance', 5)
                })

        # Check for tracked secrets
        if hasattr(character, 'secrets_discovered'):
            for secret in character.secrets_discovered:
                secrets.append({
                    'secret': secret.get('description', ''),
                    'discovered': secret.get('timestamp', 'Unknown'),
                    'importance': secret.get('importance', 5)
                })

        return secrets

    @staticmethod
    def _get_vulnerabilities(character) -> List[Dict]:
        """Get known vulnerabilities and weaknesses"""

        vulnerabilities = []

        # Low resistance is a vulnerability
        if character.resistance < 30:
            vulnerabilities.append({
                'type': 'Low Mental Resistance',
                'description': f'Only {character.resistance}% resistance - highly suggestible',
                'severity': 'High',
                'icon': '🎯'
            })

        # Clothing-based vulnerability
        if hasattr(character, 'clothing_modifier') and character.clothing_modifier < -5:
            vulnerabilities.append({
                'type': 'Suggestive Clothing',
                'description': f'Current outfit reduces resistance by {abs(character.clothing_modifier)}%',
                'severity': 'Medium',
                'icon': '👗'
            })

        # High suspicion is a weakness
        if hasattr(character, 'suspicion_level') and character.suspicion_level > 50:
            vulnerabilities.append({
                'type': 'High Suspicion',
                'description': f'{character.suspicion_level}% suspicious - be careful!',
                'severity': 'High',
                'icon': '⚠️'
            })

        # Emotional state vulnerabilities
        if character.emotional_state in ['nervous', 'anxious', 'sad']:
            vulnerabilities.append({
                'type': 'Emotional Vulnerability',
                'description': f'Currently {character.emotional_state} - more receptive to comfort',
                'severity': 'Medium',
                'icon': '💭'
            })

        # Track from character data
        if hasattr(character, 'vulnerabilities'):
            for vuln in character.vulnerabilities:
                vulnerabilities.append({
                    'type': vuln.get('type', 'Unknown'),
                    'description': vuln.get('description', ''),
                    'severity': vuln.get('severity', 'Medium'),
                    'icon': vuln.get('icon', '📌')
                })

        return vulnerabilities

    @staticmethod
    def _get_character_goals(game_state, character_name: str) -> List[Dict]:
        """Get player's goals with this character"""

        # Get from goal system if exists
        from systems.goal_system import GoalSystem

        all_goals = GoalSystem.get_all_goals(game_state)

        # Filter for character-specific goals
        char_goals = [
            g for g in all_goals
            if character_name.lower() in g.get('description', '').lower()
        ]

        return char_goals

    @staticmethod
    def _get_character_statistics(character) -> Dict:
        """Get statistical information about character"""

        return {
            'total_conversations': getattr(character, 'total_conversations', 0),
            'total_activities': getattr(character, 'total_activities', 0),
            'gifts_received': getattr(character, 'gifts_received', 0),
            'total_rapport_gained': getattr(character, 'total_rapport_gained', character.rapport),
            'times_suspicious': getattr(character, 'times_suspicious', 0),
            'phs_activations': sum(
                phs.reinforcements for phs in getattr(character, 'active_phs', [])
            )
        }

    @staticmethod
    def _get_dossier_entries(character) -> List[Dict]:
        """Get auto-tracked dossier entries"""

        if not hasattr(character, 'dossier_entries'):
            return []

        return [
            {
                'timestamp': entry.timestamp,
                'type': entry.entry_type,
                'title': entry.title,
                'description': entry.description,
                'importance': entry.importance,
                'icon': entry.icon,
                'metadata': entry.metadata
            }
            for entry in sorted(
                character.dossier_entries,
                key=lambda e: e.importance,
                reverse=True
            )[:20]  # Top 20 most important
        ]

    @staticmethod
    def add_dossier_entry(character, entry_type: str, title: str,
                         description: str, importance: int = 5,
                         metadata: Dict = None):
        """Add auto-tracked entry to character dossier"""

        if not hasattr(character, 'dossier_entries'):
            character.dossier_entries = []

        icons = {
            'milestone': '⭐',
            'phs': '✨',
            'secret': '🔐',
            'vulnerability': '🎯',
            'conversation': '💬',
            'event': '📌'
        }

        entry = DossierEntry(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'),
            entry_type=entry_type,
            title=title,
            description=description,
            importance=importance,
            icon=icons.get(entry_type, '📌'),
            metadata=metadata or {}
        )

        character.dossier_entries.append(entry)

        # Keep only top 50 entries
        if len(character.dossier_entries) > 50:
            character.dossier_entries.sort(key=lambda e: e.importance, reverse=True)
            character.dossier_entries = character.dossier_entries[:50]

    @staticmethod
    def get_all_dossiers_summary(game_state) -> List[Dict]:
        """Get summary of all character dossiers"""

        summaries = []

        for char_name, character in game_state.characters.items():
            active_phs_count = len(getattr(character, 'active_phs', []))
            secrets_count = len(JournalSystem._get_secrets(character))

            summaries.append({
                'name': char_name,
                'rapport': character.rapport,
                'resistance': character.resistance,
                'active_phs': active_phs_count,
                'secrets_known': secrets_count,
                'last_interaction': getattr(character, 'last_interaction_time', 'Unknown')
            })

        # Sort by rapport (most progress first)
        summaries.sort(key=lambda s: s['rapport'], reverse=True)

        return summaries
