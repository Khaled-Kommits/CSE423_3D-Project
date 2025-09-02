from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math, time

# Camera-related variables
camera_pos = [0, 500, 500]  # Default camera position (Third-Person View)
fovY = 120  # Field of view
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
        wall_color = (0.1, 0.1, 0.2) # Dark blue for night mode
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
            glColor3f(0.1, 0.1, 0.2)  # Dark blue for night mode
        else:
            glColor3f(0.4, 0.7, 0.9)  # Day color
        glVertex3f(x0, y0, z00)
        glVertex3f(x1, y0, z10)
        glVertex3f(x1, y1, z11)
        glVertex3f(x0, y1, z01)
    glEnd()


def draw_shapes():
    draw_water_volume()
    draw_ocean_objects()

# Max number of fish
MAX_FISH = 15
fish_list = []

# Fish settings (size, speed range)
FISH_SIZE_MIN = 10
FISH_SIZE_MAX = 40
FISH_SPEED_LIST = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]  # Speed list from slow to fast

# Camera movement speed
camera_speed = 10.0

# Mode flag (Day or Night)
is_night_mode = False

# Colors for Day Mode (excluding neon blue, neon green, and neon purple)
day_colors = [
 
    (255, 165, 0),  # Bright Orange
    (255, 255, 0),  # Bright Yellow

    (0, 128, 128),  # Bright Teal

]

# Non-neon colors for Tail in Day Mode
tail_colors =[
    (255, 69, 0),   # Orange Red
    (34, 139, 34),  # Forest Green
    (255, 20, 147), # Deep Pink
    (138, 43, 226), # Blue Violet
    (70, 130, 180), # Steel Blue

]

# Neon Colors for Night Mode
neon_colors = [
    (57, 255, 20),    # Neon Green: RGB(57, 255, 20) 
    (0, 255, 255),    # Neon Blue: RGB(0, 255, 255) 
    (255, 0, 255),    # Neon Purple: RGB(255, 0, 255) 
    (255, 20, 147),   # Neon Pink: RGB(255, 20, 147)
    (0, 255, 255),    # Neon Cyan: RGB(0, 255, 255) 
    (0, 191, 255),    # Bioluminescent Blue: RGB(0, 191, 255) 
]

BUBBLE_BASE_RADIUS = 4.0  # Base size for the bubbles
BUBBLE_LIFE_TIME = 10.0  # Lifetime of the bubble before it disappears
BUBBLE_SPAWN_CHANCE = 0.05  # Probability per frame to spawn a new bubble
MAX_BUBBLES = 50  # Maximum number of bubbles at any time
GRID_LENGTH = 400  # Grid size for spawning bubbles
BUBBLE_SPEED = 50  # Speed of the bubble's vertical movement (in pixels per second)

# Bubble list: each bubble is a dictionary containing position, velocity, size, and ttl
bubble_list = []

# Area limits for bubble spawning
X_LIMIT = [(random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10), random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10)) for _ in range(5)]  # X-axis limit for bubble spawning
Y_LIMIT = [(random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10), random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10)) for _ in range(5)]  # Y-axis limit for bubble spawning
Z_MIN = -300   # Minimum Z position for bubble spawning
Z_MAX = 100    # Maximum Z position for bubble spawning (just below water surface)


