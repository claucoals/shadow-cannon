# ======================================================================
# SHADOW GAME
# BY CLAUDIA MARIA CARBONI (535421) AND SUSANNA MAZZOCCHI (535996)
# COMPUTER PROGRAMMING EXAM
# ======================================================================


import random
import time
from math import sin, cos, radians
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder
from kivy.graphics import Rectangle, Rotate, PushMatrix, PopMatrix, Color, Line
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.core.audio import SoundLoader





# ======================================================================
# Constants to help code readability
# ======================================================================

# Game Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

FPS = 60  # Frames per second

# Projectile parameters
BULLET_MASS = 10  
BOMB_MASS = 20    
BULLET_RADIUS = 17.5  
BOMB_RADIUS = 17.5   

# Laser parameters
LASER_DIST = 1000     # Maximum laser range
LASER_VEL = 500      # Fixed laser velocity
LASER_IMPULSE = 3000  # Laser force on impact

# Variabile globale
current_level = 1

# Carica il file KV manualmente
Builder.load_file("menu.kv")
Builder.load_file("Level1Game.kv")
Builder.load_file("Level2Game.kv")
Builder.load_file("Level3Game.kv")
Builder.load_file("Level4Game.kv")
Builder.load_file('congrats.kv')





#=======================================================================
# Score Timer class
#=======================================================================
class Timer:
    def __init__(self, label):
        self.label = label
        self.seconds = 0
        self.minutes = 0
        self.running = False

    def start(self):
        self.running = True
        Clock.schedule_interval(self.update, 1)

    def stop(self):
        self.running = False
        Clock.unschedule(self.update)

    def reset(self):
        self.seconds = 0
        self.minutes = 0
        self.update_label()

    def update(self, dt):
        self.seconds += 1
        if self.seconds >= 60:
            self.seconds = 0
            self.minutes += 1
        self.update_label()

    def update_label(self):
        self.label.text = f"{self.minutes:02}:{self.seconds:02}"








# =======================================================================
# CannonLevel1 Class
# =======================================================================
class CannonLevel1(Widget):
    """
    A class representing the first level of the cannon game.
    This class handles the game logic, including shooting, collisions, and level reset.
    """

    # Class properties
    angle_int_deg = NumericProperty(50)  # Initial angle of the cannon
    shots_left = NumericProperty(15)     # Number of shots remaining

    def __init__(self, **kwargs):
        """
        Initialize the CannonLevel1 class.
        Sets up the game environment, including obstacles, cannon, and initial properties.
        """
        super(CannonLevel1, self).__init__(**kwargs)

        # Initialize game state variables
        self.start_time = time.time()  # Track the start time of the level
        self.popup_visible = False     # Track if a popup is currently visible
        self.velocity = 0              # Initial velocity of the cannonball
        self.velocity_clock = 0        # Clock for updating cannonball position
        self.velocity_x = 0            # Horizontal velocity component
        self.velocity_y = 0            # Vertical velocity component
        self.angle = 0                 # Current angle of the cannon
        self.update_shots_label()      # Update the shots label on the UI

        # Create static elements (obstacles, targets, etc.)
        self.create_static_elements()

        # Create the rotating cannon and cannonball
        self.create_cannon()


    # =======================================================================
    # Static Element Creation
    # =======================================================================
    def create_static_elements(self):
        """
        Create static elements such as obstacles and targets.
        """
        with self.canvas.before:
            # Create perpetual obstacles (2 rows x 3 columns)
            self.perpetuos = []
            for row in range(2):
                for col in range(3):
                    perpetuo = Rectangle(
                        size=(150, 150),
                        pos=(450 + col * 110, 0 + row * 110),
                        source="images/perpetuo-obstacle1.png"
                    )
                    self.perpetuos.append(perpetuo)

            # Create ghost target (to the right of the perpetual obstacles)
            self.ghost = Rectangle(
                size=(150, 150),
                pos=(1050, 100),
                source="images/ghost.png"
            )

            # Create rock obstacles (3 rows x 5 columns)
            self.obstacles = []
            for row in range(3):
                for col in range(5):
                    rock = Rectangle(
                        size=(150, 150),
                        pos=(450 + col * 110, 250 + row * 110),
                        source="images/rock-obstacle1.png"
                    )
                    self.obstacles.append(rock)


    # =======================================================================
    # Cannon Creation
    # =======================================================================
    def create_cannon(self):
        """
        Create the rotating cannon and cannonball.
        """
        with self.canvas:
            PushMatrix()
            self.rotate = Rotate(origin=(80, 30), angle=self.angle)
            self.cannon = Rectangle(
                size=(200, 150),
                pos=(50, 50),
                source="images/cannon1.png"
            )
            PopMatrix()

            self.cannonball = Rectangle(
                size=(25, 25),
                pos=(-100, -100),
                source="images/bullet.png"
            )

    # =======================================================================
    # Game Logic Methods
    # =======================================================================
    def set_velocity(self, velocity):
        """
        Set the velocity of the cannonball.
        """
        try:
            v = int(velocity)
            if v > 0:  # Velocity must be greater than 0
                self.velocity = v
        except ValueError:
            pass  # Ignore invalid inputs

    def set_angle(self, angle):
        """
        Set the angle of the cannon.
        """
        try:
            a = int(angle)
            if -1 < a <= 90:  # Angle must be between 0 and 90 degrees
                self.angle = a
                self.rotate.angle = self.angle
        except ValueError:
            pass  # Ignore invalid inputs


    def shoot(self):
        """
        Handle the shooting logic.
        Decrements the shot count, updates the UI, and starts the cannonball movement.
        """
        if self.shots_left <= 0:  # Check if shots are available
            self.show_game_over_popup()
            return

        # Decrement shots and update the label
        self.shots_left -= 1
        self.update_shots_label()

        # Position the cannonball at the cannon's mouth
        self.cannonball.pos = (
            int(self.cannon.pos[0] + cos(radians(self.angle)) * self.cannon.size[0] / 2),
            int(self.cannon.pos[1] + sin(radians(self.angle)) * self.cannon.size[1] / 2)
        )

        # Start the clock for updating cannonball position
        self.velocity_clock = Clock.schedule_interval(self.drop, 0.1)

        # Calculate velocity components based on the angle
        self.velocity_y = self.velocity * sin(radians(self.angle))
        self.velocity_x = self.velocity * cos(radians(self.angle))

    def drop(self, dt):
        """
        Update the cannonball's position and handle collisions.
        """
        # Update cannonball position
        new_x = self.cannonball.pos[0] + self.velocity_x
        new_y = self.cannonball.pos[1] + self.velocity_y
        self.cannonball.pos = (new_x, new_y)

        # Apply gravity
        self.velocity_y -= 0.98

        # Check for collisions
        self.check_collisions()

        # Check if the cannonball is out of bounds
        if new_x > Window.width or new_y < 0 or new_x < 0:
            self.reset_cannonball()

    def check_collisions(self):
        """
        Check for collisions with the ghost target, obstacles, and perpetual obstacles.
        """
        ball_left = self.cannonball.pos[0]
        ball_right = ball_left + self.cannonball.size[0]
        ball_bottom = self.cannonball.pos[1]
        ball_top = ball_bottom + self.cannonball.size[1]

        # Collision with the ghost target
        ghost_left = self.ghost.pos[0]
        ghost_right = ghost_left + self.ghost.size[0]
        ghost_bottom = self.ghost.pos[1]
        ghost_top = ghost_bottom + self.ghost.size[1]

        if (ball_right > ghost_left and ball_left < ghost_right and
                ball_top > ghost_bottom and ball_bottom < ghost_top):
            self.hit_target()
            self.reset_cannonball()

        # Collision with destructible obstacles
        for obstacle in self.obstacles[:]:
            if obstacle.pos[0] != -1000:  # If the obstacle is not destroyed
                obs_left = obstacle.pos[0]
                obs_right = obs_left + obstacle.size[0]
                obs_bottom = obstacle.pos[1]
                obs_top = obs_bottom + obstacle.size[1]

                if (ball_right > obs_left and ball_left < obs_right and
                        ball_top > obs_bottom and ball_bottom < obs_top):
                    obstacle.pos = (-1000, -1000)  # Destroy the obstacle
                    self.reset_cannonball()

        # Collision with perpetual obstacles
        for perpetuo in self.perpetuos:
            perp_left = perpetuo.pos[0]
            perp_right = perp_left + perpetuo.size[0]
            perp_bottom = perpetuo.pos[1]
            perp_top = perp_bottom + perpetuo.size[1]

            if (ball_right > perp_left and ball_left < perp_right and
                    ball_top > perp_bottom and ball_bottom < perp_top):
                self.show_perpetuo_error()
                self.reset_cannonball()

    def reset_cannonball(self):
        """
        Reset the cannonball's position and stop the movement clock.
        """
        self.cannonball.pos = (-100, -100)
        if self.velocity_clock:
            Clock.unschedule(self.velocity_clock)
            self.velocity_clock = 0


    # =======================================================================
    # UI Update Methods
    # =======================================================================
    def update_shots_label(self):
        """
        Update the shots label on the UI.
        """
        app = App.get_running_app()
        if app.root:
            level_screen = app.root.get_screen('level1game')
            level_screen.ids.shots_label.text = f"Number of shots: {self.shots_left}/15"


    # =======================================================================
    # Popup Handling Methods
    # =======================================================================
    def show_game_over_popup(self):
        """
        Show the game over popup when the player runs out of shots.
        """
        if not self.popup_visible:
            self.popup_visible = True
            content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)

            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(
                text="Try Again",
                font_size=18,
                size_hint=(None, None),
                size=(200, 50),
                background_color=[0.5, 0, 0, 1],
                color=[1, 1, 1, 1]
            )

            button_layout.add_widget(button)
            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)
            content.add_widget(button_layout)

            self.P = Popup(
                title="Game Over! You ran out of shots!",
                title_align='center',
                title_size=30,
                title_color=[0.5, 0, 0, 1],
                content=content,
                size_hint=(None, None),
                size=(500, 300),
                background='images/popup.png',
                auto_dismiss=False
            )

            button.bind(on_press=lambda x: self.reset_and_dismiss())
            self.P.open()

    def show_perpetuo_error(self):
        """
        Show a popup when the player hits a perpetual obstacle.
        """
        if not self.popup_visible:
            self.popup_visible = True

            content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)

            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(
                text="Try Again",
                font_size=18,
                size_hint=(None, None),
                size=(200, 50),
                background_color=[0.5, 0, 0, 1],
                color=[1, 1, 1, 1]
            )

            button_layout.add_widget(button)
            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)
            content.add_widget(button_layout)

            self.P = Popup(
                title="You can't destroy Perpetuo!",
                title_align='center',
                title_size=30,
                title_color=[0.5, 0, 0, 1],
                content=content,
                size_hint=(None, None),
                size=(500, 300),
                background='images/popup.png',
                auto_dismiss=False
            )

            button.bind(on_press=self.dismiss_popup)
            self.P.open()

    def dismiss_popup(self, instance):
        """
        Dismiss the current popup.
        """
        self.P.dismiss()
        self.popup_visible = False

    def reset_and_dismiss(self):
        """
        Reset the level and dismiss the popup.
        """
        if hasattr(self, 'P'):
            self.P.dismiss()
        self.popup_visible = False
        self.reset_level()


    # =======================================================================
    # Level Reset Methods
    # =======================================================================
    def reset_level(self):
        """
        Reset the level to its initial state.
        """
        # Reset shot count
        self.shots_left = 15
        self.update_shots_label()

        # Reset cannonball position
        self.reset_cannonball()

        # Reset obstacles
        for obstacle in self.obstacles:
            if obstacle.pos[0] == -1000:  # If the obstacle was destroyed
                idx = self.obstacles.index(obstacle)
                row = idx // 5
                col = idx % 5
                obstacle.pos = (450 + col * 110, 250 + row * 110)

        # Reset the timer
        self.start_time = time.time()

    # =======================================================================
    # Target Hit Handling
    # =======================================================================
    def hit_target(self):
        """
        Handle the logic when the target is hit.
        """
        global current_level
        elapsed_time = time.time() - self.start_time

        # Add the record to the Hall of Fame
        app = App.get_running_app()
        hall_of_fame = app.root.get_screen('halloffame')
        hall_of_fame.add_record(f'level{current_level}', elapsed_time)


        # Create the popup content
        content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)

        label_space_left = Label(size_hint_x=1)
        button_layout.add_widget(label_space_left)

        button = Button(
            text=f'Next Level\nTime: {elapsed_time:.2f} sec',
            font_size=18,
            size_hint=(None, None),
            size=(200, 50),
            background_color=[0, 0.5, 0, 1],
            color=[1, 1, 1, 1]
        )

        button_layout.add_widget(button)
        label_space_right = Label(size_hint_x=1)
        button_layout.add_widget(label_space_right)
        content.add_widget(button_layout)

        # Create the popup
        self.P = Popup(
            title="Great Shot! Next Level Unlocked!",
            title_align='center',
            title_size=40,
            title_color=[0, 0.3, 0, 1],
            content=content,
            size_hint=(None, None),
            size=(500, 350),
            background='images/popup.png',
            auto_dismiss=False
        )

        # Bind the button to dismiss the popup and proceed to the next level
        button.bind(on_press=self.P.dismiss)
        button.bind(on_press=self.next_level)
        self.P.open()

    def next_level(self, instance):
        """
        Proceed to the next level.
        """
        app = App.get_running_app()
        screen_manager = app.root
        if hasattr(screen_manager, 'current'):
            screen_manager.current = 'level2game'
            if hasattr(self, 'P') and self.P:
                self.P.dismiss()











