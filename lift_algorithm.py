import os
import pygame
import pygameMenu
import time
import random
import json
import csv
from threading import Timer, Event

# Colours
COLOUR_BLACK = (0, 0, 0)
COLOUR_WHITE = (255, 255, 255)
COLOUR_BACKGROUND = (66, 66, 66)
COLOR_MENU_BACKGROUND = (128, 128, 128)
COLOUR_MENU_TITLE = (238, 154, 23)
COLOUR_RED = (255, 51, 51)

# Window setup
WINDOW_SIZE = (850, 1000)
Algorithm = ['BASE']
FPS = 60.0
clock = None
main_menu = None
surface = None
pygame.init()

# Graphics Variables
stickman_up = pygame.image.load('stickman_up.png')
stickman_down = pygame.image.load('stickman_down.png')
stickman_up_scaled = pygame.transform.scale(stickman_up, (40, 80))
stickman_down_scaled = pygame.transform.scale(stickman_down, (40, 80))
large_font = pygame.font.Font(pygameMenu.font.FONT_BEBAS, 30)
small_font = pygame.font.Font(pygameMenu.font.FONT_BEBAS, 22)
lift_width = 220
lift_height = 100
lift_pos_x = 0

def load_config():
    """
    Load simulation configuration from config.json
    return: None
    """
    global floors
    global spawn_rate
    global lift_speed

    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    floors = config['floors']
    spawn_rate = config['spawn_rate']
    lift_speed = config['lift_speed']

    if spawn_rate == 1:
        spawn_rate = 6
    elif spawn_rate == 2:
        spawn_rate = 5
    elif spawn_rate == 3:
        spawn_rate = 4
    elif spawn_rate == 4:
        spawn_rate = 3
    elif spawn_rate == 5:
        spawn_rate = 2

def change_algorithm(value, algorithm):
    """
    Change the algorithm for the simulation to run
    return: None
    """
    selected, index = value
    Algorithm[0] = algorithm

def change_floors(value, new_floors):
    """
    Change the total number of floors on the simulation
    return: Load config function
    """
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    config['floors'] = new_floors

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=2)
    return load_config()

def change_spawn_rate(value, new_spawn_rate):
    """
    Change the rate at which requests are spawned
    return: Load config function
    """
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    config['spawn_rate'] = new_spawn_rate

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=2)
    return load_config()

def change_lift_speed(value, new_lift_speed):
    """
    Change the speed of the lift.
    return: Load config function
    """
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    config['lift_speed'] = new_lift_speed

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=2)
    return load_config()

def algorithm_selector():
    """
    Runs specific algorithm dependent on the value of Algorithm[0]
    return: Algorithm function
    """
    if Algorithm[0] == 'BASE':
        return base_algorithm_run()
    else:
        return improved_algorithm_run()

def main_background():
    """
    Function used by menus to fill the background with colour
    return: None
    """
    global surface
    surface.fill(COLOUR_BACKGROUND)

def generate_random_requests(floors, spawn_rate):
    """
    Function responsible for generating random requests. Each request
    is from a random floor, a random direction and a random destination
    floor. The rate at which the requests are spawned is random using a
    timer with a range of integers from 0 to the spawn rate. So the lower
    the spawn rate integer the higher rate of requests are spawned on
    average.
    return: None
    """
    global sim_exit
    global request_number
    global requests
    floor_from = random.randrange(floors)
    floor_to = random.randrange(floors)

    # Prevent the two floors from being the same.
    while floor_to == floor_from:
        floor_to = random.randrange(floors)
    
    # Declare the direction the request is going.
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
    requests_each_floor[floor_from].append(request['direction'])

    if not sim_exit:
        exit()
    else:
        Timer(random.randrange(0, spawn_rate), generate_random_requests,
              args=[floors, spawn_rate]).start()

