import flask
import json

from components.utils import *
from recommender import PlaceRecommender


app = flask.Flask(__name__) 



@app.route('/api/recommendplace/', methods = ['POST'])
def api_recommendplace():
    req_body = flask.request.get_json()
    recommended_places = PlaceRecommender().recommend_attraction(req_body['features'], req_body['activities'], req_body['destination'], req_body['top_n'])

    return json.dumps({"recommended_places":recommended_places.to_dict('records')})

@app.route('/api/recommendaccom', methods = ['POST'])
def api_recommendaccom():
    req_body = flask.request.get_json()

    #TODO
    accom_list = []

    return nearest_place(req_body['places'], accom_list)

@app.route('/api/recommendrestaurant/', methods = ['POST'])
def api_recommendrestaurant():
    req_body = flask.request.get_json()
    recommended_restaurant = PlaceRecommender().recommend_restaurant(req_body['cuisines'], req_body['destination'], req_body['top_n'])

    return json.dumps({"places":recommended_restaurant.to_dict('records')}, indent=4)
