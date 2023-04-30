import numpy as np
import random
from threading import Event
from datetime import date, time, datetime, timedelta

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
        plan = []
        itinerary = None  
        start_iteration = 0

        for iter in range(self.max_iter):
            stop_event = Event()
            ants = list(Ant(self.graph, start_date) for _ in range(self.ants_num))

            for k in range(self.ants_num):
                unused_depot_count = day_num
                
                while not ants[k].index_to_visit_empty() and unused_depot_count > 0:

                    next_index = self.select_next_index(ants[k])
                    wait_time = self.graph.temp_dist_mat[ants[k].current_index][next_index] - \
                        self.graph.node_dist_mat[ants[k].current_index][next_index]

                    if not ants[k].check_condition(next_index):

                        temp = ants[k].index_to_visit[:]
                        flag = False
                        for n in temp:
                            cond = ants[k].check_condition(n)
                            if cond:
                                flag = True
                                next_index = n
                                break

                        if not flag:
                            next_index = 0
                            unused_depot_count -= 1
                        elif ants[k].travel_path[-1] == ants[k].start_index:
                            pass

                    elif ants[k].travel_path[-1] == ants[k].start_index:
                        pass

                    ants[k].move_to_next_index(next_index)

                    if ants[k].check_empty_fleet() and not ants[k].index_to_visit_empty():
                        ants[k].travel_path = ants[k].travel_path[:-1]
                        ants[k].wait_time = ants[k].wait_time[:-1]
                        unused_depot_count += 1

                        wait_time = float('inf')
                        next_index = None
                        for ind in ants[k].index_to_visit:
                            temp_wait_time = self.graph.nodes[ind].ready_time[DAY_OF_WEEK[ants[k].day.weekday()]]
                            if temp_wait_time >= self.graph.meal_time[ants[k].day_meals[0]][0] and \
                                temp_wait_time <= self.graph.meal_time[ants[k].day_meals[0]][1] and \
                                    self.graph.nodes[ind].place.category != 'RESTAURANT':
                                continue

                            if temp_wait_time < wait_time:
                                wait_time = temp_wait_time
                                next_index = ind

                        # wait_time = self.graph.nodes[ants[k].index_to_visit[0]].ready_time
                        # next_index = ants[k].index_to_visit[0]
                        # for ind in ants[k].index_to_visit[1:]:
                        #     ind_ready_time = self.graph.nodes[ind].ready_time
                        #     if ind_ready_time < wait_time:
                        #         wait_time = ind_ready_time
                        #         next_index = ind

                        ants[k].move_to_next_index(next_index)

                    ants[k].graph.local_update_multi_pheromone(ants[k].current_index, next_index, self.cal_score(ants[k]), self.best_score )

                if ants[k].travel_path[-1] != 0:
                    ants[k].graph.local_update_multi_pheromone(ants[k].current_index, 0, self.cal_score(ants[k]), self.best_score )

                    ants[k].move_to_next_index(0)
                    ants[k].wait_time.append(0)

                # ants[k].insertion_procedure(stop_event)

            # new_ants = []
            # for ant in ants:
            #     if ant.index_to_visit_empty():
            #         new_ants.append(ant)
            # ants = new_ants

            # if len(ants) == 0:
            #     continue

            ##TODO
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
                start_iteration = iter

                cur_date = datetime(start_date.year, start_date.month, start_date.day)
                cur_time = add_time(start_time, time(self.best_wait_time[0] // 60, self.best_wait_time[0] % 60))
                temp = []
                wait_time_ind = 0

                travel_time_ind = 1

                print('\n\nBEST_PATHHH: ', self.best_path)
                print('SCORE:', self.best_score)
                print('TRAVEL_TIME', self.best_travel_time)
                print('WAIT_TIME', self.best_wait_time)

                for ind, i in enumerate(self.best_path):
                    cur_node = self.graph.nodes[i]
                    cur_place = self.graph.nodes[i].place
                    if ind < len(self.best_path) - 1:
                        next_place = self.graph.nodes[self.best_path[ind+1]].place
                        if self.best_travel_time[travel_time_ind] == 0:
                            travel_time = {}
                            travel_time_ind += 1
                        else:
                            travel_time = {next_place.place_id: self.best_travel_time[travel_time_ind] - self.best_wait_time[wait_time_ind]}
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

                            travel_time = {next_place.place_id: self.best_travel_time[travel_time_ind] - self.best_wait_time[wait_time_ind]}
                            wait_time_ind += 1
                            travel_time_ind += 1
                        else:
                            next_place = None
                            travel_time = {}
                        
                        temp = [Agenda(cur_place, cur_date
                                       , datetime(cur_date.year, cur_date.month, cur_date.day, day_start_time.hour, day_start_time.minute, day_start_time.second)
                                       , datetime(cur_date.year, cur_date.month, cur_date.day, day_start_time.hour, day_start_time.minute, day_start_time.second)
                                       , travel_time)]
                        

                itinerary = Itinerary(dest, start_date, start_date + timedelta(days=len(plan) - 1), start_time, end_time, plan)
                plan = []

            #TODO
            self.graph.global_update_pheromone(self.best_path, self.best_travel_distance)
            # self.graph.global_update_multi_pheromone(self.best_path, self.cal_score(), self.best_score)

            given_iteration = 100
            if iter - start_iteration > given_iteration and len(plan) == 2:
                # print('\n')
                # print('iteration exit: can not find better solution in %d iteration' % given_iteration)
                break

        # print('\nBEST_PATH: ', self.best_path)
        # print('WAIT_TIME', self.best_wait_time)

        return itinerary
        
    def select_next_index(self, ant):
        
        current_index = ant.current_index
        index_to_visit = ant.index_to_visit
        if len(index_to_visit) == 0:
            return 0
        
        distance_mat = ant.cal_temp_dist_mat(ant.vehicle_travel_time)
        
        self.graph.temp_dist_mat = distance_mat
        ant.graph.temp_dist_mat = distance_mat

        # print('\n dist', distance_mat)

        closeness = 1 / distance_mat
        # print('\n closeness', closeness)

        transition_prob = self.graph.pheromone_mat[current_index][index_to_visit] * \
            np.power(closeness[current_index][index_to_visit], self.beta)
        # print('\ntrans', transition_prob)
        transition_prob = transition_prob / np.sum(transition_prob)
        # print(current_index, index_to_visit,transition_prob)
        if np.random.rand() < self.q0:
            next_index = np.random.choice(index_to_visit, p=transition_prob)
        else:
            next_index = BasicACO.stochastic_accept(index_to_visit, transition_prob)

        return next_index

    @staticmethod
    def stochastic_accept(index_to_visit, transition_prob):
        
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

        avg_travel_time = sum(ant.travel_time) / (len(ant.travel_time) - ant.travel_time.count(0))

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
        # print()
        # for ind in ant.travel_path:
        #     print( self.graph.nodes[ind].place, self.graph.nodes[ind].place.category)
        # print(score)
        # print()
        return score




        
