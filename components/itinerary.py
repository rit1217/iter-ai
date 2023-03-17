class Itinerary:
    def __init__(self, dest, start_date, end_date, start_time, end_time, plan):
        self.destination = dest
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.plan = plan
    
    def __str__(self):
        plan = ''
        for ind, day_plan in enumerate(self.plan):
            plan += f'DAY {ind + 1}:\n'
            for d_ind, agenda in enumerate(day_plan):
                if d_ind == 0:
                    plan += agenda.leave_only() + '\n'

                elif d_ind == len(day_plan) - 1:
                    plan += agenda.arrive_only() + '\n'
                else:
                    plan += str(agenda) + '\n'
        
        return '' + self.destination + ' : ' + str(self.start_date) + ' - ' + str(self.end_date) + '\n' + plan