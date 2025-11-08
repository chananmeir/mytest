# Family Dynamics RPG - Modding Guide

## Overview

Welcome to the Family Dynamics RPG modding system! This guide will teach you how to create custom content for the game, including:

- **Custom Characters** - Add new family members, neighbors, or visitors
- **Custom Activities** - Create new interactions and events
- **Custom Techniques** - Design new hypnosis induction methods
- **Custom Scenarios** - Build complete storylines and challenges

All mods are **JSON-based**, making them easy to create, edit, and share without programming knowledge!

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Character Mods](#character-mods)
3. [Activity Mods](#activity-mods)
4. [Technique Mods](#technique-mods)
5. [Scenario Mods](#scenario-mods)
6. [API Reference](#api-reference)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

1. **Locate the Mods Directory**: `mods/` in your game installation
2. **Directory Structure**:
   ```
   mods/
   ├── characters/    ← Character mods go here
   ├── activities/    ← Activity mods go here
   ├── techniques/    ← Technique mods go here
   └── scenarios/     ← Scenario mods go here
   ```

### Creating Your First Mod

1. Create a `.json` file in the appropriate subdirectory
2. Copy an example mod template (see below)
3. Edit the JSON to customize your mod
4. Load the game - mods load automatically!

### Mod Structure (All Types)

Every mod has two main sections:

```json
{
  "metadata": {
    // Information about the mod
  },
  "character_data": {  // or activity_data, technique_data, scenario_data
    // The actual content
  }
}
```

---

## Character Mods

### What Can Character Mods Do?

- Add new characters to the game world
- Define personality traits and background
- Set initial relationships with existing characters
- Create custom dialogue
- Add special mechanics (gossip, random visits, etc.)

### Character Mod Schema

#### Required Fields

```json
{
  "metadata": {
    "mod_id": "unique_identifier",           // Must be unique!
    "name": "Display Name",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "What this mod adds",
    "mod_type": "character",                 // Must be "character"
    "dependencies": [],                      // List of required mod IDs
    "compatible_game_version": "1.0",
    "tags": ["character", "neighbor"]        // For organization
  },
  "character_data": {
    "name": "Character Name",                // Display name in-game
    "age": 38,
    "gender": "female",                      // "male", "female", "non-binary"
    "personality_traits": [
      "curious",
      "friendly",
      "perceptive"
    ],
    "background": "Character backstory...",
    "relationships": {                       // Existing character relationships
      "Ruth": 8,                            // 0-20 scale
      "Tom": 6,
      "Dawn": 7
    }
  }
}
```

#### Optional Fields

```json
"character_data": {
  // ... required fields ...

  "initial_emotional_state": "curious",    // Starting emotion
  "initial_rapport": 6,                    // Starting rapport with player
  "initial_suspicion": 0,                  // Starting suspicion level

  "custom_dialogue": {
    "greeting": "Hello there!",
    "high_rapport": "You're a good friend!",
    "high_suspicion": "Something's not right...",
    "low_rapport": "I should go.",
    "phs_vulnerable": "I trust your advice.",
    "phs_resistant": "I'll figure it out myself."
  },

  "special_mechanics": {
    "gossip_network": true,               // Can spread gossip
    "visits_randomly": true,              // Appears unexpectedly
    "observes_family_dynamics": true,     // Notices family changes
    "can_spread_rumors": true,
    "visit_frequency_days": 3             // How often they visit
  }
}
```

### Character Mod Example

See `mods/characters/example_neighbor.json` for a complete example!

**Sarah - The Nosy Neighbor**
- Visits every 3 days
- Notices family dynamics
- Can spread rumors
- Builds friendship or becomes suspicious

### Using Character Mods

#### Via API:
```javascript
// Add character to game
fetch('/api/mods/character/add', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    mod_id: 'neighbor_sarah'
  })
});
```

#### Via Integration:
```javascript
// Integrate any mod
fetch('/api/mods/integrate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    mod_id: 'neighbor_sarah'
  })
});
```

---

## Activity Mods

### What Can Activity Mods Do?

- Create new interactions with characters
- Design group activities
- Add PHS opportunities
- Create time-based events
- Define multiple outcomes

### Activity Mod Schema

#### Required Fields

```json
{
  "metadata": {
    "mod_id": "activity_game_night",
    "name": "Family Game Night",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "Host a family game night",
    "mod_type": "activity",
    "tags": ["activity", "family", "group"]
  },
  "activity_data": {
    "activity_id": "family_game_night",    // Unique ID
    "name": "Host Family Game Night",      // Display name
    "description": "Gather the family...",
    "duration_minutes": 120,
    "available_locations": ["living_room", "family_room"],
    "available_times": ["evening"]         // Optional time restriction
  }
}
```

#### Optional Fields

```json
"activity_data": {
  // ... required fields ...

  "sp_cost": 2,                           // SP to use activity
  "money_cost": 0,                        // Money cost

  "participants": {
    "required": ["player"],
    "optional": ["Ruth", "Tom", "Dawn"]
  },

  "rapport_effects": {
    "all_participants": 2,                // Rapport gain for all
    "Ruth": 1,                           // Additional for Ruth
    "if_player_wins": {                  // Conditional effects
      "Tom": 1
    }
  },

  "emotional_effects": {
    "all_participants": "relaxed"
  },

  "suspicion_effects": {
    "all_participants": -5               // Reduce suspicion
  },

  "special_mechanics": {
    "phs_opportunity": true,
    "phs_success_bonus": 15,             // +15% PHS success
    "phs_detection_risk": 20,            // 20% detection chance
    "allows_group_suggestion": true,
    "max_group_suggestion_targets": 3
  },

  "unlock_conditions": {
    "min_game_day": 2,
    "min_average_rapport": 5,
    "required_time": "evening",
    "cooldown_hours": 48                 // Can't repeat for 48 hours
  },

  "dialogue": {
    "start": "You suggest a game night...",
    "during": {
      "positive": ["Everyone's laughing!"],
      "phs_opportunity": "During a quiet moment..."
    },
    "end": {
      "success": "What a great evening!",
      "phs_success": "Suggestion planted successfully.",
      "phs_caught": "Someone noticed something odd..."
    }
  },

  "outcomes": [
    {
      "outcome_id": "great_success",
      "probability": 30,
      "conditions": {
        "min_average_rapport": 8
      },
      "effects": {
        "rapport_bonus": 1,
        "sp_gain": 3
      },
      "message": "The night was a huge success!"
    }
  ]
}
```

### Activity Mod Example

See `mods/activities/example_game_night.json`!

**Family Game Night**
- 2-hour group activity
- Builds rapport with everyone
- Creates PHS opportunities
- Multiple outcomes based on family dynamics

---

## Technique Mods

### What Can Technique Mods Do?

- Create new hypnosis induction methods
- Design multi-stage techniques
- Add success modifiers and conditions
- Create advanced unlock trees
- Balance risk vs reward

### Technique Mod Schema

#### Required Fields

```json
{
  "metadata": {
    "mod_id": "technique_mirror",
    "name": "Mirror Induction",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "Subtle mirroring technique",
    "mod_type": "technique",
    "tags": ["technique", "subtle", "advanced"]
  },
  "technique_data": {
    "technique_id": "mirror_induction",
    "name": "Mirror Induction",
    "category": "conversational",          // conversational, direct, covert
    "description": "Mirror body language...",
    "induction_method": "behavioral_matching",
    "base_success_rate": 65                // Base success % (0-100)
  }
}
```

#### Optional Fields

```json
"technique_data": {
  // ... required fields ...

  "sp_cost": 6,
  "duration_minutes": 45,
  "required_rapport": 8,                  // Minimum rapport needed
  "required_emotional_state": [
    "relaxed", "comfortable", "neutral"
  ],
  "incompatible_emotional_state": [
    "angry", "suspicious", "defensive"
  ],

  "trance_depth": "light_to_medium",     // light, medium, deep
  "detection_risk": 20,                   // Base detection % (0-100)

  "success_modifiers": {
    "high_rapport_bonus": {
      "condition": "rapport >= 12",
      "modifier": 15,
      "description": "Deep trust helps"
    },
    "rushed_penalty": {
      "condition": "duration < 30",
      "modifier": -25,
      "description": "Needs time to work"
    }
  },

  "stages": [
    {
      "stage": 1,
      "name": "Observation",
      "duration_minutes": 10,
      "description": "Observe baseline behavior",
      "sp_cost": 1,
      "detection_risk": 5,
      "failure_consequence": "minor",    // minor, moderate, technique_fails
      "can_abort": true
    },
    {
      "stage": 2,
      "name": "Matching",
      "duration_minutes": 15,
      "description": "Match their patterns",
      "sp_cost": 2,
      "detection_risk": 8,
      "success_requirement": "stage_1_complete",
      "can_abort": true
    }
  ],

  "special_effects": {
    "rapport_preservation": true,
    "rapport_preservation_desc": "Even if detected, seems natural",
    "builds_trust": true,
    "trust_bonus": "+2 rapport on success",
    "reusable": true,
    "cooldown_hours": 24,
    "advanced_unlock": {
      "required_successful_uses": 3,
      "unlocks": "technique_deep_mirror",
      "description": "Master to unlock deep version"
    }
  },

  "dialogue": {
    "start": "You settle into conversation...",
    "stage_1_success": "Patterns identified.",
    "stage_2_success": "Your breathing syncs.",
    "detected": "Why are you copying me?",
    "success": "Suggestion planted seamlessly.",
    "failure": "Technique fails."
  },

  "tips": [
    "Requires patience - don't rush",
    "Best with high rapport (8+)",
    "Avoid defensive targets"
  ]
}
```

### Technique Mod Example

See `mods/techniques/example_mirror_technique.json`!

**Mirror Induction**
- 4-stage subtle technique
- 65% base success rate
- Builds genuine rapport
- Unlocks advanced version after 3 successes

---

## Scenario Mods

### What Can Scenario Mods Do?

- Create complete storylines
- Design custom challenges
- Add unique locations
- Define win/fail conditions
- Create branching narratives

### Scenario Mod Schema

#### Required Fields

```json
{
  "metadata": {
    "mod_id": "scenario_weekend_cabin",
    "name": "Weekend at the Cabin",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "3-day isolated getaway",
    "mod_type": "scenario",
    "tags": ["scenario", "challenge", "isolated"]
  },
  "scenario_data": {
    "scenario_id": "weekend_cabin",
    "title": "Weekend at the Cabin",
    "subtitle": "3 days. 1 cabin. Unlimited opportunities.",
    "description": "Family weekend at remote cabin...",
    "starting_conditions": {
      "game_day": 1,
      "game_time": "09:00",
      "location": "cabin_main_room",
      "player_sp": 20,
      "characters": {
        "Ruth": {
          "rapport": 7,
          "suspicion": 10,
          "emotional_state": "relaxed",
          "present": true
        }
      }
    },
    "objectives": {
      "primary": [
        {
          "id": "cabin_master",
          "title": "Cabin Master",
          "description": "Plant 5+ PHS",
          "type": "phs_count",
          "target": 5,
          "reward_sp": 10
        }
      ]
    },
    "scenes": [
      {
        "scene_id": "arrival",
        "title": "Arrival at Cabin",
        "trigger": "scenario_start",
        "description": "Family arrives...",
        "participants": ["all"],
        "location": "cabin_main_room",
        "forced": true,
        "choices": [
          {
            "id": "help_everyone",
            "text": "Help everyone unpack",
            "effects": {
              "rapport": {"all": 1}
            }
          }
        ]
      }
    ]
  }
}
```

#### Optional Scenario Fields

```json
"scenario_data": {
  // ... required fields ...

  "duration_days": 3,
  "difficulty": "intermediate",           // easy, intermediate, hard, expert

  "objectives": {
    "primary": [...],                     // Main goals
    "secondary": [...],                   // Optional goals
    "hidden": [...]                       // Secret achievements
  },

  "custom_locations": [
    {
      "id": "cabin_deck",
      "name": "Deck Overlooking Lake",
      "description": "Beautiful deck...",
      "privacy_level": 8,                // 0-10 scale
      "typical_occupants": [],
      "activities_available": ["talk", "hypnosis"],
      "special": "High privacy location"
    }
  ],

  "win_conditions": [
    {
      "id": "perfect_win",
      "name": "Perfect Cabin Master",
      "requirements": {
        "min_phs": 6,
        "min_average_rapport": 10,
        "all_objectives": true
      },
      "rewards": {
        "sp": 50,
        "unlock_achievement": "cabin_master_perfect"
      }
    }
  ],

  "fail_conditions": [
    {
      "id": "exposed",
      "name": "Caught and Exposed",
      "trigger": "suspicion_threshold_exceeded",
      "threshold": 60
    }
  ],

  "special_rules": {
    "isolated_location": {
      "no_visitors": true,
      "no_leaving": true
    },
    "time_pressure": {
      "time_limited": true,
      "max_game_days": 3
    }
  },

  "custom_events": [
    {
      "event_id": "thunderstorm",
      "probability": 30,
      "trigger": "any_evening",
      "description": "Storm knocks out power",
      "effects": {
        "phs_bonus_all": 20,
        "detection_risk_reduction": 15
      }
    }
  ]
}
```

### Scenario Mod Example

See `mods/scenarios/example_weekend_getaway.json`!

**Weekend at the Cabin**
- 3-day challenge scenario
- Custom locations (deck, dock, trails)
- 8 unique scenes
- Multiple endings
- Hidden achievements

---

## API Reference

### Load All Mods

```http
POST /api/mods/load
```

**Response:**
```json
{
  "success": true,
  "results": {
    "total_found": 4,
    "loaded": 4,
    "failed": 0,
    "errors": []
  }
}
```

### List Loaded Mods

```http
GET /api/mods/list
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_mods": 4,
    "by_type": {
      "character": 1,
      "activity": 1,
      "technique": 1,
      "scenario": 1
    },
    "mods": [
      {
        "mod_id": "neighbor_sarah",
        "name": "Sarah - The Nosy Neighbor",
        "version": "1.0.0",
        "author": "Example Modder",
        "type": "character"
      }
    ]
  }
}
```

### Get Character Mods

```http
GET /api/mods/characters
```

**Response:**
```json
{
  "success": true,
  "character_mods": [...],
  "count": 1
}
```

### Get Activity Mods

```http
GET /api/mods/activities
```

### Get Technique Mods

```http
GET /api/mods/techniques
```

### Get Scenario Mods

```http
GET /api/mods/scenarios
```

### Integrate Mod

```http
POST /api/mods/integrate
Content-Type: application/json

{
  "mod_id": "neighbor_sarah"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Added character: Sarah"
}
```

### Add Character Mod

```http
POST /api/mods/character/add
Content-Type: application/json

{
  "mod_id": "neighbor_sarah"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Added character: Sarah",
  "character": {
    "name": "Sarah",
    "age": 38,
    "gender": "female",
    "rapport": 6,
    "suspicion": 0
  }
}
```

### Reload Mod (Development)

```http
POST /api/mods/reload
Content-Type: application/json

{
  "mod_id": "neighbor_sarah"
}
```

### Validate Mod

```http
POST /api/mods/validate
Content-Type: application/json

{
  "mod_data": {
    "metadata": {...},
    "character_data": {...}
  }
}
```

**Response:**
```json
{
  "success": true,
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": [],
    "mod_id": "neighbor_sarah"
  }
}
```

---

## Best Practices

### Mod Design

**DO:**
- ✅ Use descriptive, unique mod_ids
- ✅ Test thoroughly before sharing
- ✅ Include detailed descriptions
- ✅ Balance rewards and costs
- ✅ Consider integration with existing content
- ✅ Add helpful tips and dialogue

**DON'T:**
- ❌ Make overpowered content (breaks game balance)
- ❌ Use existing character names
- ❌ Create duplicate mod_ids
- ❌ Forget to test edge cases
- ❌ Ignore the relationship web system

### JSON Formatting

```json
{
  "use_proper_indentation": true,
  "quote_all_keys": "yes",
  "validate_json": "always",
  "comment_your_reasoning": "Use descriptions"
}
```

**Validate JSON:** Use [JSONLint](https://jsonlint.com/) to check syntax!

### Balance Guidelines

**Character Mods:**
- Initial rapport: 3-10 (balanced range)
- Initial suspicion: 0-20 (max 20)
- Relationships: Match personality

**Activity Mods:**
- SP cost: 0-10 (most 2-5)
- Duration: 15-180 minutes
- Rapport changes: ±1-4 per character
- PHS bonuses: 10-30%

**Technique Mods:**
- Base success: 40-75%
- SP cost: 3-10
- Detection risk: 15-40%
- Duration: 20-90 minutes

**Scenario Mods:**
- Duration: 1-7 days
- Objectives: 3-8 total
- Scenes: 5-15
- Balance challenge vs fun

---

## Troubleshooting

### Mod Won't Load

**Check:**
1. Is the JSON valid? Use JSONLint
2. Is the file in the correct directory?
3. Does it have the `.json` extension?
4. Are all required fields present?
5. Is the mod_type correct?

**Common Errors:**
```
Missing metadata section
→ Add "metadata": {...} at top level

Missing required field: name
→ Add all required fields for mod type

Invalid JSON
→ Check for missing commas, quotes, brackets
```

### Mod Loads But Doesn't Appear

**Check:**
1. Did you call `/api/mods/integrate`?
2. Is the mod_id correct?
3. Are unlock conditions met?
4. Is the game state compatible?

### Character Not Showing Up

```javascript
// Make sure to integrate:
fetch('/api/mods/character/add', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({mod_id: 'neighbor_sarah'})
});
```

### Validation Errors

Use the validate endpoint before loading:

```javascript
fetch('/api/mods/validate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({mod_data: yourModData})
})
.then(r => r.json())
.then(data => {
  if (!data.validation.valid) {
    console.error('Errors:', data.validation.errors);
  }
});
```

---

## Advanced Topics

### Mod Dependencies

If your mod requires another mod:

```json
"metadata": {
  "dependencies": ["mod_id_1", "mod_id_2"]
}
```

The system will:
1. Check if dependencies are loaded
2. Refuse to load if missing
3. Load dependencies first (automatic ordering)

### Bundle Mods

Create a mod that packages multiple mods:

```json
{
  "metadata": {
    "mod_type": "bundle"
  },
  "bundle_contents": [
    "character_mod_1",
    "activity_mod_1",
    "scenario_mod_1"
  ]
}
```

### Mod Versioning

Use semantic versioning:
- `1.0.0` - Initial release
- `1.0.1` - Bug fix
- `1.1.0` - New feature
- `2.0.0` - Breaking change

### Hot Reload (Development)

While developing:

```javascript
// Edit your mod file
// Then reload without restarting:
fetch('/api/mods/reload', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({mod_id: 'your_mod_id'})
});
```

---

## Sharing Your Mods

### Preparing for Release

1. **Test Thoroughly**
   - Load in fresh game
   - Test all features
   - Check edge cases
   - Verify balance

2. **Document**
   - Clear description
   - Usage instructions
   - Known issues
   - Credits

3. **Package**
   ```
   my_awesome_mod/
   ├── mod_file.json
   ├── README.md
   └── screenshots/
   ```

4. **Share**
   - Upload to mod repository
   - Share on community forums
   - Include version number
   - Credit dependencies

### Mod License

Consider adding a license field:

```json
"metadata": {
  "license": "CC-BY-4.0",
  "credits": "Based on work by..."
}
```

---

## Example: Creating a Complete Mod

Let's create a "Pizza Night" activity mod from scratch!

### Step 1: Plan

**Concept:** Order pizza as a family
- Duration: 60 minutes
- Cost: $30 (money)
- Builds rapport with everyone
- PHS opportunity while relaxed
- Can trigger family bonding

### Step 2: Create File

Create `mods/activities/pizza_night.json`

### Step 3: Write JSON

```json
{
  "metadata": {
    "mod_id": "activity_pizza_night",
    "name": "Family Pizza Night",
    "version": "1.0.0",
    "author": "YourName",
    "description": "Order pizza and enjoy a casual family meal together",
    "mod_type": "activity",
    "dependencies": [],
    "compatible_game_version": "1.0",
    "tags": ["activity", "family", "food", "casual"]
  },
  "activity_data": {
    "activity_id": "pizza_night",
    "name": "Order Pizza for Family",
    "description": "Order pizza delivery and share a casual meal. Everyone gathers in the kitchen for food and conversation.",
    "duration_minutes": 60,
    "available_locations": ["kitchen", "dining_room"],
    "available_times": ["evening"],

    "sp_cost": 0,
    "money_cost": 30,

    "participants": {
      "required": ["player"],
      "optional": ["Ruth", "Tom", "Dawn", "Melanie", "Derek", "Vanessa"]
    },

    "rapport_effects": {
      "all_participants": 1
    },

    "emotional_effects": {
      "all_participants": "content"
    },

    "suspicion_effects": {
      "all_participants": -3
    },

    "special_mechanics": {
      "phs_opportunity": true,
      "phs_success_bonus": 10,
      "phs_detection_risk": 25,
      "description": "Casual atmosphere lowers defenses slightly"
    },

    "unlock_conditions": {
      "cooldown_hours": 72
    },

    "dialogue": {
      "start": "You suggest ordering pizza. Everyone agrees enthusiastically!",
      "during": {
        "positive": [
          "The family gathers around the kitchen table.",
          "Everyone's enjoying the food and chatting.",
          "Ruth: 'This was a nice idea!'"
        ],
        "phs_opportunity": "In the relaxed atmosphere, you lean in to {target}..."
      },
      "end": {
        "success": "A simple but effective family bonding moment!",
        "phs_success": "Your suggestion blends naturally into the conversation.",
        "partial": "Most of the family enjoyed it."
      }
    },

    "outcomes": [
      {
        "outcome_id": "everyone_happy",
        "probability": 60,
        "effects": {
          "as_defined": true
        },
        "message": "Pizza night was a success! Simple pleasures work best."
      },
      {
        "outcome_id": "topping_argument",
        "probability": 25,
        "effects": {
          "rapport_bonus": -1,
          "emotional_state_change": "annoyed"
        },
        "message": "An argument breaks out over pizza toppings. Tensions rise slightly."
      },
      {
        "outcome_id": "bonding_moment",
        "probability": 15,
        "conditions": {
          "min_average_rapport": 7
        },
        "effects": {
          "rapport_bonus": 2,
          "sp_gain": 2
        },
        "message": "The casual meal becomes a genuine bonding moment. The family feels closer!"
      }
    ]
  }
}
```

### Step 4: Test

1. Start game
2. Call `/api/mods/load`
3. Call `/api/mods/integrate` with `mod_id: "activity_pizza_night"`
4. Test in-game!

### Step 5: Refine

Based on testing:
- Adjust costs
- Balance probabilities
- Refine dialogue
- Add more outcomes

---

## Community Resources

- **Mod Repository:** [Coming Soon]
- **Discord:** [Community Link]
- **Forums:** [Discussion Board]
- **Wiki:** [Mod Database]

---

## Changelog

### Version 1.0.0 (Current)
- Initial modding system release
- Character, Activity, Technique, Scenario mods supported
- 4 example mods included
- Full API documentation

---

## Credits

- **Mod System Design:** Family Dynamics RPG Team
- **Example Mods:** Community Contributors
- **Documentation:** Modding Guide Team

---

**Happy Modding!** 🎮

Create amazing content and share it with the community. We can't wait to see what you build!
