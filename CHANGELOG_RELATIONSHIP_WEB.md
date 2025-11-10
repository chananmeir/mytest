# Relationship Web System - Implementation Complete! 🎉

## What Was Added

We've successfully implemented a **Character Relationship Web** system that makes your Family Dynamics RPG truly dynamic and realistic!

### Core Hypnosis Mechanics (Preserved)
✅ All existing hypnosis features intact:
- Post-Hypnotic Suggestions (PHS)
- Rapport building
- Suggestion Points (SP)
- Emotional states
- Resistance levels
- Memory system
- All hypnosis techniques

### NEW: Social Dynamics Layer

## 1. New Files Created

### `systems/relationship_web.py` (455 lines)
Core relationship mechanics:
- Character-to-character relationship tracking
- Observation system (characters notice changes)
- Gossip generation and credibility
- Protective behavior detection
- Alliance strength calculation
- Relationship context for LLM conversations

**Key Functions:**
- `observe_character_changes()` - Detect when characters notice others changing
- `generate_gossip()` - Generate gossip between characters
- `spread_suspicion()` - Suspicion spreads through social network
- `check_protective_response()` - Family members protect each other
- `calculate_alliance_strength()` - Detect coordinated resistance
- `detect_coordinated_resistance()` - Find character alliances

### `systems/social_dynamics.py` (392 lines)
Integration layer that hooks into gameplay:
- Automatic observation triggers
- Cascade effects when PHS activates
- Periodic gossip sessions
- Alliance monitoring
- Relationship context injection

**Key Functions:**
- `on_phs_activation()` - Others notice PHS-triggered behavior
- `on_rapport_increase()` - Others notice player's growing influence
- `on_emotional_state_change()` - Others notice mood shifts
- `trigger_gossip_session()` - Characters gossip during time advancement
- `check_alliances()` - Monitor alliance formation

## 2. Integration Points in `app.py`

### In `/api/talk` (Conversation System)
**Lines 412, 444-449**: Added SocialDynamics import and relationship context
```python
# Characters are now aware of their relationships
relationship_context = SocialDynamics.get_relationship_context_for_conversation(char, game_state)
```

**Lines 501-507**: Rapport change observers
```python
# Others notice when someone becomes close to player
if abs(analysis['rapport_change']) >= 2:
    social_msgs = SocialDynamics.on_rapport_increase(...)
```

**Lines 518-523**: Emotional state observers
```python
# Others notice emotional changes
social_msgs = SocialDynamics.on_emotional_state_change(...)
```

**Lines 539-544**: PHS activation observers
```python
# Others notice out-of-character behavior
social_msgs = SocialDynamics.on_phs_activation(game_state, char, phs)
```

### In `/api/advance-time` (Time System)
**Lines 1347-1352**: Periodic gossip sessions
```python
# Characters gossip when time passes
if minutes >= 15:
    gossip_msgs = SocialDynamics.trigger_gossip_session(game_state)
```

**Lines 1407-1409**: Gossip messages in response
```python
# Add gossip messages to player notifications
if gossip_messages:
    response['messages'].extend(gossip_messages)
```

### New API Endpoints

#### `/api/social/alliances` (GET)
Check for character alliances forming against player
```json
{
  "success": true,
  "alliances": [
    {
      "character1": "Ruth",
      "character2": "Tom",
      "alliance_strength": 75,
      "threat_level": "high"
    }
  ],
  "threat_level": "high"
}
```

#### `/api/social/relationship-map` (GET)
Get full relationship network visualization
```json
{
  "success": true,
  "relationships": [
    {
      "name": "Ruth",
      "player_suspicion": 45,
      "relationships": {
        "Tom": {"score": 12, "type": "close", "protective_threshold": 40}
      },
      "character_suspicions": {"Lisa": 30}
    }
  ]
}
```

## 3. Documentation

### `RELATIONSHIP_WEB_GUIDE.md` (680 lines)
Comprehensive user guide covering:
- How the system works
- Observation mechanics
- Gossip spreading
- Protective behaviors
- Alliance formation
- Strategic implications
- API documentation
- Gameplay examples
- Character-specific behaviors
- Advanced strategies

### `test_relationship_web.py` (300 lines)
Test suite demonstrating:
- Observation system
- Gossip mechanics
- Protection triggers
- Alliance detection
- Cascading effects

## 4. Game Flow Changes

### Before (Simple)
```
Player manipulates character
  ↓
Character changes
  ↓
Done
```

### After (Complex Social Web)
```
Player manipulates character
  ↓
Character changes
  ↓
Other characters observe (based on relationships)
  ↓
Observers gossip to close friends
  ↓
Suspicion spreads through network
  ↓
Protective responses trigger
  ↓
Alliances form if multiple suspicious
  ↓
Possible coordinated resistance!
```

