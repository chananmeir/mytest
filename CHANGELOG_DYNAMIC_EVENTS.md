# Dynamic Random Events System - Implementation Complete! 🎲

## What Was Added

We've implemented a **Dynamic Random Events System** that makes gameplay unpredictable and creates emergent stories. The world now acts on YOU, not just the other way around!

### Core Systems Still Intact
✅ All hypnosis mechanics preserved
✅ Relationship Web fully integrated
✅ All existing systems enhanced

### NEW: Dynamic Random Events Layer

## Files Created

### 1. `systems/dynamic_events.py` (590 lines)
Core event system with probability engine.

**Key Classes:**
- `EventOption` - Player choice with costs, effects, and consequences
- `DynamicEvent` - Event definition with triggers and conditions
- `DynamicEventSystem` - Probability engine and event management

**Key Functions:**
- `calculate_event_probability()` - Dynamic probability based on game state
- `should_trigger_event()` - Roll for event occurrence
- `check_event_conditions()` - Validate trigger requirements
- `get_available_events()` - Find events that can trigger
- `select_event()` - Weighted random selection
- `trigger_event()` - Activate event and record history
- `respond_to_event()` - Process player choice
- `check_opportunity_expiration()` - Monitor time-limited events

### 2. `data/event_library.py` (600+ lines)
Library of 12 sample events across all 6 types.

**Event Categories:**
- **Encounters** (2 events): Coffee Spill, Overheard Gossip
- **Character-Initiated** (2 events): Tom's Crisis, Melanie's Advice
- **Opportunities** (2 events): Dawn Alone, Vulnerable Vanessa
- **Crises** (2 events): Family Argument, Derek's Injury
- **Visitors** (2 events): Ruth Suspicious, Joint Intervention
- **Memory Triggers** (2 events): Public PHS Activation, Déjà Vu

Each event has:
- Multiple choice options
- Trigger conditions
- Social consequences
- Integration with relationship web

### 3. `DYNAMIC_EVENTS_GUIDE.md` (800+ lines)
Comprehensive documentation covering:
- All 6 event types
- Probability engine mechanics
- Strategic guide
- Event flow diagrams
- API documentation
- Example scenarios
- Advanced tactics

## Integration Points

### In `app.py`

#### Lines 1361-1377: Time Advancement Integration
```python
# DYNAMIC RANDOM EVENTS: Check if a random event should trigger
should_trigger, event_type = DynamicEventSystem.should_trigger_event(game_state)
if should_trigger:
    available_events = DynamicEventSystem.get_available_events(...)
    selected_event = DynamicEventSystem.select_event(available_events)
    event_result = DynamicEventSystem.trigger_event(game_state, selected_event)

# Check for opportunity expiration
opportunity_expired_msg = DynamicEventSystem.check_opportunity_expiration(game_state)
```

Events trigger automatically during time advancement with:
- 25% base chance
- Dynamic probability modifiers
- Weighted type selection
- Condition checking

#### Lines 1440-1446: Response Integration
```python
# Add dynamic random event to response
if dynamic_event_triggered:
    response['dynamic_event'] = dynamic_event_triggered

# Add opportunity expiration warning
if opportunity_expired_msg:
    response['messages'].append(opportunity_expired_msg)
```

### New API Endpoints

#### `/api/events/respond` (POST) - Lines 2405-2429
Respond to an event with a chosen option:
```json
{
  "event_id": "initiated_tom_work_crisis",
  "option_id": "listen_empathetically"
}

Response:
{
  "success": true,
  "outcome": "Tom opens up completely...",
  "messages": ["Rapport with Tom: 8 → 11"],
  "option_success": true,
  "allows_phs": false,
  "phs_success_bonus": 0
}
```

#### `/api/events/active` (GET) - Lines 2432-2456
Get currently active event or opportunity:
```json
{
  "success": true,
  "active_event": {
    "event": {...},
    "time_remaining": 7,
    "type": "opportunity"
  }
}
```

#### `/api/events/probabilities` (GET) - Lines 2459-2471
Check current event probabilities (debugging/UI):
```json
{
  "success": true,
  "probabilities": {
    "encounter": 20,
    "initiated": 30,
    "opportunity": 10,
    "crisis": 25,
    "visitor": 18,
    "memory_trigger": 21
  }
}
```

## Event Types & Mechanics

### 1. Random Encounters (☕ 20% base)
Unexpected situations like spilling coffee on Ruth.
- Quick decisions
- Often have observers
- Low-medium consequence
- Good for rapport building

