# Procedural Generation Guide

This guide covers the procedural generation system that adds replayability through randomized character traits, variable family dynamics, and expanded random events.

## Table of Contents
1. [Overview](#overview)
2. [Randomized Character Traits](#randomized-character-traits)
3. [Variable Family Dynamics](#variable-family-dynamics)
4. [Procedural Events](#procedural-events)
5. [Usage Guide](#usage-guide)
6. [Advanced Features](#advanced-features)

---

## Overview

The Procedural Generation System creates unique playthroughs by varying three key elements:

1. **Character Traits** - Resistance and personality variations
2. **Family Dynamics** - Starting relationships between NPCs
3. **Random Events** - Dynamic medical emergencies, financial crises, surprise visitors, and scandals

**Benefits:**
- **Replayability**: Each playthrough feels fresh
- **Strategic Variety**: Different character builds require different approaches
- **Emergent Stories**: Unique narrative possibilities
- **Replay Value**: Discover new interactions and outcomes

---

## Randomized Character Traits

### How It Works

Each character has defined variation ranges for resistance and personality:

**Ruth Example:**
```python
Resistance: 50-65% (base: 55%)
Personalities:
- "Guilt-driven, loyal, tries to please everyone" (original)
- "Guilt-driven, loyal, but sometimes stands up for herself"
- "Anxious, loyal, desperately needs approval"
- "Guilt-driven, loyal, quietly resentful underneath"
```

### Character Variation Ranges

| Character | Resistance Range | Personality Variants |
|-----------|-----------------|---------------------|
| Ruth | 50-65% | 4 variants (guilt/anxiety focused) |
| Melanie | 70-82% | 4 variants (pride/insecurity focused) |
| Tom | 25-38% | 4 variants (conflict-avoidance focused) |
| Dawn | 40-52% | 4 variants (control/harmony focused) |
| Vanessa | 45-58% | 4 variants (status/validation focused) |
| Derek | 60-72% | 4 variants (ego/insecurity focused) |
| Karen | 30-42% | 4 variants (rigidity/anxiety focused) |

### Impact on Gameplay

**Low Resistance Run (Tom at 25%):**
- Very easy to plant suggestions
- Max PHS capacity (3 slots)
- But: Low resistance might indicate instability

**High Resistance Run (Melanie at 82%):**
- Extremely difficult to influence
- Min PHS capacity (1 slot)
- But: More satisfying when you break through

**Personality Variations:**
Each variant changes dialogue style, emotional responses, and relationship dynamics:

```
Ruth (Original): "I'm so sorry, I hope that's okay..."
Ruth (Stands Up): "I appreciate that, but I need to be honest..."
Ruth (Needs Approval): "Did I do something wrong? Please tell me..."
Ruth (Resentful): "Fine. Whatever you need." (underlying tension)
```

---

## Variable Family Dynamics

### Relationship Randomization

Starting relationships between characters vary each playthrough:

**Example: Ruth & Melanie Relationship**
- **Range:** 4-10 (out of 20)
- **Low (4):** Distant sisters, barely talk
- **Medium (7):** Civil but not close
- **High (10):** Close sisters who confide

### Relationship Ranges by Pair

**Close Bonds (Range: 10-17):**
- Ruth & Tom: 10-15 (married couple)
- Dawn & Karen: 12-17 (best friends)
- Melanie & Karen: 8-14 (professional respect)

**Variable Bonds (Range: 4-11):**
- Ruth & Melanie: 4-10 (sisters - varies widely)
- Tom & Derek: 5-11 (different but bros)
- Vanessa & Melanie: 2-8 (sisters - competitive)

**Typically Distant (Range: 2-8):**
- Melanie & Derek: 2-8 (can be competitive or friendly)
- Vanessa & Karen: 2-6 (clashing personalities)
- Derek & Karen: 3-7 (little overlap)

### Strategic Implications

**High Ruth-Melanie Relationship (10):**
- They defend each other
- Trust each other's judgment
- Harder to play them against each other
- But: Can use one to influence the other

**Low Ruth-Melanie Relationship (4):**
- They don't trust each other
- Easy to play them against each other
- But: Can't use sisterly bonds as leverage

**Family Alliances:**
Different starting relationships create different alliance structures:
- Dawn-Karen alliance (always strong)
- Ruth-Tom couple (always close)
- Sister dynamics (highly variable)
- Cross-family connections (varies)

---

## Procedural Events

### Event Categories

The system generates 4 types of dynamic events:

#### 1. Medical Emergencies (2-3 per game)

**Types:**
- Critical heart/collapse event
- Severe allergic reaction
- Home accident/injury
- Sudden illness/fever

**Options:**
- Help immediately (+5 rapport with victim, +2 with observers, +3 SP)
- Call 911 (practical response, +2 rapport, +1 SP)
- **Exploit vulnerability** (4 SP, PHS with +25% success, 60% detection risk)
- Freeze up (lose rapport, people remember)

**Strategic Value:**
- High-rapport opportunity (crisis reveals character)
- PHS planting window (vulnerable state)
- But: High detection risk if you exploit

**Example:**
```
🚑 MEDICAL EMERGENCY: Ruth's Medical Emergency
Ruth suddenly clutches her chest and collapses! She needs help NOW!

Options:
1. Drop everything and help immediately
   → +5 rapport with Ruth, +2 with Dawn/Tom, +3 SP

2. Help her, but use this vulnerable moment... (costs 4 SP)
   → Plant PHS with +25% bonus
   → But 60% chance Dawn notices your opportunism!
```

#### 2. Financial Crises (2-3 per game)

**Types:**
- Job loss (need $500)
- Unexpected bill - car breakdown ($300)
- Rent crisis/eviction risk ($800)
- Medical bills ($1000)

**Options:**
- Lend money (costs money, +6 rapport, +2 SP, builds trust)
- Emotional support only (+3 rapport, +1 SP)
- **Exploit desperation** (3 SP, PHS with +30% success, 50% detection)
- Dismiss their problems (lose rapport)

**Strategic Value:**
- Build deep loyalty through generosity
- Or exploit desperate state for influence
- Money management becomes important

**Example:**
```
💸 FINANCIAL CRISIS: Tom's Job Loss
Tom just got laid off. He's devastated and panicking about money.

Options:
1. Lend him $500
   → He'll never forget your generosity (+6 rapport)

2. "They're desperate... use this" (costs 3 SP)
   → Plant PHS with +30% bonus while they're vulnerable
   → 50% chance they realize you're exploiting them
```

#### 3. Surprise Visitors (1-2 per game)

**Types:**
- Someone's ex-partner
- Debt collector
- Old friend from high school
- Estranged relative

**Options:**
- Be welcoming (+3 rapport if character's visitor)
- Be protective (+5 rapport, shows loyalty)
- **Gather information** (+3 SP, learn family dynamics)
- Create chaos (lose rapport but fun)

**Strategic Value:**
- Learn hidden family information
- Show loyalty to gain trust
- Observe authentic reactions

**Example:**
```
🚪 SURPRISE VISITOR: An Ex-Partner
Melanie's ex shows up unexpectedly, causing tension.

Options:
1. Be welcoming and diplomatic
   → Family notices your tact (+1 SP)

2. Be protective of Melanie
   → +5 rapport with Melanie, she feels defended

3. Observe and gather information
   → +3 SP, learn about Melanie's past
```

#### 4. Character Scandals (2-4 per game)

**Types:**
- Secret exposed
- Caught doing something wrong
- Damaging rumor spreads
- Old mistake resurfaces

**Options:**
- Publicly defend them (+7 rapport with character, -1 with others)
- Stay neutral (avoid drama)
- Investigate for truth (+3 SP, gain leverage)
- **Exploit their shame** (5 SP, PHS with +35% success, 70% detection!)
- Pile on (-8 rapport, show cruelty)

**Strategic Value:**
- Loyalty tests (defend or abandon)
- Maximum vulnerability for PHS (but highest risk)
- Leverage opportunities (blackmail potential)

**Example:**
```
😱 SCANDAL: Vanessa's Secret Exposed
Someone found out Vanessa has been lying about something significant...

Options:
1. Publicly defend her
   → +7 rapport with Vanessa, she's deeply grateful
   → -1 rapport with others (you're taking sides)

2. Investigate the truth
   → +3 SP, you gain leverage

3. Use her shame to plant deep suggestions (costs 5 SP)
   → PHS with +35% success (she's completely vulnerable)
   → But 70% chance someone catches you exploiting her!
```

### Event Generation

**Initial Pool:** When starting procedural game, generates:
- 2-3 medical emergencies
- 2-3 financial crises
- 1-2 surprise visitors
- 2-4 character scandals

**Total:** 8-12 unique procedural events per playthrough

**Trigger Timing:** Events trigger based on:
- Game time progression
- Character states (stressed, vulnerable, etc.)
- Player actions
- Random chance

---

## Usage Guide

### Starting a Procedural Game

**Option 1: Random Seed (Different Every Time)**
```python
# Start new procedural game with random variations
game_state = GameState(procedural_mode=True)

# Characters are randomized
# Relationships are randomized
# Events are generated
```

**Option 2: Specific Seed (Reproducible)**
```python
# Use specific seed for reproducible generation
game_state = GameState(procedural_mode=True, procedural_seed=12345)

# Same seed = same character variations
# Same seed = same relationship patterns
# Same seed = same event pool
```

**Option 3: Standard Game (No Procedural)**
```python
# Classic mode - characters as designed
game_state = GameState(procedural_mode=False)

# Fixed resistances
# Fixed relationships
# Standard events only
```

### Viewing Procedural Summary

When you start a procedural game, you see:

```
======================================================================
PROCEDURAL PLAYTHROUGH (Seed: 742891)
======================================================================

CHARACTER VARIATIONS:
----------------------------------------------------------------------

Ruth:
  Resistance: 58% (base: 55%, range: +3)
  Personality: Guilt-driven, loyal, but sometimes stands up for herself
  Key Relationships:
    - Tom: 13/20 (range: 10-14)
    - Melanie: 8/20 (range: 5-9)
    - Dawn: 11/20 (range: 9-13)

Melanie:
  Resistance: 76% (base: 75%, range: +1)
  Personality: Proud, competent, but secretly insecure
  Key Relationships:
    - Ruth: 8/20 (range: 5-9)
    - Derek: 5/20 (range: 3-7)
    - Karen: 11/20 (range: 9-13)

[... other characters ...]

======================================================================
💡 TIP: Every playthrough is different! Adapt your strategy.
======================================================================
```

### Saving & Loading

**Procedural games save:**
- Current seed
- Character variations
- Relationship matrix
- Generated events

**Loading restores:**
- Exact character states
- All relationships
- Event pool

**Backwards Compatibility:**
- Old saves load as standard (non-procedural)
- No migration needed

---

## Advanced Features

### Seed Sharing

Share seeds with other players for challenge runs:

```
"Beat the game with seed 123456!"
→ Everyone gets same character variations
→ Same relationship dynamics
→ Same event pool
→ Compare strategies
```

### Difficulty Variations

Different seeds create different difficulty profiles:

**Easy Seed Example (Seed: 111):**
- Most characters rolled low resistance
- Positive relationships across board
- Fewer crisis events

**Hard Seed Example (Seed: 666):**
- Most characters rolled high resistance
- Many conflicted relationships
- More crisis events

**Balanced Seed Example (Seed: 42):**
- Mix of high/low resistance
- Varied relationships
- Normal event distribution

### Procedural Event Expansion

The system is designed for easy expansion:

**Adding New Event Types:**
```python
# In ProceduralEventLibrary class

@staticmethod
def generate_YOUR_EVENT_TYPE(character_name: str):
    # Define event structure
    # Set options
    # Return DynamicEvent
    pass
```

**Event Categories to Add:**
- Weather emergencies
- Celebration events
- Legal troubles
- Workplace drama
- Romantic entanglements

### Strategy Tips by Mode

**Procedural Mode Strategy:**
1. **Adapt to variations** - Don't assume fixed resistances
2. **Scout relationships** - Check who's close to whom
3. **Event preparation** - Save SP for crisis opportunities
4. **Flexible planning** - Your usual approach may not work

**Standard Mode Strategy:**
1. **Optimize paths** - You know exact resistances
2. **Fixed routes** - Proven strategies work
3. **Consistency** - Same approach each time
4. **Mastery** - Perfect your technique

---

## Examples

### Example Playthrough 1: "The Easy Run" (Seed: 54321)

**Character Rolls:**
- Ruth: 51% resistance (LOW) - 3 PHS slots
- Melanie: 71% resistance (LOW for her) - 1 slot
- Tom: 26% resistance (VERY LOW) - 3 slots
- Derek: 61% resistance (LOW) - 2 slots

**Relationships:**
- Ruth-Melanie: 9/20 (close sisters!)
- Ruth-Tom: 14/20 (strong marriage)
- Dawn-Karen: 16/20 (very tight)

**Events Generated:**
- Ruth medical emergency (early opportunity)
- Tom financial crisis (easy rapport)
- Vanessa scandal (high leverage)

**Strategy:** Focus on Tom (easiest), then Ruth, use their relationship to reach Melanie.

---

### Example Playthrough 2: "The Challenge" (Seed: 13337)

**Character Rolls:**
- Ruth: 64% resistance (HIGH) - 1 PHS slot
- Melanie: 81% resistance (VERY HIGH) - 1 slot
- Tom: 37% resistance (HIGH for him) - 2 slots
- Derek: 71% resistance (HIGH) - 1 slot

**Relationships:**
- Ruth-Melanie: 5/20 (distant sisters)
- Ruth-Tom: 11/20 (strained marriage)
- Dawn-Karen: 14/20 (still close)

**Events Generated:**
- Melanie medical emergency (rare vulnerability)
- Derek financial crisis (pride vs. need)
- Multiple scandals (chaos mode)

**Strategy:** Wait for crisis events, exploit vulnerabilities, use conflicts between sisters.

---

### Example Playthrough 3: "The Social Web" (Seed: 99999)

**Character Rolls:**
- Mixed resistances (average difficulty)

**Relationships:**
- Everyone relatively connected (7-11 range)
- Few extremes
- Complex web of relationships

**Events Generated:**
- Multiple surprise visitors
- Few crises
- Relationship-focused events

**Strategy:** Social manipulation, use existing bonds, create alliances.

---

## Configuration

### Adjusting Variation Ranges

Edit `systems/procedural_generation.py`:

```python
# Make variations more extreme
CHARACTER_VARIATIONS = {
    'Ruth': CharacterVariation(
        resistance_min=40,  # Lower minimum
        resistance_max=70,  # Higher maximum
        # More variation = more extreme differences
    )
}
```

### Controlling Event Frequency

```python
# In ProceduralGameMode.initialize_procedural_game()

# More events
for _ in range(random.randint(4, 6)):  # Was (2, 3)
    initial_events.append(generate_medical_emergency_event(...))
```

### Adding Custom Personalities

```python
personality_variants=[
    'Original personality',
    'Variant 1',
    'Variant 2',
    'YOUR CUSTOM VARIANT HERE'
]
```

---

## Troubleshooting

### "Procedural mode too unpredictable"
→ Use specific seeds for more control
→ Reduce variation ranges
→ Stick to standard mode

### "Same characters every time"
→ Make sure procedural_mode=True
→ Don't reuse same seed
→ Check random state

### "Events not triggering"
→ Events have trigger conditions
→ Check character states
→ Advance game time

### "Too easy/too hard"
→ Reroll with different seed
→ Adjust variation ranges
→ Mix procedural with standard mode

---

## Future Enhancements

Potential expansions:

- **More Event Types**: Weather, celebrations, legal, workplace
- **Event Chains**: Events that trigger follow-ups
- **Dynamic Difficulty**: Adjust based on player performance
- **Procedural Locations**: Randomized house layouts
- **Trait Combinations**: Synergies between personality variants
- **Historical Events**: Past family drama that surfaces
- **Secret Variations**: Hidden character secrets randomized

---

## Credits

Procedural Generation System designed for:
- Infinite replayability
- Strategic variety
- Emergent storytelling
- Player-driven discovery

Enjoy unique playthroughs every time! 🎲✨
