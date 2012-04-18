#
#  image_models.py
#  
#  Created by Michael Delong, #0636022, for CIS*4800 Assignment 4
#  This program generates a solid in 3D image space, and then projects it onto a 2D image buffer, 
#  which is saved as a JPEG file.
#

import math
from image_utils import *

class Polygon(object):

    """ """
    def __init__(self, V, color=RED):
        self.edges        = []
        self.vertices     = V
        self.color        = color
        self.segment_list = []

        numV = len(V)
        for i in range(numV):
            self.edges.append([(i, (i+1) % numV), True])

        self.calculateNormal()
    
    """ """
    def calculateNormal(self):
        (V, e1, e2) = (self.vertices, self.edges[0], self.edges[len(self.edges)-1])

        (x1, y1, z1) = (V[e1[0][1]][0] - V[e1[0][0]][0], V[e1[0][1]][1] - V[e1[0][0]][1], V[e1[0][1]][2] - V[e1[0][0]][2])
        (x2, y2, z2) = (V[e2[0][0]][0] - V[e2[0][1]][0], V[e2[0][0]][1] - V[e2[0][1]][1], V[e2[0][0]][2] - V[e2[0][1]][2])

        (V1, V2) = (Vector3(x1, y1, z1), Vector3(x2, y2, z2))
        self.normal = V2.cross(V1)

        try:
            self.normal.normalize()
        except ZeroDivisionError:
            print "normalize zero division"
        """e = [(len(self.vertices), len(self.vertices)+1), True]
        self.edges.append(e)
        self.vertices.append((self.normal.x, self.normal.y, self.normal.z))"""
    
    """ """
    def getMaxDistance(self, origin):
        maxdist = 0.0
        for v in self.vertices:
            dist = distance(origin, v)
            if dist > maxdist:  maxdist = dist
        return maxdist

    """ """
    def inPlane(self, point, h, d=0.0, f=1.0):
        return (point[0] >= -h and point[0] <= h and point[1] >= -h and point[1] <= h and point[2] >= d and point [2] <= f)

    """ """
    def calc_intersection(self, edge, h, d=0.0, f=1.0):
        (P, Q) = (edge[0], edge[1])
        PQ = Vector3(Q[0] - P[0], Q[1] - P[1], Q[2] - P[2])

        try:
            if P[0] < -h:
                (l, x) = ((-h - P[0])/PQ.x, -h)
                (y, z) = ((PQ.y * l) + P[1], (PQ.z * l) + P[2])
            elif P[0] > h:
                (l, x) = ((h - P[0])/PQ.x, h)
                (y, z) = ((PQ.y * l) + P[1], (PQ.z * l) + P[2])
            elif P[1] < -h:
                (l, y) = ((-h - P[1])/PQ.y, -h)
                (x, z) = ((PQ.x * l) + P[0], (PQ.z * l) + P[2])
            elif P[1] > h:
                (l, y) = ((h - P[1])/PQ.y, h)
                (x, z) = ((PQ.x * l) + P[0], (PQ.z * l) + P[2])
            elif P[2] < d:
                (l, z) = ((d - P[2])/PQ.z, d)
                (x, y) = ((PQ.x * l) + P[0], (PQ.y * l) + P[1])
            elif P[2] > f:
                (l, z) = ((f - P[2])/PQ.z, f)
                (x, y) = ((PQ.x * l) + P[0], (PQ.y * l) + P[1])
        except ZeroDivisionError:
            return None
        if l < 0.0 or l > 1.0:  return None
        return (x, y, z)

    """ """
    def isBackface(self):
        N = Vector3(self.vertices[0][0], self.vertices[0][1], self.vertices[0][2])
        return (self.normal.dot(N) >= 0.0)
    
    """ """
    def transformPolygon(self, T):
        for i in range(0, len(self.vertices)):
            V     = [[self.vertices[i][0]], [self.vertices[i][1]], [self.vertices[i][2]], [1.0]]
            V_new = multiplyMatrices(T, V)

            if V_new[3][0] == 0.0:  V_new[3][0] = 1.0
            self.vertices[i] = (V_new[0][0]/V_new[3][0], V_new[1][0]/V_new[3][0], V_new[2][0]/V_new[3][0])        

    """ """
    def transformNormal(self, T):
        V_coord = [[self.normal.x], [self.normal.y], [self.normal.z], [1.0]]
        V_new   = multiplyMatrices(T, V_coord)
        self.normal = Vector3(V_new[0][0]/V_new[3][0], V_new[1][0]/V_new[3][0], V_new[2][0]/V_new[3][0])
        self.normal.normalize()

    """ """
    def isBoundingBoxInside(self):
        (xmin, ymin, zmin) = (self.vertices[0][0], self.vertices[0][1], self.vertices[0][2])
        (xmax, ymax, zmax) = (xmin, ymin, zmin)

        for v in self.vertices:
            if v[0] < xmin: xmin = v[0]
            if v[0] > xmax: xmax = v[0]
            if v[1] < ymin: ymin = v[1]
            if v[1] > ymax: ymax = v[1]
            if v[2] < zmin: zmin = v[2]
            if v[2] > zmax: zmax = v[2]

        return ((-1.0 <= xmin) or (xmax <= 1.0) or (-1.0 <= ymin) or (ymax <= 1.0) or (0.0 <= zmin) or (zmax <= 1.0))

    """ """
    def clipPolygon(self):
        V = []
        for i in range(len(self.edges)):
            h = 1.0
            nvert = len(self.vertices)
            (M, N) = (self.vertices[self.edges[i][0][0]], self.vertices[self.edges[i][0][1]])
            (m, n) = (self.inPlane(M, h), self.inPlane(N, h))

            if m and n:
                V.append(M)
                V.append(N)
            elif m and not n:
                P = self.calc_intersection((N, M), h)
                if P != None:
                    V.append(M)
                    V.append(P)

            elif not m and n:
                P = self.calc_intersection((M, N), h)
                if P != None:
                    V.append(P)
                    V.append(N)
            else:
                P = self.calc_intersection((M, N), h)
                Q = self.calc_intersection((N, M), h)
                if P != None and Q != None:
                    V.append(P)
                    V.append(Q)

        self.vertices = V
        self.edges = []
        for i in range(0, len(self.vertices)):
            self.edges.append([(i, (i+1) % len(self.vertices)), True])

