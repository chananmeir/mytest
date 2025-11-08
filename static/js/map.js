/**
 * Travel Map System
 * Handles location display, filtering, and travel
 */

let allLocations = [];
let currentFilter = 'all';

/**
 * Open the map modal and load locations
 */
async function openMap() {
    try {
        const response = await fetch('/api/locations');
        const data = await response.json();

        allLocations = data.locations;

        // Update current location display
        const currentLoc = allLocations.find(loc => loc.is_current);
        if (currentLoc) {
            document.getElementById('current-location-name').textContent = currentLoc.name;
        }

        // Display all locations
        displayLocations(allLocations);

        // Reset filter
        currentFilter = 'all';
        updateFilterButtons();

        // Open modal using the standard modal system
        openModal('mapModal');
    } catch (error) {
        console.error('Error loading locations:', error);
        showMessage('Failed to load locations', 'error');
    }
}

/**
 * Display locations in the grid
 */
function displayLocations(locations) {
    const grid = document.getElementById('locations-grid');
    grid.innerHTML = '';

    locations.forEach(location => {
        const card = createLocationCard(location);
        grid.appendChild(card);
    });
}

/**
 * Create a location card element
 */
function createLocationCard(location) {
    const card = document.createElement('div');
    card.className = 'location-card';
    card.dataset.locationId = location.id;
    card.dataset.locationType = location.location_type;

    // Determine card style based on status
    let cardStyle = 'background: var(--card-bg); border: 2px solid var(--border-color);';
    let statusBadge = '';
    let canTravel = true;

    if (location.is_current) {
        cardStyle = 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: 2px solid #764ba2;';
        statusBadge = '<div style="position: absolute; top: 0.5rem; right: 0.5rem; background: rgba(255,255,255,0.9); color: #667eea; padding: 0.3rem 0.6rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">📍 Here</div>';
        canTravel = false;
    } else if (!location.is_open) {
        cardStyle = 'background: var(--card-bg); border: 2px solid #888; opacity: 0.6;';
        statusBadge = '<div style="position: absolute; top: 0.5rem; right: 0.5rem; background: rgba(200,0,0,0.8); color: white; padding: 0.3rem 0.6rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">🔒 Closed</div>';
        canTravel = false;
    }

    // Location type icon
    const typeIcons = {
        'home': '🏠',
        'work': '💼',
        'public': '🌆',
        'private': '🔐'
    };
    const typeIcon = typeIcons[location.location_type] || '📍';

    // Characters present
    const charactersHtml = location.characters_present && location.characters_present.length > 0
        ? `<div style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(0,0,0,0.2); border-radius: 5px;">
               <div style="font-size: 0.8rem; color: rgba(255,255,255,0.8); margin-bottom: 0.3rem;">👥 Present:</div>
               <div style="font-size: 0.85rem; font-weight: bold;">${location.characters_present.join(', ')}</div>
           </div>`
        : '<div style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(0,0,0,0.1); border-radius: 5px; font-size: 0.8rem; color: rgba(255,255,255,0.6);">Nobody here</div>';

    // Travel time
    const travelTimeHtml = location.travel_time > 0
        ? `<div style="font-size: 0.8rem; color: rgba(255,255,255,0.7); margin-top: 0.5rem;">⏱️ ${location.travel_time} min travel</div>`
        : '<div style="font-size: 0.8rem; color: rgba(255,255,255,0.7); margin-top: 0.5rem;">⚡ Instant travel</div>';

    // Opening hours
    let hoursHtml = '';
    if (location.opens_at !== null || location.closes_at !== null) {
        const opensAt = location.opens_at !== null ? `${location.opens_at}:00` : 'Always';
        const closesAt = location.closes_at !== null ? `${location.closes_at}:00` : 'Always';
        hoursHtml = `<div style="font-size: 0.75rem; color: rgba(255,255,255,0.6); margin-top: 0.3rem;">🕐 Open: ${opensAt} - ${closesAt}</div>`;
    }

    // Travel button
    const buttonHtml = canTravel
        ? `<button class="btn btn-primary" onclick="travelToLocation('${location.id}')" style="width: 100%; margin-top: 1rem;">
               ✈️ Travel Here
           </button>`
        : '';

    card.innerHTML = `
        <div style="position: relative; padding: 1rem; border-radius: 10px; ${cardStyle} color: white;">
            ${statusBadge}
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">${typeIcon}</div>
            <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0.5rem;">${location.name}</div>
            <div style="font-size: 0.85rem; color: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">${location.description}</div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">Atmosphere: ${location.atmosphere}</div>
            ${charactersHtml}
            ${travelTimeHtml}
            ${hoursHtml}
            ${buttonHtml}
        </div>
    `;

    return card;
}

