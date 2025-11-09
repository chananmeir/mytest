# Advanced Hypnosis Mechanics Guide

This guide covers the advanced hypnosis features that expand gameplay beyond basic post-hypnotic suggestions.

## Table of Contents
1. [Combo Suggestions (Chained PHS)](#combo-suggestions)
2. [Conflicting Suggestions (Internal Conflict)](#conflicting-suggestions)
3. [Group Hypnosis](#group-hypnosis)
4. [Resistance Breaking](#resistance-breaking)
5. [Mastery Level System](#mastery-level-system)

---

## Combo Suggestions

### Overview
Combo Suggestions allow you to create chains of connected PHS where one suggestion triggers the next, creating powerful cascading effects.

### How It Works
When you create a combo, you plant multiple PHS across different characters where each step triggers the next in sequence:

**Example Chain:**
1. Ruth feels guilty → She defends you to others
2. Ruth defends you → Tom agrees with her
3. Tom agrees → Dawn reconsiders her judgment of you

### Benefits
- **Combo Bonus:** +15% success rate on all steps in the chain
- **Powerful Effects:** Create complex social dynamics
- **Multi-Character Influence:** Affect multiple people in one coordinated action

### Costs
- **Base Cost:** 8 SP to create a combo
- **Per Step:** +2 SP for each step in the chain
- **Minimum:** 2 steps required
- **Maximum:** 5 steps allowed

**Example Cost Calculation:**
- 3-step combo: 8 + (3 × 2) = 14 SP total

### Usage Example

```python
from systems.advanced_hypnosis import AdvancedHypnosisSystem

# Define your combo chain
chain_steps = [
    {
        'target': 'Ruth',
        'trigger': 'when she feels guilty',
        'response': 'defend you to others',
        'next_trigger': 'Ruth defends you'
    },
    {
        'target': 'Tom',
        'trigger': 'Ruth defends you',
        'response': 'agree with Ruth',
        'next_trigger': 'Tom agrees'
    },
    {
        'target': 'Dawn',
        'trigger': 'Tom agrees',
        'response': 'reconsider her judgment of you'
    }
]

# Create the combo
success, message, combo = AdvancedHypnosisSystem.create_combo_suggestion(
    game_state,
    combo_name="Family Support Chain",
    chain_steps=chain_steps
)

if success:
    # Combo is active! Track it in game_state.player.active_combos
    game_state.player.active_combos.append(combo)
```

### Tracking Combo Progress
Each combo tracks its completion:
- `combo.get_completion_percent()` - Returns 0-100%
- `combo.is_complete` - True when all steps have activated
- `combo.activated_steps` - List of boolean flags for each step

---

## Conflicting Suggestions

### Overview
Plant contradictory suggestions in the same character to create internal psychological conflict. This is risky but can lead to interesting narrative outcomes.

### Conflict Types

1. **Emotional Conflict**
   - Mix positive emotions (love, trust) with negative (fear, suspicion)
   - Example: "Trust you deeply" vs. "Feel suspicious of you"

2. **Behavioral Clash**
   - Contradictory actions
   - Example: "Seek you out" vs. "Avoid you"

3. **Direct Contradiction**
   - Opposite responses to similar triggers
   - Example: "Speak warmly" vs. "Speak coldly"

### Conflict Level System
- **0-25:** Mild confusion, character notices something feels off
- **25-50:** Noticeable internal conflict, emotional distress
- **50-80:** Severe conflict, character may act erratically
- **80-100:** BREAKDOWN THRESHOLD - Character may have mental breakdown

### Risks
⚠️ **WARNING:** High conflict can lead to:
- Character becoming suspicious of manipulation
- Emotional breakdown requiring intervention
- Loss of rapport
- Unpredictable behavior

### Usage Example

```python
from systems.advanced_hypnosis import AdvancedHypnosisSystem

# Define conflicting suggestions
phs1 = {
    'trigger': 'when talking about family',
    'response': 'speak warmly about you'
}

phs2 = {
    'trigger': 'when thinking about trust',
    'response': 'feel suspicious of you'
}

# Plant conflicting suggestions
success, message, conflict = AdvancedHypnosisSystem.plant_conflicting_suggestions(
    game_state,
    target_name='Ruth',
    phs1=phs1,
    phs2=phs2
)

if success:
    # Track the conflict
    game_state.player.active_conflicts.append(conflict)

    # Monitor conflict level
    if conflict.is_near_breakdown():
        print("⚠️  Character is approaching mental breakdown!")
```

### Managing Conflicts
- Monitor `conflict.conflict_level` regularly
- Each time both PHS trigger, conflict increases
- You can resolve conflicts by:
  - Removing one of the conflicting PHS
  - Building rapport to help character cope
  - Using therapeutic conversation to reconcile the conflict

---

## Group Hypnosis

### Overview
Influence multiple people simultaneously with a shared trigger but individual responses. More challenging but highly rewarding.

### Mechanics
- **Minimum:** 2 targets required
- **Maximum:** 4 targets allowed
- **Shared Trigger:** All targets respond to the same trigger
- **Individual Responses:** Each person has their own unique response

### Success Rate Penalties
Group hypnosis is harder than individual sessions:
- **Base Success Rate:** Starts lower (35% + modifiers)
- **Group Penalty:** -10% per additional person beyond the first
- **Maximum Success:** Capped at 85% (vs 95% for individual)

**Example Penalties:**
- 2 people: -10% penalty
- 3 people: -20% penalty
- 4 people: -30% penalty

### Costs
- **Base Cost:** 10 SP
- **Per Person:** +4 SP for each target
- **2 person session:** 10 + (2 × 4) = 18 SP
- **4 person session:** 10 + (4 × 4) = 26 SP

### Strategic Uses
1. **Family Dinners:** Influence everyone at once during group scenes
2. **Coordinated Responses:** Make multiple people react similarly
3. **Social Proof:** When many people respond the same way, it normalizes the behavior

### Usage Example

```python
from systems.advanced_hypnosis import AdvancedHypnosisSystem

# Define group targets and their responses
targets = ['Ruth', 'Tom', 'Dawn']

shared_trigger = "when someone criticizes you"

individual_responses = {
    'Ruth': 'feel protective of you',
    'Tom': 'speak up in your defense',
    'Dawn': 'change the subject tactfully'
}

# Perform group hypnosis
success, message, num_planted = AdvancedHypnosisSystem.perform_group_hypnosis(
    game_state,
    targets=targets,
    shared_trigger=shared_trigger,
    individual_responses=individual_responses
)

if success:
    print(f"Successfully influenced {num_planted} people!")
    game_state.player.mastery_level.group_sessions_done += 1
```

---

## Resistance Breaking

### Overview
Permanently reduce a character's resistance through focused psychological work. This is a mini-game mechanic with three approaches.

### Approaches

#### 1. Rapport Approach (Safe & Slow)
- **Success Rate:** 70%
- **Resistance Reduction:** 10 points
- **Suspicion Risk:** 5% chance of +5 suspicion
- **Rapport Change:** +1
- **Description:** Build deep trust through genuine connection

#### 2. Pressure Approach (Fast & Risky)
- **Success Rate:** 85%
- **Resistance Reduction:** 15 points
- **Suspicion Risk:** 25% chance of +5 suspicion
- **Rapport Change:** -1
- **Description:** Apply psychological pressure to overwhelm defenses

#### 3. Manipulation Approach (Balanced)
- **Success Rate:** 75%
- **Resistance Reduction:** 10 points
- **Suspicion Risk:** 15% chance of +5 suspicion
- **Rapport Change:** 0
- **Description:** Use subtle manipulation techniques

### Costs
- **SP Cost:** 5 SP per attempt
- **Failure Penalty:** If you fail, you lose the SP AND character becomes more suspicious

### Minimum Resistance
Characters cannot be reduced below 10 resistance (some natural wariness remains).

### Usage Example

```python
from systems.advanced_hypnosis import AdvancedHypnosisSystem

# Choose your approach carefully
success, message, reduction = AdvancedHypnosisSystem.initiate_resistance_breaking(
    game_state,
    target_name='Melanie',
    approach='rapport'  # 'rapport', 'pressure', or 'manipulation'
)

if success:
    print(f"Reduced Melanie's resistance by {reduction} points!")
    # Melanie is now more susceptible to suggestions
else:
    print("Failed! She became more suspicious.")
```

### Strategy Tips
- **Use Rapport Approach** for characters you have good relationships with
- **Use Pressure Approach** when you need quick results and can afford the rapport loss
- **Use Manipulation Approach** when you want balanced risk/reward
- **Check suspicion levels** before attempting - high suspicion reduces success
- **Build rapport first** to offset any negative consequences

---

## Mastery Level System

### Overview
Your mastery level tracks your overall skill and experience with hypnosis. Higher mastery provides permanent bonuses.

### Tracked Statistics
- **Total PHS Planted:** Every suggestion you create
- **Successful Activations:** When your suggestions trigger successfully
- **Failed Activations:** When suggestions fail to trigger
- **Reinforcements Done:** Times you've reinforced existing PHS
- **Combos Completed:** Successful combo chains
- **Group Sessions Done:** Group hypnosis attempts
- **Resistance Breaks:** Successful resistance reduction

### Mastery Levels (0-10)

| Level | Title | Total Actions Required | Bonuses |
|-------|-------|------------------------|---------|
| 0 | Novice | 0-4 | None |
| 1 | Initiate | 5-9 | -0 SP cost, +2% success |
| 2 | Apprentice | 10-19 | -0 SP cost, +4% success |
| 3 | Practitioner | 20-29 | -1 SP cost, +6% success |
| 4 | Adept | 30-44 | -1 SP cost, +8% success |
| 5 | Expert | 45-64 | -1 SP cost, +10% success |
| 6 | Advanced Expert | 65-89 | -2 SP cost, +12% success |
| 7 | Master | 90-119 | -2 SP cost, +14% success |
| 8 | Grand Master | 120-149 | -2 SP cost, +16% success |
| 9 | Legendary | 150-199 | -3 SP cost, +18% success |
| 10 | Transcendent Master | 200+ | -3 SP cost, +20% success |

### Action Point Values
Different actions contribute different amounts:
- Basic PHS: 1 point
- Reinforcement: 1 point
- Successful activation: 1 point
- Combo completed: 3 points (more valuable!)
- Group session: 2 points
- Resistance break: 2 points

### Bonuses Explained

#### SP Cost Reduction
At higher mastery, you spend less SP on suggestions:
- Level 3+: -1 SP (3 SP ability costs 2 SP)
- Level 6+: -2 SP (3 SP ability costs 1 SP)
- Level 9+: -3 SP (3 SP ability costs 0 SP minimum)

Note: Minimum SP cost is always 1 (can't go below that).

#### Success Rate Bonus
Higher mastery increases your success rates:
- Level 1: +2% to all PHS success rates
- Level 5: +10% to all PHS success rates
- Level 10: +20% to all PHS success rates

This stacks with rapport and other bonuses!

### Checking Your Mastery

```python
# Get current mastery level
mastery = game_state.player.mastery_level
current_level = mastery.get_overall_mastery()  # 0-10

# Get description
from systems.advanced_hypnosis import AdvancedHypnosisSystem
description = AdvancedHypnosisSystem.get_mastery_level_description(current_level)

# Get current bonuses
sp_reduction, success_bonus = mastery.get_mastery_bonuses()

print(f"Mastery Level: {current_level} - {description}")
print(f"Bonuses: -{sp_reduction} SP cost, +{success_bonus}% success rate")
print(f"Success Rate: {mastery.get_success_rate():.1f}%")
```

### Tracking Your Progress

```python
mastery = game_state.player.mastery_level

print(f"Total PHS Planted: {mastery.total_phs_planted}")
print(f"Successful Activations: {mastery.successful_activations}")
print(f"Failed Activations: {mastery.failed_activations}")
print(f"Reinforcements: {mastery.reinforcements_done}")
print(f"Combos Completed: {mastery.combos_completed}")
print(f"Group Sessions: {mastery.group_sessions_done}")
print(f"Resistance Breaks: {mastery.resistance_breaks}")
```

---

## Integration with Game Systems

### Automatic Mastery Tracking
The system automatically tracks your actions when you use these features:
- Planting PHS (including combos and group) increments `total_phs_planted`
- The Game Master system should increment `successful_activations` or `failed_activations` when PHS trigger
- Reinforcements are tracked when you reinforce PHS
- Combos completion is tracked when all steps activate
- Group sessions are tracked when you perform group hypnosis
- Resistance breaks are tracked on success

### Save System Compatibility
All advanced features are compatible with the save/load system:
- Mastery level persists across saves
- Active combos are saved with their progress
- Active conflicts are saved with their conflict levels
- All data serializes to JSON

### Memory System Integration
Characters remember:
- When combos trigger (memorable multi-step events)
- Internal conflicts they experience
- Group hypnosis sessions (unusual group interactions)
- Resistance breaking attempts (significant psychological events)

---

## Best Practices

### Strategic Tips

1. **Start Simple**
   - Master basic PHS before attempting advanced techniques
   - Build mastery level through regular practice

2. **Combo Suggestions**
   - Plan your chains carefully - each step must be achievable
   - Use high-rapport characters for early steps
   - Save combos for important narrative moments

3. **Conflicting Suggestions**
   - Only use on characters you're willing to potentially damage
   - Monitor conflict levels closely
   - Have a plan to resolve conflicts before breakdown

4. **Group Hypnosis**
   - Best used during group scenes (family dinners, etc.)
   - Accept the lower success rates - affecting multiple people is worth it
   - Use for creating social proof and group dynamics

5. **Resistance Breaking**
   - Break resistance on key characters to unlock more options
   - Use rapport approach for long-term relationships
   - Use pressure approach only when desperate or don't care about rapport

6. **Mastery Progression**
   - Regularly use diverse techniques to increase mastery faster
   - Combos and group sessions provide more mastery points
   - High mastery makes everything easier - invest in it early

### Common Mistakes to Avoid

❌ **Don't:**
- Create combos with unrealistic trigger chains
- Plant conflicts without monitoring conflict levels
- Use group hypnosis with low-rapport targets
- Spam resistance breaking without checking suspicion
- Ignore mastery bonuses when planning SP budgets

✅ **Do:**
- Test basic PHS reliability before building combos on them
- Track conflict levels and resolve them proactively
- Build rapport with all group members before group sessions
- Use resistance breaking strategically on high-value targets
- Leverage mastery bonuses to reduce costs at higher levels

---

## Example Gameplay Session

Here's a complete example of using all advanced features together:

```python
from systems.advanced_hypnosis import AdvancedHypnosisSystem

# Session 1: Build Mastery (Early Game)
# Plant basic PHS to increase mastery
# ... (plant several basic PHS)

# Check progress
mastery_level = game_state.player.mastery_level.get_overall_mastery()
print(f"Mastery Level: {mastery_level}")

# Session 2: Break Resistance (Mid Game)
# Reduce Melanie's high resistance
success, msg, reduction = AdvancedHypnosisSystem.initiate_resistance_breaking(
    game_state, 'Melanie', 'rapport'
)
# Melanie: 75 → 65 resistance

# Session 3: Group Session (Mid Game)
# Family dinner scene - influence everyone at once
targets = ['Ruth', 'Tom', 'Dawn']
shared_trigger = "when discussing your future"
responses = {
    'Ruth': 'speak optimistically about your prospects',
    'Tom': 'mention job opportunities he heard about',
    'Dawn': 'express confidence in your abilities'
}

success, msg, count = AdvancedHypnosisSystem.perform_group_hypnosis(
    game_state, targets, shared_trigger, responses
)
# All three now have coordinated positive responses!

# Session 4: Create Combo (Late Game)
# High mastery, ready for complex chains
chain = [
    {'target': 'Ruth', 'trigger': 'feels guilty about judging you',
     'response': 'apologize to you privately', 'next_trigger': 'Ruth apologizes'},
    {'target': 'Melanie', 'trigger': 'Ruth apologizes',
     'response': 'reconsider her own judgments', 'next_trigger': 'Melanie softens'},
    {'target': 'Derek', 'trigger': 'Melanie softens',
     'response': 'follow her lead and be friendlier'}
]

success, msg, combo = AdvancedHypnosisSystem.create_combo_suggestion(
    game_state, "Apology Cascade", chain
)
game_state.player.active_combos.append(combo)
# Complex social cascade ready to trigger!

# Session 5: Experimental Conflict (Advanced)
# Only if you're ready for chaos
phs1 = {'trigger': 'when alone with you', 'response': 'confide in you deeply'}
phs2 = {'trigger': 'in public', 'response': 'act distant from you'}

success, msg, conflict = AdvancedHypnosisSystem.plant_conflicting_suggestions(
    game_state, 'Vanessa', phs1, phs2
)
# Vanessa now has confusing hot/cold behavior
# Creates interesting narrative tension!
```

---

## Troubleshooting

### "Not enough SP"
- Check your current SP: `game_state.player.suggestion_points`
- Remember combos and group sessions are expensive
- Consider your mastery level bonuses

### "Character at max PHS capacity"
- Remove or let old PHS expire
- Focus on reinforcing existing PHS instead
- Choose different targets

### "Combo step failed to plant"
- Check each target's rapport (needs 6+)
- Verify emotional states (can't be defensive/hostile)
- Ensure PHS capacity available

### "Conflict level too high"
- Remove one conflicting PHS manually
- Build rapport to help character cope
- Have therapeutic conversation to reconcile

### "Group hypnosis failed on some targets"
- This is normal - group sessions have lower success
- The successful targets still get the PHS
- Consider breaking into smaller groups

---

## Future Expansions

Potential future features:
- **Combo Interruption:** Other characters interfering with combo chains
- **Conflict Resolution Mini-games:** Active resolution mechanics
- **Mastery Skill Trees:** Specialize in combos, group work, or resistance breaking
- **Advanced Group Techniques:** Larger groups, cascading effects
- **Resistance Immunity:** Very high mastery makes some characters unbreakable

---

## Credits

Advanced Hypnosis Mechanics designed to add:
- Strategic depth through combo planning
- Narrative complexity through conflicts
- Social dynamics through group influence
- Character progression through mastery
- Risk/reward through resistance breaking

Enjoy the enhanced gameplay! 🧠✨
