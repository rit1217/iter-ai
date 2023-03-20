from .vrptw_base import VrptwGraph
from .basic_aco import BasicACO


class ItineraryGenerator:
    def generate_itinerary(self, places, destination, start_date, num_day, start_time, end_time):
        graph = VrptwGraph(places, start_time, end_time)
        basic_aco = BasicACO(graph)

        return basic_aco.run_basic_aco(destination, start_date, num_day, start_time, end_time)