// Family Dynamics RPG - Game JavaScript

let selectedCharacter = null;
let isWaitingForResponse = false;

// Initialize when page loads
$(document).ready(function() {
    // Enable enter key to send message
    $('#message-input').keypress(function(e) {
        if (e.which === 13 && !isWaitingForResponse) {
            sendMessage();
        }
    });

    // Load initial game state
    updateGameState();

    // Load character schedules
    updateCharacterSchedules();

    // Load character sprites
    loadCharacterSprites();

    // Start ambient events polling (every 15-25 seconds for variety)
    startAmbientEvents();
});

// Load all character sprites
function loadCharacterSprites() {
    // Get all character names from character cards
    $('.character-card').each(function() {
        const characterName = $(this).data('character');
        const spriteContainerId = `sprite-${characterName}`;

        // Fetch character outfit
        $.ajax({
            url: `/api/character/${characterName}`,
            method: 'GET',
            success: function(data) {
                // Render sprite with template fallback support
                renderCharacterSprite(characterName, data.outfit, spriteContainerId, {
                    width: 80,
                    height: 120,
                    clickable: false,
                    showPlaceholder: true,
                    age: data.age,
                    gender: data.gender
                });
            }
        });
    });
}

// Select a character to talk to
function selectCharacter(characterName) {
    selectedCharacter = characterName;

    // Update UI
    $('.character-card').removeClass('active');
    $(`.character-card[data-character="${characterName}"]`).addClass('active');
    $('#selected-character').text(characterName);

    // Enable input and update placeholder
    $('#message-input').prop('disabled', false).attr('placeholder', 'Type your message...');
    $('#send-btn').prop('disabled', false);
    $('#plant-suggestion-btn').prop('disabled', false);

    // Focus the input so user can start typing immediately
    $('#message-input').focus();

    // Add system message
    addSystemMessage(`Now talking with ${characterName}. Type your message below.`);
}

// Wrapper functions for direct character actions (called from character cards)
function openCharacterProfile(characterName) {
    if (characterName) {
        // Called from character card button - select character first
        selectedCharacter = characterName;
        $('#selected-character').text(characterName);
    }

    // Now call the internal profile opening logic
    _openCharacterProfileModal();
}

function openPlantSuggestionFor(characterName) {
    if (characterName) {
        // Called from character card button - select character first
        selectedCharacter = characterName;
        $('#selected-character').text(characterName);
    }

    // Now call the internal plant suggestion logic
    _openPlantSuggestionModal();
}

// Send message to character
function sendMessage() {
    if (!selectedCharacter || isWaitingForResponse) return;

    const message = $('#message-input').val().trim();
    if (!message) return;

    // Disable input while waiting
    isWaitingForResponse = true;
    $('#message-input').prop('disabled', true);
    $('#send-btn').html('<div class="loading"></div>').prop('disabled', true);

    // Add player message to dialogue
    addDialogueMessage('You', message);

    // Clear input
    $('#message-input').val('');

    // Send to API
    $.ajax({
        url: '/api/talk',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            character: selectedCharacter,
            message: message
        }),
        success: function(data) {
            // Add character response
            addDialogueMessage(selectedCharacter, data.response);

            // Show any changes
            if (data.changes && data.changes.length > 0) {
                data.changes.forEach(change => {
                    if (change.type === 'phs_activation') {
                        // Special display for PHS activations
                        addPHSActivationMessage(change.message);
                    } else {
                        addSystemMessage(change.message);
                    }
                });
            }

            // Update character card
            updateCharacterCard(selectedCharacter, data.character_state);

            // Update game state
            updateGameState();

            // Check for dialogue choices
            checkForDialogueChoices(message);

            // Re-enable input
            isWaitingForResponse = false;
            $('#message-input').prop('disabled', false);
            $('#send-btn').html('Send').prop('disabled', false);
            $('#message-input').focus();
        },
        error: function(xhr, status, error) {
            addSystemMessage('Error: Failed to get response. Please try again.');
            isWaitingForResponse = false;
            $('#message-input').prop('disabled', false);
            $('#send-btn').html('Send').prop('disabled', false);
        }
    });
}

// Add dialogue message to box
function addDialogueMessage(speaker, text) {
    const messageHtml = `
        <div class="dialogue-message">
            <div class="dialogue-speaker">${speaker}:</div>
            <div class="dialogue-text">${text}</div>
        </div>
    `;
    $('#dialogue-box').append(messageHtml);
    scrollToBottom();
}

// Add system message
function addSystemMessage(text) {
    const messageHtml = `
        <div class="dialogue-message">
            <div class="system-message">${text}</div>
        </div>
    `;
    $('#dialogue-box').append(messageHtml);
    scrollToBottom();
}

// Add PHS activation message with special styling
function addPHSActivationMessage(text) {
    const messageHtml = `
        <div class="dialogue-message">
            <div class="phs-activation-message" style="
                background: linear-gradient(135deg, rgba(233, 69, 96, 0.2) 0%, rgba(255, 140, 0, 0.2) 100%);
                border-left: 4px solid var(--highlight-color);
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: 8px;
                font-weight: 600;
                color: #ffcc00;
                text-shadow: 0 0 10px rgba(255, 204, 0, 0.5);
                animation: pulse 2s ease-in-out;
            ">${text}</div>
        </div>
    `;
    $('#dialogue-box').append(messageHtml);
    scrollToBottom();
}

// Scroll dialogue box to bottom
function scrollToBottom() {
    const dialogueBox = document.getElementById('dialogue-box');
    dialogueBox.scrollTop = dialogueBox.scrollHeight;
}

// Check for dialogue choices after character responds
function checkForDialogueChoices(playerMessage) {
    if (!selectedCharacter) return;

    $.ajax({
        url: '/api/get-dialogue-choices',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            character: selectedCharacter,
            player_message: playerMessage
        }),
        success: function(data) {
            if (data.has_choices && data.choices.length > 0) {
                showDialogueChoices(data.context, data.choices);
            } else {
                hideDialogueChoices();
            }
        },
        error: function() {
            hideDialogueChoices();
        }
    });
}

// Show dialogue choice buttons
function showDialogueChoices(context, choices) {
    const choicesContainer = $('#choices-container');
    choicesContainer.empty();

    choices.forEach(choice => {
        const isDisabled = choice.requires_rapport > 0 || choice.sp_cost > 0;
        const disabledClass = isDisabled ? '' : ''; // We'll check dynamically

        let choiceHtml = `
            <div class="choice-btn" data-choice-id="${choice.choice_id}" data-context="${context}">
                <div class="choice-text">${choice.text}</div>
                <div class="choice-description">${choice.description}</div>
        `;

        // Add requirements/costs if any
        if (choice.requires_rapport > 0) {
            choiceHtml += `<div class="choice-requirement">Requires ${choice.requires_rapport}+ rapport</div>`;
        }
        if (choice.sp_cost > 0) {
            choiceHtml += `<span class="choice-cost">Cost: ${choice.sp_cost} SP</span>`;
        }

        choiceHtml += `</div>`;

        const choiceElement = $(choiceHtml);

        // Add click handler
        choiceElement.on('click', function() {
            selectDialogueChoice(choice.choice_id, context);
        });

        choicesContainer.append(choiceElement);
    });

    // Show the choices panel
    $('#dialogue-choices').slideDown(300);

    // Disable regular text input while choices are shown
    $('#message-input').prop('disabled', true).attr('placeholder', 'Choose a response from the options above...');
    $('#send-btn').prop('disabled', true);

    scrollToBottom();
}

// Hide dialogue choices
function hideDialogueChoices() {
    $('#dialogue-choices').slideUp(300);

    // Re-enable text input
    if (selectedCharacter && !isWaitingForResponse) {
        $('#message-input').prop('disabled', false).attr('placeholder', `Talk to ${selectedCharacter}...`);
        $('#send-btn').prop('disabled', false);
    }
}

// Handle dialogue choice selection
function selectDialogueChoice(choiceId, context) {
    if (!selectedCharacter || isWaitingForResponse) return;

    // Hide choices and disable input
    hideDialogueChoices();
    isWaitingForResponse = true;
    $('#message-input').prop('disabled', true);
    $('#send-btn').html('<div class="loading"></div>').prop('disabled', true);

    // Send choice to API
    $.ajax({
        url: '/api/select-dialogue-choice',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            character: selectedCharacter,
            choice_id: choiceId,
            context: context
        }),
        success: function(data) {
            // Show what the player said
            addDialogueMessage('You', data.player_said);

            // Show character's response
            addDialogueMessage(selectedCharacter, data.response);

            // Show changes/consequences
            if (data.changes && data.changes.length > 0) {
                data.changes.forEach(change => {
                    addSystemMessage(change);
                });
            }

            // Update character card with new state
            updateCharacterCard(selectedCharacter, data.character_state);

            // Update game state
            updateGameState();

            // Check for new dialogue choices
            checkForDialogueChoices(data.player_said);

            // Re-enable input
            isWaitingForResponse = false;
            $('#message-input').prop('disabled', false);
            $('#send-btn').html('Send').prop('disabled', false);
            $('#message-input').focus();
        },
        error: function(xhr) {
            const errorMsg = xhr.responseJSON?.error || 'Failed to process choice';
            addSystemMessage(`Error: ${errorMsg}`);

            isWaitingForResponse = false;
            $('#message-input').prop('disabled', false);
            $('#send-btn').html('Send').prop('disabled', false);

            // Re-show choices on error
            checkForDialogueChoices('');
        }
    });
}

