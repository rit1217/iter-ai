from place import Place
import datetime
from vrptw_base import VrptwGraph
from basic_aco import BasicACO


def generate_itinerary( places, destination, start_date, day_num, start_time, end_time):
        ants_num = 10
        max_iter = 200
        beta = 2
        q0 = 0.1

        graph = VrptwGraph(places, datetime.time(8), datetime.time(19))
        basic_aco = BasicACO(graph, ants_num=ants_num, max_iter=max_iter, beta=beta, q0=q0)

        return basic_aco.run_basic_aco(destination, start_date, day_num, start_time, end_time)


if __name__ == '__main__':
        destination = 'Bangkok'
        places = [
                Place('Prestige Suites Nana', 'ACCOMMODATION',  13.74370239, 100.5534596, 'intro', 'detail', destination, datetime.time(8), datetime.time(19)), 
                Place('Benchasiri Park', 'ATTRACTION',  13.73098757, 100.56755441, 'intro', 'detail', destination, datetime.time(15), datetime.time(20)),
                Place('Malai Restaurant', 'RESTAURANT',  13.722022, 100.546, 'intro', 'detail', destination, datetime.time(11), datetime.time(20)), 
                Place('Siriraj Phimukhsthan', 'ATTRACTION',  13.75972996, 100.4868832, 'intro', 'detail', destination, datetime.time(10), datetime.time(19)), 
                Place('Mini Murrah Farm', 'ATTRACTION',  13.76379474, 100.4967129, 'intro', 'detail', destination, datetime.time(9), datetime.time(18)), 
                Place('Wat Ratchabophit Sathitmahasimaram', 'ATTRACTION',  13.74913215, 100.49734105, 'intro', 'detail', destination, datetime.time(9), datetime.time(16,30)), 
                Place('The Royal Thai Army Museum', 'ATTRACTION',   13.761652, 100.508082, 'intro', 'detail', destination, datetime.time(8, 30), datetime.time(19)), 
                Place('R-Haan', 'RESTAURANT',  13.73189108, 100.5795599, 'intro', 'detail', destination, datetime.time(12), datetime.time(18)), 
                Place('Chulalongkorn University Museum of Natural History', 'ATTRACTION',  13.7374931, 100.53021883, 'intro', 'detail', destination, datetime.time(10), datetime.time(15,30)), 
                Place('JIM THOMPSON', 'SHOP',  13.730429, 100.533504, 'intro', 'detail', destination, datetime.time(9), datetime.time(22))
                ]
        
        # print('[')
        # for i in places:
        #         print(f'[{i.longitude}, {i.latitude}],')
        # print(']')

        itinerary = generate_itinerary(places, destination, datetime.datetime(2023, 7, 11), 2, datetime.time(8), datetime.time(19))
        print(itinerary)