from .vrptw_base import VrptwGraph
from .basic_aco import BasicACO
from .ga import GeneticAlgorithmVRPTW
from .dfs import DepthFirstSearch
from .config import PLACE_CATEGORY_SERVICE_TIME, RHO
import sys


class ItineraryGenerator:
    def generate_itinerary(self, places, destination, start_date, num_day, start_time, end_time, distance_cal_service="OPENROUTESERVICE", cat_service_time=PLACE_CATEGORY_SERVICE_TIME):
        graph = VrptwGraph(places, start_date, start_time, end_time, rho=RHO, distance_cal_service=distance_cal_service, cat_service_time=cat_service_time)
        basic_aco = BasicACO(graph)

        return basic_aco.run_basic_aco(destination, start_date, num_day, start_time, end_time)
    

    def generate_itinerary_ga(self, places, destination, start_date, num_day, start_time, end_time, distance_cal_service="OPENROUTESERVICE", cat_service_time=PLACE_CATEGORY_SERVICE_TIME):
        graph = VrptwGraph(places, start_date, start_time, end_time, rho=RHO, distance_cal_service=distance_cal_service, cat_service_time=cat_service_time)
        ga = GeneticAlgorithmVRPTW(graph, start_time, num_day)
        best_solution = ga.run()
        print(best_solution)
        return best_solution
    
    def generate_itinerary_dfs(self, places, destination, start_date, num_day, start_time, end_time, distance_cal_service="OPENROUTESERVICE", cat_service_time=PLACE_CATEGORY_SERVICE_TIME):
        graph = VrptwGraph(places, start_date, start_time, end_time, rho=RHO, distance_cal_service=distance_cal_service, cat_service_time=cat_service_time)
        dfs = DepthFirstSearch(graph)

        new_limit = 10000  # New recursion limit
        sys.setrecursionlimit(new_limit)
        visited = [False] * len(graph.nodes)
        current_path = []
        best_path = [float('inf'), None]
        dfs.find_shortest_path_dfs(graph.nodes[0], visited, current_path, best_path, 0, 0, graph.start_date, num_day - 1)
        best_solution = best_path[1]
        print(best_solution, best_path[0])
        return best_solution