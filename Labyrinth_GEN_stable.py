# coding=utf-8

import math
import os
import pygame
import random

# os.chdir('d:\')

version = "Version 0.1"

# ****** Create the game window ******
screen_size = (2490, 1248)

black = (0, 0, 0)
red = (255, 0, 0)
white = (255, 255, 255)
brown = (139, 69, 19)
yellow = (255, 238, 0)

# ****** Variables ******
FPS = 60
sprite_ratio = 15
# control_key = True    # Key not found

# Variables for developers
developer = True  # Show the development options

# ****** Read map ******
map_file = open('map_00.txt', 'r')
pointer = 0
walls_list = []
doors_list = []  # TODO: Add an ID to each door to link it to the keys
keys_list = []  # TODO: Add the ID of the linked door
ghosts_list = []  # TODO: Add the velocity of the ghost

for read_line in map_file.readlines():
    if read_line == 'WALLS\n':
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
        if pointer == 1:  # Wall
            read_line = list(map(int, read_line.split(', ')))
            read_line[1] = read_line[1] + 45
            walls_list.append(pygame.Rect(read_line))
        elif pointer == 2:  # Door
            read_line = tuple(map(int, read_line.split(', ')))
            doors_list.append(pygame.Rect(read_line))
        elif pointer == 3:  # Key
            read_line = tuple(map(int, read_line.split(', ')))
            keys_list.append(read_line)
        elif pointer == 4:  # player
            player_pos = tuple(map(int, read_line.split(', ')))
        elif pointer == 5:  # ghost
            read_line = tuple(map(int, read_line.split(', ')))
            ghosts_list.append(read_line)
        elif pointer == 6:  # house
            house_pos = tuple(map(int, read_line.split(', ')))

map_file.close()


# ****** Functions ******
def draw_wall(surface, rectangle):
    pygame.draw.rect(surface, white, rectangle)


def draw_door(surface, rectangle):
    pygame.draw.rect(surface, brown, rectangle)


def fitness(steps_number, bonus):
    return bonus + 1 / steps_number


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

    def update(self):
        self.pos_player_old_x = self.rect.x
        self.pos_player_old_y = self.rect.y
        self.rect.x += self.player_speed_x
        self.rect.y += self.player_speed_y
