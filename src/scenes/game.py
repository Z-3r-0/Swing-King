import pygame
import math
import json
import os
from datetime import datetime
import time # For potential debugging delays

# Import base class and types FIRST
from src.scene import Scene
from src.scenetype import SceneType

# Then import entities and utils
# Make sure Flag is imported if it's a separate class
from src.entities import Ball, Camera, Terrain, Obstacle, Flag
from src.utils import level_loader, drag_handler, physics_utils

# Finally, import the physics logic module
from src import physics

# --- Constants ---
# BALL_START_X, BALL_START_Y = 800, 500 # Default if not found in level
SCENE_WIDTH, SCENE_HEIGHT = 10000, 2000 # TODO - Replace with level data later

MAX_SHOT_FORCE = 2500.0 # User's value
MIN_SHOT_FORCE = 50.0   # Min force needed to register a shot

# --- Trajectory prediction parameters (OPTIMIZED) ---
PREDICTION_STEPS = 50 # Reduced steps
PREDICTION_DT = 1 / 60.0 # Simulate at target framerate
PREDICTION_DOT_SPACING = 6 # Increased spacing
PREDICTION_DOT_RADIUS = 3
PREDICTION_DOT_COLOR = (255, 255, 255, 180) # White with some transparency

# --- Physics Simulation Parameters ---
PHYSICS_SUB_STEPS = 8 # Keep substeps high for stability
# FIXED_DT will be calculated in __init__ based on self.fps

# --- Optimization Parameters ---
# No spatial grid or terrain chunking in this version


