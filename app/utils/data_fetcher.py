import requests
from app import db
from app.models.models import Destination
import time
from geopy.geocoders import Nominatim

# Predefined activities for consistency
PRESET_ACTIVITIES = [
    'hiking',
    'beach',
    'sightseeing',
    'museums',
    'shopping',
    'food_and_dining',
    'nightlife',
    'adventure_sports',
    'cultural_sites',
    'nature',
    'photography',
    'water_sports'
]

class OpenStreetMapFetcher:
    def __init__(self):
        self.base_url = "http://overpass-api.de/api/interpreter"
        self.geocoder = Nominatim(user_agent="travel_recommender")
        
    def fetch_destinations_by_region(self, country_code, batch_size=50, max_destinations=1000):
        query = f"""
        [out:json][timeout:25];
        area["ISO3166-1"="{country_code}"][admin_level=2];
        (
          node["tourism"]["name:en"](area);
          way["tourism"]["name:en"](area);
          node["historic"]["name:en"](area);
          way["historic"]["name:en"](area);
          node["natural"]["name:en"](area);
          way["natural"]["name:en"](area);
        );
        out body {max_destinations};
        """
        
        try:
            print(f"Sending request for country code: {country_code}")
            response = requests.get(self.base_url, params={'data': query})
            response.raise_for_status()
            data = response.json()
            
            destinations = []
            total_processed = 0
            
            for element in data.get('elements', []):
                if total_processed >= max_destinations:
                    break
                    
                if 'tags' in element:
                    tags = element['tags']
                    
                    # Get English name or default name
                    name = tags.get('name:en') or tags.get('name')
                    if not name:
                        continue
                    
                    # Map OSM tags to preset activities
                    activities = self._map_tags_to_activities(tags)
                    if not activities:
                        continue
                    
                    destination = {
                        'name': name,
                        'country': self._get_country_name(country_code),
                        'description': self._generate_description(tags),
                        'budget_category': self._determine_budget_category(tags),
                        'activities': ','.join(activities),
                        'rating': float(tags.get('rating', 4.0))
                    }
                    
                    destinations.append(destination)
                    total_processed += 1
                    
                    if len(destinations) >= batch_size:
                        yield destinations
                        destinations = []
            
            if destinations:
                yield destinations
                
        except Exception as e:
            print(f"Error fetching data for country code {country_code}: {str(e)}")
            return []

    def _map_tags_to_activities(self, tags):
        """Map OSM tags to preset activities"""
        activities = set()
        
        # Mapping logic
        if 'tourism' in tags:
            if tags['tourism'] in ['museum', 'gallery']:
                activities.add('museums')
            elif tags['tourism'] in ['hotel', 'hostel']:
                activities.add('food_and_dining')
                
        if 'leisure' in tags:
            if tags['leisure'] in ['beach_resort', 'swimming_area']:
                activities.add('beach')
            elif tags['leisure'] == 'sports_centre':
                activities.add('adventure_sports')
                
        if 'historic' in tags:
            activities.add('cultural_sites')
            activities.add('sightseeing')
            
        if 'natural' in tags:
            activities.add('nature')
            if tags.get('natural') in ['beach', 'coastline']:
                activities.add('beach')
                
        return list(activities)

    def _get_country_name(self, country_code):
        """Convert country code to English country name"""
        country_names = {
            'US': 'United States',
            'FR': 'France',
            'JP': 'Japan',
            'ES': 'Spain',
            'IT': 'Italy',
            'GB': 'United Kingdom',
            'DE': 'Germany',
            'AU': 'Australia',
            'CA': 'Canada',
            'TH': 'Thailand'
        }
        return country_names.get(country_code, country_code)

    def _get_location_details(self, lat, lon):
        """Get city and country information from coordinates"""
        try:
            location = self.geocoder.reverse((lat, lon))
            address = location.raw['address']
            return {
                'city': address.get('city') or address.get('town') or address.get('village'),
                'country': address.get('country'),
                'state': address.get('state'),
                'county': address.get('county')
            }
        except:
            return {'city': 'Unknown', 'country': 'Unknown'}

    def _generate_description(self, tags):
        """Generate a meaningful description from available tags"""
        description_parts = []
        
        if tags.get('description'):
            return tags['description']
            
        if tags.get('tourism'):
            description_parts.append(f"A {tags['tourism']} destination")
        if tags.get('historic'):
            description_parts.append(f"Historic {tags['historic']}")
        if tags.get('natural'):
            description_parts.append(f"Natural {tags['natural']} feature")
        if tags.get('leisure'):
            description_parts.append(f"Leisure destination for {tags['leisure']}")
            
        return ' '.join(description_parts) or "An interesting destination"

    def _determine_budget_category(self, tags):
        """Determine budget category based on amenities and location"""
        score = 0
        
        # Luxury indicators
        if any(tag in tags for tag in ['hotel:stars', 'tourism=resort']):
            score += 3
        if tags.get('fee') == 'yes':
            score += 1
            
        # Budget indicators
        if tags.get('fee') == 'no':
            score -= 1
        if tags.get('tourism') in ['camp_site', 'hostel']:
            score -= 2
            
        if score >= 2:
            return 'luxury'
        elif score >= 0:
            return 'moderate'
        return 'budget'

    def _extract_activities(self, tags):
        """Extract detailed activities from tags"""
        activities = set()
        
        # Map OSM tags to activity categories
        activity_mapping = {
            'tourism': {
                'museum': 'culture',
                'art_gallery': 'culture',
                'theme_park': 'entertainment',
                'zoo': 'nature',
                'viewpoint': 'sightseeing'
            },
            'historic': {
                'castle': 'culture',
                'ruins': 'culture',
                'monument': 'sightseeing'
            },
            'natural': {
                'beach': 'beach',
                'peak': 'hiking',
                'water': 'water_activities'
            },
            'leisure': {
                'park': 'nature',
                'garden': 'nature',
                'sports_centre': 'sports'
            },
            'sport': {
                'swimming': 'water_activities',
                'hiking': 'hiking',
                'skiing': 'winter_sports'
            }
        }
        
        # Process each category
        for category, mappings in activity_mapping.items():
            if category in tags:
                if tags[category] in mappings:
                    activities.add(mappings[tags[category]])
                else:
                    activities.add(tags[category])
        
        return ','.join(activities) if activities else 'sightseeing'