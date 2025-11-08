# Asset Manager Guide 🎨

## Quick Start

Access the Asset Manager by visiting: **http://localhost:5000/assets**

## Features

### 👔 Clothing Manager

Easily add, edit, and organize clothing items with visual assets.

**Access:** http://localhost:5000/assets/clothing

**Features:**
- ✅ Add new clothing items with full properties
- ✅ Visual item cards with previews
- ✅ Filter by category, slot, or search
- ✅ Tag-based organization
- ✅ Coverage & formality sliders
- ✅ Image upload support
- ✅ Automatic backups before any changes
- ✅ Delete items safely

### How to Add a Clothing Item

1. Click "+ Add New Item"
2. Fill in the form:
   - **Item ID**: Unique identifier (e.g., `bra_lace_red`)
   - **Name**: Display name (e.g., "Red Lace Bra")
   - **Category**: Select from dropdown (underwear, tops, bottoms, etc.)
   - **Slot**: Which body slot (bra, panties, top, bottom, etc.)
   - **Description**: Describe the item
   - **Image Path**: Relative path from character images folder
   - **Tags**: Add tags like "sexy", "revealing", "modest" (press Enter after each)
   - **Coverage**: 0-100 slider (how much body is covered)
   - **Formality**: 0-100 slider (casual to formal)
   - **Suggestibility Factor**: 0-3 (default 1.0)
3. Click "Save Item"

**Automatic backup is created before adding!**

### Coverage & Formality Guidelines

**Coverage:**
- 0-20: Minimal (thongs, crop tops)
- 20-40: Low (lace underwear, tank tops)
- 40-60: Medium (regular underwear, t-shirts)
- 60-80: High (jeans, long sleeve shirts)
- 80-100: Full (coats, full dresses)

**Formality:**
- 0-20: Very Casual (athletic wear, loungewear)
- 20-40: Casual (t-shirts, jeans)
- 40-60: Smart Casual (nice tops, dress pants)
- 60-80: Business (blouses, slacks, suits)
- 80-100: Formal (evening gowns, tuxedos)

### Tag Suggestions

**Revealing Tags:**
- `revealing` - Shows skin
- `sexy` - Attractive/alluring
- `bold` - Daring
- `provocative` - Very revealing

**Modest Tags:**
- `modest` - Conservative
- `professional` - Work appropriate
- `conservative` - Very covered
- `formal` - Formal attire

**Neutral Tags:**
- `casual` - Everyday wear
- `comfortable` - Cozy
- `elegant` - Classy
- `athletic` - Sportswear

## API Endpoints

All endpoints are prefixed with `/assets`

### Clothing Management

**List all items:**
```http
GET /assets/api/clothing/list
```

**Get specific item:**
```http
GET /assets/api/clothing/get/<item_id>
```

**Add new item:**
```http
POST /assets/api/clothing/add
Content-Type: application/json

{
  "id": "item_unique_id",
  "name": "Item Name",
  "category": "underwear",
  "slot": "bra",
  "description": "Item description",
  "tags": ["sexy", "revealing"],
  "coverage": 30,
  "formality": 50,
  "image_path": "underwear/item.png",
  "suggestibility_factor": 1.0
}
```

**Delete item:**
```http
POST /assets/api/clothing/delete/<item_id>
```

### Image Upload

**Upload image:**
```http
POST /assets/api/upload/image
Content-Type: multipart/form-data

file: <image file>
category: "underwear"
character: "Ruth"
```

**List all images:**
```http
GET /assets/api/images/list
```

### Backups

**List backups:**
```http
GET /assets/api/backup/list
```

**Restore from backup:**
```http
POST /assets/api/backup/restore/<filename>
```

## File Structure

```
mytest/
├── asset_manager.py          # Asset manager backend
├── templates/
│   ├── asset_manager.html    # Main asset manager page
│   └── clothing_manager.html # Clothing manager interface
├── data/
│   ├── clothing_items.py     # Clothing data (auto-edited)
│   └── backups/              # Automatic backups
└── static/
    └── images/
        └── characters/
            ├── general/
            │   ├── underwear/
            │   ├── tops/
            │   ├── bottoms/
            │   └── dresses/
            └── Ruth/
                ├── underwear/
                └── ...
```

