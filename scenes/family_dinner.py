"""
Family Dinner Scene - The first scene in Family Dynamics RPG
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler


class FamilyDinnerScene(BaseScene):
    """
    The family gathers for dinner. Everyone knows about your job loss.
    This is your opportunity to begin shifting the dynamics.
    """

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)
        self.characters_present = ['Ruth', 'Tom', 'Dawn', 'Vanessa', 'Derek', 'Karen']
        self.dinner_stage = 'arrival'  # arrival, main_course, dessert, ending

    def get_name(self) -> str:
        return "Family Dinner at Dawn's House"

    def get_description(self) -> str:
        if self.dinner_stage == 'arrival':
            return """You arrive at your mother Dawn's house for the monthly family dinner.
The smell of roasted chicken fills the air. You're wearing your usual simple clothes -
a faded but clean t-shirt and older jeans. Nothing fancy, nothing that draws attention.

Everyone knows about your job loss three months ago. You can feel the judgment in the air.
Your sister Ruth greets you with a sympathetic smile. Your brother-in-law Tom avoids eye contact.
Dawn, your mother, fusses with the table settings. Vanessa checks her phone - probably posting
about the "family gathering." Derek is already talking about his latest fitness achievement.
Karen, your other sister, looks at you with that familiar mix of concern and disappointment.

