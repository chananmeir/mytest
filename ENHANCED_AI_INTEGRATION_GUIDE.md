# Enhanced AI Integration Guide

This guide covers the advanced AI integration improvements that make characters more consistent, narratives more coherent, and dialogue more dynamic.

## Table of Contents
1. [Overview](#overview)
2. [Narrative Coherence Tracking](#narrative-coherence-tracking)
3. [Dynamic Dialogue System](#dynamic-dialogue-system)
4. [Emotional Memory Enhancement](#emotional-memory-enhancement)
5. [Character Voice Consistency](#character-voice-consistency)
6. [Integration & Usage](#integration--usage)

---

## Overview

The Enhanced AI Integration system improves four critical aspects of the game's AI:

1. **Narrative Coherence** - GM tracks long-term story arcs and themes
2. **Dynamic Dialogue** - Characters reference multiple past events naturally
3. **Emotional Memory** - Better importance weighting for emotional moments
4. **Voice Consistency** - Validation that characters maintain their personality

All systems work together automatically through the `EnhancedAIIntegration` class.

---

## Narrative Coherence Tracking

### What It Does

The Narrative Coherence Tracker monitors the story for emerging narrative arcs and maintains thematic consistency across the game.

### Key Features

#### Automatic Arc Detection
The system analyzes recent events to detect when narrative arcs begin:

```python
# Example: System detects "Ruth's Trust Journey" arc
Arc Detected:
- Name: "Ruth's Trust Journey"
- Theme: trust
- Characters: Ruth, You
- Key Events:
  1. Ruth confides in you
  2. You help Ruth with a problem
  3. Ruth starts defending you to others
```

#### Arc Types Detected
- **Trust & Redemption**: Character learns to trust/forgive
- **Conflict & Resolution**: Interpersonal tensions
- **Growth & Change**: Character development arcs
- **Family Dynamics**: Shifting family relationships
- **Revelation**: Secrets coming to light

#### Narrative Themes Tracked
- Trust/Betrayal
- Redemption/Fall
- Family/Connection
- Power/Influence
- Truth/Deception

### How It Works

**Automatic Detection:**
- Analyzes last 10 significant events
- Uses GM (LLM) to identify patterns
- Only creates arc if clear direction emerges
- Prevents duplicate arcs on same theme

**Arc Lifecycle:**
1. **Active**: Arc ongoing, accumulating events
2. **Resolved**: Arc reached natural conclusion
3. **Abandoned**: Arc fizzled out without resolution

**Tracking:**
- Each arc has 5+ key events before resolution check
- GM evaluates if arc has resolved (positive/negative/neutral)
- Completed arcs tracked in game history

### Usage Example

```python
# Automatic - happens in background
game_state.ai_integration.update_narrative(
    game_state,
    event_description="Ruth apologizes for past judgment",
    involved_characters=['Ruth', 'You']
)

# Check active arcs
for arc in game_state.ai_integration.narrative_tracker.active_arcs:
    print(f"{arc.arc_name}: {arc.theme}")
    print(f"Status: {arc.current_status}")
    print(f"Events: {len(arc.key_events)}")
```

### In Conversations

Narrative context automatically enhances character prompts:

```
NARRATIVE CONTEXT (roleplay awareness of these ongoing storylines):
- Ruth's Trust Journey (trust): You confided in the player →
  Player helped you → You defended them to Tom
```

This makes characters aware of broader storylines beyond individual memories.

---

## Dynamic Dialogue System

### What It Does

Enhances character dialogue by referencing multiple past events naturally, creating more realistic conversations.

### Multi-Event References

Instead of single memory recall, characters now reference:
- **2 emotional moments** (most important)
- **3 relevant conversations** (topic-based)
- **2 significant events** (highest importance)

### Example Output

**Without Enhancement:**
```
Ruth: "Yes, I remember you said that."
```

**With Enhancement:**
```
Ruth: "You know, this reminds me of when you helped me with Tom last week.
And what you said about family... I've been thinking about that a lot since
our conversation on the porch."
```

### How It Works

**Context Building:**
1. Retrieve diverse memory types
2. Sort by importance and recency
3. Filter by topic relevance
4. Format for natural reference

**Connection Detection:**
- Identifies word overlap between current topic and memories
- Suggests connections: "This reminds you of..."
- Limits to 2 connections to avoid overwhelming

### Usage Example

```python
# Automatic enhancement during conversations
enhanced_prompt = game_state.ai_integration.enhance_character_prompt(
    character=ruth,
    base_prompt=original_prompt,
    current_topic="family trust"
)

# Now ruth's prompt includes:
# - Emotional moments related to trust
# - Past conversations about family
# - Events where trust was important
```

### Benefits

- **Continuity**: Characters remember broader context
- **Depth**: Conversations feel more meaningful
- **Realism**: References feel natural, not forced
- **Engagement**: Players see their choices matter long-term

---

## Emotional Memory Enhancement

### What It Does

Improves how emotional moments are weighted, stored, and recalled with time-based decay and consolidation.

### Enhanced Importance Calculation

**Factors Considered:**
1. **Emotional Intensity** (biggest factor)
   - Ecstatic/Devastated/Furious/Betrayed: +3 importance
   - Joyful/Angry/Sad/Happy/Hurt: +2 importance
   - Anxious/Relaxed/Open/Tense: +1 importance

2. **Content Analysis**
   - High-impact words (promise, betray, love, hate, etc.): +1-2
   - Multiple impacts stack up to +2 max

3. **Rapport Level**
   - Rapport 15+: +2 importance
   - Rapport 10-14: +1 importance

4. **Social Context**
   - 3+ characters involved: +1 importance

**Result**: Emotional moments naturally rank 7-10 importance vs 3-5 for normal conversations.

### Time-Based Decay

Memories fade realistically over time:

**Decay Rates:**
- **Emotional moments**: 0.1/day (slow decay, floor of 4)
- **PHS events**: 0.05/day (very slow, floor of 5)
- **Important events**: 0.15/day (medium, floor of 3)
- **Conversations**: 0.2/day (fast, floor of 2)

**Example:**
```
Day 1:  Emotional moment = importance 9
Day 7:  importance 9 - (7 × 0.1) = 8.3 → 8
Day 30: importance 9 - (30 × 0.1) = 6
Day 50: importance 9 - (50 × 0.1) = 4 (floor reached)
```

Emotional memories persist longer but eventually fade to baseline.

### Memory Consolidation

Similar emotional moments consolidate into patterns:

**Before:**
- "Felt trust with player" (importance 7)
- "Felt trust with player" (importance 7)
- "Felt trust with player" (importance 8)

**After Consolidation:**
- "Multiple moments of feeling trust: confided secrets; shared fears; sought advice" (importance 9)

**Requirements:**
- 3+ memories with same emotional_context
- Consolidates into single, higher-importance memory
- Tagged as 'pattern' for recognition

### Usage Example

```python
# Record with enhanced importance
memory = game_state.ai_integration.record_enhanced_memory(
    character=ruth,
    content="You told the player your deepest fear",
    memory_type='emotional_moment',
    emotional_context='vulnerable',
    related_characters=['You']
)
# Automatically calculates enhanced importance (likely 8-9)

# Apply decay (call periodically, e.g., daily)
game_state.ai_integration.apply_memory_decay(ruth)

# Consolidate patterns
game_state.ai_integration.consolidate_emotional_memories(ruth)
```

---

## Character Voice Consistency

### What It Does

Validates character responses to ensure they maintain consistent personality, speech patterns, and voice across sessions.

### Voice Profiles

Each character has a tracked profile:

**Ruth's Profile:**
```python
{
    'core_phrases': ["I'm sorry", "Oh dear", "I hope", "Is that okay"],
    'sentence_length_avg': 12.5 words,
    'formality_level': 6 (out of 10),
    'consistency_score': 95.2%
}
```

**Components Tracked:**

1. **Core Phrases**: Signature expressions
   - Ruth: "I'm sorry", "Oh dear", "I hope"
   - Melanie: "Whatever", "Seriously?", "I don't have time"
   - Derek: "Bro", "No pain no gain", "Man,"

2. **Sentence Length**: Average words per sentence
   - Tracked over time
   - Flagged if 50%+ different from baseline

3. **Formality Level**: 1-10 scale
   - Ruth: 6 (casual-formal)
   - Melanie: 7 (professional)
   - Derek: 3 (very informal)
   - Karen: 9 (very formal)

4. **Consistency Score**: Running average (0-100%)
   - Starts at 100%
   - Updated with each response validation
   - Formula: (old_score × 0.9) + (new_score × 0.1)

### Validation Process

**Step 1: Analyze Response**
```python
is_valid, score, issues = validator.validate_response(
    character=ruth,
    response="Yeah bro, whatever. I don't really care.",
    expected_emotional_state="neutral"
)

# Returns:
# is_valid = False
# score = 55
# issues = [
#     "Too informal for character",
#     "Unusual phrase usage (not characteristic)"
# ]
```

**Step 2: Correction (if needed)**
```python
if not is_valid:
    correction_prompt = validator.generate_correction_prompt(
        character=ruth,
        response=response,
        issues=issues
    )
    # Re-generate with correction guidance
```

### Validation Checks

**1. Core Phrase Usage**
- Not required, but boosts score if present
- Natural usage > forced usage

**2. Sentence Length Consistency**
- Compare to baseline average
- Flag if difference > 50%
- Update rolling average

**3. Formality Match**
- Check informal vs formal markers
- Ruth (formality 6): Should be balanced
- Derek (formality 3): Should be very informal
- Karen (formality 9): Should be very formal

**Informal Markers**: gonna, wanna, yeah, bro, dude
**Formal Markers**: indeed, furthermore, shall, ought

**4. Overall Scoring**
- Start: 100 points
- Core phrase present: +5
- Sentence length off: -15
- Formality mismatch: -10
- Final: Pass threshold = 70+

### Automatic Correction

**When triggered:**
- Character response scores < 70
- Validation finds voice inconsistencies

**What happens:**
1. System generates correction prompt
2. Explains specific issues
3. Reminds of character's voice traits
4. Suggests re-generation

**Correction Prompt Example:**
```
The previous response had voice consistency issues:
- Too informal for character
- Unusual sentence length (5.0 words vs typical 12.5)

Ruth's CORE VOICE TRAITS:
- Uses phrases like: I'm sorry, Oh dear, I hope
- Formality level: 6/10
- Typical sentence length: 12 words

Please regenerate maintaining Ruth's authentic voice.
```

### Usage Example

```python
# Automatic validation during conversations
response, needs_regen, issues = game_state.ai_integration.process_character_response(
    character=ruth,
    response=llm_response,
    expected_emotional_state="neutral"
)

if needs_regen:
    print(f"Voice consistency issues: {issues}")
    # Regenerate with corrections

# Check character's consistency score over time
profile = game_state.ai_integration.voice_validator.voice_profiles['Ruth']
print(f"Ruth's consistency: {profile.consistency_score:.1f}%")
```

---

## Integration & Usage

### Automatic Integration

The enhanced AI system is automatically initialized in `GameState`:

```python
game_state = GameState()
# Automatically creates:
# - game_state.ai_integration
# - narrative_tracker
# - dialogue_enhancer
# - emotional_memory
# - voice_validator
```

### In LLM Conversations

**Enhanced Prompt Building:**

```python
# Original prompt
base_prompt = build_character_prompt(ruth)

# Enhanced with all AI features
enhanced_prompt = game_state.ai_integration.enhance_character_prompt(
    character=ruth,
    base_prompt=base_prompt,
    current_topic="family trust"
)

# Now includes:
# 1. Narrative context (active story arcs)
# 2. Multi-event references (diverse memories)
# 3. Enhanced emotional memories (properly weighted)
```

**Response Validation:**

```python
# Get LLM response
response = llm_handler.get_character_response(ruth, player_message)

# Validate consistency
final_response, needs_regen, issues = game_state.ai_integration.process_character_response(
    character=ruth,
    response=response,
    expected_emotional_state=ruth.emotional_state
)

if needs_regen:
    # Regenerate with corrections
    correction = voice_validator.generate_correction_prompt(ruth, response, issues)
    response = llm_handler.get_character_response(ruth, correction)
```

### Recording Events

**Enhanced Memory Recording:**

```python
# Use enhanced recording for automatic importance
memory = game_state.ai_integration.record_enhanced_memory(
    character=ruth,
    content="Confessed deep fear about family judgment",
    memory_type='emotional_moment',
    emotional_context='vulnerable',
    related_characters=['You']
)
# Automatically: high importance, proper weighting
```

**Narrative Updates:**

```python
# After significant events
game_state.ai_integration.update_narrative(
    game_state,
    event_description="Ruth and Melanie reconciled after argument",
    involved_characters=['Ruth', 'Melanie']
)
# Automatically: checks for new arcs, updates existing arcs
```

### Periodic Maintenance

**Memory Decay (run daily or on time advance):**

```python
# Apply to all characters
for character in game_state.characters.values():
    game_state.ai_integration.apply_memory_decay(character)
```

**Memory Consolidation (run weekly or every 50+ memories):**

```python
for character in game_state.characters.values():
    game_state.ai_integration.consolidate_emotional_memories(character)
```

### Save/Load Compatibility

**Automatic Serialization:**

```python
# Saving - automatic
game_state.save_game()
# Includes all AI integration data:
# - Narrative arcs and themes
# - Voice profiles and consistency scores

# Loading - automatic with backwards compatibility
game_state.load_game()
# Old saves: creates fresh AI integration
# New saves: restores all tracked data
```

---

## Benefits Summary

### For Players

✅ **More Believable Characters**
- Characters reference past events naturally
- Emotional moments remembered vividly
- Personality stays consistent session-to-session

✅ **Deeper Narratives**
- Story arcs emerge organically
- Themes develop over time
- Your choices create lasting storylines

✅ **Better Immersion**
- Characters feel "alive" with memory and personality
- Conversations build on history
- Long-term consequences visible

### For Developers

✅ **Automatic Quality Control**
- Voice consistency validated automatically
- No manual checking needed
- Issues flagged with specific feedback

✅ **Narrative Tracking**
- Story arcs detected and tracked
- Themes identified automatically
- Can query active storylines

✅ **Enhanced Memory System**
- Smarter importance calculation
- Realistic decay over time
- Automatic consolidation

---

## Configuration

### Tuning Parameters

```python
# In systems/enhanced_ai_integration.py

# Narrative Detection
NARRATIVE_MIN_EVENTS = 3  # Minimum events to detect arc
NARRATIVE_ARC_RESOLUTION_THRESHOLD = 5  # Events before checking resolution

# Memory Decay Rates
EMOTIONAL_DECAY_RATE = 0.1  # per day
PHS_DECAY_RATE = 0.05
EVENT_DECAY_RATE = 0.15
CONVERSATION_DECAY_RATE = 0.2

# Voice Consistency
VOICE_PASS_THRESHOLD = 70  # Score needed to pass
SENTENCE_LENGTH_VARIANCE = 0.5  # 50% allowed variance
```

### Disabling Features

To disable specific features:

```python
# Don't use narrative tracking
# Just don't call update_narrative()

# Don't use voice validation
# Just use LLM response directly without process_character_response()

# Don't use memory decay
# Don't call apply_memory_decay()
```

Each feature is independent and optional.

---

## Troubleshooting

### "No narrative arcs detected"
- Needs 3+ connected events
- Events must show clear pattern
- May take time to establish arcs

### "Voice consistency low"
- Check if character definition changed
- Verify response matches personality
- Review formality level settings

### "Too many memories consolidated"
- Adjust similarity threshold
- Increase minimum importance
- Run consolidation less frequently

### "Memory decay too fast/slow"
- Adjust decay rates in config
- Modify floor values
- Change decay rate per memory type

---

## Examples

### Complete Workflow Example

```python
# 1. Start conversation
player_msg = "Ruth, I need to talk about something important."

# 2. Enhance prompt with AI features
base_prompt = llm_handler._build_character_context(ruth)
enhanced_prompt = game_state.ai_integration.enhance_character_prompt(
    character=ruth,
    base_prompt=base_prompt,
    current_topic="important conversation"
)

# 3. Get response
response = llm_handler.get_character_response(ruth, player_msg)

# 4. Validate voice consistency
final_response, needs_regen, issues = game_state.ai_integration.process_character_response(
    character=ruth,
    response=response,
    expected_emotional_state=ruth.emotional_state
)

if needs_regen:
    # Regenerate with corrections
    print(f"Regenerating due to: {issues}")

# 5. Record enhanced memory
if player_msg_is_emotional:
    game_state.ai_integration.record_enhanced_memory(
        character=ruth,
        content=f"Deep conversation about: {topic}",
        memory_type='emotional_moment',
        emotional_context=ruth.emotional_state
    )

# 6. Update narrative
game_state.ai_integration.update_narrative(
    game_state,
    event_description="Ruth and player had important conversation",
    involved_characters=['Ruth']
)

# 7. Check for new arcs
for arc in game_state.ai_integration.narrative_tracker.active_arcs:
    if 'Ruth' in arc.involved_characters and arc.key_events[-1] == recent_event:
        print(f"✨ Story arc progressing: {arc.arc_name}")
```

---

## Future Enhancements

Potential improvements:

- **Multi-Arc Interactions**: Arcs affecting each other
- **Theme Resonance**: Amplify when multiple characters share theme
- **Voice Drift Alerts**: Notify when consistency drops below threshold
- **Memory Importance ML**: Learn optimal importance from player behavior
- **Narrative Prediction**: Suggest likely arc resolutions
- **Cross-Character Memory Sharing**: Gossip and information spread

---

## Credits

Enhanced AI Integration designed for:
- Deeper narrative coherence
- More realistic character consistency
- Better long-term memory management
- Natural multi-event references

Enjoy richer, more coherent storytelling! 🎭✨
