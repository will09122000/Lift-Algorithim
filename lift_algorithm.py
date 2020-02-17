import os
import pygame
import pygameMenu
import time
import random
import json
from threading import Timer, Event

# Colours
COLOUR_BLACK = (0, 0, 0)
COLOUR_WHITE = (255, 255, 255)
COLOUR_BACKGROUND = (66, 66, 66)
COLOR_MENU_BACKGROUND = (128, 128, 128)
COLOUR_MENU_TITLE = (238, 154, 23)
COLOUR_RED = (255, 51, 51)

WINDOW_SIZE = (850, 1000)
Algorithm = ['IMPROVED']
FPS = 60.0
clock = None
main_menu = None
surface = None
pygame.init()

stickman = pygame.image.load('stickman.png')
stickman_up = pygame.image.load('stickman_up.png')
stickman_down = pygame.image.load('stickman_down.png')
stickman_scaled = pygame.transform.scale(stickman, (40, 80))
stickman_up_scaled = pygame.transform.scale(stickman_up, (40, 80))
stickman_down_scaled = pygame.transform.scale(stickman_down, (40, 80))
large_font = pygame.font.Font(pygameMenu.font.FONT_BEBAS, 30)
small_font = pygame.font.Font(pygameMenu.font.FONT_BEBAS, 22)
lift_width = 220
lift_height = 100
lift_pos_x = 0

def load_config():
    global floors
    global spawn_rate
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    floors = config['floors']
    spawn_rate = config['spawn_rate']

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
    selected, index = value
    Algorithm[0] = algorithm

def change_floors(value, new_floors):
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    config['floors'] = new_floors

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=2)
    return load_config()

def change_spawn_rate(value, new_spawn_rate):
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    config['spawn_rate'] = new_spawn_rate

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=2)
    return load_config()

def algorithm_selector():
    if Algorithm[0] == 'BASE':
        return base_algorithm_run()
    else:
        return improved_algorithm_run()

def main_background():
    """
    Function used by menus, draw on background while menu is active.
    :return: None
    """
    global surface
    surface.fill(COLOUR_BACKGROUND)

def generate_random_requests(floors, spawn_rate):
    global sim_exit
    global request_number
    global requests
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
    requests_each_floor[floor_from].append(request['direction'])

    if not sim_exit:
        exit()
    else:
        Timer(random.randrange(0, spawn_rate), generate_random_requests, args=[floors, spawn_rate]).start()

