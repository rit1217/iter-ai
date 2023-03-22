import flask
from datetime import datetime
import json

from vrp import ItineraryGenerator
from components.place import Place
from components.constants import *


app = flask.Flask(__name__) 


def str_to_datetime(instr):
    return datetime.strptime(instr, DATETIME_FORMAT)

def str_to_date(instr):
    return datetime.strptime(instr, DATE_FORMAT)


@app.route('/api/generateitinerary/', methods = ['POST'])
def api_autocomplete():
    req_body = flask.request.get_json()
    print(req_body)
    places = []
    for place in req_body['places']:
        places.append(
            Place(place['place_id'], place['place_name'], place['category_code'], place['latitude'], place['longitude'],
                 str_to_datetime(place['opening_time']), str_to_datetime(place['closing_time']))
        )

    itinerary = ItineraryGenerator().generate_itinerary(places, req_body['destination'], 
                    str_to_date(req_body['start_date']), req_body['num_day'], 
                    str_to_datetime(req_body['start_time']), str_to_datetime(req_body['end_time']))
    # itinerary.start_date = itinerary.start_date.strftime(DATE_FORMAT)
    # itinerary.end_date = itinerary.end_date.strftime(DATE_FORMAT)
    # itinerary.start_time= itinerary.start_time.strftime(DATETIME_FORMAT)
    # itinerary.end_time = itinerary.end_time.strftime(DATETIME_FORMAT)

    return json.dumps(itinerary.to_dict())
