# Character Graphics System - Image Organization Guide

This guide explains how to organize your AI-generated character images for the layered sprite system.

## Overview

The game uses a **layered sprite system** similar to LabRats 2, where character images are composed of multiple layers:
- Base body
- Underwear (bra, panties)
- Clothing (tops, bottoms, dresses)
- Accessories (jewelry, glasses)
- Facial expressions

All layers stack on top of each other to create the final character appearance.

## Directory Structure

Images are organized by character name:

```
static/images/characters/
├── Ruth/
│   ├── base/
│   │   └── body.png
│   ├── expressions/
│   │   ├── neutral.png
│   │   ├── happy.png
│   │   ├── sad.png
│   │   ├── angry.png
│   │   ├── surprised.png
│   │   ├── aroused.png
│   │   ├── embarrassed.png
│   │   ├── confused.png
│   │   └── confident.png
│   ├── clothing/
│   │   ├── underwear/
│   │   │   ├── bra_standard_white.png
│   │   │   ├── bra_lace_black.png
│   │   │   ├── bra_sports.png
│   │   │   ├── panties_standard_white.png
│   │   │   ├── panties_lace_black.png
│   │   │   └── panties_thong.png
│   │   ├── tops/
│   │   │   ├── blouse_white.png
│   │   │   ├── blouse_sheer.png
│   │   │   ├── t_shirt_casual.png
│   │   │   ├── tank_top.png
│   │   │   ├── crop_top.png
│   │   │   └── sweater_modest.png
│   │   ├── bottoms/
│   │   │   ├── skirt_pencil.png
│   │   │   ├── skirt_mini.png
│   │   │   ├── pants_slacks.png
│   │   │   ├── jeans_casual.png
│   │   │   ├── shorts_athletic.png
│   │   │   └── leggings_yoga.png
│   │   ├── dresses/
│   │   │   ├── dress_modest_floral.png
│   │   │   ├── dress_cocktail.png
│   │   │   └── dress_sundress.png
│   │   └── outerwear/
│   │       └── (jackets, coats, etc.)
│   └── accessories/
│       ├── jewelry_pearls.png
│       ├── jewelry_choker.png
│       └── glasses_reading.png
├── Tom/
│   └── (same structure)
├── Lisa/
│   └── (same structure)
├── Marcus/
│   └── (same structure)
├── Sophie/
│   └── (same structure)
├── Rachel/
│   └── (same structure)
└── James/
    └── (same structure)
```

## Image Requirements

### Format
- **File Format**: PNG with transparency (alpha channel)
- **Recommended Size**: 1024x1536 pixels (2:3 aspect ratio portrait)
- **Color Mode**: RGBA (RGB + Alpha for transparency)

### Layer Guidelines

#### 1. Base Body (`base/body.png`)
- The foundational layer
- Should show the character's body in neutral pose
- **NO clothing** - just the body
- Use consistent skin tone across all your characters
- This layer is ALWAYS visible

#### 2. Expressions (`expressions/*.png`)
- Only the facial area (head/face)
- Transparent everywhere except the face
- Required expressions:
  - `neutral.png` - Default calm expression
  - `happy.png` - Smiling, pleased
  - `sad.png` - Unhappy, disappointed
  - `angry.png` - Frustrated, mad
  - `surprised.png` - Shocked, amazed
  - `aroused.png` - Flushed, interested
  - `embarrassed.png` - Blushing, shy
  - `confused.png` - Puzzled, uncertain
  - `confident.png` - Proud, self-assured
- Keep the same head position/angle across all expressions

#### 3. Clothing Layers
All clothing items should:
- Have transparent backgrounds
- Be positioned to align with the base body
- Only show the clothing item (bra, shirt, pants, etc.)
- NOT include the body underneath

**Underwear** (`clothing/underwear/`)
- Bras: Show only the bra, transparent everywhere else
- Panties: Show only the panties

**Tops** (`clothing/tops/`)
- Shirts, blouses, t-shirts, tank tops, crop tops, sweaters
- Should cover the appropriate body area
- Leave arms/shoulders transparent if sleeveless

**Bottoms** (`clothing/bottoms/`)
- Skirts, pants, shorts, leggings
- Cover from waist down (or wherever the garment starts)

**Dresses** (`clothing/dresses/`)
- Full dresses that replace both top and bottom
- Cover from shoulders to legs

**Accessories** (`accessories/`)
- Jewelry, glasses, etc.
- Very small items, mostly transparent

