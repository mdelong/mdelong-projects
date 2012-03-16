#
#  scene_gen.py
#  
#  Created by Michael Delong, #0636022, for CIS*4800 Assignment 3
#  
#

from image_gen import ImageGen
from image_models import ShapeModel
from image_utils import *
import math
import sys

class SceneGen(object):

    def __init__(self):
        self.myimage = ImageGen() #img_size = 500, PIX_SIZE=4
        self.models  = []
        self.currentSpace = generateAffineMatrix()
        self.worldSpace   = generateAffineMatrix()
        self.viewSpace = []

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
        self.currentSpace = multiplyMatrices(viewTranslation, self.worldSpace)
    
    def viewToScreen(self, f, d):
        ST = [[d/h, 0, 0, 0], [0, d/h, 0, 0], [0, 0, f/(f-d), -(f*d)/(f-d)], [0, 0, 1.0, 0]]
        for m in self.models:
            m.modelToScreen()
        
    def modelsToView(self):
        for m in self.models:
            m.transformModel(self.currentSpace)
            m.objectToWorld()
    
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
    
    def scaleObject(self, x_factor, y_factor, z_factor, model):
        affine_matrix = generateAffineMatrix()
        affine_matrix[0][0] = x_factor
        affine_matrix[1][1] = y_factor
        affine_matrix[2][2] = z_factor
        model.transformModel(affine_matrix)
        
    def translateObject(self, x_factor, y_factor, z_factor, model):
        affine_matrix = generateAffineMatrix()
        affine_matrix[0][3] = x_factor
        affine_matrix[1][3] = y_factor
        affine_matrix[2][3] = z_factor
        model.transformModel(affine_matrix)

    def generateScene(self):
        cube1 = ShapeModel("cube")
        cube2 = ShapeModel("cube")
        cube3 = ShapeModel("cube")        
        cube4 = ShapeModel("cube")

        sphere1 = ShapeModel("sphere")
        sphere2 = ShapeModel("sphere")      

        cylinder1 = ShapeModel("cylinder")
        cylinder2 = ShapeModel("cylinder")
        cylinder3 = ShapeModel("cylinder")
        cylinder4 = ShapeModel("cylinder")
        cylinder5 = ShapeModel("cylinder")
        cylinder6 = ShapeModel("cylinder")
                
        self.rotateObject("z", 20.0, cube1)
        self.scaleObject(5.0, 1.5, 12.0, cube1)
        self.scaleObject(3.5, 0.9, 2.0, cube2)
        self.scaleObject(3.5, 3.0, 1.0, cube3)
        self.scaleObject(4.0, 1.5, 1.5, cube4)

        self.scaleObject(1.0, 1.0, 1.0, sphere1)
        self.scaleObject(1.0, 1.0, 1.0, sphere2)
        
        self.scaleObject(2.75, 1.0, 2.75, cylinder1)
        self.scaleObject(2.75, 1.0, 2.75, cylinder2)
        self.scaleObject(2.75, 1.0, 2.75, cylinder3)
        self.scaleObject(2.75, 1.0, 2.75, cylinder4)
        
        self.scaleObject(0.25, 2.5, 0.25, cylinder5)
        self.scaleObject(2.0, 0.5, 2.0, cylinder6)        
        
        self.rotateObject("z", -90.0, cylinder1)
        self.rotateObject("z", 90.0, cylinder2)
        self.rotateObject("z", -90.0, cylinder3)
        self.rotateObject("z", 90.0, cylinder4)
        self.rotateObject("x", -35.0, cylinder5)
        self.rotateObject("x", -35.0, cylinder6)
        
        self.rotateObject("x", 20.0, sphere1)
        self.rotateObject("x", 20.0, sphere2)

        self.translateObject(-2.0, -2.0, 4.0, cylinder1)
        self.translateObject(2.0, -2.0, 4.0, cylinder2)
        self.translateObject(-2.0, -2.0, -4.0, cylinder3)
        self.translateObject(2.0, -2.0, -4.0, cylinder4)
        self.translateObject(0.0, 1.85, 1.0, cylinder5)
        self.translateObject(0.0, 3.0, 0.2, cylinder6)
        
        self.translateObject(0.0, 1.2, -2.0, cube2)
        self.translateObject(0.0, 2.25, -3.5, cube3)
        self.translateObject(0.0, 1.5, 2.5, cube4)

        self.translateObject(-2.0, 1.25, 5.5, sphere1)
        self.translateObject(2.0, 1.25, 5.5, sphere2)
        
        self.models.append(cylinder1)
        self.models.append(cylinder2)
        self.models.append(cylinder3)
        self.models.append(cylinder4)
        self.models.append(cylinder5)
        self.models.append(cylinder6)
        
        self.models.append(cube1)
        self.models.append(cube2)
        self.models.append(cube3)
        self.models.append(cube4)

        self.models.append(sphere1)
        self.models.append(sphere2)

    
    def projectScene(self, h=2.0, d=1.0, f=30.0):
        projection_M = generateAffineMatrix()
        projection_M[3][2] = float(1.0/d)
        projection_M[3][3] = 0.0
        
        for m in self.models:
            m.cullModel(self.viewSpace[3])
            m.projectModel(projection_M, h, f, d)
                
    def drawScene(self):
        self.worldToView(Vector3(-15.0, 4.0, 2.1))
        self.modelsToView()
        self.projectScene()
        for m in self.models:
            self.myimage.rasterizeModel(m)
        self.myimage.saveImage("scene")
        
scene = SceneGen()
scene.generateScene()
scene.drawScene()