/**
 * Filter locations by type
 */
function filterLocations(type) {
    currentFilter = type;
    updateFilterButtons();

    if (type === 'all') {
        displayLocations(allLocations);
    } else {
        const filtered = allLocations.filter(loc => loc.location_type === type);
        displayLocations(filtered);
    }
}

/**
 * Update filter button styles
 */
function updateFilterButtons() {
    ['all', 'home', 'work', 'public'].forEach(type => {
        const btn = document.getElementById(`filter-${type}`);
        if (btn) {
            if (type === currentFilter) {
                btn.style.background = 'var(--primary-color)';
                btn.style.color = 'white';
            } else {
                btn.style.background = 'var(--card-bg)';
                btn.style.color = 'var(--text-primary)';
            }
        }
    });
}

/**
 * Travel to a location
 */
async function travelToLocation(locationId) {
    try {
        const response = await fetch('/api/travel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                location_id: locationId
            })
        });

        const data = await response.json();

        if (data.success) {
            // Show travel message
            showMessage(`Traveled from ${data.old_location} to ${data.new_location}${data.time_passed > 0 ? ` (${data.time_passed} minutes)` : ''}`, 'success');

            // Close map modal
            closeModal('mapModal');

            // Refresh game state
            await refreshGameState();

            // Update character list to show only characters at new location
            await loadCharacters();

            // Show welcome message with location description
            addSystemMessage(`You arrive at ${data.location.name}. ${data.location.description}`);

            if (data.characters_present.length > 0) {
                addSystemMessage(`${data.characters_present.join(', ')} ${data.characters_present.length === 1 ? 'is' : 'are'} here.`);
            } else {
                addSystemMessage('Nobody else is here at the moment.');
            }
        } else {
            showMessage(data.error || 'Cannot travel to that location', 'error');
        }
    } catch (error) {
        console.error('Error traveling:', error);
        showMessage('Failed to travel', 'error');
    }
}

/**
 * Refresh game state after travel
 */
async function refreshGameState() {
    try {
        // Refresh time display
        const timeResponse = await fetch('/api/current-time');
        const timeData = await timeResponse.json();

        document.getElementById('current-time').textContent = timeData.time;
        document.getElementById('current-date').textContent = timeData.date;
        document.getElementById('current-period').textContent = timeData.period;
    } catch (error) {
        console.error('Error refreshing game state:', error);
    }
}

/**
 * Add a system message to the dialogue box
 */
function addSystemMessage(message) {
    const dialogueBox = document.getElementById('dialogue-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'dialogue-message';
    messageDiv.innerHTML = `<div class="system-message">${message}</div>`;
    dialogueBox.appendChild(messageDiv);
    dialogueBox.scrollTop = dialogueBox.scrollHeight;
}

/**
 * Show a temporary message notification
 */
function showMessage(message, type = 'info') {
    // Use the existing showMessage function if available, otherwise console log
    if (window.showMessage) {
        window.showMessage(message, type);
    } else {
        console.log(`[${type}] ${message}`);
        alert(message);
    }
}

/**
 * Reload characters list to show only characters at current location
 */
async function loadCharacters() {
    try {
        const response = await fetch('/api/characters');
        const data = await response.json();

        // Update location header
        if (data.location) {
            const header = document.getElementById('character-list-header');
            if (header) {
                header.textContent = `Characters at ${data.location}`;
            }
        }

        // Update character schedules (will use existing game.js function if available)
        if (window.updateCharacterSchedules) {
            window.updateCharacterSchedules();
        }
    } catch (error) {
        console.error('Error loading characters:', error);
    }
}
