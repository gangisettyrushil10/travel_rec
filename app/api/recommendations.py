from flask import Blueprint, jsonify, request
from app.models.models import Destination, UserPreference
from app import db

recommendations_bp = Blueprint('recommendations', __name__)

def get_budget_category(budget):
    """Convert numeric budget to category"""
    try:
        budget = int(str(budget))  # Convert to string first, then to int
        if budget < 1000:
            return "budget"
        elif budget < 3000:
            return "moderate"
        else:
            return "luxury"
    except (TypeError, ValueError):
        print(f"Invalid budget value: {budget}")  # Debug print
        return "moderate"  # default fallback

@recommendations_bp.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    print("Recommendations endpoint called")
    user_id = request.args.get('user_id', type=int)
    print(f"User ID: {user_id}")
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    user_prefs = UserPreference.query.filter_by(user_id=user_id).first()
    print(f"User preferences: {user_prefs}")
    
    if not user_prefs:
        return jsonify({'error': 'No preferences found for this user'}), 404

    destinations = Destination.query.all()
    print(f"Found {len(destinations)} destinations")
    
    # Convert user's numeric budget to category
    user_budget_category = get_budget_category(user_prefs.budget)

    # Score each destination
    scored_destinations = []
    for dest in destinations:
        score = 0
        
        # Budget matching (0-3 points)
        if dest.budget_category == user_budget_category:
            score += 3
        elif (dest.budget_category == "moderate" and user_budget_category in ["budget", "luxury"]) or \
             (user_budget_category == "moderate"):
            score += 1
            
        # Activities matching (2 points per matching activity)
        user_activities = set(user_prefs.preferred_activities.split(',')) if user_prefs.preferred_activities else set()
        dest_activities = set(dest.activities.split(',')) if dest.activities else set()
        matching_activities = user_activities & dest_activities
        score += len(matching_activities) * 2

        # Add to scored list if there's any match
        if score > 0:
            scored_destinations.append({
                'destination': dest.to_dict(),
                'score': score,
                'matching_activities': list(matching_activities)
            })

    # Sort by score and rating
    scored_destinations.sort(key=lambda x: (x['score'], x['destination']['rating']), reverse=True)

    # Return top 5 recommendations with matching details
    top_recommendations = scored_destinations[:5]
    return jsonify({
        'recommendations': [d['destination'] for d in top_recommendations],
        'matching_details': [{
            'destination_id': d['destination']['id'],
            'score': d['score'],
            'matching_activities': d['matching_activities']
        } for d in top_recommendations]
    })