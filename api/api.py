import flask
from datetime import datetime, date, time
import json

from vrp import ItineraryGenerator
from components.place import Place
from components.constants import *


app = flask.Flask(__name__) 


def str_to_datetime(instr):
    return datetime.strptime(instr, DATETIME_FORMAT)

def str_to_time(instr):
        dt = datetime.strptime(instr, TIME_FORMAT)
        return time(dt.hour, dt.minute, dt.second)


@app.route('/api/generateitinerary/', methods = ['POST'])
def api_autocomplete():
    req_body = flask.request.get_json()
    # print(req_body)
    places = []
    for place in req_body['places']:
        places.append(
            Place(place['place_id'], place['place_name'], place['category_code'], place['latitude'], place['longitude'],
                 str_to_time(place['opening_time']), str_to_time(place['closing_time']))
        )

    itinerary = ItineraryGenerator().generate_itinerary(places, req_body['destination'], 
                    datetime.strptime(req_body['start_date'], DATE_FORMAT),
                    req_body['num_day'], 
                    str_to_time(req_body['start_time']), str_to_time(req_body['end_time']))
    print(itinerary)
    itinerary = itinerary.to_dict()
    itinerary['co_travelers'] = req_body['co_travelers']
    itinerary['owner'] = req_body['owner']

    return json.dumps(itinerary)
