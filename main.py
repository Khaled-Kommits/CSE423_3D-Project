<<<<<<< HEAD
=======
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random, math, time

########### Feature 7 ###############
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
TRASH_SPAWN_INTERVAL_MS =8000
TRASH_MARGIN = 40 
trash_items = [] 
trash_created_count = 0 
_last_trash_spawn_ms = 0
draw_trash_enabled = True

def get_time_ms():
  return int(time.perf_counter() * 1000)

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
        return  # skip drawing and spawning when disabled

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

def keyboardListener(key, x, y):
    global camera, fp_active, FP_ANGLE, trash_items,draw_trash_enabled

    if key == b'f':
        fp_active = not fp_active  # Toggle first-person mode
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




def idle():
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
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)

    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
print("This is my version of the code with GitHub updates")
##feature 2 and 5
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math, time

# Camera-related variables
camera_pos = [0, 500, 500]  # Default camera position (Third-Person View)
fovY = 130  # Field of view
GRID_LENGTH = 600  # Length of grid lines
camera_orbit_degrees = 0.0  # Horizontal rotation (camera orbit)
camera_elevation = 30.0  # Vertical camera angle (elevation)

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
##feature2 fish 
# Max number of fish
MAX_FISH = 25
fish_list = []

# Fish settings (size, speed range)
FISH_SIZE_MIN = 10
FISH_SIZE_MAX = 40
FISH_SPEED_LIST = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]  # Speed list from slow to fast

# Camera movement speed
camera_speed = 10.0
## feature 5(day/night and bioluminicent fish)
# Mode flag (Day or Night)
is_night_mode = False

# Colors for Day Mode (excluding neon blue, neon green, and neon purple)
day_colors = [
    (0.5, 0.5, 0.0),    # olive
    (1.0, 0.5, 0.0),  # Bright Orange
    (1.0, 1.0, 0.0), # Bright Yellow
    (0.5, 0.0, 0.0),   #maroon
  ]

# Non-neon colors for Tail in Day Mode
tail_colors =[
    (0, 0.75, 0), # Light Green
    (.75,.25,0) ,# Light Orange
    (.75,.75,0) ,# Light Yellow
    (0.0, 0.5, 0.5) # Teal


]

# Neon Colors for Night Mode
neon_colors = [
    (0.0, 0.3, 1.0),  # Deep Sea Blue (Jellyfish glow)
    (0.0, 0.9, 1.0),  # Cyan Glow (Dinoflagellates)
    (0.0, 1.0, 0.7),  # Aqua Neon
    (0.2, 0.6, 1.0),  # Electric Blue
    (0.5, 1.0, 0.3),  # Glow Green (Firefly)
    (0.6, 1.0, 0.0),  # Neon Lime
    (0.7, 0.3, 1.0),  # Purple Glow (Deep-sea squid)
    (1.0, 0.0, 0.8),  # Magenta Neon
    (0.25, 1.0, 0.85), # Turquoise Glow
    (0.8, 0.4, 1.0)   # Radiant Violet
]


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
    glTranslatef(x, y, 16)
    glScalef(1.5,1.5,1.0)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidCube(30)
    glTranslatef(0, 0, 25)
    glColor3f(0.55, 0.5, 0.5)
    glutSolidCube(20)
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


def draw_shapes():
    draw_water_volume()
    draw_ocean_objects()