### 2. Character-Initiated (💬 15% + rapport bonus)
Characters come to YOU with problems.
- Unlocked by building rapport
- Perfect for PHS (they're receptive!)
- High rapport gain potential
- Creates bonding moments

**Probability:** +5% per character with rapport ≥ 10

### 3. Opportunity Windows (⏰ 10%)
Time-limited high-value moments.
- **EXPIRES** - must act fast!
- 2x rapport gain
- Lower detection risk
- High PHS success bonuses

**Example:** "Dawn alone - 10 minutes only!"

### 4. Crisis Events (🚨 5% + suspicion bonus)
Family emergencies requiring immediate response.
- High pressure
- Everyone watching
- Major social consequences
- Risky PHS opportunities

**Probability:** +15% if suspicion > 50%, +10% per alliance

### 5. Surprise Visitors (🚪 8% + alliance bonus)
Characters show up unexpectedly.
- Triggered by high suspicion
- Alliances coordinate visits
- Can lead to GAME OVER
- Must respond immediately

**Probability:** +10% if suspicion > 40%, +8% per alliance

### 6. Memory Triggers (💫 12% + PHS bonus)
PHS activations or déjà vu moments.
- Can expose manipulation
- Opportunity to reinforce PHS
- Confusion can be exploited

**Probability:** +3% per active PHS

## Event Options

Every event has multiple choices with:

### Costs
```python
sp_cost=3           # Pay SP
money_cost=50       # Pay money
time_cost=30        # Takes minutes
requires_rapport=10 # Need rapport threshold
```

### Effects
```python
rapport_changes={"Ruth": 2, "Tom": -1}
emotional_state_changes={"Ruth": "grateful"}
suspicion_changes={"Dawn": -10}
sp_gain=2
money_gain=100
```

### PHS Opportunities
```python
allows_phs=True
phs_target="Ruth"
phs_success_bonus=25    # +25% success!
phs_detection_risk=40   # 40% caught risk
```

### Social Integration
```python
social_effect="Dawn sees you being kind"
observers=["Dawn", "Tom"]  # Who watches
```

Effects trigger relationship web observations!

### Success Chances
```python
success_chance=70  # 70% to succeed
success_text="It works!"
failure_text="It backfires..."
```

## Probability Engine

### Base Mechanics
```
Time advances 15+ minutes
  ↓
25% chance event triggers
  ↓
Calculate probabilities:
  Base rates
  + Suspicion modifiers
  + Rapport modifiers
  + Alliance modifiers
  + PHS count modifiers
  + Time since last event
  ↓
Weighted random selection
  ↓
Check event conditions
  ↓
Trigger event
```

### Dynamic Modifiers

**High Average Suspicion (> 50%):**
- Crisis: +15%
- Visitor: +10%

**Strong Rapport:**
- Initiated: +5% per character with rapport ≥ 10

**Active Alliances:**
- Crisis: +10% per alliance
- Visitor: +8% per alliance

**Active PHS:**
- Memory Trigger: +3% per PHS

**Time Since Last Event:**
- If > 2 hours: All probabilities × 1.5

## Event Conditions

Events check requirements before triggering:

### Rapport Conditions
```python
min_rapport={"Tom": 5}      # Need 5+ with Tom
max_rapport={"Ruth": 10}    # Need < 10 with Ruth
```

### Suspicion Conditions
```python
min_suspicion={"Dawn": 40}  # Dawn must be suspicious
```

### Emotional State
```python
required_emotional_states={"Tom": ["vulnerable", "stressed"]}
```

### Location & Time
```python
required_location="kitchen"
required_time_period="evening"
```

### Alliance Strength
```python
alliance_strength_threshold=60  # Need 60%+ alliance
```

## Integration with Relationship Web

Events seamlessly integrate with the relationship web:

### Observer System
```
Event option has observers
  ↓
Observers use relationship_web.observe_character_changes()
  ↓
They notice behavioral changes
  ↓
Gossip may spread
  ↓
Suspicion cascades
```

### Example Integration
```
EVENT: Coffee Spill
OPTION: Plant PHS on Ruth
OBSERVERS: Dawn, Tom

You plant PHS...
  ↓
Dawn observes Ruth being receptive to you
  ↓
Dawn's suspicion +5 (she noticed something odd)
  ↓
Dawn tells Tom (gossip system)
  ↓
Tom's suspicion +3
  ↓
Social cascade complete!
```

## Cooldown & Limits

### Event Cooldowns
```python
cooldown_hours=24  # Can't trigger again for 24 hours
```

Prevents spam, ensures variety.

### One-Time Events
```python
one_time=True  # Only happens once
```

Special story moments that can't repeat.

### Opportunity Expiration
```python
window_expires_in=10  # Expires in 10 minutes
```

System checks expiration on every time advancement.
Player sees: "⏰ Opportunity expires in X minutes!"

## Event History Tracking

Game state now tracks:
```python
game_state.event_history = [
    {
        'event_id': 'initiated_tom_work_crisis',
        'triggered_at': 1250,  # Game time in minutes
        'timestamp': '2024-01-15T14:30:00'
    },
    ...
]

game_state.last_event_time = 1250
game_state.active_opportunity = {
    'event_id': 'opportunity_dawn_alone',
    'expires_at': 1260
}
game_state.completed_events = {'melanie_advice_once'}
```

## Gameplay Impact

### Before Events
```
Player-driven:
  - Choose when to talk
  - Choose when to manipulate
  - Full control of pacing

Predictable:
  - Optimize single strategy
  - No surprises
  - Same flow every time
```

### After Events
```
World-driven:
  - Events happen TO you
  - Must react to situations
  - Urgency from time limits

Unpredictable:
  - Can't optimize perfectly
  - Must adapt
  - Every playthrough different
```

### Strategic Depth Added

**New Considerations:**
1. **SP Management** - Save for opportunities
2. **Risk Assessment** - Observers present?
3. **Time Pressure** - Windows expire!
4. **Consequence Prediction** - Social cascades
5. **Preparation** - Build rapport to unlock events
6. **Defensive Play** - Handle crises safely

## Example Gameplay Flow

```
[MORNING]
Player talks to Tom, builds rapport to 8
  ↓
[ADVANCE TIME: 1 hour]
25% roll... EVENT TRIGGERS!
Type selected: Character-Initiated (high rapport bonus)
Event: Tom's Work Crisis
  ↓
💬 Tom pulls you aside: "Can we talk?"
Options:
  1. Listen empathetically (+3 rapport)
  2. Plant PHS [4 SP] (+25% success, vulnerable!)
  3. Dismiss him (-4 rapport)
  ↓
Player chooses #2: Plant PHS
Success! "When stressed, trust my advice"
Ruth observes, approves of support (+1 rapport with Ruth)
  ↓
[2 HOURS LATER]
25% roll... EVENT TRIGGERS!
Type selected: Memory Trigger (active PHS)
Event: Tom's PHS activates at family dinner
  ↓
💫 Tom publicly asks for your advice in front of everyone!
Dawn observes...
Roll: 65 (threshold: 60)
Dawn noticed it was unusual...
Dawn's suspicion +8
  ↓
[30 MINUTES LATER]
25% roll... EVENT TRIGGERS!
Type selected: Opportunity Window
Event: Dawn alone for 10 minutes
  ↓
⏰ Dawn Alone in Kitchen (10 min window)
Bonuses: 2x rapport, +20% PHS, -30% detection
  ↓
Player has 10 minutes to decide!
  ↓
[PLAYER ADVANCES TIME: 5 minutes]
Window still active: 5 minutes remaining
  ↓
[PLAYER ADVANCES TIME: 6 minutes]
⏰ Opportunity expired!
Missed the window...
```

## Summary Statistics

**Files Modified:** 1 (app.py)
**Files Created:** 3
  - systems/dynamic_events.py (590 lines)
  - data/event_library.py (600+ lines)
  - DYNAMIC_EVENTS_GUIDE.md (800+ lines)

**Total Lines Added:** ~2,000 lines

**Integration Points:**
  - Time advancement (automatic triggers)
  - Relationship web (observer reactions)
  - PHS system (bonus opportunities)
  - API (3 new endpoints)

**Event Library:**
  - 12 sample events
  - 6 event types
  - 40+ event options
  - Full relationship web integration

## What This Means for Gameplay

### More Dynamic
- Events happen when YOU don't expect them
- Must react to the world
- Can't always plan ahead

### More Urgent
- Opportunity windows create pressure
- Must act fast or lose chances
- Time matters more

### More Rewarding
- High-risk PHS during opportunities
- Vulnerability windows for bonuses
- Strategic timing pays off

### More Realistic
- Families have emergencies
- People come to you with problems
- Unexpected situations arise
- Life isn't always predictable

### More Replayable
- Different events each playthrough
- RNG creates unique stories
- Emergent narratives
- "That time when..." moments

## Next Steps (Optional Expansions)

1. **More Events** - Add 20+ more events
2. **Event Chains** - Events trigger follow-up events
3. **Character-Specific Events** - Unique to each character
4. **Story Arc Events** - Major plot moments
5. **Seasonal Events** - Holiday/birthday specific
6. **Location-Specific Events** - Per location type
7. **Time-of-Day Events** - Morning/evening specific
8. **Relationship Milestone Events** - Trigger at rapport thresholds

---

**The game now has THREE layers:**
1. **Hypnosis Core** - Your power
2. **Relationship Web** - Social consequences
3. **Dynamic Events** - Unpredictable situations

Together, they create a living, breathing family simulation where you navigate complex social dynamics, handle emergencies, seize opportunities, and manage the consequences of your manipulation! 🎲✨

**From "manipulation simulator" to "dynamic family drama with hypnosis powers"!**
