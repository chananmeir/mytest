# Comprehensive plant database for Homestead Tracker
# Based on Eliot Coleman and Nico Jabour's winter gardening techniques

PLANT_DATABASE = [
    # Winter Hardy Greens
    {
        'id': 'spinach-1',
        'name': 'Spinach',
        'scientificName': 'Spinacia oleracea',
        'category': 'vegetable',
        'spacing': 4,
        'rowSpacing': 12,
        'daysToMaturity': 40,
        'frostTolerance': 'very-hardy',
        'winterHardy': True,
        'companionPlants': ['lettuce-1', 'radish-1'],
        'incompatiblePlants': [],
        'waterNeeds': 'medium',
        'sunRequirement': 'full',
        'soilPH': {'min': 6.5, 'max': 7.5},
        'plantingDepth': 0.5,
        'germinationTemp': {'min': 35, 'max': 75},
        'transplantWeeksBefore': 6,
        'notes': 'Excellent for winter harvest. Grows well under row covers.'
    },
    {
        'id': 'kale-1',
        'name': 'Kale (Lacinato)',
        'scientificName': 'Brassica oleracea',
        'category': 'vegetable',
        'spacing': 12,
        'rowSpacing': 18,
        'daysToMaturity': 55,
        'frostTolerance': 'very-hardy',
        'winterHardy': True,
        'companionPlants': ['onion-1', 'beet-1'],
        'incompatiblePlants': ['tomato-1'],
        'waterNeeds': 'medium',
        'sunRequirement': 'full',
        'soilPH': {'min': 6.0, 'max': 7.5},
        'plantingDepth': 0.5,
        'germinationTemp': {'min': 40, 'max': 85},
        'transplantWeeksBefore': 6,
        'notes': 'Sweetens after frost. Survives to 10°F with protection.'
    },
    {
        'id': 'lettuce-1',
        'name': 'Lettuce (Mixed)',
        'scientificName': 'Lactuca sativa',
        'category': 'vegetable',
        'spacing': 6,
        'rowSpacing': 12,
        'daysToMaturity': 45,
        'frostTolerance': 'hardy',
        'winterHardy': True,
        'companionPlants': ['carrot-1', 'radish-1'],
        'incompatiblePlants': [],
        'waterNeeds': 'medium',
        'sunRequirement': 'partial',
        'soilPH': {'min': 6.0, 'max': 7.0},
        'plantingDepth': 0.25,
        'germinationTemp': {'min': 40, 'max': 75},
        'transplantWeeksBefore': 4,
        'notes': 'Succession plant every 2 weeks.'
    },
    # Root Vegetables
    {
        'id': 'carrot-1',
        'name': 'Carrot',
        'scientificName': 'Daucus carota',
        'category': 'vegetable',
        'spacing': 2,
        'rowSpacing': 12,
        'daysToMaturity': 70,
        'frostTolerance': 'hardy',
        'winterHardy': True,
        'companionPlants': ['onion-1', 'lettuce-1'],
        'incompatiblePlants': [],
        'waterNeeds': 'medium',
        'sunRequirement': 'full',
        'soilPH': {'min': 6.0, 'max': 6.8},
        'plantingDepth': 0.25,
        'germinationTemp': {'min': 45, 'max': 85},
        'transplantWeeksBefore': 0,
        'notes': 'Can overwinter in ground with mulch.'
    },
    {
        'id': 'beet-1',
        'name': 'Beet',
        'scientificName': 'Beta vulgaris',
        'category': 'vegetable',
        'spacing': 3,
        'rowSpacing': 12,
        'daysToMaturity': 55,
        'frostTolerance': 'hardy',
        'winterHardy': True,
        'companionPlants': ['onion-1', 'kale-1'],
        'incompatiblePlants': [],
        'waterNeeds': 'medium',
        'sunRequirement': 'full',
        'soilPH': {'min': 6.0, 'max': 7.5},
        'plantingDepth': 0.5,
        'germinationTemp': {'min': 50, 'max': 85},
        'transplantWeeksBefore': 4,
        'notes': 'Greens are also edible and cold-hardy.'
    },
    {
        'id': 'radish-1',
        'name': 'Radish',
        'scientificName': 'Raphanus sativus',
        'category': 'vegetable',
        'spacing': 2,
        'rowSpacing': 6,
        'daysToMaturity': 25,
        'frostTolerance': 'hardy',
        'winterHardy': False,
        'companionPlants': ['lettuce-1', 'spinach-1'],
        'incompatiblePlants': [],
        'waterNeeds': 'medium',
        'sunRequirement': 'full',
        'soilPH': {'min': 6.0, 'max': 7.0},
        'plantingDepth': 0.5,
        'germinationTemp': {'min': 45, 'max': 85},
        'transplantWeeksBefore': 0,
        'notes': 'Fast growing. Great for spring and fall.'
    },
    # Summer Crops
    {
        'id': 'tomato-1',
        'name': 'Tomato',
        'scientificName': 'Solanum lycopersicum',
        'category': 'vegetable',
        'spacing': 24,
        'rowSpacing': 36,
        'daysToMaturity': 75,
        'frostTolerance': 'very-tender',
        'winterHardy': False,
        'companionPlants': ['basil-1', 'carrot-1'],
        'incompatiblePlants': ['kale-1'],
        'waterNeeds': 'medium',
        'sunRequirement': 'full',
        'soilPH': {'min': 6.0, 'max': 6.8},
        'plantingDepth': 0.25,
        'germinationTemp': {'min': 60, 'max': 85},
        'transplantWeeksBefore': -2,
        'notes': 'Wait until all danger of frost has passed.'
    },
    {
        'id': 'pepper-1',
        'name': 'Pepper',
        'scientificName': 'Capsicum annuum',
        'category': 'vegetable',
        'spacing': 18,
        'rowSpacing': 24,
        'daysToMaturity': 70,
        'frostTolerance': 'very-tender',
        'winterHardy': False,
        'companionPlants': ['basil-1', 'onion-1'],
        'incompatiblePlants': [],
        'waterNeeds': 'medium',
        'sunRequirement': 'full',
        'soilPH': {'min': 6.0, 'max': 6.8},
        'plantingDepth': 0.25,
        'germinationTemp': {'min': 65, 'max': 85},
        'transplantWeeksBefore': -2,
        'notes': 'Very frost sensitive.'
    },
    # Alliums
    {
        'id': 'onion-1',
        'name': 'Onion',
        'scientificName': 'Allium cepa',
        'category': 'vegetable',
        'spacing': 4,
        'rowSpacing': 12,
        'daysToMaturity': 100,
        'frostTolerance': 'hardy',
        'winterHardy': True,
        'companionPlants': ['carrot-1', 'beet-1'],
        'incompatiblePlants': [],
        'waterNeeds': 'low',
        'sunRequirement': 'full',
        'soilPH': {'min': 6.0, 'max': 7.0},
        'plantingDepth': 1,
        'germinationTemp': {'min': 50, 'max': 95},
        'transplantWeeksBefore': 8,
        'notes': 'Can be planted as sets for overwintering.'
    },
    # Herbs
    {
        'id': 'basil-1',
        'name': 'Basil',
        'scientificName': 'Ocimum basilicum',
        'category': 'herb',
        'spacing': 10,
        'rowSpacing': 12,
        'daysToMaturity': 60,
        'frostTolerance': 'very-tender',
        'winterHardy': False,
        'companionPlants': ['tomato-1', 'pepper-1'],
        'incompatiblePlants': [],
        'waterNeeds': 'medium',
        'sunRequirement': 'full',
        'soilPH': {'min': 6.0, 'max': 7.5},
        'plantingDepth': 0.25,
        'germinationTemp': {'min': 70, 'max': 85},
        'transplantWeeksBefore': -1,
        'notes': 'Very frost sensitive.'
    },
    {
        'id': 'parsley-1',
        'name': 'Parsley',
        'scientificName': 'Petroselinum crispum',
        'category': 'herb',
        'spacing': 8,
        'rowSpacing': 12,
        'daysToMaturity': 70,
        'frostTolerance': 'hardy',
        'winterHardy': True,
        'companionPlants': ['tomato-1'],
        'incompatiblePlants': [],
        'waterNeeds': 'medium',
        'sunRequirement': 'partial',
        'soilPH': {'min': 6.0, 'max': 7.0},
        'plantingDepth': 0.25,
        'germinationTemp': {'min': 50, 'max': 80},
        'transplantWeeksBefore': 4,
        'notes': 'Slow to germinate. Overwinters well.'
    }
]

