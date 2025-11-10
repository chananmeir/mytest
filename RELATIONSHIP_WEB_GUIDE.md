# Character Relationship Web - User Guide

## Overview

The Relationship Web system makes your Family Dynamics RPG truly dynamic! Characters now:
- Notice changes in each other
- Gossip and spread information
- Protect loved ones
- Form alliances against you
- React to your manipulations realistically

**The core hypnosis mechanics are still there** - this just adds realistic social consequences!

## How It Works

### 1. Character-to-Character Relationships

Each character has relationship scores with other characters (0-20):

```python
Ruth's Relationships:
  - Tom: 12 (close - married)
  - Melanie: 7 (neutral - daughter)
  - Derek: 8 (neutral - nephew)
```

**Relationship Types:**
- 15-20: Very Close (family bonds, best friends)
- 10-14: Close (good relationship)
- 5-9: Neutral (cordial)
- 0-4: Distant (strained)

### 2. Observation System

Characters notice when others change:

**Example Scenario:**
```
You plant PHS on Lisa: "When criticized, defend me"
  ↓
Lisa activates PHS (defends you publicly)
  ↓
Ruth observes (she's Lisa's mother, relationship: 15)
  ↓
Ruth thinks: "That's not like Lisa..."
  ↓
Ruth's suspicion increases
```

**Observation Factors:**
- Relationship strength (closer = more attentive)
- Observer's personality (Dawn notices everything, Tom misses things)
- Change magnitude (bigger changes are easier to spot)
- Observer's existing suspicion (suspicious people watch closely)

**Game Messages You'll See:**
```
👀 Ruth notices Lisa is acting a bit different.
🤔 Tom thinks Derek's behavior is unusual.
😟 Dawn is concerned about Ruth's strange behavior.
⚠️ Melanie is very worried about Tom!
```

### 3. Gossip System

Characters talk to each other about what they notice:

**Example Cascade:**
```
Ruth notices Lisa acting weird
  ↓
Ruth tells Dawn (they're close, relationship: 11)
  ↓
Dawn's suspicion increases
  ↓
Dawn tells Karen (relationship: 14)
  ↓
Karen's suspicion increases
  ↓
Three people now suspicious!
```

**Gossip Credibility:**
- Close relationships = more believable
- Dawn (matriarch) = highly credible
- Vanessa (status-conscious) = less credible

**Game Messages:**
```
💬 Ruth tells Dawn about their suspicions. Dawn's suspicion increased by 15!
💬 Tom confides in Ruth...
```

### 4. Protective Behaviors

Characters protect those they care about:

**Protection Thresholds (based on relationship):**
- Very Close (15+): Protects at 20% suspicion
- Close (10-14): Protects at 40% suspicion
- Neutral (5-9): Protects at 60% suspicion
- Distant (0-4): Protects at 80% suspicion

**Example:**
```
You manipulate Lisa repeatedly
  ↓
Ruth notices (mother, relationship: 15)
  ↓
Ruth's concern reaches threshold
  ↓
Ruth takes action!
```

**Protection Actions:**
```
⚠️ Ruth warns you: "Leave Lisa alone."           (Low threat)
🛡️ Tom steps between you and Lisa!              (Medium threat)
🚨 Dawn confronts you: "Stop manipulating Lisa!" (High threat)
```

### 5. Alliance Formation

When multiple characters are suspicious, they coordinate:

**Alliance Strength Calculation:**
- Mutual relationship strength
- Similar suspicion levels (+20 if both suspicious)
- Both highly suspicious (+30)

**Example Alliance:**
```
Ruth: 60% suspicious of player
Tom: 55% suspicious of player
Ruth ↔ Tom: Relationship 12 (close)
  ↓
Alliance Strength: 75% (HIGH THREAT)
  ↓
They coordinate against you!
```

**Game Messages:**
```
🚨 WARNING: Ruth and Tom are working together against you! (Alliance: 75%)
⚠️ Melanie and Karen seem to be talking about you... (Alliance: 55%)
```

## Gameplay Examples

### Example 1: Subtle Manipulation

```
1. You plant PHS on Tom (low resistance, relationship with Ruth: 12)
2. PHS activates: Tom acts slightly different
3. Ruth observes (30% chance, she's close to Tom)
4. MISSED! Ruth doesn't notice this time
5. ✅ Safe... for now
```

### Example 2: Detected Manipulation

```
1. You plant strong PHS on Derek (high resistance)
2. PHS activates: Derek acts very out of character
3. Melanie observes (80% chance, Derek's sister)
4. ✓ NOTICED! Melanie is concerned
5. Melanie tells Ruth (gossip to close friend)
6. Ruth's suspicion increases by 12
7. ⚠️ Two people now suspicious!
```

### Example 3: Protective Response

```
1. You've built high rapport with Vanessa (15/20)
2. Ruth observes your closeness (relationship with Vanessa: 6)
3. Ruth becomes suspicious (+10)
4. Ruth tells Dawn about concerns
5. Dawn's suspicion increases (+8)
6. Ruth's suspicion hits 45
7. Dawn's relationship with Vanessa: 8 (neutral)
8. Protection threshold: 60
9. Not high enough yet... but getting close
```

