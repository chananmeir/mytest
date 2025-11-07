# Template Images System Guide

## Overview

The template images system allows you to quickly create new characters without needing unique images for each one. When you create a character, the game will automatically use age and gender-appropriate template images as fallbacks until you create character-specific images.

## How It Works

When a character's sprite is rendered, the game follows this fallback chain:

1. **Character-Specific Image** (highest priority)
   - `static/images/characters/{Name}/base/body.png`
   - `static/images/characters/{Name}/expressions/{emotion}.png`

2. **Age-Based Template** (fallback)
   - `static/images/templates/{gender}/{age-bracket}/base/body.png`
   - `static/images/templates/{gender}/{age-bracket}/expressions/{emotion}.png`

3. **Hide Layer** (if nothing found)
   - Shows placeholder with character name

## Directory Structure

```
static/images/templates/
├── male/
│   ├── teens/      (age 13-19)
│   │   ├── base/
│   │   │   └── body.png
│   │   └── expressions/
│   │       ├── neutral.png
│   │       ├── happy.png
│   │       ├── sad.png
│   │       ├── angry.png
│   │       ├── surprised.png
│   │       ├── aroused.png
│   │       ├── embarrassed.png
│   │       ├── confused.png
│   │       └── confident.png
│   ├── 20s/        (age 20-29)
│   │   ├── base/
│   │   └── expressions/
│   ├── 30s/        (age 30-39)
│   │   ├── base/
│   │   └── expressions/
│   ├── 40s/        (age 40-49)
│   │   ├── base/
│   │   └── expressions/
│   ├── 50s/        (age 50-59)
│   │   ├── base/
│   │   └── expressions/
│   └── 60s/        (age 60+)
│       ├── base/
│       └── expressions/
└── female/
    ├── teens/
    ├── 20s/
    ├── 30s/
    ├── 40s/
    ├── 50s/
    └── 60s/

```

## Creating Template Images

### Step 1: Generate Base Bodies

Create one base body image for each age/gender combination:

**Example Prompt for AI Image Generator:**
```
A generic 40-year-old male, standing straight, neutral expression,
full body from head to toe, front view, realistic style,
PNG with transparent background, 1024x1536 pixels
```

**Save as:** `static/images/templates/male/40s/base/body.png`

### Step 2: Generate Expressions

Create expression overlays for each age/gender combination:

**Example Prompt:**
```
Close-up face of a 40-year-old male, happy expression,
realistic style, PNG with transparent background,
1024x1536 pixels (same dimensions as body)
```

**Save as:** `static/images/templates/male/40s/expressions/happy.png`

### Required Expressions
- `neutral.png` - Default expression
- `happy.png` - Joyful, smiling
- `sad.png` - Disappointed, down
- `angry.png` - Frustrated, mad
- `surprised.png` - Shocked, amazed
- `aroused.png` - Interested, attracted
- `embarrassed.png` - Shy, flustered
- `confused.png` - Puzzled, uncertain
- `confident.png` - Self-assured, bold

## Workflow Examples

### Example 1: Create "George" (45-year-old male)

1. **In Game:**
   - Click "➕ Add Character"
   - Name: George
   - Age: 45
   - Gender: Male
   - Fill in other fields
   - Click "Create Character"

2. **What Happens:**
   - George appears immediately using:
     - Body: `static/images/templates/male/40s/base/body.png`
     - Expressions: `static/images/templates/male/40s/expressions/*.png`
   - George is visible and functional right away!

3. **Later (Optional):**
   - Generate George-specific images
   - Place in `static/images/characters/George/base/body.png`
   - Game automatically uses George's unique images instead of templates

### Example 2: Create "Emily" (28-year-old female)

1. **In Game:**
   - Click "➕ Add Character"
   - Name: Emily
   - Age: 28
   - Gender: Female

