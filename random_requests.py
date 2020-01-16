import time
import random
import json
from threading import Timer, Event

def generate_random_requests(number_of_floors):
    global request_number
    floor_from = random.randrange(0, number_of_floors)
    floor_to = random.randrange(0, number_of_floors)
    while floor_to == floor_from:
        floor_to = random.randrange(0, number_of_floors)
    if (floor_from - floor_to) < 0:
        direction = 'up'
    else:
        direction = 'down'

    request = {
        'floor_from': floor_from,
        'floor_to': floor_to,
        'direction': direction,
        'wait': 0
    }

    requests[request_number] = request
    request_number += 1
    
    #print(json.dumps(requests, indent=1))
    Timer(random.randrange(0, 10), generate_random_requests, args=[number_of_floors]).start()


requests = {}
request_number = 0
floors = 5
lift_capacity = 6
floor = 0
direction = 'up'
lift_volume = {}
requests_served = {}

#done = Event()
#Timer(random.randrange(0, 10), generate_random_requests, args=[number_of_floors]).start()
#done.set()
#generate_random_requests(number_of_floors)
"""
while True:
    if floor == 0:
        direction = 'up'
    if floor == number_of_floors - 1:
        direction = 'down'
    if direction == 'up':
        floor += 1
    else:
        floor -= 1

    for request in list(requests):
        if requests[request]['floor_from'] == floor and requests[request]['direction'] == direction and lift_capacity < 7:
            lift_volume[request_number] = requests[request]
            del requests[request]
            lift_capacity += 1

    for request in list(lift_volume):
        if lift_volume[request]['floor_to'] == floor:
            requests_served[request_number] = lift_volume[request]
            del lift_volume[request]
            lift_capacity -= 1

    for request in requests:
        requests[request]['wait'] += 1

    print(requests_served)
    time.sleep(1)
    print(floor)
"""

generate_random_requests(floors)