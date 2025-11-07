# Quick Start - Adding Your Images

## Step 1: Shared Clothing (Create ONCE for all characters)

Copy your clothing PNG files to `shared_clothing/`:

```
shared_clothing/underwear/bra_standard_white.png
shared_clothing/underwear/panties_standard_white.png
shared_clothing/tops/blouse_white.png
shared_clothing/tops/tank_top.png
shared_clothing/bottoms/skirt_pencil.png
shared_clothing/bottoms/jeans_casual.png
...etc
```

**All characters will automatically be able to wear these clothes!**

---

## Step 2: Character Bodies (One per character)

For each character, copy their body image:

```
characters/Ruth/base/body.png
characters/Tom/base/body.png
characters/Lisa/base/body.png
characters/Marcus/base/body.png
characters/Sophie/base/body.png
characters/Rachel/base/body.png
characters/James/base/body.png
```

**Required: 7 body images (one per character)**

---

## Step 3: Character Expressions (9 per character)

For each character, copy their 9 expression images:

```
characters/Ruth/expressions/neutral.png
characters/Ruth/expressions/happy.png
characters/Ruth/expressions/sad.png
characters/Ruth/expressions/angry.png
characters/Ruth/expressions/surprised.png
characters/Ruth/expressions/aroused.png
characters/Ruth/expressions/embarrassed.png
characters/Ruth/expressions/confused.png
characters/Ruth/expressions/confident.png
```

Repeat for all 7 characters.

**Required: 63 expression images (9 × 7 characters)**

---

## Total Images Needed

- ✅ **40 shared clothing items** (create once, all can wear)
- ✅ **7 character bodies** (one per character)
- ✅ **63 expressions** (9 per character)

**Grand Total: ~110 images**

---

## Optional: Character-Specific Clothing

If you want Ruth to have a unique blouse that others don't have:

```
characters/Ruth/tops/blouse_fancy.png
```

The system will use Ruth's version for her, and the shared version for everyone else.

---

## File Requirements

- **Format**: PNG with transparency (alpha channel)
- **Size**: 1024x1536 pixels (2:3 portrait ratio)
- **Background**: Fully transparent
- **Alignment**: Keep body/face in same position across all layers

---

## Testing

1. Copy some images into the folders
2. Start the game: `python app.py`
3. Create a new game
4. Click "Change Outfit" on a character
5. Select different clothing items
6. Watch the character change clothes!

Placeholders will show for missing images - you can add them gradually.
