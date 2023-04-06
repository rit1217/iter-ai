import flask
from datetime import datetime
import json

from vrp import ItineraryGenerator
from components.place import Place
from components.constants import *
from components.utils import *

app = flask.Flask(__name__) 



@app.route('/api/generateitinerary/', methods = ['POST'])
def api_generateitinerary():
    req_body = flask.request.get_json()
    places = []
    for place in req_body['places']:
        places.append(
            Place(place['place_id'], place['place_name'], place['category_code'], place['latitude'], place['longitude'],
                 str_to_time(place['opening_time']), str_to_time(place['closing_time']))
        )

    itinerary = ItineraryGenerator().generate_itinerary(places, req_body['destination'], 
                    datetime.strptime(req_body['start_date'], DATE_FORMAT),
                    req_body['num_day'], 
                    str_to_time(req_body['start_time']), str_to_time(req_body['end_time']),
                    cat_service_time=req_body['service_time'])
    print(itinerary)
    itinerary = itinerary.to_dict()
    itinerary['co_travelers'] = req_body['co_travelers']
    itinerary['owner'] = req_body['owner']

    return json.dumps(itinerary)
