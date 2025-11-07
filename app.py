"""
Family Dynamics RPG - Web Application
Flask-based web interface for the hypnosis RPG game
"""
from flask import Flask, render_template, request, session, jsonify, redirect, url_for
import os
import json
from datetime import datetime
from models.game_state import GameState
from systems.llm_handler import LLMHandler
from systems.hypnosis import HypnosisSystem
from systems.game_master import GameMaster
from systems.memory import MemorySystem
from systems.hypnosis_knowledge import HYPNOSIS_TECHNIQUES, LEARNING_RESOURCES
import config

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'

# Global instances
llm_handler = LLMHandler()
hypnosis_system = HypnosisSystem()
game_master = GameMaster()
memory_system = MemorySystem()


def get_game_state():
    """Get or create game state from session"""
    if 'game_state_data' not in session:
        # Create new game
        game_state = GameState()
        session['game_state_data'] = game_state.to_dict()
        return game_state

    # Reconstruct from session data
    game_state = GameState()

    # Save to temp file and load (reuse existing load logic)
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(session['game_state_data'], f)
        temp_file = f.name

    try:
        game_state.load_game(temp_file)
        os.unlink(temp_file)
    except:
        # If load fails, return fresh game state
        pass

    return game_state


def save_game_state(game_state):
    """Save game state to session"""
    session['game_state_data'] = game_state.to_dict()
    session.modified = True


@app.route('/')
def index():
    """Main menu / home page"""
    return render_template('index.html')


@app.route('/new-game', methods=['POST'])
def new_game():
    """Start a new game"""
    # Clear existing session
    session.clear()

    # Create new game state
    game_state = GameState()
    session['game_state_id'] = id(game_state)
    session['game_state_data'] = game_state.to_dict()
    session['current_scene'] = 'family_dinner'

    return jsonify({'success': True, 'redirect': '/game'})


