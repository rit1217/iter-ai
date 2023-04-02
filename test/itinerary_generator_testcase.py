import unittest

from vrp import ItineraryGenerator
from components.place import Place
from components.constants import *
from components.utils import *


class ItineraryGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.places_dict = [
            {
            "place_id": 1,
            "place_name": "Prestige Suites Nana",
            "category_code": "ACCOMMODATION",
            "latitude": 13.74370239,
            "longitude": 100.5534596,
            "opening_time": "8:00:00",
            "closing_time": "19:00:00"
        },
        {
            "place_id": 2,
            "place_name": "Benchasiri Park",
            "category_code": "ATTRACTION",
            "latitude": 13.73098757,
            "longitude": 100.56755441,
            "opening_time": "15:00:00",
            "closing_time": "20:00:00"
        },
        {
            "place_id": 3,
            "place_name": "Malai Restaurant",
            "category_code": "RESTAURANT",
            "latitude": 13.722022,
            "longitude": 100.546,
            "opening_time": "11:00:00",
            "closing_time": "20:00:00"
        },
        {
            "place_id": 4,
            "place_name": "Siriraj Phimukhsthan",
            "category_code": "ATTRACTION",
            "latitude": 13.75972996,
            "longitude": 100.4868832,
            "opening_time": "10:00:00",
            "closing_time": "19:00:00"
        },
        {
            "place_id": 5,
            "place_name": "Mini Murrah Farm",
            "category_code": "ATTRACTION",
            "latitude": 13.76379474,
            "longitude": 100.4967129,
            "opening_time": "09:00:00",
            "closing_time": "18:00:00"
        },
        {
            "place_id": 6,
            "place_name": "Wat Ratchabophit Sathitmahasimaram",
            "category_code": "ATTRACTION",
            "latitude": 13.74913215,
            "longitude": 100.49734105,
            "opening_time": "09:00:00",
            "closing_time": "16:30:00"
        },
        {
            "place_id": 7,
            "place_name": "The Royal Thai Army Museum",
            "category_code": "ATTRACTION",
            "latitude": 13.761652,
            "longitude": 100.508082,
            "opening_time": "08:30:00",
            "closing_time": "19:00:00"
        },
        {
            "place_id": 8,
            "place_name": "R-Haan",
            "category_code": "RESTAURANT",
            "latitude": 13.73189108,
            "longitude": 100.5795599,
            "opening_time": "12:00:00",
            "closing_time": "18:00:00"
        },
        {
            "place_id": 9,
            "place_name": "Chulalongkorn University Museum of Natural History",
            "category_code": "ATTRACTION",
            "latitude": 13.7374931,
            "longitude": 100.53021883,
            "opening_time": "10:00:00",
            "closing_time": "15:20:00"
        },
        {
            "place_id": 10,
            "place_name": "JIM THOMPSON",
            "category_code": "SHOP",
            "latitude": 13.730429,
            "longitude": 100.533504,
            "opening_time": "9:00:00",
            "closing_time": "22:00:00"
        }
        ]
        self.places = []
        for place in self.places_dict:
            self.places.append(
                Place(place['place_id'], place['place_name'], place['category_code'], place['latitude'], place['longitude'],
                    str_to_time(place['opening_time']), str_to_time(place['closing_time']))
            )

    def test_limit_num_day(self):
        num_day = 2
        itinerary = ItineraryGenerator().generate_itinerary(self.places, "Bangkok", 
                    datetime.strptime("2023-7-11", DATE_FORMAT),
                    num_day, 
                    str_to_time("08:00:00"), str_to_time("19:00:00"))
        self.assertLessEqual( len(itinerary), num_day )
        # ensure visit all places
        unvisited = [p.place_id for p in self.places]
        for day_plan in itinerary.plan:
            for agenda in day_plan:
                self.assertIn(agenda.place.place_id, unvisited)
                if agenda.place.category != 'ACCOMMODATION':
                    unvisited.remove(agenda.place.place_id)
        

    def test_not_enough_day(self):
        num_day = 1
        itinerary = ItineraryGenerator().generate_itinerary(self.places, "Bangkok", 
                    datetime.strptime("2023-7-11", DATE_FORMAT),
                    num_day, 
                    str_to_time("08:00:00"), str_to_time("19:00:00"))
        self.assertIsNone( itinerary )