## Features in Action

### Observation Example
```
You plant PHS on Lisa
  ↓
PHS activates (Lisa acts strangely)
  ↓
👀 Ruth notices Lisa is acting different
🤔 Tom thinks Lisa's behavior is unusual
  ↓
Both increase their suspicion
```

### Gossip Chain Example
```
Ruth notices something (suspicion: 40)
  ↓
💬 Ruth tells Dawn about suspicions
  ↓
Dawn's suspicion increases by 20
  ↓
💬 Dawn tells Karen about concerns
  ↓
Karen's suspicion increases by 12
  ↓
Three people now suspicious!
```

### Protection Example
```
You manipulate Lisa repeatedly
  ↓
Ruth's concern reaches 50 (threshold: 40)
  ↓
⚠️ Ruth warns you: "Leave Lisa alone."
  ↓
Ruth's player_suspicion increases by 10
```

### Alliance Example
```
Ruth: 60% suspicious
Tom: 55% suspicious
Relationship: 12 (married)
  ↓
Alliance strength: 75%
  ↓
🚨 WARNING: Ruth and Tom are working together against you!
```

## Strategic Depth Added

### Before
- Manipulate characters individually
- Only worry about detection by target
- Linear progression

### After
- Navigate complex social network
- Consider relationship ripple effects
- Manage information flow through gossip
- Break up alliances
- Time manipulations to avoid clustering
- Target isolated characters first
- Use defensive PHS to cover tracks

## Technical Details

### Character Data Structure (Already Existed)
```python
relationships: Dict[str, int]          # {name: score 0-20}
character_interactions: List[Dict]     # Interaction history
player_suspicion: int                  # 0-100
character_suspicions: Dict[str, int]   # {name: suspicion 0-100}
```

### Observation Calculation
```python
base_chance = 30
+ relationship_modifier (0-30)
+ personality_modifier (0-25)
+ existing_suspicion_modifier (0-20)
+ change_magnitude_bonus (0-20)
= final_observation_chance (max 95%)
```

### Gossip Credibility
```python
base_credibility = relationship_score * 5
+ personality_modifiers (-20 to +25)
= final_credibility (0-100%)
```

### Protection Thresholds
- Very Close (15-20): Threshold 20%
- Close (10-14): Threshold 40%
- Neutral (5-9): Threshold 60%
- Distant (0-4): Threshold 80%

### Alliance Strength
```python
mutual_relationship = (score1 + score2) / 2
+ similar_suspicion_bonus (0-20)
+ both_highly_suspicious_bonus (0-30)
= alliance_strength (0-100)
```

## Testing

### Module Load Tests
```bash
✓ relationship_web.py loads successfully
✓ social_dynamics.py loads successfully
```

### Integration Points Verified
✅ Conversation system hooks
✅ Time advancement hooks
✅ PHS activation hooks
✅ Rapport change hooks
✅ Emotional state hooks
✅ API endpoints added

## What This Means for Gameplay

### More Realistic
- Family actually acts like a family
- Close relationships protect each other
- Information spreads naturally
- Social consequences for manipulation

### More Challenging
- Can't just spam PHS
- Must consider social network
- Suspicion cascades through relationships
- Alliances can end the game

### More Strategic
- Target selection matters (isolation vs. relationships)
- Timing matters (space out manipulations)
- Information management (control gossip flow)
- Alliance breaking (divide and conquer)

### More Rewarding
- Clever social manipulation feels earned
- Successfully navigating web is satisfying
- Multiple layers of challenge
- Emergent storytelling from social dynamics

## Summary

The hypnosis core is intact - but now it operates within a **realistic social context**. You're not just manipulating individuals; you're navigating a complex family social network where:

- **Actions have consequences** that ripple through relationships
- **Information spreads** through gossip and observation
- **People protect** those they care about
- **Alliances form** against common threats
- **Social chess** replaces simple manipulation

The game has evolved from "hypnosis simulator" to "social dynamics chess with hypnosis powers"! 🎮

---

**Next Steps:**
1. Test the system in-game
2. Balance observation chances if needed
3. Add UI visualizations for relationship map
4. Consider adding more alliance types (helpful alliances?)
5. Expand character-specific behaviors

**Files Modified:**
- `app.py` (4 integration points + 2 new endpoints)
- `models/character.py` (already had relationship infrastructure)

**Files Created:**
- `systems/relationship_web.py`
- `systems/social_dynamics.py`
- `RELATIONSHIP_WEB_GUIDE.md`
- `test_relationship_web.py`
- `CHANGELOG_RELATIONSHIP_WEB.md` (this file)