def draw_fish(x, y, z, size, speed, body_color, tail_color, rotation):
    # Draw fish body (sphere)
    glPushMatrix()
    glTranslatef(x, y, z)  # Position at the origin
    glColor3f(body_color[0] / 255.0, body_color[1] / 255.0, body_color[2] / 255.0)  # Fish body color
    gluSphere(gluNewQuadric(), size, 20, 20)  # Adjusted for a more realistic body shape
    glPopMatrix()

    # Draw fish tail (cylinder)
    glPushMatrix()
    glTranslatef(x + size, y, z)  # Move the tail to the right of the body
    glRotatef(rotation, 0, 1, 0)  # Rotate based on fish's facing direction
    glColor3f(tail_color[0] / 255.0, tail_color[1] / 255.0, tail_color[2] / 255.0)  # Tail color (different from body)
    gluCylinder(gluNewQuadric(), size // 4, size // 6, size * 0.75, 10, 10)  # Tail dimensions
    glPopMatrix()

    # Draw fish fins (two small spheres for simplicity)
    glPushMatrix()
    glTranslatef(x - size * 0.5, y + size * 0.5, z)  # Front fin position
    glColor3f(tail_color[0] / 255.0, tail_color[1] / 255.0, tail_color[2] / 255.0)  # Fins color (same as tail)
    gluSphere(gluNewQuadric(), size * 0.3, 10, 10)  # Fin size
    glPopMatrix()

    glPushMatrix()
    glTranslatef(x - size * 0.5, y - size * 0.5, z)  # Back fin position
    glColor3f(tail_color[0] / 255.0, tail_color[1] / 255.0, tail_color[2] / 255.0)  # Fins color (same as tail)
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
random.seed(423)

def render_bubble(bubble):
    """Render a bubble with a grey outer line and pale sky blue inside"""
    glPushMatrix()
    glTranslatef(bubble["x"], bubble["y"], bubble["z"])
    
        # Render the grey outer line (wireframe mode)
    glColor3f(0.53, 0.81, 0.98)  # Grey color for the outer line
    glutWireSphere(bubble["radius"], 10, 8)  # Wireframe bubble
    if is_night_mode:
        glColor3f(0.2, 0.2, 0.3)  # Dark blue for night mode
    else:
        glColor3f(0.53, 0.81, 0.98)  # Pale sky blue color for the bubble's inner part

    glutSolidSphere(bubble["radius"], 10, 8)  # Solid filled bubble

    glPopMatrix()


def update_bubbles(dt):
    """Update bubbles' positions and remove the ones that reach their lifetime"""
    kill_idx = []  # List to store indices of bubbles to be removed
    for i, bubble in enumerate(bubble_list):
        bubble["z"] += BUBBLE_SPEED * dt  # Move bubble upwards (update z position)
        bubble["ttl"] -= dt  # Decrease ttl (time-to-live)

        # Check if the bubble has exceeded its lifetime
        if bubble["ttl"] <= 0:
            kill_idx.append(i)

    # Remove dead bubbles
    for i in reversed(kill_idx):  # Remove from the end to avoid index errors
        bubble_list.pop(i)


def spawn_bubble_within_area():
    """Spawn a new bubble within the specified area"""
    if len(bubble_list) >= MAX_BUBBLES:  # Don't spawn more bubbles if we reached the max limit
        return

    # Generate random position within the defined limits
    x = random.uniform(-X_LIMIT, X_LIMIT)
    y = random.uniform(-Y_LIMIT, Y_LIMIT)
    z = random.uniform(Z_MIN, Z_MAX)  # Spawn within the defined Z range
    radius = BUBBLE_BASE_RADIUS * random.uniform(0.6, 1.2)  # Random size variation

    # Add the new bubble to the bubble list
    bubble_list.append({
        "x": x, "y": y, "z": z,
        "radius": radius,
        "vy": 0,  # Not used anymore since we have a fixed speed
        "ttl": random.uniform(5.0, BUBBLE_LIFE_TIME)  # Set ttl for how long the bubble exists
    })


def try_spawn_bubble():
    """Try to spawn a new bubble based on spawn chance"""
    if random.random() < BUBBLE_SPAWN_CHANCE:
        spawn_bubble_within_area()

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

def showScreen():
    # Set background color depending on day or night mode
    if is_night_mode:
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background for night mode
    else:
        glClearColor(135 / 255.0, 206 / 255.0, 235 / 255.0, 1.0)  # Pale sky blue for day mode

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()

    glBegin(GL_QUADS)
    glColor3f(1.0, 0.88, 0.65)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH,  GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glEnd()

    draw_shapes()
    for bubble in bubble_list:
        render_bubble(bubble)

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
    """Update the bubble positions and continuously spawn new bubbles"""
    current = time.perf_counter()
    if not hasattr(idle, "_prev"):
        idle._prev = current
    dt = current - idle._prev
    idle._prev = current

    # Update bubbles (position, ttl, etc.)
    update_bubbles(dt)

    # Continuously spawn bubbles
    try_spawn_bubble()
    update_fish_positions() 

    glutPostRedisplay()  # Trigger screen redraw

    # Update fish positions
    update_fish_positions()

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