You are the lowest-status person in this room. And that's exactly where your power begins."""

        elif self.dinner_stage == 'main_course':
            return """Everyone is seated around the dinner table. Plates are full, conversation flows.
This is where the real dynamics play out - the subtle jabs, the careful compliments,
the unspoken hierarchies. You notice everything. You say little. You watch."""

        elif self.dinner_stage == 'dessert':
            return """Dessert is served - Dawn's famous apple pie. People are more relaxed now,
guards slightly lowered by good food and the comfort of routine. This is when suggestions
sink deepest, when words echo longest."""

        else:  # ending
            return """The evening is winding down. Some are helping clean up, others lingering
in conversation. The seeds you've planted tonight will grow in the days to come."""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        """Initialize the scene"""
        self.display_scene_header()

        print("Your mother Dawn approaches you.")
        print("\nDawn: ", end="", flush=True)

        dawn = self.game_state.get_character('Dawn')
        if dawn:
            opening = self.llm.get_character_response(
                dawn,
                "[Player has just arrived at the family dinner]",
                scene_context="You're greeting your unemployed adult child at a family dinner"
            )
            print(opening)

        print("\n" + "-"*70)
        print("The game begins. You have 3 Suggestion Points (SP).")
        print("Build rapport. Shift emotional states. Plant suggestions.")
        print("Remember: You speak less than others, but notice more.")
        print("-"*70)

        input("\nPress Enter to continue...")

    def advance_dinner_stage(self):
        """Move to the next stage of dinner"""
        stages = ['arrival', 'main_course', 'dessert', 'ending']
        current_idx = stages.index(self.dinner_stage)

        if current_idx < len(stages) - 1:
            self.dinner_stage = stages[current_idx + 1]
            print(f"\n{'='*70}")
            print(f"--- {self.dinner_stage.replace('_', ' ').upper()} ---")
            print(f"{'='*70}")
            print(self.get_description())
            print(f"{'='*70}\n")
            input("Press Enter to continue...")
            return True
        else:
            return False

    def observe_room(self):
        """Observe the room and characters"""
        print("\n" + "="*70)
        print("YOU OBSERVE THE ROOM")
        print("="*70)

        for name in self.characters_present:
            char = self.game_state.get_character(name)
            if char:
                rapport_bar = "█" * char.rapport + "░" * (20 - char.rapport)
                print(f"\n{char.name} ({char.occupation})")
                print(f"  Wearing: {char.clothing}")
                print(f"  Mood: {char.emotional_state}")
                print(f"  Rapport: [{rapport_bar}] {char.rapport}/20")

                if char.active_phs:
                    print(f"  🎯 Active Suggestions: {len(char.active_phs)}")

        print("\n" + "="*70)
        input("\nPress Enter to continue...")

    def listen_to_conversations(self):
        """Listen to what family members are saying to each other"""
        print("\n" + "="*70)
        print("YOU LISTEN QUIETLY")
        print("="*70)
        print("\nYou fade into the background, observing the dynamics...")
        print()

        # Pick 2-3 random characters to have a brief exchange
        import random
        speakers = random.sample(self.characters_present, min(3, len(self.characters_present)))

        for speaker_name in speakers:
            char = self.game_state.get_character(speaker_name)
            if char:
                # Generate a contextual comment from this character
                context = f"You are at a family dinner. Make a brief comment (1-2 sentences) that reveals your personality and current feelings. The player (your unemployed family member) is present but quiet."

                comment = self.llm.get_character_response(
                    char,
                    "[Observing the dinner scene]",
                    scene_context=context
                )

                print(f"{speaker_name}: {comment}\n")

        print("="*70)
        print("\nYou've learned more about the current dynamics.")
        print("[Sometimes listening is more valuable than speaking.]")

        # Small SP reward for patience
        self.game_state.add_sp(1, "Patient observation")

        input("\nPress Enter to continue...")

    def run(self):
        """Main scene loop"""
        self.start_scene()

        while self.scene_active:
            print(f"\n{'='*70}")
            print(f"SP: {self.game_state.player.suggestion_points} | Stage: {self.dinner_stage.replace('_', ' ').title()}")
            print(f"{'='*70}")

            options = [
                "Talk to someone",
                "Plant a suggestion",
                "Observe the room",
                "Listen to conversations",
                "View character details",
                "Advance to next stage",
                "View your status",
                "Save game",
                "End scene"
            ]

            choice = self.display_menu(options)

            if choice == -1:  # Interrupted
                break

            if choice == 1:  # Talk to someone
                print("\nWho do you want to talk to?")
                char_options = self.characters_present + ["Back"]
                char_choice = self.display_menu(char_options)

                if char_choice != -1 and char_choice <= len(self.characters_present):
                    self.talk_to_character(self.characters_present[char_choice - 1])

            elif choice == 2:  # Plant suggestion
                print("\nWho do you want to plant a suggestion on?")
                char_options = self.characters_present + ["Back"]
                char_choice = self.display_menu(char_options)

                if char_choice != -1 and char_choice <= len(self.characters_present):
                    self.plant_suggestion_menu(self.characters_present[char_choice - 1])

            elif choice == 3:  # Observe
                self.observe_room()

            elif choice == 4:  # Listen
                self.listen_to_conversations()

            elif choice == 5:  # View character details
                print("\nWhich character?")
                char_options = self.characters_present + ["Back"]
                char_choice = self.display_menu(char_options)

                if char_choice != -1 and char_choice <= len(self.characters_present):
                    self.view_character_status(self.characters_present[char_choice - 1])

            elif choice == 6:  # Advance stage
                if not self.advance_dinner_stage():
                    print("\nThe dinner has ended.")
                    self.scene_active = False

            elif choice == 7:  # Status
                self.game_state.display_status()
                input("\nPress Enter to continue...")

            elif choice == 8:  # Save
                if self.game_state.save_game():
                    print("\n✓ Game saved successfully!")
                else:
                    print("\n✗ Failed to save game")
                input("\nPress Enter to continue...")

            elif choice == 9:  # End scene
                print("\nAre you sure you want to end this scene? (yes/no)")
                confirm = input("> ").strip().lower()

                if confirm in ['yes', 'y']:
                    self.scene_active = False

        # Scene complete
        print("\n" + "="*70)
        print("SCENE COMPLETE")
        print("="*70)
        print("\nThe family dinner ends. Everyone returns to their lives.")
        print("But the suggestions you planted will echo in their minds...")
        print("\nYour influence is just beginning.")
        print("="*70 + "\n")

        self.game_state.complete_scene(self.get_name())
        input("Press Enter to continue...")
