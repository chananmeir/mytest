"""
Living Room Scene - Social gathering space with group dynamics
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.location_system import get_location, get_characters_at_location
from systems.time_system import get_current_period


class LivingRoomScene(BaseScene):
    """
    The living room at home. A casual social space where family members gather.
    TV watching, gaming, casual conversations. This is a low-privacy location
    where group dynamics are visible but planting suggestions is harder due to
    multiple observers.

    Good for observing interactions and listening to group conversations.
    """

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)

        # Load location data
        self.location = get_location('home_living_room')

        # Living room specific state
        self.activity = 'casual_hangout'  # casual_hangout, watching_tv, game_night, late_night
        self.privacy_level = 'low'  # Multiple people, harder to plant suggestions

        # Determine who's in the living room based on time
        self.update_available_characters()

    def update_available_characters(self):
        """Update who's available based on game time"""
        if hasattr(self.game_state, 'current_time'):
            period = get_current_period(self.game_state.current_time)
        else:
            period = 'evening'

        # Get characters at living room location
        scheduled_chars = get_characters_at_location('home_living_room', period)

        # Filter to only characters that exist in game state
        self.characters_present = [
            name for name in scheduled_chars
            if self.game_state.get_character(name) is not None
        ]

        # Living room usually has multiple people - ensure at least 2
        if len(self.characters_present) < 2:
            # Add James (he's always gaming here) and Tom
            for name in ['James', 'Tom', 'Lisa']:
                if name not in self.characters_present and self.game_state.get_character(name):
                    self.characters_present.append(name)
                    if len(self.characters_present) >= 2:
                        break

    def get_name(self) -> str:
        return "Living Room - Home"

    def get_description(self) -> str:
        base_desc = self.location.description

        if self.activity == 'casual_hangout':
            return f"""{base_desc}

The living room is the social hub of the house. Multiple family members drift in and out,
making this a public space within the home. Privacy is low - others can overhear your
conversations, see your interactions.

This makes planting suggestions risky (others might notice), but it's perfect for:
- Observing group dynamics
- Seeing how characters interact with each other
- Listening to multiple conversations
- Building rapport through casual participation

The lack of privacy is both a challenge and an opportunity. When multiple people are
present, they influence each other - sometimes amplifying, sometimes contradicting
your efforts."""

        elif self.activity == 'watching_tv':
            return """The family has gathered around the TV. Everyone's attention is on the screen,
creating a strange dynamic - they're together but separately focused.

This semi-distracted state can be useful. People's guards are down when they're
absorbed in entertainment. Casual comments made during commercials or boring scenes
can slip into minds more easily.

But be careful - multiple witnesses mean any misstep will be noticed."""

        elif self.activity == 'game_night':
            return """Board games and card games are spread across the coffee table. Competition
brings out people's true personalities - who cheats, who's gracious in defeat, who
takes it too seriously.

The playful atmosphere lowers defenses. Suggestions planted during games,
disguised as jokes or game banter, can be surprisingly effective.

Watch the dynamics. Alliances form and break. Old grudges surface. Knowledge is power."""

        else:  # late_night
            return """It's late. Most have gone to bed, but a few night owls remain in the living room.
The house is quiet. Guards are down. Late-night conversations have a different quality -
more honest, more vulnerable.

This is when secrets come out. When people admit things they wouldn't say in daylight.
The privacy is better now, but opportunities are limited to whoever's still awake."""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        """Initialize the living room scene"""
        self.display_scene_header()

        print("\nYou enter the living room. The familiar space where the family relaxes.")

        # Describe who's here and what they're doing
        if self.characters_present:
            print(f"\nPresent: {', '.join(self.characters_present)}")

            # Get first character to acknowledge you
            greeter_name = self.characters_present[0]
            greeter = self.game_state.get_character(greeter_name)

            if greeter:
                print(f"\n{greeter_name} glances up as you enter.")
                print(f"\n{greeter_name}: ", end="", flush=True)

                opening = self.llm.get_character_response(
                    greeter,
                    "[Player has just entered the living room]",
                    scene_context=f"You're in the living room with other family members when your unemployed relative enters. {self.location.description}"
                )
                print(opening)

        print("\n" + "-"*70)
        print("The living room is a group setting - low privacy.")
        print("Multiple people are watching. Manipulation is risky here.")
        print("But observing group dynamics can reveal useful information.")
        print(f"Privacy Level: {self.privacy_level.upper()} - High suggestion difficulty")
        print("-"*70)

        input("\nPress Enter to continue...")

    def change_activity(self):
        """Switch to a different activity"""
        activities = ['casual_hangout', 'watching_tv', 'game_night', 'late_night']
        current_idx = activities.index(self.activity)

        if current_idx < len(activities) - 1:
            self.activity = activities[current_idx + 1]
            print(f"\n{'='*70}")
            print(f"--- {self.activity.replace('_', ' ').upper()} ---")
            print(f"{'='*70}")
            print(self.get_description())
            print(f"{'='*70}\n")

            # Update characters for new activity
            self.update_available_characters()

            input("Press Enter to continue...")
            return True
        else:
            return False

    def join_activity(self):
        """Participate in the group activity"""
        print("\n" + "="*70)
        print("YOU JOIN THE GROUP")
        print("="*70)
        print("\nYou genuinely participate in what everyone's doing.")
        print()

        if self.characters_present:
            import random
            # Get reactions from 1-2 characters
            reactors = random.sample(self.characters_present, min(2, len(self.characters_present)))

            for reactor_name in reactors:
                reactor = self.game_state.get_character(reactor_name)
                if reactor:
                    # Small rapport boost for social participation
                    rapport_gain = 1
                    reactor.rapport = min(20, reactor.rapport + rapport_gain)

                    print(f"✓ Rapport with {reactor_name}: +{rapport_gain} (now {reactor.rapport}/20)")

                    context = f"Your unemployed family member is joining in the living room activity ({self.activity}). Make a brief, friendly comment."

                    comment = self.llm.get_character_response(
                        reactor,
                        "[Player joins group activity]",
                        scene_context=context
                    )

                    print(f"\n{reactor_name}: {comment}\n")

        print("="*70)
        print("Being social builds rapport, even without manipulation.")
        print("="*70)
        input("\nPress Enter to continue...")

    def observe_group_dynamics(self):
        """Watch how characters interact with each other"""
        print("\n" + "="*70)
        print("YOU OBSERVE THE GROUP DYNAMICS")
        print("="*70)
        print("\nYou fade into the background, watching how they interact...")
        print()

        if len(self.characters_present) >= 2:
            import random
            # Show interaction between two characters
            pair = random.sample(self.characters_present, 2)

            print(f"You notice an interaction between {pair[0]} and {pair[1]}:")
            print()

            for speaker_name in pair:
                char = self.game_state.get_character(speaker_name)
                if char:
                    context = f"You're in the living room with other family members. Have a brief interaction with {pair[1] if speaker_name == pair[0] else pair[0]}. Show your personality and current feelings."

                    comment = self.llm.get_character_response(
                        char,
                        f"[Interacting with {pair[1] if speaker_name == pair[0] else pair[0]}]",
                        scene_context=context
                    )

                    print(f"{speaker_name}: {comment}\n")

            # Reward for observation
            self.game_state.add_sp(1, "Observing group dynamics")
            print("="*70)
            print("You learn how they influence each other.")
            print("Understanding the web of relationships is crucial.")
            print("="*70)
        else:
            print("Not enough people here for interesting group dynamics.")
            print("="*70)

        input("\nPress Enter to continue...")

    def run(self):
        """Main living room scene loop"""
        self.start_scene()

        while self.scene_active:
            print(f"\n{'='*70}")
            print(f"SP: {self.game_state.player.suggestion_points} | " +
                  f"Activity: {self.activity.replace('_', ' ').title()} | " +
                  f"Privacy: {self.privacy_level.upper()}")
            print(f"People present: {len(self.characters_present)}")
            print(f"{'='*70}")

            options = [
                "Talk to someone",
                "Plant a suggestion (RISKY - Low Privacy)",
                "Join the group activity (+Rapport)",
                "Observe group dynamics",
                "View character details",
                "View skill tree",
                "Study hypnosis",
                "Change activity",
                "View your status",
                "Save game",
                "Leave living room"
            ]

            choice = self.display_menu(options)

            if choice == -1:
                break

            if choice == 1:  # Talk
                if not self.characters_present:
                    print("\nThe living room is empty right now.")
                    input("Press Enter to continue...")
                    continue

                print("\nWho do you want to talk to?")
                print("⚠️ Warning: Others may overhear in this public space")
                char_options = self.characters_present + ["Back"]
                char_choice = self.display_menu(char_options)

                if char_choice != -1 and char_choice <= len(self.characters_present):
                    self.talk_to_character(self.characters_present[char_choice - 1])

            elif choice == 2:  # Plant suggestion
                if not self.characters_present:
                    print("\nNo one is here.")
                    input("Press Enter to continue...")
                    continue

                print("\n⚠️ WARNING: LOW PRIVACY LOCATION")
                print("Multiple people are present. Planting suggestions here is RISKY.")
                print("Others may notice your manipulation attempt.")
                print()
                print("Continue anyway?")
                confirm = input("Type 'yes' to proceed: ").strip().lower()

                if confirm == 'yes':
                    print("\nWho do you want to plant a suggestion on?")
                    char_options = self.characters_present + ["Back"]
                    char_choice = self.display_menu(char_options)

                    if char_choice != -1 and char_choice <= len(self.characters_present):
                        self.plant_suggestion_menu(self.characters_present[char_choice - 1])

            elif choice == 3:  # Join activity
                self.join_activity()

            elif choice == 4:  # Observe
                self.observe_group_dynamics()

            elif choice == 5:  # Character details
                if not self.characters_present:
                    print("\nNo one is here.")
                    input("Press Enter to continue...")
                    continue

                print("\nWhich character?")
                char_options = self.characters_present + ["Back"]
                char_choice = self.display_menu(char_options)

                if char_choice != -1 and char_choice <= len(self.characters_present):
                    self.view_character_status(self.characters_present[char_choice - 1])

            elif choice == 6:  # Skill tree
                self.view_skill_tree()

            elif choice == 7:  # Study
                self.study_hypnosis()

            elif choice == 8:  # Change activity
                if not self.change_activity():
                    print("\nTime to move on to something else.")
                    self.scene_active = False

            elif choice == 9:  # Status
                self.game_state.display_status()
                input("\nPress Enter to continue...")

            elif choice == 10:  # Save
                if self.game_state.save_game():
                    print("\n✓ Game saved successfully!")
                else:
                    print("\n✗ Failed to save game")
                input("\nPress Enter to continue...")

            elif choice == 11:  # Leave
                print("\nLeave the living room?")
                leave_choice = self.display_menu(["Yes, leave", "No, stay"], "")

                if leave_choice == 1:
                    self.scene_active = False

        # Scene complete
        print("\n" + "="*70)
        print("LEAVING LIVING ROOM")
        print("="*70)
        print("\nYou step away from the social space.")
        print("You've learned more about how they interact as a group.")
        print("\nGroup dynamics are complex. Everyone influences everyone.")
        print("="*70 + "\n")

        self.game_state.complete_scene(self.get_name())
        input("Press Enter to continue...")
