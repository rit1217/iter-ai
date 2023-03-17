class Place:

    def __init__(self, place_name, category, lat, lng, introduction, detail, dest, open_time, close_time):
        self.place_name = place_name
        self.category = category
        self.latitude = lat
        self.longitude = lng
        self.introduction = introduction
        self.detail = detail
        self.destination = dest
        self.open_time = open_time
        self.close_time = close_time

    def __str__(self):
        return self.place_name