import pygame
import time
import random
import json
import numpy as np
from threading import Timer, Event

pygame.init()

display_width = 600
display_height = 1000

black = (0,0,0)
grey = (80, 80, 80)
white = (255,255,255)

stickman = pygame.image.load('stickman.png')
stickman_up = pygame.image.load('stickman_up.png')
stickman_down = pygame.image.load('stickman_down.png')

stickman_scaled = pygame.transform.scale(stickman, (40, 80))
stickman_up_scaled = pygame.transform.scale(stickman_up, (40, 80))
stickman_down_scaled = pygame.transform.scale(stickman_down, (40, 80))

window = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Base Algorithm')
clock = pygame.time.Clock()

def generate_random_requests(floors):
    global request_number
    floor_from = random.randrange(floors)
    floor_to = random.randrange(floors)
    while floor_to == floor_from:
        floor_to = random.randrange(floors)
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

    requests_on_floor[floor_from].append(request['direction'])
    
    #print(json.dumps(requests, indent=1))
    Timer(random.randrange(0, 2), generate_random_requests, args=[floors]).start()

floors = 5
current_floor = 0
floors_visited = 0

lift_width = 220
lift_height = 100
lift_pos_x = 0
lift_pos_y = display_height - lift_height - 10
lift_speed = 3
lift_capacity = 0

requests = {}
requests_served = {}
request_number = 0
direction = 'up'
lift_volume = {}

requests_on_floor = []
for i in range(floors):
    requests_on_floor.append([i])

gameExit = False

generate_random_requests(floors)

while not gameExit:

    #print(current_floor, direction, requests_on_floor, lift_capacity, lift_volume)
    
    #print(lift_volume)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    window.fill(grey)
    floor_height = display_height / floors
    for i in range(floors):
        pygame.draw.rect(window, black, [lift_pos_x+lift_width, (floor_height*i-1)+floor_height-10, display_width, 10])

    for floor in requests_on_floor:
        floor_spacing = 0
        for i in range(1, len(floor)):
            if floor[i] == 'up':
                window.blit(stickman_up_scaled, (lift_pos_x + lift_width + 10 + floor_spacing, display_height - int(floor[0]) * floor_height - stickman_up_scaled.get_rect().size[1] - 10))
            else:
                window.blit(stickman_down_scaled, (lift_pos_x + lift_width + 10 + floor_spacing, display_height - int(floor[0]) * floor_height - stickman_down_scaled.get_rect().size[1] - 10))
            floor_spacing += 35

    lift_spacing = 0
    for request in list(lift_volume):
        if lift_volume[request]['direction'] == 'up':
            window.blit(stickman_up_scaled, (lift_pos_x + lift_spacing, lift_pos_y + lift_height - stickman_scaled.get_rect().size[1]))
        else:
            window.blit(stickman_down_scaled, (lift_pos_x + lift_spacing, lift_pos_y + lift_height - stickman_scaled.get_rect().size[1]))
        lift_spacing += 35


    pygame.draw.rect(window, white, [lift_pos_x + lift_width, 0, 10, display_height])
    pygame.draw.rect(window, white, [lift_pos_x, lift_pos_y, lift_width, lift_height], 10)
    pygame.draw.line(window, white, (lift_width / 2, 0), (lift_width / 2, lift_pos_y), 3)


    lift_pos_y += lift_speed

    if lift_pos_y + lift_height > display_height - 10:
        lift_speed = lift_speed * -1

    if lift_pos_y + lift_height < floor_height - 10:
        lift_speed = lift_speed * -1
    
    pygame.display.update()
    clock.tick(60)
    

    """
    if direction == 'up' and (lift_pos_y + lift_height) < ((floors - current_floor) * floor_height) - floor_height:
        current_floor += 1
        floors_visited += 1
        for request in requests:
            requests[request]['wait'] += 1

    elif direction == 'down' and (lift_pos_y + lift_height) > ((floors - current_floor + 1) * floor_height - 10):
        current_floor -= 1
        floors_visited += 1
        for request in requests:
            requests[request]['wait'] += 1
    """
    
    for floor in range(floors):
        if (lift_pos_y + lift_height) < display_height - int(floor * floor_height) and (lift_pos_y + lift_height) > display_height - int(floor * floor_height) - 10:
            current_floor = floor
        elif current_floor == floor:
            current_floor = None

    if lift_pos_y + lift_height > display_height - 10:
        direction = 'up'
    if lift_pos_y + lift_height < floor_height:
        direction = 'down'
    
    for request in list(requests):
        if requests[request]['floor_from'] == current_floor and requests[request]['direction'] == direction and lift_capacity < 6:
            key_list = list(requests.keys()) 
            val_list = list(requests.values()) 
            lift_volume[key_list[val_list.index(requests[request])]] = requests[request]
            if direction == 'up':
                requests_on_floor[int(requests[request]['floor_from'])].remove('up')
            else:
                requests_on_floor[int(requests[request]['floor_from'])].remove('down')
            
            del requests[request]
            lift_capacity += 1

    for request in list(lift_volume):
        if lift_volume[request]['floor_to'] == current_floor:
            requests_served[request_number] = lift_volume[request]
            del lift_volume[request]
            lift_capacity -= 1

    time.sleep(0.01)


pygame.quit()
quit()