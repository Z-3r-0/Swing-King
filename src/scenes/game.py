import pygame
import math
from src.entities import Ball, Camera, Terrain, Obstacle
from src.scene import Scene
from src.scenetype import SceneType
from src.utils import level_loader, drag_handler, physics_utils
from src import physics # Import the physics module

# --- Constants ---
BALL_START_X, BALL_START_Y = 800, 500 # TODO - Replace with level data later
SCENE_WIDTH, SCENE_HEIGHT = 10000, 2000 # TODO - Replace with level data later

MAX_SHOT_FORCE = 1500.0 # Max force magnitude from dragging
MIN_SHOT_FORCE = 50.0   # Min force needed to register a shot

# Trajectory prediction parameters
PREDICTION_STEPS = 70
PREDICTION_DT = 1 / 60.0 # Simulate at target framerate
PREDICTION_DOT_SPACING = 4 # Draw a dot every N steps
PREDICTION_DOT_RADIUS = 3
PREDICTION_DOT_COLOR = (255, 255, 255, 180) # White with some transparency

# --- Physics Simulation Parameters ---
PHYSICS_SUB_STEPS = 2  # Number of physics steps per frame (Increase for stability, decrease for performance)
FIXED_DT = 1.0 / (120.0 * PHYSICS_SUB_STEPS) # Fixed time step for each physics sub-step (assuming target 60fps)


