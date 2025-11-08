"""
Ruth's Office Scene - Professional environment, stress leverage
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.location_system import get_location


class RuthsOfficeScene(BaseScene):
    """Ruth's workplace. Professional setting with stress-based opportunities."""

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)
        self.location = get_location('ruths_office')
        self.privacy_level = 'medium'
        self.characters_present = ['Ruth'] if self.game_state.get_character('Ruth') else []

    def get_name(self) -> str:
        return "Ruth's Office"

    def get_description(self) -> str:
        return f"""{self.location.description}

Ruth is stressed here. Work pressure makes people vulnerable.
Offering help or simply listening can build massive rapport.
Privacy: MEDIUM"""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        self.display_scene_header()
        ruth = self.game_state.get_character('Ruth')
        if ruth:
            print("\nRuth looks up from her desk, surprised to see you.")
            print("\nRuth: ", end="", flush=True)
            opening = self.llm.get_character_response(ruth, "[Unexpected visit at work]", scene_context="Your unemployed family member has come to your office")
            print(opening)
        input("\nPress Enter to continue...")

    def offer_help(self):
        """Help Ruth with work stress"""
        ruth = self.game_state.get_character('Ruth')
        if ruth:
            print("\n" + "="*70)
            print("You offer to help with her workload.")
            rapport_gain = 2
            ruth.rapport = min(20, ruth.rapport + rapport_gain)
            print(f"✓ Rapport +{rapport_gain} (now {ruth.rapport}/20)")
            self.game_state.add_sp(1, "Helping with work")
            print("="*70)
        input("\nPress Enter to continue...")

    def run(self):
        self.start_scene()
        while self.scene_active:
            options = ["Talk to Ruth", "Plant a suggestion", "Offer to help (+Rapport +SP)", "View skill tree", "Save game", "Leave office"]
            choice = self.display_menu(options)
            if choice == 1:
                self.talk_to_character('Ruth')
            elif choice == 2:
                self.plant_suggestion_menu('Ruth')
            elif choice == 3:
                self.offer_help()
            elif choice == 4:
                self.view_skill_tree()
            elif choice == 5:
                self.game_state.save_game()
                input("Press Enter...")
            elif choice == 6:
                self.scene_active = False
        print("\nYou leave the office.")
        self.game_state.complete_scene(self.get_name())
        input("Press Enter...")
