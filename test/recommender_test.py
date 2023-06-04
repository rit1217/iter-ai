import unittest

from recommender import PlaceRecommender
from components.utils import *


class RecommenderTestCase(unittest.TestCase):
    
    def setUp(self):
        self.recommender = PlaceRecommender()

    def test_rec_attraction_1(self):
        # Test case for happy path of the function
        result = self.recommender.recommend_attraction(['Temple'], ['Sightseeing'], 'BANGKOK', 3)
        self.assertEqual([
                {
                    "place_id": "P03013485",
                    "place_name": "Utthayan Rd. (Aksa Rd.)",
                    "attraction_types": [
                        "Landmarks and Memorials"
                    ],
                    "category_code": "ATTRACTION",
                    "latitude": 13.77821234,
                    "longitude": 100.3563516,
                    "opening_hours": [
                        {
                            "day": "Sunday",
                            "opening_time": "06:00",
                            "closing_time": "18:00"
                        },
                        {
                            "day": "Monday",
                            "opening_time": "06:00",
                            "closing_time": "18:00"
                        },
                        {
                            "day": "Tuesday",
                            "opening_time": "06:00",
                            "closing_time": "18:00"
                        },
                        {
                            "day": "Wednesday",
                            "opening_time": "06:00",
                            "closing_time": "18:00"
                        },
                        {
                            "day": "Thursday",
                            "opening_time": "06:00",
                            "closing_time": "18:00"
                        },
                        {
                            "day": "Friday",
                            "opening_time": "06:00",
                            "closing_time": "18:00"
                        },
                        {
                            "day": "Saturday",
                            "opening_time": "06:00",
                            "closing_time": "18:00"
                        }
                    ]
                },
                {
                    "place_id": "P03025433",
                    "place_name": "Wat Phra Si Rattana Satsadaram or Wat Phra Kaeo",
                    "attraction_types": [
                        "Temple"
                    ],
                    "category_code": "ATTRACTION",
                    "latitude": 13.75118146,
                    "longitude": 100.49263026,
                    "opening_hours": [
                        {
                            "day": "Sunday",
                            "opening_time": "08:30",
                            "closing_time": "15:30"
                        },
                        {
                            "day": "Monday",
                            "opening_time": "08:30",
                            "closing_time": "15:30"
                        },
                        {
                            "day": "Tuesday",
                            "opening_time": "08:30",
                            "closing_time": "15:30"
                        },
                        {
                            "day": "Wednesday",
                            "opening_time": "08:30",
                            "closing_time": "15:30"
                        },
                        {
                            "day": "Thursday",
                            "opening_time": "08:30",
                            "closing_time": "15:30"
                        },
                        {
                            "day": "Friday",
                            "opening_time": "08:30",
                            "closing_time": "15:30"
                        },
                        {
                            "day": "Saturday",
                            "opening_time": "08:30",
                            "closing_time": "15:30"
                        }
                    ]
                },
                {
                    "place_id": "P03025468",
                    "place_name": "Fo Guang Shan Temple",
                    "attraction_types": [
                        "Temple"
                    ],
                    "category_code": "ATTRACTION",
                    "latitude": 13.85679,
                    "longitude": 100.67776391,
                    "opening_hours": [
                        {
                            "day": "Sunday",
                            "opening_time": "09:00",
                            "closing_time": "17:00"
                        },
                        {
                            "day": "Monday",
                            "opening_time": "10:00",
                            "closing_time": "16:00"
                        },
                        {
                            "day": "Tuesday",
                            "opening_time": "09:00",
                            "closing_time": "17:00"
                        },
                        {
                            "day": "Wednesday",
                            "opening_time": "09:00",
                            "closing_time": "17:00"
                        },
                        {
                            "day": "Thursday",
                            "opening_time": "09:00",
                            "closing_time": "17:00"
                        },
                        {
                            "day": "Friday",
                            "opening_time": "09:00",
                            "closing_time": "17:00"
                        },
                        {
                            "day": "Saturday",
                            "opening_time": "09:00",
                            "closing_time": "17:00"
                        }
                    ]
                }
            ], result)
        self.assertEqual(3, len(result))
    
    def test_rec_attraction_2(self):
        # Test case for both empty list
        with self.assertRaises(ValueError) as cm:
            self.recommender.recommend_attraction([], [], 'BANGKOK', 3)
        self.assertEqual(str(cm.exception), "Attraction types or activities should have atleast 1 value")

    def test_rec_attraction_3(self):
        # Test case for everyting is empty
        with self.assertRaises(ValueError) as cm:
            self.recommender.recommend_attraction([], [], '', 3)
        self.assertEqual(str(cm.exception), "Destination cannot be empty")

    def test_rec_attraction_4(self):
        # Test case when number of attraction is less than the required n
        result = self.recommender.recommend_attraction(['Temple'], [], 'KO TAO', 3)
        self.assertEqual([
                            {
                                "place_id": "P03007654",
                                "place_name": "Ko Tao",
                                "attraction_types": [
                                    "Islands"
                                ],
                                "category_code": "ATTRACTION",
                                "latitude": 10.09409385,
                                "longitude": 99.8388893,
                                "opening_hours": [
                                    {
                                        "day": "Sunday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Monday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Tuesday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Wednesday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Thursday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Friday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Saturday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    }
                                ]
                            },
                            {
                                "place_id": "P03008115",
                                "place_name": "Ko Nang Yuan",
                                "attraction_types": [
                                    "Islands"
                                ],
                                "category_code": "ATTRACTION",
                                "latitude": 10.11765392,
                                "longitude": 99.81552176,
                                "opening_hours": [
                                    {
                                        "day": "Sunday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Monday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Tuesday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Wednesday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Thursday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Friday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    },
                                    {
                                        "day": "Saturday",
                                        "opening_time": "unknown",
                                        "closing_time": "unknown"
                                    }
                                ]
                            }
                        ], 
                        result)
        self.assertEqual(2, len(result))

    def test_rec_restaurant_1(self):
        # Test case for happy path of the function
        result = self.recommender.recommend_restaurant(['Thai'], 'BANGKOK', 3)
        self.assertEqual(3, len(result))

    def test_rec_restaurant_2(self):
        # Test case for empty cuisine type
        with self.assertRaises(ValueError) as cm:
            self.recommender.recommend_restaurant([], 'BANGKOK', 3)
        self.assertEqual(str(cm.exception), "Cuisine types should have atleast 1 value")

    def test_rec_restaurant_3(self):
        # Test case for everyting is empty
        with self.assertRaises(ValueError) as cm:
            self.recommender.recommend_restaurant([], '', 3)
        self.assertEqual(str(cm.exception), "Destination cannot be empty")

    def test_rec_restaurant_4(self):
        # Test case when number of restaurant is less than the required n
        result = self.recommender.recommend_restaurant(['Thai'], 'AMNAT CHAROEN', 3)
        self.assertEqual([
        {
            "place_id": "P08013752",
            "place_name": "Kookwan Vietnam Restaurant",
            "cuisine_types": None,
            "category_code": "RESTAURANT",
            "latitude": 15.867062,
            "longitude": 104.634764,
            "opening_hours": [
                {
                    "day": "Sunday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Monday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Tuesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Wednesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Thursday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Friday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Saturday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                }
            ]
        },
        {
            "place_id": "P08013754",
            "place_name": "Pan Din Thong Farm Fishing Park Restaurant",
            "cuisine_types": None,
            "category_code": "RESTAURANT",
            "latitude": 15.835013,
            "longitude": 104.606991,
            "opening_hours": [
                {
                    "day": "Sunday",
                    "opening_time": "09:00",
                    "closing_time": "21:00"
                },
                {
                    "day": "Monday",
                    "opening_time": "09:00",
                    "closing_time": "21:00"
                },
                {
                    "day": "Tuesday",
                    "opening_time": "09:00",
                    "closing_time": "21:00"
                },
                {
                    "day": "Wednesday",
                    "opening_time": "09:00",
                    "closing_time": "21:00"
                },
                {
                    "day": "Thursday",
                    "opening_time": "09:00",
                    "closing_time": "21:00"
                },
                {
                    "day": "Friday",
                    "opening_time": "09:00",
                    "closing_time": "21:00"
                },
                {
                    "day": "Saturday",
                    "opening_time": "09:00",
                    "closing_time": "21:00"
                }
            ]
        }
    ], result)
        self.assertEqual(2, len(result))

    def test_rec_restaurant_5(self):
        # Test case when there is enough restaurant but lots of cuisine type is missing
        result = self.recommender.recommend_restaurant(['Thai'], 'RAYONG', 5)
        self.assertEqual([
        {
            "place_id": "P08001727",
            "place_name": "Phat Thai Khun Krai",
            "cuisine_types": [],
            "category_code": "RESTAURANT",
            "latitude": 12.64123,
            "longitude": 101.5033,
            "opening_hours": [
                {
                    "day": "Sunday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Monday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Tuesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Wednesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Thursday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Friday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Saturday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                }
            ]
        },
        {
            "place_id": "P08002570",
            "place_name": "Sawoei 2 Restaurant",
            "cuisine_types": [],
            "category_code": "RESTAURANT",
            "latitude": 12.633136,
            "longitude": 101.481185,
            "opening_hours": [
                {
                    "day": "Sunday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Monday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Tuesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Wednesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Thursday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Friday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Saturday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                }
            ]
        },
        {
            "place_id": "P08003002",
            "place_name": "Bakery House",
            "cuisine_types": [],
            "category_code": "RESTAURANT",
            "latitude": 12.639085,
            "longitude": 101.514944,
            "opening_hours": [
                {
                    "day": "Sunday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Monday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Tuesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Wednesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Thursday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Friday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Saturday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                }
            ]
        },
        {
            "place_id": "P08004630",
            "place_name": "Ban Malako Fish Noodle",
            "cuisine_types": [],
            "category_code": "RESTAURANT",
            "latitude": 12.63799,
            "longitude": 101.499358,
            "opening_hours": [
                {
                    "day": "Sunday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Monday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Tuesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Wednesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Thursday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Friday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Saturday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                }
            ]
        },
        {
            "place_id": "P08007455",
            "place_name": "Mae Lamyong Restaurant",
            "cuisine_types": [],
            "category_code": "RESTAURANT",
            "latitude": 12.633148,
            "longitude": 101.480677,
            "opening_hours": [
                {
                    "day": "Sunday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Monday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Tuesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Wednesday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Thursday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Friday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                },
                {
                    "day": "Saturday",
                    "opening_time": "unknown",
                    "closing_time": "unknown"
                }
            ]
        }
    ], result)
        self.assertEqual(5, len(result))