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

    game_state = get_game_state()

    # Define possible activities for each character
    activities = {
        'Ruth': ['Setting the table', 'Checking on dinner', 'Pouring drinks', 'Adjusting her hair', 'Looking at old photos'],
        'Tom': ['Reading the newspaper', 'Checking his phone', 'Sipping coffee', 'Looking out the window', 'Organizing papers'],
        'Lisa': ['Texting friends', 'Doing homework', 'Scrolling social media', 'Listening to music', 'Doodling in notebook'],
        'Marcus': ['Lifting weights mentally', 'Checking his reflection', 'Flexing subtly', 'Adjusting his shirt', 'Checking fitness app'],
        'Sophie': ['Reading a book', 'Taking notes', 'Adjusting her glasses', 'Thinking deeply', 'Reviewing documents'],
        'Rachel': ['Dancing to imaginary music', 'Making silly faces', 'Drawing', 'Playing with toys', 'Telling jokes'],
        'James': ['Daydreaming', 'Watching TV', 'Playing video games', 'Yawning', 'Snacking']
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
        new_activity = random.choice(activities.get(char_name, ['Sitting quietly']))
        result['character'] = char_name
        result['activity'] = new_activity
        result['message'] = f"{char_name} is {new_activity.lower()}"

    elif event_type == 'dialogue':
        # Random character says something
        char_name = random.choice(list(game_state.characters.keys()))
        char = game_state.characters[char_name]
        dialogue = random.choice(ambient_dialogue.get(char_name, ['*looks around*']))
        result['character'] = char_name
        result['dialogue'] = dialogue
        result['message'] = f"{char_name}: {dialogue}"

    elif event_type == 'interaction':
        # Two characters interact
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
    data = request.json
    character_name = data.get('character')
    player_message = data.get('message')

    game_state = get_game_state()
    char = game_state.get_character(character_name)

    if not char:
        return jsonify({'error': 'Character not found'}), 404

    # Get LLM response
    response = llm_handler.get_character_response(
        char,
        player_message,
        scene_context="Family dinner",
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
    """Get all characters"""
    game_state = get_game_state()

    characters = []
    for char in game_state.characters.values():
        characters.append({
            'name': char.name,
            'age': char.age,
            'occupation': char.occupation,
            'personality': char.personality,
            'rapport': char.rapport,
            'emotional_state': char.emotional_state,
            'resistance': char.resistance,
            'clothing': char.clothing,
            'active_phs': len(char.active_phs),
            'max_phs': char.max_phs
        })

    return jsonify({'characters': characters})


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
        'occupation': char.occupation,
        'personality': char.personality,
        'rapport': char.rapport,
        'emotional_state': char.emotional_state,
        'resistance': char.resistance,
        'clothing': char.clothing,
        'clothing_meaning': char.clothing_meaning,
        'active_phs': phs_list,
        'memories': memories
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


if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5000)
