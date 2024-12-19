import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models.models import Destination

def populate_destinations():
    app = create_app()
    with app.app_context():
        # Clear existing destinations
        Destination.query.delete()
        
        # Add sample destinations
        destinations = [
            {
                'name': 'Paris',
                'country': 'France',
                'activities': 'museums,cultural_sites,food_and_dining',
                'budget_category': 'moderate',
                'rating': 4.5
            },
            {
                'name': 'Bali',
                'country': 'Indonesia',
                'activities': 'beach,water_sports,nature',
                'budget_category': 'budget',
                'rating': 4.3
            },
            {
                'name': 'Swiss Alps',
                'country': 'Switzerland',
                'activities': 'hiking,adventure_sports,nature',
                'budget_category': 'luxury',
                'rating': 4.8
            }
        ]
        
        for dest_data in destinations:
            destination = Destination(**dest_data)
            db.session.add(destination)
        
        db.session.commit()
        print("Sample destinations added successfully!")

if __name__ == '__main__':
    populate_destinations()