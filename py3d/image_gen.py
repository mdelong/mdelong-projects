#
#  image_gen.py
#  
#  Created by Michael Delong, #0636022, for CIS*4800 Assignment 4
#  This program generates a solid in 3D image space, and then projects it onto a 2D image buffer, 
#  which is saved as a JPEG file.
#

from PIL import Image
from image_utils import *

class ImageGen(object):

    """ Constructor for class """
    def __init__(self, name, size=500): #default IMG_SIZE=500
        self.M       = size
        self.name    = name
        self.ZBuffer = [[1.0 for i in range(self.M)] for j in range(self.M)]
        self.image_buffer = Image.new("RGB", (self.M, self.M), BLACK)
    
    """ """
    def shading(self, x, y, color):
        try:
            self.image_buffer.putpixel((int(x), int(y)), color)
        except IndexError:
            return
    
    """ """
    def zBuffer(self, P, rasterizePolygons):
        segment_dict = self.rasterizeEdges(P, not rasterizePolygons)
        
        if rasterizePolygons == True:
            segment_list = [s for s in segment_dict.iteritems()]

            segment_list.sort(key=lambda s: s[0])        
            for i in range(len(segment_list)):
                y, startx, endx = segment_list[i][0], segment_list[i][1][0], segment_list[i][1][1]
                
                try:
                    z, m = startx[1], float(endx[1] - startx[1])/float(endx[0] - startx[0])
                except ZeroDivisionError:
                    m, z = 0.0, startx[1]
                
                else:
                    if (startx[0] == endx[0]):
                        x = startx[0]
                        if z < self.ZBuffer[x][y]:
                            self.shading(x, y, P.color)
                            self.ZBuffer[x][y] = z
                    else:
                        for x in range(startx[0], endx[0]):
                            if z < self.ZBuffer[x][y]:
                                self.shading(x, y, P.color)
                                self.ZBuffer[x][y] = z
                            z += m

    """ """
    def rasterizeEdges(self, P, showEdges):
        rasterized_points = {}
        for edge in P.edges:
            if edge[1] == True:
                (v1, v2) = (self.roundPoint(P.vertices[edge[0][0]]), self.roundPoint(P.vertices[edge[0][1]]))
                x1, x2, y1, y2, z1, z2 = v1[0], v2[0], v1[1], v2[1], v1[2], v2[2]
                
                if (abs(x2 - x1) < abs(y2 - y1)): # go row-by-row
                    if (y1 > y2):
                        starty, endy, x, z = v2, v1, x2, z2
                    else:
                        starty, endy, x, z = v1, v2, x1, z1
                    
                    m    = float(endy[0] - starty[0])/abs(float(endy[1] - starty[1]))
                    zinc = float(endy[2] - starty[2])/abs(float(endy[1] - starty[1]))

                    for y in range(starty[1], endy[1]):
                        if showEdges == True:
                            self.shading(x, y, P.color)
                        else:
                            p = rasterized_points.get(y)
                            if p == None:
                                rasterized_points[y] = [(int(x), z), (int(x), z)]
                            else:
                                if (x < p[0][0]):  p[0] = (int(x), z)
                                if (x > p[1][0]):  p[1] = (int(x), z)
                                rasterized_points[y] = p
                        
                        x += m
                        z += zinc
                
                else: #column-by-column
                    try:
                        if (x1 > x2):
                            startx, endx, y, z = v2, v1, y2, z2
                        else:
                            startx, endx, y, z = v1, v2, y1, z1

                        m    = float(endx[1] - startx[1])/abs(float(endx[0] - startx[0]))
                        zinc = float(endx[2] - startx[2])/abs(float(endx[0] - startx[0]))
                    
                        for x in range(startx[0], endx[0]):
                            if showEdges == True:
                                self.shading(x, y, P.color)
                            else:
                                p = rasterized_points.get(int(y))
                                if p == None:
                                    rasterized_points[int(y)] = [(int(x), z), (int(x), z)]
                                else:
                                    if (x < p[0][0]):  p[0] = (int(x), z)
                                    if (x > p[1][0]):  p[1] = (int(x), z)
                                    rasterized_points[int(y)] = p
                            
                            y += m
                            z += zinc
                    
                    except ZeroDivisionError: # edge is a horizontal line
                        if showEdges == True:
                            for x in range(startx[0], endx[0]): self.shading(x, y, P.color)
                        else:
                            p = rasterized_points.get(y)
                            if p == None:
                                rasterized_points[y] = [(startx[0], startx[2]), (endx[0], endx[2])]
                            else:
                                if (startx[0] < p[0][0]):  p[0] = (startx[0], startx[2])
                                if (endx[0] > p[1][0]):    p[1] = (endx[0], endx[2])
                                rasterized_points[y] = p

        return rasterized_points
    
    """ Translates a vertex from the (x, y, z) coordinate space to its x,y coordinates in the image buffer """
    def roundPoint(self, coords, plane="xy"):
        if plane == "xy":
            xratio = (coords[0] + 1.0)/2.0
            yratio = (-coords[1] + 1.0)/2.0
            x = int(self.M * xratio)
            y = int(self.M * yratio)
            return (x, y, coords[2])
            
        elif plane == "xz":
            xratio = (coords[0] + 1.0)/2.0
            zratio = (coords[2] + 1.0)/2.0
            x = int(self.M * xratio)
            z = int(self.M * zratio)
            return (x, coords[1], z)
            
        elif plane == "yz":
            yratio = (coords[1] + 1.0)/2.0
            zratio = (coords[2] + 1.0)/2.0
            y = int(self.M * yratio)
            z = int(self.M * zratio)
            return (coords[0], y, z)

        return (0, 0)
    
    """ """
    def saveImage(self):
        self.image_buffer.save(self.name + ".jpg", "JPEG")

