"""
Game state management for Family Dynamics RPG
"""
import json
from typing import Dict, Optional
from dataclasses import dataclass, field
from models.character import Character, PostHypnoticSuggestion, CHARACTERS
from systems.hypnosis_knowledge import HypnosisKnowledge
from systems.time_system import GameTime
import config


@dataclass
class PlayerState:
    """Tracks the player character's state"""
    name: str = "You"
    age: int = 38
    occupation: str = "Currently Unemployed / Between Jobs"
    clothing: str = "Faded t-shirt, clean but older jeans, comfortable shoes"
    suggestion_points: int = config.STARTING_SP
    total_sp_earned: int = 0
    money: int = 100  # Starting money ($100)
    total_money_earned: int = 0
    current_scene: str = "start"
    scenes_completed: list = field(default_factory=list)
    hypnosis_knowledge: HypnosisKnowledge = field(default_factory=HypnosisKnowledge)
    current_location: str = "home_living_room"  # Player's current location
    statement_history: list = field(default_factory=list)  # Track player statements for contradiction detection

    # Advanced Hypnosis tracking
    mastery_level: 'MasteryLevel' = None  # Will be initialized in __post_init__
    active_combos: list = field(default_factory=list)  # List of ComboSuggestion objects
    active_conflicts: list = field(default_factory=list)  # List of ConflictingPHS objects

    def __post_init__(self):
        """Initialize mastery level if not loaded from save"""
        if self.mastery_level is None:
            from systems.advanced_hypnosis import MasteryLevel
            self.mastery_level = MasteryLevel()