2. **What Happens:**
   - Emily uses:
     - Body: `static/images/templates/female/20s/base/body.png`
     - Expressions: `static/images/templates/female/20s/expressions/*.png`

3. **Customize Later:**
   - Create Emily-specific images when ready
   - Place in `static/images/characters/Emily/`

## Image Requirements

### Technical Specs
- **Format:** PNG with transparency
- **Size:** 1024 x 1536 pixels
- **Content:**
  - **Body:** Full body, standing straight, neutral pose
  - **Expressions:** Just the face/head (will overlay on body)

### Recommended AI Tools
- **Stable Diffusion** - Free, local generation
- **Midjourney** - High quality, subscription
- **DALL-E** - Good for consistent characters
- **Leonardo.ai** - Character consistency features

## Prioritization Strategy

### Must-Have Templates (Start Here)
Create these first for maximum coverage:

1. **male/40s/** - Covers most male adults (30-49)
2. **female/40s/** - Covers most female adults (30-49)
3. **male/20s/** - Young adult males
4. **female/20s/** - Young adult females

With just these 4 templates, you can create a wide variety of characters!

### Optional Templates (Add Later)
- **teens/** - For younger characters
- **50s/60s/** - For older characters

## Tips for Consistent Templates

### 1. Use the Same Base Prompt
```
Generic [age]-year-old [gender], average build, neutral expression,
standing straight, front view, realistic style, transparent background
```

### 2. Keep Lighting Consistent
- Use the same lighting setup for all templates
- Neutral, front-facing light
- Avoid dramatic shadows

### 3. Match Proportions
- All bodies should be same height in frame
- Expressions should align with body face position

### 4. Test Your Templates
```bash
# Create a test character in game
# Check if expressions align properly
# Verify clothing layers correctly
```

## Troubleshooting

### Template Not Loading
```
Console shows: "Image not found: .../templates/male/40s/base/body.png"
```

**Solution:**
1. Check file exists at exact path
2. Verify filename is exactly `body.png` (lowercase)
3. Check image is valid PNG with transparency

### Expression Doesn't Align with Body
```
Face appears in wrong position
```

**Solution:**
1. Ensure all images are exact same dimensions (1024x1536)
2. Position face in same location across all images
3. Use image editing software to align layers before export

### Character Shows Placeholder Instead of Template
```
Shows "👤 [Name]" placeholder
```

**Possible causes:**
1. Template image doesn't exist yet
2. Age bracket has no template
3. Wrong gender specified

**Solution:**
- Create the missing template images
- Or create character-specific images

## Upgrading Characters to Unique Images

When you're ready to give a character unique images:

1. **Create directory:**
   ```bash
   mkdir -p static/images/characters/George/base
   mkdir -p static/images/characters/George/expressions
   ```

2. **Generate unique images** using AI with specific prompts for George's appearance

3. **Place images:**
   ```
   static/images/characters/George/
   ├── base/
   │   └── body.png
   └── expressions/
       ├── neutral.png
       ├── happy.png
       └── ... (other expressions)
   ```

4. **Refresh game** - George automatically uses unique images!

## Quick Start Checklist

- [ ] Create `male/40s/base/body.png`
- [ ] Create `male/40s/expressions/` (9 expressions)
- [ ] Create `female/40s/base/body.png`
- [ ] Create `female/40s/expressions/` (9 expressions)
- [ ] Test by creating a 45-year-old male character
- [ ] Test by creating a 42-year-old female character
- [ ] Verify sprites appear correctly
- [ ] Add more age brackets as needed

## Summary

**Benefits:**
- ✅ Create characters instantly without custom images
- ✅ Characters are immediately visible in game
- ✅ Customize later when you have time
- ✅ Share templates across multiple characters
- ✅ Reduce image creation workload

**Key Concept:**
Templates = Temporary placeholders that look good enough until you create unique images for specific characters you care about!

Now you can rapidly expand your game universe without image generation being a bottleneck! 🎨✨