### Example 4: Alliance Threat

```
1. Ruth suspicion: 65
2. Tom suspicion: 60
3. Ruth ↔ Tom relationship: 12 (married)
4. Alliance forms (strength: 75%)
5. 🚨 WARNING displayed
6. They start coordinating
7. If alliance strength > 80: Joint confrontation
8. Possible GAME OVER if confronted!
```

## Strategic Implications

### DO:
✅ Target low-resistance characters first (Tom, Karen)
✅ Space out your manipulations (avoid clustering)
✅ Use defensive PHS to reduce suspicion
✅ Build rapport slowly to avoid suspicion
✅ Monitor relationship map frequently
✅ Break up alliances by manipulating one member

### DON'T:
❌ Rapidly manipulate multiple people (everyone notices)
❌ Target someone's close relationships (triggers protection)
❌ Ignore rising suspicion (gossip spreads exponentially)
❌ Let alliances form (coordinated resistance is deadly)
❌ Use obvious PHS on high-resistance characters

## API Endpoints

### Check for Alliances
```
GET /api/social/alliances

Response:
{
  "success": true,
  "alliances": [
    {
      "character1": "Ruth",
      "character2": "Tom",
      "alliance_strength": 75,
      "threat_level": "high"
    }
  ],
  "alliance_count": 1,
  "threat_level": "high"
}
```

### Get Relationship Map
```
GET /api/social/relationship-map

Response:
{
  "success": true,
  "relationships": [
    {
      "name": "Ruth",
      "player_suspicion": 45,
      "relationships": {
        "Tom": {
          "score": 12,
          "type": "close",
          "protective_threshold": 40
        },
        ...
      },
      "character_suspicions": {
        "Lisa": 30,
        "Derek": 15
      }
    },
    ...
  ]
}
```

## Game Flow Integration

### During Conversations
```
Player talks to character
  ↓
GM analyzes conversation
  ↓
Rapport/emotional state changes
  ↓
SOCIAL DYNAMICS: Others observe changes
  ↓
Messages displayed: "Ruth noticed something..."
```

### When PHS Activates
```
PHS trigger detected
  ↓
Character performs influenced behavior
  ↓
SOCIAL DYNAMICS: Others observe out-of-character behavior
  ↓
Suspicion increases
  ↓
Immediate gossip if very concerned
  ↓
Protective responses if threshold met
```

### When Time Advances
```
Player advances time
  ↓
SOCIAL DYNAMICS: Gossip session triggered
  ↓
Characters share suspicions with close relationships
  ↓
Suspicion spreads through network
  ↓
Alliance checks performed
  ↓
Warnings displayed if alliances forming
```

## Character-Specific Behaviors

### Observers
- **Dawn**: Notices everything (+25% observation)
- **Karen**: Watches for rule-breaking (+20% observation)
- **Melanie**: Notices health/behavior changes (+15% observation)
- **Tom**: Often misses things (baseline only)

### Gossipers
- **Dawn**: Highly credible, everyone listens
- **Karen**: Frequent gossiper, moderate credibility
- **Vanessa**: Frequent gossiper, low credibility (exaggerates)
- **Tom**: Rarely gossips

### Protectors
- **Ruth**: Very protective of family
- **Tom**: Protective of close relationships, but conflict-avoidant
- **Dawn**: Matriarchal protection of all
- **Melanie**: Protects competence/reputation

## Tips for Success

1. **Monitor the Relationship Map**: Check `/api/social/relationship-map` regularly to see who's suspicious and who they're close to.

2. **Break Information Chains**: If Ruth is suspicious, avoid also making her close friends (Tom, Dawn) suspicious.

3. **Use Defensive PHS**: Plant suggestions that reduce suspicion toward specific targets.

4. **Target Isolated Characters**: Characters with fewer close relationships spread less gossip.

5. **Time Your Moves**: Space manipulations apart so suspicion decays between actions.

6. **Watch for Protection Triggers**: If someone's close relationship becomes suspicious, expect protective behavior.

7. **Prevent Alliances**: If two suspicious people are close, manipulate one to reduce their suspicion before they coordinate.

## Advanced Strategy: Social Chess

Think of the family as a social network graph:

```
         Dawn (matriarch)
        /  |  \
      /    |    \
   Ruth  Karen  Vanessa
    |      |      |
   Tom  Melanie Derek
```

**Key Nodes:**
- **Dawn**: Connected to everyone, high credibility
- **Ruth**: Hub for her branch (Tom, Melanie)
- **Karen**: Connected to Dawn and Melanie

**Strategy:**
1. Avoid manipulating Dawn early (alerts everyone)
2. Target edge nodes first (Tom, Derek, Vanessa)
3. Use rapport with edge nodes to build trust
4. Only target hub nodes (Ruth, Dawn) when well-established
5. Monitor cross-branch gossip (Ruth → Dawn → Karen chain)

---

**Remember:** The hypnosis is still the core power. The relationship web just makes the social consequences realistic. You're playing social chess now - every move affects the whole board!
