#
#  image_gen.py
#  
#  Created by Michael Delong, #0636022, for CIS*4800 Assignment 3
#  This program generates a solid in 3D image space, and then projects it onto a 2D image buffer, 
#  which is saved as a JPEG file.
#

from PIL import Image
from image_utils import *

class ImageGen(object):

    """ Constructor for class """
    def __init__(self, size=500, pix_size=2): #default IMG_SIZE=500, PIX_SIZE=4
        self.M = size
        self.PIX_SIZE = pix_size
        self.image_buffer = Image.new("RGB", (self.M * self.PIX_SIZE, self.M * self.PIX_SIZE), BLACK)

    """ Fills a point in the image buffer with the specified color"""
    def fillPoint(self, x, y, color):
        for i in range(self.PIX_SIZE):
            for j in range (self.PIX_SIZE):
                try:
                    self.image_buffer.putpixel((x+i, y+j), color)
                except IndexError:
                    continue
            
    """ Draw edges between connected vertices in the image buffer """
    def rasterizeEdges(self, model):
    
        for P in model.polygons:
            print P.visible
            if P.visible == True:
                for edge in P.edges:
                    if edge[1] == True:
                        v1 = self.roundPoint(P.vertices[edge[0][0]], "xy")
                        v2 = self.roundPoint(P.vertices[edge[0][1]], "xy")
                        x1, x2, y1, y2 = v1[0], v2[0], v1[1], v2[1]
                        
                        if (abs(x2 - x1) < abs(y2 - y1)):
                            m = float(x2 - x1)/abs(float(y2 - y1))
                            x, inc = x1, 1
                            if (y1 > y2):   inc = -1
                            for y in range(y1, y2, inc):
                                self.fillPoint(int(x), int(y), RED)
                                x += m
                        else:
                            try:
                                y, inc = y1, 1
                                m = float(y2 - y1)/abs(float(x2 - x1))
                                if (x1 > x2):   inc = -1
                                for x in range(x1, x2, inc):
                                    self.fillPoint(int(x), int(y), P.color)
                                    y += m

                            except ZeroDivisionError: # edge is a horizontal line
                                for x in range (x1, x2, inc):
                                    self.fillPoint(int(x), v1[1], RED) # edges are drawn in red"""
                        
                        self.fillPoint(v1[0], v1[1], YELLOW) # vertices are drawn in yellow
                        self.fillPoint(v2[0], v2[1], YELLOW)
    
    """ Translates a vertex from the (x, y, z) coordinate space to its x,y coordinates in the image buffer """
    def roundPoint(self, coords, plane="xy"):
        
        if plane == "xy":
            xratio = (coords[0] + 1.0)/2.0
            yratio = (-coords[1] + 1.0)/2.0
            x = int(self.M * xratio * self.PIX_SIZE)
            y = int(self.M * yratio * self.PIX_SIZE)
            return (x, y)
            
        elif plane == "xz":
            xratio = (coords[0] + 1.0)/2.0
            zratio = (coords[2] + 1.0)/2.0
            x = int(self.M * xratio * self.PIX_SIZE)
            z = int(self.M * zratio * self.PIX_SIZE)
            return (x, z)
            
        elif plane == "yz":
            yratio = (coords[1] + 1.0)/2.0
            zratio = (coords[2] + 1.0)/2.0
            y = int(self.M * yratio * self.PIX_SIZE)
            z = int(self.M * zratio * self.PIX_SIZE)
            return (y, z)

        return (0, 0)

    def rasterizeModel(self, model):
        self.rasterizeEdges(model)
       
    def saveImage(self, filename):
        self.image_buffer.save(filename + ".jpg", "JPEG")

