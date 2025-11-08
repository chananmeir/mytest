"""
Asset Manager System

Web UI for managing clothing items, graphics, and visual content.
Makes it easy to add, edit, and organize game assets.
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from flask import Blueprint, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import shutil

# Create blueprint
asset_manager = Blueprint('asset_manager', __name__, url_prefix='/assets')

# Configuration
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
CLOTHING_DATA_FILE = 'data/clothing_items.py'
BACKUP_FOLDER = 'data/backups'


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def backup_clothing_file():
    """Create backup of clothing_items.py before modifying"""
    os.makedirs(BACKUP_FOLDER, exist_ok=True)

    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_FOLDER, f'clothing_items_{timestamp}.py')

    if os.path.exists(CLOTHING_DATA_FILE):
        shutil.copy2(CLOTHING_DATA_FILE, backup_path)
        return backup_path
    return None


def parse_clothing_items():
    """
    Parse clothing_items.py to extract all items

    Returns dict of all clothing items
    """
    try:
        # Import the module
        from data.clothing_items import get_all_clothing_items

        all_items = get_all_clothing_items()

        # Convert to serializable format
        items_dict = {}
        for item_id, item in all_items.items():
            items_dict[item_id] = {
                'id': item.id,
                'name': item.name,
                'category': item.category,
                'slot': item.slot,
                'image_path': item.image_path,
                'description': item.description,
                'tags': item.tags,
                'coverage': item.coverage,
                'formality': item.formality,
                'suggestibility_factor': item.suggestibility_factor
            }

        return items_dict

    except Exception as e:
        print(f"Error parsing clothing items: {e}")
        return {}


def generate_clothing_item_code(item_data: Dict) -> str:
    """
    Generate Python code for a ClothingItem

    Returns the code string
    """
    # Format tags list
    tags_str = ', '.join([f"'{tag}'" for tag in item_data['tags']])

    code = f"""    '{item_data['id']}': ClothingItem(
        id='{item_data['id']}',
        name='{item_data['name']}',
        category='{item_data['category']}',
        slot='{item_data['slot']}',
        image_path='{item_data['image_path']}',
        description=\"\"{item_data['description']}\"\"\",
        tags=[{tags_str}],
        coverage={item_data['coverage']},
        formality={item_data['formality']},
        suggestibility_factor={item_data.get('suggestibility_factor', 1.0)}
    ),
"""
    return code


def add_clothing_item_to_file(item_data: Dict) -> tuple[bool, str]:
    """
    Add a new clothing item to clothing_items.py

    Returns (success, message)
    """
    try:
        # Backup first
        backup_path = backup_clothing_file()

        # Read existing file
        with open(CLOTHING_DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        # Generate code for new item
        new_item_code = generate_clothing_item_code(item_data)

        # Determine which section to add to based on category
        category = item_data['category'].upper()
        section_marker = f"{category}_ITEMS = {{"

        if section_marker not in content:
            return False, f"Category section {category}_ITEMS not found in file"

        # Find insertion point (before closing brace of that section)
        section_start = content.find(section_marker)
        section_content = content[section_start:]

        # Find the closing brace
        brace_count = 0
        insert_pos = section_start
        for i, char in enumerate(content[section_start:]):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    insert_pos = section_start + i
                    break

        # Insert new item before closing brace
        new_content = content[:insert_pos] + new_item_code + "\n" + content[insert_pos:]

        # Write back
        with open(CLOTHING_DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True, f"Added item '{item_data['name']}' (backup: {backup_path})"

    except Exception as e:
        return False, f"Error adding item: {str(e)}"


# ==================== ROUTES ====================

@asset_manager.route('/')
def index():
    """Asset manager main page"""
    return render_template('asset_manager.html')


@asset_manager.route('/clothing')
def clothing_manager():
    """Clothing items manager page"""
    return render_template('clothing_manager.html')


@asset_manager.route('/api/clothing/list')
def api_list_clothing():
    """List all clothing items"""
    items = parse_clothing_items()

    # Group by category
    by_category = {}
    for item_id, item in items.items():
        category = item['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)

    return jsonify({
        'success': True,
        'items': items,
        'by_category': by_category,
        'count': len(items)
    })


@asset_manager.route('/api/clothing/get/<item_id>')
def api_get_clothing_item(item_id):
    """Get a specific clothing item"""
    items = parse_clothing_items()

    if item_id not in items:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    return jsonify({
        'success': True,
        'item': items[item_id]
    })


@asset_manager.route('/api/clothing/add', methods=['POST'])
def api_add_clothing():
    """Add new clothing item"""
    data = request.json

    # Validate required fields
    required = ['id', 'name', 'category', 'slot', 'description', 'tags', 'coverage', 'formality']
    for field in required:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

    # Set defaults
    if 'image_path' not in data or not data['image_path']:
        data['image_path'] = f"{data['category']}/{data['id']}.png"

    if 'suggestibility_factor' not in data:
        data['suggestibility_factor'] = 1.0

    # Add to file
    success, message = add_clothing_item_to_file(data)

    if success:
        return jsonify({
            'success': True,
            'message': message,
            'item': data
        })
    else:
        return jsonify({'success': False, 'error': message}), 500


@asset_manager.route('/api/clothing/update/<item_id>', methods=['POST'])
def api_update_clothing(item_id):
    """Update existing clothing item"""
    # For now, this would require more complex parsing and rewriting
    # Recommend: Delete old + Add new approach
    return jsonify({
        'success': False,
        'error': 'Update not yet implemented. Use delete + add instead.'
    }), 501


@asset_manager.route('/api/clothing/delete/<item_id>', methods=['POST'])
def api_delete_clothing(item_id):
    """Delete clothing item"""
    try:
        # Backup first
        backup_path = backup_clothing_file()

        # Read file
        with open(CLOTHING_DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find item definition
        item_marker = f"'{item_id}': ClothingItem("

        if item_marker not in content:
            return jsonify({'success': False, 'error': 'Item not found'}), 404

        # Find start of item
        item_start = content.find(item_marker)

        # Find end (closing paren + comma)
        paren_count = 0
        in_item = False
        item_end = item_start

        for i, char in enumerate(content[item_start:]):
            if char == '(':
                paren_count += 1
                in_item = True
            elif char == ')':
                paren_count -= 1
                if paren_count == 0 and in_item:
                    # Found closing paren
                    # Skip to comma
                    rest = content[item_start + i:]
                    comma_pos = rest.find(',')
                    if comma_pos != -1:
                        item_end = item_start + i + comma_pos + 1
                    break

        # Remove item (including leading whitespace and trailing newline)
        # Find line start
        line_start = item_start
        while line_start > 0 and content[line_start-1] not in '\n':
            line_start -= 1

        # Find line end
        line_end = item_end
        while line_end < len(content) and content[line_end] != '\n':
            line_end += 1
        if line_end < len(content):
            line_end += 1  # Include newline

        # Remove
        new_content = content[:line_start] + content[line_end:]

        # Write back
        with open(CLOTHING_DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return jsonify({
            'success': True,
            'message': f'Deleted item {item_id} (backup: {backup_path})'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@asset_manager.route('/api/upload/image', methods=['POST'])
def api_upload_image():
    """Upload image file"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'Invalid file type. Allowed: {ALLOWED_EXTENSIONS}'
        }), 400

    # Get category and create directory
    category = request.form.get('category', 'misc')
    character = request.form.get('character', 'general')

    upload_dir = os.path.join(UPLOAD_FOLDER, 'characters', character, category)
    os.makedirs(upload_dir, exist_ok=True)

    # Secure filename
    filename = secure_filename(file.filename)

    # Save file
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Return relative path
    relative_path = os.path.join(category, filename)

    return jsonify({
        'success': True,
        'message': 'File uploaded successfully',
        'filename': filename,
        'path': relative_path,
        'full_path': filepath
    })