## Backup System

**Automatic Backups:**
- Created before EVERY modification
- Stored in `data/backups/`
- Named with timestamp: `clothing_items_20250101_120000.py`
- Never lose your work!

**Restore from Backup:**
1. Go to `/assets/backup`
2. View available backups
3. Click "Restore" on the backup you want
4. Current file is backed up before restoring

## Image Upload

**Supported Formats:**
- PNG (recommended)
- JPG/JPEG
- GIF
- WEBP

**Upload Process:**
1. Select category (underwear, tops, etc.)
2. Select character (or "general")
3. Upload image
4. Copy returned path
5. Use path when adding clothing item

**Image Path Format:**
```
category/filename.png
```

Example: `underwear/bra_lace_red.png`

## Tips & Best Practices

### Naming Conventions

**Item IDs:**
```
{slot}_{style}_{color}
```

Examples:
- `bra_lace_black`
- `top_blouse_white`
- `dress_evening_red`

**Image Files:**
```
{item_id}.png
```

Keep image filenames matching item IDs for consistency.

### Organization

**Categories:**
- `underwear` - Bras, panties
- `tops` - Shirts, blouses, tank tops
- `bottoms` - Pants, skirts, shorts
- `dresses` - One-piece dresses
- `outerwear` - Jackets, coats
- `accessories` - Jewelry, glasses, etc.

**Slots:**
- `bra` - Bras
- `panties` - Underwear bottom
- `top` - Upper body clothing
- `bottom` - Lower body clothing
- `dress` - Full-body clothing
- `shoes` - Footwear
- `outerwear` - Outer layers
- `jewelry` - Accessories

### Tag Strategy

Use 3-5 tags per item:
1. One revealing level tag (`modest`, `revealing`, etc.)
2. One formality tag (`casual`, `formal`, etc.)
3. One comfort tag (`comfortable`, `professional`, etc.)
4. Optional style tags (`elegant`, `sporty`, `cute`)

### Coverage/Formality Balance

**High Coverage + Low Formality:**
- Athletic wear
- Comfortable home clothes
- Pajamas

**Low Coverage + High Formality:**
- Evening gowns
- Cocktail dresses
- Formal lingerie

**High Coverage + High Formality:**
- Business suits
- Professional attire
- Modest formal wear

**Low Coverage + Low Formality:**
- Bikinis
- Casual shorts
- Tank tops

## Troubleshooting

### Item Not Appearing

1. Check browser console for errors
2. Refresh the page
3. Verify item was added (check API response)
4. Look in correct category filter

### Image Not Showing

1. Verify image uploaded successfully
2. Check image path is correct
3. Check file exists in `static/images/characters/{character}/{category}/`
4. Try absolute path starting with `/static/images/...`

### Can't Add Item

1. Check all required fields are filled
2. Ensure item ID is unique
3. Check for JavaScript errors in console
4. Verify category and slot are valid

### Lost Data

1. Go to `/assets/backup`
2. Find most recent backup before issue
3. Click "Restore"
4. Your data is recovered!

## Advanced Usage

### Bulk Import

To add many items at once:
1. Create JSON file with items
2. Use bulk API endpoint (coming soon)
3. Or manually add via Python:

```python
from data.clothing_items import ClothingItem, ALL_CLOTHING_ITEMS

new_item = ClothingItem(
    id='my_item',
    name='My Item',
    ...
)

ALL_CLOTHING_ITEMS['my_item'] = new_item
```

### Custom Categories

To add new categories:
1. Edit `asset_manager.py`
2. Add to `categories` list in `/api/categories`
3. Create directory in `static/images/characters/general/`

### Integration with Game

Clothing items automatically integrate with:
- Character outfit system
- Suggestibility calculations
- Visual rendering (when images exist)
- PHS targeting

## Future Features

Planned additions:
- Bulk upload tool
- Image editor integration
- Character graphics manager
- Background manager
- UI elements manager
- Export/import clothing sets
- Visual outfit preview
- Drag-and-drop outfit creation

---

**Need Help?**

Check the main game documentation or asset manager code comments for more details!
