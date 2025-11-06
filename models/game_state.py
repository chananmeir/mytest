"""
Game state management for Family Dynamics RPG
"""
import json
from typing import Dict, Optional
from dataclasses import dataclass, field
from models.character import Character, PostHypnoticSuggestion, CHARACTERS
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
    current_scene: str = "start"
    scenes_completed: list = field(default_factory=list)


class GameState:
    """Main game state manager"""

    def __init__(self):
        self.player = PlayerState()
        self.characters: Dict[str, Character] = {}
        self.scene_history: list = []
        self.current_scene_name: str = "start"

        # Initialize characters from database
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

    def save_game(self, filename: str = config.SAVE_FILE) -> bool:
        """Save game state to JSON file"""
        try:
            save_data = {
                'player': {
                    'name': self.player.name,
                    'age': self.player.age,
                    'occupation': self.player.occupation,
                    'clothing': self.player.clothing,
                    'suggestion_points': self.player.suggestion_points,
                    'total_sp_earned': self.player.total_sp_earned,
                    'current_scene': self.player.current_scene,
                    'scenes_completed': self.player.scenes_completed
                },
                'characters': {
                    name: char.to_dict()
                    for name, char in self.characters.items()
                },
                'scene_history': self.scene_history,
                'current_scene_name': self.current_scene_name
            }

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
            self.player = PlayerState(
                name=player_data['name'],
                age=player_data['age'],
                occupation=player_data['occupation'],
                clothing=player_data['clothing'],
                suggestion_points=player_data['suggestion_points'],
                total_sp_earned=player_data['total_sp_earned'],
                current_scene=player_data['current_scene'],
                scenes_completed=player_data['scenes_completed']
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
                    active_phs=phs_list,
                    conversation_history=char_data.get('conversation_history', []),
                    memories=memories_list
                )
                self.characters[name] = char

            self.scene_history = save_data.get('scene_history', [])
            self.current_scene_name = save_data.get('current_scene_name', 'start')

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
