#!/usr/bin/env python3
"""
List User Games Utility
Displays information about saved games for Family Dynamics RPG
"""
import json
import os
import glob
from datetime import datetime
from pathlib import Path


def format_time_display(time_dict):
    """Format game time dictionary for display"""
    if not time_dict:
        return "Unknown"

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day = day_names[time_dict.get('day', 0)]
    hour = time_dict.get('hour', 9)
    minute = time_dict.get('minute', 0)
    period = "AM" if hour < 12 else "PM"
    display_hour = hour if hour <= 12 else hour - 12
    if display_hour == 0:
        display_hour = 12

    return f"{day}, {display_hour}:{minute:02d} {period}"


def display_character_rapport(characters):
    """Display character relationship information"""
    if not characters:
        return

    print("\n  CHARACTER RELATIONSHIPS:")
    print("  " + "-" * 58)

    for name, char_data in sorted(characters.items()):
        rapport = char_data.get('rapport', 0)
        emotional_state = char_data.get('emotional_state', 'neutral')
        resistance = char_data.get('resistance', 100)
        phs_count = len(char_data.get('active_phs', []))
        max_phs = char_data.get('max_phs', 3)

        rapport_bar = "█" * rapport + "░" * (20 - rapport)
        print(f"  {name:12} | Rapport: [{rapport_bar}] {rapport}/20")
        print(f"  {'':12} | State: {emotional_state:12} | Resistance: {resistance}%")
        if phs_count > 0:
            print(f"  {'':12} | Active PHS: {phs_count}/{max_phs}")
        print()


def display_active_goals(player_data):
    """Display active goals and quests if available"""
    # This would need to check the goal system if it's tracked separately
    # For now, we can show scenes completed
    scenes_completed = player_data.get('scenes_completed', [])
    if scenes_completed:
        print(f"\n  SCENES COMPLETED: {len(scenes_completed)}")
        for scene in scenes_completed[:5]:  # Show first 5
            print(f"    • {scene}")
        if len(scenes_completed) > 5:
            print(f"    ... and {len(scenes_completed) - 5} more")


def display_game_info(save_file):
    """Display detailed information about a saved game"""
    try:
        with open(save_file, 'r') as f:
            save_data = json.load(f)

        # Get file modification time
        mod_time = datetime.fromtimestamp(os.path.getmtime(save_file))

        player = save_data.get('player', {})
        characters = save_data.get('characters', {})
        game_time = save_data.get('game_time', {})

        print("\n" + "=" * 60)
        print(f"SAVE FILE: {save_file}")
        print("=" * 60)
        print(f"Last Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Game Time: {format_time_display(game_time)}")

        # Player info
        print("\n  PLAYER STATUS:")
        print("  " + "-" * 58)
        print(f"  Name: {player.get('name', 'Unknown')}")
        print(f"  Occupation: {player.get('occupation', 'Unknown')}")
        print(f"  Current Location: {player.get('current_location', 'Unknown')}")
        print(f"  Suggestion Points: {player.get('suggestion_points', 0)} SP")
        print(f"  Total SP Earned: {player.get('total_sp_earned', 0)}")
        print(f"  Money: ${player.get('money', 0)}")
        print(f"  Total Money Earned: ${player.get('total_money_earned', 0)}")

        # Hypnosis knowledge
        hypnosis_knowledge = player.get('hypnosis_knowledge', {})
        if hypnosis_knowledge:
            unlocked_techniques = hypnosis_knowledge.get('unlocked_techniques', [])
            if unlocked_techniques:
                print(f"\n  HYPNOSIS TECHNIQUES UNLOCKED: {len(unlocked_techniques)}")
                for technique in unlocked_techniques[:3]:
                    print(f"    • {technique}")
                if len(unlocked_techniques) > 3:
                    print(f"    ... and {len(unlocked_techniques) - 3} more")

        # Character relationships
        display_character_rapport(characters)

        # Goals/Progress
        display_active_goals(player)

        print("\n" + "=" * 60 + "\n")
        return True

    except Exception as e:
        print(f"Error reading save file {save_file}: {e}")
        return False


def find_save_files(search_path='.'):
    """Find all game save files in the given path"""
    save_files = []

    # Look for game_save.json (default save file)
    default_save = os.path.join(search_path, 'game_save.json')
    if os.path.exists(default_save):
        save_files.append(default_save)

    # Look for any other .json files that might be saves
    # (in case user has multiple save files)
    for json_file in glob.glob(os.path.join(search_path, '*save*.json')):
        if json_file not in save_files:
            save_files.append(json_file)

    return save_files


def main():
    """Main function to list all ongoing games"""
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "        FAMILY DYNAMICS RPG - ONGOING GAMES".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60)

    save_files = find_save_files()

    if not save_files:
        print("\nNo saved games found.")
        print("\nTo create a saved game:")
        print("  1. Run the game: python main.py (CLI) or python app.py (Web)")
        print("  2. Play and save your progress")
        print("  3. Run this script again to view your save\n")
        return

    print(f"\nFound {len(save_files)} saved game(s):\n")

    for save_file in save_files:
        display_game_info(save_file)

    print("\nTo continue your game:")
    print("  • CLI mode: python main.py")
    print("  • Web mode: python app.py (then visit http://localhost:5000)")
    print()


if __name__ == '__main__':
    main()
