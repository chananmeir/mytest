"""
Your Room Scene - Most intimate, private setting for deep manipulation
"""
from typing import List
from scenes.base_scene import BaseScene
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.location_system import get_location, get_characters_at_location
from systems.time_system import get_current_period


class YourRoomScene(BaseScene):
    """
    Your private bedroom. The most intimate setting in the game.

    VERY HIGH PRIVACY - Only one person visits at a time. Perfect for:
    - Deep, vulnerable conversations
    - Planting powerful suggestions
    - Building maximum rapport
    - Revealing and learning secrets

    This is where the real work happens. Away from prying eyes and ears.
    """

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        super().__init__(game_state, llm_handler)

        # Load location data
        self.location = get_location('home_your_room')

        # Your room specific state
        self.conversation_depth = 'surface'  # surface, personal, vulnerable, intimate
        self.privacy_level = 'very_high'  # One-on-one only, easiest suggestions

        # Only allow ONE visitor at a time
        self.current_visitor = None
        self.update_available_characters()

    def update_available_characters(self):
        """Update who might visit based on game time"""
        if hasattr(self.game_state, 'current_time'):
            period = get_current_period(self.game_state.current_time)
        else:
            period = 'night'  # Your room is typically visited at night

        # Get characters who might visit
        scheduled_chars = get_characters_at_location('home_your_room', period)

        # Filter to existing characters
        potential_visitors = [
            name for name in scheduled_chars
            if self.game_state.get_character(name) is not None
        ]

        # Your room: typically Tom, Sophie, Rachel, or James visit
        # But only ONE at a time
        if not self.current_visitor and potential_visitors:
            import random
            self.current_visitor = random.choice(potential_visitors)

        self.characters_present = [self.current_visitor] if self.current_visitor else []

    def get_name(self) -> str:
        return "Your Room - Private Space"

    def get_description(self) -> str:
        base_desc = self.location.description

        if self.conversation_depth == 'surface':
            return f"""{base_desc}

This is YOUR territory. A private sanctuary. When someone enters your room,
they're entering your world on your terms. The power dynamic shifts here.

Privacy Level: VERY HIGH
- No interruptions
- No witnesses
- No judgment
- Complete focus on one person

This is the ideal environment for deep hypnotic work. Suggestions planted
here, in this intimate setting, have the highest chance of taking root.

But getting someone to come to your room requires trust. They have to feel
safe with you. Paradoxically, you need rapport before you can truly exploit
the privacy."""

        elif self.conversation_depth == 'personal':
            return """The conversation has moved beyond small talk. You're discussing real things -
feelings, frustrations, desires. When someone opens up in a private space like this,
they're in a heightened state of receptivity.

Their guard is partially down. They want to be understood. They want validation.
They want someone to really listen.

This is when casual suggestions become powerful commands. The words you plant
now will echo in their private thoughts, in their solitary moments."""

        elif self.conversation_depth == 'vulnerable':
            return """They're being truly vulnerable now. Admitting fears, insecurities, shameful thoughts.
Things they wouldn't say anywhere else, to anyone else.

This is dangerous territory - for them and for you. Handle this wrong and you
destroy the trust forever. Handle it right and you have access to their deepest
psychological levers.

The suggestions you plant in moments of raw vulnerability become part of their
core identity. Choose your words with extreme care."""

        else:  # intimate
            return """You've reached complete intimacy. Total emotional nakedness. In this state,
the boundary between suggestion and core belief dissolves.

This is the goal - to be trusted so completely that your ideas become their ideas.
Your desires become their desires. Your will becomes their will.

This is not magic. This is not mysticism. This is the natural result of deep
rapport combined with psychological technique in a private, safe space.

Use this power wisely. Or don't. That choice defines who you really are."""

    def get_available_characters(self) -> List[str]:
        return self.characters_present

    def start_scene(self):
        """Initialize your room scene"""
        self.display_scene_header()

        if self.current_visitor:
            print(f"\n{self.current_visitor} knocks on your door.")
            print("They've chosen to come to YOUR space. That's significant.")

            visitor = self.game_state.get_character(self.current_visitor)

            if visitor:
                print(f"\nYou: \"Come in.\"")
                print(f"\n{self.current_visitor} enters and closes the door behind them.")
                print(f"\n{self.current_visitor}: ", end="", flush=True)

                opening = self.llm.get_character_response(
                    visitor,
                    "[Entering player's private bedroom]",
                    scene_context=f"You've chosen to visit your unemployed family member in their bedroom for a private conversation. {self.location.description}"
                )
                print(opening)
        else:
            print("\nYour room is empty. A quiet refuge.")
            print("You could invite someone here for a private conversation...")

        print("\n" + "-"*70)
        print("Your room - VERY HIGH PRIVACY.")
        print("One-on-one conversations. No witnesses. Perfect for deep work.")
        print("Suggestions planted here have the HIGHEST success rate.")
        print(f"Privacy Level: {self.privacy_level.upper()}")
        print("-"*70)

        input("\nPress Enter to continue...")

    def deepen_conversation(self):
        """Move to deeper conversation level"""
        depths = ['surface', 'personal', 'vulnerable', 'intimate']
        current_idx = depths.index(self.conversation_depth)

        if not self.current_visitor:
            print("\nNo one is here to have a deep conversation with.")
            input("Press Enter to continue...")
            return False

        visitor = self.game_state.get_character(self.current_visitor)

        if visitor.rapport < 6:
            print(f"\n✗ Not enough rapport with {self.current_visitor} (need 6+)")
            print("They don't trust you enough for deeper conversations yet.")
            input("Press Enter to continue...")
            return False

        if current_idx < len(depths) - 1:
            self.conversation_depth = depths[current_idx + 1]
            print(f"\n{'='*70}")
            print(f"--- CONVERSATION DEPTH: {self.conversation_depth.upper()} ---")
            print(f"{'='*70}")
            print(self.get_description())
            print(f"{'='*70}\n")

            # Bonus rapport for reaching deeper levels
            rapport_gain = 2
            visitor.rapport = min(20, visitor.rapport + rapport_gain)
            print(f"✓ Deeper connection with {self.current_visitor}")
            print(f"  Rapport: +{rapport_gain} (now {visitor.rapport}/20)\n")

            # Bonus SP for achieving intimate conversations
            if self.conversation_depth == 'intimate':
                self.game_state.add_sp(3, "Achieving complete intimacy")

            input("Press Enter to continue...")
            return True
        else:
            print("\nYou're already at maximum conversation depth.")
            input("Press Enter to continue...")
            return False

    def invite_someone(self):
        """Invite a specific person to your room"""
        print("\n" + "="*70)
        print("INVITE SOMEONE TO YOUR ROOM")
        print("="*70)

        if self.current_visitor:
            print(f"\n{self.current_visitor} is already here.")
            print("Only one person at a time in this private space.")
            input("\nPress Enter to continue...")
            return

        # Get all characters
        all_chars = list(self.game_state.characters.keys())

        if not all_chars:
            print("\nNo one is available.")
            input("Press Enter to continue...")
            return

        print("\nWho do you want to invite?")
        options = all_chars + ["Cancel"]
        choice = self.display_menu(options)

        if choice == -1 or choice > len(all_chars):
            return

        invited_name = all_chars[choice - 1]
        invited = self.game_state.get_character(invited_name)

        # Check rapport requirement
        if invited.rapport < 4:
            print(f"\n✗ {invited_name} doesn't trust you enough to visit your room.")
            print(f"   Rapport needed: 4, Current: {invited.rapport}")
            input("\nPress Enter to continue...")
            return

        # They accept
        self.current_visitor = invited_name
        self.characters_present = [invited_name]
        self.conversation_depth = 'surface'  # Reset depth

        print(f"\n✓ {invited_name} agrees to come to your room.")
        print("\nA few minutes later, they knock on your door...")

        context = "Your family member has invited you to their bedroom for a private conversation. You've accepted because you trust them enough."

        response = self.llm.get_character_response(
            invited,
            "[Entering player's room after invitation]",
            scene_context=context
        )

        print(f"\n{invited_name}: {response}")
        input("\nPress Enter to continue...")

    def run(self):
        """Main your room scene loop"""
        self.start_scene()

        while self.scene_active:
            visitor_name = self.current_visitor or "None"
            print(f"\n{'='*70}")
            print(f"SP: {self.game_state.player.suggestion_points} | " +
                  f"Depth: {self.conversation_depth.title()} | " +
                  f"Privacy: {self.privacy_level.upper()}")
            print(f"Visitor: {visitor_name}")
            print(f"{'='*70}")

            if self.current_visitor:
                options = [
                    "Talk to them",
                    "Plant a suggestion (OPTIMAL - Very High Privacy)",
                    "Deepen the conversation",
                    "View their profile",
                    "View skill tree",
                    "Study hypnosis",
                    "View your status",
                    "Ask them to leave",
                    "Save game",
                    "Leave your room"
                ]
            else:
                options = [
                    "Invite someone to your room",
                    "View skill tree",
                    "Study hypnosis",
                    "View your status",
                    "Save game",
                    "Leave your room"
                ]

            choice = self.display_menu(options)

            if choice == -1:
                break

            if self.current_visitor:
                # Options when someone is present
                if choice == 1:  # Talk
                    self.talk_to_character(self.current_visitor)

                elif choice == 2:  # Plant suggestion
                    print("\n✓ OPTIMAL CONDITIONS FOR SUGGESTION PLANTING")
                    print("Very high privacy. One-on-one. No witnesses.")
                    print("Success rate is maximized here.")
                    print()
                    self.plant_suggestion_menu(self.current_visitor)

                elif choice == 3:  # Deepen
                    self.deepen_conversation()

                elif choice == 4:  # Profile
                    self.view_character_status(self.current_visitor)

                elif choice == 5:  # Skill tree
                    self.view_skill_tree()

                elif choice == 6:  # Study
                    self.study_hypnosis()

                elif choice == 7:  # Status
                    self.game_state.display_status()
                    input("\nPress Enter to continue...")

                elif choice == 8:  # Ask to leave
                    print(f"\nYou politely indicate the conversation is over.")
                    print(f"{self.current_visitor} says goodbye and leaves your room.")
                    self.current_visitor = None
                    self.characters_present = []
                    self.conversation_depth = 'surface'
                    input("\nPress Enter to continue...")

                elif choice == 9:  # Save
                    if self.game_state.save_game():
                        print("\n✓ Game saved successfully!")
                    else:
                        print("\n✗ Failed to save game")
                    input("\nPress Enter to continue...")

                elif choice == 10:  # Leave
                    if self.current_visitor:
                        print(f"\nYou leave your room with {self.current_visitor} still there?")
                        leave_choice = self.display_menu(["Yes, leave anyway", "No, stay"], "")
                        if leave_choice == 1:
                            self.scene_active = False
                    else:
                        self.scene_active = False

            else:
                # Options when alone
                if choice == 1:  # Invite
                    self.invite_someone()

                elif choice == 2:  # Skill tree
                    self.view_skill_tree()

                elif choice == 3:  # Study
                    self.study_hypnosis()

                elif choice == 4:  # Status
                    self.game_state.display_status()
                    input("\nPress Enter to continue...")

                elif choice == 5:  # Save
                    if self.game_state.save_game():
                        print("\n✓ Game saved successfully!")
                    else:
                        print("\n✗ Failed to save game")
                    input("\nPress Enter to continue...")

                elif choice == 6:  # Leave
                    self.scene_active = False

        # Scene complete
        print("\n" + "="*70)
        print("LEAVING YOUR ROOM")
        print("="*70)
        print("\nYou step out of your private sanctuary.")
        print("What was said in that room stays in that room.")
        print("\nBut the suggestions planted in private will manifest in public.")
        print("="*70 + "\n")

        self.game_state.complete_scene(self.get_name())
        input("Press Enter to continue...")
