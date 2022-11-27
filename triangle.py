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
        self.normal = normalize(cross(self.AB, self.AC))
        self.material = material

    def ray_intersect(self, orig, dir):
        # t = - (dot(N, orig) + D) / dot(N, dir)
        denom = dot(self.normal, dir)

        if abs(denom) > 0.0001:

            #Single/Double sided feature
            if dot(dir, self.normal) > 0 and self.isSingleSided:
                return None

            D = dot(self.normal, self.vertA)
            num = (dot(self.normal, orig) + D)
            t = num/denom

            if t > 0:
                hit = add(orig, scalarVec(t, dir))

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
                    # u, v, w = baryCoords(self.vertA, self.vertB, self.vertC, hit)
                    # tx = self.vertA.x * u + self.vertB.x * v + self.vertC.x * w
                    # ty = self.vertA.y * u + self.vertB.y * v + self.vertC.y * w
                    # ¿Por qué dividido 5???????????
                    tx = abs(hit.x / 5)
                    ty = abs(hit.y / 5)
                    #print("TX= ", tx, " - TY= ", ty)

                if tx and ty:
                    uvs = V2(tx, ty)
                else:
                    uvs = None


                return Intersect(
                    distance = t,
                    point = hit,
                    normal = self.normal,
                    texCoords = uvs,
                    sceneObject = self
                )

        return None