// Update character card
function updateCharacterCard(characterName, state) {
    const card = $(`.character-card[data-character="${characterName}"]`);
    const rapportPercent = (state.rapport / 20 * 100);

    // Get old rapport value to detect changes
    const oldRapport = parseInt(card.find('.rapport-value').text()) || 0;
    const newRapport = state.rapport;

    // Update rapport bar with animation
    card.find('.rapport-fill').css('width', rapportPercent + '%');
    card.find('.rapport-value').text(newRapport);
    card.find('.character-info').last().html(`Rapport: <span class="rapport-value" data-character="${characterName}">${newRapport}</span>/20 | ${state.emotional_state}`);

    // If rapport increased, add visual effects
    if (newRapport > oldRapport) {
        // Add sparkle particles
        createSparkleEffect(card);

        // Add pulse effect to card
        card.addClass('rapport-pulse');
        setTimeout(() => card.removeClass('rapport-pulse'), 600);

        // Check if we hit a milestone
        checkRapportMilestone(characterName, oldRapport, newRapport);
    }

    // Update milestone indicator
    updateMilestoneIndicator(characterName, newRapport);
}

// Create sparkle particle effects
function createSparkleEffect(element) {
    const sparkles = ['✨', '⭐', '💫', '🌟'];
    const card = element;
    const cardOffset = card.offset();
    const cardWidth = card.width();
    const cardHeight = card.height();

    // Create 3-5 sparkles
    const count = 3 + Math.floor(Math.random() * 3);
    for (let i = 0; i < count; i++) {
        setTimeout(() => {
            const sparkle = $('<div class="sparkle-particle"></div>');
            sparkle.text(sparkles[Math.floor(Math.random() * sparkles.length)]);

            // Random position within card
            const x = Math.random() * cardWidth;
            const y = Math.random() * cardHeight;

            sparkle.css({
                left: x + 'px',
                top: y + 'px'
            });

            card.css('position', 'relative').append(sparkle);

            // Remove after animation
            setTimeout(() => sparkle.remove(), 1000);
        }, i * 100);
    }
}

// Check if rapport milestone was reached
function checkRapportMilestone(characterName, oldRapport, newRapport) {
    const milestones = [5, 10, 15, 20];

    for (const milestone of milestones) {
        if (oldRapport < milestone && newRapport >= milestone) {
            // Milestone reached!
            showMilestoneCelebration(characterName, milestone);

            // Flash SP counter if SP was gained
            if (milestone <= 20) {
                flashSPCounter();
            }
            break;
        }
    }
}

// Show milestone celebration modal
function showMilestoneCelebration(characterName, milestone) {
    let title = '';
    let message = '';

    if (milestone === 5) {
        title = '🎊 Acquaintance!';
        message = `${characterName} is starting to warm up to you!`;
    } else if (milestone === 10) {
        title = '🎉 Friend!';
        message = `${characterName} now considers you a friend!`;
    } else if (milestone === 15) {
        title = '💖 Close Friend!';
        message = `${characterName} trusts you deeply!`;
    } else if (milestone === 20) {
        title = '✨ Maximum Rapport!';
        message = `${characterName} has complete trust in you!`;
    }

    const html = `
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem; animation: pulse 1s infinite;">🎉</div>
            <h2 style="color: var(--highlight-color); margin-bottom: 1rem;">${title}</h2>
            <p style="font-size: 1.2rem; margin-bottom: 1rem;">${message}</p>
            <div style="background: rgba(255, 215, 0, 0.2); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <strong style="color: var(--warning-color); font-size: 1.1rem;">+1 SP Earned!</strong><br>
                <span style="font-size: 0.9rem; color: var(--text-secondary);">Rapport milestone reached: ${milestone}/20</span>
            </div>
            <button class="btn btn-primary" onclick="closeModal('rapportMilestoneModal')">Continue</button>
        </div>
    `;

    // Create modal if it doesn't exist
    if ($('#rapportMilestoneModal').length === 0) {
        $('body').append(`
            <div id="rapportMilestoneModal" class="modal">
                <div class="modal-content" style="max-width: 500px;">
                    <div id="rapportMilestoneContent"></div>
                </div>
            </div>
        `);
    }

    $('#rapportMilestoneContent').html(html);
    openModal('rapportMilestoneModal');
}

// Flash SP counter
function flashSPCounter() {
    const spDisplay = $('#sp-display');
    spDisplay.addClass('flash-effect');
    setTimeout(() => spDisplay.removeClass('flash-effect'), 500);
}

// Update milestone indicator on character card
function updateMilestoneIndicator(characterName, rapport) {
    const indicator = $(`.milestone-indicator[data-character="${characterName}"]`);

    if (rapport >= 20) {
        indicator.html('✨ Maximum rapport!').css('color', 'var(--success-color)');
    } else {
        const nextMilestone = Math.ceil(rapport / 5) * 5;
        indicator.html(`⭐ Next milestone: ${nextMilestone}/20 (+1 SP)`).css('color', 'var(--warning-color)');
    }
}

// Update game state display
function updateGameState() {
    $.ajax({
        url: '/api/game-state',
        method: 'GET',
        success: function(data) {
            $('#sp-display').text(data.player.suggestion_points);
            $('#money-display').text(`$${data.player.money}`);
            $('#skill-level').text(data.player.skill_level.toUpperCase());
            $('#techniques-count').text(`${data.player.techniques_mastered}/${data.player.total_techniques}`);
        }
    });

    // Also update time display
    updateTimeDisplay();
}

// Update time display
function updateTimeDisplay() {
    $.ajax({
        url: '/api/current-time',
        method: 'GET',
        success: function(data) {
            $('#current-time').text(data.time);
            $('#current-date').text(`${data.day_name}, ${data.date.split(', ')[1]}`);
            $('#current-period').text(data.period);
        }
    });
}

// Advance time by specified minutes
function advanceTime(minutes) {
    $.ajax({
        url: '/api/advance-time',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ minutes: minutes }),
        success: function(data) {
            // Update time display
            $('#current-time').text(data.time);
            $('#current-date').text(`${data.events.current_period}, ${data.date.split(', ')[1]}`);
            $('#current-period').text(data.period);

            // Show time advancement message
            let timeMessage = `⏱️ Time advanced by ${minutes} minutes → ${data.time}`;
            addSystemMessage(timeMessage);

            // Show any event messages (new day, new period)
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => addSystemMessage(msg));
            }

            // If schedules changed, show character updates
            if (data.schedule_updates) {
                data.schedule_updates.forEach(update => {
                    const charCard = $(`.character-card[data-character="${update.character}"]`);
                    // Update the character's activity indicator if it exists
                    updateCharacterActivity(update.character, update.activity);
                });
            }

            // Update game state and character schedules
            updateGameState();
            updateCharacterSchedules();
        },
        error: function() {
            addSystemMessage('⚠️ Failed to advance time.');
        }
    });
}

// Load and display available activities
function loadActivities() {
    $.ajax({
        url: '/api/available-activities',
        method: 'GET',
        success: function(data) {
            displayActivities(data.activities, data.character_present);
        },
        error: function() {
            $('#activities-list').html('<p class="no-activities">No activities available here.</p>');
        }
    });
}

// Display activities
function displayActivities(activities, characterPresent) {
    const activitiesList = $('#activities-list');

    if (!activities || activities.length === 0) {
        activitiesList.html('<p class="no-activities">No activities available here.</p>');
        return;
    }

    let html = '';
    activities.forEach(activity => {
        const isPreferred = activity.is_preferred ? '⭐' : '';
        const cost = activity.sp_cost > 0 ? `<span class="activity-cost">${activity.sp_cost} SP</span>` : '';
        const rewards = [];

        if (activity.rapport_gain > 0) rewards.push(`+${activity.rapport_gain} Rapport`);
        if (activity.money_reward > 0) rewards.push(`$${activity.money_reward}`);
        if (activity.sp_reward > 0) rewards.push(`+${activity.sp_reward} SP`);
        if (activity.allows_phs) rewards.push(`PHS +${activity.phs_bonus}%`);

        const rewardsText = rewards.length > 0 ? `<div class="activity-rewards">${rewards.join(', ')}</div>` : '';

        html += `
            <div class="activity-btn" data-activity-id="${activity.activity_id}" data-character="${characterPresent || ''}">
                <div class="activity-header">
                    <span class="activity-icon">${activity.icon}</span>
                    <span class="activity-name">${activity.name} ${isPreferred}</span>
                    <span class="activity-duration">${activity.duration_minutes}m</span>
                    ${cost}
                </div>
                <div class="activity-description">${activity.description}</div>
                ${rewardsText}
            </div>
        `;
    });

    activitiesList.html(html);

    // Add click handlers
    $('.activity-btn').on('click', function() {
        const activityId = $(this).data('activity-id');
        const character = $(this).data('character');
        startActivity(activityId, character);
    });
}

