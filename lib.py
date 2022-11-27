import struct
from vector import *
import math
from collections import namedtuple

def char(c):
  return struct.pack('=c', c.encode('ascii'))

def word(w):
  return struct.pack('=h', w)

def dword(d):
  return struct.pack('=l', d)

# def color(r, g, b):
#     r = int(min(255, max(r, 0)))
#     g = int(min(255, max(g, 0)))
#     b = int(min(255, max(b, 0)))
#     return bytes([b, g, r])

class color(object):
  def __init__(self, r, g, b):
    self.r = r
    self.g = g
    self.b = b

  def __add__(self, other_color):
    r = self.r + other_color.r
    g = self.g + other_color.g
    b = self.b + other_color.b

    return color(r, g, b)

  def __mul__(self, other):
    r = self.r * other
    g = self.g * other
    b = self.b * other
    return color(r, g, b)

  def __repr__(self):
    return "color(%s, %s, %s)" % (self.r, self.g, self.b)

  def toBytes(self):
    self.r = int(max(min(self.r, 255), 0))
    self.g = int(max(min(self.g, 255), 0))
    self.b = int(max(min(self.b, 255), 0))
    return bytes([int(self.b), int(self.g), int(self.r)])

  __rmul__ = __mul__
  
# BLACK = color(0, 0, 0)
# WHITE = color(255, 255, 255)



def clear(self):
    self.framebuffer = [
        [self.clear_color for x in range(self.width)]
        for y in range(self.height)
    ]


def set_clear_color(self, r, g, b):
    adjusted_r = self.clamping(r * 255)
    adjusted_g = self.clamping(g * 255)
    adjusted_b = self.clamping(b * 255)
    self.clear_color = color(adjusted_r, adjusted_g, adjusted_b)


def writebmp(filename, width, height, framebuffer):
    f = open(filename, 'bw')

    # pixel header
    f.write(char('B'))
    f.write(char('M'))
    f.write(dword(14 + 40 + width * height * 3))
    f.write(word(0))
    f.write(word(0))
    f.write(dword(14 + 40))

    # info header
    f.write(dword(40))
    f.write(dword(width))
    f.write(dword(height))
    f.write(word(1))
    f.write(word(24))
    f.write(dword(0))
    f.write(dword(width * height * 3))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))

    # pixel data
    for x in range(height):
        for y in range(width):
            f.write(framebuffer[x][y].toBytes())

    f.close()



def length(v0):
    return (v0.x**2 + v0.y**2 + v0.z**2)**0.5
  
def norm(v0):
  v0length = length(v0)

  if not v0length:
      return V3(0, 0, 0)

  return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)
  
def sub(v0, v1):
  return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)
  
def dot(v0, v1):
  return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def mul(v0,k):
    return V3(
        v0.x * k,
        v0.y * k,
        v0.z * k
    )

def suma(v0, v1):
  return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)
  
#reflexion
def reflect(I, N):
  return norm(sub(I, mul(N, 2 * dot(I, N))))

#refraccion
def refract(I, N, refractive_index):  
    cosi = -max(-1, min(1, dot(I, N)))
    etai = 1
    etat = refractive_index

    if cosi < 0: 
      cosi = -cosi
      etai, etat = etat, etai
      N = mul(N, -1)

    eta = etai/etat
    k = 1 - eta**2 * (1 - cosi**2)
    if k < 0:
      return V3(1, 0, 0)

    return norm(suma(
      mul(I, eta),
      mul(N, (eta * cosi - k**(1/2)))
    ))
    
def set_current_color(self, r, g, b):
    red = self.clamping(r * 255)
    green = self.clamping(g * 255)
    blue = self.clamping(b * 255)
    self.current_color = color(red, green, blue)


def point(self, x, y):
    if x >= 0 and x < self.width and y >= 0 and y < self.height:
        self.framebuffer[x][y] = self.current_color


def line(self, v1, v2):

    x0 = round(v1.x)
    x1 = round(v2.x)
    y0 = round(v1.y)
    y1 = round(v2.y)

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    # Si es empinado, poco movimiento en x y mucho en y.
    steep = dy > dx

    # Se invierte si es empinado
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    # Si la linea tiene direccion contraria, invertir
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    offset = 0
    threshold = dx
    y = y0

    for x in range(x0, x1 + 1):
        if steep:
            self.point(y, x)
        else:
            self.point(x, y)

        offset += dy * 2

        if offset >= threshold:
            y += 1 if y0 < y1 else -1

            threshold += dx * 2
            
V2 = namedtuple('Vertex2', ['x', 'y'])
V3 = namedtuple('Vertex3', ['x', 'y', 'z'])

