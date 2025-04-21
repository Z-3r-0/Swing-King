import math
import pygame


class Polygon:
    def __init__(self, terrain_type="fairway", points: list = None, compensates=False):
        self.points = points if points else []
        self.removed = []
        self.terrain_type = terrain_type
        self.shift = pygame.Vector2(0, 0)
        self.root_point = points[0] if points and len(points) > 0 else (math.inf, math.inf)
        self.min_point = self.root_point
        self.compensates = compensates

    def draw_points(self, screen: pygame.Surface):
        for point in self.points:
            pygame.draw.circle(screen, (255, 0, 0), point, 2)

    def draw_polygon(self, screen: pygame.Surface):

        colors = {
            'green': (62,179,62), # @Lucas ici pour la couleur des terrains
            'fairway': (62, 133, 54),
            'bunker': (255, 197, 106),
            'lake': (46,118,201),
            'rocks': (156, 151, 144),#
            'dirt': (130, 99, 54),
            'darkgreen': (49, 110, 46),
            'darkrocks': (128, 128, 128),
            'darkdirt': (87, 59, 19)
        }

        if len(self.points) > 2:
            pygame.draw.polygon(screen, colors[self.terrain_type], self.points)

    def shift_poly(self, shift: pygame.Vector2):
        """
            Shifts the polygon by the shift_poly vector, such as (0, -10)
            DO NOT GIVE COORDINATES OF CAMERA mdrrr
        """
        self.points = [(point[0] - shift.x, point[1] - shift.y) for point in self.points]
        # ============= Removing these two lines will break dip management =============
        self.min_point = self.min_point[0] - shift.x, self.min_point[1] - shift.y
        self.root_point = self.root_point[0] - shift.x, self.root_point[1] - shift.y
        # ==============================================================================
        self.shift -= shift

    def add_point(self, point: tuple | pygame.Vector2):
        if isinstance(point, tuple):
            self.points.append(point)
        else:
            self.points.append((point.x, point.y))
        self.compensate_dip()

    def compensate_dip(self):

        if not self.compensates:
            return

        if not self.points:
            return

        # Check if the points just added is under level 0
        if self.root_point == (math.inf, math.inf):  # If we add the first point
            self.root_point = self.points[-1]
            self.min_point = self.root_point

        if len(self.points) > 3:
            last_pt = self.points[-2]  # This is the point we just added when the function is called
            second_last_pt = self.points[-3]

            if self.points[-1][1] < last_pt[1]:  # If point we just added is above last one
                if second_last_pt[0] == last_pt[0]:
                    self.points.pop(-2)

                new_vertex = (self.points[-1][0], self.min_point[1])
                self.points.append(new_vertex)

        if len(self.points) > 2:
            if self.points[-1][1] - self.min_point[1] > 0:  # If the added point is under root point
                if len(self.points) > 3 and self.points[-2][0] == self.points[-3][0]:
                    self.points.pop(-2)  # Remove auto generated vertex

                self.points[0] = (self.root_point[0], self.points[-1][1])
                self.points.insert(1, self.root_point)
                self.min_point = (
                self.root_point[0], self.points[-1][1])  # Add a point at level of current added point, under root point

    def remove_point(self):

        if not self.points:
            return

        # Check if a vertex was added under last vertex (dip management system)
        if len(self.points) > 2 and self.points[-1][0] == self.points[-2][0]:
            self.removed.append(self.points.pop())
            self.removed.append(self.points.pop())
        else:
            self.removed.append(self.points.pop())

        self.compensate_dip()

    def restore_point(self):

        if not self.removed:
            return

        if len(self.points) > 2 and self.points[-1][0] == self.points[-2][
            0]:  # If the last vertex is a dip-compensating vertex
            self.points.pop()  # Remove that auto-generated vertex

        self.add_point(self.removed.pop())

    def update(self, screen: pygame.Surface, camera_movement: pygame.Vector2):
        self.shift_poly(camera_movement)
        self.draw_polygon(screen)
        self.draw_points(screen)