class GameState:
    """Main game state manager"""

    def __init__(self, procedural_mode: bool = False, procedural_seed: Optional[int] = None):
        """
        Initialize game state

        Args:
            procedural_mode: If True, use procedural generation for variety
            procedural_seed: Optional seed for reproducible procedural generation
        """
        self.player = PlayerState()
        self.characters: Dict[str, Character] = {}
        self.scene_history: list = []
        self.current_scene_name: str = "start"
        self.game_time: GameTime = GameTime()  # Time system

        # Unlock progression tracking
        self.completed_events: list = ['game_start']  # Event IDs that have triggered
        self.completed_quests: list = []  # Quest IDs completed
        self.unlocked_locations: list = []  # Manually unlocked locations
        self.unlocked_characters: list = ['Ruth', 'Tom']  # Starting characters

        # Enhanced AI Integration
        from systems.enhanced_ai_integration import EnhancedAIIntegration
        self.ai_integration: EnhancedAIIntegration = EnhancedAIIntegration()

        # Procedural Generation
        self.procedural_mode: bool = procedural_mode
        self.procedural_generator: Optional['ProceduralGameMode'] = None
        self.procedural_events: list = []  # Store generated events

        # Initialize characters (procedural or standard)
        if procedural_mode:
            self._initialize_procedural_game(procedural_seed)
        else:
            self._initialize_characters()

    def _initialize_characters(self):
        """Initialize all characters from the character database"""
        for name, char in CHARACTERS.items():
            # Create a fresh copy of each character
            self.characters[name] = Character(
                name=char.name,
                age=char.age,
                occupation=char.occupation,
                clothing=char.clothing,
                clothing_meaning=char.clothing_meaning,
                personality=char.personality,
                resistance=char.resistance,
                rapport=0,
                emotional_state="neutral"
            )

    def _initialize_procedural_game(self, seed: Optional[int] = None):
        """Initialize game with procedural generation"""
        from systems.procedural_generation import ProceduralGameMode

        # Create procedural generator
        self.procedural_generator = ProceduralGameMode(seed=seed)

        # Generate characters and events
        self.characters, self.procedural_events = self.procedural_generator.initialize_procedural_game()

        # Display procedural summary
        print(self.procedural_generator.get_procedural_summary(self.characters))

    def get_character(self, name: str) -> Optional[Character]:
        """Get a character by name"""
        return self.characters.get(name)

    def add_sp(self, amount: int, reason: str = "") -> None:
        """Add suggestion points"""
        self.player.suggestion_points += amount
        self.player.total_sp_earned += amount
        if reason:
            print(f"\n[+{amount} SP] {reason}")

    def spend_sp(self, amount: int) -> bool:
        """Try to spend suggestion points"""
        if self.player.suggestion_points >= amount:
            self.player.suggestion_points -= amount
            return True
        return False

    def add_scene_to_history(self, scene_name: str, description: str = ""):
        """Record a scene in history"""
        self.scene_history.append({
            'scene': scene_name,
            'description': description
        })

    def complete_scene(self, scene_name: str):
        """Mark a scene as completed"""
        if scene_name not in self.player.scenes_completed:
            self.player.scenes_completed.append(scene_name)

    def get_characters_at_location(self, location_id: str = None) -> Dict[str, Character]:
        """Get all characters currently at a specific location (defaults to player's location)"""
        from systems.location_system import get_character_location

        if location_id is None:
            location_id = self.player.current_location

        current_period = self.game_time.period
        characters_here = {}

        for name, character in self.characters.items():
            char_location = get_character_location(name, current_period)
            if char_location == location_id:
                characters_here[name] = character

        return characters_here

    def travel_to_location(self, location_id: str) -> bool:
        """
        Travel to a new location, advancing time appropriately
        Returns True if successful, False if location unavailable
        """
        from systems.location_system import get_location, ALL_LOCATIONS

        if location_id not in ALL_LOCATIONS:
            return False

        location = get_location(location_id)

        # Check if location is open at current time
        if not location.is_open(self.game_time.hour):
            return False

        # Advance time by travel time (in minutes)
        if location.travel_time_from_home > 0:
            for _ in range(location.travel_time_from_home):
                self.game_time.advance_time(1)  # Advance 1 minute at a time

        # Update player location
        self.player.current_location = location_id
        return True

    def get_current_location(self):
        """Get the Location object for player's current location"""
        from systems.location_system import get_location
        return get_location(self.player.current_location)

    def to_dict(self) -> dict:
        """Convert game state to dictionary for serialization"""
        return {
            'player': {
                'name': self.player.name,
                'age': self.player.age,
                'occupation': self.player.occupation,
                'clothing': self.player.clothing,
                'suggestion_points': self.player.suggestion_points,
                'total_sp_earned': self.player.total_sp_earned,
                'money': self.player.money,
                'total_money_earned': self.player.total_money_earned,
                'current_scene': self.player.current_scene,
                'scenes_completed': self.player.scenes_completed,
                'hypnosis_knowledge': self.player.hypnosis_knowledge.to_dict(),
                'current_location': self.player.current_location,
                'statement_history': [
                    {
                        'timestamp': stmt.timestamp,
                        'character_told': stmt.character_told,
                        'content': stmt.content,
                        'topic': stmt.topic,
                        'keywords': stmt.keywords
                    } for stmt in self.player.statement_history
                ] if hasattr(self.player, 'statement_history') else [],
                'mastery_level': self.player.mastery_level.to_dict() if self.player.mastery_level else {},
                'active_combos': [combo.to_dict() for combo in self.player.active_combos] if hasattr(self.player, 'active_combos') else [],
                'active_conflicts': [conflict.to_dict() for conflict in self.player.active_conflicts] if hasattr(self.player, 'active_conflicts') else []
            },
            'characters': {
                name: char.to_dict()
                for name, char in self.characters.items()
            },
            'scene_history': self.scene_history,
            'current_scene_name': self.current_scene_name,
            'game_time': self.game_time.to_dict(),
            'ai_integration': self.ai_integration.to_dict() if hasattr(self, 'ai_integration') else {},
            'procedural_mode': self.procedural_mode if hasattr(self, 'procedural_mode') else False,
            'procedural_generator': self.procedural_generator.to_dict() if hasattr(self, 'procedural_generator') and self.procedural_generator else None
        }

    def save_game(self, filename: str = config.SAVE_FILE) -> bool:
        """Save game state to JSON file"""
        try:
            save_data = self.to_dict()

            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, filename: str = config.SAVE_FILE) -> bool:
        """Load game state from JSON file"""
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)

            # Restore player state
            player_data = save_data['player']

            # Restore hypnosis knowledge
            if 'hypnosis_knowledge' in player_data:
                hypnosis_knowledge = HypnosisKnowledge.from_dict(player_data['hypnosis_knowledge'])
            else:
                hypnosis_knowledge = HypnosisKnowledge()  # Default for old saves

            # Restore statement history
            statement_history = []
            if 'statement_history' in player_data:
                from systems.contradiction_tracker import PlayerStatement
                statement_history = [
                    PlayerStatement(
                        timestamp=stmt['timestamp'],
                        character_told=stmt['character_told'],
                        content=stmt['content'],
                        topic=stmt['topic'],
                        keywords=stmt.get('keywords', [])
                    ) for stmt in player_data['statement_history']
                ]

            # Restore mastery level
            from systems.advanced_hypnosis import MasteryLevel, ComboSuggestion, ConflictingPHS
            if 'mastery_level' in player_data and player_data['mastery_level']:
                mastery_level = MasteryLevel.from_dict(player_data['mastery_level'])
            else:
                mastery_level = MasteryLevel()  # Default for old saves

            # Restore active combos
            active_combos = []
            if 'active_combos' in player_data:
                active_combos = [
                    ComboSuggestion.from_dict(combo_data)
                    for combo_data in player_data['active_combos']
                ]

            # Restore active conflicts
            active_conflicts = []
            if 'active_conflicts' in player_data:
                active_conflicts = [
                    ConflictingPHS.from_dict(conflict_data)
                    for conflict_data in player_data['active_conflicts']
                ]

            self.player = PlayerState(
                name=player_data['name'],
                age=player_data['age'],
                occupation=player_data['occupation'],
                clothing=player_data['clothing'],
                suggestion_points=player_data['suggestion_points'],
                total_sp_earned=player_data['total_sp_earned'],
                money=player_data.get('money', 100),  # Default for old saves
                total_money_earned=player_data.get('total_money_earned', 0),  # Default for old saves
                current_scene=player_data['current_scene'],
                scenes_completed=player_data['scenes_completed'],
                hypnosis_knowledge=hypnosis_knowledge,
                current_location=player_data.get('current_location', 'home_living_room'),  # Default for old saves
                statement_history=statement_history,
                mastery_level=mastery_level,
                active_combos=active_combos,
                active_conflicts=active_conflicts
            )

            # Restore characters
            self.characters = {}
            for name, char_data in save_data['characters'].items():
                # Reconstruct PHS objects
                phs_list = [
                    PostHypnoticSuggestion.from_dict(phs_data)
                    for phs_data in char_data.get('active_phs', [])
                ]

                # Reconstruct Memory objects
                from systems.memory import Memory
                memories_list = [
                    Memory.from_dict(mem_data)
                    for mem_data in char_data.get('memories', [])
                ]

                char = Character(
                    name=char_data['name'],
                    age=char_data['age'],
                    occupation=char_data['occupation'],
                    clothing=char_data['clothing'],
                    clothing_meaning=char_data['clothing_meaning'],
                    personality=char_data['personality'],
                    resistance=char_data['resistance'],
                    rapport=char_data['rapport'],
                    emotional_state=char_data['emotional_state'],
                    gender=char_data.get('gender', 'male'),  # Default for old saves
                    active_phs=phs_list,
                    conversation_history=char_data.get('conversation_history', []),
                    memories=memories_list,
                    clothing_history=char_data.get('clothing_history', []),
                    relationships=char_data.get('relationships', {}),  # Default for old saves
                    character_interactions=char_data.get('character_interactions', [])  # Default for old saves
                )
                self.characters[name] = char

            self.scene_history = save_data.get('scene_history', [])
            self.current_scene_name = save_data.get('current_scene_name', 'start')

            # Restore game time (with backwards compatibility)
            if 'game_time' in save_data:
                self.game_time = GameTime.from_dict(save_data['game_time'])
            else:
                self.game_time = GameTime()  # Default time for old saves

            # Restore AI integration (with backwards compatibility)
            from systems.enhanced_ai_integration import EnhancedAIIntegration
            if 'ai_integration' in save_data and save_data['ai_integration']:
                self.ai_integration = EnhancedAIIntegration.from_dict(save_data['ai_integration'])
            else:
                self.ai_integration = EnhancedAIIntegration()  # Default for old saves

            # Restore procedural generation (with backwards compatibility)
            self.procedural_mode = save_data.get('procedural_mode', False)
            if 'procedural_generator' in save_data and save_data['procedural_generator']:
                from systems.procedural_generation import ProceduralGameMode
                self.procedural_generator = ProceduralGameMode.from_dict(save_data['procedural_generator'])
            else:
                self.procedural_generator = None
                self.procedural_events = []

            return True
        except FileNotFoundError:
            print(f"No save file found: {filename}")
            return False
        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    def display_status(self):
        """Display current game status"""
        print("\n" + "="*60)
        print("CURRENT STATUS")
        print("="*60)
        print(f"You: {self.player.occupation}")
        print(f"Suggestion Points: {self.player.suggestion_points} SP")
        print(f"Total SP Earned: {self.player.total_sp_earned}")
        print("\nCHARACTER RELATIONSHIPS:")
        print("-"*60)

        for name, char in sorted(self.characters.items()):
            rapport_bar = "█" * char.rapport + "░" * (20 - char.rapport)
            print(f"{name:12} | Rapport: [{rapport_bar}] {char.rapport}/20")
            print(f"{'':12} | State: {char.emotional_state:12} | Resistance: {char.resistance}%")
            if char.active_phs:
                print(f"{'':12} | Active PHS: {len(char.active_phs)}/{char.max_phs}")
            print()

        print("="*60 + "\n")
