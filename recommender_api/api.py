import flask
from flask_cors import CORS
import json

from components.utils import *
from recommender import PlaceRecommender


app = flask.Flask(__name__) 
CORS(app)

@app.route('/api/recommendattraction/', methods = ['POST'])
def api_recommendplace():
    req_body = flask.request.get_json()
    recommended_places = PlaceRecommender().recommend_attraction(req_body['features'], req_body['activities'], req_body['destination'], req_body['top_n'])

    return json.dumps({"recommended_attractions":recommended_places.to_dict('records')})

@app.route('/api/recommendaccommodation/', methods = ['POST'])
def api_recommendaccom():
    req_body = flask.request.get_json()
    recommended_accom = PlaceRecommender().recommend_accommodation(req_body['places'])

    return json.dumps({"recommended_accommodation": recommended_accom})

@app.route('/api/recommendrestaurant/', methods = ['POST'])
def api_recommendrestaurant():
    req_body = flask.request.get_json()
    recommended_restaurant = PlaceRecommender().recommend_restaurant(req_body['cuisines'], req_body['destination'], req_body['top_n'])

    return json.dumps({"recommended_restaurants":recommended_restaurant.to_dict('records')}, indent=4)
