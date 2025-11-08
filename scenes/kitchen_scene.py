"""
Kitchen Scene - Intimate conversations while helping with cooking
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.location_system import get_location, get_characters_at_location
from systems.time_system import get_current_period


class KitchenScene(BaseScene):
    """
    The kitchen at Dawn's house. A more intimate setting than the dining room.
    Characters come and go as they help with meal preparation. Good for one-on-one
    conversations and building deeper rapport.

    This is a medium-privacy location - easier to plant suggestions than in
    the crowded dining room, but not as private as a bedroom.
    """

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)

        # Load location data
        self.location = get_location('home_kitchen')

        # Kitchen-specific state
        self.cooking_stage = 'preparation'  # preparation, cooking, serving, cleanup
        self.privacy_level = 'medium'  # Easier to plant suggestions here

        # Determine who's in the kitchen based on time
        self.update_available_characters()

    def update_available_characters(self):
        """Update who's available based on game time"""
        # Get current time period from game state
        if hasattr(self.game_state, 'current_time'):
            period = get_current_period(self.game_state.current_time)
        else:
            period = 'evening'  # Default to evening

        # Get characters at kitchen location
        scheduled_chars = get_characters_at_location('home_kitchen', period)

        # Filter to only characters that exist in game state
        self.characters_present = [
            name for name in scheduled_chars
            if self.game_state.get_character(name) is not None
        ]

        # Ensure at least Ruth is here (kitchen is her domain)
        if 'Ruth' not in self.characters_present and self.game_state.get_character('Ruth'):
            self.characters_present.insert(0, 'Ruth')

    def get_name(self) -> str:
        return "Kitchen - Dawn's House"

    def get_description(self) -> str:
        # Get location description
        base_desc = self.location.description

        if self.cooking_stage == 'preparation':
            return f"""{base_desc}

You enter the kitchen to find meal preparation underway. Vegetables are being chopped,
ingredients measured out on the counter. The warm lighting and close quarters create
an atmosphere more intimate than the formal dining room.

This is where the real conversations happen - between the tasks, the casual questions
about "can you pass that?" and "how's the sauce looking?" People's guards are lowered
when their hands are busy. They talk while they work.

The natural topics here: family, daily life, food, domestic concerns. More personal
than public spaces, but not as vulnerable as a bedroom."""

        elif self.cooking_stage == 'cooking':
            return """The kitchen is alive with activity now. Pots simmer on the stove, the oven
radiates heat. You're all moving in the choreography of meal preparation - a dance
everyone knows by heart.

In these moments, when someone's stirring a pot or watching the oven timer, they're
in a slightly different state. More open. More present. More suggestible.

Notice who helps, who avoids tasks, who takes charge, who follows."""

        elif self.cooking_stage == 'serving':
            return """Time to plate and serve. There's a sense of accomplishment in the air -
everyone contributed to creating this meal. The satisfaction of completion, the
anticipation of eating together.

People are in a good mood. Guards down. Perfect for planting suggestions that will
carry into the meal itself."""

        else:  # cleanup
            return """The meal is over, and now comes the cleanup. Some help eagerly, others
reluctantly. This is often when the most honest conversations happen - when the
performance of dinner is over, and you're just dealing with the mundane reality
of dirty dishes.

People say things while washing dishes they wouldn't say at the table."""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        """Initialize the kitchen scene"""
        self.display_scene_header()

        print("\nYou enter the kitchen. The warm lighting and the aroma of cooking create")
        print("an atmosphere of comfort and familiarity.")

        # Get Ruth (or first available character) to greet you
        greeter_name = 'Ruth' if 'Ruth' in self.characters_present else self.characters_present[0]
        greeter = self.game_state.get_character(greeter_name)

        if greeter:
            print(f"\n{greeter_name} looks up from the counter.")
            print(f"\n{greeter_name}: ", end="", flush=True)

            opening = self.llm.get_character_response(
                greeter,
                "[Player has just entered the kitchen]",
                scene_context=f"You're in the kitchen preparing food when your unemployed family member enters. {self.location.description}"
            )
            print(opening)

        print("\n" + "-"*70)
        print("The kitchen offers more privacy than the dining room.")
        print("People are more relaxed here. Conversations flow more naturally.")
        print("This is a good place to build deeper rapport.")
        print(f"Privacy Level: {self.privacy_level.upper()} - Moderate suggestion difficulty")
        print("-"*70)

        input("\nPress Enter to continue...")

    def advance_cooking_stage(self):
        """Move to the next stage of cooking"""
        stages = ['preparation', 'cooking', 'serving', 'cleanup']
        current_idx = stages.index(self.cooking_stage)

        if current_idx < len(stages) - 1:
            self.cooking_stage = stages[current_idx + 1]
            print(f"\n{'='*70}")
            print(f"--- {self.cooking_stage.upper()} ---")
            print(f"{'='*70}")
            print(self.get_description())
            print(f"{'='*70}\n")

            # Potentially new characters arrive during different stages
            self.update_available_characters()

            input("Press Enter to continue...")
            return True
        else:
            return False

    def help_with_cooking(self):
        """Offer to help with cooking - builds rapport"""
        print("\n" + "="*70)
        print("YOU HELP WITH THE COOKING")
        print("="*70)
        print("\nYou roll up your sleeves and genuinely help out.")
        print()

        # Pick a character to work alongside
        if self.characters_present:
            import random
            helper_name = random.choice(self.characters_present)
            helper = self.game_state.get_character(helper_name)

            if helper:
                print(f"You work alongside {helper_name}. The shared task creates")
                print("a natural opportunity for conversation and connection.")

                # Small rapport boost for genuine help
                rapport_gain = 1
                helper.rapport = min(20, helper.rapport + rapport_gain)

                print(f"\n✓ Rapport with {helper_name}: +{rapport_gain} (now {helper.rapport}/20)")

                # Character comments while you work
                context = "You and your unemployed family member are working together in the kitchen. Make a brief comment about the cooking or ask a casual question."

                comment = self.llm.get_character_response(
                    helper,
                    "[Working together in kitchen]",
                    scene_context=context
                )

                print(f"\n{helper_name}: {comment}")

                # Small SP reward for taking time to genuinely help
                self.game_state.add_sp(1, "Helping with cooking")

        print("\n" + "="*70)
        print("Genuine help builds genuine rapport.")
        print("="*70)
        input("\nPress Enter to continue...")

    def observe_kitchen(self):
        """Observe the kitchen and who's doing what"""
        print("\n" + "="*70)
        print("YOU OBSERVE THE KITCHEN DYNAMICS")
        print("="*70)

        print(f"\nCooking Stage: {self.cooking_stage.title()}")
        print(f"Location: {self.location.name}")
        print(f"Atmosphere: {self.location.atmosphere.title()}")
        print(f"Natural topics: {', '.join(self.location.conversation_modifiers)}")
        print(f"\nCharacters Present:")

        for name in self.characters_present:
            char = self.game_state.get_character(name)
            if char:
                rapport_bar = "█" * char.rapport + "░" * (20 - char.rapport)
                print(f"\n  {char.name} ({char.occupation})")
                print(f"    Mood: {char.emotional_state}")
                print(f"    Rapport: [{rapport_bar}] {char.rapport}/20")

                if char.active_phs:
                    print(f"    🎯 Active PHS: {len(char.active_phs)}/{char.max_phs}")

        print("\n" + "="*70)
        input("\nPress Enter to continue...")

    def eavesdrop_on_cooking_talk(self):
        """Listen to kitchen conversation"""
        print("\n" + "="*70)
        print("YOU LISTEN TO THE KITCHEN TALK")
        print("="*70)
        print("\nYou keep quiet, hands busy with tasks, ears open...")
        print()

        import random
        if len(self.characters_present) >= 2:
            speakers = random.sample(self.characters_present, min(2, len(self.characters_present)))

            for speaker_name in speakers:
                char = self.game_state.get_character(speaker_name)
                if char:
                    context = f"You're in the kitchen helping cook. Make a brief, natural comment about cooking, family, or daily life. Kitchen conversation is more casual and personal than dining room talk."

                    comment = self.llm.get_character_response(
                        char,
                        "[Casual kitchen conversation]",
                        scene_context=context
                    )

                    print(f"{speaker_name}: {comment}\n")

        else:
            print("The kitchen is quiet except for the sounds of cooking.")
            print("Sometimes silence reveals as much as conversation.")

        print("="*70)
        print("\nYou've observed the dynamics. Knowledge is power.")

        # Small SP reward
        self.game_state.add_sp(1, "Patient observation")

        input("\nPress Enter to continue...")

    def run(self):
        """Main kitchen scene loop"""
        self.start_scene()

        while self.scene_active:
            print(f"\n{'='*70}")
            print(f"SP: {self.game_state.player.suggestion_points} | " +
                  f"Stage: {self.cooking_stage.title()} | " +
                  f"Privacy: {self.privacy_level.upper()}")
            print(f"{'='*70}")

            options = [
                "Talk to someone",
                "Plant a suggestion",
                "Help with cooking (+Rapport)",
                "Observe the kitchen",
                "Listen to kitchen talk",
                "View character details",
                "View clothing details",
                "Change someone's clothing",
                "View skill tree",
                "Study hypnosis",
                "Advance cooking stage",
                "View your status",
                "Save game",
                "Leave kitchen"
            ]

            choice = self.display_menu(options)

            if choice == -1:  # Interrupted
                break

            if choice == 1:  # Talk to someone
                if not self.characters_present:
                    print("\nThe kitchen is empty right now.")
                    input("Press Enter to continue...")
                    continue

                print("\nWho do you want to talk to?")
                char_options = self.characters_present + ["Back"]
                char_choice = self.display_menu(char_options)

                if char_choice != -1 and char_choice <= len(self.characters_present):
                    self.talk_to_character(self.characters_present[char_choice - 1])

            elif choice == 2:  # Plant suggestion
                if not self.characters_present:
                    print("\nNo one is here to plant suggestions on.")
                    input("Press Enter to continue...")
                    continue

                print("\nWho do you want to plant a suggestion on?")
                char_options = self.characters_present + ["Back"]
                char_choice = self.display_menu(char_options)

                if char_choice != -1 and char_choice <= len(self.characters_present):
                    self.plant_suggestion_menu(self.characters_present[char_choice - 1])

            elif choice == 3:  # Help with cooking
                self.help_with_cooking()

            elif choice == 4:  # Observe
                self.observe_kitchen()

            elif choice == 5:  # Listen
                self.eavesdrop_on_cooking_talk()

            elif choice == 6:  # View character details
                if not self.characters_present:
                    print("\nNo one is here.")
                    input("Press Enter to continue...")
                    continue

                print("\nWhich character?")
                char_options = self.characters_present + ["Back"]
                char_choice = self.display_menu(char_options)

                if char_choice != -1 and char_choice <= len(self.characters_present):
                    self.view_character_status(self.characters_present[char_choice - 1])

            elif choice == 7:  # View clothing details
                if not self.characters_present:
                    print("\nNo one is here.")
                    input("Press Enter to continue...")
                    continue

                print("\nWhich character's clothing?")
                char_options = self.characters_present + ["Back"]
                char_choice = self.display_menu(char_options)

                if char_choice != -1 and char_choice <= len(self.characters_present):
                    self.view_clothing_details(self.characters_present[char_choice - 1])

            elif choice == 8:  # Change someone's clothing
                if not self.characters_present:
                    print("\nNo one is here.")
                    input("Press Enter to continue...")
                    continue

                print("\nWhose clothing do you want to change?")
                char_options = self.characters_present + ["Back"]
                char_choice = self.display_menu(char_options)

                if char_choice != -1 and char_choice <= len(self.characters_present):
                    self.change_character_clothing(self.characters_present[char_choice - 1])

            elif choice == 9:  # View skill tree
                self.view_skill_tree()

            elif choice == 10:  # Study hypnosis
                self.study_hypnosis()

            elif choice == 11:  # Advance stage
                if not self.advance_cooking_stage():
                    print("\nThe meal is complete and cleanup is done.")
                    print("Time to move to another location.")
                    self.scene_active = False

            elif choice == 12:  # Status
                self.game_state.display_status()
                input("\nPress Enter to continue...")

            elif choice == 13:  # Save
                if self.game_state.save_game():
                    print("\n✓ Game saved successfully!")
                else:
                    print("\n✗ Failed to save game")
                input("\nPress Enter to continue...")

            elif choice == 14:  # Leave kitchen
                print("\nLeave the kitchen?")
                print("1. Yes, leave")
                print("2. No, stay")

                leave_choice = self.display_menu(["Yes, leave", "No, stay"], "")

                if leave_choice == 1:
                    self.scene_active = False

        # Scene complete
        print("\n" + "="*70)
        print("LEAVING KITCHEN")
        print("="*70)
        print("\nYou step out of the kitchen. The conversations you had here")
        print("were more intimate, more revealing than those at the dinner table.")
        print("\nThe seeds planted in private spaces grow differently.")
        print("="*70 + "\n")

        self.game_state.complete_scene(self.get_name())
        input("Press Enter to continue...")
