from lib import *
from math import *
from sphere import *
from material import *
from light import *
from intersect import *
from Plane import *

#importantisimo NO LO TOQUES
MAX_RECURSION_DEPTH = 3
#IMPORANTE


class Raytracer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_color = color(255, 255, 255)
        self.clear()
        self.scene = []
        self.background_color = color(0, 0, 0)
        self.light = Light(V3(0, 0, 0), 1)
        self.envmap = None

    def clear(self):
        self.framebuffer = [
            [self.background_color for x in range(self.width)] for y in range(self.height)
        ]

    def point(self, x, y, c=None):
        if y >= 0 and y < self.height and x >= 0 and x < self.width:
            self.framebuffer[y][x] = c or self.current_color

    def write(self, filename):
        writebmp(filename, self.width, self.height, self.framebuffer)

    def render(self):
        fov = int(pi / 2)
        ar = self.width / self.height
        tana = tan(fov / 2)

        for y in range(self.height):
            for x in range(self.width):
                i = ((2 * (x + 0.5) / self.width) - 1) * ar * tana
                j = ((2 * (y + 0.5) / self.height) - 1) * tana

                direction = norm(V3(i, j, -1))
                self.framebuffer[y][x] = self.cast_ray(V3(0, 0, 0), direction)

    def cast_ray(self, origin, direction, recursion=0):

        material, intersect = self.scene_intersect(origin, direction)

        #rompe la recursion si llega al maximo, NO CAMBIAR
        if (
            material is None or recursion >= MAX_RECURSION_DEPTH
        ):  
            if self.envmap:
                return self.envmap.get_color(direction)
            return self.background_color

        if intersect is None:
            return self.background_color

        offset_normal = mul(intersect.normal, 1.1)  
        
        #Reflexion
        if material.albedo[2] > 0:
            reverse_direction = mul(direction, -1)
            reflect_direction = reflect(direction, intersect.normal)
            reflect_orig = (
                sub(intersect.point, offset_normal)
                if dot(reflect_direction, intersect.normal) < 0
                else suma(intersect.point, offset_normal)
            )
            reflect_color = self.cast_ray(
                reflect_orig, reflect_direction, recursion + 1
            )
        else:
            reflect_color = color(0, 0, 0)

        #Refraccion
        if material.albedo[3] > 0:
            refract_dir = refract(
                direction, intersect.normal, material.refractive_index
            )
            refract_orig = (
                sub(intersect.point, offset_normal)
                if dot(refract_dir, intersect.normal) < 0
                else suma(intersect.point, offset_normal)
            )
            refract_color = self.cast_ray(refract_orig, refract_dir, recursion + 1)
        else:
            refract_color = color(0, 0, 0)

        
        #Luz (como estaba antes)
        light_dir = norm(sub(self.light.position, intersect.point))
        intensity = dot(light_dir, intersect.normal)

        light_distance = length(sub(self.light.position, intersect.point))

        light_reflection = reflect(light_dir, intersect.normal)
        specular_intensity = self.light.intensity * (
            max(0, -dot(light_reflection, direction)) ** material.spec
        )

        diffuse = material.diffuse * intensity * material.albedo[0]
        specular = color(255, 255, 255) * specular_intensity * material.albedo[1]
        reflection = reflect_color * material.albedo[2]
        refraction = refract_color * material.albedo[3]

        #Agregado de sombras
        shadow_orig = (
            sub(intersect.point, offset_normal)
            if dot(light_dir, intersect.normal) < 0
            else suma(intersect.point, offset_normal)
        )
        shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)
        shadow_intensity = 0

        if (
            shadow_material
            and length(sub(shadow_intersect.point, shadow_orig)) < light_distance
        ):
            shadow_intensity = 0.9

        intensity = (
            self.light.intensity
            * max(0, dot(light_dir, intersect.normal))
            * (1 - shadow_intensity)
        )

        if material.texture and intersect.text_coords is not None:
            text_color = material.texture.get_color(
                intersect.text_coords[0], intersect.text_coords[1]
            )
            diffuse = text_color * 255

        return diffuse + specular + reflection + refraction


    def scene_intersect(self, origin, direction):
        zbuffer = 999999
        material = None
        intersect = None

        for s in self.scene:
            object_intersect = s.ray_intersect(origin, direction)
            if object_intersect:
                if object_intersect.distance < zbuffer:
                    zbuffer = object_intersect.distance
                    material = s.material
                    intersect = object_intersect

        return material, intersect

# --------------------- LO CHIDO --------------------------------------------
rubber = Material(diffuse=color(80, 0, 0), albedo=(0.4, 0.3), spec=50)
white = Material(diffuse=color(255, 255, 255), albedo=(0.9, 0.9), spec=10)
cafe = Material(diffuse=color(170, 80, 40), albedo=(0.3, 0.5), spec=10)
cafeclaro = Material(diffuse=color(230, 170, 135), albedo=(0.9, 0.9), spec=5)
negro = Material(diffuse=color(0, 0, 0), albedo=(0.3, 0.3), spec=3)


r = Raytracer(800, 800)
r.light = Light(V3(20, 20, -20), 1.5)
r.scene = [
    Sphere(V3(2.5, -1, -10), 1.5, rubber),
    Sphere(V3(2.5, 1.5, -10), 1.25, cafeclaro),
    Sphere(V3(2.3, 1.1, -9), 0.4, cafe),
    Sphere(V3(3.4, 2.3, -9), 0.35, cafe),
    Sphere(V3(1.4, 2.3, -9), 0.35, cafe),
    Sphere(V3(4, 0, -10), 0.45, cafeclaro),
    Sphere(V3(1, 0, -10), 0.45, cafeclaro),
    Sphere(V3(4, -2.2, -10), 0.5, cafeclaro),
    Sphere(V3(1, -2.2, -10), 0.5, cafeclaro),
    Sphere(V3(2, 1, -8), 0.1, negro),
    Sphere(V3(2.3, 1.5, -8), 0.1, negro),
    Sphere(V3(1.7, 1.5, -8), 0.1, negro),
    Sphere(V3(-2.5, -1, -10), 1.5, white),
    Sphere(V3(-2.5, 1.5, -10), 1.25, white),
    Sphere(V3(-2.4, 1.1, -9), 0.4, white),
    Sphere(V3(-3.3, 2.3, -9), 0.35, white),
    Sphere(V3(-1.3, 2.3, -9), 0.35, white),
    Sphere(V3(-4, 0, -10), 0.45, white),
    Sphere(V3(-1, 0, -10), 0.45, white),
    Sphere(V3(-4, -2.2, -10), 0.5, white),
    Sphere(V3(-1, -2.2, -10), 0.5, white),
    Sphere(V3(-2.1, 1, -8), 0.1, negro),
    Sphere(V3(-2.4, 1.5, -8), 0.1, negro),
    Sphere(V3(-1.8, 1.5, -8), 0.1, negro),
]

r.render()
r.write("Proyecto2.bmp")