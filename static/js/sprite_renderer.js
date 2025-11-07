// Character Sprite Renderer
// Renders layered character sprites based on outfit configuration

/**
 * Render a character sprite
 * @param {string} characterName - Name of the character
 * @param {object} outfit - Outfit configuration {slot: item_id}
 * @param {string} containerId - ID of the container element
 * @param {object} options - Rendering options (size, clickable, etc.)
 */
function renderCharacterSprite(characterName, outfit, containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container ${containerId} not found`);
        return;
    }

    const defaults = {
        width: 300,
        height: 500,
        clickable: true,
        showPlaceholder: true
    };
    const opts = { ...defaults, ...options };

    // Clear container
    container.innerHTML = '';

    // Create sprite canvas
    const spriteContainer = document.createElement('div');
    spriteContainer.className = 'character-sprite-container';
    spriteContainer.style.width = opts.width + 'px';
    spriteContainer.style.height = opts.height + 'px';
    spriteContainer.style.position = 'relative';

    // Layer order (bottom to top)
    const layerOrder = [
        'base',           // Base body
        'bra',            // Underwear top
        'panties',        // Underwear bottom
        'bottom',         // Pants/skirt/etc
        'top',            // Shirt/blouse/etc
        'dress',          // Dress (if worn, replaces top+bottom visibility)
        'outerwear',      // Jacket/coat
        'shoes',          // Footwear
        'necklace',       // Jewelry
        'glasses',        // Eyewear
        'expression'      // Facial expression (always on top)
    ];

    // Build layers
    let layersRendered = 0;
    const baseImagePath = `/static/images/characters/${characterName}/`;

    layerOrder.forEach((slot, index) => {
        const itemId = outfit[slot];

        if (itemId || slot === 'base' || slot === 'expression') {
            const layer = document.createElement('img');
            layer.className = `sprite-layer sprite-layer-${slot}`;
            layer.style.position = 'absolute';
            layer.style.top = '0';
            layer.style.left = '0';
            layer.style.width = '100%';
            layer.style.height = '100%';
            layer.style.zIndex = index;
            layer.style.objectFit = 'contain';

            // Determine image path
            let imagePath;
            if (slot === 'base') {
                imagePath = baseImagePath + 'base/body.png';
            } else if (slot === 'expression') {
                const expression = outfit.expression || 'neutral';
                imagePath = baseImagePath + `expressions/${expression}.png`;
            } else if (itemId) {
                // Get clothing item image path from backend
                imagePath = baseImagePath + getClothingItemPath(itemId);
            }

            if (imagePath) {
                layer.src = imagePath;
                layer.dataset.slot = slot;
                layer.dataset.itemId = itemId || '';

                // Handle image load errors
                layer.onerror = function() {
                    if (opts.showPlaceholder) {
                        // Show placeholder if image doesn't exist
                        this.style.display = 'none';
                        console.warn(`Image not found: ${imagePath}`);
                    }
                };

                layer.onload = function() {
                    layersRendered++;
                };

                spriteContainer.appendChild(layer);
            }
        }
    });

    // Add placeholder if no images loaded
    if (opts.showPlaceholder) {
        const placeholder = document.createElement('div');
        placeholder.className = 'sprite-placeholder';
        placeholder.style.width = '100%';
        placeholder.style.height = '100%';
        placeholder.style.display = 'flex';
        placeholder.style.alignItems = 'center';
        placeholder.style.justifyContent = 'center';
        placeholder.style.background = 'linear-gradient(135deg, rgba(83, 52, 131, 0.3) 0%, rgba(233, 69, 96, 0.3) 100%)';
        placeholder.style.border = '2px dashed var(--border-color)';
        placeholder.style.borderRadius = '10px';
        placeholder.style.color = 'var(--text-secondary)';
        placeholder.style.fontSize = '14px';
        placeholder.style.textAlign = 'center';
        placeholder.style.padding = '20px';
        placeholder.style.position = 'absolute';
        placeholder.style.top = '0';
        placeholder.style.left = '0';
        placeholder.style.zIndex = '-1';
        placeholder.innerHTML = `
            <div>
                <div style="font-size: 48px; margin-bottom: 10px;">👤</div>
                <div>${characterName}</div>
                <div style="font-size: 12px; margin-top: 10px; opacity: 0.7;">
                    Place character images in:<br>
                    static/images/characters/${characterName}/
                </div>
            </div>
        `;
        spriteContainer.appendChild(placeholder);
    }

    // Make clickable if option enabled
    if (opts.clickable) {
        spriteContainer.style.cursor = 'pointer';
        spriteContainer.onclick = function() {
            openCharacterDressUp(characterName, outfit);
        };
        spriteContainer.title = 'Click to change outfit';
    }

    container.appendChild(spriteContainer);
}

/**
 * Get clothing item image path (cached from backend)
 */
const clothingItemCache = {};

function getClothingItemPath(itemId) {
    // This will be populated by backend data
    // For now, use simple path construction
    if (clothingItemCache[itemId]) {
        return clothingItemCache[itemId];
    }

    // Default path pattern
    return `clothing/${itemId}.png`;
}

/**
 * Load clothing items database from backend
 */
function loadClothingDatabase() {
    $.ajax({
        url: '/api/clothing-items',
        method: 'GET',
        success: function(data) {
            data.items.forEach(item => {
                clothingItemCache[item.id] = item.image_path;
            });
        },
        error: function() {
            console.warn('Failed to load clothing database, using default paths');
        }
    });
}

/**
 * Update a character's sprite outfit
 */
function updateCharacterOutfit(characterName, slot, itemId) {
    $.ajax({
        url: '/api/update-outfit',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            character: characterName,
            slot: slot,
            item_id: itemId
        }),
        success: function(data) {
            if (data.success) {
                // Refresh all sprite instances of this character
                refreshCharacterSprites(characterName);
            }
        },
        error: function() {
            console.error('Failed to update outfit');
        }
    });
}

/**
 * Refresh all sprite instances of a character
 */
function refreshCharacterSprites(characterName) {
    // Find all sprite containers for this character and re-render
    $(`.character-sprite-container[data-character="${characterName}"]`).each(function() {
        const containerId = $(this).attr('id');
        const outfit = getCharacterOutfit(characterName);
        renderCharacterSprite(characterName, outfit, containerId);
    });
}

/**
 * Get character's current outfit from backend
 */
function getCharacterOutfit(characterName, callback) {
    $.ajax({
        url: `/api/character/${characterName}`,
        method: 'GET',
        success: function(data) {
            if (callback) {
                callback(data.outfit);
            }
            return data.outfit;
        }
    });
}

/**
 * Open dress-up modal for a character
 */
function openCharacterDressUp(characterName, currentOutfit) {
    // Get character data and clothing options
    $.ajax({
        url: `/api/character/${characterName}`,
        method: 'GET',
        success: function(charData) {
            $.ajax({
                url: '/api/clothing-items',
                method: 'GET',
                success: function(clothingData) {
                    showDressUpModal(characterName, charData, clothingData.items);
                }
            });
        }
    });
}

/**
 * Show the dress-up modal
 */
function showDressUpModal(characterName, characterData, clothingItems) {
    const modal = $('#dressUpModal');

    // Set character name
    $('#dressup-character-name').text(characterName);

    // Render current outfit in preview
    const currentOutfit = characterData.outfit || {};
    renderCharacterSprite(characterName, currentOutfit, 'dressup-preview', {
        width: 300,
        height: 500,
        clickable: false
    });

    // Populate clothing options by category
    const categories = {
        'underwear': [],
        'tops': [],
        'bottoms': [],
        'dresses': [],
        'accessories': []
    };

    clothingItems.forEach(item => {
        if (categories[item.category]) {
            categories[item.category].push(item);
        }
    });

    // Build clothing selection UI
    let clothingHtml = '';
    Object.keys(categories).forEach(category => {
        if (categories[category].length > 0) {
            clothingHtml += `
                <div class="clothing-category">
                    <h3 class="category-title">${category.charAt(0).toUpperCase() + category.slice(1)}</h3>
                    <div class="clothing-items-grid">
            `;

            categories[category].forEach(item => {
                const isWearing = currentOutfit[item.slot] === item.id;
                clothingHtml += `
                    <div class="clothing-item ${isWearing ? 'wearing' : ''}"
                         data-item-id="${item.id}"
                         data-slot="${item.slot}"
                         onclick="selectClothingItem('${characterName}', '${item.slot}', '${item.id}')">
                        <div class="item-icon">👕</div>
                        <div class="item-name">${item.name}</div>
                        ${isWearing ? '<div class="wearing-badge">Wearing</div>' : ''}
                    </div>
                `;
            });

            clothingHtml += `
                    </div>
                </div>
            `;
        }
    });

    $('#dressup-clothing-options').html(clothingHtml);

    // Show modal
    modal.fadeIn(300);
}

/**
 * Select a clothing item in dress-up modal
 */
function selectClothingItem(characterName, slot, itemId) {
    // Update outfit via API
    updateCharacterOutfit(characterName, slot, itemId);

    // Update preview in modal
    getCharacterOutfit(characterName, function(outfit) {
        renderCharacterSprite(characterName, outfit, 'dressup-preview', {
            width: 300,
            height: 500,
            clickable: false
        });
    });

    // Update UI to show this item as wearing
    $('.clothing-item').removeClass('wearing');
    $('.wearing-badge').remove();
    $(`.clothing-item[data-item-id="${itemId}"]`).addClass('wearing').append('<div class="wearing-badge">Wearing</div>');
}

/**
 * Close dress-up modal
 */
function closeDressUpModal() {
    $('#dressUpModal').fadeOut(300);

    // Refresh character sprites in main game
    const characterName = $('#dressup-character-name').text();
    refreshCharacterSprites(characterName);

    // Also reload character cards
    location.reload();
}

// Initialize when page loads
$(document).ready(function() {
    // Load clothing database
    loadClothingDatabase();
});
