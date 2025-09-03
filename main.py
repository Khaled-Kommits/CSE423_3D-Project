from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random, math, time

########### Feature 7 ############
fovY = 130
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
WATER_HEIGHT   = 600
WAVE_AMPLITUDE = 6
WAVE_FREQ      = 0.8
WAVE_SUBDIV    = 28

fp_active = False
camera = [0.0, 0.0]
EYE_HEIGHT = 100
FP_SPEED   = 25.0
FP_ANGLE   = 0.0
ROT_SPEED  = 5.0

#Trash cleaning
TRASH_SPAWN_INTERVAL_MS =7000
TRASH_MARGIN = 40 
trash_items = [] 
trash_created_count = 0 
_last_trash_spawn_ms = 0
draw_trash_enabled = True

############# Feature 2 and 5 ###############
MAX_FISH = 25
fish_list = []
FISH_SIZE_MIN = 10
FISH_SIZE_MAX = 40
FISH_SPEED_LIST = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]  

is_night_mode = False
# Colors for Day Mode
day_colors = [(0.5, 0.5, 0.0), (1.0, 0.5, 0.0), (1.0, 1.0, 0.0),(0.5, 0.0, 0.0)]
# Non-neon colors for Tail in Day Mode
tail_colors =[(0, 0.75, 0), (.75,.25,0) ,(.75,.75,0) ,(0.0, 0.5, 0.5)]
# Neon Colors for Night Mode
neon_colors = [
    (0.0, 0.3, 1.0),  
    (0.0, 0.9, 1.0),  
    (0.0, 1.0, 0.7),  
    (0.2, 0.6, 1.0),  
    (0.5, 1.0, 0.3),  
    (0.6, 1.0, 0.0),  
    (0.7, 0.3, 1.0),  
    (1.0, 0.0, 0.8),  
    (0.25, 1.0, 0.85), 
    (0.8, 0.4, 1.0)]

def get_time_ms():
  return int(time.perf_counter() * 1000)
 
 ######feature 1 #########
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

            glColor3f(0.4, 0.7, 0.9) 
            glVertex3f(x0, y0, z00)
            glVertex3f(x1, y0, z10)
            glVertex3f(x1, y1, z11)
            glVertex3f(x0, y1, z01)
    glEnd()

######## feature 8 ###########

def draw_trash_bottle():

    glPushMatrix()
    glRotatef(90, 1, 0, 0)  

    glColor3f(0.2, 0.8, 0.9)  
    quad = gluNewQuadric()
    
    # body
    gluCylinder(quad, 3.0, 3.0, 20.0, 12, 6)
    
    # neck
    glTranslatef(0, 0, 20.0)
    gluCylinder(quad, 1.6, 1.2, 6.0, 10, 4)
    
    # cap
    glTranslatef(0, 0, 6.0)
    glColor3f(0.5, 0.2, 0.2)
    glutSolidSphere(1.6, 10, 8)

    glPopMatrix()

def draw_trash_bag():
#small top nubs as handles
    glColor3f(0.95, 0.95, 1.0)
# bag body
    glPushMatrix()
    glScalef(10.0, 2.5, 12.0)
    glutSolidCube(1.0)
    glPopMatrix()
# left handle nub
    glPushMatrix()
    glTranslatef(-4.5, 0.0, 6.5)
    glScalef(2.0, 1.2, 2.0)
    glutSolidCube(1.0)
    glPopMatrix()
# right handle nub
    glPushMatrix()
    glTranslatef(4.5, 0.0, 6.5)
    glScalef(2.0, 1.2, 2.0)
    glutSolidCube(1.0)
    glPopMatrix()


