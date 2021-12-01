"""
File: asteroids.py
Original Author: Br. Burton
Designed to be completed by others
This program implements the asteroids game.
"""
import arcade
import math
from abc import abstractmethod, ABC
import random
import time

# These are Global constants to use throughout the game
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

BULLET_RADIUS = 30
BULLET_SPEED = 10
BULLET_LIFE = 60

SHIP_TURN_AMOUNT = 3
SHIP_THRUST_AMOUNT = 0.25
SHIP_RADIUS = float(30)

INITIAL_ROCK_COUNT = 3

BIG_ROCK_SPIN = 1
BIG_ROCK_SPEED = 1.5
BIG_ROCK_RADIUS = 15

MED_ROCK_SPIN = -2
MED_ROCK_RADIUS = 5

SMALL_ROCK_SPIN = 5
SMALL_ROCK_RADIUS = 2

SHIELD_HEALTH = 1000

class Point:
    def __init__(self): # initializes point to a random spot in a 100 pixel margin of the windows edge.
        self.x = random.randint(100, SCREEN_WIDTH-100)
        self.y = random.randint(100, SCREEN_HEIGHT-100)
        
class Velocity: # initializes velocity values to zero.
    def __init__(self):
        self.dx = 0
        self.dy = 0

class Flying_Object(ABC): # Abstract class, will be used in asteroids, lasers, and ships
    def __init__(self, radius):
        self.center = Point()
        self.velocity = Velocity()
        self.alive = True
        self.radius = radius
        self.speed = None  # sometimes used to simplify passing of velocity values, not absolutely necessary but this made more sense in my brain
        self.angle = random.randint(0,360) # Random init value really just used for the asteroids, laser and ships angles will be initialized later
        
    def advance(self):  # Advances movement of all the things
        self.center.x += self.velocity.dx
        self.center.y += self.velocity.dy
        
    @abstractmethod
    def draw(self):
        pass

class Ship(Flying_Object):
    def __init__(self):
        super().__init__(SHIP_RADIUS)
        self.angle = 0
        self.texture = arcade.load_texture("ship.png") # Enemy ship will use this texture throughout its life. Enemy ship dies after 1 hit. Player ship will have more textures later on, and 3 hits.
        self.center.x = SCREEN_WIDTH/2
        self.center.y = SCREEN_HEIGHT/2
        self.state = 1  # used to determine the *damaged* state of the ship, which texture to use
        self.collide_time = 0 # used later to prevent from repeat collisions each frame
        self.shield = SHIELD_HEALTH
        self.protect = False
        self.shield_texture = arcade.load_texture("shield.png")
    def draw(self):
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.radius*2, self.radius*2, self.texture, self.angle-90)
    def accelerate(self):
        self.velocity.dx += .25*math.cos(math.radians(self.angle))
        self.velocity.dy += .25*math.sin(math.radians(self.angle))
    def deccelerate(self):
        self.velocity.dx *= .98  #  -= .25*math.cos(math.radians(self.angle))    # Commented out code is a different method of decceleration.
        self.velocity.dy *= .98  #  -= .25*math.sin(math.radians(self.angle))    # Current method will slow from very high speeds much faster
    def turn(self, value):
        self.angle += value
    def collide(self):    # Each collision consists of two state iterations. State 6 is death
        self.state += 1
        if self.state == 6:
            self.alive = False
    def power_shield(self):
        self.shield -= 1
    def draw_shield(self):
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.radius*2.5, self.radius*2.5, self.shield_texture, self.angle)
    
        
class Laser(Flying_Object):
    def __init__(self, x, y, speed, angle, bad):
        super().__init__(30)
        self.center.x = x
        self.center.y = y
        self.angle = angle
        self.bad = bad     # Used to differentiate player lasers from enemy lasers
        self.velocity.dx = (speed+10)*math.cos(math.radians(self.angle))
        self.velocity.dy = (speed+10)*math.sin(math.radians(self.angle))
        self.age = 0       # Age in frames
        self.texture = arcade.load_texture("laser.png")
    def draw(self):
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.texture.width, self.texture.height, self.texture, self.angle)

