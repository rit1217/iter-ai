import flask
from datetime import datetime
import json

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
    req_body = flask.request.get_json()
    places = []
    for place in req_body['places']:
        opening_time = {}
        closing_time = {}
        for i in place['opening_hour']:
            opening_time[i['day'].lower()] = str_to_time(i['opening_time'])
            closing_time[i['day'].lower()] = str_to_time(i['closing_time'])

        places.append(
            Place(place['place_id'], place['place_name'], place['category_code'], place['latitude'], place['longitude'],
                 opening_time, closing_time)
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
    print(json.dumps(itinerary))

    return json.dumps(itinerary)