#=======================================================================
# CannonLevel2 class
#=======================================================================
class CannonLevel2(Widget):
    angle_int_deg = NumericProperty(50)
    shots_left = NumericProperty(10)

    def __init__(self, **kwargs):
        super(CannonLevel2, self).__init__(**kwargs)
        self.update_shots_label()
        self.start_time = time.time()
        self.popup_visible = False
        self.velocity = 0
        self.velocity_clock = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.angle = 0
        self.x_collide = False
        self.y_collide = False
        self.x_rand = 0
        self.y_rand = 0
        self.current_weapon = "cannon"
        random.seed()
        self.dragon_direction = 1   # Direction of dragon movement
        Clock.schedule_interval(self.move_dragon, 1 / FPS)   # Schedule dragon movement
        self.bind(pos=self.update_rectangles, size=self.update_rectangles)  # Bind position and size changes to update rectangles
        self.pellets = []



        # =======================================================================
        # Static Element Creation
        # =======================================================================
        # Create separate canvas groups for static and rotating elements

        # Create dragon target
        with self.canvas.before:
            self.dragon = Rectangle(size=(120, 200), pos=(self.width - 120, self.height / 2 - 100),
                                    source="images/dragon-target2.png")

            # Create rock and perpetuo obstacles
            self.rock2 = Rectangle(size=(120, 120), pos=(650, 50), source="images/rock2.png")
            self.perpetuo2 = Rectangle(size=(120, 120), pos=(650, 150), source="images/perpetuo2.png")
            self.rock2_above_perpetuo = Rectangle(size=(120, 120), pos=(650, 250), source="images/rock2.png")
            self.perpetuo_above = Rectangle(size=(120, 120), pos=(650, 350), source="images/perpetuo2.png")
            # Aggiungi una nuova rock2 sopra perpetuo_above
            self.rock2_top = Rectangle(size=(120, 120), pos=(650, 450), source="images/rock2.png")
            self.perpetuo_top = Rectangle(size=(120, 120), pos=(650, 550), source="images/perpetuo2.png")

            # Create bats
            self.bats = []
            bat_y_positions = [50, 175, 300, 425, 550, 675]  # Vertical positions for bats

            # Original bats at x=350
            for y_pos in bat_y_positions:
                bat = Rectangle(
                    size=(100, 100),
                    pos=(350, y_pos),
                    source="images/bat-obstacle2.png"
                )
                self.bats.append(bat)

            # New row of bats at x=800 (left of the dragon)
            for y_pos in bat_y_positions:
                bat = Rectangle(
                    size=(100, 100),
                    pos=(800, y_pos),
                    source="images/bat-obstacle2.png"
                )
                self.bats.append(bat)

            # Create additional rock2 obstacles at x=500
            self.rock2_left_1 = Rectangle(size=(120, 120), pos=(500, 50), source="images/rock2.png")
            self.rock2_left_2 = Rectangle(size=(120, 120), pos=(500, 150), source="images/rock2.png")
            self.rock2_left_3 = Rectangle(size=(120, 120), pos=(500, 250), source="images/rock2.png")
            self.rock2_left_4 = Rectangle(size=(120, 120), pos=(500, 350), source="images/rock2.png")
            self.rock2_left_5 = Rectangle(size=(120, 120), pos=(500, 450), source="images/rock2.png")
            self.rock2_left_6 = Rectangle(size=(120, 120), pos=(500, 550), source="images/rock2.png")

        # Wheel goes in its own canvas group
        with self.canvas:
            self.wheel = Rectangle(size=(150, 150), pos=(5, 5), source="images/cannon_wheel2.png")

        # Rotating elements (cannon) go in their own canvas group
        with self.canvas:
            PushMatrix()
            self.rotate = Rotate(origin=(142.5, 12.5), angle=self.angle)
            self.cannon = Rectangle(size=(200, 75), pos=(100, 30), source="images/cannon.png")
            PopMatrix()

        # Cannonball in its own canvas group
        with self.canvas:
            self.cannonball = Rectangle(pos=(-100, -100), size=(35, 35), source="images/bullet.png")


    # =======================================================================
    # UI Update Methods
    # =======================================================================
    def update_rectangles(self, *args):
        # Update wheel position
        wheel_x = self.x + 20
        wheel_y = self.y + 20
        self.wheel.pos = (wheel_x, wheel_y)

        # Update cannon position
        cannon_x = wheel_x + self.wheel.size[0] / 2 - self.cannon.size[0] / 2 + 65
        cannon_y = wheel_y + self.wheel.size[1] - 100
        self.cannon.pos = (cannon_x, cannon_y)

        # Update rotation origin
        self.rotate.origin = (cannon_x + self.cannon.size[0] * 0.5, cannon_y)

        # Update dragon position
        original_width = 250
        original_height = 250
        scale_factor = 1
        self.dragon.size = (original_width * scale_factor, original_height * scale_factor)
        dragon_x = self.width - self.dragon.size[0] + 850
        dragon_y = 20
        self.dragon.pos = (dragon_x, dragon_y)

        # Update rock2_above_perpetuo position
        self.rock2_above_perpetuo.pos = (650, 250)
        self.perpetuo_above.pos = (650, 350)
        self.rock2_top.pos = (650, 450)
        self.perpetuo_top.pos = (650, 550)
        bat_y_positions = [50, 175, 300, 425, 550, 675]

        # Update bat positions
        for i, bat in enumerate(self.bats):
            x_pos = 400 if i < 6 else 800
            y_pos = bat_y_positions[i % 6]
            bat.pos = (x_pos, y_pos)

        # Update rock2 positions
        self.rock2_left_1.pos = (500, 50)
        self.rock2_left_2.pos = (500, 150)
        self.rock2_left_3.pos = (500, 250)
        self.rock2_left_4.pos = (500, 350)
        self.rock2_left_5.pos = (500, 450)
        self.rock2_left_6.pos = (500, 550)


    def update_shots_label(self):
        """
        Update the shots label on the UI.
        """
        app = App.get_running_app()
        if app.root:  # Controlla se root è None
            level_screen = app.root.get_screen('level2game')  # Assicurati che il nome dello schermo sia corretto
            level_screen.ids.shots_label.text = f"Number of shots: {self.shots_left}/10"  # Aggiorna l'etichetta


    # =======================================================================
    # Game Logic Methods
    # =======================================================================
    """
    Switch the current weapon type.
    
    """
    def switch_weapon(self, weapon_type):
        self.current_weapon = weapon_type
        if weapon_type == "shotgun":
            self.cannon.source = "images/cannon.png"
            self.cannonball.source = "images/bullet2.png"
            self.cannonball.size = (BULLET_RADIUS * 2, BULLET_RADIUS * 2)
            self.mass = BULLET_MASS
        else:
            self.cannon.source = "images/cannon.png"
            self.cannonball.source = "images/bullet.png"
            self.cannonball.size = (BOMB_RADIUS * 2, BOMB_RADIUS * 2)
            self.mass = BOMB_MASS

    def fire_cannon(self):
        if self.shots_left <= 0:   # Check if shots are available
            self.show_game_over_popup()
            self.reset_level()  # Reset the level when there are no shots left
            return

        if self.current_weapon == "cannon":
            self.fire_single_shot()
        elif self.current_weapon == "shotgun":
            self.fire_shotgun()

        # Decrement shots and update the label
        self.shots_left -= 1
        self.update_shots_label()


    def fire_single_shot(self):
        """
        Fire a single shot from the cannon.
        """
        self.cannonball.pos = (
            int(self.cannon.pos[0] + cos(radians(self.angle)) * self.cannon.size[0] / 2),
            int(self.cannon.pos[1] + sin(radians(self.angle)) * self.cannon.size[1] / 2)
        )
        self.velocity_clock = Clock.schedule_interval(self.drop, 0.1)
        self.velocity_y = self.velocity * sin(radians(self.angle))
        self.velocity_x = self.velocity * cos(radians(self.angle))

    def fire_shotgun(self):
        """
        Fire multiple pellets from the shotgun.
        """
        for offset in [-10, 0, 10]:
            self.create_pellet(self.angle + offset)

    def create_pellet(self, angle):
        """
        Create a pellet for the shotgun.
        """
        with self.canvas:
            pellet = Rectangle(source="images/bullet2.png", size=(25, 25), pos=self.cannonball.pos)

        # Set initial pellet position
        pellet_x = self.cannon.pos[0] + cos(radians(angle)) * self.cannon.size[0] / 2
        pellet_y = self.cannon.pos[1] + sin(radians(angle)) * self.cannon.size[1] / 2
        pellet.pos = (pellet_x, pellet_y)

        # Calculate velocity components
        pellet_velocity_x = self.velocity * cos(radians(angle))
        pellet_velocity_y = self.velocity * sin(radians(angle))

        # Add pellet to the list
        self.pellets.append((pellet, pellet_velocity_x, pellet_velocity_y))

        # Schedule pellet movement
        Clock.schedule_interval(lambda dt: self.move_pellet(pellet, pellet_velocity_x, pellet_velocity_y), 0.1)

    def move_pellet(self, pellet, velocity_x, velocity_y):
        """
        Move the pellet and handle collisions.
        """
        try:
            # Update pellet position
            new_x = pellet.pos[0] + velocity_x
            new_y = pellet.pos[1] + velocity_y
            pellet.pos = (new_x, new_y)

            # Apply gravity
            velocity_y -= 0.98

            # Bounding box
            pellet_left = pellet.pos[0]
            pellet_right = pellet.pos[0] + pellet.size[0]
            pellet_top = pellet.pos[1] + pellet.size[1]
            pellet_bottom = pellet.pos[1]

            # Check for bat's collisions
            for bat in self.bats:
                if bat.pos[0] != -1000:
                    bat_left = bat.pos[0]
                    bat_right = bat.pos[0] + bat.size[0]
                    bat_top = bat.pos[1] + bat.size[1]
                    bat_bottom = bat.pos[1]

                    if (pellet_right > bat_left and pellet_left < bat_right and
                            pellet_top > bat_bottom and pellet_bottom < bat_top):
                        bat.pos = (-1000, -1000)
                        pellet.pos = (-1000, -1000)
                        return False

            # Bounding box of Rock 2
            rock2_left = self.rock2.pos[0]
            rock2_right = self.rock2.pos[0] + self.rock2.size[0]
            rock2_top = self.rock2.pos[1] + self.rock2.size[1]
            rock2_bottom = self.rock2.pos[1]

            # Bounding box of Perpetuo2
            perpetuo2_left = self.perpetuo2.pos[0]
            perpetuo2_right = self.perpetuo2.pos[0] + self.perpetuo2.size[0]
            perpetuo2_top = self.perpetuo2.pos[1] + self.perpetuo2.size[1]
            perpetuo2_bottom = self.perpetuo2.pos[1]

            # Bounding box of perpetuo_above
            perpetuo_above_left = self.perpetuo_above.pos[0]
            perpetuo_above_right = self.perpetuo_above.pos[0] + self.perpetuo_above.size[0]
            perpetuo_above_top = self.perpetuo_above.pos[1] + self.perpetuo_above.size[1]
            perpetuo_above_bottom = self.perpetuo_above.pos[1]

            # Bounding box of rock2_top_left
            rock2_top_left = self.rock2_top.pos[0]
            rock2_top_right = self.rock2_top.pos[0] + self.rock2_top.size[0]
            rock2_top_top = self.rock2_top.pos[1] + self.rock2_top.size[1]
            rock2_top_bottom = self.rock2_top.pos[1]

            # Bounding box of the dragon
            dragon_left = self.dragon.pos[0]
            dragon_right = self.dragon.pos[0] + self.dragon.size[0]
            dragon_top = self.dragon.pos[1] + self.dragon.size[1]
            dragon_bottom = self.dragon.pos[1]

            # Bounding box of perpetuo_top_left
            perpetuo_top_left = self.perpetuo_top.pos[0]
            perpetuo_top_right = self.perpetuo_top.pos[0] + self.perpetuo_top.size[0]
            perpetuo_top_top = self.perpetuo_top.pos[1] + self.perpetuo_top.size[1]
            perpetuo_top_bottom = self.perpetuo_top.pos[1]

            # Check the collision with Rock2
            if (pellet_right > rock2_left and pellet_left < rock2_right and
                    pellet_top > rock2_bottom and pellet_bottom < rock2_top):
                self.show_shotgun_error()
                pellet.pos = (-1000, -1000)  # Hide the bullet
                return False

            # Check the collision with Perpetuo2
            if (pellet_right > perpetuo2_left and pellet_left < perpetuo2_right and
                    pellet_top > perpetuo2_bottom and pellet_bottom < perpetuo2_top):
                self.show_perpetuo_error()
                pellet.pos = (-1000, -1000)
                return False

            # Check the collision with Perpetuo_above_left
            if (pellet_right > perpetuo_above_left and pellet_left < perpetuo_above_right and
                    pellet_top > perpetuo_above_bottom and pellet_bottom < perpetuo_above_top):
                self.show_perpetuo_error()
                pellet.pos = (-1000, -1000)
                return False

            # Check the collision with the dragon using shotgun
            if (pellet_right > dragon_left and pellet_left < dragon_right and
                    pellet_top > dragon_bottom and pellet_bottom < dragon_top):
                self.hit_target()
                pellet.pos = (-1000, -1000)
                return False

            # Check the collision with rock2_top_left
            if (pellet_right > rock2_top_left and pellet_left < rock2_top_right and
                    pellet_top > rock2_top_bottom and pellet_bottom < rock2_top_top):
                self.show_shotgun_error()
                self.canvas.remove(pellet)
                return False

            # Check the collision with Perpetuo_top_right
            if (pellet_right > perpetuo_top_left and pellet_left < perpetuo_top_right and
                    pellet_top > perpetuo_top_bottom and pellet_bottom < perpetuo_top_top):
                self.show_perpetuo_error()
                pellet.pos = (-1000, -1000)
                return False

            # Check collision with the new rocks
            for rock in [self.rock2_left_1, self.rock2_left_2, self.rock2_left_3,
                        self.rock2_left_4, self.rock2_left_5, self.rock2_left_6]:
                if rock.pos[0] != -1000:     # Ignore rocks that have been "removed" by setting their x position to -1000.
                    rock_left = rock.pos[0]
                    rock_right = rock.pos[0] + rock.size[0]
                    rock_top = rock.pos[1] + rock.size[1]
                    rock_bottom = rock.pos[1]

                    if (pellet_right > rock_left and pellet_left < rock_right and
                            pellet_top > rock_bottom and pellet_bottom < rock_top):
                        self.show_shotgun_error()
                        pellet.pos = (-1000, -1000)
                        return False

            # Check if pellet goes ot of the window
            if new_x > Window.width or new_y < 0 or new_x < 0:
                pellet.pos = (-1000, -1000)
                return False

            return True

        except Exception as e:
            return False

    def drop(self, dt):
        """
        Update the cannonball's position and handle collisions.
        """
        new_x = self.cannonball.pos[0] + self.velocity_x
        new_y = self.cannonball.pos[1] + self.velocity_y
        self.cannonball.pos = (new_x, new_y)

        # Apply gravity
        self.velocity_y -= 0.98

        """
        Check for collisions with obstacles, targets, and bats.
        """
        ball_left = self.cannonball.pos[0]
        ball_right = self.cannonball.pos[0] + self.cannonball.size[0]
        ball_top = self.cannonball.pos[1] + self.cannonball.size[1]
        ball_bottom = self.cannonball.pos[1]


        rock2_left = self.rock2.pos[0]
        rock2_right = self.rock2.pos[0] + self.rock2.size[0]
        rock2_top = self.rock2.pos[1] + self.rock2.size[1]
        rock2_bottom = self.rock2.pos[1]


        rock2_above_left = self.rock2_above_perpetuo.pos[0]
        rock2_above_right = self.rock2_above_perpetuo.pos[0] + self.rock2_above_perpetuo.size[0]
        rock2_above_top = self.rock2_above_perpetuo.pos[1] + self.rock2_above_perpetuo.size[1]
        rock2_above_bottom = self.rock2_above_perpetuo.pos[1]


        perpetuo2_left = self.perpetuo2.pos[0]
        perpetuo2_right = self.perpetuo2.pos[0] + self.perpetuo2.size[0]
        perpetuo2_top = self.perpetuo2.pos[1] + self.perpetuo2.size[1]
        perpetuo2_bottom = self.perpetuo2.pos[1]


        perpetuo_above_left = self.perpetuo_above.pos[0]
        perpetuo_above_right = self.perpetuo_above.pos[0] + self.perpetuo_above.size[0]
        perpetuo_above_top = self.perpetuo_above.pos[1] + self.perpetuo_above.size[1]
        perpetuo_above_bottom = self.perpetuo_above.pos[1]

        dragon_left = self.dragon.pos[0]
        dragon_right = self.dragon.pos[0] + self.dragon.size[0]
        dragon_top = self.dragon.pos[1] + self.dragon.size[1]
        dragon_bottom = self.dragon.pos[1]


        rock2_top_left = self.rock2_top.pos[0]
        rock2_top_right = self.rock2_top.pos[0] + self.rock2_top.size[0]
        rock2_top_top = self.rock2_top.pos[1] + self.rock2_top.size[1]
        rock2_top_bottom = self.rock2_top.pos[1]

        perpetuo_top_left = self.perpetuo_top.pos[0]
        perpetuo_top_right = self.perpetuo_top.pos[0] + self.perpetuo_top.size[0]
        perpetuo_top_top = self.perpetuo_top.pos[1] + self.perpetuo_top.size[1]
        perpetuo_top_bottom = self.perpetuo_top.pos[1]


        if (ball_right > dragon_left and ball_left < dragon_right and
                ball_top > dragon_bottom and ball_bottom < dragon_top):
            self.hit_target()
            self.cannonball.pos = (-100, -100)
            Clock.unschedule(self.velocity_clock)


        if (ball_right > rock2_left and ball_left < rock2_right and
                ball_top > rock2_bottom and ball_bottom < rock2_top):
            if self.current_weapon == "cannon":
                self.rock2.pos = (-1000, -1000)
            else:
                self.show_shotgun_error()

            self.cannonball.pos = (-100, -100)
            Clock.unschedule(self.velocity_clock)


        if (ball_right > rock2_above_left and ball_left < rock2_above_right and
                ball_top > rock2_above_bottom and ball_bottom < rock2_above_top):
            if self.current_weapon == "cannon":
                self.rock2_above_perpetuo.pos = (-1000, -1000)  # Nascondi la nuova Rock2
            else:
                self.show_shotgun_error()

            self.cannonball.pos = (-100, -100)
            Clock.unschedule(self.velocity_clock)


        if (ball_right > perpetuo2_left and ball_left < perpetuo2_right and
                ball_top > perpetuo2_bottom and ball_bottom < perpetuo2_top):
            self.show_perpetuo_error()


            self.cannonball.pos = (-100, -100)
            Clock.unschedule(self.velocity_clock)

        if (ball_right > perpetuo_above_left and ball_left < perpetuo_above_right and
                ball_top > perpetuo_above_bottom and ball_bottom < perpetuo_above_top):
            self.show_perpetuo_error()
            self.cannonball.pos = (-100, -100)
            Clock.unschedule(self.velocity_clock)

        if (ball_right > rock2_top_left and ball_left < rock2_top_right and
                ball_top > rock2_top_bottom and ball_bottom < rock2_top_top):
            if self.current_weapon == "cannon":
                self.rock2_top.pos = (-1000, -1000)
            else:
                self.show_shotgun_error()

        if (ball_right > perpetuo_top_left and ball_left < perpetuo_top_right and
                ball_top > perpetuo_top_bottom and ball_bottom < perpetuo_top_top):
            self.show_perpetuo_error()
            self.cannonball.pos = (-100, -100)
            Clock.unschedule(self.velocity_clock)

        for bat in self.bats:
            if bat.pos[0] != -1000:
                bat_left = bat.pos[0]
                bat_right = bat.pos[0] + bat.size[0]
                bat_top = bat.pos[1] + bat.size[1]
                bat_bottom = bat.pos[1]

                if (ball_right > bat_left and ball_left < bat_right and
                        ball_top > bat_bottom and ball_bottom < bat_top):
                    if self.current_weapon == "cannon":
                        self.show_cannon_error()
                    else:
                        bat.pos = (-1000, -1000)

                    self.cannonball.pos = (-100, -100)
                    Clock.unschedule(self.velocity_clock)


        if new_x > Window.width or new_y < 0 or new_x < 0:
            self.cannonball.pos = (-100, -100)
            Clock.unschedule(self.velocity_clock)


        for i, rock in enumerate([self.rock2_left_1, self.rock2_left_2, self.rock2_left_3,
                                self.rock2_left_4, self.rock2_left_5, self.rock2_left_6]):
            if rock.pos[0] != -1000:
                rock_left = rock.pos[0]
                rock_right = rock.pos[0] + rock.size[0]
                rock_top = rock.pos[1] + rock.size[1]
                rock_bottom = rock.pos[1]

                if (ball_right > rock_left and ball_left < rock_right and
                        ball_top > rock_bottom and ball_bottom < rock_top):
                    if self.current_weapon == "cannon":
                        rock.pos = (-1000, -1000)
                    else:
                        self.show_shotgun_error()

                    # Reset the cannonball's position and stop the movement clock.
                    self.cannonball.pos = (-100, -100)
                    Clock.unschedule(self.velocity_clock)

    def set_velocity(self, velocity):
        """
        Set the velocity of the cannonball.
        """
        try:
            v = int(velocity)
            if v > 0:  # Velocity must be greater than 0
                self.velocity = v
        except ValueError:
            pass  # Ignore invalid inputs


    def set_angle(self, angle):
        """
        Set the angle of the cannon.
        """
        try:
            a = int(angle)
            if -1 < a <= 90:  # Angle must be between 0 and 90 degrees
                self.angle = a
                self.rotate.angle = self.angle
        except ValueError:
            pass  # Ignore invalid inputs



    # =======================================================================
    # Dragon Movement
    # =======================================================================

    def move_dragon(self, dt):
        """
        Move the dragon up and down.
        """
        new_y = self.dragon.pos[1] + self.dragon_direction * 5
        if new_y > self.height - self.dragon.size[1] + 200:
            self.dragon_direction = -1
        elif new_y < 50:
            self.dragon_direction = 1

        self.dragon.pos = (self.dragon.pos[0], new_y)



    # =======================================================================
    # Popup Handling Methods
    # =======================================================================

    def show_finished_popup(self):
        content = BoxLayout(orientation='vertical', padding=(20, 20), spacing=10)
        content.add_widget(Label(text="YOU FINISHED YOUR AVAILABLE SHOTS", size_hint_y=None, height=40))

        # Create the "Try Again" button
        try_again_button = Button(text="Try Again", size_hint_y=None, height=50)
        try_again_button.bind(on_press=self.reset_level)  # Bind the button to reset the level
        content.add_widget(try_again_button)

        # Create the popup
        self.popup = Popup(title="Game Over", content=content, size_hint=(None, None), size=(400, 200),
                           auto_dismiss=False)
        self.popup.open()  # Open the popup

    def show_game_over_popup(self):
        if not self.popup_visible:  # Show the popup only if there is not a popup already
            self.popup_visible = True
            content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                      height=30)

            # Empty label for occupy the left space
            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(text="Try Again",
                            font_size=18,
                            size_hint=(None, None),
                            size=(200, 50),
                            background_color=[0.5, 0, 0, 1],
                            color=[1, 1, 1, 1])

            button_layout.add_widget(button)

            # Empty label for occupy the right space
            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)

            content.add_widget(button_layout)

            self.P = Popup(title="Game Over! You ran out of shots!",
                           title_align='center',
                           title_size=30,
                           title_color=[0.5, 0, 0, 1],
                           content=content,
                           size_hint=(None, None),
                           size=(500, 300),
                           background='images/popup.png',
                           auto_dismiss=False)

            # Link the button to the closure of the popup and at the reset of the level
            button.bind(on_press=self.dismiss_popup)
            self.P.open()

    def stop_dragon_movement(self):
        self.dragon_direction = 0

    def start_dragon_movement(self):
        self.dragon_direction = 1



    def dismiss_popup(self, instance):
        self.P.dismiss()
        self.popup_visible = False
        self.reset_level()


    def show_perpetuo_error(self):
        if not self.popup_visible:
            self.popup_visible = True

            content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                      height=30)

            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(text="Try Again",
                            font_size=18,
                            size_hint=(None, None),
                            size=(200, 50),
                            background_color=[0.5, 0, 0, 1],
                            color=[1, 1, 1, 1])

            button_layout.add_widget(button)


            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)  #

            content.add_widget(button_layout)

            self.P = Popup(title="You can't destroy Perpetuo!",
                           title_align='center',
                           title_size=30,
                           title_color=[0.5, 0, 0, 1],
                           content=content,
                           size_hint=(None, None),
                           size=(500, 300),
                           background='images/popup.png',
                           auto_dismiss=False)

            button.bind(on_press=self.dismiss_popup)
            self.P.open()

    def show_shotgun_error(self):
        if not self.popup_visible:
            self.popup_visible = True

            content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                      height=30)

            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(text="Try Again",
                            font_size=18,
                            size_hint=(None, None),
                            size=(200, 50),
                            background_color=[0.5, 0, 0, 1],
                            color=[1, 1, 1, 1])

            button_layout.add_widget(button)

            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)

            content.add_widget(button_layout)

            self.P = Popup(title="Shotgun can't destroy it!",
                           title_align='center',
                           title_size=30,
                           title_color=[0.5, 0, 0, 1],
                           content=content,
                           size_hint=(None, None),
                           size=(500, 300),
                           background='images/popup.png',
                           auto_dismiss=False)

            button.bind(on_press=self.dismiss_popup)
            self.P.open()

    def dismiss_popup(self, instance):
        self.P.dismiss()
        self.popup_visible = False

    def show_cannon_error(self):

        if not self.popup_visible:
            self.popup_visible = True


            content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                      height=30)

            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(text="Try Again",
                            font_size=18,
                            size_hint=(None, None),
                            size=(200, 50),
                            background_color=[0.5, 0, 0, 1],
                            color=[1, 1, 1, 1])

            button_layout.add_widget(button)


            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)

            content.add_widget(button_layout)

            self.P = Popup(title="Cannon can't destroy bats! Use the shotgun!",
                           title_align='center',
                           title_size=30,
                           title_color=[0.5, 0, 0, 1],
                           content=content,
                           size_hint=(None, None),
                           size=(500, 300),
                           background='images/popup.png',
                           auto_dismiss=False)

            button.bind(on_press=self.P.dismiss)
            button.bind(on_press=self.reset_popup_visible)
            self.P.open()

    def reset_popup_visible(self, instance):
        self.popup_visible = False



    # =======================================================================
    # Level Reset Methods
    # =======================================================================
    def reset_level(self):
        # Reset number of shots
        self.shots_left = 10
        self.update_shots_label()

        # Reset the position of the objects
        self.dragon.pos = (self.width - 120, self.height / 2 - 100)
        self.rock2.pos = (650, 50)
        self.perpetuo2.pos = (650, 150)
        self.rock2_above_perpetuo.pos = (650, 250)
        self.perpetuo_above.pos = (650, 350)
        self.rock2_top.pos = (650, 450)
        self.perpetuo_top.pos = (650, 550)


        self.rock2_left_1.pos = (500, 50)
        self.rock2_left_2.pos = (500, 150)
        self.rock2_left_3.pos = (500, 250)
        self.rock2_left_4.pos = (500, 350)
        self.rock2_left_5.pos = (500, 450)
        self.rock2_left_6.pos = (500, 550)


        self.update_rectangles()  # Recall the method update_rectangles

        # Restart the dragon's movement
        self.start_dragon_movement()

        self.start_time = time.time()



    # =======================================================================
    # Target Hit Handling
    # =======================================================================
    def hit_target(self):
        global current_level
        elapsed_time = time.time() - self.start_time

        # Add the record alla Hall of Fame
        app = App.get_running_app()
        hall_of_fame = app.root.get_screen('halloffame')
        hall_of_fame.add_record(f'level{current_level}', elapsed_time)

        content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                  height=30)


        label_space_left = Label(size_hint_x=1)
        button_layout.add_widget(label_space_left)


        button = Button(text=f'Next Level\nTime: {elapsed_time:.2f} sec',
                        font_size=18,
                        size_hint=(None, None),
                        size=(200, 50),
                        background_color=[0, 0.5, 0, 1],
                        color=[1, 1, 1, 1])

        button_layout.add_widget(button)


        label_space_right = Label(size_hint_x=1)
        button_layout.add_widget(label_space_right)

        content.add_widget(button_layout)


        self.P = Popup(title="Great Shot! Next Level Unlocked!",
                       title_align='center',
                       title_size=40,
                       title_color=[0, 0.3, 0, 1],
                       content=content,
                       size_hint=(None, None),
                       size=(500, 350),
                       background='images/popup.png',
                       auto_dismiss=False)


        button.bind(on_press=self.P.dismiss)
        button.bind(on_press=self.next_level)
        self.P.open()

    def next_level(self, instance):
        app = App.get_running_app()
        screen_manager = app.root
        if hasattr(screen_manager, 'current'):
            screen_manager.current = 'level3game'
            if hasattr(self, 'P') and self.P:
                self.P.dismiss()











