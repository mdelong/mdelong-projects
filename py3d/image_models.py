#
#  image_models.py
#  
#  Created by Michael Delong, #0636022, for CIS*4800 Assignment 3
#  This program generates a solid in 3D image space, and then projects it onto a 2D image buffer, 
#  which is saved as a JPEG file.
#

import math
from image_utils import *

class Polygon(object):

    def __init__(self, V, color=RED):
        self.edges    = []
        self.vertices = V
        self.visible  = True
        self.color    = color
        
        numV = len(V)
        for i in range(numV):
            self.edges.append([(i, (i+1) % numV), True])
        self.normal = Vector3(0.0, 0.0, 0.0)
        self.calculateNormal((0.0, 0.0, 0.0))
        
    def calculateNormal(self, origin):
        (V, e1, e2) = (self.vertices, self.edges[0], self.edges[len(self.edges)-1])
        
        (x1, y1, z1) = (V[e1[0][1]][0] - V[e1[0][0]][0], V[e1[0][1]][1] - V[e1[0][0]][1], V[e1[0][1]][2] - V[e1[0][0]][2])
        (x2, y2, z2) = (V[e2[0][0]][0] - V[e2[0][1]][0], V[e2[0][0]][1] - V[e2[0][1]][1], V[e2[0][0]][2] - V[e2[0][1]][2])
        
        (V1, V2) = (Vector3(x1, y1, z1), Vector3(x2, y2, z2))
        self.normal = V2.cross(V1)

        try:
            self.normal.normalize()
        except ZeroDivisionError:
            print ""
            #self.visible = False
        """e = [(len(self.vertices), len(self.vertices)+1), True]
        self.edges.append(e)
        self.vertices.append((self.normal.x, self.normal.y, self.normal.z))"""
            
    def getMaxDistance(self, origin):
        maxdist = 0.0
        for v in self.vertices:
            dist = distance(origin, v)
            if dist > maxdist:  maxdist = dist
        return maxdist
    
    def inPlane(self, point, h, d=0.0, f=1.0):
        return (point[0] >= -h and point[0] <= h and point[1] >= -h and point[1] <= h and point[2] >= d and point [2] <= f)
    
    def calc_intersection(self, edge, h, d=0.0, f=1.0):
        (P, Q) = (edge[0], edge[1])
        PQ = Vector(Q[0] - P[0], Q[1] - P[1], Q[2] - P[2])
        
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

        return (x, y, z)
        
    def clipPolygon(self, h):
        for i in range(len(self.edges)):
            (M, N) = (self.vertices[edges[i][0][0]], self.vertices[edges[i][0][1]])
            (m, n) = (self.inPlane(M, h), self.inPlane(N, h))
            Plist = []
            if m and n:
                Plist.append(N)
            elif m and not n:
                P = self.calc_intersection((N, M))
                Plist.append(P)
            elif not m and n:
                P = self.calc_intersection((M, N))
                Plist.append(P)
                Plist.append(N)
            else:
                self.edges[i].visible = False

