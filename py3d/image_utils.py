#
#  image_utils.py
#  
#  Created by Michael Delong, #0636022, for CIS*4800 Assignment 4
#  This program includes various utilities which are useful when working with 3D models and 
#  coordinate systems
#

import math

""" Constant RGB color values """
BLACK  = (0,0,0)
RED    = (255,0,0)
BROWN  = (51, 0, 0)
DRED   = (102,0,0)
YELLOW = (255,255,0)
GREY   = (49, 79, 79)
NAVY   = (0, 0, 51)


""" """
def distance(P1, P2):
    return math.sqrt((math.pow((P2[0] - P1[0]), 2.0) + math.pow((P2[1] - P1[1]), 2.0) + math.pow((P2[2] - P1[2]), 2.0)))

""" """
def generateAffineMatrix():
    new_matrix = [[0.0 for row in range(4)] for col in range(4)]
    for i in range(4):
        new_matrix[i][i] = 1.0
    return new_matrix

""" """
def zeroMatrix(m, n):
    new_matrix = [[0.0 for row in range(n)] for col in range(m)]
    return new_matrix

""" """
def multiplyMatrices(matrix_A, matrix_M):
    if (len(matrix_A[0]) != len(matrix_M)):
        return matrix_A
    else:
        new_matrix = zeroMatrix(len(matrix_A), len(matrix_M[0]))
        for i in range(len(matrix_A)):
            for j in range(len(matrix_M[0])):
                for k in range(len(matrix_A[0])):
                    new_matrix[i][j] += matrix_A[i][k] * matrix_M[k][j]
        return new_matrix

""" return the inverse of the matrix M """
def invertMatrix(M):
    #clone the matrix and append the identity matrix
    # [int(i==j) for j in range_M] is nothing but the i(th row of the identity matrix
    m2 = [row[:]+[int(i==j) for j in range(len(M) )] for i,row in enumerate(M) ]
    # extract the appended matrix (kind of m2[m:,...]
    return [row[len(M[0]):] for row in m2] if gaussJordan(m2) else M  

"""Puts given matrix (2D array) into the Reduced Row Echelon Form.
 Returns True if successful, False if 'm' is singular.
 NOTE: make sure all the matrix items support fractions! Int matrix will NOT work!
 Written by Jarno Elonen in April 2005, released into Public Domain"""
def gaussJordan(m, eps = 1.0/(10**10)):
    (h, w) = (len(m), len(m[0]))
    for y in range(0,h):
        maxrow = y
        for y2 in range(y+1, h):    # Find max pivot
            if abs(m[y2][y]) > abs(m[maxrow][y]):
                maxrow = y2

        (m[y], m[maxrow]) = (m[maxrow], m[y])
        if abs(m[y][y]) <= eps:     # Singular?
            return False

        for y2 in range(y+1, h):    # Eliminate column y
            c = m[y2][y] / m[y][y]
            for x in range(y, w):
                m[y2][x] -= m[y][x] * c

    for y in range(h-1, 0-1, -1): # Backsubstitute
        c  = m[y][y]
        for y2 in range(0,y):
            for x in range(w-1, y-1, -1):
                m[y2][x] -=  m[y][x] * m[y2][y] / c
        m[y][y] /= c
        for x in range(h, w):       # Normalize row y
            m[y][x] /= c
    return True


class Vector3(object):
    
    def __init__(self, x1, y1, z1):
        self.x = float(x1)
        self.y = float(y1)
        self.z = float(z1)
        self.magnitude = self.calcMagnitude(self)

    def cross(self, V):
        newX = self.y * V.z - self.z * V.y
        newY = self.z * V.x - self.x * V.z
        newZ = self.x * V.y - self.y * V.x
        return Vector3(newX, newY, newZ)

    def subtract(self, V):
        return Vector3(self.x - V.x, self.y - V.y, self.z - V.z)

    def add(self, V):
        return Vector3(self.x + V.x, self.y + V.y, self.z + V.z)

    def dot(self, V):
        return self.x * V.x + self.y * V.y + self.z * V.z
    
    def multiply(self, a):
        return Vector3(self.x * a, self.y * a, self.z * a)

    def calcMagnitude(self, V):
        return math.sqrt(self.dot(V))
        
    def normalize(self):
        self.x /= self.magnitude
        self.y /= self.magnitude
        self.z /= self.magnitude
        self.magnitude = self.calcMagnitude(self)
        
    def getAngle(self, V):
        invCos = self.dot(V)/(self.magnitude * V.magnitude)
        if invCos >= 1.0:
            return math.acos(1.0)
        elif invCos <= -1.0:
            return math.acos(-1.0)
        else:
            return math.acos(invCos)