#=======================================================================
# CannonLevel3 class
#=======================================================================
class CannonLevel3(Widget):
    angle_int_deg = NumericProperty(50)
    LASER_IMPULSE = LASER_IMPULSE
    LASER_DIST = LASER_DIST
    LASER_VEL = LASER_VEL
    shots_left = NumericProperty(10)

    def __init__(self, **kwargs):
        super(CannonLevel3, self).__init__(**kwargs)
        self.update_shots_label()
        self.velocity = 0
        self.velocity_clock = None
        self.velocity_x = 0
        self.velocity_y = 0
        self.angle = 0
        self.current_weapon = "cannon"
        self.popup_visible = False
        random.seed()
        self.laser_beam = None
        self.start_time = time.time()
        self.bind(pos=self.update_rectangles, size=self.update_rectangles)



        # =======================================================================
        # Static Element Creation
        # =======================================================================

        with self.canvas.before:
            # Draw the target (witch-target3)
            self.witch = Rectangle(
                size=(200, 220),
                pos=(1000, 50),
                source="images/witch-target3.png"
            )

            # Add the column of obstacles
            # 3 perpetuo3 at the bottom
            self.perpetuo1 = Rectangle(size=(120, 120), pos=(600, 50),
                                       source="images/perpetuo3.png")
            self.perpetuo2 = Rectangle(size=(120, 120), pos=(600, 150),
                                       source="images/perpetuo3.png")
            self.perpetuo3 = Rectangle(size=(120, 120), pos=(600, 250),
                                       source="images/perpetuo3.png")

            # 2 rock3 at the top
            self.rock1 = Rectangle(size=(120, 120), pos=(600, 350),
                                   source="images/rock3.png")
            self.rock2 = Rectangle(size=(120, 120), pos=(600, 450),
                                   source="images/rock3.png")

            # Add bats 
            self.bats = []
            bat_x = 480
            bat_y_positions = [100, 220, 330, 550]

            for i, y_pos in enumerate(bat_y_positions):
                bat = Rectangle(
                    size=(120, 120),
                    pos=(bat_x, y_pos),
                    source="images/bat-obstacle2.png"
                )
                self.bats.append(bat)

            # Add the middle rock3
            self.rock_middle = Rectangle(
                size=(120, 120),
                pos=(bat_x, 440),
                source="images/rock3.png"
            )

            # Add the new perpetuo3 to the left of the middle rock
            self.perpetuo_middle = Rectangle(
                size=(120, 120),
                pos=(bat_x - 130, 450),
                source="images/perpetuo3.png"
            )

            # Add the new rock3 below the perpetuo_middle
            self.rock_under_perpetuo = Rectangle(
                size=(120, 120),
                pos=(350, 350),
                source="images/rock3.png"
            )

            # Add mirror_horizontal3 at the bottom right
            self.mirror = Rectangle(
                size=(150, 15),
                pos=(800, 600),
                source="images/mirror_horizontal3.png")

        # Wheel
        with self.canvas:
            self.wheel = Rectangle(size=(150, 150), pos=(5, 5), source="images/cannon_wheel2.png")

        # Rotating elements (cannon)
        with self.canvas:
            PushMatrix()
            self.rotate = Rotate(origin=(142.5, 12.5), angle=self.angle)
            self.cannon = Rectangle(size=(200, 75), pos=(100, 30), source="images/cannon.png")
            PopMatrix()

        # Cannonball
        with self.canvas:
            self.cannonball = Rectangle(pos=(-100, -100), size=(35, 35), source="images/bullet.png")


    # =======================================================================
    # UI Update Methods
    # =======================================================================
    def update_rectangles(self, *args):
        # Wheel position (fixed at the bottom left)
        wheel_x = self.x + 20
        wheel_y = self.y + 20
        self.wheel.pos = (wheel_x, wheel_y)

        # Cannon position (centered above the wheel, but lower)
        cannon_x = wheel_x + self.wheel.size[0] / 2 - self.cannon.size[
            0] / 2 + 65
        cannon_y = wheel_y + self.wheel.size[1] - 100
        self.cannon.pos = (cannon_x, cannon_y)

        # Bullet position (initially invisible)
        self.cannonball.pos = (-100, -100)  # Hide the cannonball initially

        # Update the rotation origin of the cannon
        self.rotate.origin = (cannon_x + self.cannon.size[0] * 0.5, cannon_y)

        # Update witch position
        witch_x = self.width - 300
        witch_y = 20
        self.witch.pos = (witch_x, witch_y)

        # Update obstacle positions
        obstacles_x = 600
        self.perpetuo1.pos = (obstacles_x, 50)
        self.perpetuo2.pos = (obstacles_x, 150)
        self.perpetuo3.pos = (obstacles_x, 250)
        self.rock1.pos = (obstacles_x, 350)
        self.rock2.pos = (obstacles_x, 450)

        # Update object's positions
        bat_x = 480
        bat_y_positions = [110, 220, 330, 550]
        for i, bat in enumerate(self.bats):
            bat.pos = (bat_x, bat_y_positions[i])

        self.rock_middle.pos = (480, 450)
        self.perpetuo_middle.pos = (bat_x - 130, 450)
        self.rock_under_perpetuo.pos = (350, 350)

        witch_x = 800
        witch_y = 50
        self.witch.pos = (witch_x, witch_y)

        mirror_x = 800
        mirror_y = 600
        self.mirror.pos = (mirror_x, mirror_y)


    def update_shots_label(self):
        app = App.get_running_app()
        if app.root:
            level_screen = app.root.get_screen('level3game')
            level_screen.ids.shots_label.text = f"Number of shots: {self.shots_left}/10"



        # =======================================================================
        # Game Logic Methods
        # =======================================================================
        """
        Switch the current weapon type.
        """
    def switch_weapon(self, weapon_type):
        self.current_weapon = weapon_type
        if weapon_type == "shotgun":
            self.cannon.source = "images/cannon.png"
            self.cannonball.source = "images/bullet2.png"
            self.cannonball.size = (BULLET_RADIUS * 2, BULLET_RADIUS * 2)
            self.mass = BULLET_MASS
        else:
            self.cannon.source = "images/cannon.png"
            self.cannonball.source = "images/bullet.png"
            self.cannonball.size = (BOMB_RADIUS * 2, BOMB_RADIUS * 2)
            self.mass = BOMB_MASS

    def fire_cannon(self):
        if self.current_weapon == "cannon":
            self.fire_single_shot()
        elif self.current_weapon == "shotgun":
            self.fire_shotgun()
        elif self.current_weapon == "laser":
            self.fire_laser()

        self.shots_left -= 1
        self.update_shots_label()

        if self.shots_left <= 0:
            self.reset_level()


    def fire_single_shot(self):
        self.cannonball.pos = (
            int(self.cannon.pos[0] + cos(radians(self.angle)) * self.cannon.size[0] / 2),
            int(self.cannon.pos[1] + sin(radians(self.angle)) * self.cannon.size[1] / 2)
        )
        self.velocity_clock = Clock.schedule_interval(self.drop, 0.1)
        self.velocity_y = self.velocity * sin(radians(self.angle))
        self.velocity_x = self.velocity * cos(radians(self.angle))


    def fire_shotgun(self):
        for offset in [-10, 0, 10]:
            self.create_pellet(self.angle + offset)



    def fire_laser(self):
        if self.laser_beam:
            self.canvas.before.remove(self.laser_beam)

        start_x = self.cannon.pos[0] + self.cannon.size[0] / 2
        start_y = self.cannon.pos[1] + self.cannon.size[1] / 2 + 5
        end_x = start_x + cos(radians(self.angle)) * self.LASER_DIST
        end_y = start_y + sin(radians(self.angle)) * self.LASER_DIST


        mirror_collision = self.check_laser_collision(start_x, start_y, end_x, end_y, self.mirror)

        if mirror_collision:
            reflection_x, reflection_y = mirror_collision


            first_collision = self.check_path_collisions(start_x, start_y, reflection_x, reflection_y)
            if first_collision:
                collision_point, collision_type = first_collision
                with self.canvas.before:
                    Color(1, 0, 0, 1)
                    self.laser_beam = Line(points=[start_x, start_y, collision_point[0], collision_point[1]], width=2)
                    Color(1, 1, 1, 1)

                if collision_type == "perpetuo":
                    self.show_perpetuo_error()
                elif collision_type == "rock":
                    self.show_shotgun_error()
                elif collision_type == "bat":
                    self.show_cannon_error()
                return

            # Check the reflex path of the laser
            reflected_collision = self.check_path_collisions(reflection_x, reflection_y, reflection_x, 0)
            if reflected_collision:
                collision_point, collision_type = reflected_collision
                # Draw the laser
                with self.canvas.before:
                    Color(1, 0, 0, 1)
                    self.laser_beam = Line(points=[start_x, start_y, reflection_x, reflection_y], width=2)
                    self.reflected_beam = Line(
                        points=[reflection_x, reflection_y, collision_point[0], collision_point[1]], width=2)
                    Color(1, 1, 1, 1)

                if collision_type == "witch":
                    self.hit_target()
                elif collision_type == "perpetuo":
                    self.show_perpetuo_error()
                elif collision_type == "rock":
                    self.show_shotgun_error()
                elif collision_type == "bat":
                    self.show_cannon_error()
            else:
                with self.canvas.before:
                    Color(1, 0, 0, 1)
                    self.laser_beam = Line(points=[start_x, start_y, reflection_x, reflection_y], width=2)
                    self.reflected_beam = Line(points=[reflection_x, reflection_y, reflection_x, 0], width=2)
                    Color(1, 1, 1, 1)

        else:
            collision = self.check_path_collisions(start_x, start_y, end_x, end_y)
            if collision:
                collision_point, collision_type = collision
                with self.canvas.before:
                    Color(1, 0, 0, 1)
                    self.laser_beam = Line(points=[start_x, start_y, collision_point[0], collision_point[1]], width=2)
                    Color(1, 1, 1, 1)

                if collision_type == "perpetuo":
                    self.show_perpetuo_error()
                elif collision_type == "rock":
                    self.show_shotgun_error()
                elif collision_type == "bat":
                    self.show_cannon_error()
            else:
                with self.canvas.before:
                    Color(1, 0, 0, 1)
                    self.laser_beam = Line(points=[start_x, start_y, end_x, end_y], width=2)
                    Color(1, 1, 1, 1)

        Clock.schedule_once(self.end_laser, 2.0)



    def drop(self, dt):
        try:
            new_x = self.cannonball.pos[0] + self.velocity_x
            new_y = self.cannonball.pos[1] + self.velocity_y
            self.cannonball.pos = (new_x, new_y)

            self.velocity_y -= 0.98

            ball_left = self.cannonball.pos[0]
            ball_right = self.cannonball.pos[0] + self.cannonball.size[0]
            ball_top = self.cannonball.pos[1] + self.cannonball.size[1]
            ball_bottom = self.cannonball.pos[1]

            perpetuos = [self.perpetuo1, self.perpetuo2, self.perpetuo3, self.perpetuo_middle]
            for perpetuo in perpetuos:
                perpetuo_left = perpetuo.pos[0]
                perpetuo_right = perpetuo.pos[0] + perpetuo.size[0]
                perpetuo_top = perpetuo.pos[1] + perpetuo.size[1]
                perpetuo_bottom = perpetuo.pos[1]

                if (ball_right > perpetuo_left and ball_left < perpetuo_right and
                        ball_top > perpetuo_bottom and ball_bottom < perpetuo_top):
                    self.show_perpetuo_error()
                    self.cannonball.pos = (-100, -100)
                    Clock.unschedule(self.velocity_clock)
                    return False


            witch_left = self.witch.pos[0]
            witch_right = self.witch.pos[0] + self.witch.size[0]
            witch_top = self.witch.pos[1] + self.witch.size[1]
            witch_bottom = self.witch.pos[1]


            if (ball_right > witch_left and ball_left < witch_right and
                    ball_top > witch_bottom and ball_bottom < witch_top):
                self.show_weapon_error()
                self.cannonball.pos = (-100, -100)
                Clock.unschedule(self.velocity_clock)
                return False


            for bat in self.bats:
                if bat.pos[0] != -1000:
                    bat_left = bat.pos[0]
                    bat_right = bat.pos[0] + bat.size[0]
                    bat_top = bat.pos[1] + bat.size[1]
                    bat_bottom = bat.pos[1]

                    if (ball_right > bat_left and ball_left < bat_right and
                            ball_top > bat_bottom and ball_bottom < bat_top):
                        self.show_cannon_error()
                        self.cannonball.pos = (-100, -100)
                        Clock.unschedule(self.velocity_clock)
                        return False


            rocks = [self.rock1, self.rock2, self.rock_middle, self.rock_under_perpetuo]
            for rock in rocks:
                if rock.pos[0] != -1000:
                    rock_left = rock.pos[0]
                    rock_right = rock.pos[0] + rock.size[0]
                    rock_top = rock.pos[1] + rock.size[1]
                    rock_bottom = rock.pos[1]

                    if (ball_right > rock_left and ball_left < rock_right and
                            ball_top > rock_bottom and ball_bottom < rock_top):
                        if self.current_weapon == "cannon":
                            rock.pos = (-1000, -1000)
                        else:
                            self.show_shotgun_error()
                        self.cannonball.pos = (-100, -100)
                        Clock.unschedule(self.velocity_clock)
                        return False


            if new_x > Window.width or new_y < 0 or new_x < 0:
                self.cannonball.pos = (-100, -100)
                Clock.unschedule(self.velocity_clock)
                return False

            return True

        except Exception as e:
            return False

    def set_velocity(self, velocity):
        """
        Set the velocity of the cannonball.
        """
        try:
            v = int(velocity)
            if v > 0:  # Velocity must be greater than 0
                self.velocity = v
        except ValueError:
            pass  # Ignore invalid inputs

    def set_angle(self, angle):
        """
        Set the angle of the cannon.
        """
        try:
            a = int(angle)
            if -1 < a <= 90:  # Angle must be between 0 and 90 degrees
                self.angle = a
                self.rotate.angle = self.angle
        except ValueError:
            pass  # Ignore invalid inputs


    def create_pellet(self, angle):
        pellet_x = self.cannon.pos[0] + cos(radians(angle)) * self.cannon.size[0] / 2
        pellet_y = self.cannon.pos[1] + sin(radians(angle)) * self.cannon.size[1] / 2

        with self.canvas:
            pellet = Rectangle(
                source="images/bullet2.png",
                size=(25, 25),
                pos=(pellet_x, pellet_y)
            )


        pellet_velocity_x = self.velocity * cos(radians(angle))
        pellet_velocity_y = self.velocity * sin(radians(angle))


        Clock.schedule_interval(
            lambda dt: self.move_pellet(pellet, pellet_velocity_x, pellet_velocity_y),
            0.1
        )

    def move_pellet(self, pellet, velocity_x, velocity_y):
        try:
            new_x = pellet.pos[0] + velocity_x
            new_y = pellet.pos[1] + velocity_y - 0.98
            pellet.pos = (new_x, new_y)


            pellet_left = pellet.pos[0]
            pellet_right = pellet.pos[0] + pellet.size[0]
            pellet_top = pellet.pos[1] + pellet.size[1]
            pellet_bottom = pellet.pos[1]


            perpetuos = [self.perpetuo1, self.perpetuo2, self.perpetuo3, self.perpetuo_middle]
            for perpetuo in perpetuos:
                perpetuo_left = perpetuo.pos[0]
                perpetuo_right = perpetuo.pos[0] + perpetuo.size[0]
                perpetuo_top = perpetuo.pos[1] + perpetuo.size[1]
                perpetuo_bottom = perpetuo.pos[1]

                if (pellet_right > perpetuo_left and pellet_left < perpetuo_right and
                        pellet_top > perpetuo_bottom and pellet_bottom < perpetuo_top):
                    self.show_perpetuo_error()
                    self.canvas.remove(pellet)
                    return False


            rocks = [self.rock1, self.rock2, self.rock_middle, self.rock_under_perpetuo]
            for rock in rocks:
                if rock.pos[0] != -1000:
                    rock_left = rock.pos[0]
                    rock_right = rock.pos[0] + rock.size[0]
                    rock_top = rock.pos[1] + rock.size[1]
                    rock_bottom = rock.pos[1]

                    if (pellet_right > rock_left and pellet_left < rock_right and
                            pellet_top > rock_bottom and pellet_bottom < rock_top):
                        self.show_shotgun_error()
                        self.canvas.remove(pellet)
                        return False


            for bat in self.bats:
                if bat.pos[0] != -1000:
                    bat_left = bat.pos[0]
                    bat_right = bat.pos[0] + bat.size[0]
                    bat_top = bat.pos[1] + bat.size[1]
                    bat_bottom = bat.pos[1]

                    if (pellet_right > bat_left and pellet_left < bat_right and
                            pellet_top > bat_bottom and pellet_bottom < bat_top):
                        bat.pos = (-1000, -1000)
                        self.canvas.remove(pellet)
                        return False


            witch_left = self.witch.pos[0]
            witch_right = self.witch.pos[0] + self.witch.size[0]
            witch_top = self.witch.pos[1] + self.witch.size[1]
            witch_bottom = self.witch.pos[1]

            if (pellet_right > witch_left and pellet_left < witch_right and
                    pellet_top > witch_bottom and pellet_bottom < witch_top):
                self.show_weapon_error()
                self.canvas.remove(pellet)
                return False

            # Controlla se il proiettile esce dallo schermo
            if new_x > Window.width or new_y < 0 or new_x < 0:
                self.canvas.remove(pellet)
                return False

            return True

        except Exception as e:
            return False


    def check_path_collisions(self, start_x, start_y, end_x, end_y):
        """
        Checks for collisions along the laser's path with multiple types of objects
        """
        perpetuos = [self.perpetuo1, self.perpetuo2, self.perpetuo3, self.perpetuo_middle]
        rocks = [self.rock1, self.rock2, self.rock_middle, self.rock_under_perpetuo]

        closest_collision = None
        closest_distance = float('inf')
        collision_type = None


        for perpetuo in perpetuos:
            collision = self.check_laser_collision(start_x, start_y, end_x, end_y, perpetuo)
            if collision:
                distance = self.get_distance(start_x, start_y, collision[0], collision[1])
                if distance < closest_distance:
                    closest_collision = collision
                    closest_distance = distance
                    collision_type = "perpetuo"


        for rock in rocks:
            if rock.pos[0] != -1000:
                collision = self.check_laser_collision(start_x, start_y, end_x, end_y, rock)
                if collision:
                    distance = self.get_distance(start_x, start_y, collision[0], collision[1])
                    if distance < closest_distance:
                        closest_collision = collision
                        closest_distance = distance
                        collision_type = "rock"


        for bat in self.bats:
            if bat.pos[0] != -1000:
                collision = self.check_laser_collision(start_x, start_y, end_x, end_y, bat)
                if collision:
                    distance = self.get_distance(start_x, start_y, collision[0], collision[1])
                    if distance < closest_distance:
                        closest_collision = collision
                        closest_distance = distance
                        collision_type = "bat"


        witch_collision = self.check_laser_collision(start_x, start_y, end_x, end_y, self.witch)
        if witch_collision:
            distance = self.get_distance(start_x, start_y, witch_collision[0], witch_collision[1])
            if distance < closest_distance:
                closest_collision = witch_collision
                closest_distance = distance
                collision_type = "witch"

        if closest_collision:
            return (closest_collision, collision_type)
        return None

    def check_laser_collision(self, start_x, start_y, end_x, end_y, obj):
        """
        Calculate the exact collision point between the laser and the object
        """
        obj_left = obj.pos[0]
        obj_right = obj.pos[0] + obj.size[0]
        obj_bottom = obj.pos[1]
        obj_top = obj.pos[1] + obj.size[1]

        # Increase number of checking points for a better precision
        num_points = 200
        for t in range(num_points):
            t_normalized = t / float(num_points - 1)
            point_x = start_x + (end_x - start_x) * t_normalized
            point_y = start_y + (end_y - start_y) * t_normalized

            if (obj_left - 1 <= point_x <= obj_right + 1 and
                    obj_bottom - 1 <= point_y <= obj_top + 1):
                return (point_x, point_y)
        return None


    def get_distance(self, x1, y1, x2, y2):
        """Calculate Euclidean distance between two points """
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def end_laser(self, dt):
        """Rimuove il laser dopo il timeout"""
        if self.laser_beam:
            self.canvas.before.remove(self.laser_beam)
            self.laser_beam = None
        if hasattr(self, 'reflected_beam') and self.reflected_beam:
            self.canvas.before.remove(self.reflected_beam)
            self.reflected_beam = None



    # =======================================================================
    # Popup Handling Methods
    # =======================================================================

    def show_game_over_popup(self):
        if not self.popup_visible:
            self.popup_visible = True
            content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                      height=30)


            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(text="Try Again",
                            font_size=18,
                            size_hint=(None, None),
                            size=(200, 50),
                            background_color=[0.5, 0, 0, 1],
                            color=[1, 1, 1, 1])

            button_layout.add_widget(button)

            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)

            content.add_widget(button_layout)

            self.P = Popup(title="Game Over! You ran out of shots!",
                           title_align='center',
                           title_size=30,
                           title_color=[0.5, 0, 0, 1],
                           content=content,
                           size_hint=(None, None),
                           size=(500, 300),
                           background='images/popup.png',
                           auto_dismiss=False)

            button.bind(on_press=self.dismiss_popup)
            self.P.open()


    def dismiss_popup(self, instance):
        self.P.dismiss()
        self.popup_visible = False
        self.reset_level()


    def show_cannon_error(self):
        if not self.popup_visible:
            self.popup_visible = True
            content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                      height=30)

            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(text="Try Again",
                            font_size=18,
                            size_hint=(None, None),
                            size=(200, 50),
                            background_color=[0.5, 0, 0, 1],
                            color=[1, 1, 1, 1])

            button_layout.add_widget(button)

            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)

            content.add_widget(button_layout)

            self.P = Popup(title="Cannon can't destroy bats! Use the shotgun!",
                           title_align='center',
                           title_size=30,
                           title_color=[0.5, 0, 0, 1],
                           content=content,
                           size_hint=(None, None),
                           size=(500, 300),
                           background='images/popup.png',
                           auto_dismiss=False)

            button.bind(on_press=self.P.dismiss)
            button.bind(on_press=self.reset_popup_visible)
            self.P.open()


    def show_shotgun_error(self):
        if not self.popup_visible:
            self.popup_visible = True
            content = BoxLayout(orientation='vertical', padding=(20, 90), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                      height=30)

            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(text="Try Again",
                            font_size=18,
                            size_hint=(None, None),
                            size=(200, 50),
                            background_color=[0.5, 0, 0, 1],
                            color=[1, 1, 1, 1])

            button_layout.add_widget(button)

            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)

            content.add_widget(button_layout)

            self.P = Popup(title="Only Cannon can destroy rocks!",
                           title_align='center',
                           title_size=30,
                           title_color=[0.5, 0, 0, 1],
                           content=content,
                           size_hint=(None, None),
                           size=(500, 300),
                           background='images/popup.png',
                           auto_dismiss=False)

            button.bind(on_press=self.P.dismiss)
            button.bind(on_press=self.reset_popup_visible)
            self.P.open()


    def show_perpetuo_error(self):
        if not self.popup_visible:
            self.popup_visible = True
            content = BoxLayout(orientation='vertical', padding=(20, 90), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                      height=30)

            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(text="Try Again",
                            font_size=18,
                            size_hint=(None, None),
                            size=(200, 50),
                            background_color=[0.5, 0, 0, 1],
                            color=[1, 1, 1, 1])

            button_layout.add_widget(button)

            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)

            content.add_widget(button_layout)

            self.P = Popup(title="Perpetuo is indestructible!",
                           title_align='center',
                           title_size=30,
                           title_color=[0.5, 0, 0, 1],
                           content=content,
                           size_hint=(None, None),
                           size=(500, 300),
                           background='images/popup.png',
                           auto_dismiss=False)

            button.bind(on_press=self.P.dismiss)
            button.bind(on_press=self.reset_popup_visible)
            self.P.open()


    def show_weapon_error(self):
        if not self.popup_visible:
            self.popup_visible = True
            content = BoxLayout(orientation='vertical', padding=(20, 90), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                      height=30)

            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(text="Try Again",
                            font_size=18,
                            size_hint=(None, None),
                            size=(200, 50),
                            background_color=[0.5, 0, 0, 1],
                            color=[1, 1, 1, 1])

            button_layout.add_widget(button)

            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)

            content.add_widget(button_layout)

            self.P = Popup(title="Only Laser can hit the Witch!",
                           title_align='center',
                           title_size=30,
                           title_color=[0.5, 0, 0, 1],
                           content=content,
                           size_hint=(None, None),
                           size=(500, 300),
                           background='images/popup.png',
                           auto_dismiss=False)

            button.bind(on_press=self.P.dismiss)
            button.bind(on_press=self.reset_popup_visible)
            self.P.open()


    def reset_popup_visible(self, instance):
        self.popup_visible = False



        # =======================================================================
        # Level Reset Methods
        # =======================================================================
    def reset_level(self):
        self.shots_left = 10
        self.update_shots_label()

        for i, bat in enumerate(self.bats):
            bat.pos = (480, [100, 220, 330, 550][i])

        self.rock1.pos = (600, 350)
        self.rock2.pos = (600, 450)
        self.rock_middle.pos = (480, 440)
        self.rock_under_perpetuo.pos = (350, 350)
        self.perpetuo1.pos = (600, 50)
        self.perpetuo2.pos = (600, 150)
        self.perpetuo3.pos = (600, 250)

        self.cannonball.pos = (-100, -100)
        self.start_time = time.time()



        # =======================================================================
        # Target Hit Handling
        # =======================================================================

    def hit_target(self):
        global current_level  # Aggiungi questa riga
        elapsed_time = time.time() - self.start_time

        # Add the record to Hall of Fame
        app = App.get_running_app()
        hall_of_fame = app.root.get_screen('halloffame')
        hall_of_fame.add_record(f'level{current_level}', elapsed_time)

        content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                  height=30)

        label_space_left = Label(size_hint_x=1)
        button_layout.add_widget(label_space_left)

        button = Button(text=f'Next Level\nTime: {elapsed_time:.2f} sec',
                        font_size=18,
                        size_hint=(None, None),
                        size=(200, 50),
                        background_color=[0, 0.5, 0, 1],
                        color=[1, 1, 1, 1])

        button_layout.add_widget(button)

        label_space_right = Label(size_hint_x=1)
        button_layout.add_widget(label_space_right)

        content.add_widget(button_layout)

        self.P = Popup(title="Great Shot! Next Level Unlocked!",
                       title_align='center',
                       title_size=40,
                       title_color=[0, 0.3, 0, 1],
                       content=content,
                       size_hint=(None, None),
                       size=(500, 350),
                       background='images/popup.png',
                       auto_dismiss=False)

        button.bind(on_press=self.P.dismiss)
        button.bind(on_press=self.next_level)
        self.P.open()


    def next_level(self, instance):
        app = App.get_running_app()
        screen_manager = app.root
        if hasattr(screen_manager, 'current'):
            screen_manager.current = 'level4game'
            # Chiudi eventuali popup aperti
            if hasattr(self, 'P') and self.P:
                self.P.dismiss()









