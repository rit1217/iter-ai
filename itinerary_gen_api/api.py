import flask
from datetime import datetime, date
import json
import time as t
import requests

from vrp import ItineraryGenerator
from components.place import Place
from components.constants import *
from components.utils import *
from .config import *

app = flask.Flask(__name__) 


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
    num_day = ((end_date - start_date).days) + 1

    day_duration = (datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)).seconds
    day_duration = day_duration//60 #as minutes
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
        n_restaurants = num_day  * 2
    else:
        n_restaurants = num_day

    n_attractions = n_places - n_restaurants
    places_dict = []

    # recommend attraction
    URL     = RECOMMENDER_API_URL + "/api/recommendattraction"
    data = {
        'features': req_body['targetTypes'],
        'activities': req_body['preferredActivities'],
        'destination': req_body['destination'].upper(),
        'top_n': n_attractions
    }
    attractions = requests.post(URL, json=data).json()['recommended_attractions']
    places_dict.extend(attractions)

    #recommend restaurant
    URL     = RECOMMENDER_API_URL + "/api/recommendrestaurant"
    data = {
        'cuisines': req_body['preferredCuisine'],
        'destination': req_body['destination'].upper(),
        'top_n': n_restaurants
    }
    restaurants = requests.post(URL, json=data).json()['recommended_restaurants']
    places_dict.extend(restaurants)

    #recommend accommodation
    URL     = RECOMMENDER_API_URL + "/api/recommendaccommodation"
    data = {
        'places': places_dict
    }
    accommodation = requests.post(URL, json=data).json()['recommended_accommodation']
    places_dict.insert(0, accommodation)
    places = []
    for place in places_dict:
        opening_time = {}
        closing_time = {}
        for i in place['opening_hours']:
            if place['category_code'] == 'ACCOMMODATION':
                opening_time[i['day'].lower()] = start_time
                closing_time[i['day'].lower()] = end_time
            else:
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

    return itinerary_json

