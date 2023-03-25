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
    print(req_body)
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
    # itinerary.start_date = itinerary.start_date.strftime(DATE_FORMAT)
    # itinerary.end_date = itinerary.end_date.strftime(DATE_FORMAT)
    # itinerary.start_time= itinerary.start_time.strftime(DATETIME_FORMAT)
    # itinerary.end_time = itinerary.end_time.strftime(DATETIME_FORMAT)

    return json.dumps(itinerary.to_dict())