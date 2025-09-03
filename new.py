from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random, math, time

########### Feature 7 ###############
fovY = 130
camera_pos = [0, 500, 500]  # Default camera position (Third-Person View)
camera_radius = 900
camera_angle  = 0     
camera_height = 650   

GRID_LENGTH = 800

##### Feature 1 #####
#Corals
coral_offsets = [(-3,  2,  0),(10,  5, 0),(23,  0.8, 0)]

coral_color_y = [0, 0, 0.3]
coral_color_z = [0.2, 0.18, 0.19]
NUM_CORALS = 30
coral_positions = [(random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10),random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10))
    for _ in range(NUM_CORALS)]
CORAL_HEIGHTS = [50, 67, 35]

#Rocks
NUM_ROCKS = 20
rock_positions = [(random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10),random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10))
    for _ in range(NUM_ROCKS)]

#Water
WATER_HEIGHT   = 300
WAVE_AMPLITUDE = 6
WAVE_FREQ      = 0.8
WAVE_SUBDIV    = 28

# Camera movement speed
camera_speed = 10.0
## feature 3 (day/night and bioluminicent fish)
# Mode flag (Day or Night)
is_night_mode = False
##feture 5 bubble##

MAX_BUBBLES = 200
bubble_list = []

BUBBLE_MIN_SIZE = 2
BUBBLE_MAX_SIZE = 6
BUBBLE_SPEED = 1.0  
bubble_speed_multiplier = 1.0

##feture 13
# Treasure Box
TREASURE_SIZE = 60
treasure_pos = [0, 0, 0]  # x, y, z position
treasure_mode = False  # False = normal, True = treasure controllable
TREASURE_STEP = 10  # units per key press
collison=False
def spawn_treasure_bottom():
    global treasure_pos,collison
    x = random.uniform(-GRID_LENGTH, GRID_LENGTH)
    y = random.uniform(-GRID_LENGTH, GRID_LENGTH)
    treasure_pos = [x, y, 0]



def draw_coral(x, y, heights):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glScalef(2.0, 2.0, 2.0)
    for i in range(3):
        ox, oy, oz = coral_offsets[i]
        glPushMatrix()
        glTranslatef(ox, oy, oz)
        glColor3f(1, coral_color_y[i], coral_color_z[i])
        gluCylinder(gluNewQuadric(), 8, 4, heights[i], 5, 4)
        glPopMatrix()
    glPopMatrix()

