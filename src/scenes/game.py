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


GRAVITY = 980  # Gravitational acceleration in pixels/s²


class Game(Scene):
    def __init__(self, screen, levels_dir_path: str, scene_from: SceneType = None):
        super().__init__(screen, SceneType.GAME, "Game", scene_from)
        self.dt = 0
        self.dragging = False
        self.drag_done = False
        self.ball_in_motion = False

        self.max_force = 1500

        self.force = 0
        self.angle = 0



        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        self.level_dir = levels_dir_path

        self.level_path = f"{self.level_dir}/level1.json"  # default level

        # Load level data
        self.terrain_data, self.obstacles_data = level_loader.load_json_level(self.level_path)

        BALL_START_X, BALL_START_Y = 0, 0  # Default start position
        # Initialize game objects
        self.ball = Ball(pygame.Vector2(BALL_START_X, BALL_START_Y), 4.2, 0.047, pygame.Color("white"),
                         "assets/images/balls/golf_ball.png")

        # Load terrain and obstacles
        self.terrain_polys = level_loader.json_to_list(self.terrain_data, self.screen, 0)
        self.obstacles = level_loader.json_to_list(self.obstacles_data, self.screen, 1)
        self.potential_collision_indices = []
        self.potential_collision_polygons = []


        # Calculation of level limitations:
        WORLD_MIN_X_BOUNDARY = self.terrain_polys[0].points[0][0]
        WORLD_MAX_X_BOUNDARY = self.terrain_polys[0].points[0][0]
        WORLD_MIN_Y_BOUNDARY = self.terrain_polys[0].points[0][0]
        WORLD_MAX_Y_BOUNDARY = self.terrain_polys[0].points[0][1]

        for terrain in self.terrain_polys:
            for point in terrain.points:
                if point[0] < WORLD_MIN_X_BOUNDARY:
                    WORLD_MIN_X_BOUNDARY = point[0]
                if point[0] > WORLD_MAX_X_BOUNDARY:
                    WORLD_MAX_X_BOUNDARY = point[0]
                if point[1] < WORLD_MIN_Y_BOUNDARY:
                    WORLD_MIN_Y_BOUNDARY = point[1]
                if point[1] > WORLD_MAX_Y_BOUNDARY:
                    WORLD_MAX_Y_BOUNDARY = point[1]
        WORLD_MIN_Y_BOUNDARY = WORLD_MIN_Y_BOUNDARY - self.height


        self.prev_collision_terrain = None
        self.collision_toggle_count = 0
        self.max_toggle_toggles = 4  # maximum alternations allowed before stopping

        # --- Compteur et Police (Minimum Requis) ---
        self.stroke_count = 0
        try:
            # Gardons une taille et police simples pour l'instant
            self.ui_font = pygame.font.SysFont('Arial', 30)
        except:
            self.ui_font = pygame.font.Font(None, 36)
        # On a besoin de ça pour l'animation simple :
        self.previous_stroke_count = -1

        # region Stroke counter animation
        self.previous_stroke_count = -1
        self.animate_stroke_timer = 0
        self.STROKE_ANIM_DURATION = 10
        self.STROKE_ANIM_SCALE = 1.1
        self.STROKE_TEXT_COLOR = (220, 70, 70)
        self.STROKE_BG_COLOR = (40, 40, 40, 180)
        self.STROKE_PADDING = 8
        self.STROKE_CORNER_RADIUS = 5
        # endregion

        # Initialize camera
        self.camera = Camera(pygame.Vector2(0, 0), self.width, self.height,level_max_width=WORLD_MAX_X_BOUNDARY,level_max_height=WORLD_MAX_Y_BOUNDARY,level_min_x=WORLD_MIN_X_BOUNDARY,level_min_y=WORLD_MIN_Y_BOUNDARY)

        # Load background
        self.background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
        self.background = pygame.transform.smoothscale(self.background, (self.width, self.height))

        self.dt = 1 / self.fps

        # Set up the dot parameters
        self.dot_spacing = 10
        self.dot_radius = 2
        self.dot_color = (255, 0, 0)

        self.flag = None
        self.isflag = False
        for obstacle in self.obstacles:
            if not isinstance(obstacle, Flag) and obstacle.characteristic == "start":
                self.ball.position = obstacle.position
            if isinstance(obstacle, Flag) and not self.isflag:
                self.flag = obstacle
                self.isflag = True
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
            draw_predicted_trajectory(ball_screen_pos, self.force, self.angle, GRAVITY, self.fps, self.screen)

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
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.ball_in_motion:
                    mouse_screen_pos = pygame.Vector2(event.pos)
                    mouse_world_pos = mouse_screen_pos + self.camera.position

                    click_dist = mouse_world_pos.distance_to(self.ball.position)

                    clickable_radius = self.ball.radius * self.ball.scale_value
                    if click_dist <= clickable_radius:
                        self.dragging = True
                        self.drag_start_pos = self.ball.position.copy()

            if event.type == pygame.MOUSEBUTTONUP and self.dragging:
                mouse_screen_pos = pygame.mouse.get_pos()
                mouse_world_pos = pygame.Vector2(mouse_screen_pos) + self.camera.position

                self.force, self.angle = drag_and_release(self.drag_start_pos,mouse_world_pos)

                self.ball.velocity = pygame.Vector2(-self.force * math.cos(math.radians(self.angle)),self.force * math.sin(math.radians(self.angle)))

                self.stroke_count += 1
                self.dragging = False
                self.ball_in_motion = True
        #region Ball movement and collision detection
        if self.ball_in_motion:

            self.ball.position += self.ball.velocity * self.dt
            self.ball.rect.center = self.ball.position

            self.ball.velocity.y += GRAVITY * self.dt
            self.ball.velocity *= 0.98

            possible_collisions = []
            collisions = []

            for terrain in self.terrain_polys:
                mask_off = (
                    self.ball.rect.left - terrain.rect.left,
                    self.ball.rect.top - terrain.rect.top
                )
                overlap = terrain.mask.overlap(self.ball.mask, mask_off)
                if not overlap:
                    continue
                gx = terrain.rect.left + overlap[0]
                gy = terrain.rect.top + overlap[1]
                rad_px = self.ball.radius * self.ball.scale_value
                normal, depth = physics.get_collision_normal_and_depth(
                    terrain.points, (gx, gy), self.ball.position, rad_px
                )
                if normal and depth > 0:
                    collisions.append((terrain, normal, depth))

            if len(collisions) >= 2:
                self.ball.velocity = pygame.Vector2(0, 0)
                self.ball_in_motion = False
                return

            elif len(collisions) == 1:
                terrain, normal, depth = collisions[0]

                self.ball.position += normal * depth
                self.ball.rect.center = self.ball.position

                vel = self.ball.velocity
                tangent = pygame.Vector2(-normal.y, normal.x)
                vn = vel.dot(normal)
                vt = vel.dot(tangent)
                rest = terrain.bounce_factor
                fric = terrain.friction
                if abs(normal.x) < 0.2 and normal.y < 0:
                    new_vn = 0
                else:
                    new_vn = -vn * rest
                new_vt = vt * (1 - fric)
                MICRO = 2.0
                if abs(new_vn) < MICRO:
                    self.ball.velocity = new_vt * tangent
                else:
                    self.ball.velocity = new_vn * normal + new_vt * tangent
                current_terrain_id = id(terrain)
                if self.prev_collision_terrain is not None and current_terrain_id != self.prev_collision_terrain:
                    self.collision_toggle_count += 1
                self.prev_collision_terrain = current_terrain_id
                if self.collision_toggle_count >= self.max_toggle_toggles:
                    self.ball.velocity = pygame.Vector2(0, 0)
                    self.ball_in_motion = False
                    return

                STOP_S = 5.0
                if self.ball.velocity.length_squared() < STOP_S ** 2:
                    self.ball.velocity = pygame.Vector2(0, 0)
                    self.ball_in_motion = False
            else:
                self.prev_collision_terrain = None
                self.collision_toggle_count = 0
        #endregion
        if self.dragging:
            mouse_screen_pos = pygame.mouse.get_pos()
            mouse_world_pos = pygame.Vector2(mouse_screen_pos) + self.camera.position
            self.force, self.angle = drag_and_release(self.drag_start_pos, mouse_world_pos)

        if self.check_flag_collision():
            level_id = int(self.level_path.split("/")[-1].split(".json")[0].split("level")[-1])
            if not self.saved:
                self.save_level_stats(level_id)
                self.saved = True
                self.__init__(self.screen, self.level_dir, self.scene_from)
                self.switch_scene(SceneType.LEVEL_SELECTOR)

        self.camera.calculate_position(self.ball.position)

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

        if not self.flag or not self.ball_in_motion:
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