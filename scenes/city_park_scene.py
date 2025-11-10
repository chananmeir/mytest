"""
City Park Scene - Outdoor, relaxed, reflective conversations
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.location_system import get_location, get_characters_at_location
from systems.time_system import get_current_period


class CityParkScene(BaseScene):
    """Beautiful park. Peaceful and open for reflective conversations."""

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)
        self.location = get_location('city_park')
        self.privacy_level = 'medium'
        self.update_available_characters()

    def update_available_characters(self):
        period = get_current_period(self.game_state.current_time) if hasattr(self.game_state, 'current_time') else 'afternoon'
        scheduled = get_characters_at_location('city_park', period)
        self.characters_present = [n for n in scheduled if self.game_state.get_character(n)]
        if not self.characters_present:
            for n in ['Sophie', 'Rachel']:
                if self.game_state.get_character(n):
                    self.characters_present.append(n)
                    break

    def get_name(self) -> str:
        return "City Park"

    def get_description(self) -> str:
        return f"""{self.location.description}

Neutral ground. The peaceful setting encourages openness and reflection.
Good for deep conversations. Privacy: MEDIUM"""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        self.display_scene_header()
        if self.characters_present:
            char = self.game_state.get_character(self.characters_present[0])
            if char:
                print(f"\nYou spot {char.name} on a park bench.")
                print(f"\n{char.name}: ", end="", flush=True)
                opening = self.llm.get_character_response(char, "[Meeting at park]", scene_context="You're at the park when your family member approaches")
                print(opening)
        input("\nPress Enter...")

    def walk_together(self):
        """Take a walk with someone"""
        if self.characters_present:
            char = self.game_state.get_character(self.characters_present[0])
            if char:
                print("\n" + "="*70)
                print("You suggest a walk together. Moving side-by-side creates rapport.")
                rapport_gain = 1
                char.rapport = min(20, char.rapport + rapport_gain)
                print(f"✓ Rapport +{rapport_gain} (now {char.rapport}/20)")
                self.game_state.add_sp(1, "Walking together")
                print("="*70)
        input("\nPress Enter...")

    def run(self):
        self.start_scene()
        while self.scene_active:
            options = ["Talk to someone", "Plant a suggestion", "Walk together (+Rapport +SP)", "View skill tree", "Save game", "Leave park"]
            choice = self.display_menu(options)
            if choice == 1 and self.characters_present:
                char_choice = self.display_menu(self.characters_present + ["Back"])
                if char_choice <= len(self.characters_present):
                    self.talk_to_character(self.characters_present[char_choice - 1])
            elif choice == 2 and self.characters_present:
                char_choice = self.display_menu(self.characters_present + ["Back"])
                if char_choice <= len(self.characters_present):
                    self.plant_suggestion_menu(self.characters_present[char_choice - 1])
            elif choice == 3:
                self.walk_together()
            elif choice == 4:
                self.view_skill_tree()
            elif choice == 5:
                self.game_state.save_game()
                input("Press Enter...")
            elif choice == 6:
                self.scene_active = False
        print("\nYou leave the park.")
        self.game_state.complete_scene(self.get_name())
        input("Press Enter...")
