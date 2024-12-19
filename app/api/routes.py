from flask import Blueprint, jsonify, request, render_template
from app.models.models import User, UserPreference
from app import db

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    return render_template('main/preferences.html')

@bp.route('/preferences', methods=['GET'])
def preferences_page():
    return render_template('main/preferences.html')

@bp.route('/recommendations', methods=['GET'])
def recommendations_page():
    return render_template('main/recommendations.html')

@bp.route('/api/preferences', methods=['GET', 'POST'])
def save_preferences():
    if request.method == 'POST':
        data = request.get_json()
        
        if data is None:
            return jsonify({"error": "No data provided"}), 400
        
        try:
            # Convert budget to integer
            budget = int(data.get('budget', 0))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid budget value"}), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == data.get('email')) | 
            (User.username == data.get('username'))
        ).first()
        
        if existing_user:
            preferences = UserPreference.query.filter_by(user_id=existing_user.id).first()
            if preferences:
                preferences.budget = budget  # Use converted integer
                preferences.travel_style = data.get('travel_style')
                preferences.preferred_activities = ','.join(data.get('preferred_activities', []))
            else:
                preferences = UserPreference(
                    user_id=existing_user.id,
                    budget=budget,  # Use converted integer
                    travel_style=data.get('travel_style'),
                    preferred_activities=','.join(data.get('preferred_activities', []))
                )
                db.session.add(preferences)
            
            try:
                db.session.commit()
                return jsonify({"message": "Preferences updated successfully", "user_id": existing_user.id})
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500
        
        # Create new user and preferences
        try:
            user = User(
                username=data.get('username'),
                email=data.get('email')
            )
            db.session.add(user)
            db.session.commit()
            
            preferences = UserPreference(
                user_id=user.id,
                budget=budget,  # Use converted integer
                travel_style=data.get('travel_style'),
                preferred_activities=','.join(data.get('preferred_activities', []))
            )
            db.session.add(preferences)
            db.session.commit()
            
            return jsonify({"message": "Preferences saved successfully", "user_id": user.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to save preferences: {str(e)}"}), 500
    
    return render_template('main/preferences.html')