"""
Modding Support System for Family Dynamics RPG

Allows players to create and load custom content:
- Custom characters with full personality definitions
- Custom activities and interactions
- Custom hypnosis techniques
- Custom scenarios and storylines

Mods are JSON-based for easy editing and sharing.
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# MOD METADATA
# ============================================================================

@dataclass
class ModMetadata:
    """Metadata for a mod package"""
    mod_id: str
    name: str
    version: str
    author: str
    description: str
    mod_type: str  # "character", "activity", "technique", "scenario", "bundle"
    dependencies: List[str] = field(default_factory=list)
    compatible_game_version: str = "1.0"
    created_at: str = ""
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class ModValidationResult:
    """Result of mod validation"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    mod_id: str = ""


# ============================================================================
# MOD SCHEMAS - Define what valid mods look like
# ============================================================================

class ModSchemas:
    """JSON schemas for validating mod files"""

    # Required fields for character mods
    CHARACTER_SCHEMA = {
        "required_fields": [
            "metadata",
            "character_data"
        ],
        "character_data_fields": [
            "name",
            "age",
            "gender",
            "personality_traits",
            "background",
            "relationships"
        ],
        "optional_fields": [
            "initial_emotional_state",
            "initial_rapport",
            "initial_suspicion",
            "custom_dialogue",
            "special_mechanics"
        ]
    }

    # Required fields for activity mods
    ACTIVITY_SCHEMA = {
        "required_fields": [
            "metadata",
            "activity_data"
        ],
        "activity_data_fields": [
            "activity_id",
            "name",
            "description",
            "duration_minutes",
            "available_locations"
        ],
        "optional_fields": [
            "sp_cost",
            "money_cost",
            "rapport_effects",
            "emotional_effects",
            "unlock_conditions"
        ]
    }

    # Required fields for technique mods
    TECHNIQUE_SCHEMA = {
        "required_fields": [
            "metadata",
            "technique_data"
        ],
        "technique_data_fields": [
            "technique_id",
            "name",
            "description",
            "induction_method",
            "base_success_rate"
        ],
        "optional_fields": [
            "sp_cost",
            "required_rapport",
            "required_emotional_state",
            "success_modifiers",
            "detection_risk",
            "special_effects"
        ]
    }

    # Required fields for scenario mods
    SCENARIO_SCHEMA = {
        "required_fields": [
            "metadata",
            "scenario_data"
        ],
        "scenario_data_fields": [
            "scenario_id",
            "title",
            "description",
            "starting_conditions",
            "objectives",
            "scenes"
        ],
        "optional_fields": [
            "custom_characters",
            "custom_locations",
            "win_conditions",
            "fail_conditions",
            "rewards"
        ]
    }

    @staticmethod
    def validate_required_fields(data: Dict, schema: Dict) -> List[str]:
        """Check if all required fields are present"""
        errors = []

        # Check top-level required fields
        for field in schema.get("required_fields", []):
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Check nested required fields (e.g., character_data fields)
        for data_type in ["character_data", "activity_data", "technique_data", "scenario_data"]:
            if data_type in data and f"{data_type}_fields" in schema:
                for field in schema[f"{data_type}_fields"]:
                    if field not in data[data_type]:
                        errors.append(f"Missing required field in {data_type}: {field}")

        return errors


# ============================================================================
# MOD LOADER
# ============================================================================