def draw_rock(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidCube(45)
    glTranslatef(0, 0, 30)
    glColor3f(0.55, 0.5, 0.5)
    glutSolidCube(30)
    glPopMatrix()

def draw_ocean_objects():
    for (cx, cy) in coral_positions:
        draw_coral(cx, cy, CORAL_HEIGHTS)
    for (rx, ry) in rock_positions:
        draw_rock(rx, ry)

def draw_water_volume():
    half = GRID_LENGTH
    base_z = 0.0
    top_z = base_z + WATER_HEIGHT
    if is_night_mode:
        wall_color = (0.0, 0.0, 0.2)
    else:
        wall_color = (0.68, 0.85, 0.90)

    glColor3f(*wall_color)
    glBegin(GL_QUADS)
    # +X
    glVertex3f( half, -half, base_z)
    glVertex3f( half,  half, base_z)
    glVertex3f( half,  half, top_z)
    glVertex3f( half, -half, top_z)

    # -X
    glVertex3f(-half, -half, base_z)
    glVertex3f(-half,  half, base_z)
    glVertex3f(-half,  half, top_z)
    glVertex3f(-half, -half, top_z)

    # +Y
    glVertex3f(-half,  half, base_z)
    glVertex3f( half,  half, base_z)
    glVertex3f( half,  half, top_z)
    glVertex3f(-half,  half, top_z)

    # -Y
    glVertex3f(-half, -half, base_z)
    glVertex3f( half, -half, base_z)
    glVertex3f( half, -half, top_z)
    glVertex3f(-half, -half, top_z)
    glEnd()

    #Wavy surface
    t = time.perf_counter()
    step = (half * 2.0) / float(WAVE_SUBDIV)
    start = -half

    glBegin(GL_QUADS)
    for i in range(WAVE_SUBDIV):
        for j in range(WAVE_SUBDIV):
            x0 = start + i * step
            y0 = start + j * step
            x1 = x0 + step
            y1 = y0 + step

            z00 = top_z + math.sin((x0*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y0*0.015 - t*1.5)) * WAVE_AMPLITUDE
            z01 = top_z + math.sin((x0*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y1*0.015 - t*1.5)) * WAVE_AMPLITUDE
            z10 = top_z + math.sin((x1*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y0*0.015 - t*1.5)) * WAVE_AMPLITUDE
            z11 = top_z + math.sin((x1*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y1*0.015 - t*1.5)) * WAVE_AMPLITUDE
            if is_night_mode:
                glColor3f(0.0, 0.0, 0.5)
            else:
                glColor3f(0.4, 0.7, 0.9) #light blue
            glVertex3f(x0, y0, z00)
            glVertex3f(x1, y0, z10)
            glVertex3f(x1, y1, z11)
            glVertex3f(x0, y1, z01)
    glEnd()


###------feature 5------- ###
def increment_bubble_speed(bubble):
        bubble["speed"] *= 2.0 

def create_bubble():
    x = random.uniform(-GRID_LENGTH, GRID_LENGTH)
    y = random.uniform(-GRID_LENGTH, GRID_LENGTH)
    z = 0  # start from ocean floor
    size = random.uniform(BUBBLE_MIN_SIZE, BUBBLE_MAX_SIZE)
    speed = BUBBLE_SPEED * random.uniform(0.8, 1.2)
    return {"x": x, "y": y, "z": z, "size": size, "speed": speed, "on": True}
def update_bubbles():
    global bubble_list, bubble_speed_multiplier
    # Add new bubbles if below max count
    while len(bubble_list) < MAX_BUBBLES:
        bubble_list.append(create_bubble())

    t = time.perf_counter()
    for bubble in bubble_list:
       
        bubble["z"] += bubble["speed"] * bubble_speed_multiplier
     
        wave = WAVE_AMPLITUDE*2*math.sin((bubble["x"]*0.02 + t*2.0)) + WAVE_AMPLITUDE*math.cos((bubble["y"]*0.015 - t*1.5))
        if bubble["z"] >= WATER_HEIGHT + wave:
           
            bubble["x"] = random.uniform(-GRID_LENGTH, GRID_LENGTH)
            bubble["y"] = random.uniform(-GRID_LENGTH, GRID_LENGTH)
            bubble["z"] = 0
            bubble["size"] = random.uniform(BUBBLE_MIN_SIZE, BUBBLE_MAX_SIZE)
            bubble["speed"] = BUBBLE_SPEED * random.uniform(0.8, 1.2)


def draw_bubbles():
    if is_night_mode:
        glColor3f(0.8, 0.8, 1.0)  #light blue
    else:
        glColor3f(1.0, 1.0, 1.0)  # white bubbles
    for bubble in bubble_list:
        glPushMatrix()
        glTranslatef(bubble["x"], bubble["y"], bubble["z"])
        glutSolidSphere(bubble["size"], 10, 10)
        glPopMatrix()

def draw_treasure():
    x, y, z = treasure_pos
    glPushMatrix()
    glTranslatef(x, y, z + TREASURE_SIZE / 2)  # raise by half size so it sits on floor
    if is_night_mode:
        glColor3f(0.5, 0.35, 0.2)  # brown color
    else:
        glColor3f(1.0, 0.84, 0.0)  # gold color
    glutSolidCube(TREASURE_SIZE)
    glPopMatrix()

def check_collision(x, y):
    # Water boundary check
    half = GRID_LENGTH
    if x - TREASURE_SIZE/2 < -half or x + TREASURE_SIZE/2 > half:
        return True
    if y - TREASURE_SIZE/2 < -half or y + TREASURE_SIZE/2 > half:
        return True

    # Check corals
    for cx, cy in coral_positions:
        if abs(x - cx) < TREASURE_SIZE + 10 and abs(y - cy) < TREASURE_SIZE + 10:
            return True
    # Check rocks
    for rx, ry in rock_positions:
        if abs(x - rx) < TREASURE_SIZE + 20 and abs(y - ry) < TREASURE_SIZE + 20:
            return True
    return False


def draw_shapes():
    draw_water_volume()
    draw_ocean_objects()
    if not treasure_mode:  # Only draw bubbles and fish when not in Treasure Mode
        draw_bubbles()
        #draw_fish()  # if you have fish drawing function
    else:
        draw_treasure()
      # Respawn treasure at bottom if needed


########### Feature 7 ###############

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
def keyboardListener(key, x, y):
    global treasure_mode, treasure_pos, is_night_mode
    
    if key == b'd' or key == b'D':  # Switch to day mode
        is_night_mode = False
    elif key == b'n' or key == b'N':  # Switch to night mode
        is_night_mode = True
    elif key == b'a' or key == b'A':  # Speed up bubbles
        bubble_speed_multiplier *= 2.0
    elif key == b'r' or key == b'R':  # Reset bubbles to normal speed
        bubble_speed_multiplier = 1.0
    elif key == b't' or key == b'T':
        treasure_mode = not treasure_mode
        if treasure_mode:
            spawn_treasure_bottom()
        print("Treasure Mode:", "ON" if treasure_mode else "OFF")
    
    if treasure_mode:
        new_x, new_y = treasure_pos[0], treasure_pos[1]

        if key == b'i' or key == b'I':  # Move left
            new_x -= TREASURE_STEP
        elif key == b'p' or key == b'P':  # Move right
            new_x += TREASURE_STEP
        elif key == b'l' or key == b'L':  # Move forward (+y)
            new_y += TREASURE_STEP
        elif key == b'o' or key == b'O':  # Move backward (-y)
            new_y -= TREASURE_STEP
        elif key == b'q' or key == b'Q':
            treasure_mode = False
            return
        
        # Check for collision with new position
        if not check_collision(new_x, new_y):
            treasure_pos[0] = new_x
            treasure_pos[1] = new_y
        else:
            # If collision detected, respawn the treasure
            spawn_treasure_bottom()
         


def idle():
  update_bubbles
  glutPostRedisplay()



def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1200, 1000)
    setupCamera()
    # Ocean floor
    glBegin(GL_QUADS)
    glColor3f(1.0, 0.88, 0.65)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH,  GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glEnd()

    draw_shapes()

    glutSwapBuffers()



def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 1000)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Ocean Visualizer - Floor, Corals, Rocks & Water")
    glutDisplayFunc(showScreen)
    glutSpecialFunc(specialKeyListener)
    glutKeyboardFunc(keyboardListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
  main()