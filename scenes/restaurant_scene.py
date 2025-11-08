"""
Restaurant Scene - Upscale dining, special occasion bonding
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.location_system import get_location


class RestaurantScene(BaseScene):
    """Nice restaurant. Perfect for special conversations over good food."""

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)
        self.location = get_location('restaurant')
        self.privacy_level = 'high'
        self.meal_stage = 'appetizers'
        self.characters_present = []

    def get_name(self) -> str:
        return "Nice Restaurant"

    def get_description(self) -> str:
        return f"""{self.location.description}

Taking someone to a nice restaurant signals effort and care. The formal setting
encourages deeper conversations. Good food lowers defenses. Privacy: HIGH"""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        self.display_scene_header()
        print("\nYou're at an upscale restaurant. Who are you dining with?")

        # Select dinner companion
        all_chars = [n for n in self.game_state.characters.keys()]
        char_choice = self.display_menu(all_chars + ["Dine alone"])

        if char_choice <= len(all_chars):
            companion_name = all_chars[char_choice - 1]
            self.characters_present = [companion_name]

            companion = self.game_state.get_character(companion_name)
            if companion:
                print(f"\n{companion_name} arrives and sits across from you.")
                print(f"\n{companion_name}: ", end="", flush=True)
                opening = self.llm.get_character_response(companion, "[Having dinner together]", scene_context="Your family member has taken you to a nice restaurant")
                print(opening)

        input("\nPress Enter...")

    def advance_meal(self):
        """Progress through meal courses"""
        stages = ['appetizers', 'main_course', 'dessert']
        idx = stages.index(self.meal_stage)
        if idx < len(stages) - 1:
            self.meal_stage = stages[idx + 1]
            print(f"\n{'='*70}")
            print(f"--- {self.meal_stage.upper()} ---")
            print(f"{'='*70}")
            if self.meal_stage == 'dessert' and self.characters_present:
                char = self.game_state.get_character(self.characters_present[0])
                if char:
                    rapport_gain = 1
                    char.rapport = min(20, char.rapport + rapport_gain)
                    print(f"The meal has gone well. Rapport +{rapport_gain} (now {char.rapport}/20)")
            print(f"{'='*70}\n")
            input("Press Enter...")
            return True
        return False

    def run(self):
        self.start_scene()
        while self.scene_active:
            if self.characters_present:
                options = ["Talk to them", "Plant a suggestion (HIGH PRIVACY)", "Advance meal course", "View skill tree", "Save game", "End dinner"]
                choice = self.display_menu(options)
                if choice == 1:
                    self.talk_to_character(self.characters_present[0])
                elif choice == 2:
                    self.plant_suggestion_menu(self.characters_present[0])
                elif choice == 3:
                    if not self.advance_meal():
                        print("\nThe meal is complete.")
                        self.scene_active = False
                elif choice == 4:
                    self.view_skill_tree()
                elif choice == 5:
                    self.game_state.save_game()
                    input("Press Enter...")
                elif choice == 6:
                    self.scene_active = False
            else:
                print("\nYou dine alone, then leave.")
                self.scene_active = False

        print("\nYou pay the bill and leave the restaurant.")
        self.game_state.complete_scene(self.get_name())
        input("Press Enter...")
