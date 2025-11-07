"""
Configuration management for Family Dynamics RPG
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API Configuration
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'

# Default API key (fallback if character-specific key not found)
DEFAULT_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
DEFAULT_MODEL = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')

# GM/Narrator System - Oversees game logic, triggers, and consequences
GM_API_KEY = os.getenv('GM_API_KEY', DEFAULT_API_KEY)
GM_MODEL = os.getenv('GM_MODEL', 'anthropic/claude-3.5-sonnet')

# Per-Character API Configuration
# Format: 'CharacterName_API_KEY' and 'CharacterName_MODEL'
CHARACTER_API_KEYS = {
    'Ruth': os.getenv('RUTH_API_KEY', DEFAULT_API_KEY),
    'Melanie': os.getenv('MELANIE_API_KEY', DEFAULT_API_KEY),
    'Tom': os.getenv('TOM_API_KEY', DEFAULT_API_KEY),
    'Dawn': os.getenv('DAWN_API_KEY', DEFAULT_API_KEY),
    'Vanessa': os.getenv('VANESSA_API_KEY', DEFAULT_API_KEY),
    'Derek': os.getenv('DEREK_API_KEY', DEFAULT_API_KEY),
    'Karen': os.getenv('KAREN_API_KEY', DEFAULT_API_KEY),
}

CHARACTER_MODELS = {
    'Ruth': os.getenv('RUTH_MODEL', 'anthropic/claude-3.5-sonnet'),
    'Melanie': os.getenv('MELANIE_MODEL', 'anthropic/claude-3.5-sonnet'),
    'Tom': os.getenv('TOM_MODEL', 'openai/gpt-4o-mini'),  # Simpler character, cheaper model
    'Dawn': os.getenv('DAWN_MODEL', 'anthropic/claude-3.5-sonnet'),
    'Vanessa': os.getenv('VANESSA_MODEL', 'openai/gpt-4o-mini'),
    'Derek': os.getenv('DEREK_MODEL', 'openai/gpt-4o-mini'),
    'Karen': os.getenv('KAREN_MODEL', 'openai/gpt-4o-mini'),
}

# Optional OpenRouter headers
SITE_URL = os.getenv('SITE_URL', '')
SITE_NAME = os.getenv('SITE_NAME', 'Family Dynamics RPG')

# Game Configuration
STARTING_SP = 3
MAX_RAPPORT = 20
MIN_RAPPORT = 0

# Memory System Configuration
MAX_MEMORIES_PER_CHARACTER = int(os.getenv('MAX_MEMORIES_PER_CHARACTER', 100))  # Max stored memories (increased from 50)
MEMORY_RETRIEVAL_COUNT = int(os.getenv('MEMORY_RETRIEVAL_COUNT', 15))           # How many memories to retrieve for context (increased from 10)
MEMORY_IMPORTANCE_THRESHOLD = int(os.getenv('MEMORY_IMPORTANCE_THRESHOLD', 3))  # Minimum importance (1-10) to auto-save
MEMORY_CONSOLIDATION_ENABLED = os.getenv('MEMORY_CONSOLIDATION_ENABLED', 'true').lower() == 'true'  # Auto-consolidate similar memories
MEMORY_CONSOLIDATION_THRESHOLD = int(os.getenv('MEMORY_CONSOLIDATION_THRESHOLD', 7))  # Similarity threshold for consolidation

# Conversation History Configuration
CONVERSATION_HISTORY_LENGTH = int(os.getenv('CONVERSATION_HISTORY_LENGTH', 30))  # How many messages to keep in history (increased from 10)
USE_CONVERSATION_SUMMARY = os.getenv('USE_CONVERSATION_SUMMARY', 'false').lower() == 'true'  # Use summaries for very long conversations

# Save file location
SAVE_FILE = 'game_save.json'