@asset_manager.route('/api/images/list')
def api_list_images():
    """List all uploaded images"""
    images = {}

    base_path = os.path.join(UPLOAD_FOLDER, 'characters')

    if os.path.exists(base_path):
        for character in os.listdir(base_path):
            char_path = os.path.join(base_path, character)
            if not os.path.isdir(char_path):
                continue

            images[character] = {}

            for category in os.listdir(char_path):
                cat_path = os.path.join(char_path, category)
                if not os.path.isdir(cat_path):
                    continue

                images[character][category] = []

                for img in os.listdir(cat_path):
                    if allowed_file(img):
                        images[character][category].append({
                            'filename': img,
                            'path': os.path.join(category, img),
                            'url': f'/static/images/characters/{character}/{category}/{img}'
                        })

    return jsonify({
        'success': True,
        'images': images
    })


@asset_manager.route('/api/categories')
def api_get_categories():
    """Get available categories and slots"""
    return jsonify({
        'success': True,
        'categories': ['underwear', 'tops', 'bottoms', 'dresses', 'outerwear', 'accessories'],
        'slots': ['bra', 'panties', 'top', 'bottom', 'dress', 'shoes', 'jewelry', 'outerwear'],
        'tag_suggestions': [
            'revealing', 'sexy', 'bold', 'provocative',
            'formal', 'professional', 'modest', 'conservative',
            'casual', 'comfortable', 'elegant', 'athletic',
            'cute', 'sporty', 'business', 'party'
        ]
    })


@asset_manager.route('/api/backup/list')
def api_list_backups():
    """List all backups"""
    backups = []

    if os.path.exists(BACKUP_FOLDER):
        for filename in sorted(os.listdir(BACKUP_FOLDER), reverse=True):
            if filename.endswith('.py'):
                filepath = os.path.join(BACKUP_FOLDER, filename)
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })

    return jsonify({
        'success': True,
        'backups': backups
    })


@asset_manager.route('/api/backup/restore/<filename>', methods=['POST'])
def api_restore_backup(filename):
    """Restore from backup"""
    backup_path = os.path.join(BACKUP_FOLDER, filename)

    if not os.path.exists(backup_path):
        return jsonify({'success': False, 'error': 'Backup not found'}), 404

    try:
        # Create backup of current file first
        current_backup = backup_clothing_file()

        # Restore
        shutil.copy2(backup_path, CLOTHING_DATA_FILE)

        return jsonify({
            'success': True,
            'message': f'Restored from {filename} (current backed up to {current_backup})'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
