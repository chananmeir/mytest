# List User Games - Documentation

This feature allows you to view information about your ongoing saved games for the Family Dynamics RPG.

## Features

### 1. CLI Utility (`list_games.py`)

A command-line tool to view detailed information about all your saved games.

**Usage:**
```bash
python list_games.py
```

**What it shows:**
- Save file location and last modified time
- In-game time and location
- Player stats (SP, money, techniques unlocked)
- Character relationships with visual rapport bars
- Active post-hypnotic suggestions
- Scenes completed

**Example Output:**
```
════════════════════════════════════════════════════════════
█                                                          █
█               FAMILY DYNAMICS RPG - ONGOING GAMES        █
█                                                          █
════════════════════════════════════════════════════════════

Found 1 saved game(s):

============================================================
SAVE FILE: ./game_save.json
============================================================
Last Modified: 2025-11-08 14:30:00
Game Time: Monday, 2:30 PM

  PLAYER STATUS:
  ----------------------------------------------------------
  Name: You
  Occupation: Currently Unemployed / Between Jobs
  Current Location: home_living_room
  Suggestion Points: 15 SP
  Total SP Earned: 35
  Money: $250
  Total Money Earned: $400

  CHARACTER RELATIONSHIPS:
  ----------------------------------------------------------
  Melanie      | Rapport: [████████████░░░░░░░░] 12/20
               | State: friendly     | Resistance: 80%
               | Active PHS: 1/3

  Ruth         | Rapport: [████████░░░░░░░░░░░░] 8/20
               | State: content      | Resistance: 75%
               | Active PHS: 1/3
```

### 2. Web Interface

Two new endpoints have been added to the web application:

#### API Endpoint: `/api/saved-games`

**Method:** GET
**Returns:** JSON with information about all saved games

**Response Format:**
```json
{
  "success": true,
  "count": 1,
  "games": [
    {
      "file_name": "game_save.json",
      "last_modified": "2025-11-08T14:30:00",
      "last_modified_display": "2025-11-08 14:30:00",
      "game_time": "Monday, 2:30 PM",
      "player": {
        "name": "You",
        "location": "home_living_room",
        "sp": 15,
        "total_sp": 35,
        "money": 250,
        "total_money": 400,
        "techniques_unlocked": 3
      },
      "characters": [
        {
          "name": "Ruth",
          "rapport": 8,
          "emotional_state": "content",
          "active_phs": 1
        }
      ],
      "scenes_completed": 3
    }
  ]
}
```

#### Web Page: `/saved-games`

A beautiful, responsive web page that displays all your saved games with:
- Player statistics in colorful stat boxes
- Character relationship cards with visual rapport bars
- Game time and location information
- Last played timestamp
- Easy navigation back to main menu

**Access:**
1. Run the web server: `python app.py`
2. Navigate to: `http://localhost:5000/saved-games`
3. Or click "View Saved Games" from the main menu

### 3. Main Menu Integration

The main menu (`/`) now includes a "View Saved Games" button that takes you directly to the saved games overview page.

## How Save Files Work

The game saves to `game_save.json` by default (configured in `config.py`).

The list utilities will automatically find:
- The default save file (`game_save.json`)
- Any other files matching the pattern `*save*.json`

## Use Cases

1. **Check progress before playing** - See where you left off in your game
2. **Compare multiple saves** - If you have multiple save files, compare your progress
3. **Track character relationships** - See which characters you've built rapport with
4. **Monitor resources** - Check your SP and money before deciding which save to load

## Technical Details

### Files Added/Modified:
- `list_games.py` - CLI utility for listing games
- `app.py` - Added `/api/saved-games` and `/saved-games` endpoints
- `templates/saved_games.html` - Web interface for viewing saves
- `templates/index.html` - Added "View Saved Games" button

### Dependencies:
- Python 3.6+
- Flask (for web interface)
- Standard library modules: `json`, `os`, `glob`, `datetime`

## Future Enhancements

Potential improvements for this feature:
- Export save data to readable formats (PDF, HTML report)
- Compare two save files side-by-side
- Save file management (rename, delete, duplicate)
- Multiple save slots with custom names
- Auto-backup of save files
- Cloud save synchronization
- Achievement/milestone tracking across saves