class Asteroid(Flying_Object, ABC):
    def __init__(self, spinvalue, radius):
        super().__init__(radius)
        self.spinval = spinvalue
    def spin(self):   # Continuously spinning the asteroids.
        self.angle += self.spinval
    @abstractmethod
    def draw(self):
        pass
    @abstractmethod
    def collide(self):
        pass
    @property
    def angle(self):
        return self._angle
    @angle.setter
    def angle(self, angle):   # Angle will always be between 0 and 360
        if angle > 360:
            self._angle = 0
        else:
            self._angle = angle
        
class Large(Asteroid):
    def __init__(self):
        super().__init__(BIG_ROCK_SPIN,  BIG_ROCK_RADIUS)
        self.texture = arcade.load_texture("big.png")
        self.speed = BIG_ROCK_SPEED
        self.velocity.dx = self.speed*math.cos(math.radians(self.angle)) # velocities calculated using speed value
        self.velocity.dy = self.speed*math.sin(math.radians(self.angle))
    def draw(self):
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.texture.width, self.texture.height, self.texture, self.angle)
    def collide(self):   # Collide will set current asteroid to dead and return a list of new asteroids, which will be added to the games asteroid list. Same concept for each rock.
        self.alive = False 
        return [Med(self.center.x, self.center.y, self.velocity.dx, self.velocity.dy+2), Med(self.center.x, self.center.y, self.velocity.dx, self.velocity.dy-2),
                Small(self.center.x, self.center.y, self.velocity.dx+5, self.velocity.dy)]
    
class Med(Asteroid):
    def __init__(self, x, y, dx, dy):
        super().__init__(MED_ROCK_SPIN,  MED_ROCK_RADIUS)
        self.texture = arcade.load_texture("medium.png")
        self.center.x = x
        self.center.y = y
        self.velocity.dx = dx
        self.velocity.dy = dy
    def draw(self):
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.texture.width, self.texture.height, self.texture, self.angle)
    def collide(self):
        self.alive = False
        return [Small(self.center.x, self.center.y, self.velocity.dx+1.5, self.velocity.dy+1.5), Small(self.center.x, self.center.y, self.velocity.dx-1.5, self.velocity.dy-1.5)]
    
class Small(Asteroid):
    def __init__(self, x, y, dx, dy):
        super().__init__(SMALL_ROCK_SPIN,  SMALL_ROCK_RADIUS)
        self.texture = arcade.load_texture("small.png")
        self.center.x = x
        self.center.y = y
        self.velocity.dx = dx
        self.velocity.dy = dy
    def draw(self):
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.texture.width, self.texture.height, self.texture, self.angle)
    def collide(self):
        self.alive = False
        return [] # small asteroid returns no other rocks

class Game(arcade.Window):
    """
    This class handles all the game callbacks and interaction
    This class will then call the appropriate functions of
    each of the above classes.
    """

    def __init__(self, width, height):
        """
        Sets up the initial conditions of the game
        :param width: Screen width
        :param height: Screen height
        """
        super().__init__(width, height)
        #arcade.set_background_color(arcade.color.SMOKY_BLACK)

        self.held_keys = set()
        self.ship = Ship()
        self.enemy_angle = 0
        self.attack_angle = 0
        self.enemy = Ship()
