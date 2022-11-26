class Material:
    def __init__(self, diffuse,  albedo=(1, 0), spec=0):
        self.diffuse = diffuse
        self.albedo = albedo
        self.spec = spec