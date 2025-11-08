# Advanced Save System - Complete Guide 💾

## Overview

The **Advanced Save System** provides professional save/load functionality with multiple slots, auto-save, export/import, and comprehensive metadata tracking. Never lose progress and experiment with different playthroughs!

## Features

### 1. Multiple Save Slots (10 Slots)
- **10 numbered slots** for manual saves
- **1 quicksave slot** for fast saving
- **5 rotating autosave slots** for automatic backups
- Each slot stores complete game state + metadata

### 2. Auto-Save System
Automatic saves triggered by:
- **Time Interval** (every 15 minutes of real-time play)
- **Location Changes** (when moving between areas)
- **Scene Completions** (after completing story scenes)
- **Major Events** (important gameplay moments)

Configurable triggers - enable/disable each type!

### 3. Export/Import
- **Export saves** as portable `.fdrpg` files
- **Import saves** from exported files
- **Share saves** with friends
- **Backup saves** to external storage
- **Cross-device play** (export on PC, import on laptop)

### 4. Rich Metadata
Every save stores:
- Timestamp & playtime
- Game day & time
- Current location
- SP & money
- Active PHS count
- Character statistics
- Progress indicators
- Relationship summary

### 5. Save Protection
- **Automatic backups** (keeps last 3 backups per slot)
- **Checksum verification** (detects corrupted saves)
- **Version tracking** (future-proof)
- **Validation** (ensures save file integrity)

## File Structure

```
saves/
├── slot_1.fdrpg          # Manual save slot 1
├── slot_2.fdrpg          # Manual save slot 2
├── ...
├── slot_10.fdrpg         # Manual save slot 10
├── quicksave.fdrpg       # Quick save
├── autosaves/
│   ├── autosave_1.fdrpg  # Most recent autosave
│   ├── autosave_2.fdrpg
│   ├── ...
│   └── autosave_5.fdrpg  # Oldest autosave
├── exports/
│   └── export_*.fdrpg    # Exported saves
├── cloud/
│   └── cloud_*.fdrpg     # Cloud saves (future)
└── backups/
    ├── slot_1/
    │   ├── backup_1.fdrpg
    │   ├── backup_2.fdrpg
    │   └── backup_3.fdrpg
    └── ...
```

## Save File Format

### .fdrpg File Structure
```json
{
  "metadata": {
    "slot_id": "slot_1",
    "save_name": "Day 3 at Kitchen",
    "timestamp": "2024-01-15T14:30:00",
    "playtime_minutes": 120,
    "game_day": 3,
    "game_time": "14:30",
    "location": "kitchen",
    "suggestion_points": 15,
    "money": 250,
    "characters_count": 7,
    "total_phs_active": 5,
    "scenes_completed": ["intro", "family_dinner_1"],
    "achievements_unlocked": 3,
    "average_rapport": 8.5,
    "average_suspicion": 25.0,
    "alliances_count": 0,
    "file_size_kb": 125.5,
    "version": "1.0"
  },
  "game_state": {
    "player": {...},
    "characters": {...},
    "game_time": {...},
    ...
  },
  "checksum": "a1b2c3d4..." // For verification
}
```

## API Endpoints

### 1. List Saves
```http
GET /api/saves/list

Response:
{
  "success": true,
  "saves": [
    {
      "slot_id": "slot_1",
      "save_name": "Day 3 at Kitchen",
      "timestamp": "2024-01-15T14:30:00",
      "playtime_minutes": 120,
      "game_day": 3,
      "game_time": "14:30",
      "location": "kitchen",
      "suggestion_points": 15,
      "money": 250,
      ...
    },
    ...
  ],
  "max_slots": 10
}
```

### 2. Save to Slot
```http
POST /api/saves/save
Content-Type: application/json

{
  "slot_id": "slot_1",
  "save_name": "My Custom Save Name"  // Optional
}

Response:
{
  "success": true,
  "message": "Game saved to My Custom Save Name",
  "slot_id": "slot_1"
}
```

### 3. Load from Slot
```http
POST /api/saves/load
Content-Type: application/json

{
  "slot_id": "slot_1"
}

Response:
{
  "success": true,
  "message": "Loaded from Day 3 at Kitchen",
  "metadata": {...}
}
```

### 4. Delete Slot
```http
POST /api/saves/delete
Content-Type: application/json

{
  "slot_id": "slot_2"
}

Response:
{
  "success": true,
  "message": "Deleted save from slot_2"
}
```

