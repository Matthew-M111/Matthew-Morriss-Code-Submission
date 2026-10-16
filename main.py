# libraries
import pygame
import json
from random import randint

# allows pygame to run
pygame.init()

# WINDOW AND GRID PROPERTIES
WINDOW_HEIGHT = 700  # constant window pixel height
WINDOW_WIDTH = 900  # constant window pixel width
GRID_COLUMNS = 17  # constant number of columns in grid
GRID_ROWS = 4  # constant number of rows in grid
MOVE_TIMER = 4  # constant number of moves before a new row forms
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # sets screen size as given sizes

# BUBBLE PROPERTIES
BUBBLE_DIAMETER = 50  # number of pixels for diameter
BUBBLE_RADIUS = BUBBLE_DIAMETER / 2  # calculation to get the bubble radius
SHOOTER_X = WINDOW_WIDTH // 2  # shooter's x position
SHOOTER_Y = WINDOW_HEIGHT - 30  # shooter's y position
SPEED = 12.5  # constant speed of bubble
BUBBLE_SIXTH = BUBBLE_DIAMETER / 6  # size of a sixth of a bubble (used for grid snapping)
QUEUE_SPACING = 2 * BUBBLE_DIAMETER  # space between each bubble in the queue
colours = ["red", "blue", "green", "yellow", "orange", "pink"]  # list of available colours for bubble


# JSON TEXT FILE HANDLING
file_name = "user_saves.json"  # name of file to save user data

# load saves is a function to open the text file
# returns a dictionary consisting of the users and their scores as the key and value respectively
def load_saves():
    with open(file_name, "r") as file:
        file_old = json.load(file)
    return file_old

# save recent is a function to save the latest score data for each user
# convert the list of characters for username into string
# updates the highest score if the username exists or creates a new entry with given score
def save_recent(username, score):
    file_old = load_saves()
    username = "".join(username)

    if username in file_old:
        if file_old[username] < score:
            file_old[username] = score
    else:
        file_old[username] = score

    with open(file_name, "w") as file:
        json.dump(file_old, file, indent=4)

# sorts the data descendingly into a array of data
# slices the array to get the top five
def top_five():
    scores = load_saves()
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_scores[:5]


# RANDOM COLOUR SELECTION

# function to randomly select a colour
# selects a random index from the array of colours and thus returns a colour
def select_colour():
    colour = colours[randint(0, len(colours) - 1)]
    return colour


# SCORE CLASS CREATION

# Manage scoring, multipliers, streaks and text rendering
class Score:
    def __init__(self):
        self.base_bubble_score = 20
        self.bubble_streak_multiplier = 1
        self.bubble_combo_multiplier = 1
        self.total_score = 0
        self.highest_score = 0

# score for successful matches
    def matching_score(self, combo_length):
        self.bubble_combo_multiplier = combo_length
        self.total_score += self.base_bubble_score * self.bubble_combo_multiplier * self.bubble_streak_multiplier

# seperate score calculation for bubbles that fall down
    def floating_score(self, floating_count):
        self.total_score += floating_count * self.base_bubble_score

# reset streak multiplier
    def streak_reset(self):
        self.bubble_streak_multiplier = 1

# showing the user's current and highest score onto the screen
# converts user scores to strings so they can be blitted
# "".join changes the list input of their username to a string
    def game_score(self):
        file_access = load_saves()
        font = pygame.font.SysFont("Arial", 20)
        img = font.render(("Current Score: " + str(self.total_score)), True, (0, 0, 0))
        img_2 = font.render("Highest Score: " + str(file_access["".join(FullGame.username)]), True, (0, 0, 0))
        SCREEN.blit(img, (30, WINDOW_HEIGHT - 50))
        SCREEN.blit(img_2, (30, WINDOW_HEIGHT - 30))

# reset all conditions for new game
    def score_reset(self):
        self.total_score = 0
        self.bubble_streak_multiplier = 1