#=======================================================================
# CannonLevel4 class
#=======================================================================
class CannonLevel4(Widget):
    angle_int_deg = NumericProperty(50)
    LASER_IMPULSE = LASER_IMPULSE
    LASER_DIST = LASER_DIST
    LASER_VEL = LASER_VEL
    shots_left = NumericProperty(8)

    def __init__(self, **kwargs):
        super(CannonLevel4, self).__init__(**kwargs)
        self.angle = 0
        self.current_weapon = "laser_red"
        self.popup_visible = False
        self.laser_beam = None
        self.start_time = time.time()
        self.bind(pos=self.update_rectangles, size=self.update_rectangles)
        self.update_shots_label()



        # =======================================================================
        # Static Element Creation
        # =======================================================================
        # Create separate canvas groups for static and rotating elements

        with self.canvas.before:
            # Target spaceship
            self.spaceship_target = Rectangle(
                size=(150, 150),
                pos=(900, 600),
                source="images/spaceship-target4.png"
            )

            # Create asteroids
            self.asteroids = []
            asteroid_positions = [
                # First row
                (380, 500), (470, 500), (560, 500), (650, 500), (740, 500), (830, 500), (920, 500),
                # Second row
                (380, 400), (470, 400), (560, 400), (650, 400), (740, 400), (830, 400), (920, 400),
                # Third row
                (380, 300), (470, 300), (560, 300), (650, 300), (740, 300), (830, 300), (920, 300),
                # Fourth row
                (380, 200), (470, 200), (560, 200), (650, 200), (740, 200), (830, 200), (920, 200)
            ]
            
            for i, pos in enumerate(asteroid_positions):
                # Toggle between asteroid1 and asteroid2
                source = "images/asteroid1.png" if i % 2 == 0 else "images/asteroid2.png"
                asteroid = Rectangle(
                    size=(120, 120),
                    pos=pos,
                    source=source
                )
                self.asteroids.append(asteroid)

        # Spaceship (substitute cannon and wheel)
        with self.canvas:
            self.spaceship = Rectangle(
                size=(150, 150),
                pos=(100, 30),
                source="images/spaceship4.png"
            )

        # Add movement of the target
        self.target_direction = 1
        Clock.schedule_interval(self.move_target, 1/60)  # 60 FPS



    # =======================================================================
    # UI Update Methods
    # =======================================================================
    def update_rectangles(self, *args):
        # Update spaceship position (lock at the left bottom)
        spaceship_x = 100
        spaceship_y = 30
        self.spaceship.pos = (spaceship_x, spaceship_y)


    def update_shots_label(self):
        app = App.get_running_app()
        if app.root:
            level_screen = app.root.get_screen('level4game')
            level_screen.ids.shots_label.text = f"Number of shots: {self.shots_left}/8"


    # =======================================================================
    # Game Logic Methods
    # =======================================================================
    """
    Switch the current laser type.
    """

    def switch_weapon(self, weapon_type):
        if weapon_type in ["laser_red", "laser_blue"]:
            self.current_weapon = weapon_type

    def fire_cannon(self):
        self.fire_laser()

    def fire_laser(self):
        if self.shots_left <= 0:
            self.show_game_over_popup()
            return

        self.shots_left -= 1
        self.update_shots_label()

        if self.laser_beam:
            self.canvas.before.remove(self.laser_beam)

        start_x = self.spaceship.pos[0] + self.spaceship.size[0] / 2
        start_y = self.spaceship.pos[1] + self.spaceship.size[1] / 2

        end_x = start_x + cos(radians(self.angle)) * self.LASER_DIST
        end_y = start_y + sin(radians(self.angle)) * self.LASER_DIST

        # Set the laser's color based on the type
        laser_color = (1, 0, 0, 1) if self.current_weapon == "laser_red" else (0, 0, 1, 1)

        closest_collision = None
        closest_distance = float('inf')
        collision_type = None

        # Check collision with the target
        target_collision = self.check_laser_collision(start_x, start_y, end_x, end_y, self.spaceship_target)
        if target_collision:
            dist = self.get_distance(start_x, start_y, target_collision[0], target_collision[1])
            if dist < closest_distance:
                closest_collision = target_collision
                closest_distance = dist
                collision_type = "target"

        # Check the collision with asteroids
        for asteroid in self.asteroids:
            if asteroid.pos[0] != -1000:
                asteroid_collision = self.check_laser_collision(start_x, start_y, end_x, end_y, asteroid)
                if asteroid_collision:
                    dist = self.get_distance(start_x, start_y, asteroid_collision[0], asteroid_collision[1])
                    if dist < closest_distance:
                        closest_collision = asteroid_collision
                        closest_distance = dist
                        collision_type = "asteroid"

        if closest_collision:
            end_x, end_y = closest_collision
            if collision_type == "target":
                if self.current_weapon == "laser_red":
                    self.hit_target()
                else:
                    self.show_wrong_laser_error("red")
            elif collision_type == "asteroid":
                if self.current_weapon == "laser_blue":
                    # Rimuovi l'asteroide colpito
                    for asteroid in self.asteroids:
                        if (asteroid.pos[0] <= end_x <= asteroid.pos[0] + asteroid.size[0] and
                            asteroid.pos[1] <= end_y <= asteroid.pos[1] + asteroid.size[1]):
                            asteroid.pos = (-1000, -1000)
                            break
                else:
                    self.show_wrong_laser_error("blue")

        # Draw the laser
        with self.canvas.before:
            Color(*laser_color)
            self.laser_beam = Line(points=[start_x, start_y, end_x, end_y], width=2)
            Color(1, 1, 1, 1)

        # Remove the laser after 3 seconds
        Clock.schedule_once(self.end_laser, 3.0)

    def check_laser_collision(self, start_x, start_y, end_x, end_y, obj):
        """
        Calculate the exact collision point between the laser and the object
        """
        obj_left = obj.pos[0]
        obj_right = obj.pos[0] + obj.size[0]
        obj_bottom = obj.pos[1]
        obj_top = obj.pos[1] + obj.size[1]

        # Check 100 points along the laser's path
        for t in range(100):
            point_x = start_x + (end_x - start_x) * t / 100
            point_y = start_y + (end_y - start_y) * t / 100

            if (point_x > obj_left and point_x < obj_right and
                    point_y > obj_bottom and point_y < obj_top):
                return (point_x, point_y)
        return None

    def get_distance(self, x1, y1, x2, y2):
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def end_laser(self, dt):
        if self.laser_beam:
            self.canvas.before.remove(self.laser_beam)
            self.laser_beam = None
        if hasattr(self, 'reflected_beam'):
            self.canvas.before.remove(self.reflected_beam)
            self.reflected_beam = None


    def set_angle(self, angle):
        """
        Set the angle of the laser.
        """
        self.angle = angle


    # =======================================================================
    # Target Movement
    # =======================================================================
    def move_target(self, dt):
        current_x = self.spaceship_target.pos[0]
        new_x = current_x + (2 * self.target_direction)

        if new_x > self.width - self.spaceship_target.size[0] - 100:  # Margine destro
            self.target_direction = -1
        elif new_x < 700:
            self.target_direction = 1

        self.spaceship_target.pos = (new_x, self.spaceship_target.pos[1])


    # =======================================================================
    # Popup Handling Methods
    # =======================================================================

    def show_game_over_popup(self):
        """Show the popup of game over"""
        if not self.popup_visible:
            self.popup_visible = True
            content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            
            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)
            
            button = Button(
                text="Try Again",
                font_size=18,
                size_hint=(None, None),
                size=(200, 50),
                background_color=[0.5, 0, 0, 1],
                color=[1, 1, 1, 1]
            )
            
            button_layout.add_widget(button)
            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)
            content.add_widget(button_layout)
            
            self.P = Popup(
                title="Game Over! You ran out of shots!",
                title_align='center',
                title_size=30,
                title_color=[0.5, 0, 0, 1],
                content=content,
                size_hint=(None, None),
                size=(500, 300),
                background='images/popup.png',
                auto_dismiss=False
            )

            button.bind(on_press=lambda x: self.reset_and_dismiss())
            self.P.open()

    def reset_and_dismiss(self):
        if hasattr(self, 'P'):
            self.P.dismiss()
        self.popup_visible = False
        self.shots_left = 8
        self.update_shots_label()
        self.reset_level()

    def show_wrong_laser_error(self, required_color):
        if not self.popup_visible:
            self.popup_visible = True
            content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)

            label_space_left = Label(size_hint_x=1)
            button_layout.add_widget(label_space_left)

            button = Button(
                text="Try Again",
                font_size=18,
                size_hint=(None, None),
                size=(200, 50),
                background_color=[0.5, 0, 0, 1],
                color=[1, 1, 1, 1]
            )

            button_layout.add_widget(button)
            label_space_right = Label(size_hint_x=1)
            button_layout.add_widget(label_space_right)
            content.add_widget(button_layout)

            self.P = Popup(
                title=f"Use the {required_color} laser!",
                title_align='center',
                title_size=30,
                title_color=[0.5, 0, 0, 1],
                content=content,
                size_hint=(None, None),
                size=(500, 300),
                background='images/popup.png',
                auto_dismiss=False
            )

            button.bind(on_press=self.dismiss_popup)
            self.P.open()



    def dismiss_popup(self, instance):
        self.P.dismiss()
        self.popup_visible = False



    # =======================================================================
    # Level Reset Methods
    # =======================================================================
    def reset_level(self):
        self.shots_left = 8
        self.update_shots_label()
        

        asteroid_positions = [
            (380, 500), (470, 500), (560, 500), (650, 500), (740, 500), (830, 500), (920, 500),
            (380, 400), (470, 400), (560, 400), (650, 400), (740, 400), (830, 400), (920, 400),
            (380, 300), (470, 300), (560, 300), (650, 300), (740, 300), (830, 300), (920, 300),
            (380, 200), (470, 200), (560, 200), (650, 200), (740, 200), (830, 200), (920, 200)
        ]
        

        for asteroid in self.asteroids:
            self.canvas.before.remove(asteroid)
        

        self.asteroids = []
        with self.canvas.before:
            for i, pos in enumerate(asteroid_positions):
                source = "images/asteroid1.png" if i % 2 == 0 else "images/asteroid2.png"
                asteroid = Rectangle(
                    size=(120, 120),
                    pos=pos,
                    source=source
                )
                self.asteroids.append(asteroid)


        self.spaceship_target.pos = (900, 600)

        self.start_time = time.time()

        if self.laser_beam:
            self.canvas.before.remove(self.laser_beam)
            self.laser_beam = None




    # =======================================================================
    # Target Hit Handling
    # =======================================================================
    def hit_target(self):
        elapsed_time = time.time() - self.start_time
        # Add the record at Hall of Fame
        app = App.get_running_app()
        hall_of_fame = app.root.get_screen('halloffame')
        hall_of_fame.add_record(f'level4', elapsed_time)

        content = BoxLayout(orientation='vertical', padding=(20, 80), spacing=40)
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)

        label_space_left = Label(size_hint_x=1)
        button_layout.add_widget(label_space_left)

        button = Button(
            text="Game Complete!",
            font_size=18,
            size_hint=(None, None),
            size=(200, 50),
            background_color=[0, 0.7, 0, 1],
            color=[1, 1, 1, 1]
        )

        button_layout.add_widget(button)
        label_space_right = Label(size_hint_x=1)
        button_layout.add_widget(label_space_right)
        content.add_widget(button_layout)

        self.P = Popup(
            title=f"Congratulation\nTime: {elapsed_time:.2f} sec",
            title_align='center',
            title_size=30,
            title_color=[0, 0.7, 0, 1],
            content=content,
            size_hint=(None, None),
            size=(500, 300),
            background='images/popup.png',
            auto_dismiss=False
        )

        button.bind(on_press=self.congrats)
        self.P.open()

    def congrats(self, instance):
        """
        Transition to the congratulations screen after completing a level or achieving a goal.
        """
        app = App.get_running_app()
        screen_manager = app.root
        if hasattr(screen_manager, 'current'):
            screen_manager.current = 'congrats'
            if hasattr(self, 'P') and self.P:
                self.P.dismiss()





