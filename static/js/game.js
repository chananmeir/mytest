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

    // Start ambient events polling (every 15-25 seconds for variety)
    startAmbientEvents();
});

// Select a character to talk to
function selectCharacter(characterName) {
    selectedCharacter = characterName;

    // Update UI
    $('.character-card').removeClass('active');
    $(`.character-card[data-character="${characterName}"]`).addClass('active');
    $('#selected-character').text(characterName);

    // Enable input
    $('#message-input').prop('disabled', false);
    $('#send-btn').prop('disabled', false);
    $('#plant-suggestion-btn').prop('disabled', false);

    // Add system message
    addSystemMessage(`Now talking with ${characterName}. Type your message below.`);
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
                    addSystemMessage(change.message);
                });
            }

            // Update character card
            updateCharacterCard(selectedCharacter, data.character_state);

            // Update game state
            updateGameState();

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

// Scroll dialogue box to bottom
function scrollToBottom() {
    const dialogueBox = document.getElementById('dialogue-box');
    dialogueBox.scrollTop = dialogueBox.scrollHeight;
}

// Update character card
function updateCharacterCard(characterName, state) {
    const card = $(`.character-card[data-character="${characterName}"]`);
    const rapportPercent = (state.rapport / 20 * 100);

    card.find('.rapport-fill').css('width', rapportPercent + '%');
    card.find('.character-info').last().text(`Rapport: ${state.rapport}/20 | ${state.emotional_state}`);
}

// Update game state display
function updateGameState() {
    $.ajax({
        url: '/api/game-state',
        method: 'GET',
        success: function(data) {
            $('#sp-display').text(data.player.suggestion_points);
            $('#skill-level').text(data.player.skill_level.toUpperCase());
            $('#techniques-count').text(`${data.player.techniques_mastered}/${data.player.total_techniques}`);
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

// Open character profile
function openCharacterProfile() {
    if (!selectedCharacter) {
        addSystemMessage('Please select a character first.');
        return;
    }

    $.ajax({
        url: `/api/character/${selectedCharacter}`,
        method: 'GET',
        success: function(char) {
            $('#profile-character-name').text(char.name);

            let html = `
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
                        <strong>Rapport:</strong> ${char.rapport}/20<br>
                        <strong>Emotional State:</strong> ${char.emotional_state}<br>
                        <strong>Resistance:</strong> ${char.resistance}%<br>
                    </div>
                </div>

                <div style="margin-bottom: 2rem;">
                    <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">Appearance</h3>
                    <div style="line-height: 2;">
                        <strong>Wearing:</strong> ${char.clothing}<br>
                        <strong>Meaning:</strong> ${char.clothing_meaning}<br>
                    </div>
                </div>
            `;

            if (char.active_phs && char.active_phs.length > 0) {
                html += `
                    <div style="margin-bottom: 2rem;">
                        <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">Active Suggestions (${char.active_phs.length})</h3>
                `;

                char.active_phs.forEach((phs, i) => {
                    let statusColor = phs.activation_chance >= 70 ? 'var(--success-color)' :
                                     phs.activation_chance >= 50 ? 'var(--warning-color)' : 'var(--danger-color)';
                    html += `
                        <div style="background: var(--accent-color); padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid ${statusColor};">
                            <div style="font-weight: bold; margin-bottom: 0.5rem;">${phs.activation_chance}% activation chance</div>
                            <div style="margin-bottom: 0.3rem;"><strong>Trigger:</strong> "${phs.trigger}"</div>
                            <div style="margin-bottom: 0.3rem;"><strong>Response:</strong> "${phs.response}"</div>
                            <div style="font-size: 0.85rem; color: var(--text-secondary);">Reinforced ${phs.reinforcements} time(s)</div>
                        </div>
                    `;
                });

                html += '</div>';
            }

            if (char.memories && char.memories.length > 0) {
                html += `
                    <div style="margin-bottom: 2rem;">
                        <h3 style="color: var(--highlight-color); margin-bottom: 1rem;">Memories (${char.memories.length})</h3>
                `;

                // Show top 5 most important memories
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

            $('#profile-content').html(html);
            openModal('profileModal');
        }
    });
}

// Open plant suggestion modal
function openPlantSuggestion() {
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
        // Characters interact
        const messageHtml = `
            <div class="dialogue-message">
                <div class="ambient-message">
                    <span class="ambient-icon">💬</span> ${event.message}
                </div>
            </div>
        `;
        dialogueBox.append(messageHtml);
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
