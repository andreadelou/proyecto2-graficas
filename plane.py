from lib import *
from sphere import *
from math import pi, acos, atan2
import struct


class Plane(object):
    def __init__(self, position, normal, material):
        self.position = position
        self.normal = norm(normal)
        self.material = material

    def ray_intersect(self, origin, direction):
        d = dot(direction, self.normal)

        if abs(d) > 0.0001:
            t = dot(self.normal, sub(self.position, origin)) / d
            if t > 0:
                hit = suma(
                    origin, V3(direction.x * t, direction.y * t, direction.z * t)
                )

                return Intersect(
                    distance=t, point=hit, normal=self.normal, text_coords=None
                )

        return None


class Envmap(object):
    def __init__(self, path):
        self.path = path
        self.read()

    def read(self):
        image = open(self.path, "rb")
        image.seek(10)
        header_size = struct.unpack("=l", image.read(4))[0]

        image.seek(14 + 4)
        self.width = struct.unpack("=l", image.read(4))[0]
        self.height = struct.unpack("=l", image.read(4))[0]
        image.seek(header_size)

        self.framebuffer = []
        for y in range(self.height):
            self.framebuffer.append([])
            for x in range(self.width):
                b = ord(image.read(1))
                g = ord(image.read(1))
                r = ord(image.read(1))
                self.framebuffer[y].append(color(r, g, b))

        image.close()

    def get_color(self, direction):
        direction = norm(direction)
        x = int((atan2(direction[2], direction[0]) / (2 * pi) + 0.5) * self.width)
        y = int(acos(-direction[1]) / pi * self.height)

        if x < self.width and y < self.height:
            return self.framebuffer[y][x]

        return color(0, 0, 0)


class Cube(object):
    def __init__(self, position, size, material):
        self.position = position
        self.size = size
        self.material = material
        mid_size = size / 2

        self.planes = [
            Plane(suma(position, V3(mid_size, 0, 0)), V3(1, 0, 0), material),
            Plane(suma(position, V3(-mid_size, 0, 0)), V3(-1, 0, 0), material),
            Plane(suma(position, V3(0, mid_size, 0)), V3(0, 1, 0), material),
            Plane(suma(position, V3(0, -mid_size, 0)), V3(0, -1, 0), material),
            Plane(suma(position, V3(0, 0, mid_size)), V3(0, 0, 1), material),
            Plane(suma(position, V3(0, 0, -mid_size)), V3(0, 0, -1), material),
        ]

    def ray_intersect(self, origin, direction):
        epsilon = 0.001

        min_bounds = [0, 0, 0]
        max_bounds = [0, 0, 0]

        for i in range(3):
            min_bounds[i] = self.position[i] - (epsilon + self.size / 2)
            max_bounds[i] = self.position[i] + (epsilon + self.size / 2)

        t = float("inf")
        intersect = None
        texture_coords = None

        for plane in self.planes:
            plane_intersection = plane.ray_intersect(origin, direction)

            if plane_intersection is not None:
                if (
                    plane_intersection.point[0] >= min_bounds[0]
                    and plane_intersection.point[0] <= max_bounds[0]
                ):
                    if (
                        plane_intersection.point[1] >= min_bounds[1]
                        and plane_intersection.point[1] <= max_bounds[1]
                    ):
                        if (
                            plane_intersection.point[2] >= min_bounds[2]
                            and plane_intersection.point[2] <= max_bounds[2]
                        ):
                            if plane_intersection.distance < t:
                                t = plane_intersection.distance
                                intersect = plane_intersection

                                if abs(plane.normal[2]) > 0:
                                    coord0 = (
                                        plane_intersection.point[0] - min_bounds[0]
                                    ) / (max_bounds[0] - min_bounds[0])
                                    coord1 = (
                                        plane_intersection.point[1] - min_bounds[1]
                                    ) / (max_bounds[1] - min_bounds[1])

                                elif abs(plane.normal[1]) > 0:
                                    coord0 = (
                                        plane_intersection.point[0] - min_bounds[0]
                                    ) / (max_bounds[0] - min_bounds[0])
                                    coord1 = (
                                        plane_intersection.point[2] - min_bounds[2]
                                    ) / (max_bounds[2] - min_bounds[2])

                                elif abs(plane.normal[0]) > 0:
                                    coord0 = (
                                        plane_intersection.point[1] - min_bounds[1]
                                    ) / (max_bounds[1] - min_bounds[1])
                                    coord1 = (
                                        plane_intersection.point[2] - min_bounds[2]
                                    ) / (max_bounds[2] - min_bounds[2])

                                texture_coords = [coord0, coord1]

        if intersect is None:
            return None

        return Intersect(
            distance=intersect.distance,
            point=intersect.point,
            normal=intersect.normal,
            text_coords=texture_coords,
        )