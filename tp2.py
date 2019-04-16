import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

angle_x = 0
angle_y = 0
angle_z = 0
draw_teapot = False
                
def display():
    global angle_x, angle_y, angle_z, draw_teapot
    
    glMatrixMode(GL_MODELVIEW)
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glColor3f(0.0, 0.0, 1.0)

    glPushMatrix()
    
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)
    glRotatef(angle_z, 0, 0, 1)
    
    if draw_teapot:
        glutSolidTeapot(30.0)
    else:
        # Front face
        glBegin(GL_QUADS)
        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(  25, -25, -25 )
        glVertex3f(  25,  25, -25 )
        glVertex3f( -25,  25, -25 )
        glVertex3f( -25, -25, -25 )
        glEnd()

        # Back face
        glBegin(GL_QUADS)
        glNormal3f(0.0, 0.0, 1.0)
        glVertex3f(  25, -25, 25 )
        glVertex3f(  25,  25, 25 )
        glVertex3f( -25,  25, 25 )
        glVertex3f( -25, -25, 25 )
        glEnd()

        # Right face
        glBegin(GL_QUADS)
        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f( 25, -25, -25 )
        glVertex3f( 25,  25, -25 )
        glVertex3f( 25,  25,  25 )
        glVertex3f( 25, -25,  25 )
        glEnd()

        # Left face
        glBegin(GL_QUADS)
        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f( -25, -25,  25 )
        glVertex3f( -25,  25,  25 )
        glVertex3f( -25,  25, -25 )
        glVertex3f( -25, -25, -25 )
        glEnd()

        # Top face
        glBegin(GL_QUADS)
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(  25,  25,  25 )
        glVertex3f(  25,  25, -25 )
        glVertex3f( -25,  25, -25 )
        glVertex3f( -25,  25,  25 )
        glEnd()

        # Bottom face
        glBegin(GL_QUADS)
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(  25, -25, -25 )
        glVertex3f(  25, -25,  25 )
        glVertex3f( -25, -25,  25 )
        glVertex3f( -25, -25, -25 )
        glEnd()

    glPopMatrix()

    glFlush()


def window_resize(w, h):
    # Função chamada quando a janela é reescalonada
    if(h == 0):
        h = 1
    
    glViewport(0, 0, w, h)

    fAspect = w/h
    angle = 45

    glMatrixMode(GL_PROJECTION)

    glLoadIdentity()

    gluPerspective(angle,fAspect,0.1,500)

    glMatrixMode(GL_MODELVIEW)
    
    glLoadIdentity()

    gluLookAt(0,50,200, 0,0,0, 0,1,0)

def init():   
    luzAmbiente = [0.2,0.2,0.2,1.0]
    luzDifusa = [0.7,0.7,0.7,1.0]
    luzEspecular = [1.0, 1.0, 1.0, 1.0]
    posicaoLuz = [0.0, 50.0, 50.0, 1.0]

    especularidade = [1.0,1.0,1.0,1.0]
    especMaterial = 60

    glClearColor(0.0, 0.0, 0.0, 1.0)

    glShadeModel(GL_SMOOTH)

    glMaterialfv(GL_FRONT,GL_SPECULAR, especularidade)
    glMateriali(GL_FRONT,GL_SHININESS,especMaterial)

    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luzAmbiente)

    glLightfv(GL_LIGHT0, GL_AMBIENT, luzAmbiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luzDifusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luzEspecular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicaoLuz)

    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)

def mouse_click(button, state, x, y):
    global draw_teapot

    if state == GLUT_UP:
        return
    if button == GLUT_LEFT_BUTTON:
        draw_teapot = True
    elif button == GLUT_RIGHT_BUTTON:
        draw_teapot = False

def key_pressed_special(key, x, y):
    if key == GLUT_KEY_UP:
        glTranslatef(0.0, 10.0, 0.0)
    elif key == GLUT_KEY_DOWN:
        glTranslatef(0.0, -10.0, 0.0)
    elif key == GLUT_KEY_RIGHT:
        glTranslatef(10.0, 0.0, 0.0)
    elif key == GLUT_KEY_LEFT:
        glTranslatef(-10.0, 0.0, 0.0)

def key_pressed(key, x, y):
    global angle_x, angle_y, angle_z
    
    if key == b'x':
        angle_x = (angle_x+10)%360
    elif key == b'X':
        angle_x = (angle_x-10)%360
    elif key == b'y':
        angle_y = (angle_y+10)%360
    elif key == b'Y':
        angle_y = (angle_y-10)%360
    elif key == b'z':
        angle_z = (angle_z+10)%360
    elif key == b'Z':
        angle_z = (angle_z-10)%360
    elif key == b's':
        glScalef(0.5, 0.5, 0.5)
    elif key == b'S':
        glScalef(2.0, 2.0, 2.0)

def timer(value):
    # Função usada para chamar display() a cada 33ms
    glutPostRedisplay()
    glutTimerFunc(33, timer, 0)


glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(800, 600)
glutInitWindowPosition(0, 0)
glutCreateWindow("Pentagon")
glutDisplayFunc(display)
glutTimerFunc(33, timer, 0)
glutReshapeFunc(window_resize)
glutMouseFunc(mouse_click)
glutKeyboardFunc(key_pressed)
glutSpecialFunc(key_pressed_special)
init()

glutMainLoop()