class Game(Scene):
    def __init__(self, screen, scene_from: SceneType = None):
        super().__init__(screen, SceneType.GAME, "Game", scene_from)

        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        # Game State
        self.dragging = False
        self.drag_start_pos = None # Screen position where drag started
        self.current_mouse_pos = None # Current screen position during drag
        self.current_force = 0
        self.current_angle = 0

        # Load Level
        self.level_path = "data/levels/test_level.json" # TODO: Make dynamic later
        self.terrain_data, self.obstacles_data = level_loader.load_json_level(self.level_path)

        # Create Game Objects
        # TODO: Get ball start position from level data
        ball_start_pos = pygame.Vector2(BALL_START_X, BALL_START_Y)
        self.ball = Ball(ball_start_pos, 4.2, 0.047, pygame.Color("white"),
                         "assets/images/balls/golf_ball.png")

        self.terrain_polys = level_loader.json_to_list(self.terrain_data, self.screen, 0)
        self.obstacles = level_loader.json_to_list(self.obstacles_data, self.screen, 1)

        # Camera
        # TODO: Get level bounds from level data if available
        self.camera = Camera(pygame.Vector2(0, 0), self.width, self.height, SCENE_WIDTH, SCENE_HEIGHT)
        self.camera.calculate_position(self.ball.position) # Initial camera position

        # Background
        try:
            self.background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
            self.background = pygame.transform.smoothscale(self.background, (self.width, self.height))
        except pygame.error as e:
            print(f"Error loading background image: {e}")
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill(pygame.Color("lightblue")) # Fallback color

        # Timing - Accumulator for fixed physics steps
        self.physics_accumulator = 0.0
        self.dt = 0.0 # Frame delta time

    def handle_events(self):
        """Handles user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # In a real game, you might want to switch to a quit confirmation scene
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Example: Go back to the main menu
                    self.switch_scene(SceneType.MAIN_MENU) # Assumes MAIN_MENU exists

            # --- Mouse Drag Handling ---
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Start dragging only if the ball isn't moving
                if not self.ball.is_moving:
                    mouse_pos = pygame.Vector2(event.pos)
                    ball_screen_pos = self.ball.position - self.camera.position
                    # Check if click is reasonably close to the ball
                    if mouse_pos.distance_to(ball_screen_pos) < self.ball.scaled_radius * 1.5:
                        self.dragging = True
                        self.drag_start_pos = ball_screen_pos # Use ball's screen pos as anchor
                        self.current_mouse_pos = mouse_pos
                        # print("Dragging started") # Optional debug

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.current_mouse_pos = pygame.Vector2(event.pos)
                    # Calculate live force/angle for trajectory preview
                    self.current_force, self.current_angle = drag_handler.calculate_shot_parameters(
                        self.drag_start_pos,
                        self.current_mouse_pos,
                        MAX_SHOT_FORCE,
                        MIN_SHOT_FORCE
                    )

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging:
                    self.dragging = False
                    # print("Dragging ended") # Optional debug
                    # Calculate final force/angle
                    final_force, final_angle = drag_handler.calculate_shot_parameters(
                        self.drag_start_pos,
                        self.current_mouse_pos,
                        MAX_SHOT_FORCE,
                        MIN_SHOT_FORCE
                    )
                    # Shoot the ball if force is sufficient
                    if final_force >= MIN_SHOT_FORCE:
                        self.ball.shoot(final_force, final_angle)
                    # else: # Optional debug
                        # print("Shot cancelled (force too low)")
                    # Reset drag state
                    self.drag_start_pos = None
                    self.current_mouse_pos = None
                    self.current_force = 0
                    self.current_angle = 0

    def update_physics(self):
        """Updates game physics using fixed sub-steps."""
        # Add frame time to the accumulator
        self.physics_accumulator += self.dt

        # While there's enough accumulated time for a fixed step, process it
        while self.physics_accumulator >= FIXED_DT:
            if self.ball.is_moving:
                # Perform one physics sub-step
                still_moving = physics.update_ball_physics(
                    self.ball,
                    self.terrain_polys,
                    self.obstacles,
                    FIXED_DT # Use the fixed delta time here
                )
                # If the physics step stopped the ball, break the sub-step loop
                if not still_moving:
                    self.ball.is_moving = False
                    self.physics_accumulator = 0 # Clear accumulator if ball stops
                    break
            else:
                 # If ball isn't moving, no need for more physics steps this frame
                 self.physics_accumulator = 0 # Clear accumulator
                 break

            # Decrease accumulator by the fixed step time
            self.physics_accumulator -= FIXED_DT

        # Update camera AFTER all physics steps for the frame are done
        # (or during if you want smoother camera during slow-mo, but this is simpler)
        if self.ball.is_moving or self.dragging:
             self.camera.calculate_position(self.ball.position)


    def draw(self):
        """Draws all game elements to the screen."""
        # Draw background
        self.screen.blit(self.background, (0, 0))

        # Draw terrain polygons (pass camera offset)
        for poly in self.terrain_polys:
            poly.draw_polygon(self.screen, self.camera.position)

        # Draw obstacles (pass camera offset)
        for obs in self.obstacles:
            obs.draw_obstacle(self.screen, self.camera.position)
            # Optional: Draw obstacle collision points/boxes for debugging
            # obs.draw_points(self.screen, self.camera.position)
            # obs.draw_bounding_box(self.screen, self.camera.position)


        # Draw the ball (pass camera offset)
        # Interpolation could be added here for smoother visuals between physics steps,
        # but let's keep it simple for now. Draw at the final physics position.
        self.ball.draw(self.screen, self.camera.position)

        # Draw aiming line and trajectory prediction if dragging
        if self.dragging and self.drag_start_pos and self.current_mouse_pos:
            # Draw the drag line
            drag_handler.draw_drag_line(
                self.screen,
                self.drag_start_pos, # Line starts from ball's screen pos
                self.current_mouse_pos,
                pygame.Color("red"),
                2
            )

            # Draw predicted trajectory if force is sufficient
            if self.current_force >= MIN_SHOT_FORCE:
                 angle_rad = math.radians(self.current_angle)
                 initial_vel = pygame.Vector2(
                     self.current_force * math.cos(angle_rad),
                     self.current_force * math.sin(angle_rad)
                 )
                 physics_utils.draw_predicted_trajectory(
                     self.screen,
                     self.ball.position, # Start prediction from ball's world pos
                     initial_vel,
                     physics.GRAVITY,
                     physics.DEFAULT_DAMPING,
                     PREDICTION_DT, # Use prediction DT here, not fixed physics DT
                     PREDICTION_STEPS,
                     self.camera.position, # Pass camera offset
                     PREDICTION_DOT_COLOR,
                     PREDICTION_DOT_RADIUS,
                     PREDICTION_DOT_SPACING
                 )

    def run(self):
        """Main game loop for the Game scene."""
        self.running = True
        while self.running:
            # Calculate frame delta time
            try:
                # Convert milliseconds to seconds
                self.dt = self.clock.tick(self.fps) / 1000.0
            except AttributeError:
                self.dt = pygame.time.Clock().tick(60) / 1000.0

            # Clamp dt to avoid large spikes ("spiral of death")
            self.dt = min(self.dt, 0.1) # Don't allow dt larger than 0.1 seconds

            # --- Game Logic ---
            self.handle_events()
            self.update_physics() # This now handles sub-steps internally
            self.draw()

            # --- Display Update ---
            pygame.display.flip()

        # Loop finished (e.g., switched scene)
        print(f"Exiting {self.name} scene.")