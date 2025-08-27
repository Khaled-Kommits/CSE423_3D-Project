from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random, math, time


fovY = 130
camera_radius = 900
camera_angle  = 0     
camera_height = 600   

########### Feature 7 #################

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)  
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    global camera_radius, camera_angle, camera_height

    cam_x = camera_radius * math.cos(math.radians(camera_angle))
    cam_y = camera_radius * math.sin(math.radians(camera_angle))
    cam_z = camera_height

    gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)



def specialKeyListener(key, x, y):
    global camera_height, camera_angle
    if key == GLUT_KEY_UP:
        camera_height += 20
    elif key == GLUT_KEY_DOWN:
        camera_height -= 20
    elif key == GLUT_KEY_LEFT:
        camera_angle -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_angle += 5




def idle():
  glutPostRedisplay()



def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1200, 1000)
    setupCamera()



    glutSwapBuffers()



def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 1000)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Ocean Visualizer - Floor, Corals, Rocks & Water")
    glutDisplayFunc(showScreen)
    glutSpecialFunc(specialKeyListener)

    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()

