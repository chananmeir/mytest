"""
Fitness Center Scene - Marcus's domain, ego-based manipulation
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.location_system import get_location


class FitnessCenterScene(BaseScene):
    """The gym where Marcus works. Ego and physical pride dominate here."""

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)
        self.location = get_location('fitness_center')
        self.privacy_level = 'medium'
        self.characters_present = ['Marcus'] if self.game_state.get_character('Marcus') else []

    def get_name(self) -> str:
        return "Fitness Center"

    def get_description(self) -> str:
        return f"""{self.location.description}

Marcus's ego is tied to physical performance. Compliments on his physique,
asking for fitness advice - these build rapport quickly. Challenge him wrong
and he becomes defensive. Privacy: MEDIUM"""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        self.display_scene_header()
        marcus = self.game_state.get_character('Marcus')
        if marcus:
            print("\nMarcus is mid-workout. He nods at you between sets.")
            print("\nMarcus: ", end="", flush=True)
            opening = self.llm.get_character_response(marcus, "[Player arrives at gym]", scene_context="Your unemployed family member has come to the gym where you work")
            print(opening)
        input("\nPress Enter...")

    def ask_for_training(self):
        """Ask Marcus for fitness advice"""
        marcus = self.game_state.get_character('Marcus')
        if marcus:
            print("\n" + "="*70)
            print("You ask Marcus for training advice. His ego loves this.")
            rapport_gain = 2
            marcus.rapport = min(20, marcus.rapport + rapport_gain)
            print(f"✓ Rapport +{rapport_gain} (now {marcus.rapport}/20)")
            self.game_state.add_sp(1, "Feeding Marcus's ego")
            print("="*70)
        input("\nPress Enter...")

    def run(self):
        self.start_scene()
        while self.scene_active:
            options = ["Talk to Marcus", "Plant a suggestion", "Ask for training advice (+Rapport +SP)", "View skill tree", "Save game", "Leave gym"]
            choice = self.display_menu(options)
            if choice == 1:
                self.talk_to_character('Marcus')
            elif choice == 2:
                self.plant_suggestion_menu('Marcus')
            elif choice == 3:
                self.ask_for_training()
            elif choice == 4:
                self.view_skill_tree()
            elif choice == 5:
                self.game_state.save_game()
                input("Press Enter...")
            elif choice == 6:
                self.scene_active = False
        print("\nYou leave the fitness center.")
        self.game_state.complete_scene(self.get_name())
        input("Press Enter...")