def spawn_trash_once():
    global trash_created_count

    x = random.randint(-GRID_LENGTH + TRASH_MARGIN, GRID_LENGTH - TRASH_MARGIN)
    y = random.randint(-GRID_LENGTH + TRASH_MARGIN, GRID_LENGTH - TRASH_MARGIN)
    type_id = random.randint(0, 1) # 0=bottle, 1=bag
    rot_deg = random.uniform(0, 360)
    scale = random.uniform(0.8, 1.6)
    trash_items.append((x, y, type_id, rot_deg, scale))
    trash_created_count += 1

def trash_cleaning():
    global _last_trash_spawn_ms
    if not draw_trash_enabled:
        return  

    now = get_time_ms()
    if now - _last_trash_spawn_ms >= TRASH_SPAWN_INTERVAL_MS:
        spawn_trash_once()
        _last_trash_spawn_ms = now

    # draw all trash
    for (tx, ty, type_id, rot, s) in trash_items:
        glPushMatrix()
        glTranslatef(tx, ty, 0.0)
        glRotatef(rot, 0, 0, 1)
        glScalef(s, s, s)
        if type_id == 0:
            draw_trash_bottle()
        else:
            draw_trash_bag()
        glPopMatrix()

def draw_shapes():
    draw_water_volume()
    draw_ocean_objects()
    trash_cleaning()