# this was a testing function for seeing if the scores and multipliers worked before I blitted them to screen
    def print_score(self):
        print(f"{self.total_score=}")
        print(f"{self.highest_score=}")
        print(f"{self.bubble_streak_multiplier=}")


# BUBBLE SPRITE CLASS CREATION

# inheritance used for pygame sprite functions
# Manages its movement physics, trajectory and states
class Bubble(pygame.sprite.Sprite):
    def __init__(self, colour, x_pos, y_pos):
# shooter bubble properties
        pygame.sprite.Sprite.__init__(self)  # initialises sprite function
        self.colour = colour
        self.image = pygame.Surface((BUBBLE_DIAMETER, BUBBLE_DIAMETER), pygame.SRCALPHA)  # colours outside of bubble are transparent
        pygame.draw.circle(self.image, colour, (BUBBLE_RADIUS, BUBBLE_RADIUS), BUBBLE_RADIUS) # draws circle with costant measurements
        self.rect = self.image.get_rect()

        self.x_pos = float(x_pos)    # float so direction is accurate
        self.y_pos = float(y_pos)
        self.rect.center = (int(self.x_pos), int(self.y_pos))  # int so snaps to grid nicely
        self.x_velocity = 0
        self.y_velocity = 0

        self.shooter_x = SHOOTER_X
        self.shooter_y = SHOOTER_Y

        self.released = False  # bubble states
        self.falling = False
        self.timeout = False

# should player be able to shoot
    def valid_shot_check(self):
        # calculates the distance
        mouse_position = pygame.mouse.get_pos()
        dx = mouse_position[0] - self.shooter_x
        dy = mouse_position[1] - self.shooter_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # checks if y position of mouse is above shooter
        if mouse_position[1] > (self.shooter_y - BUBBLE_RADIUS) or distance == 0:
            return False
        return True

#draws trajectory line
    def trajectory(self):
        # if valid shot available, creates trajectory line from shooter to mouse
        if self.valid_shot_check():
            mouse_position = pygame.mouse.get_pos()
            pygame.draw.line(SCREEN, (92, 92, 92), (self.rect.centerx, self.rect.centery), mouse_position, width=3)

# deciding the direction of bubble movement
    def shooting(self):
        # if valid shot available, calculates distance again
        if self.valid_shot_check():
            mouse_position = pygame.mouse.get_pos()
            dx = mouse_position[0] - self.shooter_x
            dy = mouse_position[1] - self.shooter_y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            # creates a unit vector (decides direction of bubble) and releases bubble
            x_direction = dx / distance
            y_direction = dy / distance
            self.x_velocity = x_direction * SPEED
            self.y_velocity = y_direction * SPEED
            self.released = True

# live movement of bubble on screen
    def update(self):
        self.timeout = True
        # moves bubble when it is released.
        if self.released:
            # hitting walls inverts velocity to allow bounce mechanic
            if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH:
                self.x_velocity *= -1

            self.x_pos += self.x_velocity
            self.y_pos += self.y_velocity
            self.rect.center = (int(self.x_pos), int(self.y_pos))

            # bubble dies if the centre goes past top of screen
            if self.rect.centery < 0:
                pygame.sprite.Sprite.kill(self)

        elif self.falling:
            self.y_velocity += 0.2  # gravity acceleration instead of constant speed
            self.y_pos += self.y_velocity
            self.rect.center = (int(self.x_pos), int(self.y_pos)) # update bubble position on screen (int for precision)

            #print(self.y_velocity)  # TESTING SPEED INCREASE

            # kill sprite if fully passes the line
            if self.rect.top > (8 / 9 * WINDOW_HEIGHT):
                pygame.sprite.Sprite.kill(self)

        # user can shoot another bubble if one currently not in play
        else:
            self.timeout = False


# GRID CLASS CREATION

# Manage hexagonal layout, snapping, matching algorithms and floating checks
class Grid:
    def __init__(self):
