import numpy as np
import random
from datetime import time, datetime, timedelta

from .vrptw_base import VrptwGraph
from .ant import Ant
from components.utils import *
from components.agenda import Agenda
from components.itinerary import Itinerary
from .config import ACO_PARAMS


class BasicACO:
    def __init__(self, graph: VrptwGraph, ants_num=ACO_PARAMS['ANTS_NUM'], max_iter=ACO_PARAMS['MAX_ITER']
                 , beta=ACO_PARAMS['BETA'], q0=ACO_PARAMS['Q0']):
        self.graph = graph
        self.ants_num = ants_num
        self.max_iter = max_iter
        self.beta = beta
        self.q0 = q0
        self.best_score = None
        self.best_travel_distance = None
        self.best_path = None
        self.best_vehicle_num = None
        self.best_wait_time = None
        self.best_ants = []

    def run_basic_aco(self, dest, start_date, day_num, start_time, end_time):  
        for _ in range(self.max_iter):
            ants = list(Ant(self.graph, start_date) for _ in range(self.ants_num))

            for k in range(self.ants_num):
                unused_depot_count = day_num
                
                while not ants[k].index_to_visit_empty() and unused_depot_count > 0:

                    next_index, unused_depot_count = self.select_next_index(ants[k], unused_depot_count)

                    ants[k].move_to_next_index(next_index)
            
                    ants[k].graph.local_update_pheromone(ants[k].current_index, next_index)

                if ants[k].travel_path[-1] != 0:
                    ants[k].graph.local_update_pheromone(ants[k].current_index, 0)
                    ants[k].move_to_next_index(0)
                    ants[k].wait_time.append(0)

            scores = np.array([self.cal_score(ant) for ant in ants])
            paths_score = [i['TOTAL'] for i in scores] 
            best_index = np.argmin(paths_score)

            if self.best_path is None or paths_score[best_index] < self.best_score['TOTAL']:
                self.best_path = ants[int(best_index)].travel_path
                self.best_travel_time = ants[int(best_index)].travel_time
                self.best_wait_time = ants[int(best_index)].wait_time
                self.best_ants.append(ants[int(best_index)])

                self.best_score = scores[best_index]
                self.best_travel_distance = ants[int(best_index)].total_travel_distance
                self.best_vehicle_num = self.best_path.count(0) - 1

            self.graph.global_update_pheromone(self.best_path, self.best_score)

        return self.best_path, self.best_score
        # return self.construct_itinerary(dest, start_date, start_time, end_time)
        
    def select_next_index(self, ant, unused_depot_count):
        current_index = ant.current_index
        index_to_visit = ant.index_to_visit

        if ant.index_to_visit_empty():
            return 0, unused_depot_count - 1
        
        else:
            distance_mat = ant.cal_temp_dist_mat(ant.vehicle_travel_time)
            
            self.graph.temp_dist_mat = distance_mat
            ant.graph.temp_dist_mat = distance_mat
            closeness = 1 / distance_mat
            transition_prob = self.graph.pheromone_mat[current_index][index_to_visit] * \
                np.power(closeness[current_index][index_to_visit], self.beta)
            transition_prob = transition_prob / np.sum(transition_prob)

            # if np.random.rand() < self.q0:
            next_index = np.random.choice(index_to_visit, p=transition_prob)
            # else:
            #     next_index = self._stochastic_accept(index_to_visit, transition_prob)

            if not ant.check_condition(next_index):
                    temp = [x for _, x in sorted(zip(transition_prob, index_to_visit), reverse=True)]
                    flag = False
                    for n in temp:
                        if ant.check_condition(n):
                            flag = True
                            next_index = n
                            break

                    if not flag and ant.travel_path[-1] != 0:
                        next_index = 0
                        unused_depot_count -= 1

        return next_index, unused_depot_count

    def _stochastic_accept(self, index_to_visit, transition_prob):
        # stochastic acceptance algorithm
        N = len(index_to_visit)

        sum_tran_prob = np.sum(transition_prob)
        norm_transition_prob = transition_prob/sum_tran_prob
        while True:
            ind = int(N * random.random())
            if random.random() <= norm_transition_prob[ind]:
                return index_to_visit[ind]
            
    def place_visit_objective(self, ant):
        # ant.travel_path is list of index of nodes in a graph that visited by the ant
        path = [ind for ind in ant.travel_path if ind != 0] #travel path excluding hotel

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

    
    def total_time_objective(self, ant):
        return ant.total_travel_distance

    def cal_score(self, ant):
        place_visit_score = self.place_visit_objective(ant)
        distance_score = self.total_time_objective(ant)
        score = {'VISIT': place_visit_score, 'DISTANCE': distance_score, 
                'TOTAL' :(place_visit_score )+ distance_score}
        
        return score
    
    def construct_itinerary(self, dest, start_date, start_time, end_time):
        plan = []
        print('BEST_PATHHH: ', self.best_path)
        print('SCORE:', self.best_score)
        print('TRAVEL_TIME', self.best_travel_time)
        print('WAIT_TIME', self.best_wait_time)

        cur_date = datetime(start_date.year, start_date.month, start_date.day)
        cur_time = add_time(start_time, time(self.best_wait_time[0] // 60, self.best_wait_time[0] % 60))
        temp = []
        wait_time_ind = 0

        travel_time_ind = 0
        for ind, i in enumerate(self.best_path):
            cur_node = self.graph.nodes[i]
            cur_place = self.graph.nodes[i].place
            if ind < len(self.best_path) - 1:
                next_place = self.graph.nodes[self.best_path[ind+1]].place
                if i == 0 and ind != 0:
                    travel_time = {}
                else:
                    travel_time = {next_place.place_id: int(self.best_travel_time[travel_time_ind] - self.best_wait_time[wait_time_ind])}
                    wait_time_ind += 1
                    travel_time_ind += 1
            else:
                next_place = None
                travel_time = {}
            service_time = cur_node.service_time
            leave_time = add_time(cur_time, time(service_time // 60, service_time % 60))
            temp.append(Agenda(cur_place, cur_date
                                , datetime(cur_date.year, cur_date.month, cur_date.day, cur_time.hour, cur_time.minute, cur_time.second)
                                ,datetime(cur_date.year, cur_date.month, cur_date.day, leave_time.hour, leave_time.minute, leave_time.second)
                                ,travel_time))
            if ind == len(self.best_path) - 1:
                minute = service_time
            else:
                minute = service_time + self.graph.node_dist_mat[i][self.best_path[ind+1]]
            cur_time = add_time(cur_time, time(minute // 60, minute % 60))

            if i == 0 and ind != 0:
                plan.append(temp)

                if ind != len(self.best_path) - 1:
                    day_start_time = add_time(start_time, time(self.best_wait_time[ind] // 60, self.best_wait_time[ind] % 60))
                else:
                    day_start_time = start_time
                cur_time = add_time(day_start_time, time(minute // 60, minute % 60))
                cur_date += timedelta(days=1)
                if ind < len(self.best_path) - 1:
                    next_place = self.graph.nodes[self.best_path[ind+1]].place

                    travel_time = {next_place.place_id: int(self.best_travel_time[travel_time_ind] - self.best_wait_time[wait_time_ind])}
                    wait_time_ind += 1
                    travel_time_ind += 1
                else:
                    next_place = None
                    travel_time = {}
                temp = [Agenda(cur_place, cur_date
                                , datetime(cur_date.year, cur_date.month, cur_date.day, day_start_time.hour, day_start_time.minute, day_start_time.second)
                                , datetime(cur_date.year, cur_date.month, cur_date.day, day_start_time.hour, day_start_time.minute, day_start_time.second)
                                , travel_time)]
                

        return Itinerary(dest, start_date, start_date + timedelta(days=len(plan) - 1), start_time, end_time, plan)