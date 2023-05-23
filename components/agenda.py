from datetime import datetime

from .constants import *
from .utils import *


class Agenda:
    def __init__(self, place, date, arrive, leave, travel_time):
        self.place = place
        if type(arrive) == datetime:
            arrive = arrive.time()
        if type(leave) == datetime:
            leave = leave.time()
        self.date = date
        self.arrival_time = arrive #datetime
        self.leave_time = leave #datetime        
        self.duration = datetime.combine(date.today(), leave) - datetime.combine(date.today(), arrive)
        self.travel_time = travel_time        

    def __str__(self):
        
        return f'{self.place.place_id} ' + f'{self.place.types} ' + str(self.place) + ' : ' + str(self.arrival_time) + ' - ' + str(self.leave_time) + ' visit for ' + str(self.duration) + f' travel {self.travel_time}'

    def arrive_only(self):
        return f'{self.place.place_id} ' + str(self.place) + ' : ARRIVE ' + str(self.arrival_time)+ f' travel {self.travel_time}'

    def leave_only(self):
        return f'{self.place.place_id} ' + str(self.place) + ' : LEAVE ' + str(self.leave_time)+ f' travel {self.travel_time}'

    def to_dict(self):
        return {
            'place_id': self.place.place_id,
            'date': self.date.strftime(DATE_FORMAT),
            'arrival_time': self.arrival_time.strftime(TIME_FORMAT),
            'leave_time': self.leave_time.strftime(TIME_FORMAT),
            'travel_time': self.travel_time
        }
    
    def check_open_close_time(self):
        if to_minute(self.arrival_time) > to_minute(self.place.closing_time):
            return f'{self.place.place_name} cannot be arrived on time'
        elif to_minute(self.leave_time) > to_minute(self.place.closing_time):
            return f'{self.place.place_name} will close before leaving'
        return  ''