### 5. Quick Save
```http
POST /api/saves/quicksave

Response:
{
  "success": true,
  "message": "Game saved to Quick Save - Day 3 14:30"
}
```

### 6. Auto-Save
```http
POST /api/saves/autosave
Content-Type: application/json

{
  "reason": "location_change"  // or "major_event", "scene_complete", "interval"
}

Response:
{
  "success": true,
  "autosaved": true,
  "message": "Game saved to Auto-Save 14:30"
}
```

### 7. Export Save
```http
POST /api/saves/export
Content-Type: application/json

{
  "slot_id": "slot_1",
  "export_name": "my_backup"  // Optional
}

Response:
File download (.fdrpg file)
```

### 8. Import Save
```http
POST /api/saves/import
Content-Type: multipart/form-data

file: [.fdrpg file]
target_slot: "slot_3"  // Optional, auto-selects if not provided

Response:
{
  "success": true,
  "message": "Imported to slot_3"
}
```

### 9. Get Configuration
```http
GET /api/saves/config

Response:
{
  "success": true,
  "config": {
    "max_save_slots": 10,
    "max_autosaves": 5,
    "autosave_enabled": true,
    "autosave_interval_minutes": 15,
    "autosave_on_major_events": true,
    "autosave_on_location_change": true,
    "autosave_on_scene_complete": true,
    "backup_on_save": true
  }
}
```

## Configuration

### SaveSystemConfig Class
```python
class SaveSystemConfig:
    # Save directories
    SAVES_DIR = "saves"
    AUTOSAVES_DIR = "saves/autosaves"
    EXPORTS_DIR = "saves/exports"

    # Save slots
    MAX_SAVE_SLOTS = 10
    MAX_AUTOSAVES = 5  # Keep last 5 autosaves

    # Auto-save triggers
    AUTOSAVE_ENABLED = True
    AUTOSAVE_INTERVAL_MINUTES = 15  # Real-time minutes
    AUTOSAVE_ON_MAJOR_EVENTS = True
    AUTOSAVE_ON_LOCATION_CHANGE = True
    AUTOSAVE_ON_SCENE_COMPLETE = True

    # File format
    SAVE_FILE_EXTENSION = ".fdrpg"  # Family Dynamics RPG

    # Backup
    BACKUP_ON_SAVE = True
    MAX_BACKUPS_PER_SLOT = 3
```

### Customizing Configuration
```python
# In app.py or config.py
from systems.save_system import SaveSystem, SaveSystemConfig

# Create custom config
config = SaveSystemConfig()
config.MAX_SAVE_SLOTS = 20  # More slots!
config.AUTOSAVE_INTERVAL_MINUTES = 10  # More frequent
config.AUTOSAVE_ON_LOCATION_CHANGE = False  # Disable location trigger

# Initialize with custom config
save_system = SaveSystem(config)
```

## Usage Examples

### Example 1: Manual Save
```javascript
// Save to slot 3 with custom name
fetch('/api/saves/save', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    slot_id: 'slot_3',
    save_name: 'Before risky manipulation'
  })
})
.then(r => r.json())
.then(data => {
  console.log(data.message);  // "Game saved to Before risky manipulation"
});
```

### Example 2: Quick Save
```javascript
// Quick save (F5 key binding)
document.addEventListener('keydown', (e) => {
  if (e.key === 'F5') {
    e.preventDefault();
    fetch('/api/saves/quicksave', {method: 'POST'})
      .then(r => r.json())
      .then(data => showNotification(data.message));
  }
});
```

### Example 3: List and Display Saves
```javascript
// Fetch save list
fetch('/api/saves/list')
  .then(r => r.json())
  .then(data => {
    const saves = data.saves;

    saves.forEach(save => {
      console.log(`${save.save_name}`);
      console.log(`  Day ${save.game_day}, ${save.game_time}`);
      console.log(`  SP: ${save.suggestion_points}, $${save.money}`);
      console.log(`  ${save.total_phs_active} active PHS`);
      console.log(`  Saved: ${new Date(save.timestamp).toLocaleString()}`);
    });
  });
```

### Example 4: Export and Download
```javascript
// Export save for backup
async function exportSave(slotId) {
  const response = await fetch('/api/saves/export', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      slot_id: slotId,
      export_name: 'my_backup_' + Date.now()
    })
  });

  // File download starts automatically
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'save.fdrpg';
  a.click();
}
```