// Start an activity
function startActivity(activityId, characterName) {
    if (!confirm('Start this activity? Time will pass.')) return;

    $.ajax({
        url: '/api/start-activity',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            activity_id: activityId,
            character_name: characterName || null
        }),
        success: function(data) {
            // Show activity completion message
            addSystemMessage(`✨ ${data.activity_name} completed!`);
            addSystemMessage(data.message);

            // Show all changes
            if (data.changes && data.changes.length > 0) {
                data.changes.forEach(change => addSystemMessage(change));
            }

            // Show PHS opportunity if available
            if (data.phs_opportunity) {
                addSystemMessage(`💡 Perfect moment for a suggestion! (+${data.phs_bonus}% success)`);
                // Optionally auto-open plant suggestion modal
                // _openPlantSuggestionModal();
            }

            // Update character card if applicable
            if (data.character_state && characterName) {
                updateCharacterCard(characterName, data.character_state);
            }

            // Update game state
            updateGameState();
            loadActivities();
            updateCharacterList();
        },
        error: function(xhr) {
            const errorMsg = xhr.responseJSON?.error || 'Failed to start activity';
            addSystemMessage(`❌ ${errorMsg}`);
        }
    });
}

// Open skill tree modal
function openSkillTree() {
    $.ajax({
        url: '/api/skill-tree',
        method: 'GET',
        success: function(data) {
            // Update header info
            $('#modal-skill-level').text(data.skill_level.toUpperCase());
            $('#modal-techniques-count').text(data.techniques_mastered);
            $('#modal-bonuses').text(`-${data.total_sp_reduction} SP, +${data.total_success_bonus}% success`);

            // Build skill tree
            const categories = {
                'basic': [],
                'intermediate': [],
                'advanced': [],
                'master': []
            };

            Object.entries(data.techniques).forEach(([techId, tech]) => {
                categories[tech.category].push({id: techId, ...tech});
            });

            let html = '';
            Object.entries(categories).forEach(([category, techniques]) => {
                html += `
                    <div class="skill-category">
                        <div class="category-title">${category} Techniques</div>
                `;

                techniques.forEach(tech => {
                    let statusClass = tech.status;
                    let statusIcon = {
                        'mastered': '🟢',
                        'learning': '🟡',
                        'available': '⚪',
                        'locked': '🔴'
                    }[tech.status];

                    let statusText = {
                        'mastered': 'MASTERED',
                        'learning': `LEARNING ${tech.progress}%`,
                        'available': 'AVAILABLE',
                        'locked': 'LOCKED'
                    }[tech.status];

                    html += `
                        <div class="technique-item ${statusClass}">
                            <div class="technique-header">
                                <div class="technique-name">${statusIcon} ${tech.name}</div>
                                <div class="technique-status">${statusText}</div>
                            </div>
                            <div style="font-size: 0.9rem; color: var(--text-secondary); margin: 0.5rem 0;">
                                ${tech.description}
                            </div>
                    `;

                    if (tech.progress > 0 && tech.progress < 100) {
                        html += `
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${tech.progress}%"></div>
                            </div>
                        `;
                    }

                    if (tech.sp_cost_reduction > 0 || tech.success_rate_bonus > 0) {
                        html += `
                            <div style="font-size: 0.85rem; color: var(--highlight-color); margin-top: 0.5rem;">
                        `;
                        if (tech.sp_cost_reduction > 0) {
                            html += `-${tech.sp_cost_reduction} SP cost `;
                        }
                        if (tech.success_rate_bonus > 0) {
                            html += `+${tech.success_rate_bonus}% success`;
                        }
                        html += '</div>';
                    }

                    if (tech.prerequisites && tech.prerequisites.length > 0) {
                        const prereqNames = tech.prerequisites.map(p => data.techniques[p].name).join(', ');
                        html += `
                            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.5rem;">
                                Requires: ${prereqNames}
                            </div>
                        `;
                    }

                    html += '</div>';
                });

                html += '</div>';
            });

            $('#skill-tree-content').html(html);
            openModal('skillTreeModal');
        }
    });
}

// Helper function to determine PHS type
function detectPHSType(trigger, response) {
    const triggerLower = trigger.toLowerCase();
    const responseLower = response.toLowerCase();

    // Behavioral prompts - actions and behaviors
    if (triggerLower.includes('getting dressed') ||
        triggerLower.includes('choosing clothes') ||
        triggerLower.includes('dressing') ||
        responseLower.includes('wear') ||
        responseLower.includes('dress')) {
        return { type: 'Behavioral Prompt', icon: '👗' };
    }

    if (responseLower.includes('call me') ||
        responseLower.includes('visit me') ||
        responseLower.includes('come to') ||
        responseLower.includes('meet me')) {
        return { type: 'Behavioral Prompt', icon: '🚶' };
    }

    // Emotional nudges - feelings and attractions
    if (responseLower.includes('feel') ||
        responseLower.includes('attracted') ||
        responseLower.includes('like me') ||
        responseLower.includes('love') ||
        responseLower.includes('trust')) {
        return { type: 'Emotional Nudge', icon: '💭' };
    }

    // Compliance triggers - obedience and agreement
    if (responseLower.includes('obey') ||
        responseLower.includes('agree') ||
        responseLower.includes('do what') ||
        responseLower.includes('listen to')) {
        return { type: 'Compliance Trigger', icon: '🎯' };
    }

    // Default to behavioral prompt
    return { type: 'Behavioral Prompt', icon: '🎯' };
}

