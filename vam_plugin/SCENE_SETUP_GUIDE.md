# Virt-A-Mate Scene Setup Guide

This guide explains how to create the game locations in Virt-A-Mate.

## Scene Organization

Create separate VaM scenes for each location, or use a single scene with different "rooms" that can be loaded/unloaded.

**Recommended Approach:** Single scene with separate room areas that can be shown/hidden.

---

## Location 1: Home - Living Room

**Scene Name:** `FamilyDynamics_Home_LivingRoom`

### Room Layout

```
     [Window]           [Window]
         |                 |
    [Bookshelf]       [TV on wall]
         |                 |
    [Armchair]  [Coffee Table]  [Armchair]
         \          |          /
          \     [Couch]      /
           \                /
        [Entry to Kitchen]
```

### Required Assets/Objects

1. **Furniture:**
   - Large couch (3-seater, fabric, beige/gray)
   - 2 armchairs (matching set)
   - Coffee table (wood, magazines on top)
   - TV stand or wall-mounted TV
   - Bookshelf (filled with books)
   - Side tables with lamps

2. **Electronics:**
   - **TV (Atom name: "TV")** - Make clickable
   - Remote control on coffee table
   - **Phone (Atom name: "Phone")** - Make clickable

3. **Decorations:**
   - Family photos on walls
   - Plants (potted, on floor/tables)
   - Curtains on windows
   - Rug under coffee table
   - Magazines, books on tables

4. **Books (Atom name: "Book")** - Make clickable
   - Place hypnosis book on coffee table or bookshelf
   - Should glow slightly or have indicator

5. **Lighting:**
   - Ceiling light (overhead)
   - 2 floor lamps
   - Natural light from windows
   - Time-based lighting system

### Interactive Objects

Set up collider triggers on:
- TV → Shows menu: Watch, Turn Off
- Phone → Shows menu: Check Messages, Call
- Book → Shows menu: Read, Study
- Couch → Shows menu: Sit, Wait
- Each character → Shows interaction menu

### Character Spawn Points

Create empty atoms for spawn positions:
- `Ruth_LivingRoom_Couch` (sitting on couch)
- `Tom_LivingRoom_Armchair` (sitting in armchair)
- `Melanie_LivingRoom_Standing` (near bookshelf)
- `Player_LivingRoom_Entry` (player spawn point)

### Camera Positions

Set up preset camera angles:
- `Cam_LivingRoom_Overview` - Full room view
- `Cam_LivingRoom_Couch` - Focused on couch
- `Cam_LivingRoom_TV` - TV viewing angle
- `Cam_LivingRoom_Player_POV` - First-person view

### Lighting States

**Morning (6:00-12:00):**
- Bright natural light from windows
- Lamps off
- Light color: Warm white (6500K)

**Afternoon (12:00-18:00):**
- Natural light, slightly dimmer
- Lamps off
- Light color: Neutral (5500K)

**Evening (18:00-21:00):**
- Dimmer natural light
- Lamps on
- Light color: Warm (3000K)

**Night (21:00-6:00):**
- No natural light
- Only lamps on, dimmed
- Light color: Very warm (2700K)

---

## Location 2: Home - Kitchen

**Scene Name:** `FamilyDynamics_Home_Kitchen`

### Room Layout

```
   [Window above sink]
          |
   [Counter] [Sink] [Counter]
          |
   [Stove] [Fridge]
          |
   [Island/Counter]
          |
      [Table] [Chairs x4]
```

### Required Assets/Objects

1. **Appliances:**
   - **Coffee Maker (Atom: "Coffee_Maker")** - Clickable
   - Refrigerator
   - Stove/Oven
   - Microwave
   - Toaster

2. **Furniture:**
   - Kitchen table with 4 chairs
   - Counter/island
   - Cabinets

3. **Items:**
   - Coffee mugs
   - Plates, bowls
   - Food items (fruit bowl, bread, etc.)
   - Clock on wall
   - Calendar