class ShapeModel(object):

    """ """
    def __init__(self, shape, color=RED, s=10):
        self.polygons = []
        self.transformMatrix = None
        self.color = color
        self.origin_bsphere = (0.0, 0.0, 0.0)
        self.radius_bsphere = 0.0

        if shape == "cone":
            self.generateCone(s)
        elif shape == "cylinder":
            self.generateCylinder(s)
        elif shape == "cube":
            self.generateCube()
        elif shape == "sphere":
            self.generateSphere(s)

    """ """
    def objectToView(self):
        maxdist = 0.0
        coords  = [[self.origin_bsphere[0]], [self.origin_bsphere[1]], [self.origin_bsphere[2]], [1.0]]
        O_new   = multiplyMatrices(self.transformMatrix, coords)
        self.origin_bsphere = (O_new[0][0]/O_new[3][0], O_new[1][0]/O_new[3][0], O_new[2][0]/O_new[3][0])

        for i in range(len(self.polygons)):
            self.polygons[i].transformPolygon(self.transformMatrix)

            VT = [self.transformMatrix[0][0:], self.transformMatrix[1][0:], self.transformMatrix[2][0:], self.transformMatrix[3][0:]]
            (VT[0][3], VT[1][3], VT[2][3], VT[3][3]) = (0.0, 0.0, 0.0, 1.0)
            self.polygons[i].transformNormal(VT)

            """self.polygons[i].vertices.append((self.origin_bsphere[0], self.origin_bsphere[1], self.origin_bsphere[2]))
            self.polygons[i].vertices.append((self.polygons[i].normal.x, self.polygons[i].normal.y, self.polygons[i].normal.z))"""

            dist = self.polygons[i].getMaxDistance(self.origin_bsphere)
            if (dist > maxdist):    maxdist = dist

        self.radius_bsphere = maxdist

    """ """
    def displayModel(self, ST, h, d, f, images):
        self.objectToView()
        result = self.checkBoundingSphere(h, d, f)
        if result   == "OUTSIDE":   return
        elif result == "INSIDE":    clipping = False
        else:
            clipping = True

        for i in range(len(self.polygons)):
            if (self.polygons[i].isBackface()):
                if images[0] != None:
                    self.polygons[i].transformPolygon(ST)
                    images[0].zBuffer(self.polygons[i], False)
                continue

            self.polygons[i].transformPolygon(ST) # to screen space
            
            if images[0] != None:   images[0].zBuffer(self.polygons[i], False)
            if images[1] != None:   images[1].zBuffer(self.polygons[i], False)
                
            if clipping == True:
                if (self.polygons[i].isBoundingBoxInside() == False):
                    continue
                else:
                    self.polygons[i].clipPolygon()

            if images[2] != None:   images[2].zBuffer(self.polygons[i], False)
            if images[3] != None:   images[3].zBuffer(self.polygons[i], True)

    """ """
    def checkBoundingSphere(self, h, d, f):
        (x, y, z) = (self.origin_bsphere[0], self.origin_bsphere[1], self.origin_bsphere[2])
        (a, r, b) = (d/h, self.radius_bsphere, math.sqrt(d*d + h*h)/h)
        if (z >= (a*x + b*r)) and (z >= -a*x + b*r) and (z >= a*y + b*r) and (z >= -a*y + b*r) and (z >= d+r) and (z <= f-r):
            return "INSIDE"
        elif (z <= (a*x - b*r)) or (z <= -a*x - b*r) or (z <= a*y - b*r) or (z <= -a*y - b*r) or (z <= d-r) or (z >= f+r):
            return "OUTSIDE"
        else:
            return "INTERSECT"

    """ """
    def transformModel(self, M):
        if self.transformMatrix == None:
            self.transformMatrix = [M[0][0:], M[1][0:], M[2][0:], M[3][0:]]
        else:
            self.transformMatrix = multiplyMatrices(M, self.transformMatrix)

    """ Generates a circle with radius r and s vertices in the specified plane """     
    def generateCircle(self, origin, plane, r, s):
        V = []
        for i in range(0, int(s)):
            angle = i * 2.0 * math.pi / s

            (x, y, z) = (origin[0], origin[1], origin[2])

            if plane   == "xy":
                x = (math.cos(angle) * r) + x
                y = (math.sin(angle) * r) + y
            elif plane == "xz":
                x = (math.cos(angle) * r) + x
                z = (math.sin(angle) * r) + z
            elif plane == "yz":
                y = (math.cos(angle) * r) + y
                z = (math.sin(angle) * r) + z

            V.append((x, y, z))

        return V

    """ Plots the points for a 3D cylinder with radius r and height h, and s vertices/circle """    
    def generateCylinder(self, s, r=0.5, h=1.0, origin=(0.0, 0.0, 0.0)):

        (y1, y2) = (origin[1] + h/2, origin[1] - h/2)

        C1 = self.generateCircle((origin[0], y1, origin[2]), "xz", r, s)
        C2 = self.generateCircle((origin[0], y2, origin[2]), "xz", r, s)

        for i in range(0, int(s)):
            self.polygons.append(Polygon([C2[(i+1) % s], C1[(i+1) % s], C1[i], C2[i]], self.color))

        C2.reverse()
        self.polygons.append(Polygon(C1, self.color))
        self.polygons.append(Polygon(C2, self.color))

    """ Plots the points for a 3D cone with radius r and height h, and s vertices/circle """    
    def generateCone(self, s, r=0.5, h=1.0, origin=(0.0, 0.0, 0.0)):

        (y1, y2) = (origin[1] + h/2, origin[1] - h/2)

        tip    = (origin[0], y1, origin[2])
        center = (origin[0], y2, origin[2])
        C = self.generateCircle(center, "xz", r, s)
        C.reverse()
        self.polygons.append(Polygon(C, self.color))

        for i in range(0, int(s)):
            self.polygons.append(Polygon([C[(i+1) % s], tip, C[i]], self.color))

    """ Plots the points for a 3D cube with side length = h """
    def generateCube(self, h=1.0, origin=(0.0, 0.0, 0.0)):

        (y1, y2, x1, x2, z1, z2) = (origin[1]+h/2, origin[1]-h/2, origin[0]+h/2, origin[0]-h/2, origin[2]+h/2, origin[2]-h/2)

        self.polygons.append(Polygon([(x2, y1, z1), (x2, y1, z2), (x1, y1, z2), (x1, y1, z1)], self.color))
        self.polygons.append(Polygon([(x2, y2, z1), (x1, y2, z1), (x1, y2, z2), (x2, y2, z2)], self.color))

        self.polygons.append(Polygon([(x1, y2, z1), (x1, y1, z1), (x1, y1, z2), (x1, y2, z2)], self.color))
        self.polygons.append(Polygon([(x2, y2, z2), (x2, y1, z2), (x2, y1, z1), (x2, y2, z1)], self.color))

        self.polygons.append(Polygon([(x2, y2, z1), (x2, y1, z1), (x1, y1, z1), (x1, y2, z1)], self.color))
        self.polygons.append(Polygon([(x1, y2, z2), (x1, y1, z2), (x2, y1, z2), (x2, y2, z2)], self.color))
    

    """ Plots the points for a 3D sphere with radius r and s vertices/circle """
    def generateSphere(self, s, r=0.5, origin=(0.0, 0.0, 0.0)):

        C = self.generateCircle(origin, "xy", r, s)
        mid = int(s/2)

        (prevC1, prevC2) = (C, C)
        for i in range(int(s/2)+1):
            rad    = math.fabs(C[i][0] - origin[0])
            center = (origin[0], C[i][1], origin[2])

            C1 = self.generateCircle(center, "xz", rad, s)

            rad    = math.fabs(C[int(s) - i - 1][0] - origin[0])
            center = (origin[0], C[int(s) - i - 1][1], origin[2])

            C2 = self.generateCircle(center, "xz", rad, s)

            if i > 0:
                for j in range(s):
                    self.polygons.append(Polygon([prevC1[(j+1) % s], C1[(j+1) % s], C1[j], prevC1[j]], self.color))
                    self.polygons.append(Polygon([C2[(j+1) % s], prevC2[(j+1) % s], prevC2[j], C2[j]], self.color))

            (prevC1, prevC2) = (C1, C2)
