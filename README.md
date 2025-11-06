# Family Dynamics RPG

A psychological RPG where you use conversational hypnosis to shift family dynamics. Play as a recently unemployed 38-year-old who discovers the power of being underestimated.

## 🎮 Game Concept

You've lost your job 3 months ago. Your family knows. They pity you, judge you, or dismiss you. But what they don't know is that you've been studying conversational hypnosis - the subtle art of influence through rapport, emotional states, and carefully planted suggestions.

Starting from the lowest-status position in the family, you'll use:
- **Rapport Building** - Genuine connection creates influence
- **Emotional State Management** - Guide people from defensive to open
- **Post-Hypnotic Suggestions (PHS)** - Plant ideas that echo long after conversations end
- **Suggestion Points (SP)** - Earned through authentic interaction

This is not magic. This is **slow power**.

## 🎯 Game Features

- **Dynamic NPC Conversations** powered by LLM (via OpenRouter)
- **Complex Character System** with individual resistance levels and personalities
- **Post-Hypnotic Suggestion Mechanics** with trigger-based activation
- **Rapport & Emotional State Tracking** for each family member
- **Save/Load System** to preserve your progress
- **Multiple Dinner Stages** that evolve as the evening progresses

## 📋 Requirements

- Python 3.8+
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai/))

## 🚀 Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key:**
   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
   ```

4. **Run the game:**
   ```bash
   python main.py
   ```

## 🎲 How to Play

### Starting the Game

1. Choose "New Game" from the main menu
2. Read the introduction carefully - it sets the tone
3. You begin with **3 Suggestion Points (SP)**

### During Scenes

#### Talk to Someone
Engage in dynamic conversations powered by AI. The LLM will roleplay each character authentically based on:
- Their personality
- Current emotional state
- Rapport level with you
- Active post-hypnotic suggestions

Your words are analyzed to determine rapport changes and emotional shifts.

#### Plant Suggestions

**Requirements:**
- Rapport ≥ 6 with the target
- Target is not in a defensive/hostile state
- Target has capacity for more PHS
- Enough SP

**Types of Suggestions:**

| Type | SP Cost | Description |
|------|---------|-------------|
| Emotional Nudge | 2 SP | Subtle emotional shifts |
| Behavioral Prompt | 3 SP | Action-based suggestions |
| Strong Anchor | 4-6 SP | Deep, reinforced reactions |

**Example PHS:**
```
Target: Ruth
Trigger: "When someone mentions dinner"
Response: "You will feel the urge to speak kindly first"
```

#### Observe & Listen
- **Observe the Room** - Review everyone's status
- **Listen to Conversations** - Gain SP by being patient, learn dynamics

#### Build Rapport
Rapport increases through:
- Empathetic responses
- Authentic listening
- Showing vulnerability
- Understanding their perspective

Rapport decreases through:
- Manipulation detected
- Dismissive behavior
- Breaking trust

### Earning SP

- **Rapport milestones** (5, 10, 15, 20) = +1 SP each
- **Positive emotional shifts** = +1 SP
- **Patient observation** = +1 SP
- **Completing scenes** = variable SP

### Character Resistance Levels

| Character | Resistance | Notes |
|-----------|------------|-------|
| Melanie | 75% | Hardest to influence; pride-based |
| Derek | 65% | Ego identified with strength |
| Ruth | 55% | Guilt + loyalty are keys |
| Vanessa | 50% | Vanity is leverage |
| Dawn | 45% | Needs family harmony |
| Karen | 35% | Responds to authority + rules |
| Tom | 30% | Easiest to influence |

## 🗂️ Project Structure

```
family-dynamics-rpg/
├── main.py                 # Game entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment file
├── models/
│   ├── character.py      # Character & PHS classes
│   └── game_state.py     # Game state management
├── systems/
│   ├── hypnosis.py       # Suggestion & PHS mechanics
│   └── llm_handler.py    # OpenRouter API integration
└── scenes/
    ├── base_scene.py     # Base scene class
    └── family_dinner.py  # First playable scene
