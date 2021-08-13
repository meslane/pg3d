import pygame
from math import *
import struct
import sys
import time
import random
import threading

import pg3d

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("3D Demo")
    screen = pygame.display.set_mode([1280,720], pygame.RESIZABLE)
    
    pfont = pygame.font.SysFont("Consolas", 14)
    bfont = pygame.font.SysFont("Arial", 32)
    
    cam = pg3d.camera(pg3d.point(0,0, -75), [0,0,0], pg3d.point(0,0,1000))
    
    blist = []
    light = []
    
    light.append(pg3d.pointSource(pg3d.point(100000,0,0)))
    blist.append(pg3d.STLobject("shiba_inu_dog_low_poly.stl", (255, 255, 255)))
    
    s = pg3d.scene(screen, cam, blist, light)
    
    motionMatrix = { # 1 = in direction, -1 opposite direction, 0 = no motion
        "forward": 0,
        "lateral": 0,
        "vertical": 0,
        "rotational": 0
    }
    
    fps = 0
    mspeeed = 2
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    locked = True
    while True:
        startloop = time.time()
    
        mxcenter = int(screen.get_width()/2)
        mycenter = int(screen.get_height()/2)
    
        if locked:
            pygame.mouse.set_pos(mxcenter,mycenter)
            
            m = pygame.mouse.get_rel()
            
            if m[0] != 0 and abs(m[0]) < 300: #if the mouse moved, move camera
                cam.orientation[1] -= radians(m[0]/10)
            if m[1] != 0 and abs(m[1]) < 300:
                cam.orientation[0] -= radians(m[1]/10)
    
        for event in pygame.event.get(): #pygame event detection
            if event.type == pygame.QUIT:
                run = False
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    locked = False
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    
                if event.key == pygame.K_SPACE and winner != None:
                    run = False
            
                if event.key == pygame.K_w:
                    motionMatrix["forward"] = 1 * mspeeed
                elif event.key == pygame.K_s:
                    motionMatrix["forward"] = -1 * mspeeed
                elif event.key == pygame.K_a:
                    motionMatrix["lateral"] = 1 * mspeeed
                elif event.key == pygame.K_d:
                    motionMatrix["lateral"] = -1 * mspeeed
                elif event.key == pygame.K_r:
                    motionMatrix["vertical"] = -1 * mspeeed
                elif event.key == pygame.K_f:
                    motionMatrix["vertical"] = 1 * mspeeed
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    motionMatrix["forward"] = 0
                elif event.key == pygame.K_s:
                    motionMatrix["forward"] = 0
                elif event.key == pygame.K_a:
                    motionMatrix["lateral"] = 0
                elif event.key == pygame.K_d:
                    motionMatrix["lateral"] = 0
                elif event.key == pygame.K_r:
                    motionMatrix["vertical"] = 0
                elif event.key == pygame.K_f:
                    motionMatrix["vertical"] = 0
    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not locked:
                    locked = True
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
    
        
        s.camera.position.z += motionMatrix["forward"] * cos(cam.orientation[1])
        s.camera.position.x += motionMatrix["forward"] * sin(cam.orientation[1])
        s.camera.position.y -= motionMatrix["forward"] * sin(cam.orientation[0])
        s.camera.position.x += motionMatrix["lateral"] * sin(cam.orientation[1] + radians(90))
        s.camera.position.z += motionMatrix["lateral"] * cos(cam.orientation[1] + radians(90))
        s.camera.position.y += motionMatrix["vertical"]
        
        for o in s.objects:
            o.rotate((0.01,0.01,0.01))
        
        screen.fill((0,0,0))
    
        s.drawPaintedRaster(False)
    
        frames = pfont.render("{} fps".format(round(fps,1)),True, (255,255,255))
        screen.blit(frames, (10, 10))
        
        #draw crosshair
        chsize = 15
        pygame.draw.line(screen, (255, 255, 255), (mxcenter - chsize, mycenter), (mxcenter + chsize, mycenter), 1)
        pygame.draw.line(screen, (255, 255, 255), (mxcenter, mycenter - chsize), (mxcenter, mycenter + chsize), 1)
    
        pygame.display.flip()
        fps = 1/(time.time() - startloop + 0.01)

if __name__ == "__main__":
    main(sys.argv)