from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    preferences = db.relationship('UserPreference', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    budget = db.Column(db.Integer)  # Actual budget amount
    travel_style = db.Column(db.String(50))  # adventure, relaxation, culture, nature
    preferred_activities = db.Column(db.String(200))  # comma-separated list from preset activities
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserPreference {self.id}>'

    @property
    def budget_value(self):
        """Get budget as integer"""
        try:
            return int(self.budget)
        except (TypeError, ValueError):
            return 0

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    activities = db.Column(db.String(200))  # comma-separated list
    budget_category = db.Column(db.String(50))  # budget, moderate, luxury
    rating = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'activities': self.activities,
            'budget_category': self.budget_category,
            'rating': self.rating
        }
