'''
donut.c Python implementation

Branching off the matplotlib implementation, I decided to convert it to a simple terminal output.

'''

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import time, os
import numpy as np

#Number of points that will be accounted for initially
noofpoints = 100

#Initialisation of two major angles, theta and phi
Theta = np.linspace(0, 2*math.pi, noofpoints)
Phi = np.linspace(0, 2*math.pi, noofpoints)

#Used later in rendering
FPS_60 = 1/60

#Set up of screen width and height
screen_width, screen_height = 50, 50

screen = [[' ' for _ in range(screen_width)] for i in range(screen_height)] #Initialised the screen as a 2d array

R, r = 1, 0.4 #2 major radii, R for the circular radius, and r for the radius of the tube
k2 = 10 #Adds some distance to the screen
k1 = 100 #Scaling factor used in perspective projection
A, B = 0.0, 0.0 #Rotation angles

theta, phi = np.meshgrid(Theta, Phi) #Map each value of theta to a value of phi

def update():
    global A, B, theta, phi, k2, k1, screen_height, screen_width
    dt = 1/10

    #Update rotation angles
    A += 0.6 * dt
    B += 0.6 * dt

    #Precompute all values of sin and cos
    p =(R+r*np.cos(theta))
    sinB, sinA = math.sin(B), math.sin(A) 
    cosB, cosA = math.cos(B), math.cos(A)
    sinphi, cosphi = np.sin(phi), np.cos(phi)
    sintheta, costheta = np.sin(theta), np.cos(theta)

    X_3d = ((p)*(cosB*cosphi+sinA*sinB*sinphi)-r*cosA*sinB*sintheta).flatten()
    Y_3d = ((p)*(cosphi*sinB-cosB*sinA*sinphi)+r*cosA*cosB*sintheta).flatten()
    Z_3d = (cosA*sinphi*p+r*sinA*sintheta).flatten()

    #One over depth. Makes calculation easier 
    ooz = 1/(k2+Z_3d)

    xscreen = (k1 * X_3d * ooz).astype(int) + screen_width // 2
    yscreen = (k1 * Y_3d * ooz).astype(int) + screen_height // 2

    #Calculate the lighting values as the dot product of the surface normals and a light vector. Calculation has been oversimplified as per the donut.c documentation
    L = (cosphi*costheta*sinB - cosA*costheta*sinphi - sinA*sintheta + cosB*(cosA*sintheta-costheta*sinA*sinphi)).flatten()
    L = np.maximum(L, 0)

    #Initalise the z-buffer
    zbuffer = np.full((screen_height, screen_width), 0.0)

    visible_x = np.zeros_like(xscreen)
    visible_y = np.zeros_like(yscreen)
    visible_L = np.zeros_like(L)

    index = 0

    #Update the z-buffer
    for x, y, z in zip(xscreen, yscreen, ooz):
        if 0 <= x < screen_width and 0 <= y < screen_height:
            if z > zbuffer[y, x]:
                zbuffer[y, x] = z
                visible_x = np.append(visible_x, xscreen[index])
                visible_y = np.append(visible_y, yscreen[index])
                visible_L = np.append(visible_L, L[index])

        index += 1

    return visible_x, visible_y, visible_L

#Simple printing function
def PrintScreen(screen):
    for i in screen:
        for j in i:
            print(j, end='')
        print()

while True:
    screen = [[' ' for _ in range(screen_width)] for i in range(screen_height)]
    vx, vy, vl = update()
    for x, y, l in zip(vx, vy, vl):
        #Map each value for luminance to an ascii character
        luminance_index = math.floor((l/np.max(vl))*11)
        screen[x][y] = '.,-~:;=!*#$@'[luminance_index]
        # screen[x][y] = '.'

    PrintScreen(screen)
    time.sleep(FPS_60)
    os.system('clear')
