# Dynamic Random Events System - Complete Guide

## Overview

The **Dynamic Random Events System** adds unpredictable gameplay elements that create emergent stories and break the predictability of pure player-driven actions. Events react to your behavior, relationship dynamics, and the current state of the family.

**Core Principle:** The world acts on YOU, not just the other way around!

## Event Types

### 1. 🎲 Random Encounters (20% base probability)
Unexpected situations requiring quick decisions.

**Examples:**
- Coffee spill accidents
- Overheard conversations
- Lost items to find
- Witnessing private moments

**Characteristics:**
- Usually brief (5-15 minutes)
- Low to medium consequence
- Good for building/losing rapport quickly
- Often have observers

### 2. 💬 Character-Initiated Events (15% + rapport bonus)
Characters come to YOU with problems, requests, or confessions.

**Examples:**
- Tom's work crisis
- Melanie seeking advice
- Ruth needing emotional support
- Derek asking for help

**Characteristics:**
- Require minimum rapport
- Character must be in specific emotional state
- High rapport gain opportunities
- Perfect for planting PHS (they're receptive)
- Can create strong bonding moments

**Probability Modifiers:**
- +5% for each character with rapport ≥ 10

### 3. ⏰ Opportunity Windows (10% probability)
Time-limited chances for significant actions.

**Examples:**
- Dawn alone in kitchen (10 min window)
- Character in vulnerable emotional state (15 min)
- Private moment with no observers
- Character asking for specific help

**Characteristics:**
- **EXPIRES!** Time limit creates urgency
- Bonuses: 2x rapport gain, lower detection risk
- High-risk, high-reward PHS opportunities
- Must act quickly or lose the chance

**UI Warning:** ⏰ This opportunity expires in X minutes!

### 4. 🚨 Crisis Events (5% + suspicion bonus)
Family emergencies requiring immediate response.

**Examples:**
- Ruth & Melanie fighting publicly
- Derek's injury
- Family intervention
- Emotional breakdowns

**Characteristics:**
- **HIGH PRESSURE** - must respond immediately
- Multiple observers watching
- Decisions have major social consequences
- Can dramatically shift relationships
- Risky PHS opportunities (everyone watching)

**Probability Modifiers:**
- +15% if average suspicion > 50%
- +10% per alliance formed

### 5. 🚪 Surprise Visitors (8% + alliance bonus)
Characters show up unexpectedly, often confrontationally.

**Examples:**
- Ruth visiting when suspicious
- Dawn & Tom intervention (requires alliance)
- Character "dropping by" to investigate
- Confrontational visits

**Characteristics:**
- Triggered by high suspicion
- Alliances coordinate visits
- Must respond on the spot
- Can lead to GAME OVER if handled badly

**Probability Modifiers:**
- +10% if suspicion > 40%
- +8% per alliance

### 6. 💫 Memory Trigger Events (12% + PHS bonus)
PHS activations or memory-based moments.

**Examples:**
- PHS activates in public
- Déjà vu moments
- Character recalls past conversation
- Memory creates vulnerability

**Characteristics:**
- Tied to active PHS count
- Can expose your manipulation
- Opportunity to reinforce suggestions
- Confusion can be exploited

**Probability Modifiers:**
- +3% per active PHS

## Probability Engine

### Base Chances (on time advancement)
- **Any Event Triggers:** 25%
- **Event Type Selection:** Weighted by probabilities above

### Dynamic Modifiers

**High Suspicion (avg > 50%):**
```
Crisis: +15%
Visitor: +10%
```

**Strong Rapport (char rapport ≥ 10):**
```
Character-Initiated: +5% per character
```

**Active Alliances:**
```
Crisis: +10% per alliance
Visitor: +8% per alliance
```

**Active PHS Count:**
```
Memory Trigger: +3% per PHS
```

**Time Since Last Event:**
```
If > 2 hours: All probabilities × 1.5
```

## Event Conditions

Events have trigger requirements that must be met:

### Rapport Requirements
```python
min_rapport: {"Tom": 5}      # Need 5+ rapport with Tom
max_rapport: {"Ruth": 10}    # Need < 10 rapport with Ruth
```

### Suspicion Requirements
```python
min_suspicion: {"Dawn": 40}  # Dawn must be 40%+ suspicious
```

### Emotional State Requirements
```python
required_emotional_states: {
    "Tom": ["vulnerable", "stressed", "anxious"]
}
```

### Location/Time Requirements
```python
required_location: "kitchen"
required_time_period: "evening"
```

### Alliance Requirements
```python
alliance_strength_threshold: 60  # Need 60%+ alliance
```

## Event Options & Choices

Every event presents multiple choices:

### Option Structure
```python
EventOption(
    option_id="unique_id",
    text="What you choose to do",

    # Requirements
    requires_rapport=10,      # Need 10+ rapport
    requires_sp=5,            # Need 5+ SP

    # Costs
    sp_cost=3,                # Pay 3 SP
    money_cost=50,            # Pay $50
    time_cost=30,             # Takes 30 minutes

    # Direct Effects
    rapport_changes={"Ruth": 2, "Tom": -1},
    emotional_state_changes={"Ruth": "grateful"},
    suspicion_changes={"Dawn": -10},
    sp_gain=2,
    money_gain=100,

    # PHS Opportunities
    allows_phs=True,
    phs_target="Ruth",
    phs_success_bonus=25,     # +25% success chance
    phs_detection_risk=40,    # 40% chance of being caught

    # Social Effects
    social_effect="Dawn sees you being kind",
    observers=["Dawn", "Tom"],  # Who watches

    # Success Chance
    success_chance=70,        # 70% chance to succeed
    success_text="It works!",
    failure_text="It backfires..."
)
```

### Option Types

**1. Safe Choices**
- Build rapport honestly
- Help without manipulation
- Low risk, moderate reward

**2. Manipulative Choices**
- Plant PHS during event
- Exploit vulnerability
- High risk, high reward
- Detection possible!

**3. Defensive Choices**
- Apologize and de-escalate
- Deflect suspicion
- Protect your position

**4. Aggressive Choices**
- Confront directly
- Take risks
- Possible backfire

## Integration with Relationship Web

Events trigger social dynamics:

### Observers React
```
You choose an option with observers
  ↓
Observers use relationship web observation system
  ↓
They notice if character acts differently
  ↓
Gossip may spread based on what they saw
  ↓
Suspicion or rapport changes ripple
```

### Example Cascade
```
EVENT: Tom asks for help (Crisis)
YOU: Plant PHS while helping
OBSERVER: Ruth is watching (relationship with Tom: 12)
  ↓
Ruth observes Tom acting receptive to you
  ↓
Ruth's suspicion increases: +10
  ↓
Ruth tells Dawn (relationship: 11)
  ↓
Dawn's suspicion increases: +6
  ↓
Two people now suspicious!
```

## Event Cooldowns & Limits

### Cooldown System
```python
cooldown_hours=24  # Can't trigger again for 24 hours
```

After an event triggers, it goes on cooldown to prevent spam.

### One-Time Events
```python
one_time=True  # Can only happen once in playthrough
```

Special story events that mark progression milestones.

### Opportunity Expiration
```python
window_expires_in=10  # Expires in 10 minutes
```

Active opportunities expire! The system checks on each time advancement.

## API Endpoints

### 1. Respond to Event
```http
POST /api/events/respond
Content-Type: application/json

{
  "event_id": "initiated_tom_work_crisis",
  "option_id": "listen_empathetically"
}

Response:
{
  "success": true,
  "outcome": "Tom opens up completely. 'Thanks... I really needed this.'",
  "messages": [
    "Rapport with Tom: 8 → 11",
    "Tom is now relieved (was stressed)"
  ],
  "option_success": true,
  "allows_phs": false
}
```

### 2. Get Active Event
```http
GET /api/events/active

Response:
{
  "success": true,
  "active_event": {
    "event": {
      "event_id": "opportunity_dawn_alone",
      "title": "Dawn Alone in Kitchen",
      "description": "Dawn is alone in the kitchen for the next 10 minutes...",
      "options": [...]
    },
    "time_remaining": 7,
    "type": "opportunity"
  }
}
```

### 3. Check Event Probabilities
```http
GET /api/events/probabilities

Response:
{
  "success": true,
  "probabilities": {
    "encounter": 20,
    "initiated": 30,  # High due to strong rapport
    "opportunity": 10,
    "crisis": 25,      # High due to suspicion
    "visitor": 18,
    "memory_trigger": 21  # High due to active PHS
  }
}
```

## Event Flow in Game

### Time Advancement Trigger
```
Player advances time by 15+ minutes
  ↓
System rolls for event (25% chance)
  ↓
IF event triggers:
  Calculate probabilities based on game state
  Select event type (weighted random)
  Find available events of that type
  Check event conditions
  Select one event (weighted by event.weight)
  Trigger event
  ↓
Event appears in UI
  ↓
Player chooses option
  ↓
Effects applied
  Rapport changes
  Emotional states change
  Suspicion changes
  SP/money changes
  Time advances
  Social dynamics triggered
  ↓
If option allows PHS:
  Player can plant suggestion with bonuses
  ↓
Opportunity windows expire if time limit reached
```

## Strategic Guide

### Maximizing Event Benefits

**1. Monitor Probabilities**
- Check `/api/events/probabilities` to see what's likely
- High character-initiated probability? Build rapport now!
- High crisis probability? Prepare defensive options

**2. Prepare for Opportunities**
- Keep SP reserve for sudden opportunities
- Note which characters are vulnerable
- Be ready to drop everything for time-limited windows

**3. Crisis Management**
- Crises are HIGH RISK
- Everyone is watching
- PHS during crisis = big reward but huge detection risk
- Consider safe options unless desperate

**4. Character-Initiated Events**
- BUILD RAPPORT to unlock these
- These are GOLD for PHS (they're receptive)
- Use empathy first, manipulation second

**5. Visitor Events**
- DEFENSIVE MODE
- They're confronting you
- Reduce suspicion or risk game over
- Sometimes retreat is best

**6. Memory Triggers**
- Can expose manipulation
- Use defensively (reduce suspicion)
- Or offensively (reinforce PHS during confusion)

### Risk Management

**Low Risk Options:**
```
✓ Genuine empathy
✓ Helping without manipulation
✓ Observing and learning
✓ Safe relationship building
```

**High Risk Options:**
```
⚠️ PHS with observers present
⚠️ Exploiting vulnerabilities
⚠️ Aggressive confrontation
⚠️ Lying when suspicious
```

### Opportunity Windows Strategy

**When you see a window:**
1. **Evaluate time remaining** - Do you have enough?
2. **Check detection risk** - Are observers present?
3. **Consider rewards** - Is the bonus worth it?
4. **Act fast** - Windows expire!

**Examples:**
```
"Dawn alone - 10 minutes left"
→ High value target, rare opportunity
→ USE IT!

"Vanessa vulnerable - 15 minutes left"
→ You have active alliance against you
→ TOO RISKY, skip it

"Tom stressed - 5 minutes left"
→ Not enough time if conversation interrupted
→ Maybe skip
```

## Event Design Philosophy

Events are designed to:

1. **Break Player Control** - You can't always choose when things happen
2. **Create Stories** - "Remember when Derek got hurt and I..."
3. **Add Urgency** - Opportunity windows force decisions
4. **Integrate Systems** - Events use relationship web, PHS, time, location
5. **Reward Preparation** - Having good rapport opens opportunities
6. **Punish Overreach** - Too much manipulation creates crises

## Event Examples in Action

### Example 1: The Coffee Spill
```
[TIME ADVANCES 30 MINUTES]
EVENT TRIGGERS: Random Encounter (20% chance)
TYPE SELECTED: Encounter
EVENT: Coffee Spill with Ruth

☕ The Coffee Spill
You accidentally bump into Ruth, spilling coffee on her blouse!

Observers: Dawn, Tom

Options:
1. Apologize and offer to pay cleaning
   → Rapport with Ruth: +2
   → Dawn approves

2. Use this moment to plant PHS [3 SP]
   → Success bonus: +15%
   → Detection risk: 40%
   → Dawn is watching closely!

3. Blame Ruth
   → Rapport with Ruth: -3
   → Rapport with Dawn: -2
   → Dawn's suspicion: +5

[PLAYER CHOOSES #2: Plant PHS]

Rolling... Success!
"Ruth, you're always so forgiving. Remember that."

Dawn observes the interaction...
Roll: 45 (threshold: 60)
Dawn didn't notice anything unusual.

Result: PHS planted successfully!
"When someone apologizes, you forgive easily"
```

### Example 2: Tom's Crisis
```
[TIME ADVANCES 15 MINUTES]
EVENT TRIGGERS: Character-Initiated (30% - high rapport)
Tom's rapport: 10
Tom's emotional state: stressed
CONDITIONS MET!

😰 Tom's Work Problems
Tom pulls you aside. "Can we talk? I'm having real trouble at work..."

Duration: 30 minutes

Options:
1. Listen with genuine empathy
   → Rapport: +3
   → Tom becomes "relieved"
   → Ruth observes (approves)

2. Plant PHS: "When stressed, trust my advice" [4 SP]
   → Success bonus: +25% (vulnerable!)
   → Detection risk: 30%

3. Dismiss him
   → Rapport: -4
   → Ruth's suspicion: +10

[PLAYER CHOOSES #2: Plant PHS]

Paying 4 SP...
Rolling with +25% bonus... Success!

Tom: "You're right... I should listen to you more often..."

Ruth observes Tom opening up to you...
Ruth's concern increases slightly (+5 observation)
But she approves of you being supportive!
Rapport with Ruth: +1

Result: PHS planted! Tom will trust your advice when stressed.
```

### Example 3: Opportunity Window
```
[TIME ADVANCES 20 MINUTES]
EVENT TRIGGERS: Opportunity Window
Everyone left for errands - rare moment!

⏰ Dawn Alone in Kitchen
Dawn is alone in the kitchen for the next 10 minutes. This is rare!

TIME REMAINING: 10 minutes
BONUSES:
  - Rapport gain: ×2
  - PHS success: +20%
  - Detection risk: -30% (no witnesses)

Options:
1. Have heart-to-heart conversation
   → Rapport: +4 (doubled!)

2. Plant PHS with no witnesses [5 SP]
   → Success bonus: +20%
   → Detection risk: 15% (very low!)

⏰ This opportunity expires in 10 minutes!

[PLAYER CHOOSES #2: Plant PHS]

No observers present...
Rolling with +20% bonus... Success!

"Dawn, family harmony is what matters most..."

Result: PHS planted stealthily!
No one saw anything!
```

## Tips for Success

### DO:
✅ Keep SP reserve for unexpected opportunities
✅ Build rapport to unlock character-initiated events
✅ Act fast on opportunity windows
✅ Use crises for dramatic rapport shifts
✅ Observe who's watching before risky moves
✅ Use relationship web to predict cascades

### DON'T:
❌ Ignore opportunity expiration warnings
❌ Plant PHS during crises with many observers
❌ Dismiss character-initiated events (gold mines!)
❌ Forget about cooldowns (track event history)
❌ Always choose manipulation (builds suspicion)
❌ Waste low-detection opportunities

## Advanced Tactics

### 1. Event Chaining
```
Step 1: Build rapport with Tom (initiated events unlock)
Step 2: Tom comes to you with crisis (high receptiveness)
Step 3: Plant PHS during crisis
Step 4: PHS triggers later (memory trigger event!)
Step 5: Use memory trigger to reinforce
```

### 2. Observer Management
```
Check who's watching before choosing option
If Dawn observing + high suspicion: Choose safe option
If no observers: Take risky PHS opportunity
If only allies observing: Medium risk acceptable
```

### 3. Opportunity Hoarding
```
Save SP for opportunities (they're time-limited!)
Don't blow SP on regular conversations
When opportunity appears: GO ALL IN
```

### 4. Crisis Exploitation
```
Crises = everyone watching
But also = emotional vulnerability
IF you have defensive PHS planted:
  → Safer to manipulate during crisis
ELSE:
  → Play it safe, build rapport
```

---

**Events make your game come ALIVE!** Every playthrough will be different based on when events trigger and how you respond. The combination of events + relationship web + PHS creates infinite emergent stories! 🎲

## Summary

Dynamic Random Events add:
- **Unpredictability** - You can't control everything
- **Urgency** - Time-limited decisions
- **Stories** - Memorable moments
- **Depth** - Multiple layers of consequence
- **Replayability** - Different events each playthrough

The game evolves from "manipulate characters when you want" to "navigate a living, reactive family system that acts on YOU!"
