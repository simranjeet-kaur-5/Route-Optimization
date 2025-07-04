import requests
import time
from typing import Tuple, Optional

def get_lat_lon(location_name: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Get latitude and longitude for a location using OpenStreetMap's Nominatim service.
    
    Args:
        location_name (str): Name of the location to geocode
        
    Returns:
        Tuple[Optional[float], Optional[float]]: Tuple of (latitude, longitude) or (None, None) if not found
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': location_name,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'SmartRouteOptimizer/1.0'  # Identify our application
        }
        
        # Add delay to respect Nominatim's usage policy
        time.sleep(1)
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        
        data = response.json()
        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
        else:
            print(f"No coordinates found for location: {location_name}")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates for {location_name}: {str(e)}")
        return None, None
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error parsing coordinates for {location_name}: {str(e)}")
        return None, None
    except Exception as e:
        print(f"Unexpected error for {location_name}: {str(e)}")
        return None, None

# Example usage
location = "Times Square, New York"
lat, lon = get_lat_lon(location)
print(f"Latitude: {lat}, Longitude: {lon}")