# grid properties
        self.spacing = BUBBLE_DIAMETER
        self.gridbubble_group = pygame.sprite.Group()
        self.move_count = MOVE_TIMER
        self.new_row_counter = 0

# method to fill grid with bubbles
    def fill_grid(self):
        # nested iteration to go through every cell
        for i in range(GRID_ROWS):
            for j in range(GRID_COLUMNS):
                self.colour = select_colour()

                # creates a bubble at each cell with even spacing vertically
                self.y_position = BUBBLE_RADIUS + (i * self.spacing)

                # alternate first bubble x_centre a radius for hexagonal grid
                if i % 2 != 0:
                    self.x_position = BUBBLE_DIAMETER + (j * self.spacing)
                else:
                    self.x_position = BUBBLE_RADIUS + (j * self.spacing)

                # creates bubble object at this position and adds to the group (aggregation)
                gridBubble = Bubble(self.colour, self.x_position, self.y_position)
                self.gridbubble_group.add(gridBubble)

# method for snapping bubbles to correct positions surrounding where it hit
    def snap(self, current_bubble, collided_bubble):
        #stopping bubble movement
        current_bubble.released = False
        current_bubble.x_velocity = 0
        current_bubble.y_velocity = 0

        collided_bubblex = collided_bubble.rect.centerx
        collided_bubbley = collided_bubble.rect.centery
        position_occupied = False
        temp_x = 0
        temp_y = 0

        # checking if hitting top third of bubble
        if current_bubble.rect.centery < collided_bubbley - BUBBLE_SIXTH:
            # checking if hit left / right and giving x,y values
            if current_bubble.rect.centerx < collided_bubblex:
                temp_x = collided_bubblex - BUBBLE_RADIUS
                temp_y = collided_bubbley - BUBBLE_DIAMETER

            elif current_bubble.rect.centerx >= collided_bubblex:
                temp_x = collided_bubblex + BUBBLE_RADIUS
                temp_y = collided_bubbley - BUBBLE_DIAMETER

        # checking if hitting bottom third of bubble
        elif current_bubble.rect.centery > collided_bubbley + BUBBLE_SIXTH:
            # checking if hit left / right and giving x,y values
            if current_bubble.rect.centerx < collided_bubblex:
                temp_x = collided_bubblex - BUBBLE_RADIUS
                temp_y = collided_bubbley + BUBBLE_DIAMETER

            elif current_bubble.rect.centerx >= collided_bubblex:
                temp_x = collided_bubblex + BUBBLE_RADIUS
                temp_y = collided_bubbley + BUBBLE_DIAMETER

        # only other option is to hit middle third of bubble
        else:
            # checking if hit left / right and giving x,y values
            if current_bubble.rect.centerx < collided_bubblex:
                temp_x = collided_bubblex - BUBBLE_DIAMETER
                temp_y = collided_bubbley

            elif current_bubble.rect.centerx >= collided_bubblex:
                temp_x = collided_bubblex + BUBBLE_DIAMETER
                temp_y = collided_bubbley

        # checking if a position is taken
        for bubbles in self.gridbubble_group:
            # skips over the collided bubble
            if bubbles == collided_bubble:
                continue

            dx = bubbles.rect.centerx - temp_x
            dy = bubbles.rect.centery - temp_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            # distance to temp position and other will be approximately zero but smaller than diameter if taken
            if distance < BUBBLE_RADIUS:
                position_occupied = True
                break

        if not position_occupied:
            current_bubble.rect.centerx = temp_x
            current_bubble.rect.centery = temp_y
        else:
            # move bubble down a row if occupied
            temp_y += BUBBLE_DIAMETER
            current_bubble.rect.centerx = temp_x
            current_bubble.rect.centery = temp_y

