# .ENV Configuration Guide

This guide explains how to set up your `.env` file for optimal memory and performance.

## Quick Setup (Recommended)

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Add your single API key**:
   ```bash
   # Edit .env file
   OPENROUTER_API_KEY=your_actual_key_here
   ```

3. **Done!** The game will work perfectly with just one API key.

---

## Understanding API Keys

### ❌ DON'T: Use Multiple API Keys for Memory
You mentioned using 8 different API keys to give characters "more memory". **This doesn't work!**

**Why it doesn't work:**
- LLMs are completely stateless
- API keys don't create separate "memory spaces"
- Each conversation is independent regardless of which key you use
- The game's architecture already handles character separation

**Problems with multiple keys:**
- 8x more expensive
- More complex to manage
- No actual benefit
- Harder to scale

### ✅ DO: Use ONE API Key
The game already keeps characters separate through:
- Per-character conversation histories
- Character-specific system prompts
- Individual memory systems
- Unique personalities and context

**Benefits of one key:**
- 87.5% cheaper!
- Simpler to manage
- Same quality conversations
- Unlimited characters

---

## .ENV File Structure

### 1. BASIC SETUP (Required)

```bash
# Your single OpenRouter API key
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# Default model for all characters
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

**That's it!** This is all you need.

---

### 2. MEMORY OPTIMIZATION (Optional but Recommended)

```bash
# How much each character remembers
MAX_MEMORIES_PER_CHARACTER=100        # More = better long-term memory
MEMORY_RETRIEVAL_COUNT=15             # More = more context in conversations
MEMORY_IMPORTANCE_THRESHOLD=3         # Lower = remember more details

# Auto-consolidate similar memories to prevent redundancy
MEMORY_CONSOLIDATION_ENABLED=true
MEMORY_CONSOLIDATION_THRESHOLD=7

# Conversation history
CONVERSATION_HISTORY_LENGTH=30        # More = better short-term memory
```

**What these do:**
- `MAX_MEMORIES_PER_CHARACTER`: Total memories stored (100 is good, can go higher)
- `MEMORY_RETRIEVAL_COUNT`: How many memories included per conversation (15 is balanced)
- `CONVERSATION_HISTORY_LENGTH`: Messages kept in context (30 = ~15 exchanges)

**Recommendations by playstyle:**
- **Short sessions**: Use defaults (works great)
- **Long campaigns**: Increase to 150/20/50
- **Cost-conscious**: Decrease to 50/10/20

---

### 3. PER-CHARACTER MODELS (Optional - Cost Optimization)

If you want to save money, use cheaper models for simple characters:

```bash
# Main characters - use best model
RUTH_MODEL=anthropic/claude-3.5-sonnet
MELANIE_MODEL=anthropic/claude-3.5-sonnet

# Side characters - use cheaper model
TOM_MODEL=openai/gpt-4o-mini
DEREK_MODEL=openai/gpt-4o-mini
```

**Cost comparison:**
- Claude 3.5 Sonnet: $3 per million tokens (best quality)
- GPT-4o Mini: $0.15 per million tokens (good quality, 20x cheaper)

**You can skip this entirely** and just use one model for everyone!

---

## Complete .ENV Example

Here's a complete, optimized setup:

```bash
# ==============================================================================
# BASIC CONFIGURATION (REQUIRED)
# ==============================================================================
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# ==============================================================================
# MEMORY OPTIMIZATION (OPTIONAL)
# ==============================================================================
# Increased from defaults for better long-term campaigns
MAX_MEMORIES_PER_CHARACTER=150
MEMORY_RETRIEVAL_COUNT=20
MEMORY_IMPORTANCE_THRESHOLD=2
MEMORY_CONSOLIDATION_ENABLED=true
MEMORY_CONSOLIDATION_THRESHOLD=7
CONVERSATION_HISTORY_LENGTH=40