4. **Decorations:**
   - Kitchen towels
   - Plants (windowsill)
   - Family calendar/notices on fridge

### Interactive Objects

- Coffee Maker → Make Coffee, Drink Coffee
- Fridge → Open, Get Food
- Table → Sit, Eat
- Characters → Interact

### Character Spawn Points

- `Ruth_Kitchen_Stove` (cooking position)
- `Tom_Kitchen_Table` (sitting, reading paper)
- `Melanie_Kitchen_Counter` (getting coffee)
- `Player_Kitchen_Entry`

---

## Location 3: Home - Bedroom (Player's Room)

**Scene Name:** `FamilyDynamics_Home_Bedroom`

### Room Layout

```
     [Window]
        |
    [Dresser] [Mirror]
        |
     [Bed]
        |
   [Nightstand]
        |
    [Door]
```

### Required Assets/Objects

1. **Furniture:**
   - Single/double bed
   - Nightstand with lamp
   - Dresser
   - **Mirror (Atom: "Mirror")** - Clickable
   - Desk with chair

2. **Items:**
   - Alarm clock
   - Laptop/computer on desk
   - Books on nightstand
   - Clothes (some on chair/floor)
   - Personal items

3. **Decorations:**
   - Posters or art
   - Curtains
   - Rug

### Interactive Objects

- Bed → Sleep, Rest, Wait
- Mirror → Check Appearance, Change Clothes
- Laptop → Research Hypnosis, Browse
- Closet → Change Clothes

### Character Spawn Points

- `Player_Bedroom_Bed` (sleeping/sitting)
- `Player_Bedroom_Desk` (working)
- Characters don't normally enter (except special events)

---

## Location 4: Cafe

**Scene Name:** `FamilyDynamics_Cafe`

### Room Layout

```
   [Counter/Register]
         |
   [Display Case]
         |
   [Tables x6] [Chairs]
         |
   [Cozy Corner] [Armchairs]
```

### Required Assets/Objects

1. **Furniture:**
   - 6-8 small tables with chairs
   - Counter/bar
   - Cozy corner with armchairs
   - Bookshelves

2. **Cafe Items:**
   - Coffee machine (behind counter)
   - Display case with pastries
   - Menu boards
   - Coffee cups, mugs
   - Sugar, cream, napkins

3. **Decorations:**
   - Plants
   - Artwork on walls
   - Warm lighting
   - Music (ambient)

4. **NPCs:**
   - Barista (optional background character)
   - 2-3 background patrons

### Interactive Objects

- Counter → Order Coffee, Order Food
- Table → Sit, Meet Character
- Book (on table) → Read

### Character Spawn Points

- `Ruth_Cafe_Corner` (cozy armchair)
- `Melanie_Cafe_Table` (working on laptop)
- `Player_Cafe_Entry`
- `Player_Cafe_Counter` (ordering)

### Lighting

- Warm, cozy atmosphere
- Pendant lights over tables
- Natural light from large windows
- Consistent (no time changes in commercial space)

---

## Location 5: Park

**Scene Name:** `FamilyDynamics_Park`

### Scene Layout

```
       [Trees]
          |
   [Walking Path]
          |
   [Bench] [Bench]
          |
    [Pond/Fountain]
          |
   [Playground]
          |
   [Open Grass Area]
```

### Required Assets/Objects

1. **Nature:**
   - Trees (varied)
   - Grass ground texture
   - Flowers, bushes
   - Pond or fountain

2. **Furniture:**
   - Park benches (multiple)
   - Picnic tables
   - Trash bins
   - Lamp posts

3. **Playground:**
   - Swings
   - Slide
   - Sandbox

4. **NPCs:**
   - Joggers (background)
   - Dog walkers (background)
   - Families (background)

### Interactive Objects

- Bench → Sit, Wait, Meet
- Pond → Look at, Feed Ducks
- Path → Walk, Jog

