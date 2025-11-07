"""
Clothing Items Database
Defines all available clothing items with their visual representations
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ClothingItem:
    """Represents a clothing item with visual and gameplay properties"""
    id: str
    name: str
    category: str  # 'underwear', 'tops', 'bottoms', 'dresses', 'outerwear', 'accessories'
    slot: str  # 'bra', 'panties', 'top', 'bottom', 'dress', 'shoes', 'jewelry', etc.
    image_path: str  # Relative path from /static/images/characters/{name}/
    description: str
    tags: List[str]  # e.g., ['revealing', 'formal', 'casual', 'sexy', 'modest']
    coverage: int  # 0-100, how much body is covered
    formality: int  # 0-100, casual to formal

    # Hypnosis relevance
    suggestibility_factor: float = 1.0  # Multiplier for suggestions related to this item


# ==================== UNDERWEAR ====================

UNDERWEAR_ITEMS = {
    # Bras
    'bra_standard_white': ClothingItem(
        id='bra_standard_white',
        name='White Cotton Bra',
        category='underwear',
        slot='bra',
        image_path='clothing/underwear/bra_standard_white.png',
        description='Simple, comfortable white cotton bra',
        tags=['modest', 'casual', 'comfortable'],
        coverage=40,
        formality=20
    ),
    'bra_lace_black': ClothingItem(
        id='bra_lace_black',
        name='Black Lace Bra',
        category='underwear',
        slot='bra',
        image_path='clothing/underwear/bra_lace_black.png',
        description='Elegant black lace bra',
        tags=['sexy', 'revealing', 'elegant'],
        coverage=30,
        formality=50
    ),
    'bra_sports': ClothingItem(
        id='bra_sports',
        name='Sports Bra',
        category='underwear',
        slot='bra',
        image_path='clothing/underwear/bra_sports.png',
        description='Athletic sports bra',
        tags=['athletic', 'casual', 'comfortable'],
        coverage=50,
        formality=10
    ),

    # Panties
    'panties_standard_white': ClothingItem(
        id='panties_standard_white',
        name='White Cotton Panties',
        category='underwear',
        slot='panties',
        image_path='clothing/underwear/panties_standard_white.png',
        description='Simple, comfortable white cotton panties',
        tags=['modest', 'casual', 'comfortable'],
        coverage=60,
        formality=20
    ),
    'panties_lace_black': ClothingItem(
        id='panties_lace_black',
        name='Black Lace Panties',
        category='underwear',
        slot='panties',
        image_path='clothing/underwear/panties_lace_black.png',
        description='Elegant black lace panties',
        tags=['sexy', 'revealing', 'elegant'],
        coverage=40,
        formality=50
    ),
    'panties_thong': ClothingItem(
        id='panties_thong',
        name='Thong',
        category='underwear',
        slot='panties',
        image_path='clothing/underwear/panties_thong.png',
        description='Minimal coverage thong',
        tags=['sexy', 'revealing', 'bold'],
        coverage=20,
        formality=40
    ),
}


# ==================== TOPS ====================

TOPS_ITEMS = {
    'blouse_white': ClothingItem(
        id='blouse_white',
        name='White Blouse',
        category='tops',
        slot='top',
        image_path='clothing/tops/blouse_white.png',
        description='Classic white button-up blouse',
        tags=['formal', 'professional', 'modest'],
        coverage=80,
        formality=80
    ),
    'blouse_sheer': ClothingItem(
        id='blouse_sheer',
        name='Sheer Blouse',
        category='tops',
        slot='top',
        image_path='clothing/tops/blouse_sheer.png',
        description='Semi-transparent blouse',
        tags=['revealing', 'sexy', 'bold'],
        coverage=50,
        formality=60
    ),
    't_shirt_casual': ClothingItem(
        id='t_shirt_casual',
        name='Casual T-Shirt',
        category='tops',
        slot='top',
        image_path='clothing/tops/t_shirt_casual.png',
        description='Comfortable casual t-shirt',
        tags=['casual', 'comfortable', 'modest'],
        coverage=70,
        formality=20
    ),
    'tank_top': ClothingItem(
        id='tank_top',
        name='Tank Top',
        category='tops',
        slot='top',
        image_path='clothing/tops/tank_top.png',
        description='Sleeveless tank top',
        tags=['casual', 'revealing', 'comfortable'],
        coverage=50,
        formality=15
    ),
    'crop_top': ClothingItem(
        id='crop_top',
        name='Crop Top',
        category='tops',
        slot='top',
        image_path='clothing/tops/crop_top.png',
        description='Midriff-revealing crop top',
        tags=['revealing', 'sexy', 'casual', 'bold'],
        coverage=40,
        formality=10
    ),
    'sweater_modest': ClothingItem(
        id='sweater_modest',
        name='Modest Sweater',
        category='tops',
        slot='top',
        image_path='clothing/tops/sweater_modest.png',
        description='Cozy, covering sweater',
        tags=['modest', 'comfortable', 'casual'],
        coverage=90,
        formality=40
    ),
}


# ==================== BOTTOMS ====================

BOTTOMS_ITEMS = {
    'skirt_pencil': ClothingItem(
        id='skirt_pencil',
        name='Pencil Skirt',
        category='bottoms',
        slot='bottom',
        image_path='clothing/bottoms/skirt_pencil.png',
        description='Professional knee-length pencil skirt',
        tags=['formal', 'professional', 'modest'],
        coverage=70,
        formality=80
    ),
    'skirt_mini': ClothingItem(
        id='skirt_mini',
        name='Mini Skirt',
        category='bottoms',
        slot='bottom',
        image_path='clothing/bottoms/skirt_mini.png',
        description='Short, thigh-revealing mini skirt',
        tags=['revealing', 'sexy', 'bold'],
        coverage=30,
        formality=30
    ),
    'pants_slacks': ClothingItem(
        id='pants_slacks',
        name='Dress Slacks',
        category='bottoms',
        slot='bottom',
        image_path='clothing/bottoms/pants_slacks.png',
        description='Professional dress pants',
        tags=['formal', 'professional', 'modest'],
        coverage=85,
        formality=85
    ),
    'jeans_casual': ClothingItem(
        id='jeans_casual',
        name='Casual Jeans',
        category='bottoms',
        slot='bottom',
        image_path='clothing/bottoms/jeans_casual.png',
        description='Comfortable casual jeans',
        tags=['casual', 'comfortable', 'modest'],
        coverage=80,
        formality=30
    ),
    'shorts_athletic': ClothingItem(
        id='shorts_athletic',
        name='Athletic Shorts',
        category='bottoms',
        slot='bottom',
        image_path='clothing/bottoms/shorts_athletic.png',
        description='Short athletic shorts',
        tags=['athletic', 'revealing', 'casual'],
        coverage=40,
        formality=10
    ),
    'leggings_yoga': ClothingItem(
        id='leggings_yoga',
        name='Yoga Leggings',
        category='bottoms',
        slot='bottom',
        image_path='clothing/bottoms/leggings_yoga.png',
        description='Form-fitting yoga leggings',
        tags=['athletic', 'revealing', 'casual', 'comfortable'],
        coverage=75,
        formality=15
    ),
}


# ==================== DRESSES ====================

DRESSES_ITEMS = {
    'dress_modest_floral': ClothingItem(
        id='dress_modest_floral',
        name='Floral Dress',
        category='dresses',
        slot='dress',
        image_path='clothing/dresses/dress_modest_floral.png',
        description='Modest floral print dress',
        tags=['modest', 'casual', 'feminine'],
        coverage=80,
        formality=60
    ),
    'dress_cocktail': ClothingItem(
        id='dress_cocktail',
        name='Cocktail Dress',
        category='dresses',
        slot='dress',
        image_path='clothing/dresses/dress_cocktail.png',
        description='Elegant cocktail dress',
        tags=['formal', 'elegant', 'sexy'],
        coverage=60,
        formality=85
    ),
    'dress_sundress': ClothingItem(
        id='dress_sundress',
        name='Sundress',
        category='dresses',
        slot='dress',
        image_path='clothing/dresses/dress_sundress.png',
        description='Light, casual sundress',
        tags=['casual', 'comfortable', 'feminine'],
        coverage=65,
        formality=35
    ),
}


# ==================== ACCESSORIES ====================

ACCESSORIES_ITEMS = {
    'jewelry_pearls': ClothingItem(
        id='jewelry_pearls',
        name='Pearl Necklace',
        category='accessories',
        slot='necklace',
        image_path='accessories/jewelry_pearls.png',
        description='Classic pearl necklace',
        tags=['formal', 'elegant', 'traditional'],
        coverage=0,
        formality=90
    ),
    'jewelry_choker': ClothingItem(
        id='jewelry_choker',
        name='Choker',
        category='accessories',
        slot='necklace',
        image_path='accessories/jewelry_choker.png',
        description='Trendy choker necklace',
        tags=['sexy', 'bold', 'modern'],
        coverage=0,
        formality=40
    ),
    'glasses_reading': ClothingItem(
        id='glasses_reading',
        name='Reading Glasses',
        category='accessories',
        slot='glasses',
        image_path='accessories/glasses_reading.png',
        description='Practical reading glasses',
        tags=['professional', 'practical'],
        coverage=0,
        formality=60
    ),
}


# ==================== EXPRESSIONS ====================

EXPRESSIONS = {
    'neutral': 'expressions/neutral.png',
    'happy': 'expressions/happy.png',
    'sad': 'expressions/sad.png',
    'angry': 'expressions/angry.png',
    'surprised': 'expressions/surprised.png',
    'aroused': 'expressions/aroused.png',
    'embarrassed': 'expressions/embarrassed.png',
    'confused': 'expressions/confused.png',
    'confident': 'expressions/confident.png',
}


# ==================== COMBINED DATABASE ====================

ALL_CLOTHING_ITEMS = {
    **UNDERWEAR_ITEMS,
    **TOPS_ITEMS,
    **BOTTOMS_ITEMS,
    **DRESSES_ITEMS,
    **ACCESSORIES_ITEMS,
}


# ==================== CHARACTER OUTFITS ====================

# Default starting outfits for each character
DEFAULT_OUTFITS = {
    'Ruth': {
        'bra': 'bra_standard_white',
        'panties': 'panties_standard_white',
        'top': 'blouse_white',
        'bottom': 'skirt_pencil',
        'necklace': 'jewelry_pearls',
        'expression': 'neutral'
    },
    'Tom': {
        # For now, Tom uses generic clothing description
        'expression': 'neutral'
    },
    'Lisa': {
        'bra': 'bra_standard_white',
        'panties': 'panties_standard_white',
        'top': 't_shirt_casual',
        'bottom': 'jeans_casual',
        'expression': 'neutral'
    },
    'Marcus': {
        # Athletic outfit
        'expression': 'confident'
    },
    'Sophie': {
        'bra': 'bra_standard_white',
        'panties': 'panties_standard_white',
        'top': 'blouse_white',
        'bottom': 'pants_slacks',
        'necklace': 'glasses_reading',
        'expression': 'neutral'
    },
    'Rachel': {
        'bra': 'bra_standard_white',
        'panties': 'panties_standard_white',
        'top': 't_shirt_casual',
        'bottom': 'jeans_casual',
        'expression': 'happy'
    },
    'James': {
        'expression': 'neutral'
    },
}


def get_clothing_item(item_id: str) -> Optional[ClothingItem]:
    """Get a clothing item by ID"""
    return ALL_CLOTHING_ITEMS.get(item_id)


def get_items_by_category(category: str) -> dict:
    """Get all items in a specific category"""
    return {k: v for k, v in ALL_CLOTHING_ITEMS.items() if v.category == category}


def get_items_by_slot(slot: str) -> dict:
    """Get all items for a specific slot"""
    return {k: v for k, v in ALL_CLOTHING_ITEMS.items() if v.slot == slot}


def get_items_by_tag(tag: str) -> dict:
    """Get all items with a specific tag"""
    return {k: v for k, v in ALL_CLOTHING_ITEMS.items() if tag in v.tags}
