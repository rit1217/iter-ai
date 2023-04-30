import flask
import json

from components.utils import *
from recommender import PlaceRecommender


app = flask.Flask(__name__) 



@app.route('/api/recommendplace/', methods = ['POST'])
def api_recommendplace():
    req_body = flask.request.get_json()
    recommended_places = PlaceRecommender().recommend(req_body['features'], req_body['top_n'])

    return json.dumps({"recommended_places":recommended_places.tolist()})


@app.route('/api/recommendaccom', methods = ['POST'])
def api_recommendaccom():
    req_body = flask.request.get_json()

    #TODO
    accom_list = []

    return nearest_place(req_body['places'], accom_list)
        
