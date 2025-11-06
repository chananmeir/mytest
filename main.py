#!/usr/bin/env python3
"""
Family Dynamics RPG - Main Game Entry Point

A psychological RPG where you use conversational hypnosis to shift family dynamics.
"""
import os
import sys
from typing import Optional

# Add color support for terminal
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

from models.game_state import GameState
from systems.llm_handler import LLMHandler
from scenes.family_dinner import FamilyDinnerScene
import config


class Game:
    """Main game controller"""

    def __init__(self):
        self.game_state: Optional[GameState] = None
        self.llm_handler: Optional[LLMHandler] = None
        self.running = True

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_title(self):
        """Print game title"""
        title = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║                    FAMILY DYNAMICS RPG                            ║
║                                                                   ║
║              A Game of Conversational Hypnosis                    ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
        if HAS_COLOR:
            print(Fore.CYAN + title + Style.RESET_ALL)
        else:
            print(title)

    def print_introduction(self):
        """Print game introduction"""
        intro = """
You are 38 years old. Three months ago, you lost your job.
Everyone in your family knows. Some pity you. Some judge you.
Most have already decided what your story means.

But they're wrong about one thing:

They think you're powerless.

You've spent these months studying. Learning. Understanding the subtle
patterns of influence that flow beneath every conversation. The way
rapport shifts with a well-timed pause. How emotional states change
with carefully chosen words. The power of post-hypnotic suggestions
planted in moments of openness.

You wear simple clothes. You speak less than others. You let them
talk, let them assume, let them underestimate.

And then, quietly, you reshape everything.

This is not magic. This is slow power.
This is conversational hypnosis.

Your goal: Shift the family dynamics. Build influence. Plant suggestions
that will echo long after the words are spoken.

Remember: People tell their secrets to those they don't consider dangerous.
"""
        print(intro)
        input("\nPress Enter to begin...")

    def display_main_menu(self) -> int:
        """Display main menu and get choice"""
        print("\n" + "="*70)
        print("MAIN MENU")
        print("="*70)

        options = [
            "New Game",
            "Load Game",
            "About",
            "Exit"
        ]

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
                print("\n\nExiting game...")
                return 4

    def new_game(self):
        """Start a new game"""
        self.clear_screen()
        self.print_title()
        self.print_introduction()

        self.game_state = GameState()
        self.llm_handler = LLMHandler()

        # Start with the first scene
        self.play_scene(FamilyDinnerScene(self.game_state, self.llm_handler))

    def load_game(self):
        """Load a saved game"""
        if not os.path.exists(config.SAVE_FILE):
            print(f"\n✗ No save file found at {config.SAVE_FILE}")
            input("\nPress Enter to continue...")
            return

        self.game_state = GameState()

        if self.game_state.load_game():
            print("\n✓ Game loaded successfully!")
            self.llm_handler = LLMHandler()

            print(f"\nWelcome back!")
            print(f"Suggestion Points: {self.game_state.player.suggestion_points}")
            print(f"Scenes completed: {len(self.game_state.player.scenes_completed)}")

            input("\nPress Enter to continue...")

            # For now, return to family dinner scene
            # In a full game, this would resume from the saved scene
            self.play_scene(FamilyDinnerScene(self.game_state, self.llm_handler))
        else:
            print("\n✗ Failed to load game")
            input("\nPress Enter to continue...")

    def show_about(self):
        """Show about/help screen"""
        about = """
═══════════════════════════════════════════════════════════════════

                        ABOUT FAMILY DYNAMICS RPG

═══════════════════════════════════════════════════════════════════

CONCEPT:
You play as a recently unemployed 38-year-old attending family gatherings.
Through conversational hypnosis and psychological influence, you shift
the family dynamics from your position as the "lowest status" person.

MECHANICS:
- RAPPORT (0-20): Your influence with each character
- RESISTANCE (0-100%): How hard they are to influence
- EMOTIONAL STATE: Affects receptiveness to suggestions
- SUGGESTION POINTS (SP): Currency for planting suggestions
- POST-HYPNOTIC SUGGESTIONS (PHS): Planted behaviors that trigger later

GAMEPLAY:
1. Build rapport through authentic conversation
2. Soften emotional states (defensive → open)
3. Plant post-hypnotic suggestions when conditions are right
4. Reinforce suggestions to increase activation chance
5. Watch the dynamics shift over time

TIPS:
- Listen more than you speak
- Patience earns SP
- Each character has unique resistance levels
- Higher rapport = more influence
- Suggestions are subtle, not mind control
- Save your game frequently!

TECHNICAL:
- Uses OpenRouter API for dynamic NPC conversations
- Requires API key in .env file
- Supports various LLM models

═══════════════════════════════════════════════════════════════════
"""
        print(about)
        input("\nPress Enter to continue...")

    def play_scene(self, scene):
        """Play a scene"""
        scene.run()

        # After scene, return to main menu (or could go to scene selection)
        print("\nReturning to main menu...")
        input("Press Enter to continue...")

    def run(self):
        """Main game loop"""
        self.clear_screen()
        self.print_title()

        # Check for API key
        if not config.OPENROUTER_API_KEY:
            print("\n" + "!"*70)
            print("⚠️  WARNING: OpenRouter API key not configured!")
            print("!"*70)
            print("\nTo use this game with dynamic NPC conversations:")
            print("1. Copy .env.example to .env")
            print("2. Add your OpenRouter API key")
            print("3. Get a key at: https://openrouter.ai/")
            print("\nThe game will run in demo mode without an API key.")
            print("!"*70)
            input("\nPress Enter to continue...")

        while self.running:
            self.clear_screen()
            self.print_title()

            choice = self.display_main_menu()

            if choice == 1:  # New Game
                self.new_game()
            elif choice == 2:  # Load Game
                self.load_game()
            elif choice == 3:  # About
                self.show_about()
            elif choice == 4:  # Exit
                print("\n" + "="*70)
                print("Thank you for playing Family Dynamics RPG")
                print("Remember: Power lies in being underestimated.")
                print("="*70 + "\n")
                self.running = False

        sys.exit(0)


def main():
    """Entry point"""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
