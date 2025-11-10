# Character Images - All 37 Characters

Each character folder contains images unique to that character:
- **base/body.png** - The character's body (no clothing)
- **expressions/** - 9 facial expressions for this character

---

## Directory Structure

```
CharacterName/
├── base/
│   └── body.png          # Base body image
└── expressions/
    ├── neutral.png       # Default/resting expression
    ├── happy.png         # Smiling, content
    ├── sad.png           # Sad, disappointed
    ├── angry.png         # Angry, frustrated
    ├── surprised.png     # Shocked, surprised
    ├── aroused.png       # Flirty, aroused
    ├── embarrassed.png   # Blushing, shy
    ├── confused.png      # Puzzled, uncertain
    └── confident.png     # Confident, assertive
```

---

## All Characters (37 Total)

### Original Family (7)
- **Ruth** (40, F) - Office Manager, guilt-driven matriarch
- **Melanie** (35, F) - Nurse Practitioner, competent & proud
- **Tom** (42, M) - IT Technician, conflict-avoidant
- **Dawn** (68, F) - Retired Teacher, passive-aggressive
- **Vanessa** (37, F) - Marketing Executive, status-conscious
- **Derek** (33, M) - Personal Trainer, ego-driven
- **Karen** (44, F) - School Principal, rigid & judgmental

### Grocery Store Staff (3)
- **Emma** (22, F) - Cashier, bubbly & naive
- **Michael** (45, M) - Store Manager, stressed & lonely
- **Sofia** (28, F) - Produce Worker, health-conscious

### Neighbors (5)
- **Jessica** (32, F) - Stay-at-Home Mom, gossipy
- **David** (41, M) - Divorced Dad/Accountant, lonely
- **Amber** (25, F) - Bartender, wild & impulsive
- **Robert** (58, M) - Retired Professor, wise & intellectual
- **Chloe** (19, F) - College Student, naive & eager

### Gym/Fitness (4)
- **Tyler** (29, M) - Personal Trainer, motivating
- **Ashley** (34, F) - Yoga Instructor, calm & spiritual
- **Jake** (26, M) - Bodybuilder, arrogant & vain
- **Mia** (23, F) - Fitness Influencer, attention-seeking

### Café/Social (4)
- **Olivia** (21, F) - Barista/Art Student, creative & dreamy
- **Ethan** (37, M) - Freelance Writer, cynical & lonely
- **Isabella** (30, F) - Librarian, shy & bookish
- **Noah** (27, M) - Musician/Barista, passionate & emotional

### Mall/Shopping (3)
- **Sophia** (35, F) - Boutique Owner, stylish & critical
- **Liam** (24, M) - Electronics Clerk, nerdy & enthusiastic
- **Ava** (29, F) - Beauty Consultant, confident & flirty

### Professional/Work (4)
- **Daniel** (42, M) - Corporate Lawyer, ambitious & analytical
- **Emma_R** (38, F) - Family Doctor, caring but exhausted
- **William** (33, M) - High School Teacher, patient but worn
- **Madison** (31, F) - Real Estate Agent, persuasive & charming

### Service Workers (3)
- **Lucas** (26, M) - Delivery Driver, friendly hustler
- **Grace** (28, F) - Restaurant Waitress, bubbly but tired
- **Henry** (50, M) - Handyman, practical & reliable

### Random Encounters (4)
- **Zoe** (24, F) - Street Artist, free-spirited & spontaneous
- **Ryan** (36, M) - Police Officer, protective & suspicious
- **Natalie** (40, F) - Social Worker, empathetic & perceptive
- **Alex** (32, M) - Photographer, observant & creative

---

## Image Requirements

### For Each Character:
- **1 body image** (`base/body.png`)
- **9 expression images** (in `expressions/` folder)

### File Specifications:
- **Format**: PNG with alpha transparency
- **Size**: 1024x1536 pixels (2:3 portrait ratio)
- **Background**: Fully transparent
- **Alignment**: Keep face/body position consistent across all images

---

## Total Images Needed

| Category | Characters | Images per Character | Total |
|----------|-----------|---------------------|-------|
| Bodies | 37 | 1 | **37** |
| Expressions | 37 | 9 | **333** |
| **Grand Total** | | | **370 images** |

---

## Priority Order (Start Here)

Since 370 images is a lot, prioritize characters you'll encounter most:

### High Priority - Most Common Encounters
1. **Emma** (Grocery Store cashier - you'll see her often)
2. **Jessica** (Neighbor, grocery store, gossipy)
3. **David** (Lonely neighbor, grocery store evenings)
4. **Olivia** (Coffee shop barista)
5. **Chloe** (College student, easy target)

### Medium Priority - Regular Encounters
6. **Michael** (Grocery Store manager)
7. **Sofia** (Produce worker)
8. **Tyler** (Gym trainer)
9. **Ashley** (Yoga instructor)
10. **Ethan** (Writer at coffee shop)

### Lower Priority - Occasional
- Robert, Amber, Sophia, Liam, Ava
- Daniel, Emma_R, William, Madison
- Lucas, Grace, Henry
- Zoe, Ryan, Natalie, Alex

---

## Fallback System

Don't worry if you're missing images! The game uses placeholders:
- **Missing body**: Grey silhouette with character name
- **Missing expression**: Neutral grey face
- **Missing clothing**: Default outfit from `shared_clothing/`

You can add images gradually - start with 1-2 characters and expand!

---

## Character-Specific Clothing (Optional)

If you want a character to have unique clothing items:

```
CharacterName/
├── underwear/
├── tops/
├── bottoms/
├── dresses/
└── accessories/
```

The game will use character-specific versions over shared versions.

Example:
- Create `Emma/tops/uniform_shirt.png` for her work uniform
- Everyone else uses `shared_clothing/tops/uniform_shirt.png`

---

## Where Characters Appear

### Grocery Store
Morning: Emma, Michael, Sofia, Jessica, Henry, Lucas, Ryan
Evening: David, Emma_R, Natalie, Tyler, Ashley

### Coffee Shop
Morning: Olivia, Robert, Chloe, Noah
Afternoon: Ethan, Jessica, David, Natalie, Alex
Evening: William, Emma_R, Ashley, Sofia, Henry

### Fitness Center
Morning: Tyler, Ashley, Sofia
Afternoon: Tyler, Jake, Mia, Ryan
Evening: Michael, Daniel, Madison

### Shopping Mall
Afternoon: Sophia, Liam, Ava, Amber, Chloe
Evening: Emma, Jake, Mia, Zoe

### Library
Afternoon: Isabella, Robert, Ethan, Chloe
Evening: William, Natalie

### City Park
Afternoon: Ashley, Noah, Zoe, Alex
Night: Ryan, Grace, Henry, Isabella

### Restaurant
Evening: Michael, Noah, Robert, Sophia, Daniel, Madison
Night: David, Ethan, Grace, Alex, Zoe

---

## Quick Start Guide

1. **Pick 1 character** to start (recommend Emma - grocery cashier)
2. **Create 2 images**:
   - `Emma/base/body.png`
   - `Emma/expressions/neutral.png`
3. **Test in game**:
   - Travel to Grocery Store
   - See Emma appear with her image!
4. **Add more**:
   - Create her other 8 expressions
   - Move to next character (Jessica, David, Olivia)

---

## Tips for AI Image Generation

- Use consistent prompts/seeds per character
- Include: age, gender, occupation in prompt
- Keep camera angle/pose identical
- Use "transparent background" in prompt
- Generate all 9 expressions in one batch for consistency
- Recommend: Stable Diffusion, Midjourney, or DALL-E

Example prompt for Emma:
```
"22 year old female cashier, friendly smile, ponytail,
store uniform, standing pose, full body, transparent background,
2:3 portrait ratio, [EXPRESSION: neutral/happy/sad/etc]"
```