```

## 🎭 Characters

### Ruth (40) - Office Manager
- **Clothing:** Casual but coordinated
- **Personality:** Guilt-driven, loyal, tries to please everyone
- **Resistance:** 55%

### Melanie (35) - Nurse Practitioner
- **Clothing:** Scrubs or athletic-wear, smartwatch
- **Personality:** Proud, competent, dismissive of weakness
- **Resistance:** 75% (Hardest to influence)

### Tom (42) - IT Technician
- **Clothing:** Plain polo and jeans
- **Personality:** Conflict-avoidant, eager to please
- **Resistance:** 30% (Easiest to influence)

### Dawn (68) - Retired Teacher
- **Clothing:** Floral prints, pearls, cardigan
- **Personality:** Matriarch, values harmony
- **Resistance:** 45%

### Vanessa (37) - Marketing Executive
- **Clothing:** Trendy blazer, expensive shoes
- **Personality:** Status-conscious, competitive
- **Resistance:** 50%

### Derek (33) - Personal Trainer
- **Clothing:** Fitted t-shirt, gym shorts
- **Personality:** Ego-driven, physical confidence
- **Resistance:** 65%

### Karen (44) - Elementary School Principal
- **Clothing:** Structured, modest blouse & slacks
- **Personality:** Rigid, judgmental, needs control
- **Resistance:** 35%

## 💾 Save System

- Game automatically saves to `game_save.json`
- Save anytime during gameplay
- Load from main menu
- Preserves all character states, rapport, PHS, and progress

## 🔧 Configuration

Edit `config.py` or `.env` to customize:

```python
# OpenRouter settings
OPENROUTER_API_KEY = "your-key"
OPENROUTER_MODEL = "anthropic/claude-3.5-sonnet"

# Game settings
STARTING_SP = 3
MAX_RAPPORT = 20
```

## 🎯 Tips for Success

1. **Listen First** - Patience earns SP and reveals vulnerabilities
2. **Build Rapport Slowly** - Rushing raises suspicion
3. **Target Easy Characters First** - Tom and Karen are good starting points
4. **Use Emotional States** - Wait for openness before planting suggestions
5. **Reinforce Suggestions** - Repeated reinforcement increases activation chance
6. **Save Frequently** - Experimentation is part of the game

## 🐛 Troubleshooting

### "API key not configured"
- Make sure you've created a `.env` file
- Check that `OPENROUTER_API_KEY` is set correctly
- Verify the key is valid at openrouter.ai

### "API Error" or timeout
- Check your internet connection
- Verify OpenRouter service status
- Try a different model in config

### "Character not responding"
- This is a fallback behavior when API calls fail
- Check your API key and connection

## 📝 Game Design Philosophy

This game explores the ethics and mechanics of social influence. The "hypnosis" system is a game abstraction representing:

- Active listening and empathy
- Understanding emotional states
- Building genuine rapport
- Planting ideas through natural conversation
- The power dynamics in family systems

The player character's "power" comes from being underestimated, not from supernatural abilities.

## 🚀 Future Expansion Ideas

- [ ] Additional scenes (holiday gatherings, one-on-one meetings)
- [ ] Consequence system for failed/detected manipulation
- [ ] Character relationship webs (how they influence each other)
- [ ] Multiple endings based on final rapport levels
- [ ] PHS activation events and narrative payoffs
- [ ] Expanded character backstories and side quests

## 📜 License

This is a personal project created for entertainment and exploration of game mechanics.

## 🤝 Credits

Built with:
- Python
- OpenRouter API (LLM integration)
- Claude 3.5 Sonnet (for dynamic NPC conversations)

---

**Remember:** *People tell their secrets to those they don't consider dangerous.*

Start playing and discover the quiet power of influence.