def base_algorithm_run():

    global sim_exit
    global requests
    global request_number
    global requests_each_floor

    main_menu.disable()
    main_menu.reset(1)

    running = True
    sim_exit = True
    pygame.init()

    window = pygame.display.set_mode((WINDOW_SIZE[0],WINDOW_SIZE[1]))
    pygame.display.set_caption('Lift Algorithm')
    
    clock = pygame.time.Clock()

    lift_pos_y = WINDOW_SIZE[1] - lift_height - 10
    lift_speed = 10
    lift_capacity = 0

    requests = {}
    requests_served = {}
    request_number = 0
    direction = 'up'
    lift_volume = {}

    current_floor = 0
    floors_visited = 0

    requests_each_floor = []
    for i in range(floors):
        requests_each_floor.append([i])

    Timer(random.randrange(0, spawn_rate), generate_random_requests, args=[floors, spawn_rate]).start()

    while sim_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and main_menu.is_disabled():
                    sim_exit = False
                    main_menu.enable()
                    # Quit this function, then skip to loop of main-menu on line 317
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_pos[0] > WINDOW_SIZE[0] - 110 and mouse_pos[0] < WINDOW_SIZE[0] - 10:
                    if mouse_pos[1] > WINDOW_SIZE[1] - 60 and mouse_pos[1] < WINDOW_SIZE[1] - 10:
                        sim_exit = False
                        main_menu.enable()
                        return

        # Pass events to main_menu
        main_menu.mainloop(event)
        mouse_pos = pygame.mouse.get_pos()

        window.fill(COLOR_MENU_BACKGROUND)
        
        floor_height = WINDOW_SIZE[1] / floors
        for i in range(floors):
            floor_text = large_font.render(str(floors - i - 1), True, COLOUR_BLACK)
            window.blit(floor_text, (lift_pos_x + lift_width + 12, floor_height*i))
            pygame.draw.rect(window, COLOUR_BLACK, [lift_pos_x+lift_width, (floor_height*i)+floor_height-10, (lift_pos_x + lift_width)*1.5, 10])

        for floor in requests_each_floor:
            floor_spacing = 0
            for i in range(1, len(floor)):
                if floor[i] == 'up':
                    window.blit(stickman_up_scaled, (lift_pos_x + lift_width + 10 + floor_spacing, WINDOW_SIZE[1] - int(floor[0]) * floor_height - stickman_up_scaled.get_rect().size[1] - 10))
                else:
                    window.blit(stickman_down_scaled, (lift_pos_x + lift_width + 10 + floor_spacing, WINDOW_SIZE[1] - int(floor[0]) * floor_height - stickman_down_scaled.get_rect().size[1] - 10))
                floor_spacing += 35

        lift_spacing = 0
        for request in list(lift_volume):
            if lift_volume[request]['direction'] == 'up':
                window.blit(stickman_up_scaled, (lift_pos_x + lift_spacing, lift_pos_y + lift_height - stickman_scaled.get_rect().size[1]))
            else:
                window.blit(stickman_down_scaled, (lift_pos_x + lift_spacing, lift_pos_y + lift_height - stickman_scaled.get_rect().size[1]))
            lift_spacing += 35

        pygame.draw.rect(window, COLOUR_MENU_TITLE, [lift_width + (lift_pos_x + lift_width) * 1.5, 0, WINDOW_SIZE[0] - lift_width + (lift_pos_x + lift_width), 150])
        pygame.draw.rect(window, COLOUR_WHITE, [0, 0, 5, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE, [lift_pos_x + lift_width, 0, 10, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE, [lift_width + (lift_pos_x + lift_width) * 1.5, 0, 10, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE, [lift_pos_x, lift_pos_y, lift_width, lift_height], 10)
        pygame.draw.line(window, COLOUR_WHITE, (lift_width / 2, 0), (lift_width / 2, lift_pos_y), 3)
        pygame.draw.line(window, COLOUR_WHITE, (lift_width / 2, lift_pos_y + lift_height), (lift_width / 2, WINDOW_SIZE[1]), 3)
        pygame.draw.rect(window, COLOUR_RED, [WINDOW_SIZE[0] - 110, WINDOW_SIZE[1] - 60, 100, 50])

        quit_text = large_font.render('QUIT', True, COLOUR_BLACK)
        window.blit(quit_text, (WINDOW_SIZE[0] - 87, WINDOW_SIZE[1] - 58))

        title_text = large_font.render('Base  Algorithm', True, COLOUR_BLACK)
        window.blit(title_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 0))

        requests_served_text = small_font.render('Requests  served:  ' + str(len(list(requests_served))), True, COLOUR_BLACK)
        window.blit(requests_served_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 50))

        total_wait = 0
        for request in requests_served:
            total_wait += requests_served[request]['wait']
        try:
            avg_wait = total_wait / len(list(requests_served))
            avg_wait = round(avg_wait, 2)
        except ZeroDivisionError:
            avg_wait = 0
        avg_wait_text = small_font.render('Average  wait  time:  ' + str(avg_wait), True, COLOUR_BLACK)
        window.blit(avg_wait_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 100))

        lift_pos_y += lift_speed

        if lift_pos_y + lift_height > WINDOW_SIZE[1] - 10:
            lift_speed = lift_speed * -1

        if lift_pos_y + lift_height < floor_height - 10:
            lift_speed = lift_speed * -1

        for floor in range(floors):
            if (lift_pos_y + lift_height) < WINDOW_SIZE[1] - int(floor * floor_height) + 30 and (lift_pos_y + lift_height) > WINDOW_SIZE[1] - int(floor * floor_height) - 10 - 30:
                current_floor = floor
            elif current_floor == floor:
                current_floor = None
                for request in requests:
                    requests[request]['wait'] += 1
                for request in lift_volume:
                    lift_volume[request]['wait'] += 1

        if lift_pos_y + lift_height > WINDOW_SIZE[1] - 10:
            direction = 'up'
        if lift_pos_y + lift_height < floor_height:
            direction = 'down'
        
        for request in list(requests):
            if requests[request]['floor_from'] == current_floor and requests[request]['direction'] == direction and lift_capacity < 6:
                key_list = list(requests.keys()) 
                val_list = list(requests.values()) 
                lift_volume[key_list[val_list.index(requests[request])]] = requests[request]
                if direction == 'up':
                    requests_each_floor[int(requests[request]['floor_from'])].remove('up')
                else:
                    requests_each_floor[int(requests[request]['floor_from'])].remove('down')
                del requests[request]
                lift_capacity += 1

        for request in list(lift_volume):
            if lift_volume[request]['floor_to'] == current_floor:
                requests_served[request_number] = lift_volume[request]
                del lift_volume[request]
                lift_capacity -= 1

        pygame.display.update()
        clock.tick(60)

