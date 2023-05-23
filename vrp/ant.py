import numpy as np
from datetime import datetime, timedelta

from .vrptw_base import VrptwGraph
from components.constants import *


class Ant:
    def __init__(self, graph: VrptwGraph, start_date: datetime, start_index=0):
        self.graph = graph
        self.current_index = start_index
        self.vehicle_travel_time = 0
        self.start_index = start_index
        self.travel_path = [start_index]
        self.travel_time = []
        self.wait_time = []
        self.day_meals = list(graph.meal_time.keys())
        self.day = start_date

        self.index_to_visit = list(range(graph.node_num))
        self.index_to_visit.remove(start_index)

        self.available_index = self.index_to_visit[:]
        self.total_travel_distance = 0

    def clear(self):
        self.travel_path.clear()
        self.index_to_visit.clear()
    
    def cal_temp_dist_mat(self, vehicle_travel_time):
        distance_mat = np.copy(self.graph.node_dist_mat)
        for index in range(1, self.graph.node_num):
            ready_time = self.graph.nodes[index].ready_time[DAY_OF_WEEK[self.day.weekday()]]
            if ready_time > vehicle_travel_time:
                wait_time = ready_time - vehicle_travel_time
                for i in range(self.graph.node_num):
                    if i != index:
                        distance_mat[i][index] += wait_time

        return distance_mat

    def move_to_next_index(self, next_index):
        self.graph.temp_dist_mat = self.cal_temp_dist_mat(self.vehicle_travel_time)
        self.travel_path.append(next_index)
        self.total_travel_distance += self.graph.temp_dist_mat[self.current_index][next_index]
        self.travel_time.append(self.graph.temp_dist_mat[self.current_index][next_index])
        self.wait_time.append(self.graph.temp_dist_mat[self.current_index][next_index] - \
                        self.graph.node_dist_mat[self.current_index][next_index])
        
        next_node = self.graph.nodes[next_index]
        dist = self.graph.temp_dist_mat[self.current_index][next_index]

        if next_node.is_depot:
            self.vehicle_travel_time = 0
            self.day += timedelta(days=1)
        else:            
            self.vehicle_travel_time += dist + next_node.service_time
            self.index_to_visit.remove(next_index)
            self.available_index = self.index_to_visit[:]

        if next_node.place.category == 'RESTAURANT':
            if len(self.day_meals) > 1:
                self.day_meals.pop(0)
            else:
                self.day_meals = list(self.graph.meal_time.keys())

        self.current_index = next_index

    def index_to_visit_empty(self):
        return len(self.index_to_visit) == 0
    
    def check_empty_fleet(self):
        for i in range(len(self.travel_path[:-1])):
            if self.travel_path[i] == 0 and self.travel_path[i+1] == 0:
                return True
        
        return False

    def check_condition(self, next_index) -> bool:
        next_node = self.graph.nodes[next_index]
        self.graph.temp_dist_mat = self.cal_temp_dist_mat(self.vehicle_travel_time)
        dist = self.graph.temp_dist_mat[self.current_index][next_index]
        service_time = next_node.service_time
        arrive_time = self.vehicle_travel_time + dist
        due_time = next_node.due_time[DAY_OF_WEEK[self.day.weekday()]]

        if  arrive_time + service_time > self.graph.nodes[0].due_time[DAY_OF_WEEK[self.day.weekday()]] or\
            arrive_time + service_time > due_time:
            return False
        
        if arrive_time >= self.graph.meal_time[self.day_meals[0]][0] and \
            arrive_time <= self.graph.meal_time[self.day_meals[0]][1] and \
            next_node.place.category != 'RESTAURANT':
            return False
        
        if (arrive_time < self.graph.meal_time[self.day_meals[0]][0] or \
            arrive_time > self.graph.meal_time[self.day_meals[0]][1]) and \
            next_node.place.category == 'RESTAURANT':
            return False

        return True