# --- Define the Game Class ---
class Game(Scene):
    def __init__(self, screen, levels_dir_path: str = "data/levels", scene_from: SceneType = None):
        # Call the base class constructor FIRST
        super().__init__(screen, SceneType.GAME, "Game", scene_from)
        print("Initializing Game Scene...")

        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        # --- Calculate Fixed DT based on actual FPS target ---
        target_fps = getattr(self, 'fps', 60)
        if target_fps <= 0: target_fps = 60
        self.fixed_dt = 1.0 / (target_fps * PHYSICS_SUB_STEPS)
        print(f"Game Scene - Target FPS: {target_fps}, Substeps: {PHYSICS_SUB_STEPS}, Fixed DT: {self.fixed_dt}")

        # Game State
        self.dragging = False
        self.drag_start_pos = None
        self.current_mouse_pos = None
        self.current_force = 0
        self.current_angle = 0
        self.ball_start_pos = pygame.Vector2(800, 500) # Default start pos

        # Level Management
        self.level_dir = levels_dir_path
        self.current_level_id = 1 # Default to level 1 initially
        self.level_path = f"{self.level_dir}/level{self.current_level_id}.json"

        # Gameplay State
        self.stroke_count = 0
        self.flag = None # Will hold the Flag object instance
        self.saved_stats = False # Flag to prevent multiple saves per win

        # UI Elements (Stroke Counter)
        try:
            self.ui_font = pygame.font.SysFont('Arial', 30)
        except:
            self.ui_font = pygame.font.Font(None, 36) # Fallback font
        self.previous_stroke_count = -1
        self.animate_stroke_timer = 0
        self.STROKE_ANIM_DURATION = 10
        self.STROKE_ANIM_SCALE = 1.1
        self.STROKE_TEXT_COLOR = (220, 70, 70)
        self.STROKE_BG_COLOR = (40, 40, 40, 180)
        self.STROKE_PADDING = 8
        self.STROKE_CORNER_RADIUS = 5

        # Load Initial Level Content
        self.terrain_polys = []
        self.obstacles = []
        self.collidable_obstacles = []
        self.load_level(self.current_level_id) # Load initial level

        # Camera
        print("Initializing Camera...")
        level_w = SCENE_WIDTH # TODO: Get level bounds from level data
        level_h = SCENE_HEIGHT
        self.camera = Camera(pygame.Vector2(0, 0), self.width, self.height, level_w, level_h)
        self.camera.calculate_position(self.ball.position) # Center on ball's loaded start pos

        # Background
        print("Loading Background...")
        try:
            self.background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
            self.background = pygame.transform.smoothscale(self.background, (self.width, self.height))
        except pygame.error as e:
            print(f"Error loading background image: {e}. Using fallback.")
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill(pygame.Color("lightblue"))

        # Timing
        self.physics_accumulator = 0.0
        self.dt = 0.0 # Frame delta time

        print("Game Scene Initialized.")

    def load_level(self, level_id: int):
        """Loads level data, creates objects, and resets game state."""
        print(f"Loading level ID: {level_id}")
        self.current_level_id = level_id
        self.level_path = f"{self.level_dir}/level{level_id}.json"

        # Load data from JSON
        self.terrain_data, self.obstacles_data = level_loader.load_json_level(self.level_path)
        if not self.terrain_data and not self.obstacles_data:
             print(f"Warning: Level data is empty for {self.level_path}!")

        # Create objects from data
        print("Loading terrain polygons...")
        self.terrain_polys = level_loader.json_to_list(self.terrain_data, self.screen, 0)
        print(f"Loaded {len(self.terrain_polys)} terrain polygons.")

        print("Loading obstacles...")
        self.obstacles = level_loader.json_to_list(self.obstacles_data, self.screen, 1)
        self.collidable_obstacles = [obs for obs in self.obstacles if obs.is_colliding]
        print(f"Loaded {len(self.obstacles)} total obstacles ({len(self.collidable_obstacles)} collidable).")

        # Find start position and flag
        self.flag = None
        found_start = False
        for obstacle in self.obstacles:
            # Check for start position marker (non-flag obstacle with characteristic "start")
            if not isinstance(obstacle, Flag) and getattr(obstacle, 'characteristic', None) == "start":
                self.ball_start_pos = obstacle.position.copy()
                print(f"Found start position at {self.ball_start_pos}")
                found_start = True
            # Check for the Flag object
            if isinstance(obstacle, Flag):
                self.flag = obstacle
                print(f"Found flag at {self.flag.position}")
                # Don't break here in case start marker is after flag in list

        if not found_start:
            print("Warning: No start position found in level data. Using default.")
            # Keep the default self.ball_start_pos

        # Reset game state
        self.reset_level_state()

        # Update camera to new start position
        if hasattr(self, 'camera'): # Check if camera exists (might not on first init call)
             self.camera.calculate_position(self.ball.position)


    def reset_level_state(self):
        """Resets ball position, velocity, strokes, and flags for the current level."""
        print("Resetting level state...")
        # Reset Ball
        if not hasattr(self, 'ball'): # Create ball if it doesn't exist yet (first load)
             self.ball = Ball(self.ball_start_pos.copy(), 4.2, 0.047, pygame.Color("white"),
                              "assets/images/balls/golf_ball.png")
        else:
             self.ball.position = self.ball_start_pos.copy()
             self.ball.velocity = pygame.Vector2(0, 0)
             self.ball.is_moving = False
             self.ball.reset_collision_state()

        # Reset Gameplay State
        self.stroke_count = 0
        self.previous_stroke_count = -1 # For UI animation
        self.animate_stroke_timer = 0
        self.dragging = False
        self.drag_start_pos = None
        self.current_mouse_pos = None
        self.current_force = 0
        self.current_angle = 0
        self.saved_stats = False
        self.physics_accumulator = 0.0


    def handle_events(self):
        """Handles user input events for the Game scene."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Go back to main menu (or level select if implemented)
                    self.switch_scene(SceneType.MAIN_MENU) # Or LEVEL_SELECTOR
                elif event.key == pygame.K_r: # Add a key to reset the current level
                     print("Resetting level via R key...")
                     self.reset_level_state()
                     # Recenter camera after reset
                     self.camera.calculate_position(self.ball.position)


            # --- Mouse Drag Handling ---
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Allow aiming only if the ball is not moving
                if not self.ball.is_moving:
                    mouse_pos = pygame.Vector2(event.pos)
                    ball_screen_pos = self.ball.position - self.camera.position
                    if mouse_pos.distance_to(ball_screen_pos) < self.ball.scaled_radius * 1.5:
                        self.dragging = True
                        self.drag_start_pos = ball_screen_pos # Use screen pos for drag calculation anchor
                        self.current_mouse_pos = mouse_pos
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.current_mouse_pos = pygame.Vector2(event.pos)
                    # Calculate live force/angle for trajectory preview
                    self.current_force, self.current_angle = drag_handler.calculate_shot_parameters(
                        self.drag_start_pos, self.current_mouse_pos, MAX_SHOT_FORCE, MIN_SHOT_FORCE
                    )
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging:
                    self.dragging = False
                    # Calculate final force/angle
                    final_force, final_angle = drag_handler.calculate_shot_parameters(
                        self.drag_start_pos, self.current_mouse_pos, MAX_SHOT_FORCE, MIN_SHOT_FORCE
                    )
                    # Shoot the ball if force is sufficient
                    if final_force >= MIN_SHOT_FORCE:
                        self.ball.shoot(final_force, final_angle)
                        self.stroke_count += 1 # Increment stroke count here
                    # Reset drag state
                    self.drag_start_pos = None
                    self.current_mouse_pos = None
                    self.current_force = 0
                    self.current_angle = 0

    def update_physics(self):
        """Updates game physics using fixed sub-steps."""
        if not self.ball.is_moving: # Skip physics if ball isn't moving
            return

        self.physics_accumulator += self.dt
        max_steps_per_frame = PHYSICS_SUB_STEPS * 2
        steps_this_frame = 0

        while self.physics_accumulator >= self.fixed_dt and steps_this_frame < max_steps_per_frame:
            if self.ball.is_moving: # Double check inside loop
                # Pass ONLY collidable obstacles to physics
                still_moving = physics.update_ball_physics(
                    self.ball,
                    self.terrain_polys,
                    self.collidable_obstacles,
                    self.fixed_dt
                )
                if not still_moving:
                    self.ball.is_moving = False
                    self.physics_accumulator = 0 # Clear accumulator
                    # --- Check for flag collision AFTER ball stops ---
                    self.check_win_condition()
                    break # Exit sub-step loop for this frame
            else:
                 self.physics_accumulator = 0 # Should not happen if outer check passed
                 break

            self.physics_accumulator -= self.fixed_dt
            steps_this_frame += 1

        # Update camera if ball moved or if aiming
        if self.ball.is_moving or self.dragging:
             self.camera.calculate_position(self.ball.position)

    def check_win_condition(self):
        """Checks if the ball stopped in the hole."""
        if self.check_flag_collision():
            print(f"Level {self.current_level_id} Complete! Strokes: {self.stroke_count}")
            if not self.saved_stats:
                self.save_level_stats(self.current_level_id)
                self.saved_stats = True
            # TODO: Transition to a results screen or level select
            # For now, just switch back to main menu
            self.switch_scene(SceneType.MAIN_MENU) # Or LEVEL_SELECTOR


    def check_flag_collision(self):
        """Checks if the ball reached the base of the flag (hole)."""
        if not self.flag: # or self.ball.is_moving: # Check only when stopped
            return False

        # Simple distance check from ball center to flag position (adjust radius as needed)
        hole_radius = self.flag.rect.width / 3 # Approximate radius for hole area
        distance_sq = self.ball.position.distance_squared_to(self.flag.position)

        if distance_sq < (hole_radius + self.ball.scaled_radius)**2:
             # More precise check: Use mask overlap for the flag base if needed
             # This requires the Flag object to have the necessary mask setup
             try:
                 # Assuming flag base mask logic from friend's code is desired
                 flag_surface = self.flag.animation.image # Friend's code used animation.image
                 flag_mask = pygame.mask.from_surface(flag_surface)
                 base_height = flag_surface.get_height() // 4
                 base_rect = pygame.Rect(0, flag_surface.get_height() - base_height,
                                         flag_surface.get_width(), base_height)
                 base_mask = pygame.mask.Mask(flag_surface.get_size())
                 for x in range(base_rect.width):
                     for y in range(base_rect.height):
                         if flag_mask.get_at((x, base_rect.y + y)):
                             base_mask.set_at((x, base_rect.y + y), 1)

                 offset = (int(self.ball.rect.left - self.flag.animation.rect.left),
                           int(self.ball.rect.top - self.flag.animation.rect.top))

                 overlap = base_mask.overlap(self.ball.mask, offset)
                 return overlap is not None
             except AttributeError:
                 # Fallback if flag doesn't have animation or mask setup as expected
                 print("Warning: Flag object missing expected attributes for mask collision. Using distance check.")
                 return distance_sq < (hole_radius + self.ball.scaled_radius)**2 # Fallback to distance
             except Exception as e:
                 print(f"Error during flag mask collision check: {e}")
                 return False # Error during check
        else:
            return False


    def save_level_stats(self, level_id: int):
        """Saves the stats of the finished level in a JSON file."""
        stats_dir = "data/stats"
        try:
            os.makedirs(stats_dir, exist_ok=True)
            stats_file = f"{stats_dir}/level_{level_id}_stats.json"
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_data = {"date": current_time, "strokes": self.stroke_count}

            existing_data = []
            if os.path.exists(stats_file):
                try:
                    with open(stats_file, 'r') as file:
                        existing_data = json.load(file)
                    if not isinstance(existing_data, list): existing_data = []
                except (json.JSONDecodeError, FileNotFoundError): existing_data = []

            existing_data.append(new_data)

            with open(stats_file, 'w') as file:
                json.dump(existing_data, file, indent=4)
            print(f"Level {level_id} stats saved: {new_data}")
        except Exception as e:
            print(f"Error saving level stats for level {level_id}: {e}")


    def draw(self):
        """Draws all game elements using simple camera culling."""
        self.screen.blit(self.background, (0, 0))
        visible_rect = self.camera.get_rect()

        # --- Draw Terrain using Simple Culling ---
        for poly in self.terrain_polys:
            if poly.rect.colliderect(visible_rect):
                poly.draw_polygon(self.screen, self.camera.position)

        # --- Draw Obstacles using Simple Culling ---
        for obs in self.obstacles:
            try:
                # Skip drawing the start marker if it's just a position indicator
                if not isinstance(obs, Flag) and getattr(obs, 'characteristic', None) == "start":
                    continue

                obs_rect = obs.get_rotated_rect()
                if obs_rect.colliderect(visible_rect):
                    # Use the obstacle's own draw method if it exists, otherwise default
                    if hasattr(obs, 'draw') and callable(obs.draw):
                         obs.draw(self.screen, self.camera.position) # Assumes obstacles have a draw method
                    elif hasattr(obs, 'draw_obstacle') and callable(obs.draw_obstacle):
                         obs.draw_obstacle(self.screen, self.camera.position) # Fallback to original name
                    else:
                         # Basic fallback if no draw method (shouldn't happen with Obstacle class)
                         if hasattr(obs, 'image'):
                              screen_pos = obs.position - self.camera.position
                              self.screen.blit(obs.image, screen_pos)

            except Exception as e:
                obj_id = getattr(obs, 'id', 'N/A')
                print(f"Error drawing obstacle {type(obs)} ID '{obj_id}': {e}")

        # Draw Ball
        self.ball.draw(self.screen, self.camera.position)

        # Draw Aiming UI (Optimized trajectory)
        if self.dragging and self.drag_start_pos and self.current_mouse_pos:
            drag_handler.draw_drag_line(
                self.screen, self.drag_start_pos, self.current_mouse_pos, pygame.Color("red"), 2
            )
            angle_rad = math.radians(self.current_angle)
            initial_vel = pygame.Vector2(
                 self.current_force * math.cos(angle_rad),
                 self.current_force * math.sin(angle_rad)
            )
            physics_utils.draw_predicted_trajectory(
                 self.screen, self.ball.position, initial_vel, physics.GRAVITY,
                 physics.DEFAULT_DAMPING, PREDICTION_DT, PREDICTION_STEPS,
                 self.camera.position, PREDICTION_DOT_COLOR, PREDICTION_DOT_RADIUS,
                 PREDICTION_DOT_SPACING
            )

        # --- Draw Animated Stroke Counter ---
        current_scale = 1.0
        if self.stroke_count != self.previous_stroke_count:
            self.animate_stroke_timer = self.STROKE_ANIM_DURATION
        if self.animate_stroke_timer > 0:
            progress = self.animate_stroke_timer / self.STROKE_ANIM_DURATION
            current_scale = 1.0 + (self.STROKE_ANIM_SCALE - 1.0) * progress
            self.animate_stroke_timer -= 1
            if self.animate_stroke_timer == self.STROKE_ANIM_DURATION - 1:
                self.previous_stroke_count = self.stroke_count
        try:
            stroke_text = f"Strokes: {self.stroke_count}"
            text_surface_base = self.ui_font.render(stroke_text, True, self.STROKE_TEXT_COLOR)
            base_rect = text_surface_base.get_rect()
            if current_scale != 1.0:
                scaled_width = int(base_rect.width * current_scale)
                scaled_height = int(base_rect.height * current_scale)
                try: text_surface_final = pygame.transform.smoothscale(text_surface_base, (scaled_width, scaled_height))
                except ValueError: text_surface_final = pygame.transform.scale(text_surface_base, (scaled_width, scaled_height))
            else: text_surface_final = text_surface_base
            final_rect = text_surface_final.get_rect()
            bg_width = base_rect.width + self.STROKE_PADDING * 2
            bg_height = base_rect.height + self.STROKE_PADDING * 2
            bg_rect = pygame.Rect(0, 0, bg_width, bg_height)
            bg_rect.center = (self.width // 5, self.height // 5) # Position the background
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, self.STROKE_BG_COLOR, bg_surface.get_rect(), border_radius=self.STROKE_CORNER_RADIUS)
            self.screen.blit(bg_surface, bg_rect.topleft)
            final_rect.center = bg_rect.center # Center text in background
            self.screen.blit(text_surface_final, final_rect)
        except Exception as e:
            print(f"Error drawing stroke counter: {e}")
        # --- End Stroke Counter ---


    def run(self):
        """Main game loop for the Game scene."""
        self.running = True
        while self.running:
            try:
                self.dt = self.clock.tick(self.fps) / 1000.0
            except AttributeError:
                 print("Warning: Scene clock or fps not found, using fallback.")
                 self.dt = pygame.time.Clock().tick(60) / 1000.0

            self.dt = min(self.dt, 0.1) # Clamp dt

            self.handle_events()    # Process input
            self.update_physics()   # Update state (includes win check)
            self.draw()             # Render state

            pygame.display.flip()

        # print(f"Exiting {self.name} scene run loop.") # Optional debug
