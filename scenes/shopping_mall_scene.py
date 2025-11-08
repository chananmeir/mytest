"""
Shopping Mall Scene - Busy public space, casual encounters
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.location_system import get_location, get_characters_at_location
from systems.time_system import get_current_period


class ShoppingMallScene(BaseScene):
    """Busy mall. Good for "chance" encounters and shopping discussions."""

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)
        self.location = get_location('shopping_mall')
        self.privacy_level = 'low'
        self.update_available_characters()

    def update_available_characters(self):
        period = get_current_period(self.game_state.current_time) if hasattr(self.game_state, 'current_time') else 'afternoon'
        scheduled = get_characters_at_location('shopping_mall', period)
        self.characters_present = [n for n in scheduled if self.game_state.get_character(n)]
        if not self.characters_present:
            for n in ['Lisa', 'Vanessa']:
                if self.game_state.get_character(n):
                    self.characters_present.append(n)
                    break

    def get_name(self) -> str:
        return "Shopping Mall"

    def get_description(self) -> str:
        return f"""{self.location.description}

Public, crowded, distracting. Good for casual encounters and fashion/appearance
discussions with Vanessa or Lisa. Privacy: LOW"""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        self.display_scene_header()
        if self.characters_present:
            char = self.game_state.get_character(self.characters_present[0])
            if char:
                print(f"\nYou run into {char.name} at the mall.")
                print(f"\n{char.name}: ", end="", flush=True)
                opening = self.llm.get_character_response(char, "[Chance encounter at mall]", scene_context="You're shopping when you unexpectedly see your family member")
                print(opening)
        input("\nPress Enter...")

    def shop_together(self):
        """Browse stores together"""
        if self.characters_present:
            char = self.game_state.get_character(self.characters_present[0])
            if char:
                print("\n" + "="*70)
                print("You browse stores together. Shared activities build connection.")
                rapport_gain = 1
                char.rapport = min(20, char.rapport + rapport_gain)
                print(f"✓ Rapport +{rapport_gain} (now {char.rapport}/20)")
                print("="*70)
        input("\nPress Enter...")

    def run(self):
        self.start_scene()
        while self.scene_active:
            options = ["Talk to someone", "Plant a suggestion (RISKY - Low Privacy)", "Browse together (+Rapport)", "View skill tree", "Save game", "Leave mall"]
            choice = self.display_menu(options)
            if choice == 1 and self.characters_present:
                char_choice = self.display_menu(self.characters_present + ["Back"])
                if char_choice <= len(self.characters_present):
                    self.talk_to_character(self.characters_present[char_choice - 1])
            elif choice == 2 and self.characters_present:
                print("\n⚠️ LOW PRIVACY - Crowded public space")
                char_choice = self.display_menu(self.characters_present + ["Back"])
                if char_choice <= len(self.characters_present):
                    self.plant_suggestion_menu(self.characters_present[char_choice - 1])
            elif choice == 3:
                self.shop_together()
            elif choice == 4:
                self.view_skill_tree()
            elif choice == 5:
                self.game_state.save_game()
                input("Press Enter...")
            elif choice == 6:
                self.scene_active = False
        print("\nYou leave the mall.")
        self.game_state.complete_scene(self.get_name())
        input("Press Enter...")
