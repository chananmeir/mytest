"""
Elementary School Scene - Karen's domain, structured environment
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.location_system import get_location


class ElementarySchoolScene(BaseScene):
    """Karen's school where she's principal. Formal, rule-oriented."""

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)
        self.location = get_location('elementary_school')
        self.privacy_level = 'low'
        self.characters_present = ['Karen'] if self.game_state.get_character('Karen') else []

    def get_name(self) -> str:
        return "Elementary School"

    def get_description(self) -> str:
        return f"""{self.location.description}

Karen is in control here. She responds well to respect for rules and authority.
But the public setting makes manipulation risky. Privacy: LOW"""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        self.display_scene_header()
        karen = self.game_state.get_character('Karen')
        if karen:
            print("\nKaren is in her principal's office. Professional mode activated.")
            print("\nKaren: ", end="", flush=True)
            opening = self.llm.get_character_response(karen, "[Visiting at work]", scene_context="Your unemployed family member has come to your school")
            print(opening)
        input("\nPress Enter...")

    def run(self):
        self.start_scene()
        while self.scene_active:
            options = ["Talk to Karen", "Plant a suggestion (RISKY - Low Privacy)", "View skill tree", "Save game", "Leave school"]
            choice = self.display_menu(options)
            if choice == 1:
                self.talk_to_character('Karen')
            elif choice == 2:
                print("\n⚠️ LOW PRIVACY - Public school setting")
                self.plant_suggestion_menu('Karen')
            elif choice == 3:
                self.view_skill_tree()
            elif choice == 4:
                self.game_state.save_game()
                input("Press Enter...")
            elif choice == 5:
                self.scene_active = False
        print("\nYou leave the school.")
        self.game_state.complete_scene(self.get_name())
        input("Press Enter...")