// Open character profile modal (internal function)
function _openCharacterProfileModal() {
    if (!selectedCharacter) {
        addSystemMessage('Please select a character first.');
        return;
    }

    $.ajax({
        url: `/api/character/${selectedCharacter}`,
        method: 'GET',
        success: function(char) {
            $('#profile-character-name').text(char.name);

            // Create tabs
            let html = `
                <div class="profile-tabs" style="display: flex; gap: 0.5rem; margin-bottom: 1.5rem; border-bottom: 2px solid var(--accent-color);">
                    <button class="profile-tab active" onclick="switchProfileTab('overview')" data-tab="overview" style="flex: 1; padding: 0.8rem; background: var(--highlight-color); color: white; border: none; border-radius: 8px 8px 0 0; cursor: pointer; font-weight: 600;">
                        👤 Overview
                    </button>
                    <button class="profile-tab" onclick="switchProfileTab('suggestions')" data-tab="suggestions" style="flex: 1; padding: 0.8rem; background: var(--accent-color); color: var(--text-primary); border: none; border-radius: 8px 8px 0 0; cursor: pointer; font-weight: 600;">
                        🎯 Suggestions (${char.active_phs ? char.active_phs.length : 0}/${char.max_phs || 3})
                    </button>
                </div>

                <div class="profile-tab-content" data-tab-content="overview">
            `;

            // Overview tab content
            html += `
                <div style="margin-bottom: 2rem;">
                    <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">Basic Information</h3>
                    <div style="line-height: 2;">
                        <strong>Age:</strong> ${char.age}<br>
                        <strong>Occupation:</strong> ${char.occupation}<br>
                        <strong>Personality:</strong> ${char.personality}<br>
                    </div>
                </div>

                <div style="margin-bottom: 2rem;">
                    <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">Current Status</h3>
                    <div style="line-height: 2;">
                        <strong>Rapport (with you):</strong> ${char.rapport}/20<br>
                        <strong>Emotional State:</strong> ${char.emotional_state}<br>
                        <strong>Resistance:</strong> ${char.resistance}%<br>
                    </div>
                </div>

                <div style="margin-bottom: 2rem;">
                    <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">Appearance</h3>
                    <div style="line-height: 2;">
                        <strong>Wearing:</strong> ${char.outfit_description || char.clothing}<br>
                        <strong>Meaning:</strong> ${char.clothing_meaning}<br>
            `;

            // Add clothing effect if present
            if (char.clothing_modifier !== undefined && char.clothing_modifier !== 0) {
                let effectColor = char.clothing_modifier > 0 ? 'var(--success-color)' : 'var(--danger-color)';
                let effectIcon = char.clothing_modifier > 0 ? '✓' : '✗';
                html += `
                        <div style="margin-top: 1rem; padding: 0.8rem; background: rgba(233, 69, 96, 0.15); border-left: 3px solid ${effectColor}; border-radius: 8px;">
                            <strong style="color: ${effectColor};">${effectIcon} Suggestibility Effect:</strong><br>
                            <span style="font-size: 0.9rem;">${char.clothing_effect}</span>
                        </div>
                `;
            }

            html += `
                    </div>
                </div>
            `;

            // Add suspicion section
            if (char.suspicion_status) {
                const sus = char.suspicion_status;
                html += `
                    <div style="margin-bottom: 2rem;">
                        <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">
                            ${sus.icon} Suspicion Level
                        </h3>
                        <div style="padding: 1rem; background: var(--accent-color); border-radius: 8px; border-left: 4px solid ${sus.color};">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span style="font-weight: bold; color: ${sus.color};">${sus.status}</span>
                                <span style="font-weight: bold;">${sus.level}/100</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); height: 20px; border-radius: 10px; overflow: hidden; margin-bottom: 0.5rem;">
                                <div style="background: ${sus.bar_color}; height: 100%; width: ${sus.level}%; transition: width 0.3s;"></div>
                            </div>
                            <div style="font-size: 0.9rem; color: var(--text-secondary);">
                                ${sus.warning}
                            </div>
                `;

                // Show what characters they're suspicious about
                if (char.character_suspicions && Object.keys(char.character_suspicions).length > 0) {
                    html += `
                            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
                                <div style="font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: bold;">Concerned about:</div>
                    `;
                    for (const [targetName, suspicionLevel] of Object.entries(char.character_suspicions)) {
                        html += `
                                <div style="font-size: 0.85rem; margin-bottom: 0.3rem;">
                                    • ${targetName}: ${suspicionLevel}% suspicious
                                </div>
                        `;
                    }
                    html += `
                            </div>
                    `;
                }

                html += `
                        </div>
                    </div>
                `;
            }

            // Add relationships section
            if (char.relationships && Object.keys(char.relationships).length > 0) {
                html += `
                    <div style="margin-bottom: 2rem;">
                        <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">Relationships with Others</h3>
                `;

                for (const [otherChar, score] of Object.entries(char.relationships)) {
                    const rapport_bar = '█'.repeat(score) + '░'.repeat(20 - score);
                    let relationship_desc = '';
                    if (score >= 15) relationship_desc = '💜 Very Close';
                    else if (score >= 10) relationship_desc = '💙 Good Friends';
                    else if (score >= 5) relationship_desc = '🤝 Friendly';
                    else if (score >= 0) relationship_desc = '😐 Neutral';
                    else relationship_desc = '😠 Hostile';

                    html += `
                        <div style="background: var(--accent-color); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.8rem;">
                            <div style="font-weight: bold; margin-bottom: 0.5rem;">${otherChar}</div>
                            <div style="font-family: monospace; font-size: 0.8rem; margin-bottom: 0.3rem;">[${rapport_bar}] ${score}/20</div>
                            <div style="font-size: 0.9rem; color: var(--text-secondary);">${relationship_desc}</div>
                        </div>
                    `;
                }

                html += '</div>';
            }

            // Add character interactions section
            if (char.character_interactions && char.character_interactions.length > 0) {
                html += `
                    <div style="margin-bottom: 2rem;">
                        <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">Recent Interactions with Others</h3>
                        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">
                            Past conversations with other characters
                        </div>
                `;

                const recentInteractions = char.character_interactions.slice(-5).reverse();
                recentInteractions.forEach(interaction => {
                    html += `
                        <div style="background: var(--accent-color); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                            <div style="font-weight: bold; margin-bottom: 0.5rem; color: var(--highlight-color);">
                                Conversation with ${interaction.with_character}
                            </div>
                            <div style="margin-bottom: 0.5rem; font-size: 0.9rem;">
                                ${interaction.summary || interaction.snippet || 'Talked together'}
                            </div>
                            <div style="font-size: 0.8rem; color: var(--text-secondary);">
                                ${interaction.timestamp || 'Recently'}
                            </div>
                        </div>
                    `;
                });

                html += '</div>';
            }

            // Add memories section
            if (char.memories && char.memories.length > 0) {
                html += `
                    <div style="margin-bottom: 2rem;">
                        <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">Memories (${char.memories.length})</h3>
                `;

                const sortedMemories = char.memories.sort((a, b) => b.importance - a.importance).slice(0, 5);
                sortedMemories.forEach(mem => {
                    const icons = {
                        'conversation': '💬',
                        'emotional_moment': '💝',
                        'important_event': '⭐',
                        'phs_planted': '🎯',
                        'phs_triggered': '✨'
                    };
                    const icon = icons[mem.type] || '📝';
                    const stars = '★'.repeat(mem.importance) + '☆'.repeat(10 - mem.importance);

                    html += `
                        <div style="background: var(--accent-color); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                            <div style="margin-bottom: 0.5rem;">
                                ${icon} <strong>${mem.type.replace('_', ' ').toUpperCase()}</strong>
                                <span style="color: var(--warning-color); font-size: 0.85rem;">${stars}</span>
                            </div>
                            <div style="margin-bottom: 0.3rem;">${mem.content}</div>
                            ${mem.emotional_context ? `<div style="font-size: 0.85rem; color: var(--text-secondary); font-style: italic;">They were feeling: ${mem.emotional_context}</div>` : ''}
                        </div>
                    `;
                });

                html += '</div>';
            }

            html += '</div>'; // End overview tab

            // Suggestions tab content
            html += `<div class="profile-tab-content" data-tab-content="suggestions" style="display: none;">`;

            if (char.active_phs && char.active_phs.length > 0) {
                html += `
                    <div style="text-align: center; margin-bottom: 2rem; padding: 1rem; background: var(--accent-color); border-radius: 8px;">
                        <h3 style="color: var(--highlight-color); margin: 0;">${char.name.toUpperCase()} - ACTIVE SUGGESTIONS (${char.active_phs.length}/${char.max_phs || 3} slots)</h3>
                    </div>
                `;

                char.active_phs.forEach((phs, i) => {
                    const phsType = detectPHSType(phs.trigger, phs.response);
                    const activationChance = phs.activation_chance;
                    const barWidth = activationChance;
                    const barColor = activationChance >= 70 ? 'var(--success-color)' :
                                     activationChance >= 50 ? 'var(--warning-color)' : 'var(--danger-color)';

                    html += `
                        <div style="background: var(--accent-color); padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid ${barColor};">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                <div style="font-weight: bold; font-size: 1.1rem; color: var(--highlight-color);">
                                    ${phsType.icon} "${phs.response}"
                                </div>
                            </div>

                            <div style="margin-bottom: 0.8rem; padding: 0.5rem; background: rgba(102, 126, 234, 0.1); border-radius: 5px;">
                                <strong>Type:</strong> ${phsType.type}
                            </div>

                            <div style="margin-bottom: 0.8rem;">
                                <strong>Trigger:</strong> ${phs.trigger}
                            </div>

                            <div style="margin-bottom: 0.8rem;">
                                <strong>Activation:</strong> ${activationChance}%
                                <div style="background: rgba(255,255,255,0.1); height: 20px; border-radius: 10px; overflow: hidden; margin-top: 0.3rem;">
                                    <div style="background: ${barColor}; height: 100%; width: ${barWidth}%; transition: width 0.3s;"></div>
                                </div>
                            </div>

                            <div style="margin-bottom: 1rem; font-size: 0.9rem; color: var(--text-secondary);">
                                <strong>Reinforced:</strong> ${phs.reinforcements} time(s)
                            </div>

                            <div style="display: flex; gap: 0.5rem;">
                                <button class="btn btn-small" onclick="reinforcePHS('${char.name}', ${i})" style="flex: 1; background: var(--success-color); color: white;">
                                    ✨ Reinforce (1 SP)
                                </button>
                                <button class="btn btn-small" onclick="removePHS('${char.name}', ${i})" style="flex: 1; background: var(--danger-color); color: white;">
                                    ✗ Remove
                                </button>
                            </div>
                        </div>
                    `;
                });
            } else {
                html += `
                    <div style="text-align: center; padding: 3rem;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
                        <h3 style="color: var(--text-secondary); margin-bottom: 1rem;">No Active Suggestions</h3>
                        <p style="color: var(--text-secondary); margin-bottom: 2rem;">
                            ${char.name} has no active post-hypnotic suggestions.<br>
                            Plant suggestions to influence their behavior and emotions.
                        </p>
                        <button class="btn btn-primary" onclick="closeModal('profileModal'); openPlantSuggestionFor('${char.name}')">
                            🎯 Plant Suggestion
                        </button>
                    </div>
                `;
            }

            html += '</div>'; // End suggestions tab

            $('#profile-content').html(html);
            openModal('profileModal');
        }
    });
}