# shifts all  grid bubbles down to next row after a set number of unsuccessful moves
    def new_row(self):
        # decrease move count until 0
        self.move_count -= 1

        if self.move_count == 0:
            self.new_row_counter += 1

            # then shifts all bubbles down by a diameter to get next row
            for sprite in self.gridbubble_group:
                sprite.rect.y += BUBBLE_DIAMETER
                sprite.y_pos += BUBBLE_DIAMETER

            # for all columns in first row, a bubble is placed
            for i in range(GRID_COLUMNS):
                self.colour = select_colour()
                self.y_position = BUBBLE_RADIUS

                # x centre positions will be offset every alternating rows
                if self.new_row_counter % 2 != 0:
                    self.x_position = BUBBLE_DIAMETER + (i * self.spacing)

                else:
                    self.x_position = BUBBLE_RADIUS + (i * self.spacing)

                new_row = Bubble(self.colour, self.x_position, self.y_position)
                self.gridbubble_group.add(new_row)
                self.move_count = MOVE_TIMER    # move timer is reset

# calculations for valid neighbours (horizontally adjacent or diagonal)
# True returned if the bubble being checked (parameter adjacent bubble) is calculated to be a neighbour
    def check_neighbours(self, start_bubble, adjacent_bubble):
        dx = abs(adjacent_bubble.rect.centerx - start_bubble.rect.centerx)
        dy = abs(adjacent_bubble.rect.centery - start_bubble.rect.centery)

        if dx == BUBBLE_DIAMETER and dy == 0:
            return True
        elif dx == BUBBLE_RADIUS and dy == BUBBLE_DIAMETER:
            return True
        else:
            return False

# BFS traversal in order to compare colours
    def match_colour(self, start_bubble):
        match_queue = [start_bubble]
        visited = []

        # repeat until no matching colours
        while len(match_queue) > 0:
            bubble_being_checked = match_queue.pop(0)
            if bubble_being_checked not in visited:
                visited.append(bubble_being_checked)

                #find matching bubbles adjacent
                for bubble in self.gridbubble_group:
                    if bubble not in visited:
                        if bubble.colour == bubble_being_checked.colour:
                            if self.check_neighbours(bubble_being_checked, bubble):
                                match_queue.append(bubble)

        # the list of matched coloured bubbles is returned
        return visited

# draws a red line to mark where top of bubbles shouldn't pass
    def elimination_line(self):
        pygame.draw.line(SCREEN, (255, 0, 0), (0, (8 / 9 * WINDOW_HEIGHT)), (WINDOW_WIDTH, (8 / 9 * WINDOW_HEIGHT)), width=4)

# checks if the top of the bubble goes past the line
    def elimination_test(self, test_bubble):
        if test_bubble.rect.top >= (8 / 9 * WINDOW_HEIGHT):
            return True
        else:
            return False

# BFS used to detect floating bubbles by finding those without a path to the top
    def drop_floating(self):
        float_queue = []
        visited = []
        floating_bubbles = []

        # adds the top row of bubbles into the queue
        for bubbles in self.gridbubble_group:
            if bubbles.rect.centery < BUBBLE_DIAMETER:
                float_queue.append(bubbles)

        # adds first in queue to visited
        while len(float_queue) > 0:
            bubble_being_checked = float_queue.pop(0)
            if bubble_being_checked not in visited:
                visited.append(bubble_being_checked)

                #add neighbours of current loop's bubble to queue
                for bubble in self.gridbubble_group:
                    if bubble not in visited:
                        if self.check_neighbours(bubble_being_checked, bubble):
                            float_queue.append(bubble)

        # those that have not been visited must be floating so remove them
        # must be a list to prevent error of changing a group while looping
        for bubbles in list(self.gridbubble_group):
            if bubbles not in visited:
                self.gridbubble_group.remove(bubbles)
                floating_bubbles.append(bubbles)

        # the list of disconnected bubbles is returned
        return floating_bubbles


# GAME CLASS CREATION