def improved_algorithm_run():

    global sim_exit
    global requests
    global request_number
    global requests_each_floor

    main_menu.disable()
    main_menu.reset(1)

    running = True
    sim_exit = True
    pygame.init()

    window = pygame.display.set_mode((WINDOW_SIZE[0],WINDOW_SIZE[1]))
    pygame.display.set_caption('Lift Algorithm')  
    clock = pygame.time.Clock()

    lift_pos_y = WINDOW_SIZE[1] - lift_height - 10
    lift_pos_y = 300
    lift_speed = -10
    lift_capacity = 0

    requests = {}
    requests_served = {}
    request_number = 0
    direction = 'up'
    lift_volume = {}

    current_floor = 0
    floors_visited = 0

    requests_each_floor = []
    for i in range(floors):
        requests_each_floor.append([i])

    Timer(random.randrange(0, spawn_rate), generate_random_requests, args=[floors, spawn_rate]).start()

    floor_from = None
    while sim_exit:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and main_menu.is_disabled():
                    sim_exit = False
                    main_menu.enable()
                    # Quit this function, then skip to loop of main-menu on line 317
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_pos[0] > WINDOW_SIZE[0] - 110 and mouse_pos[0] < WINDOW_SIZE[0] - 10:
                    if mouse_pos[1] > WINDOW_SIZE[1] - 60 and mouse_pos[1] < WINDOW_SIZE[1] - 10:
                        sim_exit = False
                        main_menu.enable()
                        return

        # Pass events to main_menu
        main_menu.mainloop(event)
        mouse_pos = pygame.mouse.get_pos()

        window.fill(COLOR_MENU_BACKGROUND)
        
        floor_height = WINDOW_SIZE[1] / floors
        for i in range(floors):
            floor_text = large_font.render(str(floors - i - 1), True, COLOUR_BLACK)
            window.blit(floor_text, (lift_pos_x + lift_width + 12, floor_height*i))
            pygame.draw.rect(window, COLOUR_BLACK, [lift_pos_x+lift_width, (floor_height*i)+floor_height-10, (lift_pos_x + lift_width)*1.5, 10])

        for floor in requests_each_floor:
            floor_spacing = 0
            for i in range(1, len(floor)):
                if floor[i] == 'up':
                    window.blit(stickman_up_scaled, (lift_pos_x + lift_width + 10 + floor_spacing, WINDOW_SIZE[1] - int(floor[0]) * floor_height - stickman_up_scaled.get_rect().size[1] - 10))
                else:
                    window.blit(stickman_down_scaled, (lift_pos_x + lift_width + 10 + floor_spacing, WINDOW_SIZE[1] - int(floor[0]) * floor_height - stickman_down_scaled.get_rect().size[1] - 10))
                floor_spacing += 35

        lift_spacing = 0
        for request in list(lift_volume):
            if lift_volume[request]['direction'] == 'up':
                window.blit(stickman_up_scaled, (lift_pos_x + lift_spacing, lift_pos_y + lift_height - stickman_scaled.get_rect().size[1]))
            else:
                window.blit(stickman_down_scaled, (lift_pos_x + lift_spacing, lift_pos_y + lift_height - stickman_scaled.get_rect().size[1]))
            lift_spacing += 35

        pygame.draw.rect(window, COLOUR_MENU_TITLE, [lift_width + (lift_pos_x + lift_width) * 1.5, 0, WINDOW_SIZE[0] - lift_width + (lift_pos_x + lift_width), 150])
        pygame.draw.rect(window, COLOUR_WHITE, [0, 0, 5, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE, [lift_pos_x + lift_width, 0, 10, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE, [lift_width + (lift_pos_x + lift_width) * 1.5, 0, 10, WINDOW_SIZE[1]])
        pygame.draw.rect(window, COLOUR_WHITE, [lift_pos_x, lift_pos_y, lift_width, lift_height], 10)
        pygame.draw.line(window, COLOUR_WHITE, (lift_width / 2, 0), (lift_width / 2, lift_pos_y), 3)
        pygame.draw.line(window, COLOUR_WHITE, (lift_width / 2, lift_pos_y + lift_height), (lift_width / 2, WINDOW_SIZE[1]), 3)
        pygame.draw.rect(window, COLOUR_RED, [WINDOW_SIZE[0] - 110, WINDOW_SIZE[1] - 60, 100, 50])

        quit_text = large_font.render('QUIT', True, COLOUR_BLACK)
        window.blit(quit_text, (WINDOW_SIZE[0] - 87, WINDOW_SIZE[1] - 58))

        title_text = large_font.render('Improved  Algorithm', True, COLOUR_BLACK)
        window.blit(title_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 0))

        requests_served_text = small_font.render('Requests  served:  ' + str(len(list(requests_served))), True, COLOUR_BLACK)
        window.blit(requests_served_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 50))

        total_wait = 0
        for request in requests_served:
            total_wait += requests_served[request]['wait']
        try:
            avg_wait = total_wait / len(list(requests_served))
            avg_wait = round(avg_wait, 2)
        except ZeroDivisionError:
            avg_wait = 0
        avg_wait_text = small_font.render('Average  wait  time:  ' + str(avg_wait), True, COLOUR_BLACK)
        window.blit(avg_wait_text, (lift_width + (lift_pos_x + lift_width) * 1.5 + 20, 100))

        lift_pos_y += lift_speed

        if lift_capacity == 0:
            if requests:
                next_request = min(list(requests.keys()))
                floor_to = requests[next_request]['floor_from']
            else:
                floor_to = floors // 2
        else:
            dest = min(list(lift_volume.keys()))
            floor_to = lift_volume[dest]['floor_to']

        try:
            if current_floor >= 0:
                floor_from = current_floor
        except:
            pass


        if floor_from < floor_to:
            lift_speed = -10
            direction = 'up'

        if floor_from > floor_to:
            lift_speed = 10
            direction = 'down'

        if floor_from == floor_to and not requests:
            lift_speed = 0
            direction = 'none'


        for floor in range(floors):
            if (lift_pos_y + lift_height) < WINDOW_SIZE[1] - int(floor * floor_height) + 30 and (lift_pos_y + lift_height) > WINDOW_SIZE[1] - int(floor * floor_height) - 10 - 30:
                current_floor = floor
            elif current_floor == floor:
                current_floor = None
                for request in requests:
                    requests[request]['wait'] += 1
                for request in lift_volume:
                    lift_volume[request]['wait'] += 1

        if lift_pos_y + lift_height > WINDOW_SIZE[1] - 10:
            direction = 'up'
        if lift_pos_y + lift_height < floor_height:
            direction = 'down'

        #print(direction, requests_each_floor)

        for request in list(requests):
            if (requests[request]['floor_from'] == current_floor and (requests[request]['direction'] == direction or direction == 'none' or lift_capacity == 0) and lift_capacity < 6):
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

        for request in list(lift_volume):
            if lift_volume[request]['floor_to'] == current_floor:
                requests_served[request_number] = lift_volume[request]
                del lift_volume[request]
                lift_capacity -= 1

        pygame.display.update()
        clock.tick(60)