// Open plant suggestion modal (internal function)
function _openPlantSuggestionModal() {
    if (!selectedCharacter) {
        addSystemMessage('Please select a character first.');
        return;
    }

    // Get character data and skill tree to check technique requirements
    $.when(
        $.ajax({url: `/api/character/${selectedCharacter}`}),
        $.ajax({url: '/api/skill-tree'})
    ).done(function(charData, skillData) {
        const char = charData[0];
        const skills = skillData[0];

        const hasEmotional = skills.techniques['emotional_anchoring'].status === 'mastered';
        const hasBehavioral = skills.techniques['embedded_commands'].status === 'mastered';
        const hasStrong = skills.techniques['post_hypnotic_suggestion'].status === 'mastered';

        if (!hasEmotional && !hasBehavioral && !hasStrong) {
            let html = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">❌</div>
                    <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">
                        You Don't Know Any Hypnosis Techniques Yet!
                    </h3>
                    <p style="margin-bottom: 1rem;">You need to learn hypnosis techniques before planting suggestions.</p>
                    <p style="margin-bottom: 2rem;">Study books, practice, or research online to master techniques.</p>
                    <button class="btn btn-primary" onclick="closeModal('plantSuggestionModal'); openStudyMenu();">
                        📚 Study Hypnosis
                    </button>
                </div>
            `;
            $('#plant-suggestion-content').html(html);
            openModal('plantSuggestionModal');
            return;
        }

        let html = `
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 1.1rem;">Planting suggestion on <strong>${char.name}</strong></div>
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.5rem;">
                    SP Available: <span id="sp-in-modal">${$('#sp-display').text()}</span>
                </div>
        `;

        // Show clothing effect if present
        if (char.clothing_modifier !== undefined && char.clothing_modifier !== 0) {
            let effectColor = char.clothing_modifier > 0 ? 'var(--success-color)' : 'var(--danger-color)';
            let effectIcon = char.clothing_modifier > 0 ? '✓' : '✗';
            let sign = char.clothing_modifier > 0 ? '+' : '';
            html += `
                <div style="margin-top: 1rem; padding: 0.8rem; background: rgba(233, 69, 96, 0.15); border-left: 3px solid ${effectColor}; border-radius: 8px; max-width: 500px; margin-left: auto; margin-right: auto;">
                    <strong style="color: ${effectColor};">${effectIcon} Outfit: ${sign}${char.clothing_modifier}% Suggestibility</strong><br>
                    <span style="font-size: 0.85rem; color: var(--text-secondary);">${char.outfit_description || char.clothing}</span>
                </div>
            `;
        }

        html += `
            </div>

            <div style="margin-bottom: 1.5rem;">
                <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">Choose Suggestion Type:</h3>
        `;

        // Emotional Nudge
        html += `
            <div class="technique-item ${hasEmotional ? '' : 'locked'}" style="cursor: pointer; margin-bottom: 1rem;"
                 ${hasEmotional ? `onclick="showSuggestionForm('emotional_nudge', '${char.name}')"` : ''}>
                <div class="technique-header">
                    <div class="technique-name">${hasEmotional ? '✓' : '✗'} Emotional Nudge (2 SP)</div>
                </div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">
                    Requires: Emotional Anchoring
                </div>
            </div>
        `;

        // Behavioral Prompt
        html += `
            <div class="technique-item ${hasBehavioral ? '' : 'locked'}" style="cursor: pointer; margin-bottom: 1rem;"
                 ${hasBehavioral ? `onclick="showSuggestionForm('behavioral_prompt', '${char.name}')"` : ''}>
                <div class="technique-header">
                    <div class="technique-name">${hasBehavioral ? '✓' : '✗'} Behavioral Prompt (3 SP)</div>
                </div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">
                    Requires: Embedded Commands
                </div>
            </div>
        `;

        // Strong Anchor
        html += `
            <div class="technique-item ${hasStrong ? '' : 'locked'}" style="cursor: pointer; margin-bottom: 1rem;"
                 ${hasStrong ? `onclick="showSuggestionForm('strong_anchor', '${char.name}')"` : ''}>
                <div class="technique-header">
                    <div class="technique-name">${hasStrong ? '✓' : '✗'} Strong Anchor (4-6 SP)</div>
                </div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">
                    Requires: Post-Hypnotic Suggestion
                </div>
            </div>
        `;

        // General status
        const canPlant = char.rapport >= 6;
        html += `
            <div style="margin-top: 2rem; padding: 1rem; background: var(--accent-color); border-radius: 8px;">
                ${canPlant ?
                    `<div style="color: var(--success-color);">✓ Rapport sufficient (${char.rapport}/6)</div>` :
                    `<div style="color: var(--danger-color);">⚠️ Rapport too low (${char.rapport}/6 required)</div>`
                }
            </div>
        `;

        $('#plant-suggestion-content').html(html);
        openModal('plantSuggestionModal');
    });
}

// Show suggestion form
function showSuggestionForm(type, characterName) {
    const typeNames = {
        'emotional_nudge': 'Emotional Nudge',
        'behavioral_prompt': 'Behavioral Prompt',
        'strong_anchor': 'Strong Anchor'
    };

    let html = `
        <div style="margin-bottom: 1.5rem;">
            <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">${typeNames[type]}</h3>

            <div style="margin-bottom: 1rem;">
                <label style="display: block; margin-bottom: 0.5rem;">Trigger (when...):</label>
                <input type="text" id="phs-trigger" class="input-field" placeholder="e.g., When someone asks about money..."
                       style="width: 100%; padding: 0.8rem; background: var(--accent-color); border: 2px solid var(--border-color); border-radius: 8px; color: var(--text-primary); font-size: 1rem;">
            </div>

            <div style="margin-bottom: 1rem;">
                <label style="display: block; margin-bottom: 0.5rem;">Response (they will...):</label>
                <input type="text" id="phs-response" class="input-field" placeholder="e.g., Feel anxious and change the subject..."
                       style="width: 100%; padding: 0.8rem; background: var(--accent-color); border: 2px solid var(--border-color); border-radius: 8px; color: var(--text-primary); font-size: 1rem;">
            </div>
    `;

    if (type === 'strong_anchor') {
        html += `
            <div style="margin-bottom: 1rem;">
                <label style="display: block; margin-bottom: 0.5rem;">SP to Invest (4-6):</label>
                <input type="number" id="phs-sp-cost" min="4" max="6" value="4"
                       style="width: 100%; padding: 0.8rem; background: var(--accent-color); border: 2px solid var(--border-color); border-radius: 8px; color: var(--text-primary); font-size: 1rem;">
            </div>
        `;
    }

    html += `
            <button class="btn btn-primary" onclick="plantSuggestion('${type}', '${characterName}')" style="width: 100%; margin-top: 1rem;">
                Plant Suggestion
            </button>
        </div>
    `;

    $('#plant-suggestion-content').html(html);
}

// Plant the suggestion
function plantSuggestion(type, characterName) {
    const trigger = $('#phs-trigger').val().trim();
    const response = $('#phs-response').val().trim();
    const spCost = type === 'strong_anchor' ? parseInt($('#phs-sp-cost').val()) : null;

    if (!trigger || !response) {
        alert('Please fill in both trigger and response.');
        return;
    }

    $.ajax({
        url: '/api/plant-suggestion',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            character: characterName,
            type: type,
            trigger: trigger,
            response: response,
            sp_cost: spCost
        }),
        success: function(data) {
            if (data.success) {
                addSystemMessage(`✓ ${data.message}`);
                updateGameState();
                closeModal('plantSuggestionModal');
            } else {
                alert(`Failed: ${data.message}`);
            }
        },
        error: function() {
            alert('Failed to plant suggestion. Please try again.');
        }
    });
}

// Open books modal
function openBooks() {
    $.ajax({
        url: '/api/books',
        method: 'GET',
        success: function(data) {
            let html = '<div>';

            data.books.forEach(book => {
                const statusIcon = book.already_read ? '📖' : '📕';
                const statusText = book.already_read ? 'READ' : 'UNREAD';

                html += `
                    <div class="technique-item" style="cursor: pointer; margin-bottom: 1rem;"
                         onclick="readBook('${book.id}', '${book.title}')">
                        <div class="technique-header">
                            <div class="technique-name">${statusIcon} ${book.title}</div>
                            <div class="technique-status">${statusText}</div>
                        </div>
                        <div style="font-size: 0.9rem; color: var(--text-secondary); margin: 0.5rem 0;">
                            ${book.description}
                        </div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">
                            <strong>Teaches:</strong> ${book.teaches.map(t => t.known ? '✓ ' + t.name : '• ' + t.name).join(', ')}
                        </div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.3rem;">
                            <strong>Location:</strong> ${book.location}
                        </div>
                    </div>
                `;
            });

            html += '</div>';

            $('#books-content').html(html);
            openModal('booksModal');
        }
    });
}

// Read a book
function readBook(bookId, bookTitle) {
    $.ajax({
        url: '/api/study',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            action: 'read_book',
            book_id: bookId
        }),
        success: function(data) {
            if (data.success) {
                let message = `📚 Read "${data.book_title}".\n`;

                if (data.learned && data.learned.length > 0) {
                    message += `\n🎓 MASTERED: ${data.learned.join(', ')}!`;
                }

                if (data.progress_made && data.progress_made.length > 0) {
                    data.progress_made.forEach(p => {
                        message += `\n📖 ${p.technique}: ${p.progress}%`;
                    });
                }

                alert(message);
                updateGameState();
                closeModal('booksModal');
                openSkillTree();
            }
        }
    });
}

// Practice menu
function practiceMenu() {
    // TODO: Implement practice menu
    alert('Practice menu coming soon!');
}

// Research online
function researchOnline() {
    $.ajax({
        url: '/api/study',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            action: 'research'
        }),
        success: function(data) {
            if (data.success) {
                if (data.mastered) {
                    alert(`🎓 MASTERED: ${data.mastered} through online research!`);
                } else {
                    alert(`🌐 Researched ${data.technique}: ${data.progress}%`);
                }
                updateGameState();
                closeModal('studyModal');
            } else {
                alert(data.error || 'No techniques available to research');
            }
        }
    });
}

// Open study menu
function openStudyMenu() {
    openModal('studyModal');
}

// Modal functions
function openModal(modalId) {
    $(`#${modalId}`).addClass('active');
}

function closeModal(modalId) {
    $(`#${modalId}`).removeClass('active');
}

// Save game
function saveGame() {
    $.ajax({
        url: '/api/save-game',
        method: 'POST',
        success: function(data) {
            if (data.success) {
                addSystemMessage('💾 ' + data.message);
            } else {
                alert('Failed to save: ' + data.message);
            }
        }
    });
}

// Exit game
function exitGame() {
    if (confirm('Exit to main menu? (Make sure to save first!)')) {
        window.location.href = '/';
    }
}

// Open player profile
function openPlayerProfile() {
    $.ajax({
        url: '/api/player-profile',
        method: 'GET',
        success: function(player) {
            let html = `
                <div style="margin-bottom: 2rem;">
                    <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">📋 Basic Information</h3>
                    <div style="line-height: 2;">
                        <strong>Name:</strong> ${player.name}<br>
                        <strong>Age:</strong> ${player.age}<br>
                        <strong>Occupation:</strong> ${player.occupation}<br>
                        <strong>Appearance:</strong> ${player.clothing}<br>
                    </div>
                </div>

                <div style="margin-bottom: 2rem;">
                    <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">💰 Suggestion Points</h3>
                    <div style="line-height: 2;">
                        <strong>Current SP:</strong> ${player.suggestion_points}<br>
                        <strong>Total SP Earned:</strong> ${player.total_sp_earned}<br>
                        <strong>SP Spent:</strong> ${player.total_sp_earned - player.suggestion_points}<br>
                    </div>
                </div>

                <div style="margin-bottom: 2rem;">
                    <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">🎓 Hypnosis Mastery</h3>
                    <div style="line-height: 2;">
                        <strong>Skill Level:</strong> ${player.skill_level.toUpperCase()}<br>
                        <strong>Techniques Mastered:</strong> ${player.techniques_mastered}/${player.total_techniques}<br>
                        <strong>Books Read:</strong> ${player.books_read}<br>
                        <strong>Practice Sessions:</strong> ${player.practice_sessions}<br>
                        <strong>Bonuses:</strong> -${player.total_sp_reduction} SP cost, +${player.total_success_bonus}% success<br>
                    </div>
                </div>
            `;

            if (player.mastered_techniques && player.mastered_techniques.length > 0) {
                html += `
                    <div style="margin-bottom: 2rem;">
                        <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">🟢 Mastered Techniques (${player.mastered_techniques.length})</h3>
                `;

                // Group by category
                const categories = {
                    'basic': [],
                    'intermediate': [],
                    'advanced': [],
                    'master': []
                };

                player.mastered_techniques.forEach(tech => {
                    categories[tech.category].push(tech);
                });

                Object.entries(categories).forEach(([category, techniques]) => {
                    if (techniques.length > 0) {
                        html += `<div style="margin-bottom: 1rem;">`;
                        html += `<div style="font-weight: bold; text-transform: uppercase; margin-bottom: 0.5rem;">${category}</div>`;
                        techniques.forEach(tech => {
                            html += `
                                <div style="background: var(--accent-color); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;">
                                    <strong>${tech.name}</strong>
                                    ${tech.sp_reduction > 0 || tech.success_bonus > 0 ?
                                        `<span style="color: var(--success-color); font-size: 0.9rem; margin-left: 1rem;">
                                            ${tech.sp_reduction > 0 ? `-${tech.sp_reduction} SP ` : ''}
                                            ${tech.success_bonus > 0 ? `+${tech.success_bonus}%` : ''}
                                        </span>`
                                        : ''}
                                </div>
                            `;
                        });
                        html += `</div>`;
                    }
                });

                html += '</div>';
            }

            if (player.learning_techniques && player.learning_techniques.length > 0) {
                html += `
                    <div style="margin-bottom: 2rem;">
                        <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">🟡 Currently Learning (${player.learning_techniques.length})</h3>
                `;

                player.learning_techniques.forEach(tech => {
                    html += `
                        <div style="background: var(--accent-color); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>${tech.name}</strong>
                                <span style="color: var(--warning-color);">${tech.progress}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${tech.progress}%"></div>
                            </div>
                        </div>
                    `;
                });

                html += '</div>';
            }

            if (player.scenes_completed && player.scenes_completed.length > 0) {
                html += `
                    <div style="margin-bottom: 2rem;">
                        <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">✓ Scenes Completed</h3>
                        <div style="line-height: 1.8;">
                            ${player.scenes_completed.map(scene => `• ${scene}`).join('<br>')}
                        </div>
                    </div>
                `;
            }

            // Add quick actions
            html += `
                <div style="margin-top: 2rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <button class="btn btn-primary" onclick="closeModal('playerProfileModal'); openSkillTree();">
                        🌳 View Skill Tree
                    </button>
                    <button class="btn btn-secondary" onclick="closeModal('playerProfileModal'); openStudyMenu();">
                        📚 Study Hypnosis
                    </button>
                </div>
            `;

            $('#player-profile-content').html(html);
            openModal('playerProfileModal');
        },
        error: function() {
            alert('Failed to load player profile');
        }
    });
}

// Ambient events system
let ambientEventTimer;
let characterActivities = {}; // Track what each character is doing

function startAmbientEvents() {
    // Poll for ambient events
    function pollAmbientEvent() {
        $.ajax({
            url: '/api/ambient-events',
            method: 'GET',
            success: function(event) {
                if (event.type !== 'none') {
                    displayAmbientEvent(event);
                }
            }
        });

        // Schedule next event (randomize between 15-25 seconds)
        const delay = 15000 + Math.random() * 10000;
        ambientEventTimer = setTimeout(pollAmbientEvent, delay);
    }

    // Start first poll after 5 seconds
    setTimeout(pollAmbientEvent, 5000);
}

function displayAmbientEvent(event) {
    const dialogueBox = $('#dialogue-box');

    if (event.type === 'activity') {
        // Update character's activity status
        characterActivities[event.character] = event.activity;
        updateCharacterActivity(event.character, event.activity);

        // Show in dialogue
        const messageHtml = `
            <div class="dialogue-message">
                <div class="ambient-message">
                    <span class="ambient-icon">👀</span> ${event.message}
                </div>
            </div>
        `;
        dialogueBox.append(messageHtml);
    } else if (event.type === 'dialogue') {
        // Character says something
        const messageHtml = `
            <div class="dialogue-message">
                <div class="ambient-dialogue">
                    <span class="dialogue-speaker">${event.character}</span>
                    <div class="dialogue-text">${event.dialogue}</div>
                </div>
            </div>
        `;
        dialogueBox.append(messageHtml);
    } else if (event.type === 'interaction') {
        // Characters interact - enhanced display for LLM conversations
        let messageHtml;

        if (event.conversation_type && event.location) {
            // LLM-generated background conversation
            const typeEmoji = {
                'friendly': '😊',
                'conversation': '💬',
                'argument': '😠',
                'help': '🤝',
                'romantic': '💕',
                'conflict': '⚡'
            };
            const emoji = typeEmoji[event.conversation_type] || '💬';

            messageHtml = `
                <div class="dialogue-message">
                    <div class="background-conversation" style="
                        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
                        border-left: 3px solid var(--highlight-color);
                        padding: 0.8rem 1rem;
                        margin: 0.5rem 0;
                        border-radius: 8px;
                        font-style: italic;
                    ">
                        <span class="ambient-icon" style="font-size: 1.2rem;">${emoji}</span>
                        <span style="color: var(--highlight-color); font-weight: 600;">Background:</span>
                        ${event.message}
                    </div>
                </div>
            `;
        } else {
            // Simple interaction (non-LLM)
            messageHtml = `
                <div class="dialogue-message">
                    <div class="ambient-message">
                        <span class="ambient-icon">💬</span> ${event.message}
                    </div>
                </div>
            `;
        }

        dialogueBox.append(messageHtml);
    }

    // Display any PHS activations from this event
    if (event.phs_activations && event.phs_activations.length > 0) {
        event.phs_activations.forEach(activation => {
            if (activation) {
                addPHSActivationMessage(activation);
            }
        });
    }

    scrollToBottom();
}

function updateCharacterActivity(characterName, activity) {
    // Find the character card and update it
    const card = $(`.character-card[data-character="${characterName}"]`);

    // Remove old activity indicator if exists
    card.find('.activity-indicator').remove();

    // Add new activity indicator
    const activityHtml = `
        <div class="activity-indicator">${activity}</div>
    `;
    card.find('.character-info').last().after(activityHtml);

    // Add pulse effect to show character is active
    card.addClass('active-character');
    setTimeout(() => {
        card.removeClass('active-character');
    }, 2000);
}

// Update all character schedules
function updateCharacterSchedules() {
    $.ajax({
        url: '/api/characters',
        method: 'GET',
        success: function(data) {
            // Update location header if available
            if (data.location) {
                const header = document.getElementById('character-list-header');
                if (header) {
                    header.textContent = `Characters at ${data.location}`;
                }
            }

            data.characters.forEach(char => {
                updateCharacterActivity(char.name, char.current_activity);
                updateCharacterMood(char);
            });
        }
    });
}

// Update character mood indicator
function updateCharacterMood(char) {
    const moodIndicator = $(`.mood-indicator[data-character="${char.name}"]`);
    if (!moodIndicator.length) return;

    // Update mood display with emoji and state
    const moodDisplay = moodIndicator.find('.mood-display');
    let moodText = `${char.mood_emoji} ${char.emotional_state.charAt(0).toUpperCase() + char.emotional_state.slice(1)}`;

    // Add reason if available
    if (char.emotional_state_reason) {
        moodText += ` <span style="color: var(--text-secondary); font-weight: normal;">(${char.emotional_state_reason})</span>`;
    }

    moodDisplay.html(moodText);

    // Update recommendation
    const moodRecommendation = moodIndicator.find('.mood-recommendation');
    moodRecommendation.html(char.mood_recommendation);
    moodRecommendation.css('color', char.mood_color);

    // Update border color based on mood
    moodIndicator.css('border-left-color', char.mood_color);
}

// Open add character modal
function openAddCharacter() {
    // Clear form
    $('#new-char-name').val('');
    $('#new-char-age').val('');
    $('#new-char-occupation').val('');
    $('#new-char-personality').val('');
    $('#new-char-resistance').val('50');
    $('#new-char-clothing').val('');
    $('#new-char-clothing-meaning').val('');

    openModal('addCharacterModal');
}

// Create new character
function createCharacter() {
    const name = $('#new-char-name').val().trim();
    const age = $('#new-char-age').val();
    const gender = $('#new-char-gender').val();
    const occupation = $('#new-char-occupation').val().trim();
    const personality = $('#new-char-personality').val().trim();
    const resistance = $('#new-char-resistance').val();
    const clothing = $('#new-char-clothing').val().trim() || 'Casual clothing';
    const clothing_meaning = $('#new-char-clothing-meaning').val().trim();

    // Validate required fields
    if (!name || !age || !occupation || !personality || !resistance) {
        alert('Please fill in all required fields (marked with *)');
        return;
    }

    // Validate age and resistance
    if (age < 1 || age > 120) {
        alert('Age must be between 1 and 120');
        return;
    }

    if (resistance < 0 || resistance > 100) {
        alert('Resistance must be between 0 and 100');
        return;
    }

    // Send to API
    $.ajax({
        url: '/api/add-character',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            name: name,
            age: parseInt(age),
            gender: gender,
            occupation: occupation,
            personality: personality,
            resistance: parseInt(resistance),
            clothing: clothing,
            clothing_meaning: clothing_meaning
        }),
        success: function(data) {
            if (data.success) {
                alert(`✨ ${data.message}`);
                closeModal('addCharacterModal');

                // Reload the page to show new character
                window.location.reload();
            } else {
                alert(`Failed: ${data.error}`);
            }
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Failed to create character';
            alert(`Error: ${error}`);
        }
    });
}

// Switch profile tabs
function switchProfileTab(tabName) {
    // Update tab buttons
    $('.profile-tab').removeClass('active');
    $(`.profile-tab[data-tab="${tabName}"]`).addClass('active');

    // Update tab button styles
    $('.profile-tab').each(function() {
        if ($(this).hasClass('active')) {
            $(this).css({
                'background': 'var(--highlight-color)',
                'color': 'white'
            });
        } else {
            $(this).css({
                'background': 'var(--accent-color)',
                'color': 'var(--text-primary)'
            });
        }
    });

    // Update tab content
    $('.profile-tab-content').hide();
    $(`.profile-tab-content[data-tab-content="${tabName}"]`).show();
}

// Reinforce a PHS
function reinforcePHS(characterName, phsIndex) {
    const currentSP = parseInt($('#sp-display').text());

    if (currentSP < 1) {
        addSystemMessage('Not enough Suggestion Points! You need 1 SP to reinforce a suggestion.');
        return;
    }

    $.ajax({
        url: '/api/phs/reinforce',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            character: characterName,
            phs_index: phsIndex
        }),
        success: function(data) {
            if (data.success) {
                addSystemMessage(data.message);

                // Update SP display
                $('#sp-display').text(data.sp_remaining);

                // Flash SP counter
                $('#sp-display').parent().addClass('flash-effect');
                setTimeout(() => {
                    $('#sp-display').parent().removeClass('flash-effect');
                }, 600);

                // Refresh the profile modal to show updated PHS
                _openCharacterProfileModal();

                // Switch to suggestions tab
                setTimeout(() => {
                    switchProfileTab('suggestions');
                }, 100);
            } else {
                addSystemMessage(`Error: ${data.error}`);
            }
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Failed to reinforce suggestion';
            addSystemMessage(`Error: ${error}`);
        }
    });
}

