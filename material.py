from lib import *

class Material:
    def __init__(self, diffuse=color(255, 255, 255),  albedo=(1, 0, 0, 0), spec=0,refractive_index=1, texture = None):
        self.diffuse = diffuse
        self.albedo = albedo
        self.spec = spec
        self.refractive_index = refractive_index
        self.texture = texture


class Texture(object):
    def __init__(self, path):
        self.path = path
        self.read()

    def read(self):
        image = open(self.path, 'rb')
        image.seek(10)
        header_size = struct.unpack('=l', image.read(4))[0]

        image.seek(14 + 4)
        self.width = struct.unpack('=l', image.read(4))[0]
        self.height = struct.unpack('=l', image.read(4))[0]
        image.seek(header_size)

        self.framebuffer = []

        for y in range(self.height):
            self.framebuffer.append([])
            for x in range(self.width):
                b = ord(image.read(1)) / 255
                g = ord(image.read(1)) / 255
                r = ord(image.read(1)) / 255
                self.framebuffer[y].append(color(r,g,b))

        image.close()

    def get_color(self, tx, ty):
        if tx >= 0 and tx <= 1 and ty >= 0 and ty <= 1:
            x = int(tx * self.width - 1)
            y = int(ty * self.height - 1)

            return self.framebuffer[y][x]
        else:
            return color(0,0,0)
