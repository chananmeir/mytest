from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from models import db, GardenBed, PlantedItem, PlantingEvent, WinterPlan, CompostPile, CompostIngredient, Settings, Photo, HarvestRecord, SeedInventory
from plant_database import PLANT_DATABASE, COMPOST_MATERIALS, get_plant_by_id, get_winter_hardy_plants
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.utils import secure_filename
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///homestead.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    # Set default frost dates if not set
    if not Settings.get_setting('last_frost_date'):
        Settings.set_setting('last_frost_date', '2024-04-15')
    if not Settings.get_setting('first_frost_date'):
        Settings.set_setting('first_frost_date', '2024-10-15')

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

# ==================== GARDEN PLANNER ROUTES ====================

@app.route('/garden-planner')
def garden_planner():
    """Garden planner page"""
    beds = GardenBed.query.all()
    return render_template('garden_planner.html', beds=beds, plants=PLANT_DATABASE)

@app.route('/visual-designer')
def visual_designer():
    """Visual garden designer page"""
    beds = GardenBed.query.all()
    return render_template('visual_designer.html', beds=beds, plants=PLANT_DATABASE)

@app.route('/api/garden-beds', methods=['GET', 'POST'])
def garden_beds():
    """Get all garden beds or create new one"""
    if request.method == 'POST':
        data = request.json
        bed = GardenBed(
            name=data['name'],
            width=data['width'],
            length=data['length'],
            location=data.get('location', ''),
            sun_exposure=data.get('sunExposure', 'full')
        )
        db.session.add(bed)
        db.session.commit()
        return jsonify(bed.to_dict()), 201

    beds = GardenBed.query.all()
    return jsonify([bed.to_dict() for bed in beds])

@app.route('/api/garden-beds/<int:bed_id>', methods=['GET', 'PUT', 'DELETE'])
def garden_bed(bed_id):
    """Get, update, or delete a specific garden bed"""
    bed = GardenBed.query.get_or_404(bed_id)

    if request.method == 'DELETE':
        db.session.delete(bed)
        db.session.commit()
        return '', 204

    if request.method == 'PUT':
        data = request.json
        bed.name = data.get('name', bed.name)
        bed.width = data.get('width', bed.width)
        bed.length = data.get('length', bed.length)
        bed.location = data.get('location', bed.location)
        bed.sun_exposure = data.get('sunExposure', bed.sun_exposure)
        db.session.commit()

    return jsonify(bed.to_dict())

