"""
Backyard Scene - Outdoor privacy, fresh air excuse
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.location_system import get_location, get_characters_at_location
from systems.time_system import get_current_period


class BackyardScene(BaseScene):
    """
    The backyard. Fresh air, privacy, casual setting.


HIGH PRIVACY - Away from the house, fewer eyes.
    Good excuse for one-on-one conversations ("I needed some air").
    """

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)
        self.location = get_location('home_backyard')
        self.time_of_day = 'afternoon'
        self.privacy_level = 'high'
        self.update_available_characters()

    def update_available_characters(self):
        period = get_current_period(self.game_state.current_time) if hasattr(self.game_state, 'current_time') else 'afternoon'
        scheduled_chars = get_characters_at_location('home_backyard', period)
        self.characters_present = [name for name in scheduled_chars if self.game_state.get_character(name)]

        # Backyard often has Rachel playing, or people taking a break
        if not self.characters_present:
            for name in ['Rachel', 'Tom']:
                if self.game_state.get_character(name):
                    self.characters_present.append(name)
                    break

    def get_name(self) -> str:
        return "Backyard - Home"

    def get_description(self) -> str:
        return f"""{self.location.description}

The backyard offers natural privacy. You can have conversations here that would
draw suspicion indoors. "I just needed some fresh air" is the perfect excuse.

Privacy Level: HIGH - Easy to plant suggestions
Characters here are relaxed, guards lowered by the outdoor setting."""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        self.display_scene_header()
        print("\nYou step outside into the backyard. The fresh air is a relief.")

        if self.characters_present:
            greeter = self.game_state.get_character(self.characters_present[0])
            if greeter:
                print(f"\n{greeter.name} is already out here.")
                print(f"\n{greeter.name}: ", end="", flush=True)
                opening = self.llm.get_character_response(greeter, "[Player comes outside]", scene_context="You're in the backyard when your family member comes outside")
                print(opening)

        print("\n" + "-"*70)
        print(f"Backyard - HIGH PRIVACY. Good for private conversations.")
        print("-"*70)
        input("\nPress Enter to continue...")

    def smoke_excuse(self):
        """Use smoking/vaping as excuse for private talk"""
        print("\n" + "="*70)
        print("SMOKE BREAK EXCUSE")
        print("="*70)
        print("\nYou pull out a vape pen (or pretend to). The universal excuse")
        print("for stepping outside and having a private moment with someone.")

        if self.characters_present:
            import random
            companion = random.choice(self.characters_present)
            char = self.game_state.get_character(companion)
            if char:
                rapport_gain = 1
                char.rapport = min(20, char.rapport + rapport_gain)
                print(f"\n{companion} joins you in the shared ritual.")
                print(f"✓ Rapport +{rapport_gain} (now {char.rapport}/20)")

        print("\n" + "="*70)
        input("\nPress Enter to continue...")

    def run(self):
        self.start_scene()

        while self.scene_active:
            print(f"\n{'='*70}")
            print(f"SP: {self.game_state.player.suggestion_points} | Privacy: {self.privacy_level.upper()}")
            print(f"{'='*70}")

            options = [
                "Talk to someone",
                "Plant a suggestion (HIGH PRIVACY)",
                "Smoke break excuse (+Rapport)",
                "View character details",
                "View skill tree",
                "Study hypnosis",
                "View your status",
                "Save game",
                "Go back inside"
            ]

            choice = self.display_menu(options)

            if choice == -1:
                break
            elif choice == 1 and self.characters_present:
                char_choice = self.display_menu(self.characters_present + ["Back"])
                if char_choice <= len(self.characters_present):
                    self.talk_to_character(self.characters_present[char_choice - 1])
            elif choice == 2 and self.characters_present:
                char_choice = self.display_menu(self.characters_present + ["Back"])
                if char_choice <= len(self.characters_present):
                    self.plant_suggestion_menu(self.characters_present[char_choice - 1])
            elif choice == 3:
                self.smoke_excuse()
            elif choice == 4 and self.characters_present:
                char_choice = self.display_menu(self.characters_present + ["Back"])
                if char_choice <= len(self.characters_present):
                    self.view_character_status(self.characters_present[char_choice - 1])
            elif choice == 5:
                self.view_skill_tree()
            elif choice == 6:
                self.study_hypnosis()
            elif choice == 7:
                self.game_state.display_status()
                input("\nPress Enter to continue...")
            elif choice == 8:
                if self.game_state.save_game():
                    print("\n✓ Saved!")
                input("\nPress Enter to continue...")
            elif choice == 9:
                self.scene_active = False

        print("\n" + "="*70)
        print("You head back inside.")
        print("="*70 + "\n")
        self.game_state.complete_scene(self.get_name())
        input("Press Enter to continue...")