class ModLoader:
    """Handles loading and managing mods"""

    def __init__(self, mods_directory: str = "mods"):
        self.mods_directory = mods_directory
        self.loaded_mods: Dict[str, Dict] = {}
        self.mod_metadata: Dict[str, ModMetadata] = {}
        self.load_order: List[str] = []

        # Ensure mods directory exists
        os.makedirs(self.mods_directory, exist_ok=True)
        self._create_example_structure()

    def _create_example_structure(self):
        """Create example mod directory structure"""
        subdirs = ["characters", "activities", "techniques", "scenarios"]
        for subdir in subdirs:
            os.makedirs(os.path.join(self.mods_directory, subdir), exist_ok=True)

    def discover_mods(self) -> List[str]:
        """Scan mods directory and find all mod files"""
        mod_files = []

        for root, dirs, files in os.walk(self.mods_directory):
            for file in files:
                if file.endswith('.json') and not file.startswith('_'):
                    mod_files.append(os.path.join(root, file))

        logger.info(f"Discovered {len(mod_files)} mod files")
        return mod_files

    def load_mod(self, mod_path: str) -> Tuple[bool, Optional[Dict], List[str]]:
        """
        Load a single mod file

        Returns:
            (success, mod_data, errors)
        """
        try:
            with open(mod_path, 'r', encoding='utf-8') as f:
                mod_data = json.load(f)

            # Validate mod
            validation = self.validate_mod(mod_data)

            if not validation.valid:
                logger.error(f"Mod validation failed for {mod_path}: {validation.errors}")
                return False, None, validation.errors

            # Extract metadata
            metadata = ModMetadata(**mod_data['metadata'])

            # Check dependencies
            missing_deps = self._check_dependencies(metadata.dependencies)
            if missing_deps:
                error = f"Missing dependencies: {', '.join(missing_deps)}"
                logger.warning(error)
                return False, None, [error]

            # Store mod
            self.loaded_mods[metadata.mod_id] = mod_data
            self.mod_metadata[metadata.mod_id] = metadata
            self.load_order.append(metadata.mod_id)

            logger.info(f"Successfully loaded mod: {metadata.name} v{metadata.version}")
            return True, mod_data, []

        except json.JSONDecodeError as e:
            error = f"Invalid JSON in {mod_path}: {str(e)}"
            logger.error(error)
            return False, None, [error]
        except Exception as e:
            error = f"Error loading mod {mod_path}: {str(e)}"
            logger.error(error)
            return False, None, [error]

    def validate_mod(self, mod_data: Dict) -> ModValidationResult:
        """Validate mod structure and data"""
        errors = []
        warnings = []

        # Check metadata exists
        if 'metadata' not in mod_data:
            return ModValidationResult(valid=False, errors=["Missing metadata section"])

        metadata = mod_data['metadata']

        # Required metadata fields
        required_metadata = ['mod_id', 'name', 'version', 'author', 'mod_type']
        for field in required_metadata:
            if field not in metadata:
                errors.append(f"Missing required metadata field: {field}")

        if errors:
            return ModValidationResult(valid=False, errors=errors)

        mod_type = metadata['mod_type']
        mod_id = metadata['mod_id']

        # Validate based on mod type
        if mod_type == 'character':
            schema_errors = ModSchemas.validate_required_fields(
                mod_data, ModSchemas.CHARACTER_SCHEMA
            )
            errors.extend(schema_errors)
        elif mod_type == 'activity':
            schema_errors = ModSchemas.validate_required_fields(
                mod_data, ModSchemas.ACTIVITY_SCHEMA
            )
            errors.extend(schema_errors)
        elif mod_type == 'technique':
            schema_errors = ModSchemas.validate_required_fields(
                mod_data, ModSchemas.TECHNIQUE_SCHEMA
            )
            errors.extend(schema_errors)
        elif mod_type == 'scenario':
            schema_errors = ModSchemas.validate_required_fields(
                mod_data, ModSchemas.SCENARIO_SCHEMA
            )
            errors.extend(schema_errors)
        elif mod_type == 'bundle':
            # Bundle can contain multiple types
            if 'bundle_contents' not in mod_data:
                errors.append("Bundle mod missing 'bundle_contents'")
        else:
            warnings.append(f"Unknown mod type: {mod_type}")

        # Check for duplicate mod_id
        if mod_id in self.loaded_mods:
            warnings.append(f"Mod ID '{mod_id}' already loaded (will be overwritten)")

        return ModValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            mod_id=mod_id
        )

    def _check_dependencies(self, dependencies: List[str]) -> List[str]:
        """Check if required dependencies are loaded"""
        missing = []
        for dep in dependencies:
            if dep not in self.loaded_mods:
                missing.append(dep)
        return missing

    def load_all_mods(self) -> Dict[str, Any]:
        """
        Load all mods from the mods directory

        Returns:
            Summary of loaded mods
        """
        mod_files = self.discover_mods()

        results = {
            'total_found': len(mod_files),
            'loaded': 0,
            'failed': 0,
            'errors': []
        }

        for mod_path in mod_files:
            success, mod_data, errors = self.load_mod(mod_path)
            if success:
                results['loaded'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'file': mod_path,
                    'errors': errors
                })

        return results

    def get_mods_by_type(self, mod_type: str) -> List[Dict]:
        """Get all loaded mods of a specific type"""
        mods = []
        for mod_id, mod_data in self.loaded_mods.items():
            if mod_data['metadata']['mod_type'] == mod_type:
                mods.append(mod_data)
        return mods

    def get_mod(self, mod_id: str) -> Optional[Dict]:
        """Get a specific mod by ID"""
        return self.loaded_mods.get(mod_id)

    def unload_mod(self, mod_id: str) -> bool:
        """Unload a mod"""
        if mod_id in self.loaded_mods:
            del self.loaded_mods[mod_id]
            del self.mod_metadata[mod_id]
            self.load_order.remove(mod_id)
            logger.info(f"Unloaded mod: {mod_id}")
            return True
        return False

    def reload_mod(self, mod_id: str) -> Tuple[bool, List[str]]:
        """Reload a mod (useful for development)"""
        # Find mod file
        for root, dirs, files in os.walk(self.mods_directory):
            for file in files:
                if file.endswith('.json'):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r') as f:
                            data = json.load(f)
                            if data.get('metadata', {}).get('mod_id') == mod_id:
                                # Unload old version
                                self.unload_mod(mod_id)
                                # Load new version
                                success, _, errors = self.load_mod(path)
                                return success, errors
                    except:
                        continue

        return False, [f"Mod {mod_id} not found"]

    def get_load_summary(self) -> Dict:
        """Get summary of all loaded mods"""
        summary = {
            'total_mods': len(self.loaded_mods),
            'by_type': {},
            'mods': []
        }

        for mod_id, metadata in self.mod_metadata.items():
            mod_type = metadata.mod_type
            if mod_type not in summary['by_type']:
                summary['by_type'][mod_type] = 0
            summary['by_type'][mod_type] += 1

            summary['mods'].append({
                'mod_id': mod_id,
                'name': metadata.name,
                'version': metadata.version,
                'author': metadata.author,
                'type': mod_type,
                'description': metadata.description
            })

        return summary


