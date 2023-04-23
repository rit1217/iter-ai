from .constants import *


class Place:

    def __init__(self, place_id, place_name, category, lat, lng, open_time, close_time, types=None):
        self.place_id = place_id
        self.place_name = place_name
        self.category = category
        self.latitude = lat
        self.longitude = lng
        self.opening_time = open_time
        self.closing_time = close_time
        self.types = types

    def __str__(self):
        return self.place_name
    
    def to_dict(self):
        return {
            'place_id': self.place_id,
            'place_name': self.place_name, 
            'category': self.category,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'types': self.types,
            'opening_time': self.opening_time.strftime(TIME_FORMAT),
            'closing_time': self.closing_time.strftime(TIME_FORMAT)
        }
        