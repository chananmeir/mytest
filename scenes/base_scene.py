"""
Base scene class for Family Dynamics RPG
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.hypnosis import HypnosisSystem
from systems.game_master import GameMaster
from systems.memory import MemorySystem


class BaseScene(ABC):
    """Abstract base class for game scenes"""

    def __init__(self, game_state: GameState, llm_handler: LLMHandler):
        self.game_state = game_state
        self.llm = llm_handler
        self.hypnosis = HypnosisSystem()
        self.gm = GameMaster()
        self.memory = MemorySystem()
        self.scene_active = True

    @abstractmethod
    def get_name(self) -> str:
        """Return the scene name"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Return the scene description"""
        pass

    @abstractmethod
    def start_scene(self):
        """Initialize and display the scene opening"""
        pass

    @abstractmethod
    def get_available_characters(self) -> List[str]:
        """Return list of character names present in this scene"""
        pass

    def display_scene_header(self):
        """Display formatted scene header"""
        print("\n" + "="*70)
        print(f"SCENE: {self.get_name()}")
        print("="*70)
        print(self.get_description())
        print("="*70 + "\n")

    def display_menu(self, options: List[str], title: str = "What do you do?") -> int:
        """Display a menu and get user choice"""
        print(f"\n{title}")
        print("-" * 40)

        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        print()

        while True:
            try:
                choice = input("Enter your choice: ").strip()
                choice_num = int(choice)

                if 1 <= choice_num <= len(options):
                    return choice_num
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nGame interrupted.")
                return -1

    def talk_to_character(self, character_name: str):
        """Have a conversation with a character"""
        char = self.game_state.get_character(character_name)

        if not char:
            print(f"Character {character_name} not found.")
            return

        print(f"\n--- Talking to {character_name} ---")
        print(f"Rapport: {char.rapport}/20 | Emotional State: {char.emotional_state}")
        print(f"Resistance: {char.resistance}% | Active PHS: {len(char.active_phs)}/{char.max_phs}")
        print()

        while True:
            player_input = input("You say (or 'back' to end conversation): ").strip()

            if not player_input:
                continue

            if player_input.lower() in ['back', 'exit', 'quit']:
                print(f"\nYou end the conversation with {character_name}.\n")
                break

            # Get response from LLM (automatically records memory)
            print(f"\n{character_name}: ", end="", flush=True)
            response = self.llm.get_character_response(
                char,
                player_input,
                scene_context=self.get_description(),
                record_memory=True
            )
            print(response)

            # Analyze the interaction using GM
            analysis = self.gm.analyze_conversation_impact(
                character=char,
                player_message=player_input,
                character_response=response,
                scene_context=self.get_description()
            )

            # Apply changes
            if analysis['rapport_change'] != 0:
                if analysis['rapport_change'] > 0:
                    message = self.hypnosis.build_rapport(
                        self.game_state,
                        character_name,
                        abs(analysis['rapport_change']),
                        analysis['reasoning']
                    )
                else:
                    char.reduce_rapport(abs(analysis['rapport_change']))
                    message = f"Rapport with {character_name} decreased: {char.rapport}/20 ({analysis['reasoning']})"

                print(f"\n[{message}]")

            # Update emotional state if changed
            if analysis['new_emotional_state'] != char.emotional_state:
                message = self.hypnosis.change_emotional_state(
                    self.game_state,
                    character_name,
                    analysis['new_emotional_state'],
                    analysis['reasoning']
                )
                print(f"[{message}]")

            print()

    def plant_suggestion_menu(self, character_name: str):
        """Menu for planting post-hypnotic suggestions"""
        from systems.hypnosis_knowledge import HYPNOSIS_TECHNIQUES

        char = self.game_state.get_character(character_name)

        if not char:
            print(f"Character {character_name} not found.")
            return

        knowledge = self.game_state.player.hypnosis_knowledge

        print(f"\n{'='*70}")
        print(f"PLANT SUGGESTION ON {character_name.upper()}")
        print(f"{'='*70}")
        print(f"Available SP: {self.game_state.player.suggestion_points}")
        print()

        # Check technique requirements for each type
        technique_reqs = {
            'emotional_nudge': 'emotional_anchoring',
            'behavioral_prompt': 'embedded_commands',
            'strong_anchor': 'post_hypnotic_suggestion'
        }

        has_emotional = knowledge.knows_technique(technique_reqs['emotional_nudge'])
        has_behavioral = knowledge.knows_technique(technique_reqs['behavioral_prompt'])
        has_strong = knowledge.knows_technique(technique_reqs['strong_anchor'])

        # Check if ANY technique is known
        if not has_emotional and not has_behavioral and not has_strong:
            print("❌ YOU DON'T KNOW ANY HYPNOSIS TECHNIQUES YET!")
            print()
            print("You need to learn hypnosis techniques before planting suggestions.")
            print()
            print("What you need to learn:")
            print(f"  • {HYPNOSIS_TECHNIQUES['emotional_anchoring'].name} → Emotional Nudge (2 SP)")
            print(f"  • {HYPNOSIS_TECHNIQUES['embedded_commands'].name} → Behavioral Prompt (3 SP)")
            print(f"  • {HYPNOSIS_TECHNIQUES['post_hypnotic_suggestion'].name} → Strong Anchor (4-6 SP)")
            print()
            print("💡 TIP: Choose 'Study hypnosis' from the main menu to learn techniques!")
            print("="*70)
            input("\nPress Enter to continue...")
            return

        # Check general requirements (rapport, emotional state)
        can_plant_general, general_message = self.hypnosis.can_plant_phs(self.game_state, character_name)

        print("AVAILABLE SUGGESTION TYPES:")
        print("-" * 70)

        # Show each option with technique status
        print(f"\n1. Emotional Nudge ({self.hypnosis.EMOTIONAL_NUDGE_COST} SP)")
        print(f"   Requires: {HYPNOSIS_TECHNIQUES['emotional_anchoring'].name}")
        if has_emotional:
            print(f"   Status: ✓ You know this technique")
        else:
            print(f"   Status: ✗ Learn this technique first!")

        print(f"\n2. Behavioral Prompt ({self.hypnosis.BEHAVIORAL_PROMPT_COST} SP)")
        print(f"   Requires: {HYPNOSIS_TECHNIQUES['embedded_commands'].name}")
        if has_behavioral:
            print(f"   Status: ✓ You know this technique")
        else:
            print(f"   Status: ✗ Learn this technique first!")

        print(f"\n3. Strong Anchor ({self.hypnosis.STRONG_ANCHOR_COST_MIN}-{self.hypnosis.STRONG_ANCHOR_COST_MAX} SP)")
        print(f"   Requires: {HYPNOSIS_TECHNIQUES['post_hypnotic_suggestion'].name}")
        if has_strong:
            print(f"   Status: ✓ You know this technique")
        else:
            print(f"   Status: ✗ Learn this technique first!")

        print(f"\n4. Back")

        # Show general status
        print()
        print("-" * 70)
        if not can_plant_general:
            print(f"⚠️  General Status: {general_message}")
        else:
            print(f"✓ General Status: {general_message}")
        print("="*70)

        choice = input("\nChoice: ").strip()

        try:
            choice_num = int(choice)
        except ValueError:
            return

        if choice_num == 4 or choice_num < 1 or choice_num > 4:
            return

        # Check if they have the required technique
        if choice_num == 1 and not has_emotional:
            print(f"\n✗ You need to learn '{HYPNOSIS_TECHNIQUES['emotional_anchoring'].name}' first!")
            input("\nPress Enter to continue...")
            return
        elif choice_num == 2 and not has_behavioral:
            print(f"\n✗ You need to learn '{HYPNOSIS_TECHNIQUES['embedded_commands'].name}' first!")
            input("\nPress Enter to continue...")
            return
        elif choice_num == 3 and not has_strong:
            print(f"\n✗ You need to learn '{HYPNOSIS_TECHNIQUES['post_hypnotic_suggestion'].name}' first!")
            input("\nPress Enter to continue...")
            return

        # Check general requirements
        if not can_plant_general:
            print(f"\n✗ Cannot plant suggestion: {general_message}")
            input("\nPress Enter to continue...")
            return

        print("\nDefine the post-hypnotic suggestion:")
        trigger = input("Trigger (when...): ").strip()

        if not trigger:
            print("Cancelled.")
            return

        response = input("Response (they will...): ").strip()

        if not response:
            print("Cancelled.")
            return

        success = False
        result_message = ""

        if choice_num == 1:  # Emotional Nudge
            success, result_message = self.hypnosis.plant_emotional_nudge(
                self.game_state, character_name, trigger, response
            )
        elif choice_num == 2:  # Behavioral Prompt
            success, result_message = self.hypnosis.plant_behavioral_prompt(
                self.game_state, character_name, trigger, response
            )
        elif choice_num == 3:  # Strong Anchor
            try:
                sp_cost = int(input(f"SP to invest ({self.hypnosis.STRONG_ANCHOR_COST_MIN}-{self.hypnosis.STRONG_ANCHOR_COST_MAX}): "))
                success, result_message = self.hypnosis.plant_strong_anchor(
                    self.game_state, character_name, trigger, response, sp_cost
                )
            except ValueError:
                result_message = "Invalid SP amount"

        print(f"\n{'✓' if success else '✗'} {result_message}")
        input("\nPress Enter to continue...")

    def view_character_status(self, character_name: str):
        """View comprehensive character profile with all learned information"""
        char = self.game_state.get_character(character_name)

        if not char:
            print(f"Character {character_name} not found.")
            return

        # === HEADER ===
        print(f"\n{'='*70}")
        print(f"CHARACTER PROFILE: {char.name.upper()}")
        print(f"{'='*70}")

        # === BASIC INFO ===
        print(f"\n📋 BASIC INFORMATION")
        print("-" * 70)
        print(f"  Name: {char.name}")
        print(f"  Age: {char.age} years old")
        print(f"  Occupation: {char.occupation}")
        print(f"  Personality: {char.personality}")

        # === CURRENT STATUS ===
        print(f"\n📊 CURRENT STATUS")
        print("-" * 70)
        rapport_bar = "█" * char.rapport + "░" * (20 - char.rapport)
        rapport_desc = self._get_rapport_description(char.rapport)
        print(f"  Rapport: [{rapport_bar}] {char.rapport}/20 - {rapport_desc}")
        print(f"  Emotional State: {char.emotional_state.upper()}")
        print(f"  Resistance to Influence: {char.resistance}%")

        # === APPEARANCE ===
        print(f"\n👔 CURRENT APPEARANCE")
        print("-" * 70)
        print(f"  Wearing: {char.clothing}")
        print(f"  Meaning: {char.clothing_meaning}")

        if char.clothing_history and len(char.clothing_history) > 1:
            print(f"  (Changed outfit {len(char.clothing_history) - 1} time(s))")

        # === ACTIVE HYPNOTIC TRIGGERS ===
        print(f"\n🎯 HYPNOTIC INFLUENCES")
        print("-" * 70)
        if char.active_phs:
            print(f"  Active Suggestions: {len(char.active_phs)}/{char.max_phs}")
            print()
            for i, phs in enumerate(char.active_phs, 1):
                chance = phs.calculate_activation_chance()
                status = "🟢 STRONG" if chance >= 70 else "🟡 MODERATE" if chance >= 50 else "🔴 WEAK"
                print(f"  {i}. [{status}] {chance}% chance")
                print(f"     Trigger: \"{phs.trigger}\"")
                print(f"     Response: \"{phs.response}\"")
                print(f"     Reinforced: {phs.reinforcements} time(s)")
                print()
        else:
            print(f"  No active suggestions planted yet.")
            if char.rapport >= 6:
                print(f"  ✓ Rapport sufficient to plant suggestions (≥6 required)")
            else:
                print(f"  ✗ Need {6 - char.rapport} more rapport to plant suggestions")

        # === WHAT YOU'VE LEARNED (MEMORIES) ===
        print(f"\n🧠 WHAT YOU'VE LEARNED")
        print("-" * 70)

        if hasattr(char, 'memories') and char.memories:
            # Get important memories
            important_memories = [m for m in char.memories if m.importance >= 6]
            recent_memories = sorted(char.memories, key=lambda m: m.timestamp, reverse=True)[:5]

            if important_memories:
                print(f"  Key Insights ({len(important_memories)} significant memories):")
                print()
                for i, mem in enumerate(important_memories[:5], 1):
                    mem_type_icon = self._get_memory_icon(mem.memory_type)
                    print(f"  {i}. {mem_type_icon} {mem.content}")
                    if mem.emotional_context:
                        print(f"     (They were feeling: {mem.emotional_context})")
                    print()

            if len(important_memories) > 5:
                print(f"  ... and {len(important_memories) - 5} more significant memories")
                print()
        else:
            print(f"  You haven't had any significant interactions yet.")
            print(f"  Talk to them to learn more!")

        # === CONVERSATION SUMMARY ===
        if hasattr(char, 'conversation_history') and char.conversation_history:
            total_exchanges = len([m for m in char.conversation_history if m.get('role') == 'user'])
            print(f"\n💬 CONVERSATION HISTORY")
            print("-" * 70)
            print(f"  Total exchanges: {total_exchanges}")

            # Show last 3 player messages
            user_messages = [m for m in char.conversation_history if m.get('role') == 'user']
            if user_messages:
                print(f"  Recent topics discussed:")
                for msg in user_messages[-3:]:
                    preview = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
                    print(f"    • \"{preview}\"")

        # === RELATIONSHIP ANALYSIS ===
        print(f"\n💭 RELATIONSHIP ANALYSIS")
        print("-" * 70)
        print(f"  {self._get_relationship_analysis(char)}")

        print("\n" + "="*70)

        # Interactive options
        print("\nWhat would you like to do?")
        print("1. Talk to them")
        print("2. Plant a suggestion")
        print("3. View clothing history")
        print("4. View all memories")
        print("5. Back to main menu")

        choice = input("\nChoice: ").strip()

        if choice == "1":
            self.talk_to_character(character_name)
        elif choice == "2":
            self.plant_suggestion_menu(character_name)
        elif choice == "3":
            self.view_clothing_details(character_name)
        elif choice == "4":
            self.view_all_memories(character_name)
        # else: back to menu

    def _get_rapport_description(self, rapport: int) -> str:
        """Get a text description of rapport level"""
        if rapport >= 18:
            return "Deep trust and connection"
        elif rapport >= 15:
            return "Strong bond"
        elif rapport >= 12:
            return "Good relationship"
        elif rapport >= 9:
            return "Developing trust"
        elif rapport >= 6:
            return "Cautious acceptance"
        elif rapport >= 3:
            return "Distant"
        else:
            return "Barely know each other"

    def _get_memory_icon(self, memory_type: str) -> str:
        """Get icon for memory type"""
        icons = {
            'conversation': '💬',
            'emotional_moment': '💝',
            'important_event': '⭐',
            'phs_planted': '🎯',
            'phs_triggered': '✨'
        }
        return icons.get(memory_type, '📝')

    def _get_relationship_analysis(self, char) -> str:
        """Generate relationship analysis based on stats"""
        analysis = []

        if char.rapport >= 15:
            analysis.append(f"{char.name} trusts you deeply and is highly receptive to your influence.")
        elif char.rapport >= 10:
            analysis.append(f"{char.name} feels comfortable around you and values your input.")
        elif char.rapport >= 6:
            analysis.append(f"{char.name} is open to conversations but still cautious.")
        else:
            analysis.append(f"{char.name} sees you as someone on the periphery of their life.")

        if char.emotional_state == "open":
            analysis.append("They're currently open and receptive.")
        elif char.emotional_state == "relaxed":
            analysis.append("They're relaxed and comfortable.")
        elif char.emotional_state == "defensive":
            analysis.append("They're guarded and protective right now.")
        elif char.emotional_state == "tense":
            analysis.append("There's tension that needs to be addressed.")

        if char.active_phs:
            analysis.append(f"Your suggestions are subtly shaping their behavior.")

        if char.resistance >= 70:
            analysis.append("Very resistant to influence - proceed carefully.")
        elif char.resistance >= 50:
            analysis.append("Moderately resistant to influence.")
        else:
            analysis.append("More susceptible to subtle suggestions.")

        return " ".join(analysis)

    def view_all_memories(self, character_name: str):
        """View all memories for a character"""
        char = self.game_state.get_character(character_name)

        if not char:
            print(f"Character {character_name} not found.")
            return

        print(f"\n{'='*70}")
        print(f"ALL MEMORIES: {char.name.upper()}")
        print(f"{'='*70}")

        if not hasattr(char, 'memories') or not char.memories:
            print("\nNo memories recorded yet.")
            input("\nPress Enter to continue...")
            return

        # Sort by importance and timestamp
        sorted_memories = sorted(char.memories, key=lambda m: (m.importance, m.timestamp), reverse=True)

        print(f"\nTotal memories: {len(sorted_memories)}")
        print()

        for i, mem in enumerate(sorted_memories, 1):
            icon = self._get_memory_icon(mem.memory_type)
            importance_bar = "★" * mem.importance + "☆" * (10 - mem.importance)

            print(f"{i}. {icon} [{importance_bar}] {mem.memory_type.upper()}")
            print(f"   {mem.content}")

            if mem.emotional_context:
                print(f"   Emotional context: {mem.emotional_context}")

            if mem.related_characters:
                print(f"   Related: {', '.join(mem.related_characters)}")

            # Parse and format timestamp
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(mem.timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
                print(f"   Time: {time_str}")
            except:
                pass

            print()

        print("="*70)
        input("\nPress Enter to continue...")

    def view_clothing_details(self, character_name: str):
        """View detailed clothing information and history for a character"""
        char = self.game_state.get_character(character_name)

        if not char:
            print(f"Character {character_name} not found.")
            return

        print(f"\n{'='*60}")
        print(f"{char.name}'s CLOTHING")
        print(f"{'='*60}")
        print(f"\nCURRENT OUTFIT:")
        print(f"  {char.clothing}")
        print(f"  Meaning: {char.clothing_meaning}")

        if char.clothing_history and len(char.clothing_history) > 1:
            print(f"\nCLOTHING HISTORY:")
            print("-" * 60)
            for i, entry in enumerate(reversed(char.clothing_history[-5:]), 1):
                timestamp = entry.get('timestamp', 'unknown')
                if timestamp != 'initial':
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        timestamp_str = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        timestamp_str = timestamp
                else:
                    timestamp_str = "Initial"

                print(f"{i}. [{timestamp_str}]")
                print(f"   Outfit: {entry.get('clothing', 'Unknown')}")
                print(f"   Occasion: {entry.get('occasion', 'unspecified')}")
                print()

        print("="*60)
        input("\nPress Enter to continue...")

    def change_character_clothing(self, character_name: str):
        """Change a character's clothing"""
        char = self.game_state.get_character(character_name)

        if not char:
            print(f"Character {character_name} not found.")
            return

        print(f"\n{'='*60}")
        print(f"CHANGE {char.name}'S CLOTHING")
        print(f"{'='*60}")
        print(f"\nCurrent: {char.clothing}")
        print(f"Meaning: {char.clothing_meaning}")
        print()

        new_clothing = input("New clothing description (or 'back' to cancel): ").strip()

        if not new_clothing or new_clothing.lower() == 'back':
            print("Cancelled.")
            input("\nPress Enter to continue...")
            return

        new_meaning = input("What does this outfit signify? (optional): ").strip()
        occasion = input("Occasion for change? (e.g., 'date night', 'work meeting'): ").strip()

        # Update clothing and record memory
        old_clothing = char.update_clothing(new_clothing, new_meaning, occasion)

        # Record memory of clothing change
        self.memory.record_clothing_change(
            char,
            old_clothing,
            new_clothing,
            occasion,
            importance=6
        )

        print(f"\n✓ {char.name}'s clothing updated!")
        print(f"  Old: {old_clothing}")
        print(f"  New: {new_clothing}")

        if occasion:
            print(f"  Occasion: {occasion}")

        # Award SP for attention to detail
        self.game_state.add_sp(1, f"Noted {char.name}'s appearance change")

        input("\nPress Enter to continue...")

    def view_skill_tree(self):
        """View hypnosis skill tree and learning progress"""
        from systems.hypnosis_knowledge import HYPNOSIS_TECHNIQUES

        knowledge = self.game_state.player.hypnosis_knowledge

        print(f"\n{'='*70}")
        print(f"HYPNOSIS SKILL TREE")
        print(f"{'='*70}")
        print(f"\nSkill Level: {knowledge.skill_level.upper()}")
        print(f"Techniques Mastered: {len(knowledge.known_techniques)}/11")

        # Get total bonuses
        sp_reduction, success_bonus = knowledge.get_total_bonuses()
        print(f"Total Bonuses: -{sp_reduction} SP cost, +{success_bonus}% success rate")

        # Organize techniques by category
        categories = {
            'basic': [],
            'intermediate': [],
            'advanced': [],
            'master': []
        }

        for name, technique in HYPNOSIS_TECHNIQUES.items():
            categories[technique.category].append((name, technique))

        # Display each category
        for category in ['basic', 'intermediate', 'advanced', 'master']:
            print(f"\n{category.upper()} TECHNIQUES")
            print("-" * 70)

            for tech_name, technique in categories[category]:
                # Check if known
                if knowledge.knows_technique(tech_name):
                    status = "✓ MASTERED"
                    icon = "🟢"
                elif tech_name in knowledge.learning_progress:
                    progress = knowledge.learning_progress[tech_name]
                    status = f"📚 LEARNING ({progress}%)"
                    icon = "🟡"
                else:
                    can_learn, reason = knowledge.can_learn_technique(tech_name)
                    if can_learn:
                        status = "🔓 AVAILABLE"
                        icon = "⚪"
                    else:
                        status = f"🔒 {reason}"
                        icon = "🔴"

                print(f"\n{icon} {technique.name}")
                print(f"   Status: {status}")
                print(f"   Effect: ", end="")

                effects = []
                if technique.sp_cost_reduction > 0:
                    effects.append(f"-{technique.sp_cost_reduction} SP")
                if technique.success_rate_bonus > 0:
                    effects.append(f"+{technique.success_rate_bonus}% success")
                print(", ".join(effects) if effects else "Foundation skill")

                print(f"   {technique.description}")

                if technique.prerequisites:
                    prereq_names = [HYPNOSIS_TECHNIQUES[p].name for p in technique.prerequisites]
                    print(f"   Prerequisites: {', '.join(prereq_names)}")

        print("\n" + "="*70)
        print("\nLEGEND:")
        print("  🟢 Mastered - You know this technique")
        print("  🟡 Learning - Currently studying this")
        print("  ⚪ Available - Ready to learn")
        print("  🔴 Locked - Learn prerequisites first")
        print("="*70)

        input("\nPress Enter to continue...")

    def study_hypnosis(self):
        """Study hypnosis through books or practice"""
        from systems.hypnosis_knowledge import LEARNING_RESOURCES, HYPNOSIS_TECHNIQUES

        knowledge = self.game_state.player.hypnosis_knowledge

        print(f"\n{'='*70}")
        print(f"STUDY HYPNOSIS")
        print(f"{'='*70}")
        print(f"\nCurrent Skill Level: {knowledge.skill_level.upper()}")
        print(f"Techniques Mastered: {len(knowledge.known_techniques)}/11")

        print(f"\nWhat would you like to do?")
        print("1. Read a book")
        print("2. Practice a technique")
        print("3. Research online")
        print("4. Back")

        choice = input("\nChoice: ").strip()

        if choice == "1":
            self._read_book()
        elif choice == "2":
            self._practice_technique()
        elif choice == "3":
            self._research_online()
        # else: back

    def _read_book(self):
        """Read a book to learn techniques"""
        from systems.hypnosis_knowledge import LEARNING_RESOURCES, HYPNOSIS_TECHNIQUES

        knowledge = self.game_state.player.hypnosis_knowledge

        print(f"\n{'='*70}")
        print(f"AVAILABLE BOOKS")
        print(f"{'='*70}")

        # Show available books
        available_books = []
        for book_id, book in LEARNING_RESOURCES.items():
            # Check if already read
            already_read = book_id in knowledge.books_read

            # Check what it teaches
            teaches_something_new = False
            for tech in book['teaches']:
                if tech not in knowledge.known_techniques:
                    teaches_something_new = True
                    break

            if teaches_something_new or not already_read:
                available_books.append((book_id, book, already_read))

        if not available_books:
            print("\nYou've mastered everything these books can teach!")
            input("\nPress Enter to continue...")
            return

        for i, (book_id, book, already_read) in enumerate(available_books, 1):
            status = "📖 READ" if already_read else "📕 UNREAD"
            print(f"\n{i}. [{status}] {book['title']}")
            print(f"   {book['description']}")

            # Show what it teaches
            teaches = []
            for tech_name in book['teaches']:
                tech = HYPNOSIS_TECHNIQUES[tech_name]
                if knowledge.knows_technique(tech_name):
                    teaches.append(f"✓ {tech.name}")
                else:
                    teaches.append(f"• {tech.name}")
            print(f"   Teaches: {', '.join(teaches)}")
            print(f"   Location: {book['location']}")

        print(f"\n{len(available_books) + 1}. Back")

        try:
            choice = int(input("\nWhich book? ").strip())
            if 1 <= choice <= len(available_books):
                book_id, book, already_read = available_books[choice - 1]
                self._read_specific_book(book_id, book)
        except ValueError:
            pass

    def _read_specific_book(self, book_id: str, book: dict):
        """Read a specific book and gain progress"""
        from systems.hypnosis_knowledge import HYPNOSIS_TECHNIQUES

        knowledge = self.game_state.player.hypnosis_knowledge

        print(f"\n{'='*70}")
        print(f"READING: {book['title']}")
        print(f"{'='*70}")
        print(f"\n{book['description']}\n")
        print("You spend time carefully reading and absorbing the material...")
        print()

        # Track if we learned anything new
        learned_new = False
        progress_made = []

        # Add progress to each technique the book teaches
        for tech_name in book['teaches']:
            if tech_name not in knowledge.known_techniques:
                progress = knowledge.add_learning_progress(tech_name, book['progress_per_read'])

                tech = HYPNOSIS_TECHNIQUES[tech_name]

                if progress >= 100:
                    print(f"🎓 TECHNIQUE MASTERED: {tech.name}!")
                    print(f"   {tech.description}")
                    learned_new = True
                else:
                    print(f"📚 Learning '{tech.name}': {progress}%")
                    progress_made.append(tech.name)

        # Mark book as read
        if book_id not in knowledge.books_read:
            knowledge.books_read.append(book_id)

        # Award SP for studying
        if learned_new:
            self.game_state.add_sp(2, "Mastered new hypnosis technique")
        elif progress_made:
            self.game_state.add_sp(1, "Studied hypnosis")

        print()
        print("="*70)
        input("\nPress Enter to continue...")

    def _practice_technique(self):
        """Practice techniques to gain proficiency"""
        from systems.hypnosis_knowledge import HYPNOSIS_TECHNIQUES

        knowledge = self.game_state.player.hypnosis_knowledge

        # Get techniques currently being learned
        in_progress = [(name, progress) for name, progress in knowledge.learning_progress.items()]

        if not in_progress:
            print(f"\n{'='*70}")
            print("PRACTICE")
            print("="*70)
            print("\nYou're not currently learning any techniques.")
            print("Read books to start learning new techniques!")
            input("\nPress Enter to continue...")
            return

        print(f"\n{'='*70}")
        print(f"PRACTICE TECHNIQUES")
        print(f"{'='*70}")
        print("\nWhich technique would you like to practice?")

        for i, (tech_name, progress) in enumerate(in_progress, 1):
            tech = HYPNOSIS_TECHNIQUES[tech_name]
            bar = "█" * (progress // 10) + "░" * ((100 - progress) // 10)
            print(f"{i}. {tech.name} [{bar}] {progress}%")

        print(f"{len(in_progress) + 1}. Back")

        try:
            choice = int(input("\nChoice: ").strip())
            if 1 <= choice <= len(in_progress):
                tech_name, current_progress = in_progress[choice - 1]
                self._practice_specific_technique(tech_name)
        except ValueError:
            pass

    def _practice_specific_technique(self, tech_name: str):
        """Practice a specific technique"""
        from systems.hypnosis_knowledge import HYPNOSIS_TECHNIQUES

        knowledge = self.game_state.player.hypnosis_knowledge
        tech = HYPNOSIS_TECHNIQUES[tech_name]

        print(f"\n{'='*70}")
        print(f"PRACTICING: {tech.name}")
        print(f"{'='*70}")
        print(f"\n{tech.description}\n")
        print("You spend time practicing the technique...")

        # Gain progress (less than reading a book)
        progress_gain = 15 + (5 if knowledge.practice_sessions > 10 else 0)  # Get better at practicing
        final_progress = knowledge.add_learning_progress(tech_name, progress_gain)

        knowledge.practice_sessions += 1

        if final_progress >= 100:
            print(f"\n🎓 TECHNIQUE MASTERED: {tech.name}!")
            print(f"   Through dedicated practice, you've mastered this technique!")
            self.game_state.add_sp(2, f"Mastered {tech.name} through practice")
        else:
            print(f"\n📚 Progress: {final_progress}%")
            print(f"   +{progress_gain}% from practice session")
            self.game_state.add_sp(1, "Practiced hypnosis")

        print()
        print("="*70)
        input("\nPress Enter to continue...")

    def _research_online(self):
        """Research hypnosis online"""
        from systems.hypnosis_knowledge import HYPNOSIS_TECHNIQUES

        knowledge = self.game_state.player.hypnosis_knowledge

        print(f"\n{'='*70}")
        print(f"ONLINE RESEARCH")
        print(f"{'='*70}")
        print("\nYou spend time researching hypnosis online...")
        print("Forums, videos, articles... absorbing knowledge from many sources.")

        # Can research any available technique
        available = knowledge.get_available_techniques()

        if not available:
            print("\nYou've learned all the basics you can find online!")
            print("You'll need books or direct practice for advanced techniques.")
            input("\nPress Enter to continue...")
            return

        # Pick a random available technique to make progress on
        import random
        tech = random.choice(available)

        progress_gain = 10  # Less efficient than books
        final_progress = knowledge.add_learning_progress(tech.name, progress_gain)

        if final_progress >= 100:
            print(f"\n🎓 TECHNIQUE LEARNED: {tech.name}!")
            print(f"   {tech.description}")
            self.game_state.add_sp(2, f"Learned {tech.name} through research")
        else:
            print(f"\n📚 You made progress learning '{tech.name}': {final_progress}%")
            self.game_state.add_sp(1, "Researched hypnosis online")

        print()
        print("="*70)
        input("\nPress Enter to continue...")

    @abstractmethod
    def run(self):
        """Main scene loop"""
        pass
