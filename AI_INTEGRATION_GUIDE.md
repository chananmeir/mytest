# Advanced AI Integration Guide 🤖

## Overview

The Advanced AI Integration system transforms characters from static NPCs into living, breathing personalities that evolve, learn, and act autonomously based on their psychological state and experiences.

**Core Features:**
1. **Dynamic Dialogue** - AI-generated responses that adapt to personality state
2. **Personality Simulation** - Characters remember, evolve, and develop patterns
3. **Emergent Behavior** - Autonomous actions triggered by psychological state

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Personality States](#personality-states)
3. [Dynamic Dialogue](#dynamic-dialogue)
4. [Emergent Behavior](#emergent-behavior)
5. [API Reference](#api-reference)
6. [Integration](#integration)
7. [Examples](#examples)

---

## System Architecture

### Components

```
┌─────────────────────────────────────────┐
│     AI Personality System               │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────────────────────────┐    │
│  │  Personality Simulator         │    │
│  │  - Tracks evolving states      │    │
│  │  - Manages behavioral patterns │    │
│  │  - Predicts reactions          │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  Dynamic Context Generator     │    │
│  │  - Builds LLM prompts          │    │
│  │  - Integrates personality data │    │
│  │  - Adds real-time modifiers    │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  Emergent Behavior Engine      │    │
│  │  - Generates autonomous actions │    │
│  │  - Selects based on likelihood  │    │
│  │  - Executes and applies effects │    │
│  └────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
          ↓
    ┌─────────┐
    │   LLM   │ (Character Responses)
    └─────────┘
```

### Integration Points

1. **Conversation System** (`app.py:406`)
   - Adds dynamic personality context to LLM prompts
   - Updates personality state after conversations
   - Tracks events that shape personality

2. **Time Advancement** (`app.py:1372`)
   - Triggers emergent behaviors
   - Allows characters to act autonomously
   - Applies natural personality drift

3. **Event Processing**
   - Rapport changes update trust/vulnerability
   - PHS planting affects awareness/independence
   - Gossip modifies suspicion tendencies

---

## Personality States

### PersonalityState Class

Every character has a dynamic personality state that evolves over time:

```python
@dataclass
class PersonalityState:
    character_name: str

    # Dynamic Traits (constantly evolving)
    current_mood: str = "neutral"
    stress_level: int = 50  # 0-100
    trust_in_player: int = 50  # 0-100
    independence_level: int = 50  # 0-100

    # Awareness & Vulnerability
    player_influence_awareness: int = 0  # 0-100 (unconscious detection)
    emotional_vulnerability: int = 50  # 0-100
    resistance_to_change: int = 50  # 0-100

    # Mental State
    active_concerns: List[str]  # What's on their mind
    current_goals: List[str]  # What they want
    recent_observations: List[str]  # What they've noticed

    # Relationships
    alliance_preferences: Dict[str, int]  # Who they prefer
    conflict_targets: List[str]  # Who they're at odds with

    # Behavioral Tendencies
    assertiveness: int = 50
    openness_to_player: int = 50
    suspicion_tendency: int = 50
```

### State Evolution

**Personality states evolve through:**

1. **Event Processing**
   - Rapport changes → Trust/stress shifts
   - PHS planting → Awareness/vulnerability changes
   - Detection → Major trust loss

2. **Natural Drift**
   - Stress naturally decreases (coping)
   - Suspicion fades without incidents
   - Trust slowly rebuilds
   - Vulnerability fluctuates with mood

3. **Derived Updates**
   - High stress → Increased resistance
   - Low trust → Higher suspicion
   - High awareness → Better resistance

### Stress Level Effects

| Stress Level | Effects |
|--------------|---------|
| 0-30 | Relaxed - More open, easier to talk to, vulnerable to PHS |
| 31-70 | Moderate - Normal behavior |
| 71-100 | High Stress - Short temper, less patient, resistant |

**Stress Modifiers:**
- Anxious personality: +20 base
- Confident personality: -15 base
- High-pressure job: +10 base
- Positive interactions: -2 per rapport gain
- Negative interactions: +3 per rapport loss

### Trust vs Rapport

**Rapport** = Surface-level relationship metric (gameplay stat)
**Trust** = Deep psychological belief in player (personality sim)

- Trust initializes based on rapport
- Trust changes slower than rapport
- Trust affects vulnerability more than rapport
- Low trust + high rapport = Cognitive dissonance → Suspicion

### Independence Level

| Independence | Behavior |
|--------------|----------|
| 0-30 | Submissive - Easily influenced, follows suggestions |
| 31-70 | Balanced - Normal resistance |
| 71-100 | Highly Independent - Resists manipulation strongly |

**Independence affected by:**
- PHS planting: -3 per PHS (unconscious loss of agency)
- Character traits: Assertive +20, Submissive -20
- Successfully resisting PHS: +5

### Player Influence Awareness

**Unconscious detection of manipulation:**

| Awareness | State |
|-----------|-------|
| 0-30 | Oblivious - No suspicion |
| 31-60 | Uneasy - "Something feels off" |
| 61-80 | Suspicious - Watching for manipulation |
| 81-100 | Certain - Knows they're being manipulated |

**Awareness increases from:**
- Each PHS planted: +2 (unconscious recognition)
- PHS detected: +30 (conscious recognition)
- Gossip about player: +5
- Out-of-character behavior witnessed: +10

**High awareness effects:**
- Dramatically reduces PHS success rate
- Increases resistance to change
- Triggers emergent confrontation behaviors
- May form alliances against player

---

## Dynamic Dialogue

### How It Works

When a character responds to the player:

1. **Base Character Context** (from `llm_handler.py`)
   - Personality traits
   - Emotional state
   - Rapport level
   - Active PHS
   - Conversation history
   - Memories

2. **+ Dynamic Personality Context** (from `ai_personality.py`)
   - Current mood
   - Stress level
   - Trust in player
   - Emotional vulnerability
   - Active concerns
   - Current goals
   - Recent observations
   - Alliance preferences
   - Behavioral tendencies

3. **= Highly Contextualized Response**
   - Feels authentic to current state
   - References recent events
   - Shows personality evolution
   - Displays appropriate wariness/openness

### Dynamic Context Example

```
=== DYNAMIC PERSONALITY STATE ===
CURRENT MENTAL STATE:
- Mood: ANXIOUS
- Stress Level: 75/100 (HIGH STRESS - shorter temper, less patient)

TRUST & VULNERABILITY:
- Trust in Player: 40/100
- Emotional Vulnerability: 65/100
- Manipulation Awareness: 45/100 (You have an unconscious feeling something is off)

CURRENT CONCERNS ON YOUR MIND:
- Player seems to be influencing family members
- Ruth has been acting strange lately

WHAT YOU WANT RIGHT NOW:
- Maintain Family Harmony
- Understand What's Happening

RECENT OBSERVATIONS:
- Player spends a lot of time alone with family members
- People's opinions seem to change after talking to player

You feel particularly close to Tom right now.

CURRENT BEHAVIORAL TENDENCIES:
- Assertiveness: 35/100
- Openness to Player: 30/100
- Independence: 60/100

Adjust your responses based on these dynamic states!
```

### Response Evolution Example

**Same question, different states:**

Player: "Can we talk about something private?"

**State 1: High Trust, Low Stress**
```
Dawn: "Of course, dear. Come, let's sit down. You know you can tell me anything."
```

**State 2: Low Trust, High Stress**
```
Dawn: "I'm rather busy at the moment. Perhaps later? ...What is this about, exactly?"
```

**State 3: High Manipulation Awareness**
```
Dawn: "Another private conversation? You seem to have a lot of those lately. Why don't we talk here, where everyone can see?"
```

---

## Emergent Behavior

### What is Emergent Behavior?

Characters **proactively take actions** based on their psychological state, without player prompting.

**Examples:**
- Character seeks you out to talk about stress
- Character forms alliance with another character
- Character confronts you about manipulation
- Character suggests doing something together
- Character shares observations about the family

### Action Types

#### 1. Concern Expression
**Triggers:** High stress + trusts player
**Likelihood:** 70%

```python
{
    'action_type': 'concern_expression',
    'description': 'Ruth seeks you out to talk about her stress',
    'outcomes': [
        'Opportunity to provide emotional support',
        'Could plant PHS during vulnerable moment',
        'Builds rapport if handled well'
    ]
}
```

#### 2. Alliance Formation
**Triggers:** High suspicion + close relationship with another character
**Likelihood:** Based on awareness level

```python
{
    'action_type': 'alliance_formation',
    'description': 'Dawn privately talks to Tom about concerns regarding you',
    'target_character': 'Tom',
    'outcomes': [
        'Alliance forms against player',
        'Increases coordinated resistance',
        'May lead to intervention'
    ]
}
```

#### 3. Conversation Initiation
**Triggers:** Active goals + high trust
**Likelihood:** 65%

```python
{
    'action_type': 'conversation_initiation',
    'description': 'Melanie wants to discuss her career goals with you',
    'outcomes': [
        'Learn about deeper motivations',
        'Opportunity for subtle influence',
        'Strengthens bond'
    ]
}
```

#### 4. Confrontation
**Triggers:** Very high manipulation awareness (>80)
**Likelihood:** 90%

```python
{
    'action_type': 'confrontation',
    'description': 'Vanessa confronts you about feeling manipulated',
    'outcomes': [
        'Major crisis - must handle carefully',
        'Could lead to game over',
        'Chance to gaslight or come clean'
    ]
}
```

#### 5. Activity Suggestion
**Triggers:** High stress + good rapport
**Likelihood:** 55%

```python
{
    'action_type': 'activity_suggestion',
    'description': 'Derek suggests working out together to relax',
    'outcomes': [
        'Shared activity opportunity',
        'Natural rapport building',
        'PHS opportunity in relaxed setting'
    ]
}
```

#### 6. Emotional Support Seeking
**Triggers:** High vulnerability + high trust
**Likelihood:** 80%

```python
{
    'action_type': 'emotional_support_seeking',
    'description': 'Tom comes to you feeling vulnerable',
    'outcomes': [
        'Prime PHS opportunity (+25% success)',
        'Major rapport gain if supportive',
        'Deepens emotional bond'
    ]
}
```

#### 7. Observation Sharing
**Triggers:** Recent observations + openness to player
**Likelihood:** 50%

```python
{
    'action_type': 'observation_sharing',
    'description': 'Ruth shares what she\'s noticed about the family',
    'outcomes': [
        'Learn about family dynamics',
        'Understand relationship web better',
        'May reveal suspicions'
    ]
}
```

### Selection Algorithm

When multiple emergent actions are possible:

1. Calculate total likelihood sum
2. Generate random value
3. Select action weighted by likelihood
4. Execute action
5. Apply game effects

**Higher likelihood = More likely to trigger**

### Execution Flow

```
Time advances
    ↓
Check all characters
    ↓
Generate possible emergent actions
    ↓
Select one based on likelihood
    ↓
Execute action
    ↓
Display narrative
    ↓
Apply game effects
    ↓
Update personality state
```

### Frequency Control

Each character has `autonomous_action_frequency` (default: 24 hours).

- Prevents spam of emergent behaviors
- Makes actions feel significant
- Allows time for player response

---

## API Reference

### Get Personality State

```http
GET /api/ai/personality/<character_name>
```

**Response:**
```json
{
  "success": true,
  "character": "Ruth",
  "personality_state": {
    "current_mood": "anxious",
    "stress_level": 75,
    "trust_in_player": 40,
    "independence_level": 45,
    "player_influence_awareness": 45,
    "emotional_vulnerability": 65,
    "resistance_to_change": 60,
    "active_concerns": [
      "Player seems to be influencing family members",
      "Ruth has been acting strange"
    ],
    "current_goals": [
      "maintain_family_harmony",
      "understand_whats_happening"
    ],
    "recent_observations": [
      "Player spends a lot of time alone with family members"
    ],
    "alliance_preferences": {
      "Tom": 75
    },
    "conflict_targets": [],
    "assertiveness": 35,
    "openness_to_player": 30,
    "suspicion_tendency": 55
  }
}
```

### Predict Reaction

```http
POST /api/ai/predict-reaction
Content-Type: application/json

{
  "character": "Ruth",
  "action_type": "hypnosis_attempt"
}
```

**Action Types:**
- `hypnosis_attempt`
- `emotional_support`
- `request_favor`
- `share_secret`
- `ask_personal_question`

**Response:**
```json
{
  "success": true,
  "character": "Ruth",
  "action_type": "hypnosis_attempt",
  "prediction": {
    "success_probability": 45,
    "base_favorability": 60,
    "modifiers": {
      "stress": -20,
      "trust": 0,
      "vulnerability": 15,
      "awareness": 0
    },
    "recommendation": "Moderate chance - consider reducing their stress first"
  }
}
```

### Get Emergent Actions

```http
GET /api/ai/emergent-actions/<character_name>
```

**Response:**
```json
{
  "success": true,
  "character": "Ruth",
  "possible_actions": [
    {
      "action_id": "express_stress_Ruth",
      "action_type": "concern_expression",
      "description": "Ruth seeks you out to talk about her stress",
      "target_character": null,
      "trigger_reason": "High stress + trusts player",
      "potential_outcomes": [
        "Opportunity to provide emotional support",
        "Could plant PHS during vulnerable moment"
      ],
      "likelihood": 70
    }
  ]
}
```

### Get All Personalities

```http
GET /api/ai/all-personalities
```

**Response:**
```json
{
  "success": true,
  "personalities": {
    "Ruth": {
      "current_mood": "anxious",
      "stress_level": 75,
      "trust_in_player": 40,
      "emotional_vulnerability": 65,
      "player_influence_awareness": 45,
      "active_concerns": ["Player seems to be influencing family"],
      "current_goals": ["maintain_family_harmony"]
    },
    "Tom": { ... },
    "Dawn": { ... }
  }
}
```

---

## Integration

### Conversation Integration

In `app.py`, conversations automatically use AI personality:

```python
# Dynamic personality context is added to LLM prompt
response = llm_handler.get_character_response(
    char,
    player_message,
    scene_context=scene_context,
    location_context=location_context,
    record_memory=True,
    game_state=game_state  # Enables AI personality
)

# Personality state updates after conversation
from systems.ai_personality import update_character_personality

conversation_events = [
    {'type': 'rapport_change', 'amount': analysis['rapport_change']},
    {'type': 'phs_planted', 'phs': phs}
]

personality_changes = update_character_personality(
    char, game_state, conversation_events
)
```

### Time Advancement Integration

Emergent behaviors trigger automatically during time advancement:

```python
from systems.ai_personality import trigger_emergent_behavior

emergent_behavior = trigger_emergent_behavior(game_state)

if emergent_behavior:
    # Display narrative
    message = emergent_behavior['narrative']

    # Apply effects
    for effect in emergent_behavior['game_effects']:
        # Handle alliance formation, crises, etc.
```

---

## Examples

### Example 1: Trust Evolution

**Initial State:**
- Ruth starts with rapport 7
- Trust initializes at 35 (7 * 5)

**After positive conversation:**
- Rapport increases to 9
- Trust increases to 45 (slower than rapport)
- Emotional vulnerability increases (feels safe)

**After PHS planting (undetected):**
- Rapport stays at 9
- Trust stays at 45 (doesn't know)
- But player_influence_awareness increases to 7 (unconscious)
- Independence decreases to 47

**After 5 PHS plantings:**
- Rapport 11 (still building)
- Trust 55 (still trusting)
- Awareness 17 (starting to feel uneasy)
- Independence 38 (losing agency)
- Vulnerability 75 (very susceptible)

**After PHS detection:**
- Rapport drops to 6 (conscious anger)
- Trust crashes to 15 (betrayed)
- Awareness jumps to 47 (confirmed suspicion)
- Resistance increases to 80 (defensive)
- Likely triggers confrontation behavior

### Example 2: Emergent Confrontation

**Setup:**
- Vanessa has been manipulated 8 times
- Player_influence_awareness = 85
- Trust_in_player = 20
- Stress_level = 80

**Time advances...**

**Emergent behavior engine evaluates:**
```python
if state.player_influence_awareness > 80:
    action = EmergentAction(
        action_type="confrontation",
        likelihood=90  # Very high!
    )
```

**Action selected and executed:**
```
🎭 Vanessa's expression is serious. "We need to talk. Something's been
bothering me about... us. About how I've been acting around you."
```

**Player must respond carefully or face game over!**

### Example 3: Stress-Driven Support Seeking

**Setup:**
- Tom's stress_level = 85 (work problems)
- Trust_in_player = 70 (good rapport)
- Emotional_vulnerability = 80 (needs help)

**Emergent action generated:**
```python
action = EmergentAction(
    action_type="emotional_support_seeking",
    description="Tom comes to you feeling vulnerable",
    likelihood=80
)
```

**Executed:**
```
🎭 Tom seems vulnerable. "Can we talk? I'm... not doing great right now."
```

**Outcomes:**
- **Supportive response:** +3 rapport, trust increases, stress decreases
- **PHS attempt:** +25% success bonus (high vulnerability), but risks detection
- **Dismissive:** -2 rapport, stress increases, trust decreases

---

## Technical Details

### Personality State Storage

States are stored in memory during gameplay:

```python
class PersonalitySimulator:
    def __init__(self):
        self.personality_states: Dict[str, PersonalityState] = {}
```

**Not saved to disk** - Regenerates each session based on:
- Character base traits
- Current game state
- Historical events

### Performance Considerations

- Personality updates only on significant events
- Emergent behavior checks only during time advancement
- Dynamic context generation is fast (string building)
- No database queries - all in-memory

### LLM Integration

Dynamic personality context adds ~500-1000 tokens to prompts:
- Provides rich context for authentic responses
- Makes characters feel alive and reactive
- Worth the token cost for immersion

---

## Best Practices

### For Players

1. **Monitor Awareness Levels**
   - Use `/api/ai/personality/<name>` to check manipulation awareness
   - High awareness = Time to back off

2. **Consider Stress Before PHS**
   - High stress characters resist more
   - Reduce stress through support first

3. **Build Trust, Not Just Rapport**
   - Trust takes longer but matters more for PHS
   - Inconsistent behavior damages trust

4. **Watch for Emergent Behaviors**
   - Characters will initiate important conversations
   - Don't ignore warning signs (confrontations)

### For Developers

1. **Balance Awareness Gains**
   - Too fast = Player can't succeed
   - Too slow = No consequences

2. **Tune Emergent Frequencies**
   - Too often = Feels scripted
   - Too rare = System goes unnoticed

3. **Test Edge Cases**
   - All characters at high awareness
   - Multiple alliances forming
   - Rapid manipulation detection

---

## Future Enhancements

Potential additions:

1. **Persistent Personality Memory**
   - Save states to disk
   - Track long-term evolution

2. **Group Dynamics Simulation**
   - Family-wide mood tracking
   - Collective stress responses

3. **Therapy/Counseling Mechanics**
   - Reduce awareness through genuine help
   - Rebuild trust authentically

4. **Personality Disorders**
   - Characters develop issues from manipulation
   - Requires genuine care to heal

5. **Meta-Awareness**
   - Characters realize they're in a game (4th wall)
   - Existential crisis mechanics

---

## Summary

The AI Personality System transforms the game from:

**Before:**
- Characters respond based on static rapport
- Predictable behavior patterns
- No consequence memory
- Player-driven interactions only

**After:**
- Characters evolve psychologically
- Authentic, state-driven responses
- Long-term manipulation consequences
- Characters act autonomously
- Emergent narrative possibilities

**From "hypnosis mechanics" to "psychological simulation"!** 🧠✨