#         self.enemy2 = Ship()
        self.enemy_speed = 2
        self.lasers = []
        self.asteroids = []
        self.frame_count = 0
        for i in range(INITIAL_ROCK_COUNT):
            self.asteroids.append(Large())
            
        self.time_up = True
        self.score = 0
        self.background = arcade.load_texture("galaxy.jpg")   # I could never get this working. I NEED TO GET THIS WORKING
        self.time = time.time()
        self.fired = False
        self.victory = 0    # 0: game still in progress, 1: Victory, display victory message, 2: Loss, display loss message 
        
    def on_draw(self):
        """
        Called automatically by the arcade framework.
        Handles the responsibility of drawing all elements.
        """
        # clear the screen to begin drawing
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        
        arcade.start_render()
        
        if self.ship.alive == True and self.victory == 0: # once ship is dead or game is over, the ship it will not be drawn
            self.ship.draw()
        for i in self.lasers:
            i.draw()
        
        for i in self.asteroids:
            i.draw()
            
        self.draw_score()
        self.draw_shield_health()
        
        if self.enemy.alive: # once enemy is dead it will not be drawn
            self.enemy.draw()
        
        if self.victory == 1:
            self.draw_victory()
        elif self.victory == 2:
            self.draw_loss()
        
    def draw_score(self):
        """
        Puts the current score on the screen
        """
        score_text = "Score is: {}".format(self.score)
        start_x = 30
        start_y = SCREEN_HEIGHT - 40
        arcade.draw_text(score_text, start_x=start_x, start_y=start_y, font_size=12, color=arcade.color.WHITE)
    
    def draw_shield_health(self):
        """
        Displays remaining shield percentage
        """
        shield_percentage = int((self.ship.shield / SHIELD_HEALTH)*100)
        shield_text = "Shield remaining: {}%".format(shield_percentage)
        start_x = 30
        start_y = SCREEN_HEIGHT - 120
        arcade.draw_text(shield_text, start_x=start_x, start_y=start_y, font_size=20, color=arcade.color.WHITE)
    
    def draw_victory(self):
        """
        Puts the victory message on screen
        """
        victory_text = "Victory! You have won! You score is: {}".format(self.score)
        start_x = 150
        start_y = SCREEN_HEIGHT / 2
        arcade.draw_text(victory_text, start_x=start_x, start_y=start_y, font_size=50, color=arcade.color.WHITE)
        
    def draw_loss(self):
        """
        Puts the loss message on screen
        """
        loss_text = "Game Over!! You scored: {}".format(self.score)
        start_x = 600
        start_y = SCREEN_HEIGHT / 2
        arcade.draw_text(loss_text, start_x=start_x, start_y=start_y, font_size=45, color=arcade.color.WHITE)
    
    def enemy_move(self):
        if self.enemy.alive: # We only want the enemy to do things if it is still alive
            self.enemy.velocity.dx = self.enemy_speed*math.cos(math.radians(self.enemy_angle))
            self.enemy.velocity.dy = self.enemy_speed*math.sin(math.radians(self.enemy_angle))
            if self.enemy_speed < 10:
                self.enemy_speed = self.enemy_speed*1.0013
            
            x_delta = self.ship.center.x - self.enemy.center.x   # space between enemy and player ship
            y_delta = self.ship.center.y - self.enemy.center.y
            self.attack_angle = math.degrees(math.atan(y_delta/(x_delta+.001)))   # angle the enemy ship is pointing, but not traveling
            if self.ship.center.x < self.enemy.center.x:
                self.attack_angle += 180
            self.enemy.angle = self.attack_angle
        
    def enemy_attack(self):
        if self.enemy.alive:  # We only want the enemy to do things if it is still alive
            speed = math.sqrt(self.enemy.velocity.dx**2+ self.enemy.velocity.dy**2)
            self.lasers.append(Laser(self.enemy.center.x, self.enemy.center.y,
                                        speed-3, self.attack_angle, True))
        
    def check_collisions(self):

        for laser in self.lasers:
            for ast in self.asteroids:

                # Make sure they are both alive before checking for a collision
                if laser.alive and not laser.bad and ast.alive:  # enemy lasers only destroy the player ship, they do not destroy asteroids
                    too_close = laser.radius + ast.radius

                    if (abs(laser.center.x - ast.center.x) < too_close and
                                abs(laser.center.y - ast.center.y) < too_close):
                        # its a hit!
                        laser.alive = False
                        new_rocks = ast.collide() #list returned from collide function
                        self.score += 1
                        if len(new_rocks)>0:  # if list isn't empty, list items added to asteroids
                            for i in new_rocks:
                                self.asteroids.append(i)
        for ast in self.asteroids:
            if self.ship.alive and ast.alive and self.ship.protect == False:
                too_close = self.ship.radius + ast.radius
                if (abs(self.ship.center.x - ast.center.x) < too_close and
                            abs(self.ship.center.y - ast.center.y) < too_close):
                    if self.ship.collide_time == 0:
                        self.ship.collide()
                        self.time_up = False # time up feature used to prevent a collision per frame while objects are passing by each other
                       
        for las in self.lasers:
            if self.ship.alive and las.alive and las.bad and self.ship.protect == False:
                too_close = self.ship.radius + las.radius
                if (abs(self.ship.center.x - las.center.x) < too_close and
                            abs(self.ship.center.y - las.center.y) < too_close):
                    if self.ship.collide_time == 0:
                        self.ship.collide()
                        self.time_up = False
                        
        for las in self.lasers:
            if self.enemy.alive and las.alive and not las.bad:
                too_close = self.enemy.radius + las.radius
                if (abs(self.enemy.center.x - las.center.x) < too_close and
                            abs(self.enemy.center.y - las.center.y) < too_close):
                    if self.enemy.collide_time == 0:
                        las.alive = False
                        self.enemy.collide()
                        self.time_up = False
                        print("Collide")

    def cleanup_zombies(self):
        """
        Removes any dead bullets or targets from the list.
        :return:
        """
        for laser in self.lasers:
            if not laser.alive:
                self.lasers.remove(laser)
                
        for ast in self.asteroids:
            if not ast.alive:
                self.asteroids.remove(ast)

    def update(self, delta_time):
        """
        Update each object in the game.
        :param delta_time: tells us how much time has actually elapsed
        """
        self.check_keys()
        self.ship.advance()
        self.enemy.advance()
        self.wrap(self.enemy)
        self.wrap(self.ship)
        self.cleanup_zombies()
        self.enemy_move()
        print(str(self.ship.shield))
        
        if self.ship.shield == 0:
            self.ship.protect = False
        
        for i in self.lasers:  # age of each laser iterated, and each laser is advanced and wrapped. same for asteroids below.
            i.age += 1
            i.advance()
            self.wrap(i)
            if i.age == 60:
                i.alive = False
        for i in self.asteroids:
            i.spin()
            i.advance()
            self.wrap(i)
            
        self.check_collisions()
        
        if self.ship.state == 2:
            self.ship.texture = arcade.load_texture("ship2.png") # loads next damage texture when collision happens
            self.ship.state = 3
            
        if self.ship.state == 4:
            self.ship.texture = arcade.load_texture("ship3.png") # loads next damage texture when collision happens
            self.ship.state == 5
            
        if self.ship.state in [3,5] and self.time_up == False: #This starts and stops a frame based timer that prevents multiple collide functions from occuring during a single collision
            self.ship.collide_time += 1
            if self.ship.collide_time > 100:
                self.time_up = True
                self.ship.collide_time = 0
        
        if abs(time.time() - self.time) > 1:
            self.enemy_angle = random.randint(0,360)
            self.time = time.time()
        
        self.frame_count += 1   # enemy attacks start after 180 frames, and will occur every 60 frames
        if self.frame_count > 180 and self.frame_count % 60 == 0:
            self.enemy_attack()
            
        if self.score == (INITIAL_ROCK_COUNT * 8):
            self.victory = 1
        
        if self.ship.alive == False and self.score < (INITIAL_ROCK_COUNT * 8):
            self.victory = 2

    def check_keys(self):
        """
        This function checks for keys that are being held down.
        You will need to put your own method calls in here.
        """
        if arcade.key.LEFT in self.held_keys:
            self.ship.turn(SHIP_TURN_AMOUNT)

        if arcade.key.RIGHT in self.held_keys:
            self.ship.turn(-SHIP_TURN_AMOUNT)

        if arcade.key.UP in self.held_keys:
            self.ship.accelerate()

        if arcade.key.DOWN in self.held_keys:
            self.ship.deccelerate()
            
        if arcade.key.S in self.held_keys and self.ship.shield > 0:
            self.ship.power_shield()
            self.ship.draw_shield()
            self.ship.protect = True
    
    def wrap(self, item):   # wraps items around screen
        if item.center.x > SCREEN_WIDTH:
            item.center.x = 0
        if item.center.x < 0:
            item.center.x = SCREEN_WIDTH
        if item.center.y > SCREEN_HEIGHT:
            item.center.y = 0
        if item.center.y < 0:
            item.center.y = SCREEN_HEIGHT

    def on_key_press(self, key: int, modifiers: int):
        """
        Puts the current key in the set of keys that are being held.
        You will need to add things here to handle firing the bullet.
        """
        if self.ship.alive:
            self.held_keys.add(key)

            if key == arcade.key.SPACE:
                # TODO: Fire the bullet here!
                speed = math.sqrt(self.ship.velocity.dx**2+ self.ship.velocity.dy**2)
                self.lasers.append(Laser(self.ship.center.x, self.ship.center.y,  # adds laser to laser list when space bar is pressed
                                         speed, self.ship.angle, False))
            #if key == arcade.key.S and self.ship.shield > 0:
            #    self.ship.protect = True

    def on_key_release(self, key: int, modifiers: int):
        """
        Removes the current key from the set of held keys.
        """
        if key in self.held_keys:
            self.held_keys.remove(key)
        if key == arcade.key.S:
            self.ship.protect = False


# Creates the game and gets it going
window = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
arcade.run()