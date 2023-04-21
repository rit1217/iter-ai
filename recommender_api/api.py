import flask
import json

from recommender import PlaceRecommender


app = flask.Flask(__name__) 



@app.route('/api/recommendplace/', methods = ['POST'])
def api_recommendplace():
    req_body = flask.request.get_json()
    recommended_places = PlaceRecommender().recommend_attraction(req_body['features'], req_body['top_n'])

    return json.dumps({"recommended_places":recommended_places.tolist()})
