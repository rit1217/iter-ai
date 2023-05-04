import flask
from datetime import datetime
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
    places = []
    start_date = datetime.strptime(req_body['start_date'], DATE_FORMAT)
    end_date = datetime.strptime(req_body['end_date'], DATE_FORMAT)
    num_day = (end_date - start_date).days

    
    start_time = str_to_time(req_body['start_time'])
    end_time = str_to_time(req_body['end_time'])
    day_duration = (end_time - start_time).seconds
    day_duration = day_duration//60         #as minutes
    n_places = num_day * 7

    if req_body['tripType'].lower() == 'fast':
        service_time = FAST_PACE_SERVICE_TIME
    elif req_body['tripType'].lower() == 'medium':
        service_time = MEDIUM_PACE_SERVICE_TIME
    else:
        service_time = SLOW_PACE_SERVICE_TIME

    if start_date.replace(hour=int(MEAL_TIME['DINNER'][0][:2])+service_time['RESTAURANT']%60,
                          minute=int(MEAL_TIME['DINNER'][0][3:5])+service_time['RESTAURANT']//60) \
     <= start_date.replace(hour=end_time.hour, minute=end_time.minute):
        n_restaurants = num_day  * 2 #restaurants
    else:
        n_restaurants = num_day


    n_shops = num_day // 2 #estimated by assumption of shopping every other day
    
    n_attractions = n_places - n_restaurants - n_shops

    #recommend attraction
    URL     = "0.0.0.0:3100/api/recommendplace"
    data = {
        'features': req_body['targetTypes'],
        'top_n': n_attractions
    }
    attractions = requests.get(URL, json=data).json()
    places.extend(attractions['recommended_places'])

    #TODO
    #recommend restaurant

    #TODO
    #recommend shop

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

    return json.dumps(itinerary)