########### Feature 7 ###############

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    global camera_radius, camera_angle, camera_height, fp_active, camera

    if fp_active:
       eye_x, eye_y, eye_z = camera[0], camera[1], EYE_HEIGHT

       rad = math.radians(FP_ANGLE)
       center_x = eye_x + math.cos(rad) * 200
       center_y = eye_y + math.sin(rad) * 200
       center_z = eye_z

       gluLookAt(eye_x, eye_y, eye_z,
              center_x, center_y, center_z,
              0, 0, 1)
    else:
        cam_x = camera_radius * math.cos(math.radians(camera_angle))
        cam_y = camera_radius * math.sin(math.radians(camera_angle))
        cam_z = camera_height
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)
###### feature 2  #########
def draw_fish(x, y, z, size, speed, body_color, tail_color, rotation):
    #fish body
    glPushMatrix()
    glTranslatef(x, y, z)  
    glColor3f(body_color[0], body_color[1], body_color[2])  
    gluSphere(gluNewQuadric(), size, 20, 20)  
    glPopMatrix()

    # Draw fish tail 
    glPushMatrix()
    glTranslatef(x + size, y, z) 
    glRotatef(rotation, 0, 1, 0) 
    glColor3f(tail_color[0], tail_color[1], tail_color[2])  
    gluCylinder(gluNewQuadric(), size // 4, size // 6, size * 0.75, 10, 10)  
    glPopMatrix()
    # Draw fish fins 
    glPushMatrix()
    glTranslatef(x - size * 0.5, y + size * 0.5, z) 
    glColor3f(tail_color[0], tail_color[1], tail_color[2] )  
    gluSphere(gluNewQuadric(), size * 0.3, 10, 10) 
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(x - size * 0.5, y - size * 0.5, z)  
    glColor3f(tail_color[0], tail_color[1], tail_color[2] )  
    gluSphere(gluNewQuadric(), size * 0.3, 10, 10)  
    glPopMatrix()
    # Draw fish eye
    glPushMatrix()
    glTranslatef(x + size * 0.5, y + size * 0.5, z + size * 0.5)  
    glColor3f(0, 0, 0)  
    gluSphere(gluNewQuadric(), size * 0.15, 10, 10)  
    glPopMatrix()

    glPushMatrix()
    glTranslatef(x + size * 0.5, y - size * 0.5, z + size * 0.5)  
    glColor3f(0, 0, 0) 
    gluSphere(gluNewQuadric(), size * 0.15, 10, 10)  
    glPopMatrix()

def update_fish_positions():
    global fish_list
    for fish in fish_list:
        radians = math.radians(fish["rotation"])
        fish["x"] += (fish["speed"]) * math.cos(radians)  
        fish["z"] += (fish["speed"]) * math.sin(radians)  
        
        if fish["x"] < -GRID_LENGTH + fish["size"] or fish["x"] > GRID_LENGTH - fish['size']:
            fish["rotation"] += 180  
        if fish["z"] < fish["size"] or fish["z"] > GRID_LENGTH // 2:
            fish["rotation"] += 180  
    if len(fish_list) > MAX_FISH:
        fish_list.pop(0) 

def generate_fish(x, y, z):
    # Generate fish 
    size = random.randint(FISH_SIZE_MIN, FISH_SIZE_MAX)
    speed = random.choice(FISH_SPEED_LIST)  
    if not is_night_mode:
        body_color = random.choice(day_colors)  # Random color from the day colors list
        tail_color = random.choice(tail_colors)  
    else:
        body_color = random.choice(neon_colors)  # Neon color in night mode
        tail_color = random.choice(neon_colors) 
    rotation = random.randint(0, 360)  # Random direction 
    fish = {"x": x, "y": y, "z": z, "size": size, "speed": speed, "body_color": body_color, 
            "tail_color": tail_color, "rotation": rotation}
    fish_list.append(fish)


def keyboardListener(key, x, y):
    global camera, fp_active, FP_ANGLE, trash_items,draw_trash_enabled, is_night_mode
    if key == b'l' :
        is_night_mode = False
        #fish colors to their day mode colorr
        for fish in fish_list:
            fish["body_color"] = random.choice(day_colors)
            fish["tail_color"] = random.choice(tail_colors)
    elif key == b'n':
        is_night_mode = True
        #fish colors to neon colors
        for fish in fish_list:
            fish["body_color"] = random.choice(neon_colors)
            fish["tail_color"] = random.choice(neon_colors)
    if key == b'f':
        fp_active = not fp_active  # first-person mode
        return
    elif key == b'c':
        draw_trash_enabled = not draw_trash_enabled  # toggle drawing
        return
    if not fp_active:
        return

    rad = math.radians(FP_ANGLE)
    dx = math.cos(rad)
    dy = math.sin(rad)

    if key == b'w':
        camera[0] += dx * FP_SPEED
        camera[1] += dy * FP_SPEED
    elif key == b's':
        camera[0] -= dx * FP_SPEED
        camera[1] -= dy * FP_SPEED
    elif key == b'a':
        FP_ANGLE += ROT_SPEED
    elif key == b'd':
        FP_ANGLE -= ROT_SPEED

    # Clamp inside grid
    half = GRID_LENGTH
    margin = 10
    camera[0] = max(-half + margin, min(half - margin, camera[0]))
    camera[1] = max(-half + margin, min(half - margin, camera[1]))

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

def mouseListener(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        rand_x = random.randint(-GRID_LENGTH // 2, GRID_LENGTH // 2)
        rand_y = random.randint(-GRID_LENGTH // 2, GRID_LENGTH // 2)
        generate_fish(rand_x, rand_y, 40) 

def idle():
  update_fish_positions() 
  glutPostRedisplay()



def showScreen():
    if is_night_mode:
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background for night mode
    else:
        glClearColor(0.51, 0.81, 0.99, 1.0)  # Pale sky blue for day mode

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1200, 1000)
    setupCamera()
    # Ocean floor
    glBegin(GL_QUADS)
    if is_night_mode:
        glColor3f(0.50, 0.44, 0.33)  # Dark sandy color for night mode
    else:
        glColor3f(1.0, 0.88, 0.65)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH,  GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glEnd()

    draw_shapes()
    glEnable(GL_DEPTH_TEST)
    for fish in fish_list:
        draw_fish(fish["x"], fish["y"], fish["z"], fish["size"], fish["speed"], fish["body_color"], fish["tail_color"], fish["rotation"])
    glDisable(GL_DEPTH_TEST)
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 1000)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Ocean Visualizer - Floor, Corals, Rocks & Water")
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()
if __name__ == "__main__":
    main()

