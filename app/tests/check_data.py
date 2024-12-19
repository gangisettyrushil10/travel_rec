from app import create_app, db
from app.models.models import Destination

def check_destinations():
    app = create_app()
    with app.app_context():
        # Get total count
        total = Destination.query.count()
        print(f"\nTotal destinations in database: {total}")
        
        # Show sample of destinations
        print("\nSample destinations:")
        sample = Destination.query.limit(5).all()
        for dest in sample:
            print(f"\nName: {dest.name}")
            print(f"Country: {dest.country}")
            print(f"Activities: {dest.activities}")
            print(f"Budget: {dest.budget_category}")
            print(f"Rating: {dest.rating}")
            print("-" * 50)

if __name__ == '__main__':
    check_destinations()