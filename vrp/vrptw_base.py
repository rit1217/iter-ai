import numpy as np
import copy
import requests
import googlemaps
import os
from datetime import time
from dotenv import load_dotenv


from components.place import Place
from components.utils import *
from components.constants import *
from .config import PLACE_CATEGORY_SERVICE_TIME, DEPOT_INDEX


load_dotenv()


class Node:
    def __init__(self, id:  int, place: Place, ready_time: float, due_time: float, service_time: float):
        self.id = id
        self.place = place

        if id == DEPOT_INDEX:
            self.is_depot = True
        else:
            self.is_depot = False

        self.x = place.latitude
        self.y = place.longitude
        self.ready_time = ready_time
        self.due_time = due_time
        self.service_time = service_time


class VrptwGraph:
    def __init__(self, places, start_date, start_time, end_time, rho=0.1, distance_cal_service="OPENROUTESERVICE", cat_service_time=PLACE_CATEGORY_SERVICE_TIME):
        self.node_num = len(places)
        self.cat_service_time = cat_service_time
        self.nodes = []

        for ind, place in enumerate(places):
            # if place.category != 'RESTAURANT':
            ready_time = {}
            due_time = {}
            for day, op_time in place.opening_time.items():
                ready_time[day] = max(0, to_minute(op_time) - to_minute(start_time))

            for day, cl_time in place.closing_time.items():
                due_time[day] = min(to_minute(end_time) - to_minute(start_time), to_minute(cl_time) - to_minute(start_time))
            # else:
            #     ready_time = max(to_minute(time(11,30)) - to_minute(start_time), to_minute(place.opening_time) - to_minute(start_time))
            #     due_time = min(to_minute(time(15)) - to_minute(start_time), to_minute(place.closing_time) - to_minute(start_time))

            self.nodes.append(Node(ind, place, ready_time ,due_time, self.cat_service_time[place.category]))
        
        self.node_dist_mat = self._cal_dist_mat(places, distance_cal_service)
        
        self.temp_dist_mat = np.copy(self.node_dist_mat)

        self.meal_time = {}

        end = to_minute(end_time) - to_minute(start_time)
        for k, v in MEAL_TIME.items():
            meal_start = to_minute(str_to_time(v[0])) - to_minute(start_time)
            meal_end = to_minute(str_to_time(v[1])) - to_minute(start_time)
                    
            meal_start = max(0, meal_start)
            meal_end = min(meal_end, end - 150)
    
            if meal_start <= meal_end:
                self.meal_time[k] = [meal_start, meal_end]

        for index in range(len(self.nodes)):
            wait_time = self.nodes[index].ready_time[DAY_OF_WEEK[start_date.weekday()]]
            for i in range(self.node_num):
                if i != self.nodes[index]:
                    self.temp_dist_mat[i][index] += wait_time
        self.vehicle_num = 2

        self.rho = rho

        self.nnh_travel_path, self.init_pheromone_val, _ = self.nearest_neighbor_heuristic(start_date, self.vehicle_num)
        self.init_pheromone_val = 1/(self.init_pheromone_val * self.node_num)

        self.pheromone_mat = np.ones((self.node_num, self.node_num)) * self.init_pheromone_val
        self.heuristic_info_mat = 1 / self.node_dist_mat

    def copy(self, init_pheromone_val):
        new_graph = copy.deepcopy(self)

        new_graph.init_pheromone_val = init_pheromone_val
        new_graph.pheromone_mat = np.ones((new_graph.node_num, new_graph.node_num)) * init_pheromone_val

        return new_graph

    @staticmethod
    def calculate_dist(node_a, node_b):
        return np.linalg.norm((node_a.x - node_b.x, node_a.y - node_b.y))

    def local_update_pheromone(self, start_ind, end_ind):
        self.pheromone_mat[start_ind][end_ind] = (1-self.rho) * self.pheromone_mat[start_ind][end_ind] + \
                                                  self.rho * self.init_pheromone_val

    def local_update_multi_pheromone(self, start_ind, end_ind, path_score, best_score):
        self.pheromone_mat[start_ind][end_ind] = (1-self.rho) * self.pheromone_mat[start_ind][end_ind] + \
                                                  self.rho * self.init_pheromone_val
        # if best_score == None:
        #     best_score = {'VISIT': 0, 'DISTANCE': 0}
        # # print(path_score['VISIT'], best_score['VISIT'])
        # # print(path_score['DISTANCE'], best_score['DISTANCE'])
        # if path_score['VISIT'] - best_score['VISIT'] != -1:
        #     self.pheromone_mat[start_ind][end_ind] += 1 / (1 + path_score['VISIT'] - best_score['VISIT'])
        
        # self.pheromone_mat[start_ind][end_ind] += 1 / (1 + path_score['DISTANCE'] - best_score['DISTANCE'])

    def global_update_pheromone(self, best_path, best_path_distance):
        
        self.pheromone_mat = (1-self.rho) * self.pheromone_mat

        current_ind = best_path[0]
        for next_ind in best_path[1:]:
            self.pheromone_mat[current_ind][next_ind] += self.rho/best_path_distance
            current_ind = next_ind

    ##TODO
    def global_update_multi_pheromone(self, best_path, path_score, best_score):
        
        # self.pheromone_mat = (1-self.rho) * self.pheromone_mat

        # current_ind = best_path[0]
        # for next_ind in best_path[1:]:
        #     self.pheromone_mat[current_ind][next_ind] += 1 / (1 + path_score['VISIT'] - best_score['VISIT'])
        #     self.pheromone_mat[current_ind][next_ind] += 1 / (1 + path_score['DISTANCE'] - best_score['DISTANCE'])

        #     current_ind = next_ind
        self.pheromone_mat = (1-self.rho) * self.pheromone_mat

        current_ind = best_path[0]
        for next_ind in best_path[1:]:
            self.pheromone_mat[current_ind][next_ind] += self.rho/best_score['TOTAL']
            current_ind = next_ind



    def nearest_neighbor_heuristic(self, current_date, max_vehicle_num=None):
        index_to_visit = list(range(1, self.node_num))
        current_index = 0
        current_time = 0
        travel_distance = 0
        travel_path = [0]

        if max_vehicle_num is None:
            max_vehicle_num = self.node_num
        while len(index_to_visit) > 0 and max_vehicle_num > 0:
            nearest_next_index = self._cal_nearest_next_index(index_to_visit, current_index, current_time, current_date)

            if nearest_next_index is None:
                travel_distance += self.temp_dist_mat[current_index][0]

                current_time = 0
                travel_path.append(0)
                current_index = 0

                max_vehicle_num -= 1
            else:

                dist = self.temp_dist_mat[current_index][nearest_next_index]
                wait_time = max(self.nodes[nearest_next_index].ready_time[DAY_OF_WEEK[current_date.weekday()]] - current_time - dist, 0)
                service_time = self.nodes[nearest_next_index].service_time

                current_time += dist + wait_time + service_time
                index_to_visit.remove(nearest_next_index)

                travel_distance += self.temp_dist_mat[current_index][nearest_next_index]
                travel_path.append(nearest_next_index)
                current_index = nearest_next_index

        travel_distance += self.temp_dist_mat[current_index][0]
        travel_path.append(0)

        vehicle_num = travel_path.count(0)-1
        return travel_path, travel_distance, vehicle_num

    def _cal_dist_mat(self, places, service):
        if service == "OPENROUTESERVICE":
            headers = {
                'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
                'Authorization': os.getenv('OPENROUTE_KEY'),
                'Content-Type': 'application/json; charset=utf-8'
            }
            # if len(places) >= 60:
            #     locations = []
            #     for place in places:
            #         locations.append([place.longitude, place.latitude])
            #     r = requests.post('https://api.openrouteservice.org/v2/matrix/driving-car', json={"locations": []}, headers=headers)
            #     resp = r.json()
            #     dist_mat = np.array(resp['durations']).astype(int)

            # else:
            body = {"locations": []}
            for place in places:
                body['locations'].append([place.longitude, place.latitude])

            
            try:
                r = requests.post('https://api.openrouteservice.org/v2/matrix/driving-car', json=body, headers=headers)

                print( r.status_code, r.reason)
                resp = r.json()
                dist_mat = np.array(resp['durations']).astype(int)
                dist_mat //= 60
            except Exception as e:
                print(e)

        elif service == "GOOGLE":
            gmap = googlemaps.Client(key = os.getenv('GCP_KEY'))
            coords = [{'lat':i.latitude, 'lng':i.longitude} for i in places]
            response = gmap.distance_matrix(coords, coords)
            dist_mat = []
            for rowInd in range(len(response['rows'])):
                    temp = []
                    
                    for i in response['rows'][rowInd]['elements']:
                        temp.append(i['duration']['value'] // 60)
                    dist_mat.append(temp)
            dist_mat = np.array(dist_mat)
            
        return dist_mat  #second to minute
       
    
    def _cal_nearest_next_index(self, index_to_visit, current_index, current_time, current_date):

        nearest_ind = None
        nearest_distance = None

        for next_index in index_to_visit:

            dist = self.temp_dist_mat[current_index][next_index]
            wait_time = max(self.nodes[next_index].ready_time[DAY_OF_WEEK[current_date.weekday()]] - current_time - dist, 0)
            service_time = self.nodes[next_index].service_time

            if current_time + dist + wait_time + service_time + self.node_dist_mat[next_index][0] > self.nodes[0].due_time[DAY_OF_WEEK[current_date.weekday()]]:
                continue

            if current_time + dist < self.nodes[next_index].ready_time[DAY_OF_WEEK[current_date.weekday()]] or current_time + dist > self.nodes[next_index].due_time[DAY_OF_WEEK[current_date.weekday()]]:

                continue

            if nearest_distance is None or self.node_dist_mat[current_index][next_index] < nearest_distance:
                nearest_distance = self.node_dist_mat[current_index][next_index]
                nearest_ind = next_index

        return nearest_ind


