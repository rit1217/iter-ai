import flask
from datetime import datetime, date
import json
import time as t
import requests

from vrp import ItineraryGenerator
from components.place import Place
from components.constants import *
from components.utils import *

app = flask.Flask(__name__) 

'''
[
{'day': 'Monday',
'opening_time': '6:00',
'closing_time:' '19:00'},
{'day': 'Tuesday',
'opening_time': 'unknown',
'closing_time:' 'unknown'},
...

]
'''
'''
{
'Monday': {
    'opening_time': '6:00',
    'closing_time': '19:00',
    }
    ...
}
'''

def get_token():
    '''
    Helper function to get token to make requests
    '''
    try:
        # Define the login endpoint URL and payload
        url = "http://dev.se.kmitl.ac.th:1337/api/user/login/"
        # url = "https://localhost:1337/api/user/login/"
        payload = {"email": "admin@iter.com", "password": "admin"}

        session = requests.Session()

        session.trust_env = False

        # Send the POST request to the login endpoint
        response = session.post(url, json=payload)

        # If the request was successful, extract the access token from the response and store it in a variable
        if response.status_code == 200:
            token = response.json().get("token").get("access")
            return token
        else:
            # If the request failed, print an error message and return None
            print(f"Error: {response.status_code} - {response.reason}")
            return None

    except Exception as e:
        print(f"An error occurred while trying to get the token: {e}")
        return None

@app.route('/api/generateitinerary/', methods = ['POST'])
def api_generateitinerary():
    start = t.time()
    req_body = flask.request.get_json()
    places = []
    start_time = str_to_time(req_body['start_time'])
    end_time = str_to_time(req_body['end_time'])
    for place in req_body['places']:
        opening_time = {}
        closing_time = {}
        for i in place['opening_hour']:
            opening_time[i['day'].lower()] = str_to_time(i['opening_time']) if i['opening_time'] != 'unknown' else start_time
            closing_time[i['day'].lower()] = str_to_time(i['closing_time']) if i['opening_time'] != 'unknown' else end_time
        types = None
        if place['category_code'] == "ATTRACTION":
            types = place['attraction_types']
        elif place['category_code'] == "RESTAURANT":
            types = place['cuisine_types']

        places.append(
            Place(place['place_id'], place['place_name'], place['category_code'], place['latitude'], place['longitude'],
                 opening_time, closing_time, types)
        )

    itinerary = ItineraryGenerator().generate_itinerary(places, req_body['destination'], 
                    datetime.strptime(req_body['start_date'], DATE_FORMAT),
                    req_body['num_day'], 
                    start_time, end_time,
                    cat_service_time=req_body['service_time'])
    print(itinerary)
    itinerary = itinerary.to_dict()
    itinerary['co_travelers'] = req_body['co_travelers']
    itinerary['owner'] = req_body['owner']
    print(json.dumps(itinerary, indent=2))
    print("ELAPSED TIME:", t.time() - start)

    return json.dumps(itinerary)