#        print("(", self.pos_player_old_x, ",", self.pos_player_old_y, ") -> (", self.rect.x, ",", self.rect.y, ")")

        # Control if the location of the player is outside
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > screen_size[0] - 2 * sprite_ratio:
            self.rect.x = screen_size[0] - 2 * sprite_ratio

        if self.rect.y < 48:  # TODO: Este parametro no puede ser un número arbitrario aqui. Convertir en variable (borde superior)
            self.rect.y = 48
        elif self.rect.y > screen_size[1] - 2 * sprite_ratio:
            self.rect.y = screen_size[1] - 2 * sprite_ratio

        print("(", self.pos_player_old_x, ",", self.pos_player_old_y, ") -> (", self.rect.x, ",", self.rect.y, ")")


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
        font = pygame.font.SysFont("serif", 120, bold=True, italic=True)
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
        self.vidas = 3  # Initials lives

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
        self.control_key = False  # Key not found
        self.control_door = True  # Door close

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

    def process_events(self):
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                # Close the windows by the corner-X
                return True

            if events.type == pygame.KEYUP:
                if events.key == pygame.K_SPACE:
                    # Restart the game after "Game over" by space bar
                    if self.game_over or self.game_win:
                        self.__init__()

        return False

    def gen_algorithm(self):
        action_selected = random.randint(0, 4)
        if action_selected == 0:  # Stop
            self.player.player_speed_x = 0
            self.player.player_speed_y = 0
            print("STOP -> (", self.player.player_speed_x, ",", self.player.player_speed_y, ")")
        elif action_selected == 1:  # Move DOWN
            self.player.player_speed_x = 0
            self.player.player_speed_y = -3
            print("DOWN -> (", self.player.player_speed_x, ",", self.player.player_speed_y, ")")
        elif action_selected == 2:  # Move LEFT
            self.player.player_speed_x = -3
            self.player.player_speed_y = 0
            print("LEFT -> (", self.player.player_speed_x, ",", self.player.player_speed_y, ")")
        elif action_selected == 3:  # Move RIGHT
            self.player.player_speed_x = 3
            self.player.player_speed_y = 0
            print("RIGHT -> (", self.player.player_speed_x, ",", self.player.player_speed_y, ")")
        elif action_selected == 4:  # Move UP
            self.player.player_speed_x = 0
            self.player.player_speed_y = 3
            print("UP -> (", self.player.player_speed_x, ",", self.player.player_speed_y, ")")
        else:
            print("ERROR")
            exit(1)

    def run_logic(self):
        # Take the key TODO: link each key to each door
        for key_pointed in self.keys_game:
            if pygame.sprite.collide_rect(self.player, key_pointed):
                key_pointed.rect.x = screen_size[0] - 2 * sprite_ratio
                key_pointed.rect.y = 3
                self.control_key = True

        # ****** Collisions
        for wall in walls_list:
            if self.player.rect.colliderect(wall):
                self.player.player_speed_x = 0
                self.player.player_speed_y = 0
                self.player.rect.x = self.player.pos_player_old_x
                self.player.rect.y = self.player.pos_player_old_y

            # TODO: Improve the ghost crashes with the wall so that it follows the player
            for ghost_pointed in self.ghosts_game:
                if ghost_pointed.rect.colliderect(wall):
                    ghost_pointed.ghost_speed_x = 0
                    ghost_pointed.ghost_speed_y = 0
                    ghost_pointed.rect.x = ghost_pointed.pos_ghost_old_x
                    ghost_pointed.rect.y = ghost_pointed.pos_ghost_old_y

        for door in doors_list:
            if self.player.rect.colliderect(door):
                if self.control_key:
                    self.control_door = False
                else:
                    self.player.player_speed_x = 0
                    self.player.player_speed_y = 0
                    self.player.rect.x = self.player.pos_player_old_x
                    self.player.rect.y = self.player.pos_player_old_y

            for ghost_pointed in self.ghosts_game:
                if ghost_pointed.rect.colliderect(door):
                    ghost_pointed.ghost_speed_x = 0
                    ghost_pointed.ghost_speed_y = 0
                    ghost_pointed.rect.x = ghost_pointed.pos_ghost_old_x
                    ghost_pointed.rect.y = ghost_pointed.pos_ghost_old_y

        for ghost_pointed in self.ghosts_game:
            if ghost_pointed.rect.colliderect(self.home):
                ghost_pointed.ghost_speed_x = 0
                ghost_pointed.ghost_speed_y = 0
                ghost_pointed.rect.x = ghost_pointed.pos_ghost_old_x
                ghost_pointed.rect.y = ghost_pointed.pos_ghost_old_y

        for ghost_pointed in self.ghosts_game:
            if self.player.rect.colliderect(ghost_pointed):
                self.restart()
                if self.vidas == 1:
                    self.game_over = True
                else:
                    self.vidas -= 1

        if self.player.rect.colliderect(self.home):
            self.game_win = True

        self.player.update()
        for ghost_pointed in self.ghosts_game:
            ghost_pointed.update(self.player)

    def display_frame(self, screen):
        screen.fill(black)
        if self.game_over:
            font = pygame.font.SysFont("serif", 60, bold=False, italic=False)
            game_over_text = font.render("GAME OVER, Click to continue", True, white)
            game_over_pos_x = (screen_size[0] // 2) - (game_over_text.get_width() // 2)
            game_over_pos_y = (screen_size[1] // 2) - (game_over_text.get_height() // 2)
            screen.blit(game_over_text, [game_over_pos_x, game_over_pos_y])
        elif self.game_win:
            font = pygame.font.SysFont("serif", 60, bold=False, italic=False)
            game_over_text = font.render("WINNER!, Click to continue", True, white)
            game_over_pos_x = (screen_size[0] // 2) - (game_over_text.get_width() // 2)
            game_over_pos_y = (screen_size[1] // 2) - (game_over_text.get_height() // 2)
            screen.blit(game_over_text, [game_over_pos_x, game_over_pos_y])
        else:
            # Draw upper line
            pygame.draw.rect(screen, white, (0, 40, screen_size[0], 5))

            # Draw lives
            screen.blit(self.player_vidas.image, self.player_vidas.rect)
            font = pygame.font.SysFont("serif", 25, bold=False, italic=False)  # Font
            text = font.render("x " + str(self.vidas), True, white)  # Text
            center_x = self.player_vidas.rect.x + 2 * sprite_ratio + 5  # Position text
            center_y = 5
            screen.blit(text, [center_x, center_y])  # Display

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

            # ****** Draw the mods and player

            # Draw player
            screen.blit(self.player.image, self.player.rect)

            # Draw ghost
            for ghost_pointed in self.ghosts_game:
                screen.blit(ghost_pointed.image, ghost_pointed.rect)

            if developer:
                for ghost_pointed in self.ghosts_game:
                    pygame.draw.circle(screen, red, (ghost_pointed.rect.x, ghost_pointed.rect.y),
                                       ghost_pointed.vista, 1)

            # Draw house
            screen.blit(self.home.image, self.home.rect)

        pygame.display.flip()


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
            if not game.state:
                menu.state = True

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
