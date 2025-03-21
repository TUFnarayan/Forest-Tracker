
def calculate_area(location):
    """Calculate approximate area based on location name"""
    location = location.lower()
    if 'forest' in location:
        return np.random.uniform(50000, 100000)
    elif any(x in location for x in ['city', 'town', 'urban']):
        return np.random.uniform(5000, 20000)
    else:
        return np.random.uniform(20000, 50000)


import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def get_predefined_locations():
    """
    Return a dictionary of predefined locations with their coordinates
    """
    return {
        # Major Indian Cities
        "noida": (28.5355, 77.3910),
        "delhi": (28.6139, 77.2090),
        "mumbai": (19.0760, 72.8777),
        "bangalore": (12.9716, 77.5946),
        "greater noida": (28.4744, 77.5040),
        "ghaziabad": (28.6692, 77.4538),
        "gurugram": (28.4595, 77.0266),
        "pondicherry": (11.9416, 79.8083),

        # Indian Forests and National Parks
        "jim corbett national park": (29.5300, 78.7747),
        "sundarbans": (21.9497, 89.1833),
        "western ghats": (13.2969, 75.2479),
        "kaziranga national park": (26.5880, 93.1700),
        "ranthambore national park": (26.0173, 76.5026),
        "bandipur national park": (11.6717, 76.6340),
        "gir forest": (21.1200, 70.8200),

        # Global Forests
        "amazon rainforest": (-3.4653, -62.2159),
        "borneo rainforest": (0.9619, 114.5548),
        "congo rainforest": (-0.7264, 21.7279),
        "daintree rainforest": (-16.2500, 145.4167),
        "tongass national forest": (57.5051, -133.5001)
    }

def get_location_suggestions(query: str) -> list:
    """
    Get location suggestions based on user input
    """
    locations = get_predefined_locations()
    query = query.lower()

    # Direct match first
    direct_matches = [loc.title() for loc in locations.keys() if query == loc.lower()]
    if direct_matches:
        return direct_matches

    # Then partial matches
    return [loc.title() for loc in locations.keys() if query in loc.lower()]

def generate_deforestation_data(location: str, start_year: int = 2000) -> pd.DataFrame:
    """
    Generate mock deforestation data for demonstration purposes
    """
    # Generate yearly data from start_year to current year
    current_year = datetime.now().year
    years = list(range(start_year, current_year + 1))

    # Generate synthetic forest cover data with realistic patterns
    np.random.seed(hash(location) % 100)  # Consistent data for same location
    
    # Different initial covers based on location type
    location_lower = location.lower()
    if "rainforest" in location_lower:
        initial_forest_cover = np.random.uniform(85, 95)
    elif "national park" in location_lower:
        initial_forest_cover = np.random.uniform(75, 85)
    elif any(city in location_lower for city in ["noida", "delhi", "gurgaon", "ghaziabad", "greater noida"]):
        initial_forest_cover = np.random.uniform(10, 20)  # Urban areas have much lower forest cover
    else:
        initial_forest_cover = np.random.uniform(30, 45)

    forest_cover = []
    deforestation_rate = []
    
    # Generate seasonal and yearly patterns
    for i in range(len(years)):
        # Base decline rate varies by location
        base_decline = np.random.uniform(0.2, 0.8)
        
        # Add cyclical patterns
        seasonal = 0.2 * np.sin(i * 2 * np.pi / 5)  # 5-year cycles
        policy_impact = 0.3 * np.sin(i * 2 * np.pi / 10)  # 10-year policy cycles
        
        # Calculate year's decline with various factors
        decline = max(0, base_decline + seasonal + policy_impact)
        
        if i == 0:
            forest_cover.append(initial_forest_cover)
        else:
            # Add some recovery possibility
            recovery = np.random.random() < 0.2  # 20% chance of slight recovery
            if recovery:
                change = np.random.uniform(0, decline/2)  # Partial recovery
            else:
                change = -decline
            
            new_cover = forest_cover[-1] + change
            forest_cover.append(max(0, min(100, new_cover)))  # Keep within bounds
        
        deforestation_rate.append(abs(decline))

    data = {
        'year': years,
        'forest_cover_percentage': forest_cover,
        'deforestation_rate': deforestation_rate,
        'total_area': [calculate_area(location)] * len(years),  # Dynamic area based on location
        'location': [location] * len(years)
    }

    return pd.DataFrame(data)

def get_location_coordinates(location: str) -> tuple:
    """
    Get coordinates for a location, using predefined coordinates for known locations
    """
    locations = get_predefined_locations()
    location_key = location.lower()

    if location_key in locations:
        return locations[location_key]

    # For unknown locations, use their input name but generate consistent coordinates
    # This ensures same location gets same coordinates every time
    np.random.seed(hash(location) % 100)
    lat = np.random.uniform(-60, 60)  # Wider range for global coverage
    lon = np.random.uniform(-180, 180)
    return (lat, lon)