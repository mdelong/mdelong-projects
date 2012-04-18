#
#  scene_gen.py
#  
#  Created by Michael Delong, #0636022, for CIS*4800 Assignment 4
#  
#

from image_gen import *
from image_models import ShapeModel
from image_models import Polygon
from image_utils import *
import math
import sys

showBeforeCulling   = False
showBeforeClipping  = False
showBeforeRendering = False
showFinal           = True

class SceneGen(object):

    def __init__(self, IMG_SIZE=500, ACCURACY=10):
        self.M = IMG_SIZE
        self.s = ACCURACY
        self.models  = []

    def worldToView(self, C):
        O = Vector3(0.0, 0.0, 0.0)
        N = O.subtract(C) # view direction
        
        K     = Vector3(0.0, 1.0, 0.0)
        alpha = K.dot(N)
        KN    = K.multiply(alpha)
        V     = K.subtract(KN)
        
        U = N.cross(V) # right direction

        N.normalize()
        U.normalize()
        V.normalize()

        self.viewSpace = [O, U, V, N]

        T = [[U.x, V.x, N.x, C.x], [U.y, V.y, N.y, C.y], [U.z, V.z, N.z, C.z], [0.0, 0.0, 0.0, 1.0]]
        viewTranslation = invertMatrix(T)
    
        for i in range(0, len(self.models)):
            self.models[i].transformModel(viewTranslation)
    
    """ """
    def rotateObject(self, axis, angle, model):
        affine_matrix = generateAffineMatrix()
        
        sinA = math.sin(math.radians(angle))
        cosA = math.cos(math.radians(angle))
        
        if axis == "x":
            affine_matrix[1][1] = cosA
            affine_matrix[2][1] = sinA
            affine_matrix[1][2] = -sinA
            affine_matrix[2][2] = cosA
            
        elif axis == "y":
            affine_matrix[0][0] = cosA
            affine_matrix[2][0] = -sinA
            affine_matrix[0][2] = sinA
            affine_matrix[2][2] = cosA
            
        elif axis == "z":
            affine_matrix[0][0] = cosA
            affine_matrix[1][0] = sinA
            affine_matrix[0][1] = -sinA
            affine_matrix[1][1] = cosA

        model.transformModel(affine_matrix)
    
    """ """
    def scaleObject(self, x_factor, y_factor, z_factor, model):
        affine_matrix = generateAffineMatrix()
        affine_matrix[0][0] = x_factor
        affine_matrix[1][1] = y_factor
        affine_matrix[2][2] = z_factor
        model.transformModel(affine_matrix)

    """ """
    def translateObject(self, x_factor, y_factor, z_factor, model):
        affine_matrix = generateAffineMatrix()
        affine_matrix[0][3] = x_factor
        affine_matrix[1][3] = y_factor
        affine_matrix[2][3] = z_factor
        model.transformModel(affine_matrix)

    """ """
    def generateScene(self):
        cube1 = ShapeModel("cube", RED)
        cube2 = ShapeModel("cube", GREY)
        cube3 = ShapeModel("cube", GREY)        
        cube4 = ShapeModel("cube", DRED)

        sphere1 = ShapeModel("sphere", YELLOW, self.s)
        sphere2 = ShapeModel("sphere", YELLOW, self.s)      

        cylinder1 = ShapeModel("cylinder", GREY, self.s)
        cylinder2 = ShapeModel("cylinder", GREY, self.s)
        cylinder3 = ShapeModel("cylinder", GREY, self.s)
        cylinder4 = ShapeModel("cylinder", GREY, self.s)
        cylinder5 = ShapeModel("cylinder", BROWN, self.s)
        cylinder6 = ShapeModel("cylinder", GREY, self.s)

        self.scaleObject(5.0, 1.5, 12.0, cube1)
        self.scaleObject(3.5, 0.9, 2.0,  cube2)
        self.scaleObject(3.5, 3.0, 1.0,  cube3)
        self.scaleObject(4.0, 1.5, 1.5,  cube4)

        self.scaleObject(1.0, 1.0, 1.0, sphere1)
        self.scaleObject(1.0, 1.0, 1.0, sphere2)

        self.scaleObject(2.75, 1.0, 2.75, cylinder1)
        self.scaleObject(2.75, 1.0, 2.75, cylinder2)
        self.scaleObject(2.75, 1.0, 2.75, cylinder3)
        self.scaleObject(2.75, 1.0, 2.75, cylinder4)

        self.scaleObject(0.25, 2.5, 0.25, cylinder5)
        self.scaleObject(2.0, 0.5, 2.0,   cylinder6)
        
        self.rotateObject("z", -90.0, cylinder1)
        self.rotateObject("z", 90.0,  cylinder2)
        self.rotateObject("z", -90.0, cylinder3)
        self.rotateObject("z", 90.0,  cylinder4)
        self.rotateObject("x", -35.0, cylinder5)
        self.rotateObject("x", -35.0, cylinder6)

        self.rotateObject("x", 20.0, sphere1)
        self.rotateObject("x", 20.0, sphere2)

        self.translateObject(-2.0, -2.0, 4.0,  cylinder1)
        self.translateObject(2.0, -2.0, 4.0,   cylinder2)
        self.translateObject(-2.0, -2.0, -4.0, cylinder3)
        self.translateObject(2.0, -2.0, -4.0,  cylinder4)
        self.translateObject(0.0, 1.85, 1.0,   cylinder5)
        self.translateObject(0.0, 3.0, 0.2,    cylinder6)

        self.translateObject(0.0, 1.2, -2.0,  cube2)
        self.translateObject(0.0, 2.25, -3.5, cube3)
        self.translateObject(0.0, 1.5, 2.5,   cube4)

        self.translateObject(-2.0, 1.25, 5.5, sphere1)
        self.translateObject(2.0, 1.25, 5.5,  sphere2)
        
        self.models.append(cube1)
        self.models.append(cube2)
        self.models.append(cube3)
        self.models.append(cube4)
        self.models.append(cylinder1)
        self.models.append(cylinder2)
        self.models.append(cylinder3)
        self.models.append(cylinder4)
        self.models.append(cylinder5)
        self.models.append(cylinder6)
        self.models.append(sphere1)
        self.models.append(sphere2)
     
    """ """
    def drawScene(self, C, h, d, f):
        ST = [[d/h, 0.0, 0.0, 0.0], [0.0, d/h, 0.0, 0.0], [0.0, 0.0, f/(f-d), -(f*d)/(f-d)], [0.0, 0.0, 1.0, 0.0]]
        self.worldToView(Vector3(C[0], C[1], C[2]))
        images = [None, None, None, None]
        if showBeforeCulling:   images[0] = ImageGen("scene_beforeculling", self.M)
        if showBeforeClipping:  images[1] = ImageGen("scene_beforeclipping", self.M)
        if showBeforeRendering: images[2] = ImageGen("scene_beforerendering", self.M)
        if showFinal:           images[3] = ImageGen("scene_final", self.M)
        
        if images == [None, None, None, None]:
            print "No stage of the rendering process was selected; program will not produce any output."
            return
        
        for i in range(0, len(self.models)):
            self.models[i].displayModel(ST, h, d, f, images)

        for img in images:
            if img != None: img.saveImage()

