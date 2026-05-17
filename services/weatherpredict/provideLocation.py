from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="my_geo_app")

def get_location(city_name):
    location = geolocator.geocode(city_name)
    if location:
        return {
            "city": city_name,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "address": location.address
        }
    else:
        return None