#=======================================================================
# Level1Game(Screen) class
#=======================================================================    
class Level1Game(Screen):
    def __init__(self, **kwargs):
        super(Level1Game, self).__init__(**kwargs)
        self.timer = Timer(self.ids.timer_label)
        
    def on_enter(self, *args):
        App.get_running_app().stop_intro_music()
        self.timer.start()
        if hasattr(self, 'sound'):
            self.sound.stop()
        self.sound = SoundLoader.load('sounds/levels.mp3')
        if self.sound:
            self.sound.loop = True
            self.sound.play()

    def on_leave(self, *args):
        self.timer.stop()
        if hasattr(self, 'sound'):
            self.sound.stop()
        # Riavvia la musica dell'intro solo se si sta tornando al menu
        if self.manager.current == 'mainmenu':
            app = App.get_running_app()
            if hasattr(app, 'intro_sound'):
                app.intro_sound.play()





#=======================================================================
# Level2Game(Screen) class
#=======================================================================
class Level2Game(Screen):
    def __init__(self, **kwargs):
        super(Level2Game, self).__init__(**kwargs)
        self.timer = Timer(self.ids.timer_label)
        
    def on_enter(self, *args):
        App.get_running_app().stop_intro_music()
        self.timer.start()
        if hasattr(self, 'sound'):
            self.sound.stop()
        self.sound = SoundLoader.load('sounds/levels.mp3')
        if self.sound:
            self.sound.loop = True
            self.sound.play()

    def on_leave(self, *args):
        self.timer.stop()
        if hasattr(self, 'sound'):
            self.sound.stop()
        if self.manager.current == 'mainmenu':
            app = App.get_running_app()
            if hasattr(app, 'intro_sound'):
                app.intro_sound.play()