# ============================================================================
# MOD INTEGRATION HELPERS
# ============================================================================

class ModIntegration:
    """Helpers for integrating mods into the game"""

    @staticmethod
    def create_character_from_mod(mod_data: Dict, game_state) -> Optional[Any]:
        """
        Create a Character instance from mod data

        Returns Character object ready to add to game_state
        """
        from classes import Character  # Import here to avoid circular dependency

        char_data = mod_data['character_data']

        # Create character with mod data
        character = Character(
            name=char_data['name'],
            age=char_data['age'],
            gender=char_data['gender'],
            personality_traits=char_data['personality_traits'],
            background=char_data['background'],
            emotional_state=char_data.get('initial_emotional_state', 'neutral'),
            rapport=char_data.get('initial_rapport', 5),
            suspicion=char_data.get('initial_suspicion', 0)
        )

        # Set custom dialogue if provided
        if 'custom_dialogue' in char_data:
            character.custom_dialogue = char_data['custom_dialogue']

        # Add relationships
        if 'relationships' in char_data:
            character.relationships = char_data['relationships']

        logger.info(f"Created character from mod: {character.name}")
        return character

    @staticmethod
    def register_activity_from_mod(mod_data: Dict, game_state) -> bool:
        """Register a custom activity from mod"""
        activity_data = mod_data['activity_data']

        # Add to game_state.custom_activities
        if not hasattr(game_state, 'custom_activities'):
            game_state.custom_activities = {}

        game_state.custom_activities[activity_data['activity_id']] = activity_data

        logger.info(f"Registered activity: {activity_data['name']}")
        return True

    @staticmethod
    def register_technique_from_mod(mod_data: Dict, game_state) -> bool:
        """Register a custom hypnosis technique from mod"""
        technique_data = mod_data['technique_data']

        # Add to game_state.custom_techniques
        if not hasattr(game_state, 'custom_techniques'):
            game_state.custom_techniques = {}

        game_state.custom_techniques[technique_data['technique_id']] = technique_data

        logger.info(f"Registered technique: {technique_data['name']}")
        return True

    @staticmethod
    def load_scenario_from_mod(mod_data: Dict) -> Dict:
        """Load a custom scenario"""
        scenario_data = mod_data['scenario_data']

        logger.info(f"Loaded scenario: {scenario_data['title']}")
        return scenario_data


# ============================================================================
# GLOBAL MOD LOADER INSTANCE
# ============================================================================

# Create global instance
mod_loader = ModLoader()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def load_all_mods() -> Dict:
    """Load all mods from the mods directory"""
    return mod_loader.load_all_mods()


def get_character_mods() -> List[Dict]:
    """Get all character mods"""
    return mod_loader.get_mods_by_type('character')


def get_activity_mods() -> List[Dict]:
    """Get all activity mods"""
    return mod_loader.get_mods_by_type('activity')


def get_technique_mods() -> List[Dict]:
    """Get all technique mods"""
    return mod_loader.get_mods_by_type('technique')


def get_scenario_mods() -> List[Dict]:
    """Get all scenario mods"""
    return mod_loader.get_mods_by_type('scenario')


def integrate_mod_into_game(mod_id: str, game_state) -> Tuple[bool, str]:
    """
    Integrate a mod into the current game state

    Returns:
        (success, message)
    """
    mod_data = mod_loader.get_mod(mod_id)
    if not mod_data:
        return False, f"Mod {mod_id} not found"

    mod_type = mod_data['metadata']['mod_type']

    try:
        if mod_type == 'character':
            char = ModIntegration.create_character_from_mod(mod_data, game_state)
            game_state.characters[char.name] = char
            return True, f"Added character: {char.name}"

        elif mod_type == 'activity':
            ModIntegration.register_activity_from_mod(mod_data, game_state)
            return True, f"Registered activity: {mod_data['activity_data']['name']}"

        elif mod_type == 'technique':
            ModIntegration.register_technique_from_mod(mod_data, game_state)
            return True, f"Registered technique: {mod_data['technique_data']['name']}"

        elif mod_type == 'scenario':
            scenario = ModIntegration.load_scenario_from_mod(mod_data)
            # Store for later loading
            if not hasattr(game_state, 'available_scenarios'):
                game_state.available_scenarios = {}
            game_state.available_scenarios[scenario['scenario_id']] = scenario
            return True, f"Loaded scenario: {scenario['title']}"

        else:
            return False, f"Unknown mod type: {mod_type}"

    except Exception as e:
        logger.error(f"Error integrating mod {mod_id}: {str(e)}")
        return False, f"Error: {str(e)}"
