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
        self.obstacles = level_loader.json_to_list(self.obstacles_data, self.screen, 1)
        self.potential_collision_indices = []
        self.potential_collision_polygons = []

        self.prev_collision_terrain = None
        self.collision_toggle_count = 0
        self.max_toggle_toggles = 4 # maximum alternations allowed before stopping
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

    def handle_events(self):
        """
        Handle input, ball movement, gravity, collisions with bounce/slide,
        hole detection, flat-surface slide, and prevent infinite toggling.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                click_dist = pygame.Vector2(event.pos).distance_to(self.ball.position)
                if not self.drag_done and click_dist <= BALL_RADIUS:
                    self.dragging = True

            if event.type == pygame.MOUSEBUTTONUP and self.dragging:
                if not self.drag_done:
                    self.force, self.angle = drag_and_release(
                        self.ball.position,
                        pygame.mouse.get_pos()
                    )
                    self.ball.velocity = pygame.Vector2(
                        -self.force * math.cos(math.radians(self.angle)),
                        self.force * math.sin(math.radians(self.angle))
                    )
                    self.dragging = False
                    self.ball_in_motion = True
                    self.drag_done = True

        if self.ball_in_motion:
            # 1) Movement + gravity + damping
            self.ball.shift_position(self.ball.velocity * self.dt)
            self.ball.velocity.y += GRAVITY * self.dt
            self.ball.velocity *= 0.98

            # 2) Gather collisions
            collisions = []  # [(terrain, normal, depth)]
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

            # 3) Hole detection: simultaneous faces
            if len(collisions) >= 2:
                self.ball.velocity = pygame.Vector2(0, 0)
                self.ball_in_motion = False
                self.drag_done = False
                return

            # 4) Single collision: bounce/slide
            if len(collisions) == 1:
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

                # Increment count when switching between different terrain faces
                if self.prev_collision_terrain is not None and current_terrain_id != self.prev_collision_terrain:
                    self.collision_toggle_count += 1

                # Update the last terrain collided
                self.prev_collision_terrain = current_terrain_id

                # If too many alternations, stop the ball
                if self.collision_toggle_count >= self.max_toggle_toggles:
                    self.ball.velocity = pygame.Vector2(0, 0)
                    self.ball_in_motion = False
                    self.drag_done = False
                    return

                # 4g) stop if slow stop if slow
                STOP_S = 5.0
                if self.ball.velocity.length() < STOP_S:
                    self.ball.velocity = pygame.Vector2(0, 0)
                    self.ball_in_motion = False
                    self.drag_done = False
                    return
            else:
                # reset toggle counter if no collision
                self.prev_collision_terrain = None
                self.collision_toggle_count = 0

        # 5) draw aim line
        if self.dragging:
            mpos = pygame.mouse.get_pos()
            self.force, self.angle = drag_and_release(self.ball.position, mpos)

    def run(self):
        while True:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.fps)