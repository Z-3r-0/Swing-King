import pygame
import math
from src.entities import Ball, Camera, Terrain, Obstacle
# Removed src.utils import
# Removed src.animation import
from src.scene import Scene
from src.scenetype import SceneType
# Renamed physics_utils to physics for clarity, assuming that's the intent
from src.utils import physics_utils as physics # Use the provided physics_utils file
from src.utils import level_loader

BALL_START_X, BALL_START_Y = 800, 500 # TODO - REPLACE WITH LEVEL DATA LATER
SCENE_WIDTH, SCENE_HEIGHT = 10000, 2000 # TODO - REPLACE WITH LEVEL DATA LATER
GRAVITY = 980  # Gravitational acceleration in pixels/s² # TODO - REPLACE WITH LEVEL DATA LATER
# BALL_RADIUS = 50.0 # This was incorrect, calculated from Ball class now

# --- Helper functions moved from forbidden utils.py ---

def calculate_drag_force_angle(start_pos: pygame.Vector2, end_pos: pygame.Vector2, max_force: float, min_force: float = 0):
    drag_vector = start_pos - end_pos
    distance = drag_vector.length()

    if distance < 1.0:
        return 0, 0

    max_force_distance = 300.0
    force = (distance / max_force_distance) * max_force
    force = max(min_force if distance > 5 else 0, min(force, max_force))

    if force < min_force: # Ensure force is zero if below threshold
        return 0, 0

    if drag_vector.length_squared() > 0:
         # Angle measured clockwise from the upward direction (negative Y).
        angle_rad = math.atan2(-drag_vector.x, -drag_vector.y)
        angle_deg = math.degrees(angle_rad)
        angle_deg = (angle_deg + 360) % 360
    else:
        angle_deg = 0 # Default angle if vector is zero

    return force, angle_deg


def draw_predicted_trajectory(start_pos: pygame.Vector2, force: float, angle_deg: float, gravity: float, dt: float, surface: pygame.Surface, camera_offset: pygame.Vector2, color: tuple, radius: int, spacing: int, steps: int = 50):
    if force <= 0:
        return

    angle_rad = math.radians(angle_deg)
    velocity = pygame.Vector2(
        -force * math.cos(angle_rad),
         force * math.sin(angle_rad)
    )
    position = start_pos.copy()
    damping_factor = 0.99 # Match game loop damping

    steps_since_last_dot = 0

    for i in range(steps):
        position += velocity * dt
        velocity.y += gravity * dt
        velocity *= damping_factor

        steps_since_last_dot += 1

        if steps_since_last_dot >= spacing:
            screen_pos = position - camera_offset
            if 0 <= screen_pos.x <= surface.get_width() and 0 <= screen_pos.y <= surface.get_height():
                 pygame.draw.circle(surface, color, screen_pos, radius)
            steps_since_last_dot = 0

        if velocity.length_squared() < 1.0:
            break

# TODO - INSERT IN THE CLASS LATER

