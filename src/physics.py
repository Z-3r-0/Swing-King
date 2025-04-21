import pygame
import math
def distance_point_to_segment_vector(point_p: pygame.Vector2, seg_a: pygame.Vector2, seg_b: pygame.Vector2) -> float:
    """
    Return the distance from point_p to the line segment defined by seg_a and seg_b, using pygame.Vector2.
    """
    # Vector representing the line segment
    segment_vec = seg_b - seg_a
    # Vector from the segment start to the point
    point_vec = point_p - seg_a

    segment_len_sq = segment_vec.magnitude_squared()

    # If the segment is essentially a point
    if segment_len_sq < 1e-10: # Use a small epsilon for float comparison
        return point_vec.length()

    # Calculate the projection factor 't' of the point onto the infinite line
    # t = dot_product(AP, AB) / length_squared(AB)
    t = point_vec.dot(segment_vec) / segment_len_sq

    # Clamp t to the range [0, 1] to restrict to the segment
    t = max(0.0, min(1.0, t))

    # Calculate the closest point on the segment
    closest_point_on_segment = seg_a + t * segment_vec

    # Return the distance between the original point and the closest point on the segment
    return point_p.distance_to(closest_point_on_segment)


def get_collision_edge_angle_vector(polygon_points, collision_point):
    """
    Given a list of polygon points (tuples) and a collision point (tuple),
    determine the angle (in degrees) of the polygon edge closest to the collision point.
    Uses pygame.Vector2 internally.

    Returns a tuple (angle_degrees, edge_tuples) where edge_tuples is ((x1, y1), (x2, y2)).
    """
    if not collision_point:
        return None, None

    # Convert inputs to vectors
    collision_vec = pygame.Vector2(collision_point)
    polygon_vecs = [pygame.Vector2(p) for p in polygon_points]

    min_dist = float('inf')
    best_edge_vecs = None # Store the best edge as vectors
    num_points = len(polygon_vecs)

    # Loop through each edge of the polygon using vectors
    for i in range(num_points):
        pt1_vec = polygon_vecs[i]
        pt2_vec = polygon_vecs[(i + 1) % num_points] # wrap-around for last segment

        # Use the vectorized distance function
        dist = distance_point_to_segment_vector(collision_vec, pt1_vec, pt2_vec)

        if dist < min_dist:
            min_dist = dist
            best_edge_vecs = (pt1_vec, pt2_vec)

    if best_edge_vecs is None:
        return None, None

    # Compute the angle of the best edge relative to the horizontal axis
    edge_vector = best_edge_vecs[1] - best_edge_vecs[0]

    # Handle zero-length edge vector case (shouldn't happen with valid polygons)
    if edge_vector.length_squared() < 1e-10:
         angle_deg = 0.0 # Or handle as an error/None
    else:
        # angle_to gives angle relative to the positive x-axis in degrees [-180, 180]
        angle_deg = pygame.Vector2(1, 0).angle_to(edge_vector)
        # Optional: Normalize to [0, 360) if preferred
        # angle_deg = (angle_deg + 360) % 360

    # Convert the best edge vectors back to tuples for the return value,
    # maintaining the original expected output format.
    best_edge_tuples = (best_edge_vecs[0].xy, best_edge_vecs[1].xy)

    return angle_deg, best_edge_tuples