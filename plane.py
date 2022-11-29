from lib import *
from sphere import *
from math import pi, acos, atan2
import struct
from material import*
from vector import *
from intersect import*

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
        direction = direction.norm()
        x = int(((atan2(direction.z, direction.x) / (2 * pi)) + 0.5) * self.width)
        y = int((acos(direction.y) / pi) * self.height)

        if x < self.width and y < self.height:
            return self.framebuffer[y][x]

        return color(0, 0, 0)


class Cube(object):
    def __init__(self, position, size, material ):
        self.position = position
        self.size = size
        self.material = material
        self.planes = []
    

        self.boundsMin = [0,0,0]
        self.boundsMax = [0,0,0]

        halfSizeX = size[0] / 2
        halfSizeY = size[1] / 2
        halfSizeZ = size[2] / 2

        #Sides
        self.planes.append(Plane( add(position, V3(halfSizeX,0,0)), V3(1,0,0), material))
        self.planes.append(Plane( add(position, V3(-halfSizeX,0,0)), V3(-1,0,0), material))

        # Up and down
        self.planes.append(Plane( add(position, V3(0,halfSizeY,0)), V3(0,1,0), material))
        self.planes.append(Plane( add(position, V3(0,-halfSizeY,0)), V3(0,-1,0), material))

        # Front and Back
        self.planes.append(Plane( add(position, V3(0,0,halfSizeZ)), V3(0,0,1), material))
        self.planes.append(Plane( add(position, V3(0,0,-halfSizeZ)), V3(0,0,-1), material))

        #Bounds
        epsilon = 0.001
        for i in range(3):
            self.boundsMin[i] = self.position[i] - (epsilon + self.size[i]/2)
            self.boundsMax[i] = self.position[i] + (epsilon + self.size[i]/2)


    def ray_intersect(self, orig, dir):
        intersect = None
        t = float('inf')

        uvs = None

        for plane in self.planes:
            planeInter = plane.ray_intersect(orig, dir)
            if planeInter is not None:
                # Si estoy dentro de los bounds
                if planeInter.point[0] >= self.boundsMin[0] and planeInter.point[0] <= self.boundsMax[0]:
                    if planeInter.point[1] >= self.boundsMin[1] and planeInter.point[1] <= self.boundsMax[1]:
                        if planeInter.point[2] >= self.boundsMin[2] and planeInter.point[2] <= self.boundsMax[2]:
                            #Si soy el plano mas cercano
                            if planeInter.distance < t:
                                t = planeInter.distance
                                intersect = planeInter

                                if abs(plane.normal[0]) > 0:
                                    u = (planeInter.point[1] - self.boundsMin[1]) / (self.boundsMax[1] - self.boundsMin[1])
                                    v = (planeInter.point[2] - self.boundsMin[2]) / (self.boundsMax[2] - self.boundsMin[2])
                                elif abs(plane.normal[1]) > 0:
                                    u = (planeInter.point[0] - self.boundsMin[0]) / (self.boundsMax[0] - self.boundsMin[0])
                                    v = (planeInter.point[2] - self.boundsMin[2]) / (self.boundsMax[2] - self.boundsMin[2])
                                elif abs(plane.normal[2]) > 0:
                                    u = (planeInter.point[0] - self.boundsMin[0]) / (self.boundsMax[0] - self.boundsMin[0])
                                    v = (planeInter.point[1] - self.boundsMin[1]) / (self.boundsMax[1] - self.boundsMin[1])
                                
                                uvs = V2(u, v)

        if intersect is None:
            return None

        return Intersect(distance = intersect.distance,
                         point = intersect.point,
                         normal = intersect.normal,
                         texCoords = uvs,
                         sceneObject = self)
        
# -----------------------------TRIANGULO -----------------------------------------
     
def subtract(A, B):
    if type(A) == int and type(B) == int:
        return A - B
    elif type(A) == float and type(B) == float:
        return A - B
    elif len(A) == 3 and len(B) == 3:
        return V3(A.x - B.x, A.y - B.y, A.z - B.z)

def cross(A, B):
    i = ((A.y * B.z) - (A.z * B.y))
    j = -((A.x * B.z) - (A.z * B.x))
    k = ((A.x * B.y) - (A.y * B.x))
    product = V3(i, j, k)
    return product

def add(A, B):
    if type(A) == int and type(B) == int:
        return A + B
    elif type(A) == float and type(B) == float:
        return A + B
    elif len(A) == 3 and len(B) == 3:
        return V3(A.x + B.x, A.y + B.y, A.z + B.z)

    
class Triangle(object):
    def __init__(self, A, B, C, material = Material(), isSingleSided = True):
        self.vertA = A
        self.vertB = B
        self.vertC = C
        self.isSingleSided = isSingleSided
        self.AB = subtract(B, A)
        self.AC = subtract(C, A)
        self.BC = subtract(C, B)
        self.CA = subtract(A, C)
        self.normal = norm(cross(self.AB, self.AC))
        self.material = material

    def ray_intersect(self, orig, dir):
        intersect = None
        texture_coords = None
        denom = dot(self.normal, dir)

        if abs(denom) > 0.0001:

            #Single/Double sided feature
            if dot(dir, self.normal) > 0 and self.isSingleSided:
                return None

            D = dot(self.normal, self.vertA)
            num = (dot(self.normal, orig) + D)
            t = num/denom

            if t > 0:
                hit = add(orig, mul(t, dir))

                # edge 0
                edge0 = self.AB
                vp0 = subtract(hit, self.vertA)
                C = cross(edge0, vp0)
                if dot(self.normal, C) < 0: 
                    return None

                # edge 1
                edge1 = self.BC
                vp1 = subtract(hit, self.vertB)
                C = cross(edge1, vp1)
                if dot(self.normal, C) < 0:
                    return None
                
                # edge 2
                edge2 = self.CA
                vp2 = subtract(hit, self.vertC)
                C = cross(edge2, vp2)
                if dot(self.normal, C) < 0:
                    return None


                # Tex Coords
                tx = None
                ty = None

                if self.material.texture:
                    tx = abs(hit.x / 5)
                    ty = abs(hit.y / 5)
                
                return Intersect(
                distance=intersect.distance,
                point=intersect.point,
                normal=intersect.normal,
                text_coords=texture_coords,
                )

        return None