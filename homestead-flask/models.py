from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class GardenBed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    width = db.Column(db.Float, nullable=False)
    length = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200))
    sun_exposure = db.Column(db.String(20))  # full, partial, shade
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    planted_items = db.relationship('PlantedItem', backref='garden_bed', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'width': self.width,
            'length': self.length,
            'location': self.location,
            'sunExposure': self.sun_exposure,
            'plants': [item.to_dict() for item in self.planted_items]
        }

class PlantedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.String(50), nullable=False)  # Reference to plant in database
    garden_bed_id = db.Column(db.Integer, db.ForeignKey('garden_bed.id'), nullable=False)
    planted_date = db.Column(db.DateTime, default=datetime.utcnow)
    transplant_date = db.Column(db.DateTime)
    harvest_date = db.Column(db.DateTime)
    position_x = db.Column(db.Integer, default=0)
    position_y = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='planned')  # planned, seeded, transplanted, growing, harvested
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'plantId': self.plant_id,
            'plantedDate': self.planted_date.isoformat() if self.planted_date else None,
            'transplantDate': self.transplant_date.isoformat() if self.transplant_date else None,
            'harvestDate': self.harvest_date.isoformat() if self.harvest_date else None,
            'position': {'x': self.position_x, 'y': self.position_y},
            'quantity': self.quantity,
            'status': self.status,
            'notes': self.notes
        }

class PlantingEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.String(50), nullable=False)
    garden_bed_id = db.Column(db.Integer)
    seed_start_date = db.Column(db.DateTime)
    transplant_date = db.Column(db.DateTime)
    direct_seed_date = db.Column(db.DateTime)
    expected_harvest_date = db.Column(db.DateTime)
    succession_planting = db.Column(db.Boolean, default=False)
    succession_interval = db.Column(db.Integer)  # days
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'plantId': self.plant_id,
            'gardenBedId': self.garden_bed_id,
            'seedStartDate': self.seed_start_date.isoformat() if self.seed_start_date else None,
            'transplantDate': self.transplant_date.isoformat() if self.transplant_date else None,
            'directSeedDate': self.direct_seed_date.isoformat() if self.direct_seed_date else None,
            'expectedHarvestDate': self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            'successionPlanting': self.succession_planting,
            'successionInterval': self.succession_interval,
            'completed': self.completed,
            'notes': self.notes
        }

class WinterPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    garden_bed_id = db.Column(db.String(50))
    technique = db.Column(db.String(50))  # quick-hoops, cold-frame, etc.
    plant_list = db.Column(db.Text)  # JSON array of plant IDs
    protection_layers = db.Column(db.Integer, default=1)
    harvest_window_start = db.Column(db.DateTime)
    harvest_window_end = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_plant_list(self):
        return json.loads(self.plant_list) if self.plant_list else []

    def set_plant_list(self, plants):
        self.plant_list = json.dumps(plants)

    def to_dict(self):
        return {
            'id': self.id,
            'gardenBedId': self.garden_bed_id,
            'technique': self.technique,
            'plantList': self.get_plant_list(),
            'protectionLayers': self.protection_layers,
            'harvestWindow': {
                'start': self.harvest_window_start.isoformat() if self.harvest_window_start else None,
                'end': self.harvest_window_end.isoformat() if self.harvest_window_end else None
            },
            'notes': self.notes
        }

class CompostPile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(200))
    width = db.Column(db.Float)
    length = db.Column(db.Float)
    height = db.Column(db.Float)
    last_turned = db.Column(db.DateTime)
    estimated_ready_date = db.Column(db.DateTime)
    temperature = db.Column(db.Float)
    moisture = db.Column(db.String(20), default='ideal')  # dry, ideal, wet
    cn_ratio = db.Column(db.Float, default=30.0)
    status = db.Column(db.String(20), default='building')  # building, cooking, curing, ready
    notes = db.Column(db.Text)

    # Relationships
    ingredients = db.relationship('CompostIngredient', backref='compost_pile', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'location': self.location,
            'size': {'width': self.width, 'length': self.length, 'height': self.height},
            'lastTurned': self.last_turned.isoformat() if self.last_turned else None,
            'estimatedReadyDate': self.estimated_ready_date.isoformat() if self.estimated_ready_date else None,
            'temperature': self.temperature,
            'moisture': self.moisture,
            'carbonNitrogenRatio': self.cn_ratio,
            'status': self.status,
            'notes': self.notes,
            'ingredients': [ing.to_dict() for ing in self.ingredients]
        }

class CompostIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    compost_pile_id = db.Column(db.Integer, db.ForeignKey('compost_pile.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # cubic feet
    type = db.Column(db.String(10))  # green or brown
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    cn_ratio = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'type': self.type,
            'addedDate': self.added_date.isoformat() if self.added_date else None,
            'carbonNitrogenRatio': self.cn_ratio
        }

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_setting(key, default=None):
        setting = Settings.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set_setting(key, value):
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Settings(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
