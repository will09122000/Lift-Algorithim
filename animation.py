import pygame
import time
import random
import json
from threading import Timer, Event

pygame.init()

display_width = 600
display_height = 1000

black = (0,0,0)
grey = (80, 80, 80)
white = (255,255,255)

floors = 4

stickman = pygame.image.load('stickman.png')

window = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Base Algorithm')
clock = pygame.time.Clock()

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()


def generate_random_requests(floors):
    global request_number
    floor_from = random.randrange(0, floors)
    floor_to = random.randrange(0, floors)
    while floor_to == floor_from:
        floor_to = random.randrange(0, floors)
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
    Timer(random.randrange(0, 10), generate_random_requests, args=[floors]).start()

floors = 4
current_floor = 0

lift_width = 100
lift_height = 150
lift_pos_x = 0
lift_pos_y = display_height - lift_height - 10
lift_speed = 2
lift_capacity = 6

requests = {}
request_number = 0
direction = 'up'
lift_volume = {}
requests_served = {}

gameExit = False

generate_random_requests(floors)

while not gameExit:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    window.fill(grey)
    floor_height = display_height / floors
    for i in range(floors):
        pygame.draw.rect(window, black, [lift_pos_x+lift_width, (floor_height*i-1)+floor_height-10, display_width, 10])

    for request in list(requests):
        print(int(requests[request]['floor_from']))
        window.blit(pygame.transform.scale(stickman, (30, 45)), (lift_pos_x + lift_width + 10, display_height - int(requests[request]['floor_from']) * floor_height - 45 - 10))


    pygame.draw.rect(window, white, [lift_pos_x + lift_width, 0, 10, display_height])
    pygame.draw.rect(window, white, [lift_pos_x, lift_pos_y, lift_width, lift_height], 10)

    lift_pos_y += lift_speed

    if lift_pos_y + lift_height > display_height - 10:
        lift_speed = lift_speed * - 1

    if lift_pos_y + lift_height < floor_height:
        lift_speed = lift_speed * - 1
    
    pygame.display.update()
    clock.tick(60)
    
    if direction == 'up' and (lift_pos_y + lift_height) < ((floors - current_floor) * floor_height) - floor_height:
        current_floor += 1
        direction = 'up'
    elif direction == 'down' and (lift_pos_y + lift_height) > ((floors - current_floor) * floor_height):
        current_floor -= 1
        direction = 'down'

    if lift_pos_y + lift_height > display_height - 10:
        direction = 'up'
    if lift_pos_y+lift_height < floor_height:
        direction = 'down'
    #print(current_floor, direction, (lift_pos_y + lift_height), ((floors - current_floor) * floor_height) - floor_height)
    

    for request in list(requests):
        if requests[request]['floor_from'] == current_floor and requests[request]['direction'] == direction and lift_capacity < 7:
            lift_volume[request_number] = requests[request]
            del requests[request]
            lift_capacity += 1

    for request in list(lift_volume):
        if lift_volume[request]['floor_to'] == current_floor:
            requests_served[request_number] = lift_volume[request]
            del lift_volume[request]
            lift_capacity -= 1

    for request in requests:
        requests[request]['wait'] += 1

    #time.sleep(0.1)


pygame.quit()
quit()