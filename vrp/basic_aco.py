import numpy as np
import random
from threading import Event
import datetime

from .vrptw_base import VrptwGraph
from .ant import Ant
from .utils import *
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
        self.best_path_distance = None
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
            ants = list(Ant(self.graph) for _ in range(self.ants_num))

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

                        wait_time = self.graph.nodes[ants[k].index_to_visit[0]].ready_time
                        next_index = ants[k].index_to_visit[0]
                        for ind in ants[k].index_to_visit[1:]:
                            ind_ready_time = self.graph.nodes[ind].ready_time
                            if ind_ready_time < wait_time:
                                wait_time = ind_ready_time
                                next_index = ind
                        ants[k].move_to_next_index(next_index)

                    self.graph.local_update_pheromone(ants[k].current_index, next_index)

                if ants[k].index_to_visit_empty():
                    ants[k].graph.local_update_pheromone(ants[k].current_index, 0)
                    ants[k].move_to_next_index(0)
                    ants[k].wait_time.append(0)

                ants[k].insertion_procedure(stop_event)

            new_ants = []
            for ant in ants:
                if ant.index_to_visit_empty():
                    new_ants.append(ant)
            ants = new_ants

            if len(ants) == 0:
                continue

            paths_distance = np.array([ant.total_travel_distance for ant in ants])
            best_index = np.argmin(paths_distance)

            if self.best_path is None or paths_distance[best_index] < self.best_path_distance:
                self.best_path = ants[int(best_index)].travel_path
                self.best_wait_time = ants[int(best_index)].wait_time
                self.best_ants.append(ants[int(best_index)])

                # print('PATH DISTS', paths_distance, best_index)
                self.best_path_distance = paths_distance[best_index]
                self.best_vehicle_num = self.best_path.count(0) - 1
                start_iteration = iter

                # print('\n')
                # print('[iteration %d]: find a improved path, its distance is %f' % (iter, self.best_path_distance))
                # print('it takes %0.3f second multiple_ant_colony_system running' % (time.time() - start_time_total))
                date = datetime.date(start_date.year, start_date.month, start_date.day)
                cur_time = add_time(start_time, datetime.time(self.best_wait_time[0] // 60, self.best_wait_time[0] % 60))
                temp = []
                # print('\n\nBEST_PATHHH: ', self.best_path)
                # print('WAIT_TIME', self.best_wait_time)
                # print('BEST_PATH_DIST', self.best_path_distance)
                for ind, i in enumerate(self.best_path):
                    cur_node = self.graph.nodes[i]
                    cur_place = self.graph.nodes[i].place
                    service_time = cur_node.service_time
                    leave_time = add_time(cur_time, datetime.time(service_time // 60, service_time % 60))
                    temp.append(Agenda(cur_place, date
                                       , datetime.datetime(date.year, date.month, date.day, cur_time.hour, cur_time.minute, cur_time.second),
                                        datetime.datetime(date.year, date.month, date.day, leave_time.hour, leave_time.minute, leave_time.second)))
                    if ind == len(self.best_path) - 1:
                        minute = service_time
                    else:
                        minute = service_time + self.graph.node_dist_mat[i][self.best_path[ind+1]]
                    cur_time = add_time(cur_time, datetime.time(minute // 60, minute % 60))

                    if i == 0 and ind != 0:
                        plan.append(temp)

                        if ind != len(self.best_path) - 1:
                            day_start_time = add_time(start_time, datetime.time(self.best_wait_time[ind] // 60, self.best_wait_time[ind] % 60))
                        else:
                            day_start_time = start_time
                        cur_time = add_time(day_start_time, datetime.time(minute // 60, minute % 60))
                        date += datetime.timedelta(days=1)
                        print('\n\n', date)
                        temp = [Agenda(cur_place, date
                                       , datetime.datetime(date.year, date.month, date.day, day_start_time.hour, day_start_time.minute, day_start_time.second)
                                       , datetime.datetime(date.year, date.month, date.day, day_start_time.hour, day_start_time.minute, day_start_time.second))]
                        

                itinerary = Itinerary(dest, start_date, start_date + datetime.timedelta(days=len(plan) - 1), start_time, end_time, plan)
                plan = []

            self.graph.global_update_pheromone(self.best_path, self.best_path_distance)

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

        closeness = 1 / distance_mat

        transition_prob = self.graph.pheromone_mat[current_index][index_to_visit] * \
            np.power(closeness[current_index][index_to_visit], self.beta)

        transition_prob = transition_prob / np.sum(transition_prob)

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
