# Character-Specific Images

Each character folder contains images unique to that character:
- **base/body.png** - The character's body (no clothing)
- **expressions/** - 9 facial expressions for this character

## Required Files Per Character

For each character (Ruth, Tom, Lisa, Marcus, Sophie, Rachel, James):

### base/
- `body.png` - Character's body in neutral standing pose, no clothing

### expressions/
- `neutral.png` - Calm, default expression
- `happy.png` - Smiling, pleased
- `sad.png` - Unhappy, disappointed  
- `angry.png` - Frustrated, mad
- `surprised.png` - Shocked, amazed
- `aroused.png` - Flushed, interested
- `embarrassed.png` - Blushing, shy
- `confused.png` - Puzzled, uncertain
- `confident.png` - Proud, self-assured

## Image Requirements
- **Format**: PNG with transparency
- **Size**: 1024x1536 pixels recommended (2:3 ratio portrait)
- **Background**: Transparent (alpha channel)
- **Consistency**: Use same character seed/appearance across all images
- **Alignment**: Keep body/face in same position across all images

## Character-Specific Clothing (Optional)
If you want a character to have a unique version of a shared clothing item, create:
- `underwear/`, `tops/`, `bottoms/`, `dresses/`, `accessories/`

The game will use the character-specific version instead of the shared one.

For example:
- Create `Ruth/tops/blouse_white.png` for Ruth's special blouse
- All other characters will still use `shared_clothing/tops/blouse_white.png`