#=======================================================================
# Level3Game(Screen) class
#=======================================================================
class Level3Game(Screen):
    def __init__(self, **kwargs):
        super(Level3Game, self).__init__(**kwargs)
        self.timer = Timer(self.ids.timer_label)

    def on_enter(self, *args):
        App.get_running_app().stop_intro_music()
        self.timer.start()
        if hasattr(self, 'sound'):
            self.sound.stop()
        self.sound = SoundLoader.load('sounds/levels.mp3')
        if self.sound:
            self.sound.loop = True
            self.sound.play()

    def on_leave(self, *args):
        self.timer.stop()
        if hasattr(self, 'sound'):
            self.sound.stop()
        if self.manager.current == 'mainmenu':
            app = App.get_running_app()
            if hasattr(app, 'intro_sound'):
                app.intro_sound.play()



#=======================================================================
# Level4Game(Screen) class
#=======================================================================
class Level4Game(Screen):
    def __init__(self, **kwargs):
        super(Level4Game, self).__init__(**kwargs)
        self.timer = Timer(self.ids.timer_label)

    def on_enter(self, *args):
        App.get_running_app().stop_intro_music()
        self.timer.start()
        if hasattr(self, 'sound'):
            self.sound.stop()
        self.sound = SoundLoader.load('sounds/levels.mp3')
        if self.sound:
            self.sound.loop = True
            self.sound.play()

    def on_leave(self, *args):
        self.timer.stop()
        if hasattr(self, 'sound'):
            self.sound.stop()
        if self.manager.current == 'mainmenu':
            app = App.get_running_app()
            if hasattr(app, 'intro_sound'):
                app.intro_sound.play()




