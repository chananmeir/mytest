"""
Configuration management for Family Dynamics RPG
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'

# Optional OpenRouter headers
SITE_URL = os.getenv('SITE_URL', '')
SITE_NAME = os.getenv('SITE_NAME', 'Family Dynamics RPG')

# Game Configuration
STARTING_SP = 3
MAX_RAPPORT = 20
MIN_RAPPORT = 0

# Save file location
SAVE_FILE = 'game_save.json'