# ==============================================================================
# COST OPTIMIZATION (OPTIONAL)
# ==============================================================================
# Use cheaper models for side characters
TOM_MODEL=openai/gpt-4o-mini
DEREK_MODEL=openai/gpt-4o-mini
KAREN_MODEL=openai/gpt-4o-mini
VANESSA_MODEL=openai/gpt-4o-mini

# Keep main characters on best model
RUTH_MODEL=anthropic/claude-3.5-sonnet
MELANIE_MODEL=anthropic/claude-3.5-sonnet
DAWN_MODEL=anthropic/claude-3.5-sonnet
```

---

## Memory System Improvements

The game now has these enhanced memory features:

### 1. **Semantic Memory Retrieval**
Memories are retrieved based on relevance to current conversation, not just importance.

### 2. **Memory Consolidation**
Similar memories automatically merge to prevent redundancy:
- "Ruth said she likes coffee" + "Ruth mentioned loving coffee" → "Multiple related events: Ruth expressed enjoying coffee"

### 3. **Smart Importance Scoring**
The system automatically scores memory importance based on:
- Memory type (PHS triggers = 9/10, conversations = 5/10)
- Emotional keywords ("devastated", "ecstatic" boost importance)
- Emotional context at the time

### 4. **Conversation Summaries** (Advanced)
For very long conversations, enable:
```bash
USE_CONVERSATION_SUMMARY=true
```
This creates AI summaries of old conversations to save tokens.

---

## Recommended Settings by Use Case

### Casual Play (Default)
```bash
OPENROUTER_API_KEY=your_key
# Everything else uses defaults - works great!
```

### Long Campaign (More Memory)
```bash
OPENROUTER_API_KEY=your_key
MAX_MEMORIES_PER_CHARACTER=200
MEMORY_RETRIEVAL_COUNT=25
CONVERSATION_HISTORY_LENGTH=50
```

### Budget-Conscious (Save Money)
```bash
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=openai/gpt-4o-mini  # Cheaper model
MAX_MEMORIES_PER_CHARACTER=50
MEMORY_RETRIEVAL_COUNT=10
CONVERSATION_HISTORY_LENGTH=20
```

### Unlimited Budget (Best Quality)
```bash
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
MAX_MEMORIES_PER_CHARACTER=300
MEMORY_RETRIEVAL_COUNT=30
CONVERSATION_HISTORY_LENGTH=60
MEMORY_CONSOLIDATION_ENABLED=true
```

---

## Testing Your Setup

After creating your `.env` file:

1. **Start the game**:
   ```bash
   python app.py
   ```

2. **Check for warnings**:
   - If you see "⚠️ WARNING: OPENROUTER_API_KEY not set!" → your .env file isn't being read
   - Make sure it's named `.env` exactly (not `.env.txt`)

3. **Test a conversation**:
   - Talk to a character multiple times
   - They should remember previous conversations
   - Check memory in character profile

4. **Monitor memory usage**:
   - Characters automatically consolidate memories when they exceed the limit
   - You can view all memories in the character profile modal

---

## FAQ

**Q: Do I need separate API keys for each character?**
A: No! One key works perfectly. Characters are kept separate automatically.

**Q: Will increasing memory settings cost more?**
A: Yes, slightly. More context = more tokens = higher cost. But it's worth it for better conversations!

**Q: What if I have tons of characters?**
A: No problem! The memory system scales infinitely. Each character gets their own memory space.

**Q: Can I change settings mid-game?**
A: Yes! Changes take effect immediately when you restart Flask.

**Q: What's the optimal balance?**
A: The defaults are already optimized! Only increase if you're playing long campaigns.

---

## Summary

**Minimum setup** (just this!):
```bash
OPENROUTER_API_KEY=your_key_here
```

**Recommended setup** (add these for better memory):
```bash
OPENROUTER_API_KEY=your_key_here
MAX_MEMORIES_PER_CHARACTER=150
MEMORY_RETRIEVAL_COUNT=20
CONVERSATION_HISTORY_LENGTH=40
```

That's it! The game handles the rest automatically.