@app.route('/api/planted-items', methods=['POST'])
def add_planted_item():
    """Add a plant to a garden bed"""
    data = request.json
    position = data.get('position', {})
    item = PlantedItem(
        plant_id=data['plantId'],
        garden_bed_id=data['gardenBedId'],
        planted_date=datetime.fromisoformat(data.get('plantedDate', datetime.now().isoformat())),
        quantity=data.get('quantity', 1),
        status=data.get('status', 'planned'),
        notes=data.get('notes', ''),
        position_x=position.get('x', 0),
        position_y=position.get('y', 0)
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@app.route('/api/planted-items/<int:item_id>', methods=['PUT', 'DELETE'])
def planted_item(item_id):
    """Update or delete a planted item"""
    item = PlantedItem.query.get_or_404(item_id)

    if request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return '', 204

    data = request.json
    item.status = data.get('status', item.status)
    item.notes = data.get('notes', item.notes)
    if 'harvestDate' in data and data['harvestDate']:
        item.harvest_date = datetime.fromisoformat(data['harvestDate'])
    db.session.commit()
    return jsonify(item.to_dict())

# ==================== PLANTING CALENDAR ROUTES ====================

@app.route('/planting-calendar')
def planting_calendar():
    """Planting calendar page"""
    events = PlantingEvent.query.order_by(PlantingEvent.seed_start_date).all()
    last_frost = Settings.get_setting('last_frost_date', '2024-04-15')
    first_frost = Settings.get_setting('first_frost_date', '2024-10-15')
    return render_template('planting_calendar.html',
                         events=events,
                         plants=PLANT_DATABASE,
                         last_frost_date=last_frost,
                         first_frost_date=first_frost)

@app.route('/api/planting-events', methods=['GET', 'POST'])
def planting_events():
    """Get all planting events or create new one"""
    if request.method == 'POST':
        data = request.json
        event = PlantingEvent(
            plant_id=data['plantId'],
            garden_bed_id=data.get('gardenBedId'),
            seed_start_date=datetime.fromisoformat(data['seedStartDate']) if data.get('seedStartDate') else None,
            transplant_date=datetime.fromisoformat(data['transplantDate']) if data.get('transplantDate') else None,
            direct_seed_date=datetime.fromisoformat(data['directSeedDate']) if data.get('directSeedDate') else None,
            expected_harvest_date=datetime.fromisoformat(data['expectedHarvestDate']),
            succession_planting=data.get('successionPlanting', False),
            succession_interval=data.get('successionInterval'),
            notes=data.get('notes', '')
        )
        db.session.add(event)
        db.session.commit()
        return jsonify(event.to_dict()), 201

    events = PlantingEvent.query.all()
    return jsonify([event.to_dict() for event in events])

@app.route('/api/planting-events/<int:event_id>', methods=['PUT', 'DELETE'])
def planting_event(event_id):
    """Update or delete a planting event"""
    event = PlantingEvent.query.get_or_404(event_id)

    if request.method == 'DELETE':
        db.session.delete(event)
        db.session.commit()
        return '', 204

    data = request.json
    event.completed = data.get('completed', event.completed)
    event.notes = data.get('notes', event.notes)
    db.session.commit()
    return jsonify(event.to_dict())

@app.route('/api/frost-dates', methods=['GET', 'POST'])
def frost_dates():
    """Get or update frost dates"""
    if request.method == 'POST':
        data = request.json
        Settings.set_setting('last_frost_date', data['lastFrostDate'])
        Settings.set_setting('first_frost_date', data['firstFrostDate'])
        return jsonify({'success': True})

    return jsonify({
        'lastFrostDate': Settings.get_setting('last_frost_date', '2024-04-15'),
        'firstFrostDate': Settings.get_setting('first_frost_date', '2024-10-15')
    })

# ==================== WINTER GARDEN ROUTES ====================

@app.route('/winter-garden')
def winter_garden():
    """Winter garden planning page"""
    plans = WinterPlan.query.all()
    winter_plants = get_winter_hardy_plants()
    return render_template('winter_garden.html', plans=plans, plants=winter_plants)

@app.route('/api/winter-plans', methods=['GET', 'POST'])
def winter_plans():
    """Get all winter plans or create new one"""
    if request.method == 'POST':
        data = request.json
        plan = WinterPlan(
            garden_bed_id=data['gardenBedId'],
            technique=data['technique'],
            protection_layers=data.get('protectionLayers', 1),
            harvest_window_start=datetime.fromisoformat(data['harvestWindow']['start']),
            harvest_window_end=datetime.fromisoformat(data['harvestWindow']['end']),
            notes=data.get('notes', '')
        )
        plan.set_plant_list(data.get('plantList', []))
        db.session.add(plan)
        db.session.commit()
        return jsonify(plan.to_dict()), 201

    plans = WinterPlan.query.all()
    return jsonify([plan.to_dict() for plan in plans])

@app.route('/api/winter-plans/<int:plan_id>', methods=['DELETE'])
def winter_plan(plan_id):
    """Delete a winter plan"""
    plan = WinterPlan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    return '', 204

# ==================== WEATHER ROUTES ====================

@app.route('/weather')
def weather():
    """Weather and alerts page"""
    # Mock weather data for now
    return render_template('weather.html')

# ==================== COMPOST TRACKER ROUTES ====================

@app.route('/compost-tracker')
def compost_tracker():
    """Compost tracker page"""
    piles = CompostPile.query.all()
    return render_template('compost_tracker.html',
                         piles=piles,
                         materials=COMPOST_MATERIALS)

@app.route('/api/compost-piles', methods=['GET', 'POST'])
def compost_piles():
    """Get all compost piles or create new one"""
    if request.method == 'POST':
        data = request.json
        pile = CompostPile(
            name=data['name'],
            location=data['location'],
            width=data['size']['width'],
            length=data['size']['length'],
            height=data['size']['height'],
            estimated_ready_date=datetime.now() + timedelta(days=90)
        )
        db.session.add(pile)
        db.session.commit()
        return jsonify(pile.to_dict()), 201

    piles = CompostPile.query.all()
    return jsonify([pile.to_dict() for pile in piles])

@app.route('/api/compost-piles/<int:pile_id>', methods=['GET', 'PUT', 'DELETE'])
def compost_pile(pile_id):
    """Get, update, or delete a compost pile"""
    pile = CompostPile.query.get_or_404(pile_id)

    if request.method == 'DELETE':
        db.session.delete(pile)
        db.session.commit()
        return '', 204

    if request.method == 'PUT':
        data = request.json
        pile.status = data.get('status', pile.status)
        pile.moisture = data.get('moisture', pile.moisture)
        if data.get('lastTurned'):
            pile.last_turned = datetime.now()
        db.session.commit()

    return jsonify(pile.to_dict())

@app.route('/api/compost-piles/<int:pile_id>/ingredients', methods=['POST'])
def add_compost_ingredient(pile_id):
    """Add ingredient to compost pile"""
    pile = CompostPile.query.get_or_404(pile_id)
    data = request.json

    material = COMPOST_MATERIALS.get(data['material'])
    if not material:
        return jsonify({'error': 'Invalid material'}), 400

    ingredient = CompostIngredient(
        compost_pile_id=pile_id,
        name=data['material'],
        amount=data['amount'],
        type=material['type'],
        cn_ratio=material['cnRatio']
    )
    db.session.add(ingredient)

    # Recalculate C:N ratio
    total_carbon = 0
    total_nitrogen = 0
    for ing in pile.ingredients:
        carbon = (ing.cn_ratio * ing.amount) / 31
        nitrogen = ing.amount / 31
        total_carbon += carbon
        total_nitrogen += nitrogen

    # Add new ingredient
    carbon = (ingredient.cn_ratio * ingredient.amount) / 31
    nitrogen = ingredient.amount / 31
    total_carbon += carbon
    total_nitrogen += nitrogen

    pile.cn_ratio = total_carbon / total_nitrogen if total_nitrogen > 0 else 30

    db.session.commit()
    return jsonify(pile.to_dict())

# ==================== API ROUTES ====================

@app.route('/api/plants')
def get_plants():
    """Get all plants"""
    return jsonify(PLANT_DATABASE)

@app.route('/api/plants/<plant_id>')
def get_plant(plant_id):
    """Get specific plant"""
    plant = get_plant_by_id(plant_id)
    if plant:
        return jsonify(plant)
    return jsonify({'error': 'Plant not found'}), 404

# ==================== PHOTO UPLOAD ROUTES ====================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/photos')
def photos():
    """Photo gallery page"""
    photos = Photo.query.order_by(Photo.uploaded_at.desc()).all()
    return render_template('photos.html', photos=photos)

@app.route('/api/photos', methods=['GET', 'POST'])
def api_photos():
    """Get all photos or upload new one"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to avoid conflicts
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Save and optimize image
            img = Image.open(file)
            # Resize if too large
            max_size = (1920, 1920)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(filepath, optimize=True, quality=85)

            photo = Photo(
                filename=filename,
                filepath=f"/static/uploads/{filename}",
                caption=request.form.get('caption', ''),
                category=request.form.get('category', 'garden'),
                garden_bed_id=request.form.get('gardenBedId') or None
            )
            db.session.add(photo)
            db.session.commit()
            return jsonify(photo.to_dict()), 201

        return jsonify({'error': 'Invalid file type'}), 400

    photos = Photo.query.all()
    return jsonify([photo.to_dict() for photo in photos])

@app.route('/api/photos/<int:photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    """Delete a photo"""
    photo = Photo.query.get_or_404(photo_id)
    # Delete file from filesystem
    filepath = os.path.join('static/uploads', photo.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(photo)
    db.session.commit()
    return '', 204

# ==================== HARVEST TRACKER ROUTES ====================

@app.route('/harvest-tracker')
def harvest_tracker():
    """Harvest tracker page"""
    records = HarvestRecord.query.order_by(HarvestRecord.harvest_date.desc()).all()
    return render_template('harvest_tracker.html', records=records, plants=PLANT_DATABASE)

@app.route('/api/harvests', methods=['GET', 'POST'])
def api_harvests():
    """Get all harvest records or create new one"""
    if request.method == 'POST':
        data = request.json
        record = HarvestRecord(
            plant_id=data['plantId'],
            planted_item_id=data.get('plantedItemId'),
            harvest_date=datetime.fromisoformat(data.get('harvestDate', datetime.now().isoformat())),
            quantity=data['quantity'],
            unit=data.get('unit', 'lbs'),
            quality=data.get('quality', 'good'),
            notes=data.get('notes', '')
        )
        db.session.add(record)
        db.session.commit()
        return jsonify(record.to_dict()), 201

    records = HarvestRecord.query.all()
    return jsonify([record.to_dict() for record in records])

@app.route('/api/harvests/<int:record_id>', methods=['DELETE'])
def delete_harvest(record_id):
    """Delete a harvest record"""
    record = HarvestRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return '', 204

@app.route('/api/harvests/stats')
def harvest_stats():
    """Get harvest statistics"""
    records = HarvestRecord.query.all()
    stats = {}
    for record in records:
        if record.plant_id not in stats:
            stats[record.plant_id] = {'total': 0, 'count': 0, 'unit': record.unit}
        stats[record.plant_id]['total'] += record.quantity
        stats[record.plant_id]['count'] += 1
    return jsonify(stats)

# ==================== SEED INVENTORY ROUTES ====================

@app.route('/seed-inventory')
def seed_inventory():
    """Seed inventory page"""
    seeds = SeedInventory.query.order_by(SeedInventory.variety).all()
    return render_template('seed_inventory.html', seeds=seeds, plants=PLANT_DATABASE)

@app.route('/api/seeds', methods=['GET', 'POST'])
def api_seeds():
    """Get all seed inventory or add new seed"""
    if request.method == 'POST':
        data = request.json
        seed = SeedInventory(
            plant_id=data['plantId'],
            variety=data['variety'],
            brand=data.get('brand', ''),
            quantity=data.get('quantity', 0),
            purchase_date=datetime.fromisoformat(data['purchaseDate']) if data.get('purchaseDate') else None,
            expiration_date=datetime.fromisoformat(data['expirationDate']) if data.get('expirationDate') else None,
            germination_rate=data.get('germinationRate'),
            location=data.get('location', ''),
            price=data.get('price'),
            notes=data.get('notes', '')
        )
        db.session.add(seed)
        db.session.commit()
        return jsonify(seed.to_dict()), 201

    seeds = SeedInventory.query.all()
    return jsonify([seed.to_dict() for seed in seeds])

@app.route('/api/seeds/<int:seed_id>', methods=['PUT', 'DELETE'])
def seed_item(seed_id):
    """Update or delete seed inventory"""
    seed = SeedInventory.query.get_or_404(seed_id)

    if request.method == 'DELETE':
        db.session.delete(seed)
        db.session.commit()
        return '', 204

    data = request.json
    seed.quantity = data.get('quantity', seed.quantity)
    seed.germination_rate = data.get('germinationRate', seed.germination_rate)
    seed.notes = data.get('notes', seed.notes)
    db.session.commit()
    return jsonify(seed.to_dict())

# ==================== PDF EXPORT ROUTE ====================

@app.route('/api/export-garden-plan/<int:bed_id>')
def export_garden_plan(bed_id):
    """Export garden plan as PDF"""
    bed = GardenBed.query.get_or_404(bed_id)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 24)
    p.drawString(1*inch, height - 1*inch, f"Garden Plan: {bed.name}")

    # Bed info
    p.setFont("Helvetica", 12)
    y = height - 1.5*inch
    p.drawString(1*inch, y, f"Size: {bed.width}' x {bed.length}'")
    p.drawString(1*inch, y - 0.3*inch, f"Location: {bed.location}")
    p.drawString(1*inch, y - 0.6*inch, f"Sun Exposure: {bed.sun_exposure}")

    # Plants list
    y -= 1.2*inch
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1*inch, y, "Plants:")

    y -= 0.4*inch
    p.setFont("Helvetica", 10)
    for item in bed.planted_items:
        plant = get_plant_by_id(item.plant_id)
        if plant:
            p.drawString(1.2*inch, y, f"• {plant['name']} - Position: ({item.position_x}, {item.position_y}) - Status: {item.status}")
            y -= 0.3*inch
            if y < 1*inch:  # New page if needed
                p.showPage()
                y = height - 1*inch
                p.setFont("Helvetica", 10)

    # Footer
    p.setFont("Helvetica", 8)
    p.drawString(1*inch, 0.5*inch, f"Generated by Homestead Tracker - {datetime.now().strftime('%Y-%m-%d')}")

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{bed.name}_plan.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
