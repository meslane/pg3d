import pygame
from math import *
import struct
import sys
import time
import random

def averageOfPoints(points):
    result = point(0,0,0)
    
    for p in points:
        result += p
        
    return result / len(points)
    
def dotProduct(a, b):
    return (a.x * b.x) + (a.y * b.y) + (a.z * b.z)
    
def distance(a, b):
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2 + (b.z - a.z) ** 2)

def orientation(p, q, r): #get orientation of three points
    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    
    if (val > 0):
        return 1 #clockwise
    elif (val < 0):
        return 2 #counterclockwise
    else:
        return 0 #colinear

class camera:
    def __init__(self, position, orientation, surface):
        self.position = position #pinhole
        self.orientation = orientation #angle
        self.surface = surface #film surface RELATIVE TO PINHOLE
        
    def getDistance(self, p):
        return distance(self.position, p)
        
    def getCartOrientation(self): #This works fine I think
        return point(sin(self.orientation[1]) * cos(self.orientation[0]), sin(self.orientation[1]) * sin(self.orientation[0]), cos(self.orientation[1]))

class point: #general 3D coordinate
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def __add__(self, other): #addition/subtraction operators
        return point(self.x + other.x, self.y + other.y, self.z + other.z)
        
    def __sub__(self, other):
        return point(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __truediv__(self, other): #overload operators for scalar multiplication/division
        return point(self.x / other, self.y / other, self.z / other)
        
    def __mul__(self, other):
        return point(self.x * other, self.y * other, self.z * other)
        
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        
        return self
        
    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        
        return self
        
    def __imul__(self, other):
        self.x *= other
        self.y *= other
        self.z *= other
        
        return self
        
    def __itruediv__(self, other):
        self.x /= other
        self.y /= other
        self.z /= other
        
        return self
        
    def __str__(self):
        return "{}, {}, {}".format(self.x, self.y, self.z)
        
    def project(self, camera, xoffset, yoffset): #project point onto 2d camera plane (this formula from wikipedia.org/wiki/3D_projection)
        cx, cy, cz = camera.position.x, camera.position.y, camera.position.z
        thx, thy, thz = camera.orientation[0], camera.orientation[1], camera.orientation[2]
        ex, ey, ez = camera.surface.x, camera.surface.y, camera.surface.z
        
        x = self.x - cx
        y = self.y - cy
        z = self.z - cz
        
        dx = cos(thy) * (sin(thz) * y + cos(thz) * x) - sin(thy) * z
        dy = sin(thx) * (cos(thy) * z + sin(thy) * (sin(thz) * y + cos(thz) * x)) + cos(thx) * (cos(thz) * y - sin(thz) * x)
        dz = cos(thx) * (cos(thy) * z + sin(thy) * (sin(thz) * y + cos(thz) * x)) - sin(thx) * (cos(thz) * y - sin(thz) * x)
        
        bx = (ez/dz) * dx + ex
        by = (ez/dz) * dy + ey
        
        return (xoffset - bx, by + yoffset)
      
class line: #or line
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        
    def draw(self, camera, screen, xoffset, yoffset):
        pr1 = self.p1.project(camera, 0, 0)
        pr2 = self.p2.project(camera, 0, 0)
        pygame.draw.line(screen, (255, 255, 255), (pr1[0] + xoffset, pr1[1] + yoffset), (pr2[0] + xoffset, pr2[1] + yoffset), 1)
        
class point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __str__(self):
        return "({}, {})".format(self.x, self.y)
    
class line2D:
    def __init__(self, p1, p2): #line segment defined by two points
        self.p1 = p1
        self.p2 = p2
        
    def intersects(self, other):
        o1 = orientation(self.p1, self.p2, other.p1)
        o2 = orientation(self.p1, self.p2, other.p2)
        o3 = orientation(other.p1, other.p2, self.p1)
        o4 = orientation(other.p1, other.p2, self.p2)
        
        if ((o1 != o2) and (o3 != o4)):
            return True
        else:
            return False
    
class polygon:
    def __init__(self, normal, pointlist, color):
        self.normal = normal
        self.distace = 0 #scalar distance to camera objet for painter's algorithm
        self.pointlist = pointlist
        
        self.color = color
        
        self.com = averageOfPoints(self.pointlist) #center of mass
        
        self.parent = None #body the polygon belongs to
        
    def move(self, offset):
        for p in self.pointlist:
            p += offset
            
        self.com += offset
        
    def getcom(self): #set center of mass
        self.com = averageOfPoints(self.pointlist)
        return self.com
        
    def rotateX(self, angle): #rotate about X-axis (requires translation to maintain position)
        self.normal = point(self.normal.x, float(self.normal.y * cos(angle) - self.normal.z * sin(angle)), float(self.normal.y * sin(angle) + self.normal.z * cos(angle)))
        for p in self.pointlist:
            ny = float(p.y * cos(angle) - p.z * sin(angle))
            nz = float(p.y * sin(angle) + p.z * cos(angle))
            
            p.y = ny
            p.z = nz
            
        self.getcom()
            
    def rotateY(self, angle):
        self.normal = point(float(self.normal.x * cos(angle) + self.normal.z * sin(angle)), self.normal.y, float(self.normal.z * cos(angle) - self.normal.x * sin(angle)))
        for p in self.pointlist:
            nx = float(p.x * cos(angle) + p.z * sin(angle))
            nz = float(p.z * cos(angle) - p.x * sin(angle))
            
            p.x = nx
            p.z = nz
            
        self.getcom()
            
    def rotateZ(self, angle):
        self.normal = point(float(self.normal.x * cos(angle) - self.normal.y * sin(angle)), float(self.normal.x * sin(angle) + self.normal.y * cos(angle)), self.normal.z)
        for p in self.pointlist:
            nx = float(p.x * cos(angle) - p.y * sin(angle))
            ny = float(p.x * sin(angle) + p.y * cos(angle))
            
            p.x = nx
            p.y = ny
        
        self.getcom()
    
    def facingCamera(self, camera):
        ccart = camera.getCartOrientation()
        if dotProduct(self.normal, ccart) <= 0: #if dot product is negative, surface should be visable
            return True
        else:
            return False
            
    def getDistance(self, camera): #set distance to camera
        self.distance = distance(camera.position, self.com)
        return self.distance
        
    def insidePolygon2D(self, camera, xoffset, yoffset, point): #determine if a 2D point is in the projected polygon (from: https://observablehq.com/@tmcw/understanding-point-in-polygon)
        points2D = [] 
        lines2D = []
        crossings = 0
        
        for p in self.pointlist: #create list of projected points
            points2D.append(point2D(p.project(camera, xoffset, yoffset)[0], p.project(camera, xoffset, yoffset)[1]))
            
        for i in range(len(points2D)):
            if i == 0:
                j = len(points2D) - 1
            else:
                j = i - 1
                
            lines2D.append(line2D(points2D[i], points2D[j])) #get all lines in polygon
             
        ray = line2D(point2D(xoffset, yoffset), point2D(xoffset + 10000, yoffset)) #cast functionally infinite ray
        
        for l in lines2D:
            if ray.intersects(l):
                crossings += 1
            
        return (crossings % 2 != 0)
        
    def drawRaster(self, camera, screen, xoffset, yoffset, cull, shaders): #draw triangle using pygame.draw.polygon()
        numdrawn = 0
        
        ppoints = []
        insideView = False
        ssize = screen.get_size()
        
        for p in self.pointlist: #detect if all points in polygon are out of view
            ppoints.append(p.project(camera, xoffset, yoffset))
            if (ppoints[-1][0] > 0 and ppoints[-1][1] > 0) and (ppoints[-1][0] < ssize[0] and ppoints[-1][1] < ssize[1]):
                insideView = True
            
        if (self.facingCamera(camera) or cull == False) and insideView == True: #draw if not culled and in the camera's FOV
            tcolor = self.color
            if (shaders): #apply shaders
                scalar = 0
                
                for shader in shaders:
                    sangle = -(cos(shader.getAngle(self)) / 2)
                    
                    if sangle >= 0:
                        scalar += sangle
                
                scalar += 0.5
                
                if scalar < 0.5:
                    scalar = 0.5
                    
                tcolor = (floor(self.color[0] * scalar), floor(self.color[1] * scalar), floor(self.color[2] * scalar))
            
            pygame.draw.polygon(screen, tcolor, ppoints)
            numdrawn += 1
            
        return numdrawn
     
class triangle(polygon):
    def __init__(self, normal, p1, p2, p3, color):
        super().__init__(normal, [p1, p2, p3], color)
        
        self.vectlist = []
        self.vectlist.append(line(p1, p2))
        self.vectlist.append(line(p1, p3))
        self.vectlist.append(line(p2, p3))
        
    def drawWireframe(self, camera, screen, xoffset, yoffset):
        for v in self.vectlist:
            v.draw(camera, screen, xoffset, yoffset)
            
class square(polygon):
    def __init__(self, normal, p1, p2, p3, p4, color):
        super().__init__(normal, [p1, p2, p3, p4], color)

class object:
    def __init__(self, plist, color):
        self.plist = plist #list of polygons in body
        self.color = color
        self.com = point(0,0,0) #center of mass
        
    def changeColor(self, newcolor):
        self.color = newcolor
        for p in self.plist:
            p.color = newcolor
            
    def getcom(self):
        comsum = point(0,0,0)
        
        for p in self.plist:
            comsum += p.getcom()
            
        self.com = comsum / len(self.plist)
        
        return self.com
            
    def drawRaster(self, camera, screen, xoffset, yoffset, cull, shader):
        numdrawn = 0
    
        for p in self.plist:
            numdrawn += p.drawRaster(camera, screen, xoffset, yoffset, cull, shader)
            
        return numdrawn
    
    def translate(self, offset): #offset should be a point object
        self.com += offset #move center of mass with offset
        for p in self.plist:
            p.move(offset)
            
    def rotate(self, angles): #arg should be array or tuple of three values
        for p in self.plist:
            p.move(point(-self.com.x,-self.com.y,-self.com.z)) #move center of mass to origin
            p.rotateX(angles[0])
            p.rotateY(angles[1])
            p.rotateZ(angles[2])
            p.move(point(self.com.x,self.com.y,self.com.z)) #move back
            
class cube(object):
    def __init__(self, center, sidelength, color):
        o = sidelength / 2
        
        points = []
        for x in range(2): #procedurally create all points in the cube
            for y in range(2):
                for z in range(2):
                    points.append(center + point(((-1) ** x) * o, ((-1) ** y) * o ,((-1) ** z) * o))
                    
        squares = []
                    
        squares.append(square(point(1, 0, 0), points[0], points[2], points[3], points[1], color)) #constant +x
        squares.append(square(point(-1, 0, 0), points[4], points[6], points[7], points[5], color)) #constant -x
        squares.append(square(point(0, 1, 0), points[0], points[4], points[5], points[1], color)) #constant +y
        squares.append(square(point(0, -1, 0), points[2], points[6], points[7], points[3], color)) #constant -y
        squares.append(square(point(0, 0, 1), points[0], points[4], points[6], points[2], color)) #constant +z
        squares.append(square(point(0, 0, -1), points[1], points[5], points[7], points[3], color)) #constant -z
        
        for s in squares:
            s.parent = self
        
        super().__init__(squares, color)
        self.getcom()

class STLobject(object):
    def __init__(self, filename, color):
        super().__init__([], color)
        self.readSTL(filename)
        
    def readSTL(self, filename): #unpack stl file into object
        try:
            flines = open(filename, 'r').readlines()
        except UnicodeDecodeError:
            flines = [""]
        
        print(flines[0])
        
        normal = point(0,0,0)
        points = []
        psize = 0
        if "solid" in str(flines[0]): #if ASCII file
            for l in flines: 
                if "facet normal" in l:
                    n = l.split()
                    normal = point(float(n[2]), float(n[3]), float(n[4]))
                elif "vertex" in l:
                    v = l.split()
                    p = point(float(v[1]), float(v[2]), float(v[3]))
                    points.append(p)
                    self.com += p
                elif "endfacet" in l:
                    self.plist.append(triangle(normal, points[0], points[1], points[2], color))
                    points.clear()
                    psize += 1
                    
            self.com /= (psize * 3)
    
        else: #if binary instead
            fdata = open(filename, 'rb').read()
            psize = struct.unpack('I', fdata[80:84]) #eat up header and get number of triangles
        
            for i in range(psize[0]):
                entry = struct.unpack('<ffffffffffffH', fdata[84 + 50*i:134 + 50*i])
                self.plist.append(triangle(point(entry[0],entry[1],entry[2]), point(entry[3],entry[4],entry[5]), point(entry[6],entry[7],entry[8]), point(entry[9],entry[10],entry[11]), self.color))
                self.com.x += (entry[3] + entry[6] + entry[9])
                self.com.y += (entry[4] + entry[7] + entry[10])
                self.com.z += (entry[5] + entry[8] + entry[11])
        
            self.com /= (psize[0] * 3)
    
    def drawWireframe(self, camera, screen, xoffset, yoffset):
        for p in self.plist:
            p.drawWireframe(camera, screen, xoffset, yoffset)

class pointSource: #point source of light for shading
    def __init__(self, pos):
        self.pos = pos #point object
        
    def getAngle(self, triangle): #get angle between surface normal and point source
        dv = triangle.getcom() - self.pos
        n = triangle.normal
        
        return acos(dotProduct(n, dv)/(sqrt(dotProduct(dv, dv)) * sqrt(dotProduct(n, n)))) #return angle
        
class scene:
    def __init__(self, screen, camera, objects, lightSources):
        self.screen = screen
        self.camera = camera
        self.objects = objects
        self.lightSources = lightSources
        self.polygons = []
        
        for object in self.objects:
            for p in object.plist:
                self.polygons.append(p)
                

    def drawPaintedRaster(self, cull): #painter's algorithm
        numdrawn = 0
        
        for object in self.objects:
            for p in object.plist:
                p.getDistance(self.camera)
                
        self.polygons.sort(key = lambda x: x.distance, reverse = True) #python's sort method is faster than inorder insertion
     
        for polygon in self.polygons: #draw in order after storting 
            numdrawn += polygon.drawRaster(self.camera, self.screen, int(self.screen.get_width()/2), int(self.screen.get_height()/2), cull, self.lightSources)
        
        return numdrawn