### Character Spawn Points

- `Dawn_Park_Yoga` (on grass, yoga pose)
- `Tom_Park_Bench` (reading newspaper)
- `Player_Park_Entry`

### Lighting

Time-based outdoor lighting:
- Morning: Bright, long shadows
- Afternoon: Overhead sun, short shadows
- Evening: Golden hour, soft light
- Night: Dim streetlamps only

---

## Technical Implementation

### Scene Loading

**Method 1: Scene Switching**
```csharp
// In VaM plugin
SuperController.singleton.LoadScene("FamilyDynamics_Home_LivingRoom.json");
```

**Method 2: Show/Hide Rooms** (Recommended)
```csharp
// Keep all locations loaded, toggle visibility
SetRoomActive("LivingRoom", true);
SetRoomActive("Kitchen", false);
```

### Click Detection Setup

For each interactive object:

1. Add Collider component
2. Add Trigger script
3. Connect to plugin event handler

Example trigger code:
```csharp
// Attach to object's Collider
void OnTriggerEnter(Collider other)
{
    if (other.gameObject.name == "Player" || other.gameObject.tag == "PlayerController")
    {
        // Object was clicked/touched
        plugin.OnObjectInteraction(this.gameObject.name);
    }
}
```

### Dynamic Lighting

Use VaM's lighting system with scripted changes:

```csharp
void UpdateLighting(int hour)
{
    Light mainLight = GameObject.Find("MainLight").GetComponent<Light>();

    if (hour >= 6 && hour < 12) // Morning
    {
        mainLight.intensity = 1.0f;
        mainLight.color = new Color(1.0f, 0.95f, 0.9f); // Warm white
    }
    else if (hour >= 12 && hour < 18) // Afternoon
    {
        mainLight.intensity = 0.9f;
        mainLight.color = new Color(1.0f, 1.0f, 0.95f); // Neutral
    }
    else if (hour >= 18 && hour < 21) // Evening
    {
        mainLight.intensity = 0.5f;
        mainLight.color = new Color(1.0f, 0.85f, 0.7f); // Warm
    }
    else // Night
    {
        mainLight.intensity = 0.2f;
        mainLight.color = new Color(0.9f, 0.8f, 0.7f); // Very warm
    }
}
```

### Character Positioning

```csharp
void MoveCharacterToSpawn(string characterName, string locationId, string period)
{
    // Get spawn point based on schedule
    string spawnName = $"{characterName}_{locationId}_{period}";
    GameObject spawnPoint = GameObject.Find(spawnName);

    // Get character atom
    Atom character = SuperController.singleton.GetAtomByUid(characterName);

    if (character != null && spawnPoint != null)
    {
        character.transform.position = spawnPoint.transform.position;
        character.transform.rotation = spawnPoint.transform.rotation;
    }
}
```

---

## Setup Checklist

### For Each Scene:

- [ ] Create room layout with proper scale
- [ ] Add all required furniture and objects
- [ ] Set up interactive object colliders and triggers
- [ ] Create character spawn point markers
- [ ] Set up camera preset positions
- [ ] Configure lighting (including time-based states)
- [ ] Add decorative elements
- [ ] Test all interactive objects
- [ ] Save scene with proper naming
- [ ] Tag all objects appropriately

### Testing:

- [ ] Click detection works on all interactive objects
- [ ] Characters can be positioned at spawn points
- [ ] Lighting changes work properly
- [ ] Camera angles are comfortable
- [ ] Performance is acceptable (60+ FPS)
- [ ] VR navigation works smoothly
- [ ] No collision issues

---

## Next Steps

1. Start with **Living Room** (most important/used)
2. Add **Kitchen** and **Bedroom** (home locations)
3. Create **Cafe** (secondary location)
4. Build **Park** (outdoor variety)
5. Add additional locations as needed

Would you like me to create a step-by-step tutorial video script for building the living room scene?
