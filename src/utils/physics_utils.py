import math
import pygame # Import pygame for Vector2

# --- Collision Helper Functions ---

def project_polygon(axis, points):
    """Projects a polygon onto an axis."""
    min_proj = float('inf')
    max_proj = float('-inf')
    for point in points:
        projection = axis.dot(point)
        min_proj = min(min_proj, projection)
        max_proj = max(max_proj, projection)
    return min_proj, max_proj

def project_circle(axis, center, radius):
    """Projects a circle onto an axis."""
    projection = axis.dot(center)
    min_proj = projection - radius
    max_proj = projection + radius
    return min_proj, max_proj

def get_polygon_collision_normal_depth(poly_points, ball_center, ball_radius):
    """
    Calculates the collision normal and penetration depth for a ball colliding
    with a convex polygon using Separating Axis Theorem ideas.
    Assumes poly_points are Vector2 in world coordinates.
    Returns (normal, depth) or (None, 0).
    """
    min_depth = float('inf')
    collision_normal = None
    axis_normal = None

    points = poly_points # Assume they are already Vector2
    num_points = len(points)

    if num_points < 2: # Need at least a line segment
        return None, 0

    # 1. Check Edges
    for i in range(num_points):
        p1 = points[i]
        p2 = points[(i + 1) % num_points]
        edge = p2 - p1
        if edge.length_squared() == 0: continue # Skip zero-length edges

        # Normal perpendicular to the edge, pointing outwards for CCW winding
        edge_normal = pygame.Vector2(-edge.y, edge.x).normalize()

        min_proj_poly, max_proj_poly = project_polygon(edge_normal, points)
        min_proj_ball, max_proj_ball = project_circle(edge_normal, ball_center, ball_radius)

        if max_proj_ball < min_proj_poly or max_proj_poly < min_proj_ball:
            return None, 0 # Separating axis found

        overlap = min(max_proj_poly, max_proj_ball) - max(min_proj_poly, min_proj_ball)

        if overlap < min_depth:
            min_depth = overlap
            axis_normal = edge_normal # Potential collision normal

    # 2. Check Vertices (Closest point approach for accurate normal/depth)
    closest_point = None
    min_dist_sq = float('inf')

    for i in range(num_points):
        p1 = points[i]
        p2 = points[(i + 1) % num_points]
        edge = p2 - p1
        segment_vec = ball_center - p1
        edge_len_sq = edge.length_squared()

        if edge_len_sq > 1e-9: # Avoid division by zero for zero-length edges
            t = segment_vec.dot(edge) / edge_len_sq
            t = max(0, min(1, t)) # Clamp to segment
        else:
            t = 0 # Treat as point p1 if edge has no length

        point_on_segment = p1 + t * edge
        dist_sq = ball_center.distance_squared_to(point_on_segment)

        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            closest_point = point_on_segment

    if closest_point is not None and min_dist_sq < ball_radius * ball_radius:
        dist = math.sqrt(min_dist_sq)
        depth = ball_radius - dist
        if depth > 1e-4:
            if dist > 1e-6:
                normal = (ball_center - closest_point).normalize()
            else:
                # Ball center is very close/on boundary, use the axis normal from SAT
                # Ensure it points towards the ball
                if axis_normal is not None:
                    if axis_normal.dot(ball_center - closest_point) < 0:
                         normal = -axis_normal
                    else:
                         normal = axis_normal
                else: # Fallback if SAT failed (shouldn't happen if collision detected here)
                    normal = pygame.Vector2(0, -1) # Arbitrary up normal

            # Use the depth calculated from closest point, it's more accurate than SAT overlap
            return normal, depth

    return None, 0 # No collision detected by closest point check


# --- Original Trajectory Functions ---

def calculate_traj_y(x: float, speed: float, angle: float, initial_pos_y: float):
    """
    Calculates the vertical position (y) of the ball based on the horizontal distance (x).

    :param x: Horizontal distance traveled
    :param speed: Applied speed (m/s)
    :param angle: Launch angle (alpha) in degrees
    :param initial_pos_y: initial position of the ball
    :return: Vertical position (y) of the ball
    """

    angle_radians = math.radians(angle)
    cos_alpha = math.cos(angle_radians)
    tan_alpha = math.tan(angle_radians)

    # Avoid division by zero if angle is 90° or speed is 0
    if abs(cos_alpha) < 1e-6 or abs(speed) < 1e-6:
        return initial_pos_y

    # Using g = 9.8 m/s^2 - Needs adaptation for pixel units
    # This formula is likely not directly usable with game's pixel physics
    y = (-4.9 * (x ** 2)) / (speed ** 2 * cos_alpha ** 2) + tan_alpha * x + initial_pos_y
    return y

def calculate_traj_x(t: float, speed: float, angle: float, mass: float, initial_pos_x: float):
    """
    Calculates the horizontal position (x) of the ball based on the time (t).

    :param t: time elapsed since the impact
    :param speed: Applied speed (m/s)
    :param angle: Launch angle (alpha) in degrees
    :param mass: mass of the ball
    :param initial_pos_x: initial position of the ball
    :return: Horizontal position (x) of the ball
    """

    angle_radians = math.radians(angle)
    cos_alpha = math.cos(angle_radians)

    # Original formula: x = (speed * 0.1 / mass) * cos_alpha * t + initial_pos_x
    # Standard formula (no air resistance): x = initial_pos_x + speed * cos_alpha * t
    # Using standard formula as original seems unusual and likely not compatible
    x = initial_pos_x + speed * cos_alpha * t

    return x