def main():
    """
    Main program.
    :param test: Indicate function is being tested
    :type test: bool
    :return: None
    """

    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------
    global clock
    global main_menu
    global surface

    # -------------------------------------------------------------------------
    # Init pygame
    # -------------------------------------------------------------------------
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # Create pygame screen and objects
    surface = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Lift Algorithm')
    clock = pygame.time.Clock()
    load_config()

    # -------------------------------------------------------------------------
    # Create menus
    # -------------------------------------------------------------------------

    # select menu
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

    select_menu.add_option('Start',  # When pressing return -> select(Algorithm[0], font)
                         algorithm_selector)

    select_menu.add_selector('Select  Algorithm',
                           [('Base', 'BASE'),
                            ('Improved', 'IMPROVED')],
                           onchange=change_algorithm)
                  
    select_menu.add_option('Back', pygameMenu.events.BACK)

    # settings menu
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

    settings_menu.add_selector('Number  of  Floors', [('2',2),('3',3),('4',4),('5',5),('6',6),
                                                      ('7',7),('8',8),('9',9),('10',10)],
                                                      onchange=change_floors)
    settings_menu.add_selector('Request  Spawn  Rate', [('1',1), ('2',2),('3',3),('4',4),('5',5)],
                                                        onchange=change_spawn_rate)
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

    main_menu.add_option('Select  Algorithm', select_menu)
    main_menu.add_option('Settings', settings_menu)
    main_menu.add_option('Quit', pygameMenu.events.EXIT)

    # Configure main menu
    main_menu.set_fps(FPS)

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------
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