// Remove a PHS
function removePHS(characterName, phsIndex) {
    if (!confirm('Are you sure you want to remove this suggestion? This cannot be undone.')) {
        return;
    }

    $.ajax({
        url: '/api/phs/remove',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            character: characterName,
            phs_index: phsIndex
        }),
        success: function(data) {
            if (data.success) {
                addSystemMessage(data.message);

                // Refresh the profile modal to show updated PHS list
                _openCharacterProfileModal();

                // Switch to suggestions tab
                setTimeout(() => {
                    switchProfileTab('suggestions');
                }, 100);
            } else {
                addSystemMessage(`Error: ${data.error}`);
            }
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Failed to remove suggestion';
            addSystemMessage(`Error: ${error}`);
        }
    });
}

// ==================== GIFT SHOP ====================

let allGifts = [];
let currentGiftFilter = 'all';

// Open gift shop modal
function openGiftShop() {
    $.ajax({
        url: '/api/shop/gifts',
        method: 'GET',
        success: function(data) {
            allGifts = data.gifts;

            // Update money display
            $('#gift-shop-money').text(`$${data.player_money}`);

            // Populate character selector
            const recipientSelect = $('#gift-recipient');
            recipientSelect.html('<option value="">Select a character...</option>');

            // Get character list from the page
            $('.character-card').each(function() {
                const charName = $(this).data('character');
                recipientSelect.append(`<option value="${charName}">${charName}</option>`);
            });

            // Display gifts
            currentGiftFilter = 'all';
            displayGifts();

            // Highlight "All Gifts" filter button
            $('.btn[onclick*="filterGifts"]').css('opacity', '0.6');
            $('#filter-gifts-all').css('opacity', '1');

            openModal('giftShopModal');
        },
        error: function() {
            alert('Failed to load gift shop');
        }
    });
}

