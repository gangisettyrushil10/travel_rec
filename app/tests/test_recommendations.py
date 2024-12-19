import requests
import json

def test_recommendations():
    base_url = "http://127.0.0.1:5000"

    # First, create test users with preferences
    test_users = [
        {
            "username": "budget_traveler",
            "email": "budget@test.com",
            "budget": 800,
            "travel_style": "culture",
            "preferred_activities": ["museums", "cultural_sites", "sightseeing"]
        },
        {
            "username": "luxury_traveler",
            "email": "luxury@test.com",
            "budget": 5000,
            "travel_style": "relaxation",
            "preferred_activities": ["beach", "water_sports", "food_and_dining"]
        },
        {
            "username": "adventure_seeker",
            "email": "adventure@test.com",
            "budget": 2000,
            "travel_style": "adventure",
            "preferred_activities": ["hiking", "adventure_sports", "nature"]
        }
    ]

    created_users = []
    
    # Create users and their preferences
    for user in test_users:
        response = requests.post(
            f"{base_url}/api/preferences",
            json=user
        )
        if response.status_code == 200:
            user_data = response.json()
            created_users.append({
                "user_id": user_data["user_id"],
                "description": f"{user['travel_style'].title()} traveler with {get_budget_category(user['budget'])} budget"
            })
            print(f"Created user: {user['username']}")
        else:
            print(f"Failed to create user: {user['username']}")
            print(response.json())

    # Test recommendations for each user
    for user in created_users:
        print(f"\nTesting recommendations for {user['description']}")
        response = requests.get(f"{base_url}/api/recommendations?user_id={user['user_id']}")
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            matching_details = data.get('matching_details', [])
            
            print(f"Found {len(recommendations)} recommendations:")
            for i, (rec, details) in enumerate(zip(recommendations, matching_details), 1):
                print(f"\n{i}. {rec['name']}")
                print(f"   Country: {rec['country']}")
                print(f"   Activities: {rec['activities']}")
                print(f"   Budget: {rec['budget_category']}")
                print(f"   Rating: {rec['rating']}")
                print(f"   Match Score: {details['score']}")
                print(f"   Matching Activities: {', '.join(details['matching_activities'])}")
        else:
            print(f"Error: {response.status_code}")
            print(response.json())

def get_budget_category(budget):
    if budget < 1000:
        return "budget"
    elif budget < 3000:
        return "moderate"
    else:
        return "luxury"

if __name__ == '__main__':
    test_recommendations()
