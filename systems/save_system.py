"""
Advanced Save System with Multiple Slots, Auto-Save, and Export/Import
"""
import os
import json
import shutil
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import hashlib


@dataclass
class SaveMetadata:
    """Metadata for a save file"""
    slot_id: str  # 'slot_1', 'slot_2', 'quicksave', 'autosave'
    save_name: str  # Custom name or auto-generated
    timestamp: str  # ISO format datetime
    playtime_minutes: int  # Total playtime
    game_day: int
    game_time: str
    location: str

    # Character snapshot
    suggestion_points: int
    money: int
    characters_count: int
    total_phs_active: int

    # Progress indicators
    scenes_completed: List[str]
    achievements_unlocked: int

    # Relationship summary
    average_rapport: float
    average_suspicion: float
    alliances_count: int

    # File info
    file_size_kb: float
    version: str = "1.0"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'slot_id': self.slot_id,
            'save_name': self.save_name,
            'timestamp': self.timestamp,
            'playtime_minutes': self.playtime_minutes,
            'game_day': self.game_day,
            'game_time': self.game_time,
            'location': self.location,
            'suggestion_points': self.suggestion_points,
            'money': self.money,
            'characters_count': self.characters_count,
            'total_phs_active': self.total_phs_active,
            'scenes_completed': self.scenes_completed,
            'achievements_unlocked': self.achievements_unlocked,
            'average_rapport': self.average_rapport,
            'average_suspicion': self.average_suspicion,
            'alliances_count': self.alliances_count,
            'file_size_kb': self.file_size_kb,
            'version': self.version
        }


class SaveSystemConfig:
    """Configuration for save system"""

    # Save directories
    SAVES_DIR = "saves"
    AUTOSAVES_DIR = "saves/autosaves"
    EXPORTS_DIR = "saves/exports"
    CLOUD_DIR = "saves/cloud"

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
    COMPRESSION_ENABLED = False  # Optional future feature

    # Backup
    BACKUP_ON_SAVE = True
    MAX_BACKUPS_PER_SLOT = 3


