from intersect import *
from lib import *
from vector import V3

def suma( v0, v1):
        return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)
    
class Sphere(object):
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material
    
    def ray_intersect(self, origin, direction):
        L = sub(self.center, origin)
        tca = dot(L, direction)

        l = length(L)

        d2 = l**2 - tca**2  
        

        if d2 > self.radius**2:
            return None

        thc = (self.radius**2 - d2)**1/2

        t0 = tca - thc
        t1 = tca + thc

        if t0 < 0:
            t0 = t1
        if t0 < 0:
            return None

        impact = suma(multi(direction,t0), origin)
        normal = norm(sub(impact, self.center))

        return Intersect(
            distance=t0,
            point = impact,
            normal = normal
        )