# Virt-A-Mate Integration Guide

## Overview

This integration replaces text-based interactions with a fully interactive 3D environment where you can:
- Click on characters to interact with them
- Click on objects (TV, phone, book) to use them
- Move the camera freely to look at characters from any angle
- Use VR to physically walk around and touch objects

## Architecture

### 1. Virt-A-Mate (Frontend - 3D Environment)
- Renders all scenes in 3D
- Handles user input (mouse clicks, VR controllers)
- Displays characters with expressions, clothing, poses
- Manages camera/VR movement

### 2. Python Backend (Game Logic)
- Flask server with WebSocket support
- Character AI, dialogue system, hypnosis mechanics
- Game state management, save/load
- LLM integration for conversations

### 3. Communication Bridge
- WebSocket connection between VaM and Python
- Real-time bidirectional updates
- Event system for interactions

## How It Works

### User Interaction Flow:

```
1. You click on Ruth in VaM
   ↓
2. VaM plugin sends: {"action": "interact", "target": "Ruth"}
   ↓
3. Python backend opens dialogue menu
   ↓
4. You select "Talk about the weather"
   ↓
5. Python sends Ruth's response via LLM
   ↓
6. VaM displays speech bubble + plays animation
   ↓
7. Ruth's emotional state changes → VaM updates her expression
```

### Object Interaction:

```
1. You click TV in living room
   ↓
2. VaM sends: {"action": "use_object", "object": "tv"}
   ↓
3. Python checks: Can player watch TV? Time of day? Characters present?
   ↓
4. Python advances time, triggers events
   ↓
5. VaM shows TV screen animation, updates lighting
```

## Setup Instructions

### Part 1: Virt-A-Mate Scene Creation

#### Required Assets:
- Character models for: Ruth (65F), Tom (68M), Melanie (35F), Dawn (32F), etc.
- Environment assets: Home (living room, kitchen, bedroom, bathroom)
- Props: TV, couch, phone, books, coffee table, etc.
- Clothing items matching character descriptions

#### Scene Setup Checklist:

**Living Room Scene:**
- [ ] Couch, armchairs, coffee table
- [ ] TV with screen (can show content)
- [ ] Bookshelf with individual books
- [ ] Phone on table
- [ ] Windows with day/night lighting
- [ ] Character spawn points
- [ ] Collision for all objects
- [ ] Click triggers on interactive objects

**Kitchen Scene:**
- [ ] Counter, stove, fridge, table
- [ ] Coffee maker, mugs
- [ ] Food items
- [ ] Clock on wall
- [ ] Character positions

### Part 2: VaM Plugin Development

I'll create a C# plugin that:
- Detects clicks on objects and characters
- Sends events to Python backend
- Receives updates (character state, time, dialogue)
- Updates character expressions, poses, clothing
- Manages VR controllers

### Part 3: Python Backend Updates

Update the Flask server to:
- Add WebSocket support
- Handle interaction events from VaM
- Send real-time updates back to VaM
- Maintain game state synchronization

## Interaction System

### Interactive Objects:

| Object | Actions | Game Effects |
|--------|---------|--------------|
| TV | Watch, Turn On/Off | Advance time, trigger events, characters react |
| Phone | Check, Call, Text | Contact characters, view messages |
| Book | Read, Study | Learn hypnosis, advance time |
| Coffee Maker | Make Coffee | Increase alertness, start conversations |
| Character | Talk, Observe, Touch | Dialogue, build rapport, trigger PHS |
| Couch | Sit | Rest, wait for characters, pass time |
| Mirror | Look | Check appearance, change clothing |

### Camera Controls:

**Desktop Mode:**
- Left Click + Drag: Rotate camera
- Right Click: Context menu for selected object
- Scroll: Zoom in/out
- WASD: Move around room

**VR Mode:**
- Physically walk around
- Point controller at object → highlight
- Trigger button: Interact
- Grab: Pick up small objects
- Menu button: Open game UI

## Technical Implementation

### WebSocket Messages

**From VaM → Python:**
```json
{
  "type": "interaction",
  "data": {
    "action": "click_character",
    "target": "Ruth",
    "player_position": {"x": 1.5, "y": 0, "z": 2.0},
    "camera_angle": "from_behind"
  }
}
```

**From Python → VaM:**
```json
{
  "type": "update_character",
  "data": {
    "character": "Ruth",
    "emotional_state": "curious",
    "expression": "slight_smile",
    "dialogue": "Oh, you're interested in that old book?",
    "animation": "turn_to_player"
  }
}
```

### State Synchronization

Every game state change is mirrored in VaM:
- Character location changes → VaM teleports character
- Time advances → Lighting updates, character schedules
- Clothing changes → VaM updates character outfit
- Emotional states → Facial expressions update
- PHS activates → Special visual effect + animation

## Development Phases

### Phase 1: Basic Bridge (Start Here)
- [x] WebSocket server in Flask
- [ ] Simple VaM plugin to send click events
- [ ] Test: Click character → Python receives event
- [ ] Test: Python sends message → VaM displays it

### Phase 2: Scene Setup
- [ ] Build living room in VaM
- [ ] Create character appearances (Ruth, Tom, Melanie)
- [ ] Add clickable objects with triggers
- [ ] Test all interactions

### Phase 3: Full Integration
- [ ] Complete dialogue system in 3D
- [ ] Character animations for all emotional states
- [ ] Object interactions with visual feedback
- [ ] Time system with lighting changes
- [ ] Character scheduling (characters move between locations)

### Phase 4: VR Support
- [ ] VR controller mapping
- [ ] Hand tracking for object manipulation
- [ ] Comfort options (teleport, smooth locomotion)
- [ ] VR UI for stats, inventory, menus

### Phase 5: Advanced Features
- [ ] Character autonomy (walk around, do things)
- [ ] Multiplayer perspective (control different characters)
- [ ] Advanced physics interactions
- [ ] Voice recognition for dialogue input

## Files to Create

1. `vam_bridge.py` - WebSocket server and VaM communication
2. `vam_plugin/` - C# plugin for Virt-A-Mate
3. `vam_scenes/` - Scene setup guides and JSONs
4. `vam_character_guide.md` - Character appearance specifications
5. `interaction_system.py` - Handle object/character interactions

## Next Steps

**To get started, we need to:**

1. ✅ Set up WebSocket server in Python
2. Create basic VaM plugin template
3. Document character appearances for VaM
4. Create scene setup guide for living room
5. Test basic click → response flow

**Do you want me to start with:**
- A) WebSocket bridge + simple VaM plugin template?
- B) Character appearance guide for VaM setup?
- C) Scene interaction system design?
- D) All of the above?

Let me know and I'll start building!