# manages which part of game you're in, game states, event handling and rendering
class Game:
    def __init__(self):
        self.background_colour = (130, 170, 150)
        pygame.display.set_caption("Bubble Shooter")
        self.clock = pygame.time.Clock()  # to set fps
        self.font = pygame.font.SysFont("Arial", 30)
        self.username = []  # contains user's input

        self.colour = select_colour()
        self.queue_list = [select_colour(), select_colour(), select_colour()]

        self.shooter_group = pygame.sprite.Group()  # group for shooters to be added to
        self.floating_group = pygame.sprite.Group()  # group for floaters to be added to

        self.running = True  # running state
        self.in_menu = True  # condition for being in menu - prevent loading game immediately
        self.collision = False  # condition for collision occuring
        self.game_over = False  # condition for game lost / not in game
        self.game_won = False   # condition for grid being cleared

        self.game_won_screen = pygame.image.load("gamewon.drawio.png")
        self.game_won_screen = pygame.transform.scale(self.game_won_screen, (300, 200))
        self.game_over_screen = pygame.image.load("gameover.drawio.png")
        self.game_over_screen = pygame.transform.scale(self.game_over_screen, (300, 200))

# loading screen / username entry screen
    def start_screen(self):
        # convert username list to string so it can be drawn to screen
        temp_username = "".join(self.username)
        title = self.font.render("Enter Username", True, (0, 0, 0))
        enter_user = self.font.render(temp_username, True, (0, 0, 0))
        instruction = self.font.render("Press ENTER to start!", True, (0, 0, 0))

        # draw text onto screen
        SCREEN.blit(title, (200, 150))
        SCREEN.blit(enter_user, (200, 250))
        SCREEN.blit(instruction, (200, 350))

# draw leaderboard at end of game
    def leaderboard(self):
        # original text coordinates
        placement_x = WINDOW_WIDTH - 450
        placement_y = 20

        top_scores = top_five()

        # draws a red rectangular background if you lose, green if you win
        if self.game_over:
            pygame.draw.rect(SCREEN, (122, 59, 59), (WINDOW_WIDTH - 460, 18, 260, 230))
        else:
            pygame.draw.rect(SCREEN, (157, 222, 113), (WINDOW_WIDTH - 460, 18, 260, 230))

        title = self.font.render("Leaderboard", True, (0, 0, 0))
        SCREEN.blit(title, (placement_x, placement_y))

        # move down name and score equally
        for i in range(len(top_scores)):
            placement_y += 40
            show_user = self.font.render(str(top_scores[i][0]), True, (0, 0, 0))
            show_score = self.font.render(str(top_scores[i][1]), True, (0, 0, 0))
            SCREEN.blit(show_user, (placement_x, placement_y))
            SCREEN.blit(show_score, (placement_x + 200, placement_y))

# displays game over or game won screens
    def show_screens(self):
        if self.game_over:
            SCREEN.fill(self.background_colour)
            SCREEN.blit(self.game_over_screen, (20, 20))
            self.leaderboard()
        elif self.game_won:
            SCREEN.fill(self.background_colour)
            SCREEN.blit(self.game_won_screen, (20, 20))
            self.leaderboard()

