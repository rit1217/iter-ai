from .vrptw_base import VrptwGraph
from .basic_aco import BasicACO
from .config import ACO_PARAMS


class ItineraryGenerator:
    def generate_itinerary(self, places, destination, start_date, num_day, start_time, end_time):
        graph = VrptwGraph(places, start_time, end_time)
        basic_aco = BasicACO(graph, ants_num=ACO_PARAMS['ANTS_NUM'], max_iter=ACO_PARAMS['MAX_ITER'],
                              beta=ACO_PARAMS['BETA'], q0=ACO_PARAMS['Q0'])

        return basic_aco.run_basic_aco(destination, start_date, num_day, start_time, end_time)