#=======================================================================
# CongratsScreen class
#=======================================================================
class CongratsScreen(Screen):
    def on_enter(self, *args):
        App.get_running_app().stop_intro_music()
        # Carica e riproduci la musica finale
        self.sound = SoundLoader.load('sounds/final.mp3')
        if self.sound:
            self.sound.play()
    
    def go_to_menu(self):
        # Ferma eventuali suoni in riproduzione
        if hasattr(self, 'sound') and self.sound:
            self.sound.stop()

        # Torna al menu e riavvia la musica dell'intro
        self.manager.current = 'mainmenu'
        app = App.get_running_app()
        if hasattr(app, 'intro_sound'):
            app.intro_sound.play()

    def exit_game(self):
        # Ferma eventuali suoni in riproduzione
        if hasattr(self, 'sound') and self.sound:
            self.sound.stop()
        App.get_running_app().stop()



#=======================================================================
# MAINMENU
#=======================================================================
class MainMenu(Screen):
    pass

class LevelSelection(Screen):
    pass




#=======================================================================
# HallOfFame class
#=======================================================================
class HallOfFame(Screen):
    def __init__(self, **kwargs):
        super(HallOfFame, self).__init__(**kwargs)
        self.records = {'level1': [], 'level2': [], 'level3': [], 'level4': []}
        Clock.schedule_once(self.update_display, 0)

    def update_display(self, dt=None):
        # Carica e mostra i record per ogni livello
        for level in ['level1', 'level2', 'level3', 'level4']:
            self.load_records(level)
            self.show_records(level)
    
    def load_records(self, level):
        try:
            with open(f'./records_{level}.txt', 'r') as file:
                self.records[level] = [float(line.strip()) for line in file]
                self.records[level].sort()  # Rank by time
        except FileNotFoundError:
            self.records[level] = []

    def show_records(self, level):
        container = self.ids[f'{level}_container']
        container.clear_widgets()
        
        # Mostra i record del livello
        for i, time in enumerate(self.records[level][:10]):
            position = i + 1
            if position == 1:
                suffix = "ST"
                color = (1, 0.6, 0.2, 1)
            elif position == 2:
                suffix = "ND"
                color = (0.75, 0.75, 0.75, 1)
            elif position == 3:
                suffix = "RD"
                color = (0.8, 0.5, 0.2, 1)
            else:
                suffix = "TH"
                color = (1, 1, 1, 1)

            record_label = Label(
                text=f"{position}{suffix}    {time:.2f}s",
                color=color,
                size_hint_y=None,
                height=dp(30),
                font_size='18sp'
            )
            container.add_widget(record_label)

    def add_record(self, level, time):
        self.records[level].append(time)
        self.records[level].sort()
        self.records[level] = self.records[level][:10]  # top 10 scores
        
        # Salva i record su file
        with open(f'./records_{level}.txt', 'w') as file:
            for record in self.records[level]:
                file.write(f"{record}\n")
        
        # Aggiorna il display
        self.show_records(level)

