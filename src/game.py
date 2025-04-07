from src.entities import Ball, Camera
import src.utils.settings_loader as settings
from src.utils import *
from .animation import Animation

BALL_START_X, BALL_START_Y = 800, 500 # TODO - REPLACE WITH LEVEL DATA LATER
SCENE_WIDTH, SCENE_HEIGHT = 10000, 2000 # TODO - REPLACE WITH LEVEL DATA LATER
GRAVITY = 980  # Gravitational acceleration in pixels/s² # TODO - REPLACE WITH LEVEL DATA LATER
BALL_RADIUS = 50.0

class Game:

    def __init__(self, resolution:pygame.Vector2):
        self.screen = pygame.display.set_mode(resolution)
        self.dt = 0
        self.dragging = False
        self.drag_done = False
        self.ball_in_motion = False

        self.max_force = 500

        self.force = 0
        self.angle = 0

        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        self.level_path = "data/levels/level2.json"

        # Load game settings
        self.settings = settings.load_json_settings("data/settings/settings.json")

        # Load level data
        self.terrain_data, self.obstacles_data = level_loader.load_json_level(self.level_path)

        # Initialize game objects
        self.ball = Ball(pygame.Vector2(BALL_START_X, BALL_START_Y), 4.2, 0.047, pygame.Color("white"),
                 "assets/images/balls/golf_ball.png")

        # Load terrain and obstacles
        self.terrain_polys = level_loader.json_to_list(self.terrain_data, self.screen, 0)
        self.obstacles = level_loader.json_to_list(self.obstacles_data, self.screen, 1)

        # Initialize camera
        self.camera = Camera(pygame.Vector2(0, 0), self.width, self.height)

        # Load background
        self.background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
        self.background = pygame.transform.smoothscale(self.background, (self.width, self.height))

        # Set up the clock
        self.clock = pygame.time.Clock()
        self.fps = self.settings["graphics"]["fps_limit"]

        self.dt = 1 / self.fps

        # Set up the dot parameters
        self.dot_spacing = 10
        self.dot_radius = 2
        self.dot_color = (255, 0, 0)

        self.golfer_animation = Animation("assets/images/golfer", pygame.Vector2(500, 500))
        self.golfer_animation_sprite = pygame.sprite.Group()
        self.golfer_animation_sprite.add(self.golfer_animation)

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for poly in self.terrain_polys:
            poly.draw(self.screen)

        for obs in self.obstacles:
            obs.draw(self.screen)

        self.ball.draw(self.screen)

        self.golfer_animation_sprite.draw(self.screen)
        self.golfer_animation_sprite.update()


        # Draw the trajectory
        if self.dragging:
            current_mouse = pygame.mouse.get_pos()

            pygame.draw.line(self.screen, pygame.Color("red"), self.ball.position, current_mouse, 2)
            draw_predicted_trajectory(self.ball.position, self.force, self.angle, GRAVITY, self.fps, self.screen)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if (not self.drag_done) and math.hypot(event.pos[0] - self.ball.position.x,
                                                       event.pos[1] - self.ball.position.y) <= BALL_RADIUS:
                    self.dragging = True

            if event.type == pygame.MOUSEBUTTONUP and self.dragging:
                if not self.drag_done:
                    # Use the center of the ball for the calculation
                    force, angle = drag_and_release(self.ball.position, pygame.mouse.get_pos())

                    self.ball.velocity = pygame.Vector2(
                        -force * math.cos(math.radians(angle)),  # Inversion of the X axis
                        force * math.sin(math.radians(angle))
                    )

                    self.dragging = False
                    self.ball_in_motion = True
                    self.drag_done = True

        if self.ball_in_motion:

            if self.ball.velocity.length() < 0.1:
                self.ball.velocity = pygame.Vector2(0, 0)
                self.ball_in_motion = False
                self.drag_done = False

            # Update the position with the initial movement
            self.ball.position += self.ball.velocity * self.dt

            # Apply gravity realistically:
            self.ball.velocity.y += GRAVITY * self.dt

            # Apply a slight friction to the entire velocity
            self.ball.velocity *= 0.98

        # Update the camera
        self.camera.calculate_position(self.ball.position, SCENE_WIDTH, SCENE_HEIGHT)

        # Display the drag line and the beginning of the predicted trajectory
        if self.dragging:
            current_mouse = pygame.mouse.get_pos()
            self.force, self.angle = drag_and_release(self.ball.position, current_mouse)

    def run(self):

        while True:
            self.handle_events()
            self.draw()

            pygame.display.flip()
            self.clock.tick(self.fps)