# Virt-A-Mate Integration for Family Dynamics RPG

## Overview

This integration transforms Family Dynamics RPG from a text-based game into a fully interactive 3D/VR experience using Virt-A-Mate.

### What This Adds:

✅ **Click-based interactions** instead of typing commands
✅ **3D characters** with facial expressions and clothing
✅ **Interactive environments** with clickable objects
✅ **Free camera movement** to view from any angle
✅ **VR support** for full immersion
✅ **Real-time synchronization** between game logic and 3D world

## Quick Start

### Prerequisites

1. **Virt-A-Mate** (installed and working)
2. **Python 3.8+** with packages from `requirements.txt`
3. **Visual Studio** or **MonoDevelop** (for C# plugin compilation)

### Installation Steps

#### 1. Install Python Dependencies

```bash
cd /path/to/family-dynamics-rpg
pip install -r requirements.txt
```

This installs:
- Flask (web server)
- websockets (VaM ↔ Python communication)
- Other game dependencies

#### 2. Compile VaM Plugin

1. Open `vam_plugin/FamilyDynamicsPlugin.cs` in Visual Studio
2. Add references:
   - VaM's DLLs (from your VaM installation)
   - WebSocketSharp (install via NuGet)
3. Build → Creates `FamilyDynamicsPlugin.dll`
4. Copy DLL to: `VaM/Custom/Scripts/YourName/FamilyDynamics/`

#### 3. Set Up VaM Scenes

Follow `vam_plugin/SCENE_SETUP_GUIDE.md` to create:
- Living Room (primary location)
- Kitchen
- Bedroom
- Cafe
- Park

#### 4. Create Characters

Follow `vam_plugin/CHARACTER_APPEARANCES.md` to create:
- Ruth (65F, grandmother)
- Tom (68M, grandfather)
- Melanie (35F, daughter)
- Dawn (32F, yoga instructor)
- Vanessa (29F, influencer)
- Derek (40M, lawyer)
- Karen (42F, PTA president)

#### 5. Test Connection

**Terminal 1 - Start Python Bridge:**
```bash
python test_vam_bridge.py --server
```

**Terminal 2 - Start Game Server:**
```bash
python app.py
```

**In VaM:**
1. Load your Living Room scene
2. Add Session Plugin → Choose `FamilyDynamicsPlugin.dll`
3. Click "Connect to Game Server"
4. Should show "Connected" status

## How It Works

### Architecture Diagram

```
┌─────────────────────────────────────┐
│   Virt-A-Mate (3D Environment)      │
│   - Click on Ruth → Event           │
│   - Click on TV → Event             │
│   - VR hand touches phone → Event   │
│                                     │
│   FamilyDynamicsPlugin.cs           │
└─────────────┬───────────────────────┘
              │
              │ WebSocket (port 8765)
              │
┌─────────────▼───────────────────────┐
│   Python Backend (Flask)            │
│   - vam_bridge.py (WebSocket server)│
│   - Game logic, AI, hypnosis        │
│   - Character state management      │
│                                     │
│   Systems: dialogue, memory, goals  │
└─────────────────────────────────────┘
```

### Communication Flow

**User Action → Game Response:**

1. **You click on Ruth in VaM**
   ```
   VaM sends: {type: "click_character", data: {character: "Ruth"}}
   ```

2. **Python receives event, shows menu**
   ```
   Python sends: {type: "show_menu", data: {
     title: "Interact with Ruth",
     options: ["Talk", "Observe", "Hypnosis"]
   }}
   ```

3. **You select "Talk"**
   ```
   VaM sends: {type: "menu_selection", data: {selection: "talk", character: "Ruth"}}
   ```

4. **Python generates dialogue via LLM**
   ```
   Python sends: {type: "show_dialogue", data: {
     character: "Ruth",
     text: "Oh hello dear, would you like some tea?",
     duration: 5.0
   }}
   ```

5. **VaM displays speech bubble and plays animation**

### Interaction Examples

#### Example 1: Watching TV

```
1. Click TV in living room
   → Menu appears: "Watch TV" | "Turn Off"

2. Select "Watch TV"
   → Time advances 30 minutes
   → TV screen shows content
   → Nearby characters react
   → "Ruth sits down next to you"

3. Game state updates
   → Python tracks: player watched TV
   → Triggers events based on time/characters present
```

#### Example 2: Reading Hypnosis Book

```
1. Click book on coffee table
   → Menu: "Read (30 min)" | "Study Technique"

2. Select "Study Technique"
   → Menu shows available techniques
   → "Rapport Building" (unlocked)
   → "Mirroring" (unlocked)
   → "Progressive Relaxation" (locked - need more practice)

3. Select "Progressive Relaxation"
   → Time advances
   → Book glows with progress indicator
   → +5 SP earned
   → Notification: "Technique unlocked!"
```

#### Example 3: Talking to Character

```
1. Click on Melanie
   → Character turns to face you
   → Menu: "Talk" | "Observe" | "Use Hypnosis"

2. Select "Talk"
   → Dialogue interface opens
   → Previous conversation history shown
   → Input: "How's work going?"

3. Melanie responds (LLM generated)
   → Speech bubble appears
   → Facial expression: Stressed
   → Animation: Sighs, rubs temples
   → "Ugh, don't even get me started..."

4. Rapport increases +1
   → Visual feedback: Heart icon floats up
   → Rapport bar fills slightly
```

## VR Mode

### Controls

**VR Controllers:**
- **Trigger:** Select/Click object
- **Grip:** Grab small objects (phone, book)
- **Thumbstick:** Teleport / Smooth movement
- **Menu Button:** Open game UI overlay

### VR Interactions

**Natural Interactions:**
- Look at character from any angle (they track your gaze)
- Walk around rooms freely
- Pick up phone → Brings up to face → Shows messages
- Touch TV → Turns on, shows menu
- Sit on couch → View height changes, character may join you

### Comfort Options

- **Teleport mode:** Point and click to move (comfort++)
- **Smooth locomotion:** WASD-style movement
- **Snap turning:** 45° increments
- **Vignette:** Reduces motion sickness

## Game Features in VR

### 1. Character Observation

**Look at Ruth from behind:**
- No typing required
- Just walk/teleport behind her
- View her clothing details
- Notice her posture, body language

**Observe facial expressions:**
- Get close to see microexpressions
- Notice when she's lying or uncomfortable
- Track emotional state changes in real-time

### 2. Object Interactions

**Phone:**
- Pick up → Automatically opens
- Read messages
- Call characters
- See notifications

**Books:**
- Pick up → Opens to bookmark
- Turn pages (gesture)
- Study specific sections

**Coffee Maker:**
- Touch → Menu appears
- Make coffee → Animation plays
- Smell particle effects (if VaM supports)

### 3. Time Progression

Time passes naturally:
- Watch clock on wall move
- Lighting changes (morning → afternoon → evening)
- Characters move based on schedules
  - 9 AM: Ruth in kitchen
  - 2 PM: Tom in living room reading
  - 6 PM: Everyone at dinner table

### 4. Character Autonomy

Characters have AI behaviors:
- Walk around based on schedules
- Perform idle animations (read book, check phone)
- React to player proximity
- Trigger autonomous events (PHS activations)

## Advanced Features

### Post-Hypnotic Suggestions (PHS) Visualization

When a PHS triggers:
```
1. Character hears trigger word: "Feeling stressed"
2. Visual effect: Subtle glow around character
3. Character pauses briefly (processing)
4. Animation: Performs PHS response
5. Speech bubble: "I should go talk to them..."
6. Character walks toward you
```

### Trance Depth Visualization

During hypnosis sessions:
```
Depth Level 1 (Light): Character's eyes slightly glazed
Depth Level 2 (Medium): Relaxed posture, slow breathing animation
Depth Level 3 (Deep): Head slightly tilted, very relaxed
Depth Level 4 (Somnambulistic): Completely still, responsive to commands
```

Visual indicators:
- Particle effects (shimmer around character)
- Eye dilation (pupil size changes)
- Color grading (slight blur/glow)

### Clothing System

Real-time outfit changes:
```python
# Python sends:
{
  "type": "change_clothing",
  "data": {
    "character": "Melanie",
    "outfit": "yoga_pants_sports_bra",
    "reason": "just_got_back_from_gym"
  }
}
```

VaM applies clothing preset instantly.

Player sees:
- Melanie appears in gym clothes
- Slightly sweaty skin shader
- Hair in ponytail

### Mood Lighting

Scenes adapt to emotional context:
- Romantic moment: Warmer, dimmer lights
- Tense confrontation: Harsher, cooler lights
- Hypnosis session: Dim, focused lighting
- Happy scene: Bright, natural light

## Development Workflow

### Testing New Features

1. **Make changes in Python:**
   ```bash
   # Edit game logic
   vim systems/dialogue_system.py
   ```

2. **Restart Python backend:**
   ```bash
   # Terminal: Ctrl+C, then
   python app.py
   ```

3. **Test in VaM:**
   - VaM stays running (no restart needed)
   - Plugin auto-reconnects
   - Test new features immediately

### Debugging

**Python side:**
```bash
# Run with debug logging
python app.py --debug
```

Shows:
- All WebSocket messages
- Event handling
- LLM API calls
- Game state changes

**VaM side:**
- Check VaM logs: `VaM/Logs/`
- Plugin logs: Console in VaM
- Use breakpoints in Visual Studio

### Adding New Interactions

**Example: Add "Hug" interaction**

1. **Update Python handler:**
   ```python
   # In vam_bridge.py
   async def handle_click_character(data):
       return {
           'type': 'show_menu',
           'data': {
               'options': [
                   {'id': 'hug', 'label': 'Hug'},  # ← New option
                   # ... existing options
               ]
           }
       }
   ```

2. **Add menu handler:**
   ```python
   async def handle_menu_selection(data):
       if data['selection'] == 'hug':
           character = data['context']['character']
           # Game logic for hug
           return {
               'type': 'play_animation',
               'data': {
                   'character': character,
                   'animation': 'hug_embrace'
               }
           }
   ```

3. **Create animation in VaM:**
   - Record hug animation for each character
   - Save as `[Character]_hug_embrace.anim`
   - Plugin loads it when triggered

4. **Test:**
   - Click character
   - Select "Hug"
   - Watch animation play

## Troubleshooting

### "Could not connect to server"

**Check:**
1. Is Python bridge running? (`python test_vam_bridge.py --server`)
2. Firewall blocking port 8765?
3. Correct IP in VaM plugin? (should be `ws://localhost:8765`)

### "Character not responding to clicks"

**Check:**
1. Character atom named correctly? (e.g., "Ruth", not "Person#1")
2. Collider added to character?
3. Plugin registered the character? (check console logs)

### "Animations not playing"

**Check:**
1. Animation files in correct folder?
2. Animation names match exactly? (case-sensitive)
3. Character has required animation controller?

### "Lighting not changing with time"

**Check:**
1. Time update messages being sent? (check Python logs)
2. Lighting script attached to main light?
3. Light object named correctly? ("MainLight")

## Performance Optimization

### For Better FPS in VaM:

1. **Reduce character count:**
   - Only load characters present in current scene
   - Unload characters in other locations

2. **Lower graphics settings:**
   - Reduce shadow quality
   - Lower texture resolution
   - Disable post-processing effects

3. **Optimize scenes:**
   - Use asset bundles for common objects
   - Bake lighting where possible
   - Reduce polygon count on furniture

4. **Limit WebSocket messages:**
   - Only send updates when state changes
   - Batch multiple updates together
   - Use delta updates (only changed fields)

## Roadmap

### Phase 1: Core Integration ✅
- [x] WebSocket bridge
- [x] Basic character interactions
- [x] Object clicking
- [x] Menu system
- [x] Scene setup guides

### Phase 2: Enhanced Visuals (In Progress)
- [ ] Trance depth visualization
- [ ] PHS activation effects
- [ ] Mood-based lighting
- [ ] Character autonomy/AI behaviors

### Phase 3: Full VR Support
- [ ] VR controller input
- [ ] Hand tracking for interactions
- [ ] Voice commands (speech-to-text)
- [ ] Haptic feedback for events

### Phase 4: Advanced Features
- [ ] Multiplayer (control different characters)
- [ ] Scene editor (create custom locations)
- [ ] Animation timeline system
- [ ] Photo mode / replay system

## Resources

**Documentation:**
- `VIRT_A_MATE_INTEGRATION.md` - High-level overview
- `vam_plugin/CHARACTER_APPEARANCES.md` - Character creation guide
- `vam_plugin/SCENE_SETUP_GUIDE.md` - Scene building tutorial
- `vam_plugin/FamilyDynamicsPlugin.cs` - Plugin source code

**Code:**
- `systems/vam_bridge.py` - WebSocket server
- `test_vam_bridge.py` - Testing utilities
- `vam_plugin/` - All VaM-related files

**Community:**
- VaM Discord: [Join here](https://discord.gg/vam)
- VaM Hub: https://hub.virtamate.com/
- Plugin development: https://github.com/vam-community/

## FAQ

**Q: Do I need VR to use this?**
A: No! Desktop mode (mouse/keyboard) works great. VR is optional.

**Q: Can I use other 3D engines instead of VaM?**
A: Yes, the WebSocket bridge can work with Unity, Unreal, etc. You'd need to rewrite the client plugin for that engine.

**Q: Will this work with existing save files?**
A: Yes! The 3D layer is just visualization. Your game progress is safe.

**Q: Can I still play in text mode?**
A: Absolutely. You can run `python main.py` for CLI or use the web interface without VaM.

**Q: How big are the VaM scenes?**
A: Expect 1-5 GB for full game (all scenes, characters, animations). Start with just Living Room (~500 MB).

**Q: Does this require good hardware?**
A: VaM is demanding. Recommended:
- CPU: i7 or Ryzen 7
- GPU: RTX 2070 or better
- RAM: 16+ GB
- VR: GTX 1080 minimum

## Contributing

Want to help improve the VaM integration?

1. Create new character appearances
2. Build additional scenes (gym, office, etc.)
3. Design custom animations
4. Optimize performance
5. Add new interaction types

Submit PRs or share your creations on the community hub!

---

**Ready to start? Begin with `test_vam_bridge.py` to verify your setup!**

```bash
python test_vam_bridge.py
```

Good luck, and enjoy your immersive Family Dynamics RPG experience! 🎮