class Game(Scene):
    def __init__(self, screen, scene_from: SceneType = None):
        # Assume Scene base class exists and works as before
        # If Scene is not provided, this will error. Assuming it's available.
        try:
            super().__init__(screen, SceneType.GAME, "Game", scene_from)
        except NameError: # Fallback if Scene class isn't actually available
             print("Warning: Scene base class not found. Game running without Scene features.")
             self.screen = screen
             self.clock = pygame.time.Clock()
             self.fps = 60 # Default fps

        self.dt = 1 / self.fps # Initialize dt
        self.dragging = False
        self.drag_done = False
        self.ball_in_motion = False

        self.max_force = 1500
        self.min_force = 50

        self.force = 0
        self.angle = 0

        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        self.level_path = "data/levels/test_level.json"

        self.terrain_data, self.obstacles_data = level_loader.load_json_level(self.level_path)

        self.ball = Ball(pygame.Vector2(BALL_START_X, BALL_START_Y), 4.2, 0.047, pygame.Color("white"),
                 "assets/images/balls/golf_ball.png")
        self.ball_radius_scaled = self.ball.radius * self.ball.scale_value

        self.terrain_polys = level_loader.json_to_list(self.terrain_data, self.screen, 0)
        self.obstacles = level_loader.json_to_list(self.obstacles_data, self.screen, 1)

        self.prev_collision_object_id = None
        self.collision_toggle_count = 0
        self.max_toggle_toggles = 6

        self.camera = Camera(pygame.Vector2(0, 0), self.width, self.height, SCENE_WIDTH, SCENE_HEIGHT)
        self.camera.calculate_position(self.ball.position)

        try:
            self.background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
            self.background = pygame.transform.smoothscale(self.background, (self.width, self.height))
        except pygame.error as e:
            print(f"Error loading background image: {e}")
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill(pygame.Color("lightblue"))


        self.dot_spacing = 15
        self.dot_radius = 3
        self.dot_color = (255, 0, 0, 180)

        # Animation du golfer
        # self.golfer_animation = Animation("assets/images/golfer", pygame.Vector2(500, 500))
        # self.golfer_animation_sprite = pygame.sprite.Group()
        # self.golfer_animation_sprite.add(self.golfer_animation)

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for poly in self.terrain_polys:
            poly.draw_polygon(self.screen, self.camera.position)

        for obs in self.obstacles:
            obs.draw_obstacle(self.screen, self.camera.position)

        self.ball.draw(self.screen, self.camera.position)

        if self.dragging:
            mouse_pos = pygame.mouse.get_pos()
            ball_screen_pos = self.ball.position - self.camera.position

            pygame.draw.line(self.screen, pygame.Color("red"), ball_screen_pos, mouse_pos, 2)

            self.force, self.angle = calculate_drag_force_angle(
                ball_screen_pos,
                mouse_pos,
                self.max_force,
                self.min_force
            )

            if self.force > 0:
                 draw_predicted_trajectory(
                     self.ball.position,
                     self.force,
                     self.angle,
                     GRAVITY,
                     self.dt,
                     self.screen,
                     self.camera.position,
                     self.dot_color,
                     self.dot_radius,
                     self.dot_spacing,
                     steps=50
                 )

    def handle_events(self):
        """
        Handle input, ball movement, gravity, collisions with bounce/slide,
        hole detection, flat-surface slide, and prevent infinite toggling.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.Vector2(event.pos)
                ball_screen_pos = self.ball.position - self.camera.position
                click_dist = mouse_pos.distance_to(ball_screen_pos)

                if not self.ball_in_motion and not self.drag_done and click_dist <= self.ball_radius_scaled * 1.5:
                    self.dragging = True

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging:
                if self.force >= self.min_force:
                    self.ball.velocity = pygame.Vector2(
                        -self.force * math.cos(math.radians(self.angle)),
                        self.force * math.sin(math.radians(self.angle))
                    )
                    self.ball_in_motion = True
                    self.drag_done = True
                self.dragging = False

        if self.ball_in_motion:
            # 1) Movement + gravity + damping
            self.ball.shift_position(self.ball.velocity * self.dt)
            self.ball.velocity.y += GRAVITY * self.dt
            damping_factor = 0.99
            self.ball.velocity *= damping_factor

            # 2) Gather potential collisions
            collisions = []

            # Check Terrain
            for terrain in self.terrain_polys:
                if not self.ball.rect.colliderect(terrain.rect):
                    continue
                mask_off = (
                    self.ball.rect.left - terrain.rect.left,
                    self.ball.rect.top - terrain.rect.top
                )
                overlap_point = terrain.mask.overlap(self.ball.mask, mask_off)
                if overlap_point:
                    normal, depth = physics.get_polygon_collision_normal_depth(
                        terrain.points, self.ball.position, self.ball_radius_scaled
                    )
                    if normal and depth > 0.1:
                        collisions.append((terrain, normal, depth))

            # Check Obstacles
            for obs in self.obstacles:
                if not obs.is_colliding:
                    continue
                obs_rect = obs.get_rotated_rect()
                if not self.ball.rect.colliderect(obs_rect):
                    continue
                mask_off = (
                    self.ball.rect.left - obs_rect.left,
                    self.ball.rect.top - obs_rect.top
                )
                if obs.rotated_mask: # Check if mask exists
                    overlap_point = obs.rotated_mask.overlap(self.ball.mask, mask_off)
                    if overlap_point:
                        # Convert obstacle points relative to its position to world space
                        world_obs_points = [(p + obs.position) for p in obs.rotated_points]
                        if not world_obs_points: # Skip if no points
                             continue

                        normal, depth = physics.get_polygon_collision_normal_depth(
                            world_obs_points, self.ball.position, self.ball_radius_scaled
                        )
                        if normal and depth > 0.1:
                            collisions.append((obs, normal, depth))


            # 3) Process Collisions
            if collisions:
                # Simple: handle first collision found
                collided_object, normal, depth = collisions[0]

                # 3a) Resolve penetration
                push_factor = 1.01
                self.ball.shift_position(normal * depth * push_factor)

                # 3b) Decompose velocity
                vel = self.ball.velocity
                vn = vel.dot(normal)

                if vn < 0: # Moving into the surface
                    # 3c) Get coefficients
                    rest = getattr(collided_object, 'bounce_factor', 0.4)
                    fric = getattr(collided_object, 'friction', 0.3)

                    # 3d) Calculate new normal velocity (bounce)
                    new_vn = -vn * rest

                    # 3e) Calculate new tangential velocity (friction)
                    tangent = pygame.Vector2(-normal.y, normal.x)
                    vt = vel.dot(tangent)
                    # Simplified friction model
                    new_vt = vt * (1 - fric) # Reduce tangential velocity

                    # 3f) Combine components & minimum bounce
                    MIN_BOUNCE_VEL = 10.0
                    if abs(new_vn) < MIN_BOUNCE_VEL and abs(vn) > 1:
                        new_vn = -MIN_BOUNCE_VEL * (vn / abs(vn)) if abs(vn) > 1e-6 else -MIN_BOUNCE_VEL * normal.y

                    self.ball.velocity = new_vn * normal + new_vt * tangent

                    # 3g) Toggle detection
                    current_object_id = id(collided_object)
                    if self.prev_collision_object_id is not None and current_object_id != self.prev_collision_object_id:
                        self.collision_toggle_count += 1
                    else:
                        self.collision_toggle_count = 0
                    self.prev_collision_object_id = current_object_id

                    if self.collision_toggle_count >= self.max_toggle_toggles:
                        self.ball.velocity = pygame.Vector2(0, 0)
                        self.ball_in_motion = False
                        self.drag_done = False
                        self.prev_collision_object_id = None
                        self.collision_toggle_count = 0
                        return # Exit physics update

            else:
                # No collision this frame
                self.prev_collision_object_id = None
                self.collision_toggle_count = 0


            # 4) Check if ball should stop
            STOP_SPEED_THRESHOLD = 5.0
            is_on_flat_surface = False
            if collisions:
                 _, normal, _ = collisions[0]
                 if abs(normal.y) > 0.95:
                     is_on_flat_surface = True

            if self.ball.velocity.length_squared() < STOP_SPEED_THRESHOLD**2 and (not collisions or is_on_flat_surface):
                self.ball.velocity = pygame.Vector2(0, 0)
                self.ball_in_motion = False
                self.drag_done = False
                self.prev_collision_object_id = None
                self.collision_toggle_count = 0

        # Update camera
        if self.ball_in_motion or self.dragging:
             self.camera.calculate_position(self.ball.position)


    def run(self):
        while True:
            # Use Scene's clock and fps if available, otherwise use own
            try:
                self.dt = self.clock.tick(self.fps) / 1000.0
            except AttributeError: # Fallback if Scene init failed
                 self.dt = pygame.time.Clock().tick(60) / 1000.0 # Use a default clock/fps

            if self.dt > 0.1:
                self.dt = 1 / (self.fps if hasattr(self, 'fps') else 60)

            self.handle_events()
            self.draw()
            pygame.display.flip()