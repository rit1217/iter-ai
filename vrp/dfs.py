import random
from collections import deque
from datetime import timedelta
from components.constants import *
from components.utils import *
import numpy as np


class DepthFirstSearch:
    def __init__(self, graph):
        self.graph = graph
    
    def cal_temp_dist_mat(self, vehicle_travel_time, day):
        distance_mat = np.copy(self.graph.node_dist_mat)
        for index in range(1, self.graph.node_num):
            ready_time = self.graph.nodes[index].ready_time[DAY_OF_WEEK[day.weekday()]]
            if ready_time > vehicle_travel_time:
                wait_time = ready_time - vehicle_travel_time
                for i in range(self.graph.node_num):
                    if i != index:
                        distance_mat[i][index] += wait_time

        return distance_mat

    def check_condition(self, current_index, next_index, day, travel_time) -> bool:
        next_node = self.graph.nodes[next_index]
        self.graph.temp_dist_mat = self.cal_temp_dist_mat(travel_time, day)
        dist = self.graph.temp_dist_mat[current_index][next_index]
        service_time = next_node.service_time
        arrive_time = travel_time + dist
        due_time = next_node.due_time[DAY_OF_WEEK[day.weekday()]]

        if  arrive_time + service_time > self.graph.nodes[0].due_time[DAY_OF_WEEK[day.weekday()]] or\
            arrive_time + service_time > due_time:
            return False
        if next_node.place.category == 'RESTAURANT':
            flag = False
            for k,v in self.graph.meal_time.items():
                if arrive_time >= v[0] and \
                    arrive_time <= v[1]:
                    flag = True
                
                if (arrive_time < v[0] or \
                    arrive_time > v[1]) and \
                    next_node.place.category == 'RESTAURANT':
                    flag = True
            if not flag:
                return False
        else:
            flag = False
            for k,v in self.graph.meal_time.items():
                if (arrive_time < v[0] or \
                    arrive_time > v[1]):
                    flag = True
            if not flag:
                return False

        return arrive_time + next_node.service_time

    def find_shortest_path_dfs(self, start, visited, current_path, best_path, total_distance, current_time, day, num_day):
        visited[start.id] = True
        current_path.append(start.id)
        temp_path = current_path[:]
        if temp_path[-1] != 0:
            temp_path.append(0)
        
        score = self.cal_score(temp_path, total_distance + self.graph.node_dist_mat[start.id][0])
        if best_path[1] == None or len(best_path[1]) < len(temp_path) or\
              (len(best_path[1]) == len(temp_path) and score['TOTAL'] < best_path[0]):
            best_path[0] = score['TOTAL']
            best_path[1] = temp_path[:]
        
        flag = False
        for neighbor in self.graph.nodes[1:]:
            # waiting_time = max(0, start.ready_time[weekday] - current_time)
            arrival_time = self.check_condition(start.id, neighbor.id, day, current_time)
            distance = self.graph.temp_dist_mat[start.id][neighbor.id]

            if not visited[neighbor.id] and arrival_time:
                self.find_shortest_path_dfs(neighbor, visited, current_path, best_path, total_distance + distance, arrival_time, day, num_day)
                flag = True
        if num_day > 0:
            self.find_shortest_path_dfs(self.graph.nodes[0], visited, current_path, best_path, total_distance + distance, 0, day + timedelta(days=1), num_day - 1)

        # print(temp_path, score)

        # if not flag and False in visited:
        #     self.find_shortest_path_dfs(self.graph.nodes[0], visited, current_path, best_path, total_distance + distance, 0, day + timedelta(days=1))

        current_path.pop()
        visited[start.id] = False

    def place_visit_objective(self, travel_path):
        # ant.travel_path is list of index of nodes in a graph that visited by the ant
        path = [ind for ind in travel_path if ind != 0] #travel path excluding hotel

        # ant.travel_time is list of travel_time + wait_time between places
        # e.g. [0, 39, 18, 0, 17, 6]
        # noted that 0 in ant.travel_time is the start of each day in the trip

        # avg_travel_time = sum(ant.travel_time) / (len(ant.travel_time) - ant.travel_time.count(0))

        num_place = len(set(path))
        num_type = {}
        cuisine_type = {}
        num_shop = 0
        score = 0
        for ind in path:
            place = self.graph.nodes[ind].place
            if place.category == 'RESTAURANT':
                for type in place.types:
                    if type not in cuisine_type.keys():
                        cuisine_type[type] = 0
                    score += (((num_place - cuisine_type[type])/num_place)) \
                        / len(place.types) # place.types in this case is cuisine_types for restaurant
                    cuisine_type[type] += 1

            elif place.category == 'ATTRACTION':
                # place.types is variable stored types of place, i.e.,attraction_types,
                #  cuisine_types, etc.
                for type in place.types:
                    if type not in num_type.keys():
                        num_type[type] = 0
                    score += ( ((num_place - num_type[type])/num_place))/len(place.types)
                    num_type[type] += 1

            elif place.category == 'SHOP':
                score += ((num_place - num_shop)/num_place)
                num_shop += 1
        
        return -(score*num_place)

    def cal_score(self, travel_path, total_travel):
        place_visit_score = self.place_visit_objective(travel_path)
        distance_score = total_travel
        score = {'VISIT': place_visit_score, 'DISTANCE': distance_score, 
                'TOTAL' :(place_visit_score )+ distance_score}
        
        return score