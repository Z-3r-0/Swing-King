from src.entities import Ball, Camera
from src.utils import *
import math
from src.animation import Animation
from src.scene import Scene
from src.scenetype import SceneType
from src import physics

BALL_START_X, BALL_START_Y = 800, 500 # TODO - REPLACE WITH LEVEL DATA LATER
SCENE_WIDTH, SCENE_HEIGHT = 10000, 2000 # TODO - REPLACE WITH LEVEL DATA LATER
GRAVITY = 980  # Gravitational acceleration in pixels/s² # TODO - REPLACE WITH LEVEL DATA LATER
BALL_RADIUS = 50.0

# TODO - INSERT IN THE CLASS LATER

class Game(Scene):
    def __init__(self, screen, scene_from: SceneType = None):
        super().__init__(screen, SceneType.GAME, "Game", scene_from)
        self.dt = 0
        self.dragging = False
        self.drag_done = False
        self.ball_in_motion = False

        self.max_force = 500

        self.force = 0
        self.angle = 0

        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        self.level_path = "data/levels/test_level.json"

        # Load level data
        self.terrain_data, self.obstacles_data = level_loader.load_json_level(self.level_path)

        # Initialize game objects
        self.ball = Ball(pygame.Vector2(BALL_START_X, BALL_START_Y), 4.2, 0.047, pygame.Color("white"),
                 "assets/images/balls/golf_ball.png")

        # Load terrain and obstacles
        self.terrain_polys = level_loader.json_to_list(self.terrain_data, self.screen, 0)
        self.obstacles = level_loader.json_to_list(self.obstacles_data, self.screen, 1)
        self.potential_collision_indices = []
        self.potential_collision_polygons = []

        self.prev_collision_terrain = None
        self.collision_toggle_count = 0
        self.max_toggle_toggles = 4 # maximum alternations allowed before stopping

        # --- Compteur et Police (Minimum Requis) ---
        self.stroke_count = 0
        try:
            # Gardons une taille et police simples pour l'instant
            self.ui_font = pygame.font.SysFont('Arial', 30)
        except:
            self.ui_font = pygame.font.Font(None, 36)
        # On a besoin de ça pour l'animation simple :
        self.previous_stroke_count = -1
        # --- Variables pour Animation/Style ---
        self.previous_stroke_count = -1
        self.animate_stroke_timer = 0
        self.STROKE_ANIM_DURATION = 10
        self.STROKE_ANIM_SCALE = 1.1
        self.STROKE_TEXT_COLOR = (220, 70, 70)
        self.STROKE_BG_COLOR = (40, 40, 40, 180)
        self.STROKE_PADDING = 8
        self.STROKE_CORNER_RADIUS = 5
        # --- Fin Compteur/Police ---


        # Initialize camera
        self.camera = Camera(pygame.Vector2(0, 0), self.width, self.height, SCENE_WIDTH, SCENE_HEIGHT)

        # Load background
        self.background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
        self.background = pygame.transform.smoothscale(self.background, (self.width, self.height))

        self.dt = 1 / self.fps

        # Set up the dot parameters
        self.dot_spacing = 10
        self.dot_radius = 2
        self.dot_color = (255, 0, 0)


        # Animation du golfer
        # self.golfer_animation = Animation("assets/images/golfer", pygame.Vector2(500, 500))
        # self.golfer_animation_sprite = pygame.sprite.Group()
        # self.golfer_animation_sprite.add(self.golfer_animation)

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for poly in self.terrain_polys:
            poly.draw_polygon(self.screen)

        for obs in self.obstacles:
            obs.draw_obstacle(self.screen)

        self.ball.draw(self.screen)



        # Toujours l'anim du golfeur
        # self.golfer_animation_sprite.draw(self.screen)
        # self.golfer_animation_sprite.update()


        # Draw the trajectory
        if self.dragging:
            current_mouse = pygame.mouse.get_pos()

            pygame.draw.line(self.screen, pygame.Color("red"), self.ball.position, current_mouse, 2)
            draw_predicted_trajectory(self.ball.position, self.force, self.angle, GRAVITY, self.fps, self.screen)
            # DANS src/scenes/game.py -> MÉTHODE draw
            # REMPLACE ton bloc try/except actuel par celui-ci :

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
        # --- FIN AFFICHAGE AMÉLIORÉ ---

        # La méthode handle_events suit après...

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
                # --- CONDITION MODIFIÉE ---
                # Permet de commencer à viser SEULEMENT si la balle ne bouge pas
                if not self.ball_in_motion:
                    click_dist = pygame.Vector2(event.pos).distance_to(self.ball.position)

                    clickable_radius = self.ball.radius * self.ball.scale_value
                    if click_dist <= clickable_radius:
                    # --- FIN CONDITION MODIFIÉE ---
                        self.dragging = True

                        self.drag_start_pos = self.ball.position.copy()

            if event.type == pygame.MOUSEBUTTONUP and self.dragging:

                self.force, self.angle = drag_and_release(
                    self.drag_start_pos,
                    pygame.mouse.get_pos()
                )
                self.ball.velocity = pygame.Vector2(
                    -self.force * math.cos(math.radians(self.angle)),
                    self.force * math.sin(math.radians(self.angle))
                )

                # Incrémente le compteur
                self.stroke_count += 1

                # Met à jour les états
                self.dragging = False
                self.ball_in_motion = True



        if self.ball_in_motion:
            # 1) Movement + gravity + damping
            self.ball.shift_position(self.ball.velocity * self.dt)
            self.ball.velocity.y += GRAVITY * self.dt
            self.ball.velocity *= 0.98

            # 2) Gather collisions
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

            # 3) Hole detection: simultaneous faces (Arrête la balle)
            if len(collisions) >= 2:
                self.ball.velocity = pygame.Vector2(0, 0)
                self.ball_in_motion = False

                return

            # 4) Single collision: bounce/slide
            elif len(collisions) == 1: # Utilise elif si tu avais un return au-dessus
                terrain, normal, depth = collisions[0]
                # 4a) resolve penetration
                self.ball.shift_position(normal * depth)
                # 4b) decompose velocity
                vel = self.ball.velocity
                tangent = pygame.Vector2(-normal.y, normal.x)
                vn = vel.dot(normal)
                vt = vel.dot(tangent)
                # 4c) get coefficients
                rest = terrain.bounce_factor
                fric = terrain.friction
                # 4d) slide on flat surfaces
                if abs(normal.x) < 0.2 and normal.y < 0:
                    new_vn = 0
                else:
                    new_vn = -vn * rest
                new_vt = vt * (1 - fric)
                # 4e) micro-bounce
                MICRO = 2.0
                if abs(new_vn) < MICRO:
                    self.ball.velocity = new_vt * tangent
                else:
                    self.ball.velocity = new_vn * normal + new_vt * tangent
                # 4f) toggle detection
                current_terrain_id = id(terrain)
                if self.prev_collision_terrain is not None and current_terrain_id != self.prev_collision_terrain:
                    self.collision_toggle_count += 1
                self.prev_collision_terrain = current_terrain_id
                if self.collision_toggle_count >= self.max_toggle_toggles:
                    self.ball.velocity = pygame.Vector2(0, 0)
                    self.ball_in_motion = False

                    return

                # 4g) stop if slow (Arrête la balle)
                STOP_S = 5.0
                if self.ball.velocity.length() < STOP_S: # Tu peux utiliser length_squared() pour optimiser
                    self.ball.velocity = pygame.Vector2(0, 0)
                    self.ball_in_motion = False

            else: # Pas de collision
                # reset toggle counter if no collision
                self.prev_collision_terrain = None
                self.collision_toggle_count = 0

        # 5) draw aim line (Calcul pour la prédiction visuelle)
        if self.dragging:
            mpos = pygame.mouse.get_pos()
            # Recalcule force/angle pour la prédiction pendant le drag
            self.force, self.angle = drag_and_release(self.drag_start_pos, mpos)


    def run(self):
        while True:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.fps)