C = d = f = h = None
IMG_SIZE, ACCURACY = 500, 10
for arg in sys.argv:
    try:
        if arg.startswith("C="):
            coords = arg[2:]
            if (coords.startswith('(') and coords.endswith(')')):   coords = coords[1 : len(coords)-1]
            coords = coords.split(',')
            C = (float(coords[0]), float(coords[1]), float(coords[2]))
        elif arg.startswith("d="):
            arg = arg[2:]
            d = float(arg)
        elif arg.startswith("f="):
            arg = arg[2:]
            f = float(arg)
        elif arg.startswith("h="):
            arg = arg[2:]
            h = float(arg)
        elif arg.startswith("IMG_SIZE="):
            arg = arg[9:]
            IMG_SIZE = int(arg)
        elif arg.startswith("ACCURACY="):
            arg = arg[9:]
            ACCURACY = int(arg)
    except ValueError:
        print "Error: invalid command line argument."
        print "Usage: python scene_gen.py \"C=(x,y,z)\" d=(float) f=(float) h=(float) [IMG_SIZE=x] [ACCURACY=n]"
        sys.exit(-1)

if d == None:
    print "Error: you must provide a valid camera zoom value."
    print "Usage: python scene_gen.py \"C=(x,y,z)\" d=(float) f=(float) h=(float) [IMG_SIZE=x] [ACCURACY=n]"
    sys.exit(-1)

if h == None:
    print "Error: you must provide a valid camera viewport size."
    print "Usage: python scene_gen.py \"C=(x,y,z)\" d=(float) f=(float) h=(float) [IMG_SIZE=x] [ACCURACY=n]"
    sys.exit(-1)

if f == None:
    print "Error: you must provide a valid camera viewing distance."
    print "Usage: python scene_gen.py \"C=(x,y,z)\" d=(float) f=(float) h=(float) [IMG_SIZE=x] [ACCURACY=n]"
    sys.exit(-1)
if C == None:
    print "Error: you must provide a valid camera location."
    print "Usage: python scene_gen.py \"C=(x,y,z)\" d=(float) f=(float) h=(float) [IMG_SIZE=x] [ACCURACY=n]"
    sys.exit(-1)

while 1:
    ans = raw_input("1. View scene before culling? (y/n): ")
    if ans.strip() == "y":
        showBeforeCulling = True
        break
    elif ans.strip() == "n":
        showBeforeCulling = False
        break

while 1:
    ans = raw_input("2. View scene before clipping? (y/n): ")
    if ans.strip() == "y":
        showBeforeClipping = True
        break
    elif ans.strip() == "n":
        showBeforeClipping = False
        break

while 1:
    ans = raw_input("3. View scene before rendering? (y/n): ")
    if ans.strip() == "y":
        showBeforeRendering = True
        break
    elif ans.strip() == "n":
        showBeforeRendering = False
        break

while 1:
    ans = raw_input("4. View scene after culling, clipping, and rendering? (y/n): ")
    if ans.strip() == "y":
        showFinal = True
        break
    elif ans.strip() == "n":
        showFinal = False
        break

scene = SceneGen(IMG_SIZE, ACCURACY)
scene.generateScene()
scene.drawScene(C, h, d, f)