### Example 5: Import Save
```javascript
// Import save file
function importSave() {
  const fileInput = document.getElementById('fileInput');
  const file = fileInput.files[0];

  const formData = new FormData();
  formData.append('file', file);
  formData.append('target_slot', 'slot_5');

  fetch('/api/saves/import', {
    method: 'POST',
    body: formData
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      alert(data.message);
    }
  });
}
```

### Example 6: Auto-Save Trigger
```python
# In app.py - when player changes location
@app.route('/api/move', methods=['POST'])
def api_move():
    # ... handle movement ...

    # Trigger auto-save
    from systems.save_system import save_system

    if save_system.should_autosave(game_state, 'location_change'):
        success, message = save_system.autosave(game_state)
        if success:
            save_system._last_autosave_time = datetime.now()

    # ... return response ...
```

## Auto-Save System Details

### Trigger Types

**1. Interval Trigger**
```python
# Triggers every 15 minutes (real-time)
reason = 'interval'

# Checks: Has it been 15+ minutes since last autosave?
if time_since_last >= 15 minutes:
    autosave()
```

**2. Location Change Trigger**
```python
# Triggers when player moves to new location
reason = 'location_change'

# Example: Player moves from Kitchen → Living Room
game_state.player.current_location = 'living_room'
autosave(reason='location_change')
```

**3. Scene Complete Trigger**
```python
# Triggers after completing story scenes
reason = 'scene_complete'

# Example: After family dinner scene
game_state.player.scenes_completed.append('family_dinner_1')
autosave(reason='scene_complete')
```

**4. Major Event Trigger**
```python
# Triggers on important gameplay moments
reason = 'major_event'

# Examples:
# - Planting first PHS
# - Character becomes highly suspicious
# - Alliance forms
# - Achievement unlocked
autosave(reason='major_event')
```

### Auto-Save Rotation

```
Initial state:
  autosave_1.fdrpg (doesn't exist)
  autosave_2.fdrpg (doesn't exist)
  ...

First autosave:
  autosave_1.fdrpg ← NEW SAVE

Second autosave:
  autosave_1.fdrpg → moves to autosave_2.fdrpg
  autosave_1.fdrpg ← NEW SAVE

After 5 autosaves:
  autosave_1.fdrpg ← NEWEST
  autosave_2.fdrpg
  autosave_3.fdrpg
  autosave_4.fdrpg
  autosave_5.fdrpg ← OLDEST

Sixth autosave:
  autosave_5.fdrpg → DELETED
  autosave_4.fdrpg → moves to autosave_5.fdrpg
  autosave_3.fdrpg → moves to autosave_4.fdrpg
  autosave_2.fdrpg → moves to autosave_3.fdrpg
  autosave_1.fdrpg → moves to autosave_2.fdrpg
  autosave_1.fdrpg ← NEW SAVE
```

Always keeps the 5 most recent autosaves!

## Backup System

### Automatic Backups

When `BACKUP_ON_SAVE = True`:
```
Save to slot_1:
  1. Check if slot_1.fdrpg exists
  2. If yes:
     - Rotate backups (backup_2 → backup_3, backup_1 → backup_2)
     - Copy slot_1.fdrpg → backups/slot_1/backup_1.fdrpg
  3. Write new save to slot_1.fdrpg
```

### Recovering from Backup
```python
# Manual recovery if needed
import shutil

# Restore from backup
backup_path = 'saves/backups/slot_1/backup_1.fdrpg'
save_path = 'saves/slot_1.fdrpg'

shutil.copy2(backup_path, save_path)
```

## Save File Validation

### Validation Checks
1. **Structure Check** - Required keys present
2. **Metadata Check** - Valid metadata fields
3. **Game State Check** - Complete game state
4. **Checksum Verification** - File integrity
5. **Version Compatibility** - Version matches

### Example Validation
```python
def _validate_save_data(save_data: dict) -> bool:
    # Check required keys
    if not {'metadata', 'game_state'} <= set(save_data.keys()):
        return False

    # Check metadata
    metadata = save_data['metadata']
    if not {'slot_id', 'timestamp', 'version'} <= set(metadata.keys()):
        return False

    # Check game state
    game_state = save_data['game_state']
    if not {'player', 'characters', 'game_time'} <= set(game_state.keys()):
        return False

    return True
```

## Save Metadata Explained

