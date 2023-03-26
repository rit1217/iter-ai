import datetime

from vrp import ItineraryGenerator
from components.place import Place
from components.itinerary import Itinerary

from .api import app


app.run(use_reloader=True, host='0.0.0.0', port=3000)