@app.route('/load-game', methods=['POST'])
def load_game():
    """Load a saved game"""
    try:
        game_state = GameState()
        if game_state.load_game():
            session['game_state_id'] = id(game_state)
            session['game_state_data'] = game_state.to_dict()
            session['current_scene'] = 'family_dinner'
            return jsonify({'success': True, 'redirect': '/game'})
        else:
            return jsonify({'success': False, 'error': 'No saved game found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/game')
def game():
    """Main game interface"""
    game_state = get_game_state()

    # Get current scene
    current_scene = session.get('current_scene', 'family_dinner')

    return render_template('game.html',
                         game_state=game_state,
                         current_scene=current_scene)


@app.route('/api/game-state')
def api_game_state():
    """Get current game state as JSON"""
    game_state = get_game_state()

    return jsonify({
        'player': {
            'suggestion_points': game_state.player.suggestion_points,
            'skill_level': game_state.player.hypnosis_knowledge.skill_level,
            'techniques_mastered': len(game_state.player.hypnosis_knowledge.known_techniques),
            'total_techniques': 11
        },
        'characters': [
            {
                'name': char.name,
                'rapport': char.rapport,
                'emotional_state': char.emotional_state,
                'active_phs': len(char.active_phs),
                'clothing': char.clothing
            }
            for char in game_state.characters.values()
        ],
        'scene': session.get('current_scene', 'family_dinner')
    })


@app.route('/api/ambient-events')
def api_ambient_events():
    """Get ambient events and character activities"""
    import random
    from systems.time_system import get_character_schedule, is_character_available

    game_state = get_game_state()
    current_period = game_state.game_time.period

    # Get schedule-based activities first
    schedule_activities = {}
    for char_name in game_state.characters.keys():
        schedule = get_character_schedule(char_name, current_period)
        schedule_activities[char_name] = schedule['activity']

    # Define additional possible activities for each character (time-independent)
    extra_activities = {
        'Ruth': ['Adjusting her hair', 'Looking at old photos', 'Checking her phone'],
        'Tom': ['Checking his phone', 'Looking out the window', 'Organizing papers'],
        'Lisa': ['Texting friends', 'Scrolling social media', 'Doodling in notebook'],
        'Marcus': ['Checking his reflection', 'Flexing subtly', 'Checking fitness app'],
        'Sophie': ['Adjusting her glasses', 'Thinking deeply', 'Reviewing documents'],
        'Rachel': ['Making silly faces', 'Drawing', 'Telling jokes'],
        'James': ['Daydreaming', 'Yawning', 'Snacking']
    }

    # Define ambient dialogue for each character
    ambient_dialogue = {
        'Ruth': [
            '*sighs while setting plates* "Another family dinner..."',
            '*mutters* "I hope everyone behaves tonight."',
            '*checks watch* "Tom should be home by now."',
            '*quietly* "So much to do, so little time."'
        ],
        'Tom': [
            '*without looking up* "Hmm, interesting article here."',
            '*clears throat* "When\'s dinner ready?"',
            '*stretches* "Long day at work."',
            '*to himself* "Market\'s looking good."'
        ],
        'Lisa': [
            '*giggles at phone* "OMG, this is hilarious!"',
            '*rolls eyes* "This is so boring."',
            '*to herself* "I can\'t wait to go out later."',
            '*sighs dramatically* "Why do we have to do this?"'
        ],
        'Marcus': [
            '*flexes arm casually* "Did arm day this morning."',
            '*confidently* "Looking good, feeling good."',
            '*to mirror* "Yeah, that\'s right."',
            '*stretches* "Gotta maintain the physique."'
        ],
        'Sophie': [
            '*thoughtfully* "The geopolitical implications are fascinating..."',
            '*adjusts glasses* "According to my research..."',
            '*mutters* "If only they understood economics."',
            '*to herself* "These statistics are concerning."'
        ],
        'Rachel': [
            '*sings quietly* "La la la la!"',
            '*giggles* "That cloud looks like a bunny!"',
            '*excitedly* "Can we have dessert?!"',
            '*bounces* "This is fun! Well, kinda!"'
        ],
        'James': [
            '*yawns* "I\'m kinda tired..."',
            '*distracted* "What? Oh, nothing."',
            '*quietly* "I wonder what\'s on TV later."',
            '*to himself* "Maybe I\'ll just stay in my room."'
        ]
    }

    # Generate random event
    event_type = random.choice(['activity', 'dialogue', 'interaction', 'none', 'none'])

    result = {'type': event_type}

    if event_type == 'activity':
        # Random character changes activity
        char_name = random.choice(list(game_state.characters.keys()))

        # 60% chance to show schedule-based activity, 40% extra activity
        if random.random() < 0.6:
            new_activity = schedule_activities.get(char_name, 'Doing something')
        else:
            new_activity = random.choice(extra_activities.get(char_name, ['Sitting quietly']))

        result['character'] = char_name
        result['activity'] = new_activity

        # Include location from schedule
        schedule = get_character_schedule(char_name, current_period)
        result['location'] = schedule['location']
        result['message'] = f"{char_name} is {new_activity.lower()} in the {schedule['location'].lower()}"

    elif event_type == 'dialogue':
        # Random character says something
        char_name = random.choice(list(game_state.characters.keys()))
        char = game_state.characters[char_name]
        dialogue = random.choice(ambient_dialogue.get(char_name, ['*looks around*']))
        result['character'] = char_name
        result['dialogue'] = dialogue
        result['message'] = f"{char_name}: {dialogue}"

    elif event_type == 'interaction':
        # Two characters interact - use LLM for realistic conversations
        from systems.character_interactions import generate_character_conversation_llm, record_interaction
        from systems.location_system import get_character_location

        # Rate limiting: Only generate LLM conversation once per minute max
        last_llm_time = session.get('last_background_conversation_time', 0)
        current_time = datetime.now().timestamp()
        time_since_last = current_time - last_llm_time

        # Get characters at same location (excluding any character player is talking to)
        current_talking_to = session.get('selected_character', None)
        available_chars = []

        # Group characters by location
        location_groups = {}
        for char_name in game_state.characters.keys():
            if char_name == current_talking_to:
                continue  # Skip character player is talking to

            char_location = get_character_location(char_name, current_period)
            if char_location not in location_groups:
                location_groups[char_location] = []
            location_groups[char_location].append(char_name)

        # Find locations with 2+ characters
        valid_locations = [loc for loc, chars in location_groups.items() if len(chars) >= 2]

        if valid_locations and time_since_last >= 60:  # At least 1 minute since last LLM call
            # Pick a random location with multiple characters
            chosen_location = random.choice(valid_locations)
            chars = random.sample(location_groups[chosen_location], 2)

            char1 = game_state.characters[chars[0]]
            char2 = game_state.characters[chars[1]]

            # Try to generate LLM conversation
            conversation = generate_character_conversation_llm(
                char1, char2, chosen_location, llm_handler
            )

            if conversation:
                # Record the interaction
                record_interaction(
                    char1, char2,
                    conversation['type'],
                    conversation['summary'],
                    chosen_location
                )

                # Save the updated game state
                save_game_state(game_state)

                # Update session timestamp
                session['last_background_conversation_time'] = current_time

                result['characters'] = chars
                result['location'] = chosen_location
                result['message'] = f"*In the {chosen_location.replace('_', ' ')}: {conversation['summary']}*"
                result['conversation_type'] = conversation['type']
            else:
                # Fallback to simple interaction
                chars = random.sample(list(game_state.characters.keys()), 2)
                interactions = [
                    f"{chars[0]} glances at {chars[1]}",
                    f"{chars[1]} nods at {chars[0]}",
                    f"{chars[0]} and {chars[1]} exchange a look"
                ]
                result['characters'] = chars
                result['message'] = random.choice(interactions)
        else:
            # No valid locations or rate limited - use simple interaction
            chars = random.sample(list(game_state.characters.keys()), 2)
            interactions = [
                f"{chars[0]} glances at {chars[1]}",
                f"{chars[1]} nods at {chars[0]}",
                f"{chars[0]} and {chars[1]} exchange a look",
                f"{chars[1]} whispers something to {chars[0]}",
                f"{chars[0]} smiles at {chars[1]}"
            ]
            result['characters'] = chars
            result['message'] = random.choice(interactions)

    return jsonify(result)


@app.route('/api/player-profile')
def api_player_profile():
    """Get detailed player profile"""
    game_state = get_game_state()
    player = game_state.player
    knowledge = player.hypnosis_knowledge

    # Get techniques by status
    mastered_techniques = []
    learning_techniques = []

    for tech_id, technique in HYPNOSIS_TECHNIQUES.items():
        if knowledge.knows_technique(tech_id):
            mastered_techniques.append({
                'id': tech_id,
                'name': technique.name,
                'category': technique.category,
                'sp_reduction': technique.sp_cost_reduction,
                'success_bonus': technique.success_rate_bonus
            })
        elif tech_id in knowledge.learning_progress:
            learning_techniques.append({
                'id': tech_id,
                'name': technique.name,
                'progress': knowledge.learning_progress[tech_id]
            })

    sp_reduction, success_bonus = knowledge.get_total_bonuses()

    return jsonify({
        'name': player.name,
        'age': player.age,
        'occupation': player.occupation,
        'clothing': player.clothing,
        'suggestion_points': player.suggestion_points,
        'total_sp_earned': player.total_sp_earned,
        'skill_level': knowledge.skill_level,
        'techniques_mastered': len(knowledge.known_techniques),
        'total_techniques': 11,
        'mastered_techniques': mastered_techniques,
        'learning_techniques': learning_techniques,
        'books_read': len(knowledge.books_read),
        'practice_sessions': knowledge.practice_sessions,
        'total_sp_reduction': sp_reduction,
        'total_success_bonus': success_bonus,
        'scenes_completed': player.scenes_completed
    })


@app.route('/api/talk', methods=['POST'])
def api_talk():
    """Handle character conversation"""
    from systems.location_system import get_location_context_for_llm

    data = request.json
    character_name = data.get('character')
    player_message = data.get('message')

    # Track which character player is talking to (for ambient events)
    session['selected_character'] = character_name

    game_state = get_game_state()
    char = game_state.get_character(character_name)

    if not char:
        return jsonify({'error': 'Character not found'}), 404

    # Get current location context
    current_location = game_state.get_current_location()
    location_context = get_location_context_for_llm(current_location)

    # Get LLM response with location context
    response = llm_handler.get_character_response(
        char,
        player_message,
        scene_context="Family gathering",
        location_context=location_context,
        record_memory=True
    )

    # Analyze interaction with GM
    analysis = game_master.analyze_conversation_impact(
        character=char,
        player_message=player_message,
        character_response=response,
        scene_context="Family dinner"
    )

    # Apply changes
    changes = []
    if analysis['rapport_change'] != 0:
        if analysis['rapport_change'] > 0:
            message = hypnosis_system.build_rapport(
                game_state,
                character_name,
                abs(analysis['rapport_change']),
                analysis['reasoning']
            )
        else:
            char.reduce_rapport(abs(analysis['rapport_change']))
            message = f"Rapport decreased: {char.rapport}/20"
        changes.append({'type': 'rapport', 'message': message})

    if analysis['new_emotional_state'] != char.emotional_state:
        message = hypnosis_system.change_emotional_state(
            game_state,
            character_name,
            analysis['new_emotional_state'],
            analysis['reasoning']
        )
        changes.append({'type': 'emotional_state', 'message': message})

    save_game_state(game_state)

    return jsonify({
        'response': response,
        'changes': changes,
        'character_state': {
            'rapport': char.rapport,
            'emotional_state': char.emotional_state
        }
    })


@app.route('/api/characters')
def api_characters():
    """Get characters at player's current location"""
    from systems.time_system import get_character_schedule
    from systems.location_system import get_character_location

    game_state = get_game_state()
    current_period = game_state.game_time.period
    player_location = game_state.player.current_location

    # Get only characters at player's location
    characters_here = game_state.get_characters_at_location()

    characters = []
    for char in characters_here.values():
        schedule = get_character_schedule(char.name, current_period)

        characters.append({
            'name': char.name,
            'age': char.age,
            'gender': char.gender,
            'occupation': char.occupation,
            'personality': char.personality,
            'rapport': char.rapport,
            'emotional_state': char.emotional_state,
            'resistance': char.resistance,
            'clothing': char.clothing,
            'active_phs': len(char.active_phs),
            'max_phs': char.max_phs,
            'current_location': schedule['location'],
            'current_activity': schedule['activity'],
            'outfit': char.outfit
        })

    return jsonify({
        'characters': characters,
        'location': game_state.get_current_location().name
    })


@app.route('/api/character/<name>')
def api_character(name):
    """Get detailed character info"""
    game_state = get_game_state()
    char = game_state.get_character(name)

    if not char:
        return jsonify({'error': 'Character not found'}), 404

    # Get PHS details
    phs_list = []
    for phs in char.active_phs:
        chance = phs.calculate_activation_chance()
        phs_list.append({
            'trigger': phs.trigger,
            'response': phs.response,
            'strength': phs.strength,
            'reinforcements': phs.reinforcements,
            'activation_chance': chance
        })

    # Get memories
    memories = []
    if hasattr(char, 'memories'):
        for mem in char.memories:
            memories.append({
                'content': mem.content,
                'type': mem.memory_type,
                'importance': mem.importance,
                'emotional_context': mem.emotional_context,
                'timestamp': mem.timestamp
            })

    return jsonify({
        'name': char.name,
        'age': char.age,
        'gender': char.gender,
        'occupation': char.occupation,
        'personality': char.personality,
        'rapport': char.rapport,
        'emotional_state': char.emotional_state,
        'resistance': char.resistance,
        'clothing': char.clothing,
        'clothing_meaning': char.clothing_meaning,
        'outfit': char.outfit,
        'active_phs': phs_list,
        'memories': memories,
        'relationships': char.relationships,
        'character_interactions': char.character_interactions
    })


@app.route('/api/skill-tree')
def api_skill_tree():
    """Get skill tree data"""
    game_state = get_game_state()
    knowledge = game_state.player.hypnosis_knowledge

    techniques = {}
    for tech_id, technique in HYPNOSIS_TECHNIQUES.items():
        is_known = knowledge.knows_technique(tech_id)
        progress = knowledge.learning_progress.get(tech_id, 0)
        can_learn, reason = knowledge.can_learn_technique(tech_id)

        status = 'mastered' if is_known else 'learning' if progress > 0 else 'available' if can_learn else 'locked'

        techniques[tech_id] = {
            'name': technique.name,
            'description': technique.description,
            'category': technique.category,
            'prerequisites': technique.prerequisites,
            'sp_cost_reduction': technique.sp_cost_reduction,
            'success_rate_bonus': technique.success_rate_bonus,
            'status': status,
            'progress': progress,
            'can_learn_reason': reason
        }

    sp_reduction, success_bonus = knowledge.get_total_bonuses()

    return jsonify({
        'techniques': techniques,
        'skill_level': knowledge.skill_level,
        'techniques_mastered': len(knowledge.known_techniques),
        'total_sp_reduction': sp_reduction,
        'total_success_bonus': success_bonus
    })


@app.route('/api/study', methods=['POST'])
def api_study():
    """Handle studying hypnosis"""
    data = request.json
    action = data.get('action')  # 'read_book', 'practice', 'research'

    game_state = get_game_state()
    knowledge = game_state.player.hypnosis_knowledge

    result = {'success': False}

    if action == 'read_book':
        book_id = data.get('book_id')
        if book_id in LEARNING_RESOURCES:
            book = LEARNING_RESOURCES[book_id]
            learned = []
            progress_made = []

            for tech_name in book['teaches']:
                if tech_name not in knowledge.known_techniques:
                    progress = knowledge.add_learning_progress(tech_name, book['progress_per_read'])

                    if progress >= 100:
                        learned.append(HYPNOSIS_TECHNIQUES[tech_name].name)
                        game_state.add_sp(2, "Mastered technique")
                    else:
                        progress_made.append({
                            'technique': HYPNOSIS_TECHNIQUES[tech_name].name,
                            'progress': progress
                        })

            if book_id not in knowledge.books_read:
                knowledge.books_read.append(book_id)

            if progress_made or learned:
                game_state.add_sp(1, "Studied hypnosis")

            result = {
                'success': True,
                'learned': learned,
                'progress_made': progress_made,
                'book_title': book['title']
            }

    elif action == 'practice':
        tech_id = data.get('technique_id')
        if tech_id in knowledge.learning_progress:
            tech = HYPNOSIS_TECHNIQUES[tech_id]
            progress_gain = 15
            final_progress = knowledge.add_learning_progress(tech_id, progress_gain)
            knowledge.practice_sessions += 1

            if final_progress >= 100:
                game_state.add_sp(2, "Mastered technique through practice")
                result = {
                    'success': True,
                    'mastered': tech.name,
                    'progress': 100
                }
            else:
                game_state.add_sp(1, "Practiced hypnosis")
                result = {
                    'success': True,
                    'progress': final_progress,
                    'technique': tech.name
                }

    elif action == 'research':
        available = knowledge.get_available_techniques()
        if available:
            import random
            tech = random.choice(available)
            tech_id = [k for k, v in HYPNOSIS_TECHNIQUES.items() if v == tech][0]

            progress_gain = 10
            final_progress = knowledge.add_learning_progress(tech_id, progress_gain)

            if final_progress >= 100:
                game_state.add_sp(2, "Learned technique through research")
                result = {
                    'success': True,
                    'mastered': tech.name,
                    'progress': 100
                }
            else:
                game_state.add_sp(1, "Researched hypnosis")
                result = {
                    'success': True,
                    'progress': final_progress,
                    'technique': tech.name
                }
        else:
            result = {'success': False, 'error': 'No techniques available to research'}

    save_game_state(game_state)
    return jsonify(result)


@app.route('/api/plant-suggestion', methods=['POST'])
def api_plant_suggestion():
    """Plant a post-hypnotic suggestion"""
    data = request.json
    character_name = data.get('character')
    suggestion_type = data.get('type')  # 'emotional_nudge', 'behavioral_prompt', 'strong_anchor'
    trigger = data.get('trigger')
    response_text = data.get('response')
    sp_cost = data.get('sp_cost', None)

    game_state = get_game_state()

    success = False
    message = ""

    if suggestion_type == 'emotional_nudge':
        success, message = hypnosis_system.plant_emotional_nudge(
            game_state, character_name, trigger, response_text
        )
    elif suggestion_type == 'behavioral_prompt':
        success, message = hypnosis_system.plant_behavioral_prompt(
            game_state, character_name, trigger, response_text
        )
    elif suggestion_type == 'strong_anchor':
        success, message = hypnosis_system.plant_strong_anchor(
            game_state, character_name, trigger, response_text, sp_cost
        )

    save_game_state(game_state)

    return jsonify({
        'success': success,
        'message': message
    })


@app.route('/api/save-game', methods=['POST'])
def api_save_game():
    """Save the game"""
    game_state = get_game_state()

    if game_state.save_game():
        return jsonify({'success': True, 'message': 'Game saved successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Failed to save game'})


@app.route('/api/add-character', methods=['POST'])
def api_add_character():
    """Add a new character to the game"""
    data = request.json

    game_state = get_game_state()

    # Validate required fields
    required = ['name', 'age', 'occupation', 'personality', 'resistance']
    for field in required:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

    # Check if character already exists
    if data['name'] in game_state.characters:
        return jsonify({'success': False, 'error': f'Character {data["name"]} already exists'}), 400

    # Create new character
    from models.character import Character

    new_character = Character(
        name=data['name'],
        age=int(data['age']),
        gender=data.get('gender', 'male'),  # Default to male if not provided
        occupation=data['occupation'],
        clothing=data.get('clothing', 'Casual clothing'),
        clothing_meaning=data.get('clothing_meaning', ''),
        personality=data['personality'],
        resistance=int(data['resistance']),
        rapport=0,
        emotional_state='neutral'
    )

    # Add to game state
    game_state.characters[data['name']] = new_character

    # Save updated game state
    save_game_state(game_state)

    return jsonify({
        'success': True,
        'message': f'{data["name"]} has been added to the family!',
        'character': {
            'name': new_character.name,
            'age': new_character.age,
            'occupation': new_character.occupation,
            'personality': new_character.personality,
            'resistance': new_character.resistance
        }
    })


@app.route('/api/record-interaction', methods=['POST'])
def api_record_interaction():
    """Record an interaction between two characters"""
    from systems.character_interactions import record_interaction

    data = request.json
    game_state = get_game_state()

    # Validate required fields
    char1_name = data.get('character1')
    char2_name = data.get('character2')
    interaction_type = data.get('type', 'conversation')
    summary = data.get('summary')

    if not all([char1_name, char2_name, summary]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    # Get characters
    char1 = game_state.get_character(char1_name)
    char2 = game_state.get_character(char2_name)

    if not char1 or not char2:
        return jsonify({'success': False, 'error': 'Character not found'}), 404

    # Record the interaction
    location = data.get('location', game_state.get_current_location().name)
    record_interaction(char1, char2, interaction_type, summary, location)

    # Save updated game state
    save_game_state(game_state)

    return jsonify({
        'success': True,
        'message': f'Recorded interaction between {char1_name} and {char2_name}',
        'new_relationship_scores': {
            f'{char1_name}_to_{char2_name}': char1.relationships.get(char2_name, 5),
            f'{char2_name}_to_{char1_name}': char2.relationships.get(char1_name, 5)
        }
    })


@app.route('/api/books')
def api_books():
    """Get available books"""
    game_state = get_game_state()
    knowledge = game_state.player.hypnosis_knowledge

    books = []
    for book_id, book in LEARNING_RESOURCES.items():
        teaches_list = []
        teaches_something_new = False

        for tech_id in book['teaches']:
            tech = HYPNOSIS_TECHNIQUES[tech_id]
            is_known = knowledge.knows_technique(tech_id)
            teaches_list.append({
                'name': tech.name,
                'known': is_known
            })
            if not is_known:
                teaches_something_new = True

        books.append({
            'id': book_id,
            'title': book['title'],
            'description': book['description'],
            'teaches': teaches_list,
            'location': book['location'],
            'already_read': book_id in knowledge.books_read,
            'teaches_something_new': teaches_something_new
        })

    return jsonify({'books': books})


@app.route('/api/current-time')
def api_current_time():
    """Get current game time"""
    game_state = get_game_state()

    return jsonify({
        'time': game_state.game_time.get_formatted_time(),
        'date': game_state.game_time.get_formatted_date(),
        'period': game_state.game_time.period.capitalize(),
        'day_name': game_state.game_time.day_name,
        'hour': game_state.game_time.hour,
        'minute': game_state.game_time.minute,
        'is_weekend': game_state.game_time.is_weekend
    })


@app.route('/api/advance-time', methods=['POST'])
def api_advance_time():
    """Advance game time by specified minutes"""
    game_state = get_game_state()
    data = request.json

    minutes = data.get('minutes', 15)

    # Advance time
    events = game_state.game_time.advance_minutes(minutes)

    # Save the updated game state
    save_game_state(game_state)

    # Prepare response
    response = {
        'success': True,
        'time': game_state.game_time.get_formatted_time(),
        'date': game_state.game_time.get_formatted_date(),
        'period': game_state.game_time.period.capitalize(),
        'events': events,
        'messages': []
    }

    # Add event messages
    if events['messages']:
        response['messages'] = events['messages']

    # Check if any characters' schedules changed
    if events['new_period'] or events['new_day']:
        schedule_updates = []
        for char_name in game_state.characters.keys():
            from systems.time_system import get_character_schedule
            schedule = get_character_schedule(char_name, game_state.game_time.period)
            schedule_updates.append({
                'character': char_name,
                'location': schedule['location'],
                'activity': schedule['activity'],
                'mood': schedule['mood_modifier']
            })
        response['schedule_updates'] = schedule_updates

    return jsonify(response)


@app.route('/api/locations')
def api_locations():
    """Get all available locations with their current status"""
    from systems.location_system import ALL_LOCATIONS, get_characters_at_location

    game_state = get_game_state()
    current_hour = game_state.game_time.hour
    current_period = game_state.game_time.period

    locations = []
    for loc_id, location in ALL_LOCATIONS.items():
        # Get characters at this location
        characters_here = get_characters_at_location(loc_id, current_period)

        locations.append({
            'id': location.id,
            'name': location.name,
            'description': location.description,
            'location_type': location.location_type,
            'atmosphere': location.atmosphere,
            'conversation_modifiers': location.conversation_modifiers,
            'is_open': location.is_open(current_hour),
            'opens_at': location.opens_at,
            'closes_at': location.closes_at,
            'travel_time': location.travel_time_from_home,
            'characters_present': characters_here,
            'is_current': loc_id == game_state.player.current_location
        })

    return jsonify({
        'locations': locations,
        'current_location': game_state.player.current_location
    })


@app.route('/api/current-location')
def api_current_location():
    """Get player's current location with characters present"""
    game_state = get_game_state()
    location = game_state.get_current_location()
    characters_here = game_state.get_characters_at_location()

    return jsonify({
        'location': {
            'id': location.id,
            'name': location.name,
            'description': location.description,
            'atmosphere': location.atmosphere,
            'conversation_modifiers': location.conversation_modifiers
        },
        'characters': [
            {
                'name': char.name,
                'emotional_state': char.emotional_state,
                'rapport': char.rapport,
                'outfit': char.outfit
            }
            for char in characters_here.values()
        ]
    })


@app.route('/api/travel', methods=['POST'])
def api_travel():
    """Travel to a new location"""
    from systems.location_system import get_location

    game_state = get_game_state()
    data = request.json

    destination_id = data.get('location_id')

    if not destination_id:
        return jsonify({'success': False, 'error': 'No destination specified'})

    # Get the destination location
    destination = get_location(destination_id)
    if not destination:
        return jsonify({'success': False, 'error': 'Invalid location'})

    # Check if location is open
    if not destination.is_open(game_state.game_time.hour):
        return jsonify({
            'success': False,
            'error': f'{destination.name} is closed at this time'
        })

    # Travel to location (this also advances time)
    old_location = game_state.get_current_location()
    success = game_state.travel_to_location(destination_id)

    if not success:
        return jsonify({'success': False, 'error': 'Cannot travel to that location'})

    # Save the updated game state
    save_game_state(game_state)

    # Get characters at new location
    characters_here = game_state.get_characters_at_location()

    return jsonify({
        'success': True,
        'old_location': old_location.name,
        'new_location': destination.name,
        'time_passed': destination.travel_time_from_home,
        'current_time': game_state.game_time.get_formatted_time(),
        'characters_present': [char.name for char in characters_here.values()],
        'location': {
            'id': destination.id,
            'name': destination.name,
            'description': destination.description,
            'atmosphere': destination.atmosphere
        }
    })


@app.route('/api/clothing-items')
def api_clothing_items():
    """Get all available clothing items"""
    from data.clothing_items import ALL_CLOTHING_ITEMS

    items = []
    for item_id, item in ALL_CLOTHING_ITEMS.items():
        items.append({
            'id': item.id,
            'name': item.name,
            'category': item.category,
            'slot': item.slot,
            'image_path': item.image_path,
            'description': item.description,
            'tags': item.tags,
            'coverage': item.coverage,
            'formality': item.formality
        })

    return jsonify({'items': items})


@app.route('/api/update-outfit', methods=['POST'])
def api_update_outfit():
    """Update a character's outfit"""
    game_state = get_game_state()
    data = request.json

    character_name = data.get('character')
    slot = data.get('slot')
    item_id = data.get('item_id')

    if not character_name or not slot:
        return jsonify({'success': False, 'error': 'Missing character or slot'}), 400

    character = game_state.characters.get(character_name)
    if not character:
        return jsonify({'success': False, 'error': 'Character not found'}), 404

    # Update the outfit
    character.update_outfit_item(slot, item_id)

    # Update text clothing description based on visual outfit
    from data.clothing_items import get_clothing_item
    outfit_description = []
    for slot_name, item_id in character.outfit.items():
        if slot_name != 'expression' and item_id:
            item = get_clothing_item(item_id)
            if item:
                outfit_description.append(item.name)

    if outfit_description:
        character.clothing = ', '.join(outfit_description)

    # Save game state
    save_game_state(game_state)

    return jsonify({
        'success': True,
        'outfit': character.outfit,
        'clothing_description': character.clothing
    })


@app.route('/api/character/<name>/outfit')
def api_character_outfit(name):
    """Get a character's current outfit"""
    game_state = get_game_state()

    character = game_state.characters.get(name)
    if not character:
        return jsonify({'error': 'Character not found'}), 404

    return jsonify({
        'name': character.name,
        'outfit': character.outfit,
        'expression': character.outfit.get('expression', 'neutral')
    })


if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5000)
