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

# Register Asset Manager Blueprint
from asset_manager import asset_manager
app.register_blueprint(asset_manager)

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
    from systems.location_system import ALL_LOCATIONS

    game_state = get_game_state()

    # Get location name
    current_loc = ALL_LOCATIONS.get(game_state.player.current_location)
    location_name = current_loc.name if current_loc else game_state.player.current_location.replace('_', ' ').title()

    return jsonify({
        'player': {
            'suggestion_points': game_state.player.suggestion_points,
            'money': game_state.player.money,
            'skill_level': game_state.player.hypnosis_knowledge.skill_level,
            'techniques_mastered': len(game_state.player.hypnosis_knowledge.known_techniques),
            'total_techniques': 11,
            'food_meals': getattr(game_state.player, 'food_meals', 5),
            'food_snacks': getattr(game_state.player, 'food_snacks', 8),
            'current_location': game_state.player.current_location,
            'current_location_name': location_name
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
    from systems.trigger_detection import TriggerDetector, format_activation_message

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

        # Check for PHS triggers from this activity
        char = game_state.characters[char_name]
        triggered = TriggerDetector.check_activity_triggers(
            char, new_activity, schedule['location']
        )
        activations = TriggerDetector.attempt_activations(triggered)
        successful_activations = [a for a in activations if a['success']]

        if successful_activations:
            result['phs_activations'] = [format_activation_message(a) for a in successful_activations]
            save_game_state(game_state)

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

                # Check for PHS triggers from NPC-to-NPC conversation
                # Check both characters for triggers
                triggered_char1 = TriggerDetector.check_conversation_triggers(
                    char1, chars[1], conversation['summary'], is_player=False
                )
                triggered_char2 = TriggerDetector.check_conversation_triggers(
                    char2, chars[0], conversation['summary'], is_player=False
                )

                all_triggered = triggered_char1 + triggered_char2
                activations = TriggerDetector.attempt_activations(all_triggered)
                successful_activations = [a for a in activations if a['success']]

                if successful_activations:
                    result['phs_activations'] = [format_activation_message(a) for a in successful_activations]

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
    from systems.trigger_detection import TriggerDetector, format_activation_message
    from systems.contradiction_tracker import ContradictionTracker
    from systems.social_dynamics import SocialDynamics

    data = request.json
    character_name = data.get('character')
    player_message = data.get('message')

    # Track which character player is talking to (for ambient events)
    session['selected_character'] = character_name

    game_state = get_game_state()
    char = game_state.get_character(character_name)

    if not char:
        return jsonify({'error': 'Character not found'}), 404

    # Check for contradictions in player's statement
    contradiction_msg = ContradictionTracker.record_statement(
        game_state, character_name, player_message
    )

    # Get current location context
    current_location = game_state.get_current_location()
    location_context = get_location_context_for_llm(current_location)

    # Build scene context with contradiction info if detected
    scene_context = "Family gathering"
    if contradiction_msg:
        contradiction_context = ContradictionTracker.format_contradiction_for_llm(
            contradiction_msg, char.rapport
        )
        scene_context += contradiction_context

    # Add relationship context - character is aware of family dynamics
    relationship_context = SocialDynamics.get_relationship_context_for_conversation(
        char, game_state
    )
    if relationship_context:
        scene_context += f" {relationship_context}"

    # Get LLM response with location, contradiction context, and AI personality
    response = llm_handler.get_character_response(
        char,
        player_message,
        scene_context=scene_context,
        location_context=location_context,
        record_memory=True,
        game_state=game_state
    )

    # Check for PHS triggers from the conversation
    # Check player's message for triggers (e.g., praise, criticism)
    triggered_by_player = TriggerDetector.check_conversation_triggers(
        char, None, player_message, is_player=True
    )

    # Check character's response for triggers (e.g., "when I talk about X")
    triggered_by_response = TriggerDetector.check_conversation_triggers(
        char, None, response, is_player=True
    )

    # Combine all triggers
    all_triggered = triggered_by_player + triggered_by_response

    # Attempt activations
    activations = TriggerDetector.attempt_activations(all_triggered)

    # Filter only successful activations for display
    successful_activations = [a for a in activations if a['success']]

    # Analyze interaction with GM
    analysis = game_master.analyze_conversation_impact(
        character=char,
        player_message=player_message,
        character_response=response,
        scene_context="Family dinner"
    )

    # Apply changes
    changes = []

    # Track old values for social dynamics
    old_rapport = char.rapport
    old_emotional_state = char.emotional_state

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

        # SOCIAL DYNAMICS: Others notice rapport changes
        if abs(analysis['rapport_change']) >= 2:
            social_msgs = SocialDynamics.on_rapport_increase(
                game_state, char, old_rapport, char.rapport
            )
            for msg in social_msgs:
                changes.append({'type': 'social_observation', 'message': msg})

    if analysis['new_emotional_state'] != char.emotional_state:
        message = hypnosis_system.change_emotional_state(
            game_state,
            character_name,
            analysis['new_emotional_state'],
            analysis['reasoning']
        )
        changes.append({'type': 'emotional_state', 'message': message})

        # SOCIAL DYNAMICS: Others notice emotional changes
        social_msgs = SocialDynamics.on_emotional_state_change(
            game_state, char, old_emotional_state, char.emotional_state
        )
        for msg in social_msgs:
            changes.append({'type': 'social_observation', 'message': msg})

    # Track conversation for goals
    from systems.goal_system import GoalSystem
    goal_messages = GoalSystem.track_conversation(game_state)
    for goal_msg in goal_messages:
        changes.append({'type': 'goal', 'message': goal_msg})

    # Add PHS activations to changes and handle suspicion
    from systems.suspicion_system import SuspicionSystem

    for activation in successful_activations:
        formatted_msg = format_activation_message(activation)
        if formatted_msg:
            changes.append({'type': 'phs_activation', 'message': formatted_msg})

        # SOCIAL DYNAMICS: Others notice PHS-triggered behavior
        phs = activation.get('phs')
        if phs:
            social_msgs = SocialDynamics.on_phs_activation(game_state, char, phs)
            for msg in social_msgs:
                changes.append({'type': 'social_observation', 'message': msg})

        # Track activation for goals
        activation_goal_messages = GoalSystem.track_suggestion_activated(game_state)
        for goal_msg in activation_goal_messages:
            changes.append({'type': 'goal', 'message': goal_msg})

        # Check if this PHS activation should affect suspicion
        phs = activation.get('phs')
        if phs:
            # Check if it's a defensive PHS
            if phs.phs_type == 'defensive' and phs.defensive_target:
                # Apply defensive reduction to target character's suspicion
                target_char = game_state.get_character(phs.defensive_target)
                if target_char:
                    defense_msg = SuspicionSystem.apply_defensive_phs(
                        char, target_char, phs.suspicion_reduction
                    )
                    changes.append({'type': 'suspicion', 'message': defense_msg})
            else:
                # Check if this behavior is out of character
                is_ooc, suspicion_increase = SuspicionSystem.detect_out_of_character_behavior(char, phs)

                if is_ooc and suspicion_increase > 0:
                    # Other characters notice the strange behavior
                    # Pick 1-2 random observers from available characters
                    import random
                    observers = [c for c in game_state.characters.values()
                                if c.name != char.name and c.name != 'Player']

                    if observers:
                        num_observers = min(random.randint(1, 2), len(observers))
                        selected_observers = random.sample(observers, num_observers)

                        for observer in selected_observers:
                            suspicion_msg = SuspicionSystem.increase_character_suspicion(
                                observer, char.name, suspicion_increase
                            )
                            changes.append({'type': 'suspicion', 'message': suspicion_msg})

                            # Calculate if observer blames the player
                            evidence = SuspicionSystem.calculate_evidence_against_player(
                                game_state, observer
                            )
                            if evidence > 0:
                                player_suspicion_msg, confrontation = SuspicionSystem.increase_player_suspicion(
                                    observer, evidence, f"({char.name} is acting strange)"
                                )
                                changes.append({'type': 'suspicion', 'message': player_suspicion_msg})

                                if confrontation:
                                    changes.append({
                                        'type': 'game_over',
                                        'message': f"🚨 GAME OVER: {observer.name} confronts you about manipulating the family!"
                                    })

    # Update AI personality state based on conversation
    from systems.ai_personality import update_character_personality

    conversation_events = []

    # Build events from changes
    if analysis['rapport_change'] != 0:
        conversation_events.append({
            'type': 'rapport_change',
            'amount': analysis['rapport_change']
        })

    if analysis['new_emotional_state'] != old_emotional_state:
        conversation_events.append({
            'type': 'emotional_state_change',
            'old_state': old_emotional_state,
            'new_state': analysis['new_emotional_state']
        })

    if successful_activations:
        for activation in successful_activations:
            conversation_events.append({
                'type': 'phs_planted',
                'phs': activation.get('phs')
            })

    # Update personality
    personality_changes = update_character_personality(char, game_state, conversation_events)

    # Add personality insights to changes if significant
    if personality_changes.get('mood_changed'):
        changes.append({
            'type': 'personality_shift',
            'message': f"💭 {char.name}'s mood has shifted noticeably."
        })

    if personality_changes.get('behavioral_shifts'):
        for shift in personality_changes['behavioral_shifts']:
            if shift == 'major_trust_loss':
                changes.append({
                    'type': 'personality_shift',
                    'message': f"⚠️ {char.name} seems deeply unsettled by something."
                })

    save_game_state(game_state)

    return jsonify({
        'response': response,
        'changes': changes,
        'character_state': {
            'rapport': char.rapport,
            'emotional_state': char.emotional_state
        }
    })


@app.route('/api/get-dialogue-choices', methods=['POST'])
def api_get_dialogue_choices():
    """Get contextual dialogue choices for a character conversation"""
    from systems.dialogue_system import DialogueSystem

    data = request.json
    character_name = data.get('character')
    player_message = data.get('player_message', '')

    game_state = get_game_state()
    char = game_state.get_character(character_name)

    if not char:
        return jsonify({'error': 'Character not found'}), 404

    # Check if choices should be offered
    should_offer = DialogueSystem.should_offer_choices(
        char,
        char.conversation_history
    )

    if not should_offer:
        return jsonify({
            'has_choices': False,
            'choices': []
        })

    # Detect conversation context
    context = DialogueSystem.detect_context(
        char,
        player_message,
        char.conversation_history
    )

    if not context:
        return jsonify({
            'has_choices': False,
            'choices': []
        })

    # Get contextual choices
    choices = DialogueSystem.get_contextual_choices(
        char,
        context,
        char.rapport
    )

    # Convert to dict format
    choices_data = [choice.to_dict() for choice in choices]

    return jsonify({
        'has_choices': True,
        'context': context,
        'choices': choices_data
    })


@app.route('/api/select-dialogue-choice', methods=['POST'])
def api_select_dialogue_choice():
    """Handle selection of a dialogue choice"""
    from systems.dialogue_system import DialogueSystem
    from systems.location_system import get_location_context_for_llm
    from systems.trigger_detection import TriggerDetector, format_activation_message
    from systems.goal_system import GoalSystem
    from systems.suspicion_system import SuspicionSystem
    from systems.contradiction_tracker import ContradictionTracker

    data = request.json
    character_name = data.get('character')
    choice_id = data.get('choice_id')
    context = data.get('context')

    game_state = get_game_state()
    char = game_state.get_character(character_name)

    if not char:
        return jsonify({'error': 'Character not found'}), 404

    # Get the selected choice
    choices = DialogueSystem.get_contextual_choices(char, context, char.rapport)
    selected_choice = None
    for choice in choices:
        if choice.choice_id == choice_id:
            selected_choice = choice
            break

    if not selected_choice:
        return jsonify({'error': 'Invalid choice'}), 400

    # Check SP cost
    if selected_choice.sp_cost > 0:
        if game_state.player.skill_points < selected_choice.sp_cost:
            return jsonify({'error': 'Not enough SP'}), 400
        game_state.player.skill_points -= selected_choice.sp_cost

    # Apply choice consequences
    consequences = DialogueSystem.apply_choice_consequences(
        selected_choice,
        char,
        game_state
    )

    # Generate the dialogue text that the player says
    player_dialogue = DialogueSystem.generate_choice_prompt(selected_choice, character_name)

    # Check for contradictions in the dialogue choice
    contradiction_msg = ContradictionTracker.record_statement(
        game_state, character_name, player_dialogue
    )

    # Get character's response from LLM with choice context
    current_location = game_state.get_current_location()
    location_context = get_location_context_for_llm(current_location)

    # Add choice context to help LLM understand intent
    choice_context = DialogueSystem.get_character_response_context(selected_choice, char)
    scene_context = f"Family gathering. {choice_context}"

    # Add contradiction context if detected
    if contradiction_msg:
        contradiction_context = ContradictionTracker.format_contradiction_for_llm(
            contradiction_msg, char.rapport
        )
        scene_context += contradiction_context

    response = llm_handler.get_character_response(
        char,
        player_dialogue,
        scene_context=scene_context,
        location_context=location_context,
        record_memory=True
    )

    # Check for PHS triggers
    triggered_by_player = TriggerDetector.check_conversation_triggers(
        char, None, player_dialogue, is_player=True
    )
    triggered_by_response = TriggerDetector.check_conversation_triggers(
        char, None, response, is_player=True
    )
    all_triggered = triggered_by_player + triggered_by_response

    # If this choice triggers a PHS attempt, modify success rate
    if selected_choice.triggers_phs_attempt and selected_choice.phs_difficulty_modifier != 0:
        # Adjust activation chances for this specific attempt
        for phs, chance in all_triggered:
            adjusted_chance = max(0, min(100, chance + selected_choice.phs_difficulty_modifier))
            all_triggered = [(phs, adjusted_chance) for p, c in all_triggered if p == phs]

    activations = TriggerDetector.attempt_activations(all_triggered)
    successful_activations = [a for a in activations if a['success']]

    # Build response changes
    changes = consequences['messages'].copy()

    # Track conversation for goals
    goal_messages = GoalSystem.track_conversation(game_state)
    for goal_msg in goal_messages:
        changes.append(goal_msg)

    # Add PHS activations and suspicion checks
    for activation in successful_activations:
        formatted_msg = format_activation_message(activation)
        if formatted_msg:
            changes.append(formatted_msg)

        activation_goal_messages = GoalSystem.track_suggestion_activated(game_state)
        changes.extend(activation_goal_messages)

        phs = activation.get('phs')
        if phs:
            if phs.phs_type == 'defensive' and phs.defensive_target:
                target_char = game_state.get_character(phs.defensive_target)
                if target_char:
                    defense_msg = SuspicionSystem.apply_defensive_phs(
                        char, target_char, phs.suspicion_reduction
                    )
                    changes.append(defense_msg)
            else:
                is_ooc, suspicion_increase = SuspicionSystem.detect_out_of_character_behavior(char, phs)
                if is_ooc and suspicion_increase > 0:
                    import random
                    observers = [c for c in game_state.characters.values()
                                if c.name != char.name and c.name != 'Player']

                    if observers:
                        num_observers = min(random.randint(1, 2), len(observers))
                        selected_observers = random.sample(observers, num_observers)

                        for observer in selected_observers:
                            suspicion_msg = SuspicionSystem.increase_character_suspicion(
                                observer, char.name, suspicion_increase
                            )
                            changes.append(suspicion_msg)

                            evidence = SuspicionSystem.calculate_evidence_against_player(
                                game_state, observer
                            )
                            if evidence > 0:
                                player_suspicion_msg, confrontation = SuspicionSystem.increase_player_suspicion(
                                    observer, evidence, f"({char.name} is acting strange)"
                                )
                                changes.append(player_suspicion_msg)

                                if confrontation:
                                    changes.append(
                                        f"🚨 GAME OVER: {observer.name} confronts you about manipulating the family!"
                                    )

    save_game_state(game_state)

    return jsonify({
        'success': True,
        'player_said': player_dialogue,
        'response': response,
        'changes': changes,
        'consequences': {
            'rapport_changed': consequences.get('rapport_changed', False),
            'resistance_changed': consequences.get('resistance_changed', False),
            'emotional_state_changed': consequences.get('emotional_state_changed', False),
            'suspicion_changed': consequences.get('suspicion_changed', False),
            'new_rapport': consequences.get('new_rapport', char.rapport),
            'new_resistance': consequences.get('new_resistance', char.resistance),
            'new_emotional_state': consequences.get('new_emotional_state', char.emotional_state),
            'new_suspicion': consequences.get('new_suspicion', char.player_suspicion)
        },
        'character_state': {
            'rapport': char.rapport,
            'emotional_state': char.emotional_state,
            'resistance': char.resistance,
            'player_suspicion': char.player_suspicion
        }
    })


@app.route('/api/characters')
def api_characters():
    """Get characters at player's current location"""
    from systems.time_system import get_character_schedule
    from systems.location_system import get_character_location
    from systems.mood_system import MoodSystem
    from systems.unlock_system import UnlockSystem

    game_state = get_game_state()
    current_period = game_state.game_time.period
    player_location = game_state.player.current_location

    # Get only characters at player's location
    characters_here = game_state.get_characters_at_location()

    characters = []
    for char in characters_here.values():
        # Check if character is unlocked
        is_unlocked, unlock_reasons = UnlockSystem.is_character_unlocked(char.name, game_state)
        if not is_unlocked:
            continue  # Skip locked characters

        schedule = get_character_schedule(char.name, current_period)

        # Get mood information
        mood_info = MoodSystem.format_mood_display(
            char.emotional_state,
            char.emotional_state_reason,
            include_recommendation=True
        )

        characters.append({
            'name': char.name,
            'age': char.age,
            'gender': char.gender,
            'occupation': char.occupation,
            'personality': char.personality,
            'rapport': char.rapport,
            'emotional_state': char.emotional_state,
            'emotional_state_reason': char.emotional_state_reason,
            'mood_emoji': mood_info['emoji'],
            'mood_recommendation': mood_info['recommendation_text'],
            'mood_color': mood_info['recommendation_color'],
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
    from systems.clothing_effects import ClothingEffects
    from systems.mood_system import MoodSystem
    from systems.suspicion_system import SuspicionSystem

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
            'success_rate': phs.success_rate,
            'reinforcements': phs.reinforcements,
            'activation_chance': chance,
            'phs_type': phs.phs_type
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

    # Calculate clothing effects
    clothing_modifier, clothing_desc = ClothingEffects.calculate_outfit_suggestibility(char)
    outfit_description = ClothingEffects.get_outfit_description(char)

    # Get mood information
    mood_info = MoodSystem.format_mood_display(
        char.emotional_state,
        char.emotional_state_reason,
        include_recommendation=True
    )

    # Get suspicion status
    suspicion_status = SuspicionSystem.get_suspicion_status(char)

    return jsonify({
        'name': char.name,
        'age': char.age,
        'gender': char.gender,
        'occupation': char.occupation,
        'personality': char.personality,
        'rapport': char.rapport,
        'emotional_state': char.emotional_state,
        'emotional_state_reason': char.emotional_state_reason,
        'mood_emoji': mood_info['emoji'],
        'mood_recommendation': mood_info['recommendation_text'],
        'mood_color': mood_info['recommendation_color'],
        'resistance': char.resistance,
        'clothing': char.clothing,
        'clothing_meaning': char.clothing_meaning,
        'outfit': char.outfit,
        'outfit_description': outfit_description,
        'clothing_modifier': clothing_modifier,
        'clothing_effect': clothing_desc,
        'active_phs': phs_list,
        'max_phs': char.max_phs,
        'memories': memories,
        'relationships': char.relationships,
        'character_interactions': char.character_interactions,
        'player_suspicion': char.player_suspicion,
        'suspicion_status': suspicion_status,
        'character_suspicions': char.character_suspicions
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

            # Advance time - reading takes 45 minutes
            time_warnings = game_state.advance_time_with_needs(45)

            result = {
                'success': True,
                'learned': learned,
                'progress_made': progress_made,
                'book_title': book['title'],
                'time_passed': 45,
                'new_time': game_state.game_time.get_formatted_time(),
                'warnings': list(time_warnings.values())
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

            # Advance time - practicing takes 40 minutes
            time_warnings = game_state.advance_time_with_needs(40)
            result['time_passed'] = 40
            result['new_time'] = game_state.game_time.get_formatted_time()
            result['warnings'] = list(time_warnings.values())

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

            # Advance time - researching takes 30 minutes
            time_warnings = game_state.advance_time_with_needs(30)
            result['time_passed'] = 30
            result['new_time'] = game_state.game_time.get_formatted_time()
            result['warnings'] = list(time_warnings.values())
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

    # Track suggestion planting for goals
    if success:
        from systems.goal_system import GoalSystem
        goal_messages = GoalSystem.track_suggestion_planted(game_state, character_name)
        if goal_messages:
            message += "\n" + "\n".join(goal_messages)

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

    # Track time advancement for goals
    from systems.goal_system import GoalSystem
    time_goal_messages = GoalSystem.track_time_advance(game_state, minutes)

    # Check for goal resets (daily/weekly)
    reset_messages = GoalSystem.check_daily_reset(game_state)
    reset_messages.extend(GoalSystem.check_weekly_reset(game_state))

    # Apply suspicion decay based on time passed
    from systems.suspicion_system import SuspicionSystem
    hours_passed = minutes / 60
    suspicion_messages = []

    for char in game_state.characters.values():
        decay_msgs = SuspicionSystem.decay_suspicion_over_time(char, int(hours_passed))
        suspicion_messages.extend(decay_msgs)

    # SOCIAL DYNAMICS: Characters gossip when time passes
    from systems.social_dynamics import SocialDynamics
    gossip_messages = []
    if minutes >= 15:  # Only gossip if significant time passed
        gossip_msgs = SocialDynamics.trigger_gossip_session(game_state)
        gossip_messages.extend(gossip_msgs)

    # DYNAMIC RANDOM EVENTS: Check if a random event should trigger
    from systems.dynamic_events import DynamicEventSystem
    from data.event_library import ALL_EVENTS
    dynamic_event_triggered = None

    should_trigger, event_type = DynamicEventSystem.should_trigger_event(game_state)
    if should_trigger:
        available_events = DynamicEventSystem.get_available_events(game_state, event_type, ALL_EVENTS)
        if available_events:
            selected_event = DynamicEventSystem.select_event(available_events)
            if selected_event:
                event_result = DynamicEventSystem.trigger_event(game_state, selected_event)
                if event_result['success']:
                    dynamic_event_triggered = event_result['event']

    # Check for opportunity expiration
    opportunity_expired_msg = DynamicEventSystem.check_opportunity_expiration(game_state)

    # Check for time-triggered events (character introductions, etc.)
    from systems.event_system import EventSystem
    triggered_events = EventSystem.check_time_triggered_events(game_state)
    event_data_list = []

    for event in triggered_events:
        success, event_data = EventSystem.trigger_event(event.event_id, game_state)
        if success:
            event_data_list.append(event_data)

    # Check for autonomous character events (PHS activations, etc.)
    from systems.autonomous_events import AutonomousEventsSystem
    autonomous_events = AutonomousEventsSystem.check_autonomous_triggers(game_state, minutes)
    autonomous_messages = []

    for auto_event in autonomous_events:
        # Log the event
        AutonomousEventsSystem.add_event_to_log(game_state, auto_event)

        # Add to messages if visible
        if auto_event.visibility in ['public', 'subtle']:
            autonomous_messages.append(f"{auto_event.icon} {auto_event.description}")

    # EMERGENT BEHAVIOR: Characters may take autonomous actions
    from systems.ai_personality import trigger_emergent_behavior

    emergent_behavior = trigger_emergent_behavior(game_state)
    emergent_behavior_message = None

    if emergent_behavior:
        emergent_behavior_message = emergent_behavior['narrative']

        # Apply game effects from emergent behavior
        for effect in emergent_behavior.get('game_effects', []):
            if effect['type'] == 'alliance_formed':
                # Alliance already formed in trigger
                pass
            elif effect['type'] == 'crisis_event':
                # Mark as current crisis
                game_state.current_crisis = {
                    'type': 'confrontation',
                    'character': effect['character']
                }

    # Save the updated game state
    save_game_state(game_state)

    # Prepare response
    response = {
        'success': True,
        'time': game_state.game_time.get_formatted_time(),
        'date': game_state.game_time.get_formatted_date(),
        'period': game_state.game_time.period.capitalize(),
        'events': events,
        'messages': [],
        'triggered_events': event_data_list,  # Add story events
        'emergent_behavior': emergent_behavior  # Add emergent behavior
    }

    # Add event messages
    if events['messages']:
        response['messages'] = events['messages']

    # Add suspicion decay messages
    if suspicion_messages:
        response['messages'].extend(suspicion_messages)

    # Add goal messages
    if time_goal_messages:
        response['messages'].extend(time_goal_messages)

    # Add reset messages
    if reset_messages:
        response['messages'].extend(reset_messages)

    # Add gossip messages
    if gossip_messages:
        response['messages'].extend(gossip_messages)

    # Add autonomous event messages
    if autonomous_messages:
        response['messages'].extend(autonomous_messages)

    # Add emergent behavior message
    if emergent_behavior_message:
        response['messages'].append(f"🎭 {emergent_behavior_message}")

    # Add dynamic random event
    if dynamic_event_triggered:
        response['dynamic_event'] = dynamic_event_triggered

    # Add opportunity expiration warning
    if opportunity_expired_msg:
        response['messages'].append(opportunity_expired_msg)

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

    # Map location to scene
    location_to_scene_map = {
        'home_kitchen': 'kitchen',
        'home_living_room': 'living_room',
        'home_dining_room': 'family_dinner',
        'home_your_room': 'your_room',
        'home_backyard': 'backyard',
        'ruths_office': 'ruths_office',
        'fitness_center': 'fitness_center',
        'elementary_school': 'elementary_school',
        'city_park': 'city_park',
        'coffee_cafe': 'coffee_cafe',
        'shopping_mall': 'shopping_mall',
        'restaurant': 'restaurant'
    }

    # Update current scene based on location
    new_scene = location_to_scene_map.get(destination_id, 'family_dinner')
    session['current_scene'] = new_scene

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


@app.route('/api/phs/reinforce', methods=['POST'])
def api_reinforce_phs():
    """Reinforce a post-hypnotic suggestion"""
    game_state = get_game_state()
    data = request.get_json()

    character_name = data.get('character')
    phs_index = data.get('phs_index')

    character = game_state.characters.get(character_name)
    if not character:
        return jsonify({'error': 'Character not found'}), 404

    if phs_index < 0 or phs_index >= len(character.active_phs):
        return jsonify({'error': 'Invalid PHS index'}), 400

    # Check if player has enough SP
    sp_cost = 1
    if game_state.player.suggestion_points < sp_cost:
        return jsonify({'error': 'Not enough Suggestion Points'}), 400

    # Reinforce the PHS
    phs = character.active_phs[phs_index]
    phs.reinforce()

    # Deduct SP
    game_state.player.suggestion_points -= sp_cost

    return jsonify({
        'success': True,
        'message': f'Reinforced suggestion! Now {phs.calculate_activation_chance()}% activation chance.',
        'phs': {
            'trigger': phs.trigger,
            'response': phs.response,
            'success_rate': phs.success_rate,
            'reinforcements': phs.reinforcements,
            'activation_chance': phs.calculate_activation_chance()
        },
        'sp_remaining': game_state.player.suggestion_points
    })


@app.route('/api/phs/remove', methods=['POST'])
def api_remove_phs():
    """Remove a post-hypnotic suggestion"""
    game_state = get_game_state()
    data = request.get_json()

    character_name = data.get('character')
    phs_index = data.get('phs_index')

    character = game_state.characters.get(character_name)
    if not character:
        return jsonify({'error': 'Character not found'}), 404

    if phs_index < 0 or phs_index >= len(character.active_phs):
        return jsonify({'error': 'Invalid PHS index'}), 400

    # Remove the PHS
    removed_phs = character.active_phs.pop(phs_index)

    return jsonify({
        'success': True,
        'message': f'Removed suggestion: "{removed_phs.trigger}"',
        'phs_count': len(character.active_phs),
        'max_phs': character.max_phs
    })


@app.route('/api/unlocks')
def api_unlocks():
    """Get unlock status for all characters and locations"""
    from systems.unlock_system import UnlockSystem

    game_state = get_game_state()

    # Get available locations
    available_locations = UnlockSystem.get_available_locations(game_state)

    # Get available characters
    available_characters = UnlockSystem.get_available_characters(game_state)

    # Get upcoming unlocks
    upcoming = UnlockSystem.get_next_unlock_preview(game_state)

    return jsonify({
        'locations': available_locations,
        'characters': available_characters,
        'upcoming': upcoming,
        'game_day': game_state.game_time.day,
        'game_week': game_state.game_time.day // 7 + 1
    })


@app.route('/api/trigger-event', methods=['POST'])
def api_trigger_event():
    """Manually trigger an event (for testing or story progression)"""
    from systems.event_system import EventSystem

    game_state = get_game_state()
    data = request.get_json()

    event_id = data.get('event_id')

    if not event_id:
        return jsonify({'error': 'event_id required'}), 400

    # Trigger the event
    success, event_data = EventSystem.trigger_event(event_id, game_state)

    if not success:
        return jsonify(event_data), 400

    save_game_state(game_state)

    return jsonify({
        'success': True,
        'event_data': event_data
    })


@app.route('/api/progression')
def api_progression():
    """Get progression status - unlocks, events, etc."""
    from systems.unlock_system import UnlockSystem
    from systems.event_system import EventSystem

    game_state = get_game_state()

    # Get unlock counts
    all_locations = UnlockSystem.get_available_locations(game_state)
    unlocked_locations = [l for l in all_locations if l['is_unlocked']]
    locked_locations = [l for l in all_locations if not l['is_unlocked']]

    all_characters = UnlockSystem.get_available_characters(game_state)
    unlocked_characters = [c for c in all_characters if c['is_unlocked']]
    locked_characters = [c for c in all_characters if not c['is_unlocked']]

    # Get pending events
    pending_events = EventSystem.get_pending_events(game_state)

    # Calculate progression percentage
    total_locations = len(all_locations)
    total_characters = len(all_characters)
    location_progress = (len(unlocked_locations) / total_locations * 100) if total_locations > 0 else 0
    character_progress = (len(unlocked_characters) / total_characters * 100) if total_characters > 0 else 0

    return jsonify({
        'game_day': game_state.game_time.day,
        'game_week': game_state.game_time.day // 7 + 1,
        'locations': {
            'unlocked': len(unlocked_locations),
            'total': total_locations,
            'progress': round(location_progress, 1),
            'locked_list': locked_locations
        },
        'characters': {
            'unlocked': len(unlocked_characters),
            'total': total_characters,
            'progress': round(character_progress, 1),
            'locked_list': locked_characters
        },
        'pending_events': pending_events,
        'completed_events_count': len(game_state.completed_events)
    })


@app.route('/api/goals')
def api_goals():
    """Get all goals, achievements, and progress"""
    from systems.goal_system import GoalSystem

    game_state = get_game_state()

    # Initialize goals if not already done
    GoalSystem.initialize_goals(game_state)

    # Get complete goals summary
    goals_summary = GoalSystem.get_goals_summary(game_state)

    # Calculate completion percentages
    daily_completed = sum(1 for g in goals_summary['daily_goals'] if g['completed'])
    daily_total = len(goals_summary['daily_goals'])
    daily_progress = (daily_completed / daily_total * 100) if daily_total > 0 else 0

    weekly_completed = sum(1 for g in goals_summary['weekly_goals'] if g['completed'])
    weekly_total = len(goals_summary['weekly_goals'])
    weekly_progress = (weekly_completed / weekly_total * 100) if weekly_total > 0 else 0

    achievements_completed = sum(1 for a in goals_summary['achievements'] if a['completed'])
    achievements_total = len(goals_summary['achievements'])
    achievement_progress = (achievements_completed / achievements_total * 100) if achievements_total > 0 else 0

    return jsonify({
        'daily_goals': goals_summary['daily_goals'],
        'weekly_goals': goals_summary['weekly_goals'],
        'achievements': goals_summary['achievements'],
        'character_progress': goals_summary['character_progress'],
        'stats': goals_summary['stats'],
        'summary': {
            'daily_progress': round(daily_progress, 1),
            'daily_completed': daily_completed,
            'daily_total': daily_total,
            'weekly_progress': round(weekly_progress, 1),
            'weekly_completed': weekly_completed,
            'weekly_total': weekly_total,
            'achievement_progress': round(achievement_progress, 1),
            'achievements_completed': achievements_completed,
            'achievements_total': achievements_total
        }
    })


@app.route('/api/available-activities')
def api_available_activities():
    """Get activities available at player's current location"""
    from systems.activities import ActivitiesSystem

    game_state = get_game_state()
    player_location = game_state.player.current_location

    # Get character at current location (if any)
    characters_here = game_state.get_characters_at_location()
    character_name = characters_here[0].name if characters_here else None

    # Get rapport if character present
    rapport = 0
    if character_name:
        char = game_state.get_character(character_name)
        rapport = char.rapport if char else 0

    # Get available activities
    activities = ActivitiesSystem.get_available_activities(
        location=player_location,
        character_present=character_name,
        rapport=rapport,
        player_sp=game_state.player.suggestion_points
    )

    # Convert to dict format
    activities_data = []
    for activity in activities:
        # Check if character especially likes this activity
        is_preferred = False
        if character_name:
            preferences = ActivitiesSystem.get_character_activity_preferences(character_name)
            is_preferred = activity.activity_id in preferences

        activities_data.append({
            'activity_id': activity.activity_id,
            'name': activity.name,
            'description': activity.description,
            'duration_minutes': activity.duration_minutes,
            'sp_cost': activity.sp_cost,
            'min_rapport': activity.min_rapport,
            'icon': activity.icon,
            'activity_type': activity.activity_type,
            'rapport_gain': activity.rapport_gain,
            'allows_phs': activity.allows_phs,
            'phs_bonus': activity.phs_bonus,
            'money_reward': activity.money_reward,
            'sp_reward': activity.sp_reward,
            'is_preferred': is_preferred
        })

    return jsonify({
        'activities': activities_data,
        'location': player_location,
        'character_present': character_name
    })


@app.route('/api/start-activity', methods=['POST'])
def api_start_activity():
    """Start an activity"""
    from systems.activities import ActivitiesSystem
    from systems.goal_system import GoalSystem

    data = request.json
    activity_id = data.get('activity_id')
    character_name = data.get('character_name')

    game_state = get_game_state()

    # Get activity
    activity = ActivitiesSystem.get_activity_by_id(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404

    # Get character
    char = None
    if character_name:
        char = game_state.get_character(character_name)
        if not char:
            return jsonify({'error': 'Character not found'}), 404

    # Check requirements
    if activity.sp_cost > game_state.player.suggestion_points:
        return jsonify({'error': 'Not enough SP'}), 400

    if activity.money_cost > game_state.player.money:
        return jsonify({'error': f'Not enough money (need ${activity.money_cost})'}), 400

    if char and char.rapport < activity.min_rapport:
        return jsonify({'error': f'Need {activity.min_rapport}+ rapport'}), 400

    # Deduct SP cost
    if activity.sp_cost > 0:
        game_state.player.suggestion_points -= activity.sp_cost

    # Perform activity
    results = ActivitiesSystem.perform_activity(activity, char, game_state)

    # Advance time and get warnings
    time_warnings = game_state.advance_time_with_needs(activity.duration_minutes)
    time_msgs = list(time_warnings.values())
    results['changes'].extend(time_msgs)

    # Track time for goals
    time_goal_messages = GoalSystem.track_time_advance(game_state, activity.duration_minutes)
    results['changes'].extend(time_goal_messages)

    # Check for daily/weekly resets
    reset_messages = GoalSystem.check_daily_reset(game_state)
    reset_messages.extend(GoalSystem.check_weekly_reset(game_state))
    results['changes'].extend(reset_messages)

    # Check for time-triggered events
    from systems.event_system import EventSystem
    triggered_events = EventSystem.check_time_triggered_events(game_state)
    for event in triggered_events:
        success, event_data = EventSystem.trigger_event(event.event_id, game_state)
        if success:
            results['changes'].append(f"📖 {event.name}: {event.description}")

    save_game_state(game_state)

    return jsonify({
        'success': True,
        'activity_name': results['activity_name'],
        'message': results['message'],
        'changes': results['changes'],
        'duration': results['duration'],
        'phs_opportunity': results.get('phs_opportunity', False),
        'phs_bonus': results.get('phs_bonus', 0),
        'rapport_gained': results.get('rapport_gained', 0),
        'money_earned': results.get('money_earned', 0),
        'sp_earned': results.get('sp_earned', 0),
        'character_state': {
            'rapport': char.rapport,
            'emotional_state': char.emotional_state,
            'resistance': char.resistance
        } if char else None
    })


@app.route('/api/shop/gifts')
def api_shop_gifts():
    """Get available gifts"""
    from systems.money_system import MoneySystem

    game_state = get_game_state()
    player_money = game_state.player.money

    gifts = []
    for gift in MoneySystem.ALL_GIFTS.values():
        gifts.append({
            'gift_id': gift.gift_id,
            'name': gift.name,
            'description': gift.description,
            'cost': gift.cost,
            'category': gift.category,
            'icon': gift.icon,
            'can_afford': player_money >= gift.cost,
            'rapport_gain': gift.rapport_gain,
            'resistance_change': gift.resistance_change
        })

    return jsonify({
        'gifts': gifts,
        'player_money': player_money
    })


@app.route('/api/shop/give-gift', methods=['POST'])
def api_give_gift():
    """Give a gift to a character"""
    from systems.money_system import MoneySystem

    data = request.json
    gift_id = data.get('gift_id')
    character_name = data.get('character')

    game_state = get_game_state()

    gift = MoneySystem.ALL_GIFTS.get(gift_id)
    if not gift:
        return jsonify({'error': 'Gift not found'}), 404

    results = MoneySystem.give_gift(game_state, character_name, gift)

    if not results['success']:
        return jsonify(results), 400

    save_game_state(game_state)

    return jsonify(results)


@app.route('/api/shop/groceries')
def api_shop_groceries():
    """Get available groceries"""
    from systems.money_system import MoneySystem

    game_state = get_game_state()
    player_money = game_state.player.money

    groceries = []
    for grocery in MoneySystem.GROCERIES.values():
        groceries.append({
            'item_id': grocery.item_id,
            'name': grocery.name,
            'description': grocery.description,
            'cost': grocery.cost,
            'category': grocery.category,
            'icon': grocery.icon,
            'meals_qty': grocery.meals_qty,
            'snacks_qty': grocery.snacks_qty,
            'can_afford': player_money >= grocery.cost
        })

    return jsonify({
        'groceries': groceries,
        'player_money': player_money,
        'food_meals': game_state.player.food_meals,
        'food_snacks': game_state.player.food_snacks
    })


@app.route('/api/shop/buy-grocery', methods=['POST'])
def api_buy_grocery():
    """Buy groceries"""
    from systems.money_system import MoneySystem

    data = request.json
    item_id = data.get('item_id')

    game_state = get_game_state()

    grocery = MoneySystem.GROCERIES.get(item_id)
    if not grocery:
        return jsonify({'error': 'Grocery item not found'}), 404

    results = MoneySystem.buy_groceries(game_state, grocery)

    if not results['success']:
        return jsonify(results), 400

    save_game_state(game_state)

    return jsonify(results)


@app.route('/api/jobs')
def api_jobs():
    """Get available jobs"""
    from systems.money_system import MoneySystem

    game_state = get_game_state()
    player_sp = game_state.player.suggestion_points
    player_skill_level = game_state.player.hypnosis_knowledge.skill_level

    jobs = []
    for job in MoneySystem.JOBS.values():
        # Check if player can afford SP cost
        can_afford_sp = player_sp >= job.sp_cost

        # Check skill level requirement (if any)
        requires_skill_level = getattr(job, 'requires_skill_level', 'novice')

        # Skill level hierarchy: novice, beginner, intermediate, advanced, expert, master
        skill_levels = ['novice', 'beginner', 'intermediate', 'advanced', 'expert', 'master']
        player_level_idx = skill_levels.index(player_skill_level) if player_skill_level in skill_levels else 0
        required_level_idx = skill_levels.index(requires_skill_level) if requires_skill_level in skill_levels else 0
        meets_requirement = player_level_idx >= required_level_idx

        jobs.append({
            'job_id': job.job_id,
            'name': job.name,
            'description': job.description,
            'duration_minutes': job.duration_minutes,
            'pay': job.pay,
            'sp_cost': job.sp_cost,
            'icon': job.icon,
            'requires_skill_level': requires_skill_level,
            'meets_requirement': meets_requirement,
            'can_afford_sp': can_afford_sp
        })

    return jsonify({
        'jobs': jobs,
        'player_money': game_state.player.money
    })


@app.route('/api/jobs/do-job', methods=['POST'])
def api_do_job():
    """Perform a job to earn money"""
    from systems.money_system import MoneySystem

    data = request.json
    job_id = data.get('job_id')

    game_state = get_game_state()

    job = MoneySystem.JOBS.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    results = MoneySystem.do_job(game_state, job)

    if not results['success']:
        return jsonify(results), 400

    save_game_state(game_state)

    return jsonify(results)


@app.route('/api/autonomous-events')
def api_autonomous_events():
    """Get recent autonomous character events (PHS activations, etc.)"""
    from systems.autonomous_events import AutonomousEventsSystem

    game_state = get_game_state()
    recent_events = AutonomousEventsSystem.get_recent_events(game_state, limit=10)

    return jsonify({
        'success': True,
        'events': recent_events
    })


@app.route('/api/journal/entries', methods=['GET'])
def api_get_journal_entries():
    """Get journal entries, optionally filtered"""
    from systems.journal_system import JournalSystem

    game_state = get_game_state()

    character = request.args.get('character')
    entry_type = request.args.get('type')
    limit = int(request.args.get('limit', 50))

    entries = JournalSystem.get_journal_entries(
        game_state,
        character_name=character,
        entry_type=entry_type,
        limit=limit
    )

    return jsonify({
        'success': True,
        'entries': entries
    })


@app.route('/api/journal/create', methods=['POST'])
def api_create_journal_entry():
    """Create a new journal entry"""
    from systems.journal_system import JournalSystem

    game_state = get_game_state()
    data = request.json

    entry = JournalSystem.create_journal_entry(
        game_state,
        entry_type=data.get('type', 'general'),
        content=data.get('content', ''),
        character_name=data.get('character'),
        title=data.get('title', ''),
        tags=data.get('tags', []),
        is_important=data.get('is_important', False)
    )

    save_game_state(game_state)

    return jsonify({
        'success': True,
        'entry_id': entry.entry_id,
        'message': 'Journal entry created'
    })


@app.route('/api/journal/delete/<entry_id>', methods=['DELETE'])
def api_delete_journal_entry(entry_id):
    """Delete a journal entry"""
    from systems.journal_system import JournalSystem

    game_state = get_game_state()

    success = JournalSystem.delete_journal_entry(game_state, entry_id)

    if success:
        save_game_state(game_state)
        return jsonify({'success': True, 'message': 'Entry deleted'})
    else:
        return jsonify({'success': False, 'error': 'Entry not found'}), 404


@app.route('/api/dossier/<character_name>')
def api_get_character_dossier(character_name):
    """Get comprehensive dossier for a character"""
    from systems.journal_system import JournalSystem

    game_state = get_game_state()

    dossier = JournalSystem.get_character_dossier(game_state, character_name)

    if 'error' in dossier:
        return jsonify(dossier), 404

    return jsonify({
        'success': True,
        'dossier': dossier
    })


@app.route('/api/dossiers/summary')
def api_get_all_dossiers_summary():
    """Get summary of all character dossiers"""
    from systems.journal_system import JournalSystem

    game_state = get_game_state()

    summaries = JournalSystem.get_all_dossiers_summary(game_state)

    return jsonify({
        'success': True,
        'summaries': summaries
    })


@app.route('/api/hypnosis/techniques')
def api_hypnosis_techniques():
    """Get available induction techniques"""
    from systems.deep_hypnosis import DeepHypnosisSystem

    game_state = get_game_state()

    techniques = DeepHypnosisSystem.get_available_techniques(game_state)

    return jsonify({
        'success': True,
        'techniques': techniques
    })


@app.route('/api/hypnosis/induce', methods=['POST'])
def api_hypnosis_induce():
    """Attempt hypnotic induction on a character"""
    from systems.deep_hypnosis import DeepHypnosisSystem, InductionTechnique

    game_state = get_game_state()
    data = request.json

    character_name = data.get('character')
    technique_str = data.get('technique')

    if not character_name or not technique_str:
        return jsonify({'error': 'Missing character or technique'}), 400

    # Convert string to enum
    try:
        technique = InductionTechnique(technique_str)
    except ValueError:
        return jsonify({'error': 'Invalid technique'}), 400

    # Attempt induction
    results = DeepHypnosisSystem.attempt_induction(game_state, character_name, technique)

    if not results['success']:
        return jsonify(results), 400

    save_game_state(game_state)

    return jsonify(results)


@app.route('/api/hypnosis/wake', methods=['POST'])
def api_hypnosis_wake():
    """Wake a character from trance (for fractionation)"""
    from systems.deep_hypnosis import DeepHypnosisSystem

    game_state = get_game_state()
    data = request.json

    character_name = data.get('character')

    if not character_name:
        return jsonify({'error': 'Missing character'}), 400

    results = DeepHypnosisSystem.wake_from_trance(game_state, character_name)

    if not results['success']:
        return jsonify(results), 400

    save_game_state(game_state)

    return jsonify(results)


@app.route('/api/hypnosis/trance-state/<character_name>')
def api_get_trance_state(character_name):
    """Get character's current trance state"""
    from systems.deep_hypnosis import DeepHypnosisSystem

    game_state = get_game_state()
    character = game_state.characters.get(character_name)

    if not character:
        return jsonify({'error': 'Character not found'}), 404

    DeepHypnosisSystem.initialize_trance_state(character)

    trance_state = character.trance_state

    return jsonify({
        'success': True,
        'is_in_trance': trance_state.is_in_trance,
        'current_depth': trance_state.current_depth,
        'depth_level': trance_state.get_depth_name(),
        'max_depth_reached': trance_state.max_depth_reached,
        'fractionation_count': trance_state.fractionation_count,
        'fractionation_multiplier': trance_state.fractionation_multiplier,
        'vulnerabilities': DeepHypnosisSystem.get_character_vulnerabilities(character)
    })


@app.route('/api/hypnosis/deep-phs', methods=['POST'])
def api_plant_deep_phs():
    """Plant a PHS with depth-modified effectiveness"""
    from systems.deep_hypnosis import DeepHypnosisSystem

    game_state = get_game_state()
    data = request.json

    character_name = data.get('character')
    trigger = data.get('trigger', '')
    response = data.get('response', '')

    if not character_name or not trigger or not response:
        return jsonify({'error': 'Missing required fields'}), 400

    results = DeepHypnosisSystem.plant_deep_suggestion(game_state, character_name, trigger, response)

    if not results['success']:
        return jsonify(results), 400

    save_game_state(game_state)

    return jsonify(results)


@app.route('/api/social/alliances')
def api_check_alliances():
    """Check for character alliances forming against player"""
    from systems.social_dynamics import SocialDynamics

    game_state = get_game_state()

    alliances = SocialDynamics.check_alliances(game_state)

    return jsonify({
        'success': True,
        'alliances': alliances,
        'alliance_count': len(alliances),
        'threat_level': 'high' if any(a['threat_level'] == 'high' for a in alliances) else
                       'medium' if alliances else 'none'
    })


@app.route('/api/social/relationship-map')
def api_relationship_map():
    """Get the full relationship map for visualization"""
    from systems.relationship_web import RelationshipWeb

    game_state = get_game_state()

    # Build relationship map
    relationship_data = []

    for char_name, char in game_state.characters.items():
        char_data = {
            'name': char.name,
            'player_suspicion': char.player_suspicion,
            'relationships': {}
        }

        # Character-to-character relationships
        for other_name, score in char.relationships.items():
            char_data['relationships'][other_name] = {
                'score': score,
                'type': RelationshipWeb.get_relationship_type(score),
                'protective_threshold': RelationshipWeb.get_protective_threshold(score)
            }

        # Character suspicions (who they think is acting weird)
        char_data['character_suspicions'] = char.character_suspicions

        relationship_data.append(char_data)

    return jsonify({
        'success': True,
        'relationships': relationship_data
    })


@app.route('/api/events/respond', methods=['POST'])
def api_respond_to_event():
    """Respond to a dynamic random event"""
    from systems.dynamic_events import DynamicEventSystem
    from data.event_library import ALL_EVENTS

    game_state = get_game_state()
    data = request.json

    event_id = data.get('event_id')
    option_id = data.get('option_id')

    if not event_id or not option_id:
        return jsonify({'error': 'Missing event_id or option_id'}), 400

    result = DynamicEventSystem.respond_to_event(
        game_state, event_id, option_id, ALL_EVENTS
    )

    if not result['success']:
        return jsonify(result), 400

    save_game_state(game_state)

    return jsonify(result)


@app.route('/api/events/active')
def api_get_active_event():
    """Get currently active event or opportunity"""
    game_state = get_game_state()

    active_event = None

    # Check for active opportunity
    if hasattr(game_state, 'active_opportunity') and game_state.active_opportunity:
        opp = game_state.active_opportunity
        from data.event_library import get_event

        event = get_event(opp['event_id'])
        if event:
            time_remaining = opp['expires_at'] - game_state.game_time.total_minutes
            active_event = {
                'event': event.to_dict(),
                'time_remaining': max(0, time_remaining),
                'type': 'opportunity'
            }

    return jsonify({
        'success': True,
        'active_event': active_event
    })


@app.route('/api/events/probabilities')
def api_event_probabilities():
    """Get current event probabilities (for debugging/UI)"""
    from systems.dynamic_events import DynamicEventSystem

    game_state = get_game_state()

    probabilities = DynamicEventSystem.calculate_event_probability(game_state)

    return jsonify({
        'success': True,
        'probabilities': probabilities
    })


# ==================== SAVE SYSTEM ENDPOINTS ====================

@app.route('/api/saves/list')
def api_list_saves():
    """List all available save slots"""
    from systems.save_system import save_system

    saves = save_system.list_saves()

    return jsonify({
        'success': True,
        'saves': saves,
        'max_slots': save_system.config.MAX_SAVE_SLOTS
    })


@app.route('/api/saves/save', methods=['POST'])
def api_save_game_slot():
    """Save game to a slot"""
    from systems.save_system import save_system
    from datetime import datetime

    game_state = get_game_state()
    data = request.json

    slot_id = data.get('slot_id', 'slot_1')
    save_name = data.get('save_name')

    success, message = save_system.save_to_slot(game_state, slot_id, save_name)

    if success:
        return jsonify({
            'success': True,
            'message': message,
            'slot_id': slot_id
        })
    else:
        return jsonify({'success': False, 'error': message}), 400


@app.route('/api/saves/load', methods=['POST'])
def api_load_game_slot():
    """Load game from a slot"""
    from systems.save_system import save_system

    data = request.json
    slot_id = data.get('slot_id')

    if not slot_id:
        return jsonify({'error': 'slot_id required'}), 400

    success, save_data, message = save_system.load_from_slot(slot_id)

    if not success:
        return jsonify({'success': False, 'error': message}), 404

    # Load save data into session
    session['game_state_data'] = save_data['game_state']

    return jsonify({
        'success': True,
        'message': message,
        'metadata': save_data['metadata']
    })


@app.route('/api/saves/delete', methods=['POST'])
def api_delete_save_slot():
    """Delete a save slot"""
    from systems.save_system import save_system

    data = request.json
    slot_id = data.get('slot_id')

    if not slot_id:
        return jsonify({'error': 'slot_id required'}), 400

    success, message = save_system.delete_slot(slot_id)

    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 400


@app.route('/api/saves/quicksave', methods=['POST'])
def api_quicksave_game():
    """Quick save"""
    from systems.save_system import save_system

    game_state = get_game_state()

    success, message = save_system.quicksave(game_state)

    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 400


@app.route('/api/saves/autosave', methods=['POST'])
def api_autosave_game():
    """Trigger auto-save"""
    from systems.save_system import save_system
    from datetime import datetime

    game_state = get_game_state()
    data = request.json
    reason = data.get('reason', 'manual')

    # Check if should autosave
    if not save_system.should_autosave(game_state, reason):
        return jsonify({
            'success': True,
            'autosaved': False,
            'message': 'Auto-save not triggered (conditions not met)'
        })

    success, message = save_system.autosave(game_state)

    if success:
        save_system._last_autosave_time = datetime.now()
        return jsonify({
            'success': True,
            'autosaved': True,
            'message': message
        })
    else:
        return jsonify({'success': False, 'error': message}), 400


@app.route('/api/saves/export', methods=['POST'])
def api_export_save_file():
    """Export save file"""
    from systems.save_system import save_system

    data = request.json
    slot_id = data.get('slot_id')
    export_name = data.get('export_name')

    if not slot_id:
        return jsonify({'error': 'slot_id required'}), 400

    success, export_path, message = save_system.export_save(slot_id, export_name)

    if success:
        # Return file for download
        from flask import send_file
        return send_file(
            export_path,
            as_attachment=True,
            download_name=os.path.basename(export_path)
        )
    else:
        return jsonify({'success': False, 'error': message}), 400


@app.route('/api/saves/import', methods=['POST'])
def api_import_save_file():
    """Import save file"""
    from systems.save_system import save_system

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save uploaded file temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.fdrpg') as temp_file:
        file.save(temp_file.name)
        temp_path = temp_file.name

    # Import
    target_slot = request.form.get('target_slot')
    success, message = save_system.import_save(temp_path, target_slot)

    # Clean up temp file
    os.unlink(temp_path)

    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 400


@app.route('/api/saves/config')
def api_save_system_config():
    """Get save system configuration"""
    from systems.save_system import save_system

    return jsonify({
        'success': True,
        'config': {
            'max_save_slots': save_system.config.MAX_SAVE_SLOTS,
            'max_autosaves': save_system.config.MAX_AUTOSAVES,
            'autosave_enabled': save_system.config.AUTOSAVE_ENABLED,
            'autosave_interval_minutes': save_system.config.AUTOSAVE_INTERVAL_MINUTES,
            'autosave_on_major_events': save_system.config.AUTOSAVE_ON_MAJOR_EVENTS,
            'autosave_on_location_change': save_system.config.AUTOSAVE_ON_LOCATION_CHANGE,
            'autosave_on_scene_complete': save_system.config.AUTOSAVE_ON_SCENE_COMPLETE,
            'backup_on_save': save_system.config.BACKUP_ON_SAVE
        }
    })


# ==================== MODDING SYSTEM ENDPOINTS ====================

@app.route('/api/mods/list')
def api_list_mods():
    """List all loaded mods"""
    from systems.mod_system import mod_loader

    summary = mod_loader.get_load_summary()

    return jsonify({
        'success': True,
        'summary': summary
    })


@app.route('/api/mods/load', methods=['POST'])
def api_load_mods():
    """Load all mods from mods directory"""
    from systems.mod_system import mod_loader

    results = mod_loader.load_all_mods()

    return jsonify({
        'success': True,
        'results': results
    })


@app.route('/api/mods/reload', methods=['POST'])
def api_reload_mod():
    """Reload a specific mod (for development)"""
    from systems.mod_system import mod_loader

    data = request.json
    mod_id = data.get('mod_id')

    if not mod_id:
        return jsonify({'success': False, 'error': 'mod_id required'}), 400

    success, errors = mod_loader.reload_mod(mod_id)

    if success:
        return jsonify({
            'success': True,
            'message': f'Mod {mod_id} reloaded successfully'
        })
    else:
        return jsonify({
            'success': False,
            'errors': errors
        }), 400


@app.route('/api/mods/characters')
def api_get_character_mods():
    """Get all character mods"""
    from systems.mod_system import get_character_mods

    character_mods = get_character_mods()

    return jsonify({
        'success': True,
        'character_mods': character_mods,
        'count': len(character_mods)
    })


@app.route('/api/mods/activities')
def api_get_activity_mods():
    """Get all activity mods"""
    from systems.mod_system import get_activity_mods

    activity_mods = get_activity_mods()

    return jsonify({
        'success': True,
        'activity_mods': activity_mods,
        'count': len(activity_mods)
    })


@app.route('/api/mods/techniques')
def api_get_technique_mods():
    """Get all technique mods"""
    from systems.mod_system import get_technique_mods

    technique_mods = get_technique_mods()

    return jsonify({
        'success': True,
        'technique_mods': technique_mods,
        'count': len(technique_mods)
    })


@app.route('/api/mods/scenarios')
def api_get_scenario_mods():
    """Get all scenario mods"""
    from systems.mod_system import get_scenario_mods

    scenario_mods = get_scenario_mods()

    return jsonify({
        'success': True,
        'scenario_mods': scenario_mods,
        'count': len(scenario_mods)
    })


@app.route('/api/mods/integrate', methods=['POST'])
def api_integrate_mod():
    """Integrate a mod into the current game"""
    from systems.mod_system import integrate_mod_into_game

    game_state = get_game_state()
    data = request.json

    mod_id = data.get('mod_id')
    if not mod_id:
        return jsonify({'success': False, 'error': 'mod_id required'}), 400

    success, message = integrate_mod_into_game(mod_id, game_state)

    if success:
        # Save updated game state
        save_game_state(game_state)

        return jsonify({
            'success': True,
            'message': message
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400


@app.route('/api/mods/character/add', methods=['POST'])
def api_add_character_from_mod():
    """Add a character to the game from a mod"""
    from systems.mod_system import mod_loader, ModIntegration

    game_state = get_game_state()
    data = request.json

    mod_id = data.get('mod_id')
    if not mod_id:
        return jsonify({'success': False, 'error': 'mod_id required'}), 400

    mod_data = mod_loader.get_mod(mod_id)
    if not mod_data:
        return jsonify({'success': False, 'error': f'Mod {mod_id} not found'}), 404

    if mod_data['metadata']['mod_type'] != 'character':
        return jsonify({'success': False, 'error': 'Not a character mod'}), 400

    try:
        character = ModIntegration.create_character_from_mod(mod_data, game_state)
        game_state.characters[character.name] = character

        # Save updated game state
        save_game_state(game_state)

        return jsonify({
            'success': True,
            'message': f'Added character: {character.name}',
            'character': {
                'name': character.name,
                'age': character.age,
                'gender': character.gender,
                'rapport': character.rapport,
                'suspicion': character.suspicion
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/mods/validate', methods=['POST'])
def api_validate_mod():
    """Validate a mod file without loading it"""
    from systems.mod_system import mod_loader

    data = request.json
    mod_data = data.get('mod_data')

    if not mod_data:
        return jsonify({'success': False, 'error': 'mod_data required'}), 400

    validation = mod_loader.validate_mod(mod_data)

    return jsonify({
        'success': True,
        'validation': {
            'valid': validation.valid,
            'errors': validation.errors,
            'warnings': validation.warnings,
            'mod_id': validation.mod_id
        }
    })


# ==================== AI PERSONALITY ENDPOINTS ====================

@app.route('/api/ai/personality/<character_name>')
def api_get_personality_state(character_name):
    """Get detailed personality state for a character"""
    from systems.ai_personality import personality_simulator

    game_state = get_game_state()
    char = game_state.get_character(character_name)

    if not char:
        return jsonify({'success': False, 'error': 'Character not found'}), 404

    state = personality_simulator.initialize_personality_state(char, game_state)

    return jsonify({
        'success': True,
        'character': character_name,
        'personality_state': {
            'current_mood': state.current_mood,
            'stress_level': state.stress_level,
            'trust_in_player': state.trust_in_player,
            'independence_level': state.independence_level,
            'player_influence_awareness': state.player_influence_awareness,
            'emotional_vulnerability': state.emotional_vulnerability,
            'resistance_to_change': state.resistance_to_change,
            'active_concerns': state.active_concerns,
            'current_goals': state.current_goals,
            'recent_observations': state.recent_observations,
            'alliance_preferences': state.alliance_preferences,
            'conflict_targets': state.conflict_targets,
            'assertiveness': state.assertiveness,
            'openness_to_player': state.openness_to_player,
            'suspicion_tendency': state.suspicion_tendency
        }
    })


@app.route('/api/ai/predict-reaction', methods=['POST'])
def api_predict_reaction():
    """Predict how character will react to an action"""
    from systems.ai_personality import predict_reaction

    data = request.json
    character_name = data.get('character')
    action_type = data.get('action_type')  # 'hypnosis_attempt', 'emotional_support', 'request_favor', etc.

    if not character_name or not action_type:
        return jsonify({'success': False, 'error': 'character and action_type required'}), 400

    game_state = get_game_state()
    char = game_state.get_character(character_name)

    if not char:
        return jsonify({'success': False, 'error': 'Character not found'}), 404

    prediction = predict_reaction(char, action_type, game_state)

    return jsonify({
        'success': True,
        'character': character_name,
        'action_type': action_type,
        'prediction': prediction
    })


@app.route('/api/ai/emergent-actions/<character_name>')
def api_get_emergent_actions(character_name):
    """Get possible emergent actions for a character"""
    from systems.ai_personality import generate_emergent_actions

    game_state = get_game_state()
    char = game_state.get_character(character_name)

    if not char:
        return jsonify({'success': False, 'error': 'Character not found'}), 404

    actions = generate_emergent_actions(char, game_state)

    return jsonify({
        'success': True,
        'character': character_name,
        'possible_actions': [
            {
                'action_id': action.action_id,
                'action_type': action.action_type,
                'description': action.description,
                'target_character': action.target_character,
                'trigger_reason': action.trigger_reason,
                'potential_outcomes': action.potential_outcomes,
                'likelihood': action.likelihood
            }
            for action in actions
        ]
    })


@app.route('/api/ai/all-personalities')
def api_get_all_personalities():
    """Get personality states for all characters"""
    from systems.ai_personality import personality_simulator

    game_state = get_game_state()
    all_states = {}

    for char_name, char in game_state.characters.items():
        state = personality_simulator.initialize_personality_state(char, game_state)

        all_states[char_name] = {
            'current_mood': state.current_mood,
            'stress_level': state.stress_level,
            'trust_in_player': state.trust_in_player,
            'emotional_vulnerability': state.emotional_vulnerability,
            'player_influence_awareness': state.player_influence_awareness,
            'active_concerns': state.active_concerns[:2],  # Top 2
            'current_goals': state.current_goals[:2]  # Top 2
        }

    return jsonify({
        'success': True,
        'personalities': all_states
    })


# ===== SELF-CARE SYSTEM =====

@app.route('/api/self-care/status')
def get_self_care_status():
    """Get player's current self-care status"""
    game_state = get_game_state()

    from systems.self_care import SelfCareSystem

    modifiers = SelfCareSystem.get_gameplay_modifiers(game_state.player.self_care)

    return jsonify({
        'success': True,
        'self_care': {
            'hunger': game_state.player.self_care.hunger,
            'hygiene': game_state.player.self_care.hygiene,
            'energy': game_state.player.self_care.energy,
            'bladder': game_state.player.self_care.bladder,
            'last_meal_time': game_state.player.self_care.last_meal_time,
            'last_shower_time': game_state.player.self_care.last_shower_time,
            'last_sleep_time': game_state.player.self_care.last_sleep_time
        },
        'modifiers': modifiers
    })


@app.route('/api/self-care/action', methods=['POST'])
def perform_self_care_action():
    """Perform a self-care action (eat, shower, sleep, etc.)"""
    game_state = get_game_state()
    action = request.json.get('action')

    from systems.self_care import SelfCareSystem

    # Validate action parameter
    if not action:
        return jsonify({'success': False, 'error': 'No action specified'})

    # Check if action is allowed
    action_category = 'self_care'
    can_do, reason = SelfCareSystem.can_perform_action(game_state.player.self_care, action_category)
    if not can_do:
        return jsonify({'success': False, 'error': reason})

    # Perform the action
    current_time = game_state.game_time.get_formatted_time()
    result = SelfCareSystem.perform_action(game_state, action, current_time)

    if not result['success']:
        error_msg = result['message'] if result['message'] else f'Unknown action: {action}'
        return jsonify({'success': False, 'error': error_msg})

    # Advance time by the action's cost
    time_warnings = game_state.advance_time_with_needs(result['time_cost'])

    # Save updated state
    save_game_state(game_state)

    # Get updated modifiers
    modifiers = SelfCareSystem.get_gameplay_modifiers(game_state.player.self_care)

    return jsonify({
        'success': True,
        'message': result['message'],
        'time_passed': result['time_cost'],
        'new_time': game_state.game_time.get_formatted_time(),
        'warnings': list(time_warnings.values()),
        'self_care': {
            'hunger': game_state.player.self_care.hunger,
            'hygiene': game_state.player.self_care.hygiene,
            'energy': game_state.player.self_care.energy,
            'bladder': game_state.player.self_care.bladder
        },
        'modifiers': modifiers
    })


# ===== ADVANCED HYPNOSIS SYSTEM =====

@app.route('/api/mastery-level')
def get_mastery_level():
    """Get player's hypnosis mastery level and stats"""
    game_state = get_game_state()

    from systems.advanced_hypnosis import AdvancedHypnosisSystem

    # Ensure mastery level exists
    if not hasattr(game_state.player, 'mastery_level'):
        from systems.advanced_hypnosis import MasteryLevel
        game_state.player.mastery_level = MasteryLevel()

    mastery = game_state.player.mastery_level
    sp_reduction, success_bonus = mastery.get_mastery_bonuses()

    return jsonify({
        'success': True,
        'mastery': {
            'level': mastery.get_overall_mastery(),
            'description': AdvancedHypnosisSystem.get_mastery_level_description(mastery.get_overall_mastery()),
            'success_rate': mastery.get_success_rate(),
            'sp_reduction': sp_reduction,
            'success_bonus': success_bonus,
            'stats': {
                'total_phs_planted': mastery.total_phs_planted,
                'successful_activations': mastery.successful_activations,
                'failed_activations': mastery.failed_activations,
                'reinforcements': mastery.reinforcements_done,
                'combos': mastery.combos_completed,
                'group_sessions': mastery.group_sessions_done,
                'resistance_breaks': mastery.resistance_breaks
            }
        }
    })


if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5000)
