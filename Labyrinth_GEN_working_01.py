# coding=utf-8

import math
import os
import pygame
import random
import numpy as np
import winsound

version = "Version 0.2"

# ****** Color variables
black = (0, 0, 0)
red = (255, 0, 0)
white = (255, 255, 255)
brown = (139, 69, 19)
yellow = (255, 238, 0)
green = (0, 110, 4)

# ****** Variables ******
FPS = 60
sprite_ratio = 15
# control_key = True    # Key not found

# ****** Variables for developers ******
developer = True  # Show the development options
speed = 20
top_line_y = 40  # Parameter to describe the y-location of the top line
max_trials = 100
mutation_rate = 0.2

frequency = 1000  # Set Frequency To 2500 Hertz
duration = 300  # Set Duration To 1000 ms == 1 second

# ****** Read map ******
map_file = open('map_00.txt', 'r')
pointer = 0
walls_list = []
doors_list = []  # TODO: Add an ID to each door to link it to the keys
keys_list = []  # TODO: Add the ID of the linked door
ghosts_list = []  # TODO: Add the velocity of the ghost

for read_line in map_file.readlines():
    if read_line == 'SCREEN\n':
        pointer += 1
    elif read_line == 'WALLS\n':
        pointer += 1
    elif read_line == 'DOOR\n':
        pointer += 1
    elif read_line == 'KEY\n':
        pointer += 1
    elif read_line == 'PLAYER\n':
        pointer += 1
    elif read_line == 'GHOST\n':
        pointer += 1
    elif read_line == 'HOUSE\n':
        pointer += 1
    elif read_line == 'END\n':
        break
    else:
        if pointer == 1:  # screen size
            screen_size = tuple(map(int, read_line.split(', ')))
        elif pointer == 2:  # Wall
            read_line = list(map(int, read_line.split(', ')))
            read_line[1] = read_line[1] + 45
            walls_list.append(pygame.Rect(read_line))
        elif pointer == 3:  # Door
            read_line = tuple(map(int, read_line.split(', ')))
            doors_list.append(pygame.Rect(read_line))
        elif pointer == 4:  # Key
            read_line = tuple(map(int, read_line.split(', ')))
            keys_list.append(read_line)
        elif pointer == 5:  # player
            player_pos = tuple(map(int, read_line.split(', ')))
        elif pointer == 6:  # ghost
            read_line = tuple(map(int, read_line.split(', ')))
            ghosts_list.append(read_line)
        elif pointer == 7:  # house
            house_pos = tuple(map(int, read_line.split(', ')))
map_file.close()


# ****** Functions ******
def draw_wall(surface, rectangle):
    pygame.draw.rect(surface, white, rectangle)


def draw_door(surface, rectangle):
    pygame.draw.rect(surface, brown, rectangle)


def fitness(steps_number, house_distance, win_bonus, key_bonus, dead_penalty):
    # The idea is to use the following parameter values:
    # win_bonus = 1 if find the house
    # key_bonus = 1 if find the key
    # dead_penalty = 1 if the player dead
    # Note: I'm working in this way to decide a better statistic in the future

    if win_bonus:
        win_bonus_value = 1
    else:
        win_bonus_value = 0

    if key_bonus:
        key_bonus_value = 1
    else:
        key_bonus_value = 0

    if dead_penalty:
        dead_penalty_valuer = 1
    else:
        dead_penalty_valuer = 0

    return win_bonus_value + key_bonus_value - dead_penalty_valuer + 1 / steps_number + 1 / house_distance


def procreation_probability(file_name):
    file_id = open(file_name, 'r')

    output_data = []

    for read_line in file_id.readlines():
        if read_line == 'TRIAL\n':
            p_pointer = 0
            p_pointer += 1
        elif read_line == 'FITNESS\n':
            p_pointer += 1
        elif read_line == 'PATH\n':
            p_pointer += 1
        else:
            if p_pointer == 2:  # Fitness
                output_data.append(float(read_line))
    file_id.close()

    output_data = list(map(lambda x: (x - min(output_data)) / (max(output_data) - min(output_data)), output_data))
    return output_data


def get_path(file_name, trial_selected):
    file_id = open(file_name, 'r')
    g_pointer = 0
    read_path = False

    output_data = []

    for read_line in file_id.readlines():
        if read_line == 'TRIAL\n':
            g_pointer = 0
            g_pointer += 1
        elif read_line == 'FITNESS\n':
            g_pointer += 1
        elif read_line == 'PATH\n':
            g_pointer += 1
        else:
            if g_pointer == 1:  # Trial
                if int(read_line) == trial_selected:
                    read_path = True
            if g_pointer == 3 and read_path:
                output_data.append(int(read_line))
    file_id.close()

    if len(output_data) == 0:
        print("ERROR: I didn't find any path in the selected file")
        exit(1)

    return output_data