@app.route('/api/recommenditinerary/', methods = ['POST'])
def api_recommenditinerary():
    start = t.time()
    req_body = flask.request.get_json()
    print(req_body)
    start_time = str_to_time(req_body['start_time'])
    end_time = str_to_time(req_body['end_time'])
    
    start_date = datetime.strptime(req_body['start_date'], DATE_FORMAT)
    end_date = datetime.strptime(req_body['end_date'], DATE_FORMAT)
    num_day = (end_date - start_date).days

    day_duration = (datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)).seconds
    day_duration = day_duration//60         #as minutes
    n_places = num_day * 7

    if req_body['tripType'].lower() == 'fast':
        service_time = FAST_PACE_SERVICE_TIME
    elif req_body['tripType'].lower() == 'medium':
        service_time = MEDIUM_PACE_SERVICE_TIME
    else:
        service_time = SLOW_PACE_SERVICE_TIME

    if start_date.replace(hour=(int(MEAL_TIME['DINNER'][0][:2])+service_time['RESTAURANT'])//60,
                          minute=(int(MEAL_TIME['DINNER'][0][3:5])+service_time['RESTAURANT'])%60) \
     <= start_date.replace(hour=end_time.hour, minute=end_time.minute):
        n_restaurants = num_day  * 2 #restaurants
    else:
        n_restaurants = num_day

    
    n_shops = num_day // 2 #estimated by assumption of shopping every other day
    
    n_attractions = n_places - n_restaurants - n_shops

    #recommend attraction
    # URL     = "0.0.0.0:3100/api/recommendplace"
    # data = {
    #     'features': req_body['targetTypes'],
    #     'top_n': n_attractions
    # }
    # attractions = requests.get(URL, json=data).json()
    # places.extend(attractions['recommended_places'])

    #TODO
    #recommend restaurant

    #TODO
    #recommend shop
    places_dict = [
        {
            "place_id": "1",
            "place_name": "Prestige Suites Nana",
            "category_code": "ACCOMMODATION",
            "latitude": 13.74370239,
            "longitude": 100.5534596,
            "opening_hour": [{
                "day": "Monday",
                "opening_time": "8:00:00",
                "closing_time": "19:00:00"
            },{
                "day": "Tuesday",
                "opening_time": "8:00:00",
                "closing_time": "19:00:00"
            },{
                "day": "Wednesday",
                "opening_time": "8:00:00",
                "closing_time": "19:00:00"
            },{
                "day": "Thursday",
                "opening_time": "8:00:00",
                "closing_time": "19:00:00"
            },{
                "day": "Friday",
                "opening_time": "8:00:00",
                "closing_time": "19:00:00"
            },{
                "day": "Saturday",
                "opening_time": "8:00:00",
                "closing_time": "19:00:00"
            },{
                "day": "Sunday",
                "opening_time": "8:00:00",
                "closing_time": "19:00:00"
            }
             ]
        },
        {
            "place_id": "2",
            "place_name": "Benchasiri Park",
            "category_code": "ATTRACTION",
            "latitude": 13.73098757,
            "longitude": 100.56755441,
            "attraction_types": ["Parks & Gardens"],
            "opening_hour": [{
                "day": "Monday",
                "opening_time": "15:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Tuesday",
                "opening_time": "15:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Wednesday",
                "opening_time": "15:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Thursday",
                "opening_time": "15:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Friday",
                "opening_time": "15:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Saturday",
                "opening_time": "15:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Sunday",
                "opening_time": "15:00:00",
                "closing_time": "20:00:00"
            }
             ]
            
        },
        {
            "place_id": "3",
            "place_name": "Malai Restaurant",
            "category_code": "RESTAURANT",
            "latitude": 13.722022,
            "longitude": 100.546,
            "cuisine_types": ["Thai"],
            "opening_hour": [{
                "day": "Monday",
                "opening_time": "11:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Tuesday",
                "opening_time": "11:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Wednesday",
                "opening_time": "11:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Thursday",
                "opening_time": "11:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Friday",
                "opening_time": "11:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Saturday",
                "opening_time": "11:00:00",
                "closing_time": "20:00:00"
            },{
                "day": "Sunday",
                "opening_time": "11:00:00",
                "closing_time": "20:00:00"
            }
             ]
            
        },
        {
            "place_id": "4",
            "place_name": "Siriraj Phimukhsthan",
            "category_code": "ATTRACTION",
            "latitude": 13.75972996,
            "longitude": 100.4868832,
            "attraction_types": ["Educational museums"],
            "opening_hour": [{
                "day": "Monday",
                "opening_time": "10:00:00",
            "closing_time": "19:00:00"
            },{
                "day": "Tuesday",
                "opening_time": "10:00:00",
            "closing_time": "19:00:00"
            },{
                "day": "Wednesday",
                "opening_time": "10:00:00",
            "closing_time": "19:00:00"
            },{
                "day": "Thursday",
                "opening_time": "10:00:00",
            "closing_time": "19:00:00"
            },{
                "day": "Friday",
                "opening_time": "10:00:00",
            "closing_time": "19:00:00"
            },{
                "day": "Saturday",
                "opening_time": "10:00:00",
            "closing_time": "19:00:00"
            },{
                "day": "Sunday",
                "opening_time": "10:00:00",
            "closing_time": "19:00:00"
            }
             ]
            
        },
        {
            "place_id": "5",
            "place_name": "Mini Murrah Farm",
            "category_code": "ATTRACTION",
            "latitude": 13.76379474,
            "longitude": 100.4967129,
            "attraction_types": [],
            "opening_hour": [{
                "day": "Monday",
                "opening_time": "09:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Tuesday",
                "opening_time": "09:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Wednesday",
                "opening_time": "09:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Thursday",
                "opening_time": "09:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Friday",
                "opening_time": "09:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Saturday",
                "opening_time": "09:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Sunday",
                "opening_time": "09:00:00",
            "closing_time": "18:00:00"
            }
             ]
            
        },
        {
            "place_id": "6",
            "place_name": "Wat Ratchabophit Sathitmahasimaram",
            "category_code": "ATTRACTION",
            "latitude": 13.74913215,
            "longitude": 100.49734105,
            "attraction_types": ["Temple"],
            "opening_hour": [{
                "day": "Monday",
                "opening_time": "09:00:00",
            "closing_time": "16:30:00"
            },{
                "day": "Tuesday",
                "opening_time": "09:00:00",
            "closing_time": "16:30:00"
            },{
                "day": "Wednesday",
                "opening_time": "09:00:00",
            "closing_time": "16:30:00"
            },{
                "day": "Thursday",
                "opening_time": "09:00:00",
            "closing_time": "16:30:00"
            },{
                "day": "Friday",
                "opening_time": "09:00:00",
            "closing_time": "16:30:00"
            },{
                "day": "Saturday",
                "opening_time": "09:00:00",
            "closing_time": "16:30:00"
            },{
                "day": "Sunday",
                "opening_time": "09:00:00",
            "closing_time": "16:30:00"
            }
             ]
            
        },
        {
            "place_id": "7",
            "place_name": "The Royal Thai Army Museum",
            "category_code": "ATTRACTION",
            "latitude": 13.761652,
            "longitude": 100.508082,
            "attraction_types": ["Landmarks and Memorials"],
            "opening_hour": [{
                "day": "Monday",
                "opening_time": "08:30:00",
            "closing_time": "19:00:00"
            },{
                "day": "Tuesday",
               "opening_time": "08:30:00",
            "closing_time": "19:00:00"
            },{
                "day": "Wednesday",
                "opening_time": "08:30:00",
            "closing_time": "19:00:00"
            },{
                "day": "Thursday",
                "opening_time": "08:30:00",
            "closing_time": "19:00:00"
            },{
                "day": "Friday",
               "opening_time": "08:30:00",
            "closing_time": "19:00:00"
            },{
                "day": "Saturday",
                "opening_time": "08:30:00",
            "closing_time": "19:00:00"
            },{
                "day": "Sunday",
                "opening_time": "08:30:00",
            "closing_time": "19:00:00"
            }
             ]
            
        },
        {
            "place_id": "8",
            "place_name": "R-Haan",
            "category_code": "RESTAURANT",
            "latitude": 13.73189108,
            "longitude": 100.5795599,
            "cuisine_types": ["Thai"],

            "opening_hour": [{
                "day": "Monday",
                "opening_time": "12:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Tuesday",
                "opening_time": "12:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Wednesday",
                "opening_time": "12:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Thursday",
                "opening_time": "12:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Friday",
                "opening_time": "12:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Saturday",
                "opening_time": "12:00:00",
            "closing_time": "18:00:00"
            },{
                "day": "Sunday",
                "opening_time": "12:00:00",
            "closing_time": "18:00:00"
            }
             ]
            
        },
        {
            "place_id": "9",
            "place_name": "Chulalongkorn University Museum of Natural History",
            "category_code": "ATTRACTION",
            "latitude": 13.7374931,
            "longitude": 100.53021883,
            "attraction_types": ["Museums", "Educational museums"],
            "opening_hour": [{
                "day": "Monday",
                "opening_time": "10:00:00",
            "closing_time": "15:20:00"
            },{
                "day": "Tuesday",
                "opening_time": "10:00:00",
            "closing_time": "15:20:00"
            },{
                "day": "Wednesday",
                "opening_time": "10:00:00",
            "closing_time": "15:20:00"
            },{
                "day": "Thursday",
                "opening_time": "10:00:00",
            "closing_time": "15:20:00"
            },{
                "day": "Friday",
               "opening_time": "10:00:00",
            "closing_time": "15:20:00"
            },{
                "day": "Saturday",
                "opening_time": "10:00:00",
            "closing_time": "15:20:00"
            },{
                "day": "Sunday",
                "opening_time": "10:00:00",
            "closing_time": "15:20:00"
            }
             ]
        },
        {
            "place_id": "10",
            "place_name": "JIM THOMPSON",
            "category_code": "SHOP",
            "latitude": 13.730429,
            "longitude": 100.533504,
            "opening_hour": [{
                "day": "Monday",
                "opening_time": "9:00:00",
            "closing_time": "22:00:00"
            },{
                "day": "Tuesday",
                "opening_time": "9:00:00",
            "closing_time": "22:00:00"
            },{
                "day": "Wednesday",
                "opening_time": "9:00:00",
            "closing_time": "22:00:00"
            },{
                "day": "Thursday",
                "opening_time": "9:00:00",
            "closing_time": "22:00:00"
            },{
                "day": "Friday",
                "opening_time": "9:00:00",
            "closing_time": "22:00:00"
            },{
                "day": "Saturday",
                "opening_time": "9:00:00",
            "closing_time": "22:00:00"
            },{
                "day": "Sunday",
                "opening_time": "9:00:00",
            "closing_time": "22:00:00"
            }
             ]
        }
    ]
    
    places = []
    for place in places_dict:
        opening_time = {}
        closing_time = {}
        for i in place['opening_hour']:
            opening_time[i['day'].lower()] = str_to_time(i['opening_time']) if i['opening_time'] != 'unknown' else start_time
            closing_time[i['day'].lower()] = str_to_time(i['closing_time']) if i['opening_time'] != 'unknown' else end_time
        types = None
        if place['category_code'] == "ATTRACTION":
            types = place['attraction_types']
        elif place['category_code'] == "RESTAURANT":
            types = place['cuisine_types']

        places.append(
            Place(place['place_id'], place['place_name'], place['category_code'], place['latitude'], place['longitude'],
                 opening_time, closing_time, types)
        )

    itinerary = ItineraryGenerator().generate_itinerary(places, req_body['destination'], 
                    start_date,
                    num_day, 
                    str_to_time(req_body['start_time']), str_to_time(req_body['end_time']),
                    cat_service_time=service_time)
    print(itinerary)
    itinerary = itinerary.to_dict()
    itinerary['co_travelers'] = req_body['co_travelers']
    itinerary['owner'] = req_body['owner']
    print(json.dumps(itinerary, indent=2))
    print("ELAPSED TIME:", t.time() - start)

    itinerary_json = json.dumps(itinerary)
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }
    resp = requests.post('http://dev.se.kmitl.ac.th:1337/api/itinerary/', headers=headers, json=itinerary_json)
    print(resp)
    return itinerary_json