def draw_fish(x, y, z, size, speed, body_color, tail_color, rotation):
    # Draw fish body (sphere)
    glPushMatrix()
    glTranslatef(x, y, z)  # Position at the origin
    glColor3f(body_color[0], body_color[1], body_color[2])  # Fish body color
    gluSphere(gluNewQuadric(), size, 20, 20)  # Adjusted for a more realistic body shape
    glPopMatrix()

    # Draw fish tail (cylinder)
    glPushMatrix()
    glTranslatef(x + size, y, z)  # Move the tail to the right of the body
    glRotatef(rotation, 0, 1, 0)  # Rotate based on fish's facing direction
    glColor3f(tail_color[0], tail_color[1], tail_color[2])  # Tail color (different from body)
    gluCylinder(gluNewQuadric(), size // 4, size // 6, size * 0.75, 10, 10)  # Tail dimensions
    glPopMatrix()

    # Draw fish fins (two small spheres for simplicity)
    glPushMatrix()
    glTranslatef(x - size * 0.5, y + size * 0.5, z)  # Front fin position
    glColor3f(tail_color[0], tail_color[1], tail_color[2] )  # Fins color (same as tail)
    gluSphere(gluNewQuadric(), size * 0.3, 10, 10)  # Fin size
    glPopMatrix()

    glPushMatrix()
    glTranslatef(x - size * 0.5, y - size * 0.5, z)  # Back fin position
    glColor3f(tail_color[0], tail_color[1], tail_color[2] )  # Fins color (same as tail)
    gluSphere(gluNewQuadric(), size * 0.3, 10, 10)  # Fin size
    glPopMatrix()

    # Draw fish eye (black sphere)
    glPushMatrix()
    glTranslatef(x + size * 0.5, y + size * 0.5, z + size * 0.5)  # Eye position inside the fish body
    glColor3f(0, 0, 0)  # Black color for the eye
    gluSphere(gluNewQuadric(), size * 0.15, 10, 10)  # Adjusted eye size based on fish size
    glPopMatrix()

    glPushMatrix()
    glTranslatef(x + size * 0.5, y - size * 0.5, z + size * 0.5)  # Eye position inside the fish body
    glColor3f(0, 0, 0)  # Black color for the eye
    gluSphere(gluNewQuadric(), size * 0.15, 10, 10)  # Adjusted eye size based on fish size
    glPopMatrix()


def update_fish_positions():
    global fish_list
    for fish in fish_list:
        # Move fish in the direction of its head (based on rotation)
        radians = math.radians(fish["rotation"])
        fish["x"] += (fish["speed"] / 20.0) * math.cos(radians)  # Move along X axis (slow down by 20 times)
        fish["z"] += (fish["speed"] / 20.0) * math.sin(radians)  # Move along Z axis (slow down by 20 times
        
        # Add some boundary checks (if they go too far, change direction)
        if fish["x"] < -GRID_LENGTH + fish["size"] or fish["x"] > GRID_LENGTH - fish['size']:
            fish["rotation"] += 180  # Reverse direction on X-axis

        if fish["z"] < fish["size"] or fish["z"] > GRID_LENGTH // 2:
            fish["rotation"] += 180  # Reverse direction on Z-axis

    # Limit the number of fish
    if len(fish_list) > MAX_FISH:
        fish_list.pop(0)  # Remove the oldest fish if max fish count is exceeded

def generate_fish(x, y, z):
    # Generate fish with random properties
    size = random.randint(FISH_SIZE_MIN, FISH_SIZE_MAX)
    speed = random.choice(FISH_SPEED_LIST)  # Choose a random speed
    
    # In day mode, choose from predefined colors
    if not is_night_mode:
        body_color = random.choice(day_colors)  # Random color from the day colors list
        tail_color = random.choice(tail_colors)  # Tail color (different from body)
    else:
        body_color = random.choice(neon_colors)  # Neon color in night mode
        tail_color = random.choice(neon_colors)  # Tail color (neon too in night mode)

    rotation = random.randint(0, 360)  # Random direction (0 to 360 degrees)

    fish = {"x": x, "y": y, "z": z, "size": size, "speed": speed, "body_color": body_color, 
            "tail_color": tail_color, "rotation": rotation}
    fish_list.append(fish)


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Make the camera's FOV wide and adjust near/far clipping planes
    gluPerspective(fovY, 1.25, 1.0, 1500)  # Set near clipping to 1.0, far clipping to 1500
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Calculate camera position based on orbit and elevation
    orbit_x = math.cos(math.radians(camera_orbit_degrees)) * 500
    orbit_y = math.sin(math.radians(camera_orbit_degrees)) * 500
    camera_pos[0] = orbit_x  # Update camera X based on orbit
    camera_pos[2] = camera_elevation  # Update camera Z based on orbit
    camera_pos[1] = orbit_y  # Update camera Y based on elevation

    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2], 0, 0, 0, 0, 0, 1)  # Camera behind fish, looking at origin