# Compost materials with C:N ratios
COMPOST_MATERIALS = {
    'grass-clippings': {'type': 'green', 'cnRatio': 20},
    'food-scraps': {'type': 'green', 'cnRatio': 15},
    'coffee-grounds': {'type': 'green', 'cnRatio': 20},
    'fresh-manure': {'type': 'green', 'cnRatio': 10},
    'hay-fresh': {'type': 'green', 'cnRatio': 15},
    'dried-leaves': {'type': 'brown', 'cnRatio': 60},
    'straw': {'type': 'brown', 'cnRatio': 80},
    'wood-chips': {'type': 'brown', 'cnRatio': 400},
    'cardboard': {'type': 'brown', 'cnRatio': 350},
    'paper': {'type': 'brown', 'cnRatio': 175},
    'sawdust': {'type': 'brown', 'cnRatio': 500}
}

def get_plant_by_id(plant_id):
    """Get plant details by ID"""
    for plant in PLANT_DATABASE:
        if plant['id'] == plant_id:
            return plant
    return None

def get_winter_hardy_plants():
    """Get all winter-hardy plants"""
    return [p for p in PLANT_DATABASE if p['winterHardy']]

def get_plants_by_category(category):
    """Get plants by category"""
    return [p for p in PLANT_DATABASE if p['category'] == category]
