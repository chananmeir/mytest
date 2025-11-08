"""
Coffee Café Scene - Intimate conversations in public
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.location_system import get_location, get_characters_at_location
from systems.time_system import get_current_period


class CoffeeCafeScene(BaseScene):
    """Cozy café. Good for intimate conversations in a public setting."""

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)
        self.location = get_location('coffee_cafe')
        self.privacy_level = 'high'
        self.update_available_characters()

    def update_available_characters(self):
        period = get_current_period(self.game_state.current_time) if hasattr(self.game_state, 'current_time') else 'morning'
        scheduled = get_characters_at_location('coffee_cafe', period)
        self.characters_present = [n for n in scheduled if self.game_state.get_character(n)]
        if not self.characters_present:
            for n in ['Sophie', 'Vanessa', 'Ruth']:
                if self.game_state.get_character(n):
                    self.characters_present.append(n)
                    break

    def get_name(self) -> str:
        return "Coffee Café"

    def get_description(self) -> str:
        return f"""{self.location.description}

The ambient noise provides cover. People expect deep conversations here.
Perfect for "accidental" meetups. Privacy: HIGH"""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        self.display_scene_header()
        if self.characters_present:
            char = self.game_state.get_character(self.characters_present[0])
            if char:
                print(f"\nYou see {char.name} at a corner table.")
                print(f"\n{char.name}: ", end="", flush=True)
                opening = self.llm.get_character_response(char, "[Meeting at café]", scene_context="You're having coffee when your family member arrives")
                print(opening)
        input("\nPress Enter...")

    def buy_coffee(self):
        """Buy coffee for someone"""
        if self.characters_present:
            char = self.game_state.get_character(self.characters_present[0])
            if char:
                print("\n" + "="*70)
                print("You offer to buy them a coffee. Small gestures matter.")
                rapport_gain = 1
                char.rapport = min(20, char.rapport + rapport_gain)
                print(f"✓ Rapport +{rapport_gain} (now {char.rapport}/20)")
                print("="*70)
        input("\nPress Enter...")

    def run(self):
        self.start_scene()
        while self.scene_active:
            options = ["Talk to someone", "Plant a suggestion (HIGH PRIVACY)", "Buy them coffee (+Rapport)", "View skill tree", "Save game", "Leave café"]
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
                self.buy_coffee()
            elif choice == 4:
                self.view_skill_tree()
            elif choice == 5:
                self.game_state.save_game()
                input("Press Enter...")
            elif choice == 6:
                self.scene_active = False
        print("\nYou leave the café.")
        self.game_state.complete_scene(self.get_name())
        input("Press Enter...")