def procreation(father_se, mother_se, mutation_prob):
    output_children_a = father_se[0:random.randint(1, len(father_se) - 1)]
    output_children_a = output_children_a + mother_se[random.randint(0, len(mother_se) - 1):]
    if random.random() <= mutation_prob:
        for cnt in range(random.randint(0, len(output_children_a) // 2)):
            output_children_a[random.randint(0, len(output_children_a) - 1)] = random.randint(0, 4)

    output_children_b = mother_se[0:random.randint(1, len(mother_se) - 1)]
    output_children_b = output_children_b + father_se[random.randint(0, len(father_se) - 1):]
    if random.random() <= mutation_prob:
        for cnt in range(random.randint(0, len(output_children_b) // 2)):
            output_children_b[random.randint(0, len(output_children_b) - 1)] = random.randint(0, 4)

    if len(output_children_a) == len(output_children_b):
        if max(np.array(output_children_a) - np.array(output_children_b)) == 0:
            print("ERROR: Children_a and children_b are equal.")
            exit(1)

    return output_children_a, output_children_b


# ****** Classes ******
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('Player_front_30x30.png').convert()
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.pos_player_old_x = 0
        self.pos_player_old_y = 0
        self.player_speed_x = 0
        self.player_speed_y = 0

        if developer:
            self.position_track = []

    def update(self):
        self.pos_player_old_x = self.rect.x
        self.pos_player_old_y = self.rect.y
        self.rect.x += self.player_speed_x
        self.rect.y += self.player_speed_y

        # Control if the location of the player is outside of screen
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > screen_size[0]:  # - 2 * sprite_ratio:
            self.rect.x = screen_size[0]  # - 2 * sprite_ratio

        if self.rect.y < top_line_y + 5:  # Last value = 8
            self.rect.y = top_line_y + 5  # Last value = 8
        elif self.rect.y > screen_size[1]:  # - 2 * sprite_ratio:
            self.rect.y = screen_size[1]  # - 2 * sprite_ratio

        if developer:
            self.position_track.append([self.rect.x, self.rect.y])


class Ghost(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('Ghost_left_30x30.png').convert()
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = screen_size[0] - 2 * sprite_ratio
        self.rect.y = screen_size[1] - 2 * sprite_ratio
        self.pos_ghost_old_x = 0
        self.pos_ghost_old_y = 0
        self.ghost_speed_x = 0
        self.ghost_speed_y = 0
        self.vista = 250

    def __Distance__(self, obj1, obj2):
        return math.sqrt((obj2.rect.x - obj1.rect.x) ** 2 + (obj2.rect.y - obj1.rect.y) ** 2)

    def __Speed__(self, obj1, obj2):
        if (obj2.rect.x - obj1.rect.x) < 0:
            ghost_speed_x = -1
        elif (obj2.rect.x - obj1.rect.x) == 0:
            ghost_speed_x = 0
        else:
            ghost_speed_x = 1

        if (obj2.rect.y - obj1.rect.y) < 0:
            ghost_speed_y = -1
        elif (obj2.rect.y - obj1.rect.y) == 0:
            ghost_speed_y = 0
        else:
            ghost_speed_y = 1

        return ghost_speed_x, ghost_speed_y

    def update(self, player):
        if self.__Distance__(self, player) < self.vista + 2 * sprite_ratio:
            self.pos_ghost_old_x = self.rect.x
            self.pos_ghost_old_y = self.rect.y

            tempo = self.__Speed__(self, player)
            self.rect.x += tempo[0]
            self.rect.y += tempo[1]
        else:
            self.ghost_speed_x = 0
            self.ghost_speed_y = 0


class Key(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('Key_30x30.png').convert()
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = screen_size[1] - 2 * sprite_ratio
        self.door_id = 0


class Home(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('House_30x60.png').convert()
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = screen_size[0] - 4 * sprite_ratio
        self.rect.y = 48


class Menu(object):
    def __init__(self):
        # ****** Main menu variables
        self.state = True  # Main menu
        self.menu_option = 1
        self.menu_text_list = ["Play", "Exit"]  # IDs = [1, 2]

    def process_events(self):
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                # Close the windows by the corner-X
                return True

            # Keyboard events
            if events.type == pygame.KEYDOWN:
                if self.state:  # Main menu events
                    if events.key == pygame.K_UP:
                        if self.menu_option > 1:
                            self.menu_option -= 1
                    if events.key == pygame.K_DOWN:
                        if self.menu_option < len(self.menu_text_list):
                            self.menu_option += 1
                    if events.key == pygame.K_RETURN:
                        if self.menu_option == 1:
                            self.state = False
                        else:
                            return True
        return False

    def display_frame(self, screen):
        screen.fill(black)
        font = pygame.font.SysFont("serif", 50, bold=True, italic=True)
        title_text = font.render("LABYRINTH GEN", True, white)
        title_pos_x = (screen_size[0] // 2) - (title_text.get_width() // 2)
        title_pos_y = (screen_size[1] // 2) - (title_text.get_height() // 2) - 250
        screen.blit(title_text, [title_pos_x, title_pos_y])

        font = pygame.font.SysFont("serif", 30, bold=False, italic=False)
        version_text = font.render(version, True, white)
        version_pos_x = screen_size[0] - version_text.get_width() - 25
        version_pos_y = screen_size[1] - version_text.get_height() - 25
        screen.blit(version_text, [version_pos_x, version_pos_y])

        font = pygame.font.SysFont("serif", 60, bold=True, italic=True)
        menu_pos_y = (screen_size[1] // 2) - 100
        cnt = 0
        for text in self.menu_text_list:
            cnt += 1
            if cnt == self.menu_option:
                color = yellow
            else:
                color = white

            menu_text = font.render(text, True, color)
            menu_pos_x = (screen_size[0] // 2) - (menu_text.get_width() // 2)
            menu_pos_y += 120
            screen.blit(menu_text, [menu_pos_x, menu_pos_y])

        pygame.display.flip()


class Game(object):
    def __init__(self):
        # ****** Game variables
        self.state = False
        self.game_over = False
        self.game_win = False
        self.control_key = False  # False/True = No/Yes I have the key
        self.control_door = True  # True/False = Close/Open door
        self.game_stop = False
        self.vidas = 1  # Initials lives

        # ****** Genetic algorithm variables
        self.stage_number = 1
        self.trial_number = 1
        self.steps_number = 0
        self.steps_vector = []
        self.current_path = []
        self.generation_file_name = "Generation_" + str(self.stage_number) + ".txt"
        self.children_file_name = "Generation_ch" + str(self.stage_number - 1) + ".txt"

        # ****** Objects definition
        self.player = Player()
        self.player_vidas = Player()
        self.home = Home()
        self.ghosts_game = []
        for cnt in range(len(ghosts_list)):
            self.ghosts_game.append(Ghost())

        self.keys_game = []
        for cnt in range(len(keys_list)):
            self.keys_game.append(Key())

        # ****** Variables of objects
        self.player.rect.x = player_pos[0]
        self.player.rect.y = player_pos[1]

        self.player_vidas.rect.x = 5
        self.player_vidas.rect.y = 5

        for cnt in range(len(ghosts_list)):
            self.ghosts_game[cnt].rect.x = ghosts_list[cnt][0]
            self.ghosts_game[cnt].rect.y = ghosts_list[cnt][1]

        for cnt in range(len(keys_list)):
            self.keys_game[cnt].rect.x = keys_list[cnt][0]
            self.keys_game[cnt].rect.y = keys_list[cnt][1]

        self.home.rect.x = house_pos[0]
        self.home.rect.y = house_pos[1]

    def restart(self):
        # ****** Variables
        self.game_over = False  # Game not over
        self.game_win = False  # Game not win
        self.control_key = False  # Key not found
        self.control_door = True  # Door close
        self.game_stop = False

        # ****** Player
        self.player.rect.x = player_pos[0]
        self.player.rect.y = player_pos[1]

        # ****** Keys
        for cnt in range(len(keys_list)):
            self.keys_game[cnt].rect.x = keys_list[cnt][0]
            self.keys_game[cnt].rect.y = keys_list[cnt][1]

        # ****** Ghosts
        for cnt in range(len(ghosts_list)):
            self.ghosts_game[cnt].rect.x = ghosts_list[cnt][0]
            self.ghosts_game[cnt].rect.y = ghosts_list[cnt][1]

        # ****** Genetic algorithm
        self.steps_vector = []
        self.current_path = []

        if developer:
            self.player.position_track = []

    def process_events(self):
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                # Close the windows by the corner-X
                return True

        #            if events.type == pygame.KEYUP:
        #                if events.key == pygame.K_SPACE:
        #                    # Restart the game after "Game over" by space bar
        #                    if self.game_over or self.game_win:
        #                        self.__init__()

        return False

    def gen_algorithm(self):
        if self.stage_number == 1:
            self.steps_number += 1
            action_selected = random.randint(0, 4)
        else:
            if len(self.current_path) == 0:
                self.current_path = get_path(self.children_file_name, self.trial_number)
#                print(self.current_path[:10])

            if self.steps_number < len(self.current_path):
                action_selected = self.current_path[self.steps_number]
                self.steps_number += 1
            else:
                self.game_stop = True

        self.steps_vector.append(action_selected)
        if action_selected == 0:  # Stop
            self.player.player_speed_x = 0
            self.player.player_speed_y = 0
        elif action_selected == 1:  # Move DOWN
            self.player.player_speed_x = 0
            self.player.player_speed_y = -speed
        elif action_selected == 2:  # Move LEFT
            self.player.player_speed_x = -speed
            self.player.player_speed_y = 0
        elif action_selected == 3:  # Move RIGHT
            self.player.player_speed_x = speed
            self.player.player_speed_y = 0
        elif action_selected == 4:  # Move UP
            self.player.player_speed_x = 0
            self.player.player_speed_y = speed
        else:
            print("ERROR")
            exit(1)

    def run_logic(self):
        # Player takes a key TODO: link each key to each door
        for key_pointed in self.keys_game:
            if pygame.sprite.collide_rect(self.player, key_pointed):
                key_pointed.rect.x = screen_size[0] - 2 * sprite_ratio
                key_pointed.rect.y = 3
                self.control_key = True

        # ****** Collisions
        for wall in walls_list:
            # Player - Walls
            if self.player.rect.colliderect(wall):
                self.player.player_speed_x = 0
                self.player.player_speed_y = 0
                self.player.rect.x = self.player.pos_player_old_x
                self.player.rect.y = self.player.pos_player_old_y

            # TODO: Improve the ghost crashes with the wall so that it follows the player
            # Ghost - Walls
            for ghost_pointed in self.ghosts_game:
                if ghost_pointed.rect.colliderect(wall):
                    ghost_pointed.ghost_speed_x = 0
                    ghost_pointed.ghost_speed_y = 0
                    ghost_pointed.rect.x = ghost_pointed.pos_ghost_old_x
                    ghost_pointed.rect.y = ghost_pointed.pos_ghost_old_y

        for door in doors_list:
            # Player - Door
            if self.player.rect.colliderect(door):
                if self.control_key:
                    self.control_door = False
                else:
                    self.player.player_speed_x = 0
                    self.player.player_speed_y = 0
                    self.player.rect.x = self.player.pos_player_old_x
                    self.player.rect.y = self.player.pos_player_old_y

            # Ghost - Door
            for ghost_pointed in self.ghosts_game:
                if ghost_pointed.rect.colliderect(door):
                    ghost_pointed.ghost_speed_x = 0
                    ghost_pointed.ghost_speed_y = 0
                    ghost_pointed.rect.x = ghost_pointed.pos_ghost_old_x
                    ghost_pointed.rect.y = ghost_pointed.pos_ghost_old_y

        # Ghost - Home
        for ghost_pointed in self.ghosts_game:
            if ghost_pointed.rect.colliderect(self.home):
                ghost_pointed.ghost_speed_x = 0
                ghost_pointed.ghost_speed_y = 0
                ghost_pointed.rect.x = ghost_pointed.pos_ghost_old_x
                ghost_pointed.rect.y = ghost_pointed.pos_ghost_old_y

        # Player - Ghost
        for ghost_pointed in self.ghosts_game:
            if self.player.rect.colliderect(ghost_pointed):
                self.restart()
                if self.vidas == 1:
                    self.game_over = True
                else:
                    self.vidas -= 1

        # Player - Home
        if self.player.rect.colliderect(self.home):
            self.game_win = True

        self.player.update()
        for ghost_pointed in self.ghosts_game:
            ghost_pointed.update(self.player)

    def display_frame(self, screen):
        screen.fill(black)
        # Draw upper line
        pygame.draw.rect(screen, white, (0, top_line_y, screen_size[0], 5))

        # Draw walls_list
        for wall in walls_list:
            draw_wall(screen, wall)  # Paint all walls_list defined

        # Draw door
        if self.control_door:
            for door in doors_list:
                draw_door(screen, door)

        # Draw key
        for key_pointed in self.keys_game:
            screen.blit(key_pointed.image, key_pointed.rect)

        # ****** Draw mods and player
        # Draw player
        screen.blit(self.player.image, self.player.rect)

        # Draw ghost
        for ghost_pointed in self.ghosts_game:
            screen.blit(ghost_pointed.image, ghost_pointed.rect)

        if developer:
            for ghost_pointed in self.ghosts_game:
                pygame.draw.circle(screen, red, (ghost_pointed.rect.x, ghost_pointed.rect.y), ghost_pointed.vista, 1)

        # Draw house
        screen.blit(self.home.image, self.home.rect)

        # **** Draw Genetic algorithm information
        font = pygame.font.SysFont("serif", 25, bold=False, italic=False)  # Font
        # Draw stage
        text = font.render("Stage = " + str(self.stage_number), True, white)  # Text
        screen.blit(text, [0, 5])  # Display
        # Draw trials
        text = font.render("Trial = " + str(self.trial_number), True, white)  # Text
        screen.blit(text, [200, 5])  # Display
        # Draw steps number
        text = font.render("Step = " + str(self.steps_number), True, white)  # Text
        screen.blit(text, [350, 5])  # Display

        # Draw path line
        if developer:
            if len(self.player.position_track) > 1:
                for i in range(len(self.player.position_track) - 1):
                    pygame.draw.line(screen, green, self.player.position_track[i], self.player.position_track[i + 1])

        pygame.display.flip()

    def data_process(self):
        # ****** Save paths in file
        gen_file = open(self.generation_file_name, "a")
        gen_file.write("TRIAL\n")
        gen_file.write(str(self.trial_number) + "\n")
        gen_file.write("FITNESS\n")
        aux_distance = math.sqrt(
            (self.player.rect.x - self.home.rect.x) ** 2 + (self.player.rect.y - self.home.rect.y) ** 2)
        gen_file.write(
            str(fitness(self.steps_number, aux_distance, self.game_win, self.control_key, self.game_over)) + "\n")
        gen_file.write("PATH\n")
        for i in self.steps_vector:
            gen_file.write(str(i) + "\n")

        gen_file.close()

        # ****** Update variables
        self.trial_number += 1
        self.steps_number = 0
        self.restart()

        # ****** Procreation part
        if self.trial_number > max_trials:
            self.trial_number = 1
            self.stage_number += 1
            winsound.Beep(frequency, duration)

            probabilities = procreation_probability(self.generation_file_name)

            self.children_file_name = "Generation_ch" + str(self.stage_number) + ".txt"
            new_file_id = open(self.children_file_name, 'w')
            n_trials = 1
            for j in range(max_trials // 2):
                for i in range(2):
                    accepted = False
                    selection = 0
                    while not accepted:
                        selection = random.randint(1, len(probabilities))
                        if probabilities[selection - 1] >= random.random():
                            accepted = True

                    if i == 0:
                        father = get_path(self.generation_file_name, selection)
                    else:
                        mother = get_path(self.generation_file_name, selection)

                children_a, children_b = procreation(father, mother, mutation_rate)

                new_file_id.write("TRIAL\n")
                new_file_id.write(str(n_trials) + "\n")
                new_file_id.write("FITNESS\n")
                new_file_id.write("0\n")
                new_file_id.write("PATH\n")
                for k in children_a:
                    new_file_id.write(str(k) + "\n")
                n_trials += 1

                new_file_id.write("TRIAL\n")
                new_file_id.write(str(n_trials) + "\n")
                new_file_id.write("FITNESS\n")
                new_file_id.write("0\n")
                new_file_id.write("PATH\n")
                for k in children_b:
                    new_file_id.write(str(k) + "\n")
                n_trials += 1
            new_file_id.close()

            self.generation_file_name = "Generation_" + str(self.stage_number) + ".txt"



# ******************************************************
# ********************* MAIN LOOP **********************
# ******************************************************

def main():
    # ****** Create the main window environment
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    pygame.init()

    # ****** Initialize the game window
    screen = pygame.display.set_mode(screen_size)  # , pygame.FULLSCREEN)
    pygame.display.set_caption(u'Labyrinth Gen')

    # pygame.mouse.set_visible(0)  # Hide the mouse

    done = False
    clock = pygame.time.Clock()

    menu = Menu()
    game = Game()

    while not done:
        if menu.state:
            done = menu.process_events()
            menu.display_frame(screen)
            if not menu.state:
                game.state = True

        if game.state:
            done = game.process_events()  # Exit of while loop to close
            game.gen_algorithm()
            game.run_logic()
            game.display_frame(screen)
            if game.game_win or game.game_stop:
                game.data_process()
            if not game.state:
                menu.state = True

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
