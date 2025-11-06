"""
Base scene class for Family Dynamics RPG
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.hypnosis import HypnosisSystem


class BaseScene(ABC):
    """Abstract base class for game scenes"""

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        self.game_state = game_state
        self.llm = llm_handler
        self.hypnosis = HypnosisSystem()
        self.scene_active = True

    @abstractmethod
    def get_name(self) -> str:
        """Return the scene name"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Return the scene description"""
        pass

    @abstractmethod
    def start_scene(self):
        """Initialize and display the scene opening"""
        pass

    @abstractmethod
    def get_available_characters(self) -> List[str]:
        """Return list of character names present in this scene"""
        pass

    def display_scene_header(self):
        """Display formatted scene header"""
        print("\n" + "="*70)
        print(f"SCENE: {self.get_name()}")
        print("="*70)
        print(self.get_description())
        print("="*70 + "\n")

    def display_menu(self, options: List[str], title: str = "What do you do?") -> int:
        """Display a menu and get user choice"""
        print(f"\n{title}")
        print("-" * 40)

        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        print()

        while True:
            try:
                choice = input("Enter your choice: ").strip()
                choice_num = int(choice)

                if 1 <= choice_num <= len(options):
                    return choice_num
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nGame interrupted.")
                return -1

    def talk_to_character(self, character_name: str):
        """Have a conversation with a character"""
        char = self.game_state.get_character(character_name)

        if not char:
            print(f"Character {character_name} not found.")
            return

        print(f"\n--- Talking to {character_name} ---")
        print(f"Rapport: {char.rapport}/20 | Emotional State: {char.emotional_state}")
        print(f"Resistance: {char.resistance}% | Active PHS: {len(char.active_phs)}/{char.max_phs}")
        print()

        while True:
            player_input = input("You say (or 'back' to end conversation): ").strip()

            if not player_input:
                continue

            if player_input.lower() in ['back', 'exit', 'quit']:
                print(f"\nYou end the conversation with {character_name}.\n")
                break

            # Get response from LLM
            print(f"\n{character_name}: ", end="", flush=True)
            response = self.llm.get_character_response(
                char,
                player_input,
                scene_context=self.get_description()
            )
            print(response)

            # Analyze the interaction
            analysis = self.llm.analyze_player_action(
                player_input,
                char,
                context=f"In response to: {response}"
            )

            # Apply changes
            if analysis['rapport_change'] != 0:
                if analysis['rapport_change'] > 0:
                    message = self.hypnosis.build_rapport(
                        self.game_state,
                        character_name,
                        abs(analysis['rapport_change']),
                        analysis['reasoning']
                    )
                else:
                    char.reduce_rapport(abs(analysis['rapport_change']))
                    message = f"Rapport with {character_name} decreased: {char.rapport}/20 ({analysis['reasoning']})"

                print(f"\n[{message}]")

            # Update emotional state if changed
            if analysis['new_emotional_state'] != char.emotional_state:
                message = self.hypnosis.change_emotional_state(
                    self.game_state,
                    character_name,
                    analysis['new_emotional_state'],
                    analysis['reasoning']
                )
                print(f"[{message}]")

            print()

    def plant_suggestion_menu(self, character_name: str):
        """Menu for planting post-hypnotic suggestions"""
        char = self.game_state.get_character(character_name)

        if not char:
            print(f"Character {character_name} not found.")
            return

        can_plant, message = self.hypnosis.can_plant_phs(self.game_state, character_name)

        print(f"\n--- Plant Suggestion on {character_name} ---")
        print(f"Status: {message}")
        print(f"Available SP: {self.game_state.player.suggestion_points}")

        if not can_plant:
            print("\nCannot plant suggestion at this time.")
            input("\nPress Enter to continue...")
            return

        options = [
            f"Emotional Nudge ({self.hypnosis.EMOTIONAL_NUDGE_COST} SP)",
            f"Behavioral Prompt ({self.hypnosis.BEHAVIORAL_PROMPT_COST} SP)",
            f"Strong Anchor ({self.hypnosis.STRONG_ANCHOR_COST_MIN}-{self.hypnosis.STRONG_ANCHOR_COST_MAX} SP)",
            "Back"
        ]

        choice = self.display_menu(options, "Choose suggestion type:")

        if choice == 4 or choice == -1:
            return

        print("\nDefine the post-hypnotic suggestion:")
        trigger = input("Trigger (when...): ").strip()

        if not trigger:
            print("Cancelled.")
            return

        response = input("Response (they will...): ").strip()

        if not response:
            print("Cancelled.")
            return

        success = False
        result_message = ""

        if choice == 1:  # Emotional Nudge
            success, result_message = self.hypnosis.plant_emotional_nudge(
                self.game_state, character_name, trigger, response
            )
        elif choice == 2:  # Behavioral Prompt
            success, result_message = self.hypnosis.plant_behavioral_prompt(
                self.game_state, character_name, trigger, response
            )
        elif choice == 3:  # Strong Anchor
            try:
                sp_cost = int(input(f"SP to invest ({self.hypnosis.STRONG_ANCHOR_COST_MIN}-{self.hypnosis.STRONG_ANCHOR_COST_MAX}): "))
                success, result_message = self.hypnosis.plant_strong_anchor(
                    self.game_state, character_name, trigger, response, sp_cost
                )
            except ValueError:
                result_message = "Invalid SP amount"

        print(f"\n{'✓' if success else '✗'} {result_message}")
        input("\nPress Enter to continue...")

    def view_character_status(self, character_name: str):
        """View detailed status of a character"""
        char = self.game_state.get_character(character_name)

        if not char:
            print(f"Character {character_name} not found.")
            return

        print(f"\n{'='*60}")
        print(f"{char.name} - {char.age} years old")
        print(f"{'='*60}")
        print(f"Occupation: {char.occupation}")
        print(f"Appearance: {char.clothing}")
        print(f"            ({char.clothing_meaning})")
        print(f"\nPersonality: {char.personality}")
        print(f"\nCurrent State: {char.emotional_state}")
        print(f"Rapport: {char.rapport}/20")
        print(f"Resistance: {char.resistance}%")
        print(f"Active PHS: {len(char.active_phs)}/{char.max_phs}")

        if char.active_phs:
            print(f"\nACTIVE POST-HYPNOTIC SUGGESTIONS:")
            print("-" * 60)
            for i, phs in enumerate(char.active_phs, 1):
                chance = phs.calculate_activation_chance()
                print(f"{i}. Trigger: {phs.trigger}")
                print(f"   Response: {phs.response}")
                print(f"   Activation Chance: {chance}% (reinforced {phs.reinforcements}x)")
                print()

        print("="*60)
        input("\nPress Enter to continue...")

    @abstractmethod
    def run(self):
        """Main scene loop"""
        pass
