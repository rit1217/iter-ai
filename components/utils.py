from datetime import datetime, time
from components.constants import *
import math


def to_minute(t):
    return ((t.hour * 60 + t.minute) * 60 + t.second) // 60


def add_time(t1, t2):
    minute = to_minute(t1) + to_minute(t2)
    return time(minute // 60, minute % 60)


def str_to_datetime(instr):
    return datetime.strptime(instr, DATETIME_FORMAT)


def str_to_time(instr):

    if instr == 'closed':
        instr = "00:00:00"
    elif len(instr) < 7:
        instr += ":00"

    dt = datetime.strptime(instr, TIME_FORMAT)
    return time(dt.hour, dt.minute, dt.second)


def sphericalDistance(lat1, lon1, lat2, lon2 ) :
    if (lat1 == lat2) and (lon1 == lon2):
        return 0
    
    else:
        radlat1 = math.pi * lat1/180
        radlat2 = math.pi * lat2/180
        theta = lon1-lon2
        radtheta = math.pi * theta/180
        dist = math.sin(radlat1) * math.sin(radlat2) + math.cos(radlat1) * math.cos(radlat2) * math.cos(radtheta)
        dist = 1 if dist > 1 else dist

        dist = math.acos(dist)
        dist = dist * 180/math.pi
        dist = dist * 60 * 1.1515
        return dist * 1.609344 
        

def nearest_place(lst1, lst2):
    lat = [ place['latitude'] for place in lst1]
    lng = [ place['longitude'] for place in lst1]

    center = { 'latitude': min(lat) + ((max(lat) - min(lat)) / 2),
              'longitude': min(lng) + ((max(lng) - min(lng)) / 2)}

    nearest_place = lst2[0]
    best_dist = sphericalDistance(center['latitude'], center['longitude'],
                                   nearest_place['latitude'], nearest_place['longitude'] )
    for place in lst2[1:]:
        dist = sphericalDistance(center['latitude'], center['longitude'],
                            place['latitude'], place['longitude'] )
        if dist < best_dist:
            nearest_place = place
            best_dist = dist

    return nearest_place


def row_to_dict(row):
    return row.to_dict()


def process_strings(strings):
    whitelist = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&')
    processed_strings = []
    for string in strings:
        processed_strings.append(''.join(filter(whitelist.__contains__, string)).rstrip().lower())
    
    return processed_strings