# main game loop
    def  main(self):
        # setting up shooter, grid and score objects
        shooter = Bubble(self.queue_list[0], SHOOTER_X, SHOOTER_Y)
        self.shooter_group.add(shooter)
        grid = Grid()
        grid.fill_grid()
        score = Score()

        # everything that updates during runtime loops here
        while self.running:
            self.clock.tick(60)  # fps set to 60

            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # allows program to be exited
                    self.running = False

                #  functions which occur when left click (shoot)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.game_over and not self.game_won:

                        # shooting occurs if currently in a game
                        if not shooter.released and shooter.valid_shot_check():
                            for bubbles in self.shooter_group:
                                if bubbles.timeout:
                                    break
                            else:
                                shooter.shooting()
                                self.queue_list.pop(0)
                                self.queue_list.append(select_colour())

                # game resets when game is not in play and space is pressed
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.game_over or self.game_won:
                        self.game_over = False
                        self.game_won = False

                        self.queue_list = [select_colour(), select_colour(), select_colour()]
                        shooter = Bubble(self.queue_list[0], SHOOTER_X, SHOOTER_Y)
                        self.shooter_group.add(shooter)

                        grid = Grid()
                        grid.fill_grid()
                        score.score_reset()

                # when in start screen, pressing ENTER saves username and starts the main game
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.in_menu:
                    save_recent(self.username, 0)
                    self.in_menu = False

                elif event.type == pygame.KEYDOWN and self.in_menu and event.key == pygame.K_BACKSPACE:
                    if len(self.username) > 0:
                        self.username.pop(-1)

                # limits the length of the username otherwise adds character to the list
                elif event.type == pygame.KEYDOWN and self.in_menu and len(self.username) <= 9:
                    try:
                        self.username.append(chr(event.key))
                    except ValueError:
                        pass

            if self.in_menu:
                self.start_screen()

            # following occurs when start screen exits
            else:
                SCREEN.fill(self.background_colour)
                shooter.trajectory()

                self.shooter_group.update()  # updates shooter sprite group

                # collision detection between shooter and any bubble from grid
                for current_bubble in self.shooter_group:
                    self.collision = pygame.sprite.spritecollideany(current_bubble, grid.gridbubble_group)

                    # if collision found, bubble stops moving and snaps to nearest position on grid
                    if self.collision is not None:
                        grid.snap(current_bubble, self.collision)

                        # bubble changes from a shooter object to a grid object
                        self.shooter_group.remove(current_bubble)
                        grid.gridbubble_group.add(current_bubble)

                        # uses colour matching function for shooter bubble
                        self.matching = grid.match_colour(current_bubble)

                        # if 3  or more bubbles of same colour collided, they are popped
                        if len(self.matching) >= 3:
                            for connected_bubbles in self.matching:
                                grid.gridbubble_group.remove(connected_bubbles)
                                connected_bubbles.kill()

                            # checks for floating bubbles and kills them
                            for bubbles in grid.drop_floating():
                                self.floating_group.add(bubbles)
                                bubbles.falling = True

                            # calculates the score for that turn and increases multiplier
                            score.matching_score(len(self.matching))
                            score.floating_score(len(self.floating_group))
                            score.bubble_streak_multiplier += 1

                            # updates the scores being drawn and saves to JSON
                            if score.highest_score < score.total_score:
                                score.highest_score = score.total_score
                                save_recent(self.username, score.highest_score)
                                top_five()

                        else:
                            score.streak_reset()
                            grid.new_row()


                # this tests for the bubbles below the line
                # game over to allow reset
                # stops loop to stop checking for further bubbles
                for bubbles in grid.gridbubble_group:
                    if grid.elimination_test(bubbles):
                        self.game_over = True
                        break

                # draws and updates all objects to screen

                self.shooter_group.draw(SCREEN)
                pygame.draw.circle(SCREEN, self.queue_list[1], ((SHOOTER_X + QUEUE_SPACING), SHOOTER_Y), BUBBLE_RADIUS)
                pygame.draw.circle(SCREEN, self.queue_list[2], ((SHOOTER_X + 2 * QUEUE_SPACING), SHOOTER_Y), BUBBLE_RADIUS)

                grid.elimination_line()

                self.floating_group.update()
                self.floating_group.draw(SCREEN)

                grid.gridbubble_group.update()
                grid.gridbubble_group.draw(SCREEN)

                score.game_score()

                # if a shooter has been released, a new one is made
                if shooter.released:
                    shooter = Bubble(self.queue_list[0], SHOOTER_X, SHOOTER_Y)
                    self.shooter_group.add(shooter)

                if len(grid.gridbubble_group) == 0:
                    self.game_won = True

                self.show_screens()

            pygame.display.flip()  # updates visuals only things that have changed (e.g bubble positions)
            SCREEN.fill(self.background_colour)

        pygame.quit()


# allows program to be run
if __name__ == "__main__":
    FullGame = Game()
    FullGame.main()
    