### Layer Stacking Order (Bottom to Top)
1. **base/body.png** (always visible)
2. **clothing/underwear/bra_*.png**
3. **clothing/underwear/panties_*.png**
4. **clothing/bottoms/*.png** (skirts, pants)
5. **clothing/tops/*.png** (shirts, blouses)
6. **clothing/dresses/*.png** (if worn, covers top+bottom)
7. **clothing/outerwear/*.png** (jackets, coats)
8. **accessories/*.png** (jewelry, glasses)
9. **expressions/*.png** (always on top)

## AI Image Generation Tips

### Stable Diffusion / Midjourney Prompts

#### For Base Body:
```
portrait of a woman, neutral pose, standing straight, arms at sides,
full body visible, plain background, no clothing, consistent lighting,
front view, 2:3 aspect ratio, high quality, detailed
```

#### For Expressions (example - happy):
```
close-up of woman's face, happy expression, smiling, same person as [base],
front view, neutral background, consistent lighting, high quality
```

#### For Clothing Items (example - white blouse):
```
white button-up blouse on transparent background, front view,
clothing only, no person, product photography style, high quality
```

### Important Tips:
1. **Use the SAME seed/character** for all layers of one character to maintain consistency
2. **Remove backgrounds** using tools like remove.bg or Photoshop
3. **Align layers** - all images should have the character in the same position
4. **Test each layer** individually to ensure transparency works
5. **Name files exactly** as shown in the clothing database (`data/clothing_items.py`)

## Adding New Clothing Items

### Step 1: Generate the Image
Create the clothing image with AI, remove the background, save as PNG

### Step 2: Place in Correct Folder
```bash
static/images/characters/Ruth/clothing/tops/blouse_fancy.png
```

### Step 3: Add to Database
Edit `data/clothing_items.py` and add your item:

```python
'blouse_fancy': ClothingItem(
    id='blouse_fancy',
    name='Fancy Blouse',
    category='tops',
    slot='top',
    image_path='clothing/tops/blouse_fancy.png',
    description='Elegant fancy blouse',
    tags=['formal', 'elegant'],
    coverage=80,
    formality=90
),
```

### Step 4: Restart the Game
The new item will appear in the dress-up interface!

## Available Clothing Items

See `data/clothing_items.py` for the complete list. Currently includes:

### Underwear
- White Cotton Bra
- Black Lace Bra
- Sports Bra
- White Cotton Panties
- Black Lace Panties
- Thong

### Tops
- White Blouse
- Sheer Blouse
- Casual T-Shirt
- Tank Top
- Crop Top
- Modest Sweater

### Bottoms
- Pencil Skirt
- Mini Skirt
- Dress Slacks
- Casual Jeans
- Athletic Shorts
- Yoga Leggings

### Dresses
- Floral Dress
- Cocktail Dress
- Sundress

### Accessories
- Pearl Necklace
- Choker
- Reading Glasses

## Placeholder System

If an image doesn't exist, the game will show a placeholder with:
- Character name
- Generic avatar icon
- Instructions for adding images

This means you can:
1. Start playing immediately with placeholders
2. Add images gradually as you create them
3. Test the system before committing to full art generation

## Testing Your Images

1. Place your images in the correct folders
2. Start the game
3. Click "Change Outfit" on a character card
4. Select different clothing items
5. Check that layers stack correctly
6. Verify transparency works (no white rectangles around clothing)

## Example Workflow

### Creating Ruth's Visuals:

1. **Generate base body**:
   - Prompt your AI with Ruth's description (age 44, maternal, professional)
   - Remove background
   - Save as `static/images/characters/Ruth/base/body.png`

2. **Generate expressions** (9 total):
   - Use same character seed
   - Generate each emotion
   - Remove backgrounds
   - Save in `expressions/` folder

3. **Generate her default outfit**:
   - White blouse → `clothing/tops/blouse_white.png`
   - Pencil skirt → `clothing/bottoms/skirt_pencil.png`
   - Standard white underwear → `clothing/underwear/bra_standard_white.png` + `panties_standard_white.png`

4. **Test in game**:
   - Start game
   - Check Ruth's character card shows the sprite
   - Click "Change Outfit"
   - Verify all items appear correctly

5. **Add more outfits**:
   - Generate additional clothing items
   - Add casual clothes, sexy clothes, etc.
   - Update `data/clothing_items.py` if needed

## Troubleshooting

### Image doesn't show up
- Check file path matches exactly (case-sensitive)
- Verify PNG has transparency (alpha channel)
- Make sure image is in the correct folder

### Layers don't align
- All images must be the same dimensions (1024x1536 recommended)
- Character should be in same position across all layers
- Use image editing software to align manually

### Clothing looks weird
- Check transparency - solid backgrounds will block lower layers
- Verify the clothing actually covers the right body parts
- Try adjusting the coverage/size of the clothing in AI generation

### Can't see new clothing in dress-up menu
- Check you added it to `data/clothing_items.py`
- Restart Flask server after editing Python files
- Verify the file path in the database matches the actual file

## Advanced: Creating Poses

Future enhancement: You can create multiple poses for each character:
- `base/body_standing.png`
- `base/body_sitting.png`
- `base/body_lying.png`

Then generate clothing for each pose. The system can be extended to switch poses based on context.

## Resources

### Free Tools:
- **Remove.bg** - Remove image backgrounds
- **GIMP** - Free image editor with layer support
- **Paint.NET** - Windows image editor

### AI Image Generators:
- **Stable Diffusion** (free, local)
- **Midjourney** (paid, high quality)
- **DALL-E** (paid, OpenAI)
- **Leonardo.ai** (free tier available)

### Character Consistency:
- Use same seed number
- Save your prompts
- Use "character reference" features if available
- Consider using LoRA models for consistent faces

---

**Need Help?** Check the console (F12) for error messages about missing images. The game will tell you which files it's looking for.