### Snapshot Data
```python
metadata = {
    # Identification
    'slot_id': 'slot_1',           # Which slot
    'save_name': 'Day 3 Kitchen',  # Display name
    'timestamp': '2024-01-15...',  # When saved
    'playtime_minutes': 120,       # Total playtime

    # Game Position
    'game_day': 3,                 # Current day
    'game_time': '14:30',          # Current time
    'location': 'kitchen',         # Where player is

    # Resources
    'suggestion_points': 15,       # Current SP
    'money': 250,                  # Current money

    # Character Stats
    'characters_count': 7,         # Number of characters
    'total_phs_active': 5,         # Active PHS count
    'average_rapport': 8.5,        # Avg rapport across all chars
    'average_suspicion': 25.0,     # Avg suspicion
    'alliances_count': 0,          # Alliances formed

    # Progress
    'scenes_completed': [...],     # Completed scenes
    'achievements_unlocked': 3,    # Achievement count

    # File Info
    'file_size_kb': 125.5,         # Save file size
    'version': '1.0'               # Save format version
}
```

### Using Metadata
```python
# Sort saves by progress
saves.sort(key=lambda s: s['playtime_minutes'], reverse=True)

# Filter saves by day
day_3_saves = [s for s in saves if s['game_day'] == 3]

# Find save with most PHS
most_phs = max(saves, key=lambda s: s['total_phs_active'])

# Display save info
print(f"{save['save_name']} - Day {save['game_day']}")
print(f"  {save['playtime_minutes']} min played")
print(f"  {save['total_phs_active']} PHS active")
print(f"  Avg Rapport: {save['average_rapport']}")
```

## Best Practices

### DO:
✅ Save before risky manipulations
✅ Use multiple slots for different strategies
✅ Keep quicksave for temporary checkpoints
✅ Export saves as backups
✅ Enable all autosave triggers
✅ Check metadata before loading

### DON'T:
❌ Rely only on autosaves (manual save too!)
❌ Overwrite your only good save
❌ Disable backup system
❌ Ignore file size (large saves = long load times)
❌ Edit .fdrpg files manually (corruption risk)

## Troubleshooting

### Problem: "Save file is corrupted"
**Solution:** Load from backup or autosave
```python
# Try autosaves
load_from_slot('autosave_1')
load_from_slot('autosave_2')

# Or restore from backup
```

### Problem: "No empty save slots"
**Solution:** Delete old saves or export them
```python
# Delete oldest save
oldest = min(saves, key=lambda s: s['timestamp'])
delete_slot(oldest['slot_id'])

# Or export before deleting
export_save(oldest['slot_id'], 'old_save_backup')
delete_slot(oldest['slot_id'])
```

### Problem: "Import failed - invalid format"
**Solution:** Ensure file is a valid .fdrpg file
- Check file extension
- Verify not corrupted
- Confirm from same game version

### Problem: "Auto-save not triggering"
**Solution:** Check configuration and triggers
```python
# Check config
config = save_system.config
print(f"Autosave enabled: {config.AUTOSAVE_ENABLED}")
print(f"Interval: {config.AUTOSAVE_INTERVAL_MINUTES} min")

# Manually trigger
save_system.autosave(game_state)
```

## Advanced Features

### Custom Save Naming
```python
# Generate descriptive names
def create_save_name(game_state):
    day = game_state.game_time.day
    location = game_state.player.current_location
    phs_count = sum(len(c.active_phs) for c in game_state.characters.values())

    return f"Day {day} | {location} | {phs_count} PHS"

# Use when saving
save_to_slot(game_state, 'slot_1', create_save_name(game_state))
```

### Cloud Save Integration (Future)
```python
# Cloud save endpoint (future feature)
@app.route('/api/saves/cloud/upload', methods=['POST'])
def upload_to_cloud():
    # Export save
    # Upload to cloud storage (S3, Google Drive, etc.)
    # Return cloud ID
    pass

@app.route('/api/saves/cloud/download', methods=['POST'])
def download_from_cloud():
    # Fetch from cloud
    # Import to slot
    pass
```

### Save Compression (Future)
```python
# Enable compression for smaller files
config.COMPRESSION_ENABLED = True
config.COMPRESSION_LEVEL = 6  # 1-9

# Reduces file size by ~60-70%
```

## Summary

The Advanced Save System provides:

**Reliability:**
- Multiple save slots
- Automatic backups
- Autosave protection

**Flexibility:**
- Manual saves
- Quick saves
- Autosaves

**Portability:**
- Export/import
- Share saves
- Cross-device play

**Intelligence:**
- Rich metadata
- Smart triggers
- Validation checks

**Never lose progress again!** 💾✨
