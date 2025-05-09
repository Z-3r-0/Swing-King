from pygame import Vector2

from src.entities import Ball, Camera, Flag, Obstacle
from src.utils import *
import math
import json
import os
from datetime import datetime
from src.animation import Animation
from src.scene import Scene, SceneType
from src import physics


# --- Constants for trajectory prediction ---
PREDICTION_STEPS = 350 # How many steps to predict
PRECISION_NB_DOTS = 6 # Number of dots to draw
PREDICTION_DOT_SPACING = PREDICTION_STEPS//PRECISION_NB_DOTS # Draw a dot every N steps
PREDICTION_DOT_RADIUS = 5
PREDICTION_DOT_COLOR = (255, 0, 0, 150) # Semi-transparent white
PHYSICS_SUB_STEPS = 8 # Number of physics sub-steps per frame

class Game(Scene):
    def __init__(self, screen, levels_dir_path: str, scene_from: SceneType = None):  # Keep existing signature
        super().__init__(screen, SceneType.GAME, "Game", scene_from)
        # self.dt = 0 # dt will be updated in run loop or used as fixed 1/fps
        self.dragging = False
        # self.drag_done = False # Not used in the new logic
        # self.ball_in_motion = False # We will use self.ball.is_moving

        self.max_force = 1500  # User's existing value

        self.force = 0
        self.angle = 0

        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        # Physics sub-stepping variables
        self.physics_sub_steps = PHYSICS_SUB_STEPS
        # Assuming self.fps is defined in Scene or Game. If not, set a default e.g., 60
        target_fps = getattr(self, 'fps', 60)
        if target_fps <= 0: target_fps = 60  # Ensure FPS is positive
        self.fixed_dt = 1.0 / (target_fps * self.physics_sub_steps)
        self.physics_accumulator = 0.0

        # Game state for anti-stuck mechanism (managed by Game instance)
        self.physics_last_collided_object_id = None
        self.physics_collision_toggle_count = 0
        self.max_toggle_toggles = 4#is already defined by user as 4, we'll use that

        self.level_dir = levels_dir_path
        self.level_path = f"{self.level_dir}/level1.json"  # default level

        # Load level data
        self.terrain_data, self.obstacles_data = level_loader.load_json_level(self.level_path)

        BALL_START_X, BALL_START_Y = 0, 0  # Default start position
        self.ball = Ball(pygame.Vector2(BALL_START_X, BALL_START_Y), 4.2, 0.047, pygame.Color("white"),
                         "assets/images/balls/golf_ball.png")
        # Ensure ball.is_moving exists and is False initially
        self.ball.is_moving = False

        self.terrain_polys = level_loader.json_to_list(self.terrain_data, self.screen, 0)
        self.obstacles = level_loader.json_to_list(self.obstacles_data, self.screen, 1)
        # self.potential_collision_indices = [] # Not used in new logic
        # self.potential_collision_polygons = [] # Not used in new logic

        # ... (rest of your __init__ method, including WORLD boundary calculations, camera, background) ...
        # Make sure self.dt is correctly representing frame time.
        # If self.dt is fixed (1/self.fps), the accumulator will use that.
        # If self.clock.tick() is used in run() to get variable dt, that's better.
        # For now, assuming self.dt = 1 / self.fps as per user's current code.
        # This self.dt is used for the accumulator.
        if not hasattr(self, 'dt') or self.dt == 0:  # If dt wasn't set or is 0 from Scene
            self.dt = 1.0 / target_fps

        # Ensure these are initialized as they are used in the original handle_events
        self.prev_collision_terrain = None  # Will be replaced by physics_last_collided_object_id
        # self.collision_toggle_count = 0 # Replaced by physics_collision_toggle_count
        # self.max_toggle_toggles = 4 # This will be passed to physics

        # --- Compteur et Police ---
        self.stroke_count = 0
        try:
            self.ui_font = pygame.font.SysFont('Arial', 30)
        except:
            self.ui_font = pygame.font.Font(None, 36)
        self.previous_stroke_count = -1
        self.animate_stroke_timer = 0
        self.STROKE_ANIM_DURATION = 10
        self.STROKE_ANIM_SCALE = 1.1
        self.STROKE_TEXT_COLOR = (220, 70, 70)
        self.STROKE_BG_COLOR = (40, 40, 40, 180)
        self.STROKE_PADDING = 8
        self.STROKE_CORNER_RADIUS = 5

        # Camera and background (ensure these are after width/height and level boundaries)
        # Calculation of level limitations:
        WORLD_MIN_X_BOUNDARY = self.terrain_polys[0].points[0][0] if self.terrain_polys else 0
        WORLD_MAX_X_BOUNDARY = self.terrain_polys[0].points[0][0] if self.terrain_polys else self.width
        WORLD_MIN_Y_BOUNDARY = self.terrain_polys[0].points[0][1] if self.terrain_polys else 0  # Corrected index
        WORLD_MAX_Y_BOUNDARY = self.terrain_polys[0].points[0][
            1] if self.terrain_polys else self.height  # Corrected index

        for terrain in self.terrain_polys:
            for point_tuple in terrain.points:  # Iterate through point tuples
                point = pygame.Vector2(point_tuple)  # Convert to Vector2 for consistency
                if point.x < WORLD_MIN_X_BOUNDARY:
                    WORLD_MIN_X_BOUNDARY = point.x
                if point.x > WORLD_MAX_X_BOUNDARY:
                    WORLD_MAX_X_BOUNDARY = point.x
                if point.y < WORLD_MIN_Y_BOUNDARY:
                    WORLD_MIN_Y_BOUNDARY = point.y
                if point.y > WORLD_MAX_Y_BOUNDARY:
                    WORLD_MAX_Y_BOUNDARY = point.y
        WORLD_MIN_Y_BOUNDARY = WORLD_MIN_Y_BOUNDARY - self.height  # User's original logic

        self.camera = Camera(pygame.Vector2(0, 0), self.width, self.height, level_max_width=WORLD_MAX_X_BOUNDARY,
                             level_max_height=WORLD_MAX_Y_BOUNDARY, level_min_x=WORLD_MIN_X_BOUNDARY,
                             level_min_y=WORLD_MIN_Y_BOUNDARY)
        self.background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
        self.background = pygame.transform.smoothscale(self.background, (self.width, self.height))

        self.dot_spacing = 10
        self.dot_radius = 2
        self.dot_color = (255, 0, 0)

        self.flag = None
        self.isflag = False  # Redundant if self.flag is None or set
        for obstacle in self.obstacles:
            if not isinstance(obstacle, Flag) and getattr(obstacle, 'characteristic', None) == "start":
                self.ball.position = obstacle.position.copy()  # Ensure it's a copy
                self.ball.start_position = obstacle.position.copy()
            if isinstance(obstacle, Flag):  # Removed "and not self.isflag" as it's not needed
                self.flag = obstacle
                # self.isflag = True # Not strictly needed if self.flag is the source of truth
        self.saved = False
        self.camera.calculate_position(self.ball.position)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        camera_offset = self.camera.position

        for poly in self.terrain_polys:
            screen_points = [(p[0] - camera_offset.x, p[1] - camera_offset.y) for p in poly.points]
            poly.draw_polygon(self.screen, screen_points)

        for obs in self.obstacles:
            if not (isinstance(obs, Flag)) and obs.characteristic == "start":
                continue
            obs.draw(self.screen, camera_offset)

        self.ball.draw(self.screen, camera_offset)

        if self.dragging:
            current_mouse_screen_pos = pygame.mouse.get_pos()

            ball_screen_pos = self.ball.position - camera_offset

            pygame.draw.line(self.screen, pygame.Color("red"), ball_screen_pos, current_mouse_screen_pos, 2)
            ball_screen_pos = self.ball.position - camera_offset
            pygame.draw.line(self.screen, pygame.Color("red"), ball_screen_pos, current_mouse_screen_pos, 2)
            preview_vel_x = -self.force * math.cos(math.radians(self.angle))
            preview_vel_y = self.force * math.sin(math.radians(self.angle))  # Or -self.force * sin if math angle
            initial_vel_for_prediction = pygame.Vector2(preview_vel_x, preview_vel_y)
            draw_predicted_trajectory(self.screen,self.ball.position,initial_vel_for_prediction,physics.GRAVITY_ACCELERATION,physics.DEFAULT_DAMPING_FACTOR,self.fixed_dt,PREDICTION_STEPS,self.camera.position,PREDICTION_DOT_COLOR,PREDICTION_DOT_RADIUS,PREDICTION_DOT_SPACING)

        # --- AFFICHAGE AMÉLIORÉ DU COMPTEUR (CENTERED at width/5, height/5) ---
        current_scale = 1.0
        # Détecte si le compteur a changé pour lancer l'animation
        if self.stroke_count != self.previous_stroke_count:
            self.animate_stroke_timer = self.STROKE_ANIM_DURATION
            # On met à jour previous_stroke_count seulement *après* avoir dessiné une frame animée

        # Gère l'animation si le timer est actif
        if self.animate_stroke_timer > 0:
            # Calcule la progression (de 1 à 0)
            progress = self.animate_stroke_timer / self.STROKE_ANIM_DURATION
            # Calcule l'échelle (de MAX_SCALE à 1.0)
            current_scale = 1.0 + (self.STROKE_ANIM_SCALE - 1.0) * progress
            self.animate_stroke_timer -= 1  # Décrémente le timer

            # Met à jour la valeur précédente une fois l'animation démarrée
            if self.animate_stroke_timer == self.STROKE_ANIM_DURATION - 1:
                self.previous_stroke_count = self.stroke_count

        try:
            # 1. Rendre le texte de base (non-agrandi) pour calculer la taille
            stroke_text = f"Strokes: {self.stroke_count}"
            text_surface_base = self.ui_font.render(stroke_text, True, self.STROKE_TEXT_COLOR)
            base_rect = text_surface_base.get_rect()  # Taille de base du texte

            # 2. Préparer la surface finale (potentiellement agrandie)
            if current_scale != 1.0:
                scaled_width = int(base_rect.width * current_scale)
                scaled_height = int(base_rect.height * current_scale)
                # Utilise smoothscale ou scale
                try:
                    text_surface_final = pygame.transform.smoothscale(text_surface_base,
                                                                      (scaled_width, scaled_height))
                except ValueError:
                    text_surface_final = pygame.transform.scale(text_surface_base, (scaled_width, scaled_height))
            else:
                text_surface_final = text_surface_base
            final_rect = text_surface_final.get_rect()  # Rectangle du texte qui sera affiché

            # 3. Calculer la taille du rectangle de fond (basé sur texte de BASE + padding)
            bg_width = base_rect.width + self.STROKE_PADDING * 2
            bg_height = base_rect.height + self.STROKE_PADDING * 2

            # 4. CRÉER et POSITIONNER le rectangle de FOND
            #   Crée le Rect avec la bonne taille, mais positionné à (0,0) au début
            bg_rect = pygame.Rect(0, 0, bg_width, bg_height)
            #   MAINTENANT, ajuste son CENTRE à la position voulue
            bg_rect.center = (self.width // 5, self.height // 5)  # <--- TA LOGIQUE DE POSITIONNEMENT

            # 5. Dessiner le fond (avec transparence et coins arrondis)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, self.STROKE_BG_COLOR, bg_surface.get_rect(),
                             border_radius=self.STROKE_CORNER_RADIUS)
            #   Blit le fond à sa position calculée (bg_rect.topleft)
            self.screen.blit(bg_surface, bg_rect.topleft)

            # 6. Centrer le texte (potentiellement agrandi) DANS le fond (qui est maintenant bien positionné)
            final_rect.center = bg_rect.center
            #   Blit le texte
            self.screen.blit(text_surface_final, final_rect)

        except Exception as e:
            print(f"Erreur lors de l'affichage du compteur animé : {e}")

    def handle_events(self):
        """
        Handle input, ball movement, gravity, collisions with bounce/slide,
        hole detection, flat-surface slide, prevent infinite toggling.
        Allows multiple drag-and-release actions.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # self.running = False # Assuming Scene's run loop handles this
                pygame.quit()  # Or post a quit event: pygame.event.post(pygame.event.Event(pygame.QUIT))
                exit()  # Or sys.exit()

            # --- Input Handling for Dragging and Shooting ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left-click
                if not self.ball.is_moving:  # Only allow drag if ball is stationary
                    mouse_screen_pos = pygame.Vector2(event.pos)
                    # Convert ball world position to screen position for distance check
                    ball_screen_pos = self.ball.position - self.camera.position

                    # Use ball's visual radius for click detection
                    clickable_radius = self.ball.radius * self.ball.scale_value
                    if mouse_screen_pos.distance_to(
                            ball_screen_pos) <= clickable_radius * 1.5:  # x1.5 for easier clicking
                        self.dragging = True
                        # drag_start_pos is ball's world position, not screen position
                        self.drag_start_pos = self.ball.position.copy()
                        # self.current_mouse_pos = mouse_screen_pos # For trajectory preview if needed

            if event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    # self.current_mouse_pos = pygame.Vector2(event.pos) # For trajectory preview
                    # Calculate force/angle for trajectory preview if you implement it
                    # For now, just update based on release
                    pass

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left-click release
                if self.dragging:
                    self.dragging = False
                    mouse_screen_pos = pygame.mouse.get_pos()
                    # Convert release position to world coordinates for angle/force calc
                    # drag_and_release expects world positions or consistent coordinate space
                    # Assuming drag_and_release uses the delta between drag_start_pos (world)
                    # and current mouse_world_pos.
                    current_mouse_world_pos = pygame.Vector2(mouse_screen_pos) + self.camera.position

                    # Your drag_and_release function calculates force and angle
                    # Ensure it handles the coordinate systems correctly.
                    # The original code used self.drag_start_pos (world) and mouse_world_pos
                    self.force, self.angle = drag_and_release(self.drag_start_pos, current_mouse_world_pos)

                    # Limit force if necessary
                    self.force = min(self.force, self.max_force)

                    # Apply shot if force is significant (optional min_force check)
                    MIN_SHOT_FORCE = 50
                    if self.force >= MIN_SHOT_FORCE:
                        # Apply velocity based on force and angle
                        # This matches your original code's velocity assignment
                        vel_x = -self.force * math.cos(math.radians(self.angle))
                        vel_y = self.force * math.sin(math.radians(self.angle))
                        self.ball.velocity = pygame.Vector2(vel_x, vel_y)

                        self.ball.is_moving = True
                        self.stroke_count += 1
                        # Reset anti-stuck for new shot
                        self.physics_last_collided_object_id = None
                        self.physics_collision_toggle_count = 0
                    # Reset drag state
                    self.drag_start_pos = None
                    self.force = 0
                    self.angle = 0

        # --- Physics Update Loop (replaces the old collision block) ---
        if self.ball.is_moving:
            # self.dt is the time for the current frame (e.g., 1/60.0 or variable)
            self.physics_accumulator += self.dt

            # Limit max steps per frame to prevent spiral of death if dt is too large
            max_sub_steps_per_frame = self.physics_sub_steps * 2
            sub_steps_this_frame = 0

            while self.physics_accumulator >= self.fixed_dt and sub_steps_this_frame < max_sub_steps_per_frame:
                if self.ball.is_moving:  # Double check inside loop
                    # Filter obstacles that are collidable
                    collidable_obstacles_list = [obs for obs in self.obstacles if (not isinstance(obs, Flag)) and obs.is_colliding]

                    still_moving = physics.update_ball_physics(
                        self.ball,
                        self.terrain_polys,
                        collidable_obstacles_list,
                        self.fixed_dt,
                        self  # Pass the game instance for anti-stuck state
                    )

                    if not still_moving:
                        self.ball.is_moving = False  # Ball has stopped
                        self.physics_accumulator = 0  # Clear accumulator
                        # Check win condition AFTER ball stops and physics is fully resolved
                        if self.check_flag_collision():  # check_flag_collision should verify ball is NOT moving
                            level_id = int(self.level_path.split("/")[-1].split(".json")[0].split("level")[-1])
                            if not self.saved:
                                self.save_level_stats(level_id)
                                self.saved = True
                                # self.__init__(self.screen, self.level_dir, self.scene_from) # This reinitializes, be careful
                                self.switch_scene(SceneType.LEVEL_SELECTOR)  # More common to switch scene
                        break  # Exit sub-step loop
                else:
                    # Ball stopped during a sub-step sequence (e.g. by anti-stuck)
                    self.physics_accumulator = 0
                    break  # Exit sub-step loop

                self.physics_accumulator -= self.fixed_dt
                sub_steps_this_frame += 1
        # --- End of Physics Update Loop ---

        # Update camera position based on ball (if ball moved or dragging for preview)
        # The original code had camera update outside the ball_in_motion check.
        # This is fine, camera can follow even if ball is stationary but was just placed.
        if self.ball.is_moving or self.dragging:  # Or always update if you want smooth pan to stationary ball
            self.camera.calculate_position(self.ball.position)

        # The win condition check was here in original code, moved to after ball stops in physics loop.
        # if self.check_flag_collision(): ...

        # Update drag line preview if dragging (this part is mostly for drawing, but related to input state)
        if self.dragging and self.drag_start_pos:  # drag_start_pos is world
            current_mouse_screen_pos = pygame.mouse.get_pos()
            current_mouse_world_pos = pygame.Vector2(current_mouse_screen_pos) + self.camera.position
            # Recalculate force/angle for preview if needed by draw_predicted_trajectory
            self.force, self.angle = drag_and_release(self.drag_start_pos, current_mouse_world_pos)
            self.force = min(self.force, self.max_force)


    def save_level_stats(self, level_id: int):
        """
            Saves the stats of the finished level in a JSON file.

            :param: level_id : ID of the finished level
        """

        # Create data directory if it does not exist 
        stats_dir = "data/stats"
        os.makedirs(stats_dir, exist_ok=True)

        stats_file = f"{stats_dir}/level_{level_id}_stats.json"

        # Data to save
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_data = {
            "date": current_time,
            "strokes": self.stroke_count
        }

        # Load the existing values if there are
        existing_data = []
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as file:
                    existing_data = json.load(file)

                if not isinstance(existing_data, list):
                    existing_data = []
            except (json.JSONDecodeError, FileNotFoundError):
                existing_data = []

        existing_data.append(new_data)

        # Save data
        with open(stats_file, 'w') as file:
            json.dump(existing_data, file, indent=4)

        print(f"Statistiques du niveau {level_id} enregistrées : {new_data}")

    def run(self):

        super().run()

        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.fps)



    # @Julien à quoi sert cette fonction??
    def load_level(self, id: int):

        self.level_path = f"{self.level_dir}/level{id}.json"

        # Load level data
        self.terrain_data, self.obstacles_data = level_loader.load_json_level(self.level_path)

        # Load terrain and obstacles
        self.terrain_polys = level_loader.json_to_list(self.terrain_data, self.screen, 0)
        self.obstacles = level_loader.json_to_list(self.obstacles_data, self.screen, 1)
        self.potential_collision_indices = []
        self.potential_collision_polygons = []

        for obstacle in self.obstacles:
            if not isinstance(obstacle, Flag) and obstacle.characteristic == "start":
                self.ball.position = obstacle.position
            if isinstance(obstacle, Flag):
                self.flag = obstacle
                break

        self.saved = False

    def check_flag_collision(self):
        """
        Checks if the ball reached the base of the flag (hole)
        """

        if not self.flag or self.ball.is_moving: # <--- CORRECTED THIS LINE
            return False

        ball_mask = self.ball.mask

        flag_surface = self.flag.animation.image
        flag_mask = pygame.mask.from_surface(flag_surface)

        # Create a mask for the base of the flag only (1/4 bottom of the flag)
        base_height = flag_surface.get_height() // 4
        base_rect = pygame.Rect(0, flag_surface.get_height() - base_height,
                                flag_surface.get_width(), base_height)

        base_mask = pygame.mask.Mask((flag_surface.get_width(), flag_surface.get_height()))
        for x in range(base_rect.width):
            for y in range(base_rect.height):
                if flag_mask.get_at((x, base_rect.y + y)):
                    base_mask.set_at((x, base_rect.y + y), 1)

        offset = (
            int(self.ball.rect.left - self.flag.animation.rect.left),
            int(self.ball.rect.top - self.flag.animation.rect.top)
        )

        # Check if masks overlap with the offset
        overlap = base_mask.overlap(ball_mask, offset)

        return overlap is not None