// Filter gifts by price range
function filterGifts(category) {
    currentGiftFilter = category;
    displayGifts();

    // Update button styles
    $('.btn[onclick*="filterGifts"]').css('opacity', '0.6');
    $(`#filter-gifts-${category}`).css('opacity', '1');
}

// Display gifts based on current filter
function displayGifts() {
    const giftsGrid = $('#gifts-grid');
    giftsGrid.empty();

    let filteredGifts = allGifts;

    // Apply filter
    if (currentGiftFilter === 'cheap') {
        filteredGifts = allGifts.filter(g => g.cost <= 30);
    } else if (currentGiftFilter === 'medium') {
        filteredGifts = allGifts.filter(g => g.cost >= 50 && g.cost <= 100);
    } else if (currentGiftFilter === 'expensive') {
        filteredGifts = allGifts.filter(g => g.cost >= 150);
    }

    if (filteredGifts.length === 0) {
        giftsGrid.html('<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">No gifts in this category</p>');
        return;
    }

    filteredGifts.forEach(gift => {
        const canAfford = gift.can_afford;
        const affordClass = canAfford ? '' : 'opacity: 0.5;';

        let effectsHtml = '<div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.5rem;">';
        if (gift.rapport_gain > 0) effectsHtml += `<div>❤️ +${gift.rapport_gain} Rapport</div>`;
        if (gift.resistance_change < 0) effectsHtml += `<div>🎯 ${gift.resistance_change}% Resistance</div>`;
        if (gift.suggestibility_bonus > 0) effectsHtml += `<div>✨ +${gift.suggestibility_bonus}% Permanent Suggestibility</div>`;
        if (gift.unlocks_content) effectsHtml += `<div>🔓 Unlocks: ${gift.unlocks_content.replace(/_/g, ' ')}</div>`;
        effectsHtml += '</div>';

        const giftHtml = `
            <div class="gift-card" style="${affordClass} background: var(--accent-color); padding: 1rem; border-radius: 10px; border: 2px solid var(--border-color); cursor: ${canAfford ? 'pointer' : 'not-allowed'};" ${canAfford ? `onclick="buyGift('${gift.gift_id}')"` : ''}>
                <div style="font-size: 2.5rem; text-align: center; margin-bottom: 0.5rem;">${gift.icon}</div>
                <div style="font-weight: bold; text-align: center; margin-bottom: 0.5rem;">${gift.name}</div>
                <div style="font-size: 1.2rem; text-align: center; color: var(--highlight-color); margin-bottom: 0.5rem; font-weight: bold;">$${gift.cost}</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem; min-height: 3rem;">${gift.description}</div>
                ${effectsHtml}
                ${!canAfford ? '<div style="color: var(--danger-color); text-align: center; margin-top: 0.5rem; font-size: 0.85rem;">⚠️ Cannot Afford</div>' : ''}
            </div>
        `;

        giftsGrid.append(giftHtml);
    });
}

