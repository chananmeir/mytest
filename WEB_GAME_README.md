# Family Dynamics RPG - Web Version

🎮 **Full web-based game with visual novel aesthetics and point-and-click interface!**

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up your API keys:**
```bash
cp .env.example .env
nano .env  # Add your OpenRouter API keys
```

3. **Run the web server:**
```bash
python app.py
```

4. **Open your browser:**
```
http://localhost:5000
```

## 🎯 Features

### Main Menu
- **New Game**: Start a fresh game
- **Load Game**: Continue from your saved game
- **About**: Learn about the game mechanics

### Game Interface

#### Three-Panel Layout:
1. **Left Panel - Characters**: Click any character card to select them
2. **Center Panel - Dialogue**: Real-time conversations with LLM-powered responses
3. **Right Panel - Actions**: Access all game features

### Core Actions

#### 🎯 Plant Suggestion
- Click to open the suggestion menu
- Shows technique requirements (✓ or ✗)
- Three types: Emotional Nudge, Behavioral Prompt, Strong Anchor
- Can't plant without learning techniques first

#### 👤 View Profile
- See complete character information
- Rapport, emotional state, resistance
- Active post-hypnotic suggestions with activation chances
- All memories with importance ratings
- Appearance and clothing details

#### 🌳 Skill Tree
- Visual representation of all 11 techniques
- Status indicators: 🟢 Mastered, 🟡 Learning, ⚪ Available, 🔴 Locked
- Progress bars for techniques being learned
- Shows bonuses: SP cost reduction and success rate increase
- Organized by category: Basic → Intermediate → Advanced → Master

#### 📚 Study Hypnosis
- **Read a Book**: Browse 7 books, see what they teach
- **Practice Techniques**: Work on techniques you're learning
- **Research Online**: Random progress on available techniques

#### 📖 Read Books
- See all available books
- 📕 UNREAD / 📖 READ status
- Shows what techniques each book teaches (✓ if already known)
- Click to read and gain progress

### Real-Time Features
- Live SP (Suggestion Points) counter
- Dynamic skill level display
- Rapport bars that animate as they change
- System messages for all game events
- Character emotional states update in real-time

### Save/Load
- Click 💾 Save button anytime
- Saves to JSON file
- Load from main menu or during game

## 🎨 Visual Novel Aesthetics

- **Dark Theme**: Purple and pink gradients
- **Animated Elements**: Buttons, progress bars, dialogue
- **Hover Effects**: Everything responds to mouse movement
- **Modal Windows**: Professional popups for all features
- **Color Coding**:
  - 🟢 Green: Mastered/Success
  - 🟡 Yellow: In Progress/Warning
  - 🔴 Red: Locked/Danger
  - ⚪ White: Available

## 🎮 How to Play

1. **Select a Character**: Click any character card on the left
2. **Talk**: Type messages in the input box and press Send
3. **Build Rapport**: Have meaningful conversations to increase rapport
4. **Learn Techniques**: Use "Study Hypnosis" to master hypnosis skills
5. **Plant Suggestions**: Once you have techniques, plant triggers
6. **Watch It Unfold**: See your suggestions activate during conversations

## 🔧 Technical Details

### Backend
- **Flask**: Web framework
- **Session Management**: Game state stored in session
- **API Routes**: 15+ endpoints for all features
- **LLM Integration**: OpenRouter for character conversations
- **Game Master**: AI-powered conversation analysis

### Frontend
- **jQuery**: DOM manipulation and AJAX
- **Pure CSS**: No frameworks, custom styling
- **Responsive**: Works on desktop, tablet, mobile
- **Modular JS**: Clean, organized code

### API Endpoints

- `GET /`: Main menu
- `POST /new-game`: Start new game
- `POST /load-game`: Load saved game
- `GET /game`: Game interface
- `GET /api/game-state`: Current state
- `POST /api/talk`: Send message to character
- `GET /api/characters`: List all characters
- `GET /api/character/<name>`: Character details
- `GET /api/skill-tree`: Skill tree data
- `POST /api/study`: Study hypnosis
- `POST /api/plant-suggestion`: Plant PHS
- `GET /api/books`: Available books
- `POST /api/save-game`: Save game

## 📱 Browser Compatibility

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

## 🐛 Troubleshooting

### Game won't start
- Make sure you have `.env` file with API keys
- Check console for errors (F12)

### Characters not responding
- Verify OpenRouter API key is valid
- Check internet connection
- Look for errors in browser console

### Page looks broken
- Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)
- Clear browser cache
- Make sure CSS/JS files loaded (check Network tab)

## 🎭 Game Tips

1. **Start with Observation**: Learn basic techniques first
2. **Read Books**: Fastest way to learn (25-50% progress)
3. **Practice Daily**: Techniques at 15% per session
4. **Build Rapport First**: Need 6+ rapport to plant suggestions
5. **Watch Emotional States**: Better success when they're "open"
6. **Reinforce Suggestions**: Talk about triggers to strengthen them

## 📝 Comparison to Terminal Version

| Feature | Terminal | Web |
|---------|----------|-----|
| Interface | Text commands | Point and click |
| Conversations | Type & Enter | Type & Send button |
| Character Selection | Menu numbers | Click cards |
| Skill Tree | Text list | Visual tree |
| Plant Suggestion | Text menu | Modal with forms |
| Profile View | Text blocks | Formatted panels |
| Save/Load | Menu option | Button click |
| Visual Feedback | Text messages | Animations, colors |
| Aesthetic | Basic | Visual novel |

## 🚀 Future Enhancements

Possible additions:
- Character portraits/images
- Sound effects and music
- Animations for dialogue
- More scenes beyond family dinner
- Achievement system
- Multiple save slots
- Dark/light theme toggle
- Mini-games for practicing techniques

## 📄 License

Same as the main game - personal use, educational purposes.

---

**Enjoy your visual novel-style hypnosis RPG! 🎮✨**

Have fun manipulating your family dynamics through the power of conversational hypnosis!