class ShapeModel(object):
    
    def __init__(self, shape, s=10, color=RED):
        self.polygons = []
        self.transformMatrix = generateAffineMatrix()
        self.color = color
        self.origin = (0.0, 0.0, 0.0)
        self.radius_bsphere = 0.0
        self.visible = True
        self.clip    = False

        if shape == "cone":
            self.generateCone(s)
        elif shape == "cylinder":
            self.generateCylinder(s)
        elif shape == "cube":
            self.generateCube()
        elif shape == "sphere":
            self.generateSphere(s)
        
    def objectToWorld(self):
        maxdist = 0.0
        coords = [[self.origin[0]], [self.origin[1]], [self.origin[2]], [1.0]]
        coords = self.transformPoint(self.transformMatrix, coords)
        self.origin = (coords[0], coords[1], coords[2])
        
        for i in range(len(self.polygons)):
            P = self.polygons[i]
            for j in range(len(P.vertices)):
                coords = [[P.vertices[j][0]], [P.vertices[j][1]], [P.vertices[j][2]], [1.0]]
                coords = self.transformPoint(self.transformMatrix, coords)
                self.polygons[i].vertices[j] = (coords[0], coords[1], coords[2])
                    
            #self.polygons[i].vertices.append((self.origin[0], self.origin[1], self.origin[2]))
            #self.polygons[i].vertices.append((self.polygons[i].normal.x, self.polygons[i].normal.y, self.polygons[i].normal.z))
        
            dist = self.polygons[i].getMaxDistance(self.origin)
            if (dist > maxdist):    maxdist = dist

        self.radius_bsphere = maxdist
                
    def cullModel(self, N):
        for i in range(len(self.polygons)):
            P = self.polygons[i]
                                                
            res = N.dot(P.normal)
            if res < 0.0:
                self.polygons[i].visible = True
            else:
                self.polygons[i].color = YELLOW
                self.polygons[i].visible = False
    
    def clipModel(self, ST, h, d, f):
        (x, y, z) = (origin[0], origin[1], origin[2])
        (a, r, b) = (d/h, self.radius_bsphere, math.sqrt(d*d + h*h)/h)
        if (z >= (a*x + b*r)) and (z >= -a*x + b*r) and (z >= a*y + b*r) and (z >= -a*y + b*r) and (z >= d+r) and (z <= f-r):
            self.modelToScreen(ST)
            return # bounding sphere is inside view volume
        elif (z <= (a*x - b*r)) or (z <= -a*x - b*r) or (z <= a*y - b*r) or (z <= -a*y - b*r) or (z <= d-r) or (z >= f+r):
            self.visible = False
        else:
            self.modelToScreen(ST)
            for i in range(len(self.polygons)):
                if self.polygons[i].visible:
                    self.polygons[i].clipPolygon(h)


    def transformModel(self, M):
        self.transformMatrix = multiplyMatrices(M, self.transformMatrix)
    
    def modelToScreen(self, ST):
        for i in range(len(self.polygons)):
            P = self.polygons[i]
            for j in range(len(P.vertices)):
                coords = [[P.vertices[j][0]], [P.vertices[j][1]], [P.vertices[j][2]], [1.0]]
                coords = self.transformPoint(PM, coords)
                self.polygons[i].vertices[j] = (coords[0], coords[1], coords[2])
        
    def projectModel(self, PM, h=2.0, f=0.74, d=0.5):
        for i in range(len(self.polygons)):
            P = self.polygons[i]
            if P.visible == True:
                for j in range(len(P.vertices)):
                    coords = [[P.vertices[j][0]], [P.vertices[j][1]], [P.vertices[j][2]], [1.0]]
                    coords = self.transformPoint(PM, coords)
                    
                    (x, y, z) = (coords[0], coords[1], coords[2])

                    if (x >= -h and x <= h) and (y >= -h and y <= h) and (z >= d and z <= f):
                        self.polygons[i].vertices[j] = (x, y, z)
                    else:
                        for k in range(len(P.edges)):
                            e = P.edges[k]
                            if e[0][0] == j or e[0][1] == j:
                                print ""
                                #e[1] = False

    def transformPoint(self, T, point):
        new_point = multiplyMatrices(T, point)
        return (new_point[0][0]/new_point[3][0], new_point[1][0]/new_point[3][0], new_point[2][0]/new_point[3][0], new_point[3][0]/new_point[3][0])

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
        self.polygons.append(Polygon(C1))
        
        #C2.reverse()
        self.polygons.append(Polygon(C2))

        for i in range(0, int(s)):
            self.polygons.append(Polygon([C2[(i+1) % s], C1[(i+1) % s], C1[i], C2[i]]))

    """ Plots the points for a 3D cone with radius r and height h, and s vertices/circle """    
    def generateCone(self, s, r=0.5, h=1.0, origin=(0.0, 0.0, 0.0)):
        
        (y1, y2) = (origin[1] + h/2, origin[1] - h/2)

        tip    = (origin[0], y1, origin[2])
        center = (origin[0], y2, origin[2])
        C = self.generateCircle(center, "xz", r, s)
        C.reverse()
        self.polygons.append(Polygon(C))

        for i in range(0, int(s)):
            self.polygons.append(Polygon([C[(i+1) % s], tip, C[i]]))

    """ Plots the points for a 3D cube with side length = h """
    def generateCube(self, h=1.0, origin=(0.0, 0.0, 0.0)):

        (y1, y2, x1, x2, z1, z2) = (origin[1]+h/2, origin[1]-h/2, origin[0]+h/2, origin[0]-h/2, origin[2]+h/2, origin[2]-h/2)
        
        self.polygons.append(Polygon([(x2, y1, z1), (x2, y1, z2), (x1, y1, z2), (x1, y1, z1)]))
        self.polygons.append(Polygon([(x2, y2, z1), (x1, y2, z1), (x1, y2, z2), (x2, y2, z2)]))
        
        self.polygons.append(Polygon([(x1, y2, z1), (x1, y1, z1), (x1, y1, z2), (x1, y2, z2)]))
        self.polygons.append(Polygon([(x2, y2, z2), (x2, y1, z2), (x2, y1, z1), (x2, y2, z1)]))
        
        self.polygons.append(Polygon([(x2, y2, z1), (x2, y1, z1), (x1, y1, z1), (x1, y2, z1)]))
        self.polygons.append(Polygon([(x1, y2, z2), (x1, y1, z2), (x2, y1, z2), (x2, y2, z2)]))
    

    """ Plots the points for a 3D sphere with radius r and s vertices/circle """
    def generateSphere(self, s, r=0.5, origin=(0.0, 0.0, 0.0)):
        
        C = self.generateCircle(origin, "xy", r, s)
        #self.polygons.append(Polygon(C))                        
        mid = int(s/2)
        
        (prevC1, prevC2) = (C, C)
        for i in range(int(s/2)+1):
            rad    = math.fabs(C[i][0] - origin[0])
            center = (origin[0], C[i][1], origin[2])
            
            C1 = self.generateCircle(center, "xz", rad, s)
            #self.polygons.append(Polygon(C1))

            rad    = math.fabs(C[int(s) - i - 1][0] - origin[0])
            center = (origin[0], C[int(s) - i - 1][1], origin[2])

            C2 = self.generateCircle(center, "xz", rad, s)
            #self.polygons.append(Polygon(C2.reverse()))
            
            if i > 0:
                for j in range(s):
                    self.polygons.append(Polygon([prevC1[(j+1) % s], C1[(j+1) % s], C1[j], prevC1[j]]))
                    self.polygons.append(Polygon([C2[(j+1) % s], prevC2[(j+1) % s], prevC2[j], C2[j]]))

            (prevC1, prevC2) = (C1, C2)