// Buy and give a gift
function buyGift(giftId) {
    const recipient = $('#gift-recipient').val();

    if (!recipient) {
        alert('Please select a character to give this gift to!');
        return;
    }

    const gift = allGifts.find(g => g.gift_id === giftId);

    if (!confirm(`Give ${gift.name} to ${recipient} for $${gift.cost}?`)) {
        return;
    }

    $.ajax({
        url: '/api/shop/give-gift',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            gift_id: giftId,
            character: recipient
        }),
        success: function(data) {
            if (data.success) {
                addSystemMessage(`🎁 You gave ${gift.name} to ${recipient}!`);
                addSystemMessage(data.message);

                // Show changes
                if (data.changes && data.changes.length > 0) {
                    data.changes.forEach(change => addSystemMessage(change));
                }

                // Update game state and money display
                updateGameState();

                // Refresh the gift shop to show updated affordability
                openGiftShop();

                // Update character card if they're present
                updateCharacterList();
            } else {
                alert(`Error: ${data.error || 'Failed to give gift'}`);
            }
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Failed to give gift';
            alert(`Error: ${error}`);
        }
    });
}

// ==================== JOB BOARD ====================

// Open job board modal
function openJobBoard() {
    $.ajax({
        url: '/api/jobs',
        method: 'GET',
        success: function(data) {
            // Update money display
            $('#job-board-money').text(`$${data.player_money}`);

            // Display jobs
            displayJobs(data.jobs);

            openModal('jobBoardModal');
        },
        error: function() {
            alert('Failed to load job board');
        }
    });
}

// Display jobs list
function displayJobs(jobs) {
    const jobsList = $('#jobs-list');
    jobsList.empty();

    if (jobs.length === 0) {
        jobsList.html('<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">No jobs available</p>');
        return;
    }

    jobs.forEach(job => {
        const canAfford = job.can_afford_sp;
        const meetsRequirement = job.meets_requirement;
        const canDo = canAfford && meetsRequirement;

        let requirementText = '';
        if (!meetsRequirement) {
            requirementText = `<div style="color: var(--danger-color); font-size: 0.85rem; margin-top: 0.5rem;">⚠️ Requires: ${job.requires_skill_level} skill level</div>`;
        }

        let spCostText = '';
        if (job.sp_cost > 0) {
            spCostText = `<span style="color: ${canAfford ? 'var(--warning-color)' : 'var(--danger-color)'};">• Costs ${job.sp_cost} SP</span>`;
        }

        const jobHtml = `
            <div class="job-card" style="background: var(--accent-color); padding: 1.5rem; border-radius: 10px; border: 2px solid var(--border-color); margin-bottom: 1rem; ${canDo ? 'cursor: pointer;' : 'opacity: 0.6; cursor: not-allowed;'}" ${canDo ? `onclick="doJob('${job.job_id}')"` : ''}>
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div>
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">${job.icon} ${job.name}</div>
                        <div style="font-size: 0.9rem; color: var(--text-secondary);">${job.description}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.5rem; color: var(--success-color); font-weight: bold;">$${job.pay}</div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">${job.duration_minutes} min</div>
                    </div>
                </div>

                <div style="display: flex; gap: 1rem; align-items: center; font-size: 0.9rem; color: var(--text-secondary);">
                    <span>⏱️ ${Math.floor(job.duration_minutes / 60)}h ${job.duration_minutes % 60}m</span>
                    ${spCostText}
                </div>

                ${requirementText}
                ${!canDo ? '<div style="color: var(--danger-color); text-align: center; margin-top: 0.8rem; font-size: 0.9rem; font-weight: bold;">⚠️ Requirements Not Met</div>' : ''}
            </div>
        `;

        jobsList.append(jobHtml);
    });
}

// Do a job
function doJob(jobId) {
    if (!confirm('Start this job? Time will pass and you will earn money.')) {
        return;
    }

    $.ajax({
        url: '/api/jobs/do-job',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            job_id: jobId
        }),
        success: function(data) {
            if (data.success) {
                addSystemMessage(`💼 ${data.job_name} completed!`);
                addSystemMessage(data.message);

                // Show changes (money earned, time passed)
                if (data.changes && data.changes.length > 0) {
                    data.changes.forEach(change => addSystemMessage(change));
                }

                // Update game state
                updateGameState();

                // Close job board modal
                closeModal('jobBoardModal');

                // Refresh activities (time passed, location may have changed)
                loadActivities();
                updateCharacterList();
            } else {
                alert(`Error: ${data.error || 'Failed to complete job'}`);
            }
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Failed to do job';
            alert(`Error: ${error}`);
        }
    });
}

// Helper to update character list (refresh character locations/states)
function updateCharacterList() {
    updateCharacterSchedules();
}

// ==================== EVENT LOG ====================

let allEvents = [];
let currentEventFilter = 'all';

// Open event log modal
function openEventLog() {
    $.ajax({
        url: '/api/autonomous-events',
        method: 'GET',
        success: function(data) {
            if (data.success) {
                allEvents = data.events || [];

                // Display events
                currentEventFilter = 'all';
                displayEventLog();

                // Highlight "All Events" filter button
                $('.btn[onclick*="filterEventLog"]').css('opacity', '0.6');
                $('#filter-events-all').css('opacity', '1');

                openModal('eventLogModal');
            } else {
                alert('Failed to load event log');
            }
        },
        error: function() {
            alert('Failed to load event log');
        }
    });
}

// Filter event log by type
function filterEventLog(filter) {
    currentEventFilter = filter;
    displayEventLog();

    // Update button styles
    $('.btn[onclick*="filterEventLog"]').css('opacity', '0.6');
    $(`#filter-events-${filter}`).css('opacity', '1');
}

// Display event log based on current filter
function displayEventLog() {
    const timeline = $('#events-timeline');
    timeline.empty();

    let filteredEvents = allEvents;

    // Apply filter
    if (currentEventFilter === 'phs') {
        filteredEvents = allEvents.filter(e => e.is_phs);
    } else if (currentEventFilter === 'clothing') {
        filteredEvents = allEvents.filter(e => e.type === 'clothing_change');
    } else if (currentEventFilter === 'mood') {
        filteredEvents = allEvents.filter(e => e.type === 'mood_change');
    } else if (currentEventFilter === 'action') {
        filteredEvents = allEvents.filter(e => e.type === 'action');
    }

    if (filteredEvents.length === 0) {
        timeline.html(`
            <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
                <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">No Events Yet</div>
                <div style="font-size: 0.9rem;">
                    Characters will act autonomously based on their active Post-Hypnotic Suggestions.<br>
                    Plant suggestions and let time pass to see events appear here.
                </div>
            </div>
        `);
        return;
    }

    // Display events in timeline format
    filteredEvents.forEach((event, index) => {
        const isPHS = event.is_phs;
        const typeColors = {
            'phs_activation': '#e94560',
            'clothing_change': '#ff8c00',
            'mood_change': '#667eea',
            'action': '#43a047'
        };
        const borderColor = typeColors[event.type] || '#667eea';

        const phsBadge = isPHS ? '<span style="background: linear-gradient(135deg, #e94560 0%, #ff8c00 100%); padding: 0.2rem 0.5rem; border-radius: 5px; font-size: 0.7rem; font-weight: bold; color: white; margin-left: 0.5rem;">PHS</span>' : '';

        const eventHtml = `
            <div class="event-item" style="background: var(--accent-color); padding: 1rem; border-radius: 10px; border-left: 4px solid ${borderColor}; margin-bottom: 1rem; position: relative;">
                <!-- Timestamp -->
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    ${event.timestamp}
                </div>

                <!-- Event description -->
                <div style="display: flex; align-items: start; gap: 0.8rem;">
                    <div style="font-size: 2rem; line-height: 1;">${event.icon}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: bold; margin-bottom: 0.3rem; color: var(--highlight-color);">
                            ${event.character}${phsBadge}
                        </div>
                        <div style="font-size: 0.95rem; line-height: 1.4;">
                            ${event.description}
                        </div>

                        <!-- Event type badge -->
                        <div style="margin-top: 0.5rem;">
                            <span style="background: ${borderColor}; padding: 0.2rem 0.6rem; border-radius: 5px; font-size: 0.7rem; font-weight: bold; color: white; text-transform: uppercase;">
                                ${event.type.replace('_', ' ')}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Visibility indicator -->
                ${event.visibility === 'private' ? '<div style="position: absolute; top: 0.5rem; right: 0.5rem; font-size: 0.7rem; color: var(--text-secondary);">🔒 Private</div>' : ''}
                ${event.visibility === 'subtle' ? '<div style="position: absolute; top: 0.5rem; right: 0.5rem; font-size: 0.7rem; color: var(--text-secondary);">👁️ Subtle</div>' : ''}
            </div>
        `;

        timeline.append(eventHtml);
    });

    // Add helpful tip if PHS events exist
    const phsEvents = filteredEvents.filter(e => e.is_phs);
    if (phsEvents.length > 0) {
        const tipHtml = `
            <div style="background: linear-gradient(135deg, rgba(233, 69, 96, 0.15) 0%, rgba(255, 140, 0, 0.15) 100%); padding: 1rem; border-radius: 10px; margin-top: 1.5rem; border: 2px dashed var(--highlight-color);">
                <div style="font-weight: bold; margin-bottom: 0.5rem; color: var(--highlight-color);">💡 Tip: Reinforcing Suggestions</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">
                    When PHS activations occur, the suggestion gets slightly stronger (+2% activation chance).
                    You can also manually reinforce suggestions from the character's profile for even better results!
                </div>
            </div>
        `;
        timeline.append(tipHtml);
    }
}