def save_stat_data(algorithm, avg_wait, floors):
    """
    This function is executed when the user exits a running simulation.
    The number of floors and the average wait time for all requests
    are appened to the appropriate csv file to be exported to Google
    Sheets to generate charts.
    return: None
    """
    new_line = [floors, avg_wait]

    if algorithm == 'base':
        file_name = 'base_stat_data.csv'
    else:
        file_name = 'improved_stat_data.csv'
    
    with open(file_name, 'a+', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(new_line)

def base_algorithm_run():
    """
    The basic algorithm wherby the lift starts from the bottom floor and
    continually travels to the top floor and back down to the ground
    floor, picking up requests if they are heading the same direction as
    the lift and the lift is not full.
    returns: None
    """

    global sim_exit
    global requests
    global request_number
    global requests_each_floor
    global floors
    global spawn_rate
    global lift_speed

    main_menu.disable()
    main_menu.reset(1)

    # Window configuration.
    running = True
    sim_exit = True
    pygame.init()
    clock = pygame.time.Clock()
    window = pygame.display.set_mode((WINDOW_SIZE[0],WINDOW_SIZE[1]))
    pygame.display.set_caption('Lift Algorithm')
    
    lift_pos_y = WINDOW_SIZE[1] - lift_height - 10
    lift_capacity = 0
    requests = {}
    requests_served = {}
    request_number = 0
    direction = 'up'
    lift_volume = {}
    current_floor = 0
    floors_visited = 0

    previous_floors = None
    previous_lift_position = WINDOW_SIZE[1]
    lift_distance = 0
    floors_travelled = 0
    
    # Creates a list of floors which will be used when displaying the
    # stickmen as they are waiting on a floor.
    requests_each_floor = []
    for i in range(floors):
        requests_each_floor.append([i])

    # Starts the spawning of requests on a new thread.
    Timer(random.randrange(0, spawn_rate), generate_random_requests,
          args=[floors, spawn_rate]).start()

    # Main loop
    while sim_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # Exiting simulation with escape key.
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and main_menu.is_disabled():
                    save_stat_data("base", avg_wait, floors)
                    sim_exit = False
                    main_menu.enable()
                    return
            # Exiting simulation with quit button.
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_pos[0] > WINDOW_SIZE[0] - 110 and mouse_pos[0] < WINDOW_SIZE[0] - 10:
                    if mouse_pos[1] > WINDOW_SIZE[1] - 60 and mouse_pos[1] < WINDOW_SIZE[1] - 10:
                        save_stat_data("base", avg_wait, floors)
                        sim_exit = False
                        main_menu.enable()
                        return

        # Pass events to main_menu
        main_menu.mainloop(event)
        mouse_pos = pygame.mouse.get_pos()

        window.fill(COLOR_MENU_BACKGROUND)
        
        # Drawing black horizontal lines to represent each floor of the building.
        floor_height = WINDOW_SIZE[1] / floors
        for i in range(floors):
            floor_text = large_font.render(str(floors - i - 1), True, COLOUR_BLACK)
            window.blit(floor_text, (lift_pos_x + lift_width + 12, floor_height * i))
            pygame.draw.rect(window, COLOUR_BLACK,
                             [lift_pos_x + lift_width, (floor_height * i) + floor_height - 10,
                              (lift_pos_x + lift_width) * 1.5, 10])

        # Drawing stickmen on each floor when requests spawn.
        for floor in requests_each_floor:
            floor_spacing = 0
            for i in range(1, len(floor)):
                if floor[i] == 'up':
                    window.blit(stickman_up_scaled,
                                (lift_pos_x + lift_width + 10 + floor_spacing,
                                 WINDOW_SIZE[1] - int(floor[0]) * floor_height - stickman_up_scaled.get_rect().size[1] - 10))
                else:
                    window.blit(stickman_down_scaled,
                                (lift_pos_x + lift_width + 10 + floor_spacing,
                                 WINDOW_SIZE[1] - int(floor[0]) * floor_height - stickman_down_scaled.get_rect().size[1] - 10))
                floor_spacing += 35

        # Drawing stickmen in the lift when they are picked up.
        lift_spacing = 0
        for request in list(lift_volume):
            if lift_volume[request]['direction'] == 'up':
                window.blit(stickman_up_scaled,
                            (lift_pos_x + lift_spacing,
                             lift_pos_y + lift_height - stickman_up_scaled.get_rect().size[1]))
            else:
                window.blit(stickman_down_scaled,
                            (lift_pos_x + lift_spacing,
                             lift_pos_y + lift_height - stickman_down_scaled.get_rect().size[1]))
            lift_spacing += 35

        # Drawing several lines such as the lift border, lift cables and building walls.
        pygame.draw.rect(window, COLOUR_MENU_TITLE,
                         [lift_width + (lift_pos_x + lift_width) * 1.5, 0,
                          WINDOW_SIZE[0] - lift_width + (lift_pos_x + lift_width), 150])
        pygame.draw.rect(window, COLOUR_WHITE,
                         [0, 0, 5, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE,
                        [lift_pos_x + lift_width, 0, 10, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE,
                         [lift_width + (lift_pos_x + lift_width) * 1.5, 0, 10, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE,
                         [lift_pos_x, lift_pos_y, lift_width, lift_height], 10)
        pygame.draw.line(window, COLOUR_WHITE,
                         (lift_width / 2, 0), (lift_width / 2, lift_pos_y), 3)
        pygame.draw.line(window, COLOUR_WHITE,
                         (lift_width / 2, lift_pos_y + lift_height), (lift_width / 2, WINDOW_SIZE[1]), 3)
        pygame.draw.rect(window, COLOUR_RED,
                         [WINDOW_SIZE[0] - 110, WINDOW_SIZE[1] - 60, 100, 50])

        # Quit button
        quit_text = large_font.render('QUIT', True, COLOUR_BLACK)
        window.blit(quit_text, (WINDOW_SIZE[0] - 87, WINDOW_SIZE[1] - 58))

        # Algorithm title
        title_text = large_font.render('Base  Algorithm', True, COLOUR_BLACK)
        window.blit(title_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 0))

        # Displays the total requests served during the current simulation.
        requests_served_text = small_font.render('Requests  served:  ' +
                                                 str(len(list(requests_served))), True, COLOUR_BLACK)
        window.blit(requests_served_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 50))

        # Calculates the average wait time of each request served.
        total_wait = 0
        for request in requests_served:
            total_wait += requests_served[request]['wait']
        try:
            avg_wait = total_wait / len(list(requests_served))
            avg_wait = round(avg_wait, 2)
        except ZeroDivisionError:
            avg_wait = 0

        # Displays the average wait time of each request during the current simulation.
        avg_wait_text = small_font.render('Average  wait  time:  ' +
                                          str(avg_wait), True, COLOUR_BLACK)
        window.blit(avg_wait_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 100))

        # Moves the lift a distance of 'lift_speed' pixels.
        lift_pos_y += lift_speed
        # Keeps track of the total distance moved by the lift.
        lift_distance += abs((lift_pos_y+lift_height) - previous_lift_position)
        # Keeps track of the total number of floors travelled by the lift
        # used to calculate the wait time of each request.
        floors_travelled = int((lift_distance/(WINDOW_SIZE[1] - floor_height + 25)) * floors)
        
        # If the lift is at the bottom floor, change the direction of the lift.
        if lift_pos_y + lift_height > WINDOW_SIZE[1] - 10:
            lift_speed = lift_speed * -1
            direction = 'up'

        # If the lift is at the top floor, change the direction of the lift.
        if lift_pos_y + lift_height < floor_height - 10:
            lift_speed = lift_speed * -1
            direction = 'down'

        # Keeps 'current_floor' to the value of floor the lift is
        # currently at including 'None' if the lift is betwee floors.
        for floor in range(floors):
            if (lift_pos_y + lift_height) < WINDOW_SIZE[1] - int(floor * floor_height) + 20 and \
            (lift_pos_y + lift_height) > WINDOW_SIZE[1] - int(floor * floor_height) - 10 - 20:
                current_floor = floor
            elif current_floor == floor:
                current_floor = None

        # Add an extra floor to all requests waiting and in the lift if
        # the lift has reached a new floor.
        if previous_floors:
            if previous_floors != floors_travelled:
                for request in requests:
                    requests[request]['wait'] += 1
                for request in lift_volume:
                    lift_volume[request]['wait'] += 1

        # Moves a request from a floor to the lift if it's possible and suitable.
        for request in list(requests):
            if requests[request]['floor_from'] == current_floor and \
            requests[request]['direction'] == direction and \
            lift_capacity < 6:
                key_list = list(requests.keys()) 
                val_list = list(requests.values()) 
                lift_volume[key_list[val_list.index(requests[request])]] = requests[request]
                if direction == 'up':
                    requests_each_floor[int(requests[request]['floor_from'])].remove('up')
                else:
                    requests_each_floor[int(requests[request]['floor_from'])].remove('down')
                del requests[request]
                lift_capacity += 1

        # Moves a request from the lift to a store of all requests served if they have reached their
        # requested floor.
        for request in list(lift_volume):
            if lift_volume[request]['floor_to'] == current_floor:
                requests_served[request_number] = lift_volume[request]
                del lift_volume[request]
                lift_capacity -= 1

        # Keeps track of the previous lift position to be able to calculate the total lift distance.
        previous_lift_position = lift_pos_y + lift_height
        # Keeps track of the previous floor the lift was at in order to add to the wait time of
        # each request correctly.
        previous_floors = floors_travelled

        pygame.display.update()
        clock.tick(60)

def improved_algorithm_run():
    """
    The improved algorithm wherby the lift starts from the bottom floor. While there are no
    requests on any floor or in the lift, the lift will travel to the middle floor and wait
    there for requests to be in the optimal position pending a new request on a random floor.
    When a requests spawns and the lift is empty, the lift will travel to the request that has
    been waiting the longest picking up any requests heading in the same direction as the lift.
    The lift will then travel to destination floor of that request also picking up any heading
    in the same direction as the lift.
    returns: None
    """

    global sim_exit
    global requests
    global request_number
    global requests_each_floor
    global floors
    global spawn_rate
    global lift_speed

    main_menu.disable()
    main_menu.reset(1)

    # Window configuration.
    running = True
    sim_exit = True
    pygame.init()
    clock = pygame.time.Clock()
    window = pygame.display.set_mode((WINDOW_SIZE[0],WINDOW_SIZE[1]))
    pygame.display.set_caption('Lift Algorithm')  
    
    lift_pos_y = WINDOW_SIZE[1] - lift_height - 10
    original_lift_speed = lift_speed
    lift_speed = -lift_speed
    lift_capacity = 0
    requests = {}
    requests_served = {}
    request_number = 0
    direction = 'up'
    lift_volume = {}
    current_floor = 0
    floors_visited = 0

    previous_floors = None
    previous_lift_position = WINDOW_SIZE[1]
    lift_distance = 0
    floors_travelled = 0

    # Creates a list of floors which will be used when displaying the
    # stickmen as they are waiting on a floor.
    requests_each_floor = []
    for i in range(floors):
        requests_each_floor.append([i])

    # Starts the spawning of requests on a new thread.
    Timer(random.randrange(0, spawn_rate), generate_random_requests,
          args=[floors, spawn_rate]).start()

    floor_from = None
    # Main loop
    while sim_exit:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # Exiting simulation with escape key.
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and main_menu.is_disabled():
                    save_stat_data("improved", avg_wait, floors)
                    sim_exit = False
                    main_menu.enable()
                    return
            # Exiting simulation with quit button.
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_pos[0] > WINDOW_SIZE[0] - 110 and mouse_pos[0] < WINDOW_SIZE[0] - 10:
                    if mouse_pos[1] > WINDOW_SIZE[1] - 60 and mouse_pos[1] < WINDOW_SIZE[1] - 10:
                        save_stat_data("improved", avg_wait, floors)
                        sim_exit = False
                        main_menu.enable()
                        return

        # Pass events to main_menu
        main_menu.mainloop(event)
        mouse_pos = pygame.mouse.get_pos()

        window.fill(COLOR_MENU_BACKGROUND)
        
        # Drawing black horizontal lines to represent each floor of the building.
        floor_height = WINDOW_SIZE[1] / floors
        for i in range(floors):
            floor_text = large_font.render(str(floors - i - 1), True, COLOUR_BLACK)
            window.blit(floor_text, (lift_pos_x + lift_width + 12, floor_height*i))
            pygame.draw.rect(window, COLOUR_BLACK,
                             [lift_pos_x+lift_width, (floor_height*i)+floor_height-10,
                              (lift_pos_x + lift_width)*1.5, 10])

        # Drawing stickmen on each floor when requests spawn.
        for floor in requests_each_floor:
            floor_spacing = 0
            for i in range(1, len(floor)):
                if floor[i] == 'up':
                    window.blit(stickman_up_scaled,
                                (lift_pos_x + lift_width + 10 + floor_spacing,
                                 WINDOW_SIZE[1] - int(floor[0]) * floor_height - stickman_up_scaled.get_rect().size[1] - 10))
                else:
                    window.blit(stickman_down_scaled,
                                (lift_pos_x + lift_width + 10 + floor_spacing,
                                 WINDOW_SIZE[1] - int(floor[0]) * floor_height - stickman_down_scaled.get_rect().size[1] - 10))
                floor_spacing += 35

        # Drawing stickmen in the lift when they are picked up.
        lift_spacing = 0
        for request in list(lift_volume):
            if lift_volume[request]['direction'] == 'up':
                window.blit(stickman_up_scaled,
                            (lift_pos_x + lift_spacing,
                             lift_pos_y + lift_height - stickman_up_scaled.get_rect().size[1]))
            else:
                window.blit(stickman_down_scaled,
                            (lift_pos_x + lift_spacing,
                             lift_pos_y + lift_height - stickman_down_scaled.get_rect().size[1]))
            lift_spacing += 35

        # Drawing several lines such as the lift border, lift cables and building walls.
        pygame.draw.rect(window, COLOUR_MENU_TITLE,
                         [lift_width + (lift_pos_x + lift_width) * 1.5, 0,
                          WINDOW_SIZE[0] - lift_width + (lift_pos_x + lift_width), 150])
        pygame.draw.rect(window, COLOUR_WHITE,
                         [0, 0, 5, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE,
                         [lift_pos_x + lift_width, 0, 10, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE,
                         [lift_width + (lift_pos_x + lift_width) * 1.5, 0, 10, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE,
                         [lift_pos_x, lift_pos_y, lift_width, lift_height], 10)
        pygame.draw.line(window, COLOUR_WHITE,
                         (lift_width / 2, 0), (lift_width / 2, lift_pos_y), 3)
        pygame.draw.line(window, COLOUR_WHITE,
                         (lift_width / 2, lift_pos_y + lift_height), (lift_width / 2, WINDOW_SIZE[1]), 3)
        pygame.draw.rect(window, COLOUR_RED,
                         [WINDOW_SIZE[0] - 110, WINDOW_SIZE[1] - 60, 100, 50])

        # Quit button
        quit_text = large_font.render('QUIT', True, COLOUR_BLACK)
        window.blit(quit_text, (WINDOW_SIZE[0] - 87, WINDOW_SIZE[1] - 58))

        # Algorithm title
        title_text = large_font.render('Improved  Algorithm', True, COLOUR_BLACK)
        window.blit(title_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 0))

        # Displays the total requests served during the current simulation.
        requests_served_text = small_font.render('Requests  served:  ' +
                                                 str(len(list(requests_served))), True, COLOUR_BLACK)
        window.blit(requests_served_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 50))

        # Calculates the average wait time of each request served.
        total_wait = 0
        for request in requests_served:
            total_wait += requests_served[request]['wait']
        try:
            avg_wait = total_wait / len(list(requests_served))
            avg_wait = round(avg_wait, 2)
        except ZeroDivisionError:
            avg_wait = 0
        
        # Displays the average wait time of each request during the current simulation.
        avg_wait_text = small_font.render('Average  wait  time:  ' +
                                          str(avg_wait), True, COLOUR_BLACK)
        window.blit(avg_wait_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 100))

        # Moves the lift a distance of 'lift_speed' pixels.
        lift_pos_y += lift_speed
        # Keeps track of the total distance moved by the lift.
        lift_distance += abs((lift_pos_y+lift_height) - previous_lift_position)
        # Keeps track of the total number of floors travelled by the lift
        # used to calculate the wait time of each request.
        floors_travelled = int((lift_distance/(WINDOW_SIZE[1] - floor_height + 25)) * floors)

        # If the lift is empty
        if lift_capacity == 0:
            # If there are requests waiting on any floor.
            if requests:
                # Move to the direction of the floor with the request that has been waiting
                # the longest.
                next_request = min(list(requests.keys()))
                floor_to = requests[next_request]['floor_from']
            # If there are no requests, start moving towards the middle floor.
            else:
                floor_to = floors // 2
        # If there are requests in the lift, move in the direction of the floor with the request
        # in the lift that has been waiting the longest.
        else:
            dest = min(list(lift_volume.keys()))
            floor_to = lift_volume[dest]['floor_to']

        # If the lift as at a floor, assign 'floor_from' to that same floor number.
        try:
            if current_floor >= 0:
                floor_from = current_floor
        except:
            pass

        # If the lift is below the floor it needs to go to, change the direction of the lift to up.
        if floor_from < floor_to:
            lift_speed = -original_lift_speed
            direction = 'up'

        # If the lift is above the floor it needs to go to, change the direction of the lift to down.
        if floor_from > floor_to:
            lift_speed = original_lift_speed
            direction = 'down'

        # If the lift has reached its destination floor and there are no requests to serve, wait at
        # that floor (only occurs when lift has reached the middle floor with no new requests),
        if floor_from == floor_to and not requests:
            lift_speed = 0
            direction = 'none'

        # Keeps 'current_floor' to the value of floor the lift is
        # currently at including 'None' if the lift is betwee floors.
        for floor in range(floors):
            if (lift_pos_y + lift_height) < WINDOW_SIZE[1] - int(floor * floor_height) + 20 and \
            (lift_pos_y + lift_height) > WINDOW_SIZE[1] - int(floor * floor_height) - 10 - 20:
                current_floor = floor
            elif current_floor == floor:
                current_floor = None

        # Add an extra floor to all requests waiting and in the lift if
        # the lift has reached a new floor.
        if previous_floors:
            if previous_floors != floors_travelled:
                for request in requests:
                    requests[request]['wait'] += 1
                for request in lift_volume:
                    lift_volume[request]['wait'] += 1

        # Moves a request from a floor to the lift if it's possible and suitable.
        for request in list(requests):
            if (requests[request]['floor_from'] == current_floor and \
            (requests[request]['direction'] == direction or direction == 'none' or lift_capacity == 0) and \
            lift_capacity < 6):
                key_list = list(requests.keys()) 
                val_list = list(requests.values()) 
                lift_volume[key_list[val_list.index(requests[request])]] = requests[request]
                if direction == 'up':
                    try:
                        requests_each_floor[int(requests[request]['floor_from'])].remove('up')
                    except:
                        requests_each_floor[int(requests[request]['floor_from'])].remove('down')
                elif direction == 'down':
                    try:
                        requests_each_floor[int(requests[request]['floor_from'])].remove('down')
                    except:
                        requests_each_floor[int(requests[request]['floor_from'])].remove('up')
                else:
                    try:
                        requests_each_floor[int(requests[request]['floor_from'])].remove('down')
                    except:
                        requests_each_floor[int(requests[request]['floor_from'])].remove('up')
                    
                del requests[request]
                lift_capacity += 1

        # Moves a request from the lift to a store of all requests served if they have reached
        # their requested floor.
        for request in list(lift_volume):
            if lift_volume[request]['floor_to'] == current_floor:
                requests_served[request_number] = lift_volume[request]
                del lift_volume[request]
                lift_capacity -= 1

        # Keeps track of the previous lift position to be able to calculate the total lift distance.
        previous_lift_position = lift_pos_y + lift_height
        # Keeps track of the previous floor the lift was at in order to add to the wait time of
        # each request correctly.
        previous_floors = floors_travelled

        pygame.display.update()
        clock.tick(60)

def main():
    """
    Main function used to display the GUI. The GUI can be used to configure the simulation settings
    including the number of the floors, the request spawn rate and the speed of the lift. The GUI
    can also be used select which algorithm to run and then can be used to start a simulation.

    return: None
    """

    global clock
    global main_menu
    global surface

    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # Create pygame screen and objects
    surface = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Lift Algorithm')
    clock = pygame.time.Clock()
    load_config()

    # select algorithm and start simulation menu
    select_menu = pygameMenu.Menu(surface,
                                bgfun=main_background,
                                color_selected=COLOUR_WHITE,
                                font=pygameMenu.font.FONT_BEBAS,
                                font_color=COLOUR_BLACK,
                                font_size=30,
                                menu_alpha=100,
                                menu_color=COLOR_MENU_BACKGROUND,
                                menu_color_title=COLOUR_MENU_TITLE,
                                menu_height=int(WINDOW_SIZE[1] * 0.6),
                                menu_width=int(WINDOW_SIZE[0] * 0.6),
                                onclose=pygameMenu.events.DISABLE_CLOSE,
                                option_shadow=False,
                                title='Select  Algorithm',
                                window_height=WINDOW_SIZE[1],
                                window_width=WINDOW_SIZE[0]
                                )

    # Runs 'algorithm_selector' function when the 'Start' button is pressed.
    select_menu.add_option('Start',
                         algorithm_selector)

    # Runs 'change_algorithm' function when the 'Select  Algorithm' selector is changed.
    select_menu.add_selector('Select  Algorithm',
                           [('Base', 'BASE'),
                            ('Improved', 'IMPROVED')],
                           onchange=change_algorithm)
    
    # Opens previous menu when the 'Back' button is pressed.
    select_menu.add_option('Back', pygameMenu.events.BACK)

    # Settings menu to configure simulation settings.
    settings_menu = pygameMenu.TextMenu(surface,
                                     bgfun=main_background,
                                     color_selected=COLOUR_WHITE,
                                     font=pygameMenu.font.FONT_BEBAS,
                                     font_color=COLOUR_BLACK,
                                     font_size=30,
                                     menu_alpha=100,
                                     menu_color=COLOR_MENU_BACKGROUND,
                                     menu_color_title=COLOUR_MENU_TITLE,
                                     menu_height=int(WINDOW_SIZE[1] * 0.6),
                                     menu_width=int(WINDOW_SIZE[0] * 0.6),
                                     onclose=pygameMenu.events.DISABLE_CLOSE,
                                     option_shadow=False,
                                     text_color=COLOUR_BLACK,
                                     text_fontsize=20,
                                     title='Settings',
                                     window_height=WINDOW_SIZE[1],
                                     window_width=WINDOW_SIZE[0]
                                     )

    # Runs 'change_floors' function when the 'Number of Floors' selector is changed.
    settings_menu.add_selector('Number  of  Floors', [('2',2),('3',3),('4',4),('5',5),('6',6),
                                                      ('7',7),('8',8),('9',9),('10',10),('11',11),
                                                      ('12',12),('13',13),('14',14),('15',15),
                                                      ('16',16),('17',17),('18',18),('19',19),
                                                      ('20',20), ('21',21), ('22',22),('23',23),
                                                      ('24',24),('25',25),('26',26), ('27',27),
                                                      ('28',28),('29',29),('30',30)],
                                                      onchange=change_floors)

    # Runs 'change_spawn_rate' function when the 'Request Spawn Rate' selector is changed.
    settings_menu.add_selector('Request  Spawn  Rate', [('1',1), ('2',2),('3',3),('4',4),('5',5)],
                                                        onchange=change_spawn_rate)
    
    # Runs 'change_lift_speed' function when the 'Lift Speed' selector is changed.
    settings_menu.add_selector('Lift  Speed', [('5',5),('10',10),('15',15),('20',20)],
                                                        onchange=change_lift_speed)
    
    # Opens previous menu when the 'Back' button is pressed.
    settings_menu.add_option('Back', pygameMenu.events.BACK)
    
    # Main menu
    main_menu = pygameMenu.Menu(surface,
                                bgfun=main_background,
                                color_selected=COLOUR_WHITE,
                                font=pygameMenu.font.FONT_BEBAS,
                                font_color=COLOUR_BLACK,
                                font_size=30,
                                menu_alpha=100,
                                menu_color=COLOR_MENU_BACKGROUND,
                                menu_color_title=COLOUR_MENU_TITLE,
                                menu_height=int(WINDOW_SIZE[1] * 0.6),
                                menu_width=int(WINDOW_SIZE[0] * 0.6),
                                onclose=pygameMenu.events.DISABLE_CLOSE,
                                option_shadow=False,
                                title='Main  menu',
                                window_height=WINDOW_SIZE[1],
                                window_width=WINDOW_SIZE[0]
                                )

    # Opens Select Algorithm menu when pressed.
    main_menu.add_option('Select  Algorithm', select_menu)
    # Opens Settings menu when pressed.
    main_menu.add_option('Settings', settings_menu)
    # Quits the program when pressed.
    main_menu.add_option('Quit', pygameMenu.events.EXIT)

    main_menu.set_fps(FPS)

    # Main loop
    while True:
        clock.tick(FPS)
        main_background()
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        main_menu.mainloop(events)
        pygame.display.flip()


if __name__ == '__main__':
    main()