class SaveSystem:
    """
    Advanced save system with multiple slots, auto-save, and export/import
    """

    def __init__(self, config: SaveSystemConfig = None):
        self.config = config or SaveSystemConfig()
        self._ensure_directories()
        self._last_autosave_time = None

    def _ensure_directories(self):
        """Create save directories if they don't exist"""
        for directory in [
            self.config.SAVES_DIR,
            self.config.AUTOSAVES_DIR,
            self.config.EXPORTS_DIR,
            self.config.CLOUD_DIR
        ]:
            os.makedirs(directory, exist_ok=True)

    def _get_save_path(self, slot_id: str) -> str:
        """Get full path for a save slot"""
        if slot_id.startswith('autosave'):
            return os.path.join(
                self.config.AUTOSAVES_DIR,
                f"{slot_id}{self.config.SAVE_FILE_EXTENSION}"
            )
        else:
            return os.path.join(
                self.config.SAVES_DIR,
                f"{slot_id}{self.config.SAVE_FILE_EXTENSION}"
            )

    def _extract_metadata(self, game_state) -> SaveMetadata:
        """Extract metadata from game state"""
        # Calculate totals
        total_phs = sum(len(char.active_phs) for char in game_state.characters.values())
        avg_rapport = sum(char.rapport for char in game_state.characters.values()) / len(game_state.characters)
        avg_suspicion = sum(char.player_suspicion for char in game_state.characters.values()) / len(game_state.characters)

        # Get alliances count
        from systems.social_dynamics import SocialDynamics
        alliances = SocialDynamics.check_alliances(game_state)

        # Get achievements count
        achievements_count = 0
        if hasattr(game_state, 'achievements'):
            achievements_count = sum(1 for a in game_state.achievements.values() if a.get('completed', False))

        return SaveMetadata(
            slot_id="temp",  # Set by caller
            save_name="",    # Set by caller
            timestamp=datetime.now().isoformat(),
            playtime_minutes=getattr(game_state, 'playtime_minutes', 0),
            game_day=game_state.game_time.day,
            game_time=game_state.game_time.get_formatted_time(),
            location=game_state.player.current_location,
            suggestion_points=game_state.player.suggestion_points,
            money=game_state.player.money,
            characters_count=len(game_state.characters),
            total_phs_active=total_phs,
            scenes_completed=game_state.player.scenes_completed,
            achievements_unlocked=achievements_count,
            average_rapport=round(avg_rapport, 1),
            average_suspicion=round(avg_suspicion, 1),
            alliances_count=len(alliances),
            file_size_kb=0  # Set after save
        )

    def save_to_slot(self, game_state, slot_id: str, save_name: str = None) -> Tuple[bool, str]:
        """
        Save game to a specific slot

        Args:
            game_state: Current game state
            slot_id: Slot identifier (e.g., 'slot_1', 'quicksave', 'autosave_1')
            save_name: Optional custom name

        Returns:
            (success, message)
        """
        try:
            # Generate save name if not provided
            if not save_name:
                save_name = self._generate_save_name(game_state, slot_id)

            # Extract metadata
            metadata = self._extract_metadata(game_state)
            metadata.slot_id = slot_id
            metadata.save_name = save_name

            # Prepare save data
            save_data = {
                'metadata': metadata.to_dict(),
                'game_state': game_state.to_dict()
            }

            # Get save path
            save_path = self._get_save_path(slot_id)

            # Backup existing save if configured
            if self.config.BACKUP_ON_SAVE and os.path.exists(save_path):
                self._create_backup(save_path, slot_id)

            # Write save file
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            # Update file size in metadata
            file_size_kb = os.path.getsize(save_path) / 1024
            metadata.file_size_kb = round(file_size_kb, 2)

            # Re-write with updated metadata
            save_data['metadata'] = metadata.to_dict()
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True, f"Game saved to {save_name}"

        except Exception as e:
            return False, f"Save failed: {str(e)}"

    def load_from_slot(self, slot_id: str) -> Tuple[bool, Optional[dict], str]:
        """
        Load game from a specific slot

        Returns:
            (success, save_data, message)
        """
        try:
            save_path = self._get_save_path(slot_id)

            if not os.path.exists(save_path):
                return False, None, f"No save found in {slot_id}"

            with open(save_path, 'r') as f:
                save_data = json.load(f)

            # Validate save data
            if not self._validate_save_data(save_data):
                return False, None, "Save file is corrupted or invalid"

            return True, save_data, f"Loaded from {save_data['metadata']['save_name']}"

        except Exception as e:
            return False, None, f"Load failed: {str(e)}"

    def delete_slot(self, slot_id: str) -> Tuple[bool, str]:
        """Delete a save slot"""
        try:
            save_path = self._get_save_path(slot_id)

            if not os.path.exists(save_path):
                return False, f"No save found in {slot_id}"

            os.remove(save_path)
            return True, f"Deleted save from {slot_id}"

        except Exception as e:
            return False, f"Delete failed: {str(e)}"

    def list_saves(self) -> List[Dict]:
        """List all available saves with metadata"""
        saves = []

        # List regular slots
        for i in range(1, self.config.MAX_SAVE_SLOTS + 1):
            slot_id = f"slot_{i}"
            save_path = self._get_save_path(slot_id)

            if os.path.exists(save_path):
                try:
                    with open(save_path, 'r') as f:
                        save_data = json.load(f)
                    saves.append(save_data['metadata'])
                except:
                    pass

        # Add quicksave if exists
        quicksave_path = self._get_save_path('quicksave')
        if os.path.exists(quicksave_path):
            try:
                with open(quicksave_path, 'r') as f:
                    save_data = json.load(f)
                saves.append(save_data['metadata'])
            except:
                pass

        # List autosaves
        for i in range(1, self.config.MAX_AUTOSAVES + 1):
            slot_id = f"autosave_{i}"
            save_path = self._get_save_path(slot_id)

            if os.path.exists(save_path):
                try:
                    with open(save_path, 'r') as f:
                        save_data = json.load(f)
                    saves.append(save_data['metadata'])
                except:
                    pass

        # Sort by timestamp (newest first)
        saves.sort(key=lambda x: x['timestamp'], reverse=True)

        return saves

    def quicksave(self, game_state) -> Tuple[bool, str]:
        """Quick save to dedicated quicksave slot"""
        return self.save_to_slot(game_state, 'quicksave', 'Quick Save')

    def autosave(self, game_state) -> Tuple[bool, str]:
        """Auto-save with rotation"""
        # Rotate autosave slots
        self._rotate_autosaves()

        # Save to slot 1
        return self.save_to_slot(
            game_state,
            'autosave_1',
            f"Auto-Save {datetime.now().strftime('%H:%M')}"
        )

    def should_autosave(self, game_state, reason: str = None) -> bool:
        """
        Determine if auto-save should trigger

        Args:
            game_state: Current game state
            reason: Trigger reason ('interval', 'major_event', 'location_change', 'scene_complete')
        """
        if not self.config.AUTOSAVE_ENABLED:
            return False

        # Check reason-based triggers
        if reason == 'major_event' and not self.config.AUTOSAVE_ON_MAJOR_EVENTS:
            return False
        if reason == 'location_change' and not self.config.AUTOSAVE_ON_LOCATION_CHANGE:
            return False
        if reason == 'scene_complete' and not self.config.AUTOSAVE_ON_SCENE_COMPLETE:
            return False

        # Check interval trigger
        if reason == 'interval':
            if self._last_autosave_time is None:
                return True

            time_since_last = datetime.now() - self._last_autosave_time
            if time_since_last.total_seconds() / 60 >= self.config.AUTOSAVE_INTERVAL_MINUTES:
                return True

            return False

        return True

    def export_save(self, slot_id: str, export_name: str = None) -> Tuple[bool, Optional[str], str]:
        """
        Export save to a portable file

        Returns:
            (success, export_path, message)
        """
        try:
            # Load save
            success, save_data, msg = self.load_from_slot(slot_id)
            if not success:
                return False, None, msg

            # Generate export name
            if not export_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                export_name = f"export_{slot_id}_{timestamp}"

            # Add checksum for verification
            save_data['checksum'] = self._calculate_checksum(save_data)

            # Export path
            export_path = os.path.join(
                self.config.EXPORTS_DIR,
                f"{export_name}{self.config.SAVE_FILE_EXTENSION}"
            )

            # Write export
            with open(export_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True, export_path, f"Exported to {export_name}"

        except Exception as e:
            return False, None, f"Export failed: {str(e)}"

    def import_save(self, import_path: str, target_slot: str = None) -> Tuple[bool, str]:
        """
        Import save from a file

        Returns:
            (success, message)
        """
        try:
            # Read import file
            with open(import_path, 'r') as f:
                save_data = json.load(f)

            # Verify checksum if present
            if 'checksum' in save_data:
                expected_checksum = save_data.pop('checksum')
                actual_checksum = self._calculate_checksum(save_data)

                if expected_checksum != actual_checksum:
                    return False, "Import failed: File may be corrupted"

            # Validate save data
            if not self._validate_save_data(save_data):
                return False, "Import failed: Invalid save file format"

            # Determine target slot
            if not target_slot:
                # Find first empty slot
                for i in range(1, self.config.MAX_SAVE_SLOTS + 1):
                    slot_id = f"slot_{i}"
                    if not os.path.exists(self._get_save_path(slot_id)):
                        target_slot = slot_id
                        break

                if not target_slot:
                    return False, "No empty save slots available"

            # Write to slot
            save_path = self._get_save_path(target_slot)

            # Update metadata
            save_data['metadata']['slot_id'] = target_slot
            save_data['metadata']['timestamp'] = datetime.now().isoformat()

            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True, f"Imported to {target_slot}"

        except Exception as e:
            return False, f"Import failed: {str(e)}"

    def _generate_save_name(self, game_state, slot_id: str) -> str:
        """Generate automatic save name"""
        day = game_state.game_time.day
        time = game_state.game_time.get_formatted_time()
        location = game_state.player.current_location

        if slot_id == 'quicksave':
            return f"Quick Save - Day {day} {time}"
        elif slot_id.startswith('autosave'):
            return f"Auto-Save - Day {day} {time}"
        else:
            return f"Save {slot_id.split('_')[1]} - Day {day} at {location}"

    def _rotate_autosaves(self):
        """Rotate autosave slots (delete oldest, shift others)"""
        # Delete oldest autosave
        oldest_slot = f"autosave_{self.config.MAX_AUTOSAVES}"
        oldest_path = self._get_save_path(oldest_slot)
        if os.path.exists(oldest_path):
            os.remove(oldest_path)

        # Shift autosaves
        for i in range(self.config.MAX_AUTOSAVES - 1, 0, -1):
            old_path = self._get_save_path(f"autosave_{i}")
            new_path = self._get_save_path(f"autosave_{i + 1}")

            if os.path.exists(old_path):
                shutil.move(old_path, new_path)

    def _create_backup(self, save_path: str, slot_id: str):
        """Create backup of existing save"""
        backup_dir = os.path.join(self.config.SAVES_DIR, 'backups', slot_id)
        os.makedirs(backup_dir, exist_ok=True)

        # Rotate backups
        for i in range(self.config.MAX_BACKUPS_PER_SLOT - 1, 0, -1):
            old_backup = os.path.join(backup_dir, f"backup_{i}{self.config.SAVE_FILE_EXTENSION}")
            new_backup = os.path.join(backup_dir, f"backup_{i + 1}{self.config.SAVE_FILE_EXTENSION}")

            if os.path.exists(old_backup):
                shutil.move(old_backup, new_backup)

        # Create new backup
        backup_path = os.path.join(backup_dir, f"backup_1{self.config.SAVE_FILE_EXTENSION}")
        shutil.copy2(save_path, backup_path)

    def _validate_save_data(self, save_data: dict) -> bool:
        """Validate save file structure"""
        required_keys = ['metadata', 'game_state']

        if not all(key in save_data for key in required_keys):
            return False

        # Validate metadata
        metadata = save_data['metadata']
        required_metadata = ['slot_id', 'timestamp', 'version']

        if not all(key in metadata for key in required_metadata):
            return False

        # Validate game state
        game_state = save_data['game_state']
        required_game_state = ['player', 'characters', 'game_time']

        if not all(key in game_state for key in required_game_state):
            return False

        return True

    def _calculate_checksum(self, save_data: dict) -> str:
        """Calculate checksum for save data verification"""
        # Convert to stable JSON string
        json_str = json.dumps(save_data, sort_keys=True)

        # Calculate MD5 hash
        return hashlib.md5(json_str.encode()).hexdigest()


# Global instance
save_system = SaveSystem()
