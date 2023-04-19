from .vrptw_base import VrptwGraph
from .basic_aco import BasicACO
from .config import PLACE_CATEGORY_SERVICE_TIME


class ItineraryGenerator:
    def generate_itinerary(self, places, destination, start_date, num_day, start_time, end_time, distance_cal_service="OPENROUTESERVICE", cat_service_time=PLACE_CATEGORY_SERVICE_TIME):
        graph = VrptwGraph(places, start_date, start_time, end_time, distance_cal_service=distance_cal_service, cat_service_time=cat_service_time)
        basic_aco = BasicACO(graph)

        return basic_aco.run_basic_aco(destination, start_date, num_day, start_time, end_time)