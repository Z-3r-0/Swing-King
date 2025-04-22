from src.entities import Ball, Camera
from src.utils import *
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
        print(self.terrain_polys)
        self.obstacles = level_loader.json_to_list(self.obstacles_data, self.screen, 1)
        self.potential_collision_indices = []
        self.potential_collision_polygons = []

        # Initialize camera
        self.camera = Camera(pygame.Vector2(0, 0), self.width, self.height, SCENE_WIDTH, SCENE_HEIGHT)

        # Load background
        self.background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
        self.background = pygame.transform.smoothscale(self.background, (self.width, self.height))

        # Set up the clock
        self.clock = pygame.time.Clock()

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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if (not self.drag_done
                        and pygame.Vector2(event.pos).distance_to(self.ball.position) <= BALL_RADIUS):
                    self.dragging = True

            if event.type == pygame.MOUSEBUTTONUP and self.dragging:
                if not self.drag_done:
                    self.force, self.angle = drag_and_release(
                        self.ball.position, pygame.mouse.get_pos()
                    )
                    self.ball.velocity = pygame.Vector2(
                        -self.force * math.cos(math.radians(self.angle)),
                        self.force * math.sin(math.radians(self.angle))
                    )
                    self.dragging = False
                    self.ball_in_motion = True
                    self.drag_done = True

        if self.ball_in_motion:
            # 1) Mouvement + gravité + friction globale
            self.ball.shift_position(self.ball.velocity * self.dt)
            self.ball.velocity.y += GRAVITY * self.dt
            self.ball.velocity *= 0.98

            # 2) Collecte des collisions potentielles
            collisions = []
            for poly in self.terrain_polys:
                off = (self.ball.rect.left - poly.rect.left,
                       self.ball.rect.top - poly.rect.top)
                pt = poly.mask.overlap(self.ball.mask, off)
                if not pt:
                    continue

                px, py = poly.rect.left + pt[0], poly.rect.top + pt[1]
                ball_r = self.ball.radius * self.ball.scale_value
                normal, depth = physics.get_collision_normal_and_depth(
                    poly.points, (px, py), self.ball.position, ball_r
                )
                if normal and depth > 0:
                    collisions.append((poly, normal, depth))

            # 3) Si on touche plusieurs faces, c'est probablement un trou → on arrête net
            if len(collisions) >= 2:
                self.ball.velocity = pygame.Vector2(0, 0)
                self.ball_in_motion = False
                self.drag_done = False
                return

            # 4) S'il y a exactement une collision, on gère le rebond/glissement
            if len(collisions) == 1:
                poly, normal, depth = collisions[0]

                # 4a) Recalage précis
                self.ball.shift_position(normal * depth)

                # 4b) Décomposition de la vélocité
                v = self.ball.velocity
                t = pygame.Vector2(-normal.y, normal.x)
                v_n, v_t = v.dot(normal), v.dot(t)

                # 4c) Récupération des coefficients (vous avez dit que vous avez modifié)
                rest = poly.bounce_factor
                fric = poly.friction

                # 4d) Calcul du nouveau vecteur vitesse
                v_n_after = -v_n * rest
                v_t_after = v_t * (1 - fric)

                # 4e) Micro‑rebond minimal pour laisser un léger slide
                MICRO_BOUNCE = 2.0
                if abs(v_n_after) < MICRO_BOUNCE:
                    self.ball.velocity = v_t_after * t
                else:
                    self.ball.velocity = v_n_after * normal + v_t_after * t

                # 4f) Arrêt si très lent après rebond
                STOP_THRESHOLD = 5.0
                if self.ball.velocity.length() < STOP_THRESHOLD:
                    self.ball.velocity = pygame.Vector2(0, 0)
                    self.ball_in_motion = False
                    self.drag_done = False
                    return

        # 5) Affichage de la ligne de tir pendant le drag
        if self.dragging:
            current_mouse = pygame.mouse.get_pos()
            self.force, self.angle = drag_and_release(self.ball.position, current_mouse)

    def run(self):
        while True:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.fps)