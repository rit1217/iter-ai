from datetime import datetime, date


class Agenda:
    def __init__(self, place, arrive, leave):
        self.place = place
        self.arrival_time = arrive #datetime
        self.leave_time = leave #datetime
        self.duration = datetime.combine(date.today(), leave) - datetime.combine(date.today(), arrive)


    def __str__(self):
        
        return '' + str(self.place) + ' : ' + str(self.arrival_time) + ' - ' + str(self.leave_time) + ' visit for ' + str(self.duration)

    def arrive_only(self):
        return '' + str(self.place) + ' : ARRIVE ' + str(self.arrival_time)

    def leave_only(self):
        return '' + str(self.place) + ' : LEAVE ' + str(self.leave_time)
