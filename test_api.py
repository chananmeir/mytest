#!/usr/bin/env python3
"""Quick test for the saved games API endpoint"""
import json
from app import app

# Create test client
with app.test_client() as client:
    # Test the API endpoint
    response = client.get('/api/saved-games')

    print("API Response Status:", response.status_code)
    print("\nAPI Response Data:")

    if response.status_code == 200:
        data = json.loads(response.data)
        print(json.dumps(data, indent=2))

        if data['success']:
            print(f"\n✓ Successfully found {data['count']} saved game(s)")
            for game in data['games']:
                print(f"\n  Game: {game['file_name']}")
                print(f"  - Last Modified: {game['last_modified_display']}")
                print(f"  - Game Time: {game['game_time']}")
                print(f"  - Player SP: {game['player']['sp']}")
                print(f"  - Characters: {len(game['characters'])}")
        else:
            print("\n✗ API returned success=False")
    else:
        print(f"\n✗ API request failed with status {response.status_code}")