def showScreen():
    # Set background color depending on day or night mode
    if is_night_mode:
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background for night mode
    else:
        glClearColor(0.51, 0.81, 0.99, 1.0)  # Pale sky blue for day mode

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()

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

    # Draw all fish
    for fish in fish_list:
        draw_fish(fish["x"], fish["y"], fish["z"], fish["size"], fish["speed"], fish["body_color"], fish["tail_color"], fish["rotation"])

    glutSwapBuffers()

def mouseListener(button, state, x, y):
    """
    Generates a new fish when clicked at a random position on the screen
    """
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        rand_x = random.randint(-GRID_LENGTH // 2, GRID_LENGTH // 2)
        rand_y = random.randint(-GRID_LENGTH // 2, GRID_LENGTH // 2)
        generate_fish(rand_x, rand_y, 40)  # Generate fish at a random position

def idle():

    update_fish_positions()  # Update fish positions
    glutPostRedisplay()  # Redraw the screen

def keyboardListener(key, x, y):

    global is_night_mode
    if key == b'd' or key == b'D':  # Switch to day mode
        is_night_mode = False
        # Update all existing fish colors to their day mode colors
        for fish in fish_list:
            fish["body_color"] = random.choice(day_colors)
            fish["tail_color"] = random.choice(tail_colors)
    elif key == b'n' or key == b'N':  # Switch to night mode
        is_night_mode = True
        # Update all existing fish colors to neon colors
        for fish in fish_list:
            fish["body_color"] = random.choice(neon_colors)
            fish["tail_color"] = random.choice(neon_colors)




def keyboardListener(key, x, y):
    """
    Toggle the camera view when 'C' key is pressed and move the camera with arrow keys
    """
    global is_night_mode
    if key == b'd' or key == b'D':  # Switch to day mode
        is_night_mode = False
        # Update all existing fish colors to their day mode colors
        for fish in fish_list:
            fish["body_color"] = random.choice(day_colors)
            fish["tail_color"] = random.choice(tail_colors)
    elif key == b'n' or key == b'N':  # Switch to night mode
        is_night_mode = True
        # Update all existing fish colors to neon colors
        for fish in fish_list:
            fish["body_color"] = random.choice(neon_colors)
            fish["tail_color"] = random.choice(neon_colors)

def handle_special_keys(key, x, y):
    global camera_orbit_degrees, camera_elevation
    if key == GLUT_KEY_UP: 
        camera_elevation += 15.0  # Move the camera up (increase elevation)
    elif key == GLUT_KEY_DOWN: 
        camera_elevation -= 15.0  # Move the camera down (decrease elevation)
    elif key == GLUT_KEY_LEFT: 
        camera_orbit_degrees -= 2.0  # Rotate camera left
    elif key == GLUT_KEY_RIGHT: 
        camera_orbit_degrees += 2.0  # Rotate camera right

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D Fish Example")
    glutDisplayFunc(showScreen)
    glutSpecialFunc(handle_special_keys)
    glutMouseFunc(mouseListener)
    glutKeyboardFunc(keyboardListener)  # Add keyboard listener for day/night mode
    glutIdleFunc(idle)  # Register the idle function to move the fish automatically
    glEnable(GL_DEPTH_TEST)  # Enable depth testing for proper 3D rendering
    glutMainLoop()

if __name__ == "__main__":
    main()
