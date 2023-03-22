from datetime import datetime, date

from .constants import *

class Agenda:
    def __init__(self, place, arrive, leave):
        self.place = place
        if type(arrive) == datetime:
            arrive = arrive.time()
        if type(leave) == datetime:
            leave = leave.time()
        self.arrival_time = arrive #datetime
        self.leave_time = leave #datetime        
        self.duration = datetime.combine(date.today(), leave) - datetime.combine(date.today(), arrive)


    def __str__(self):
        
        return '' + str(self.place) + ' : ' + str(self.arrival_time) + ' - ' + str(self.leave_time) + ' visit for ' + str(self.duration)

    def arrive_only(self):
        return '' + str(self.place) + ' : ARRIVE ' + str(self.arrival_time)

    def leave_only(self):
        return '' + str(self.place) + ' : LEAVE ' + str(self.leave_time)

    def to_dict(self):
        return {
            'place': self.place.to_dict(),
            'arrival_time': self.arrival_time.strftime(DATETIME_FORMAT),
            'leave_time': self.leave_time.strftime(DATETIME_FORMAT),
            'duration': str(self.duration)
        }