#=======================================================================

class Help(Screen):
    pass

class IntroStory(Screen):
    pass


class MyScreenManager(ScreenManager):
    pass

#=======================================================================
# MenuApp class
#=======================================================================
class MenuApp(App):
    def build(self):
        self.title = "Shadow Cannon"
        sm = MyScreenManager(transition=FadeTransition())
        sm.add_widget(IntroStory(name="introstory"))
        sm.add_widget(MainMenu(name="mainmenu"))
        sm.add_widget(LevelSelection(name="levelselection"))
        sm.add_widget(Help(name="help"))
        sm.add_widget(Level1Game(name="level1game"))
        sm.add_widget(Level2Game(name="level2game"))
        sm.add_widget(Level3Game(name="level3game"))
        sm.add_widget(Level4Game(name="level4game"))
        sm.add_widget(CongratsScreen(name='congrats'))
        sm.add_widget(HallOfFame(name="halloffame"))
        sm.current = "introstory"
        
        # Avvia la musica dell'intro
        self.intro_sound = SoundLoader.load('sounds/intro.mp3')
        if self.intro_sound:
            self.intro_sound.loop = True
            self.intro_sound.play()

        return sm

    def stop_intro_music(self):
        if hasattr(self, 'intro_sound') and self.intro_sound:
            self.intro_sound.stop()


#=======================================================================
# Run the game
#=======================================================================
if __name__ == '__main__':
    MenuApp().run()