import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

# Bubble settings
BUBBLE_BASE_RADIUS = 4.0  # Base size for the bubbles
BUBBLE_LIFE_TIME = 10.0  # Lifetime of the bubble before it disappears
BUBBLE_SPAWN_CHANCE = 0.05  # Probability per frame to spawn a new bubble
MAX_BUBBLES = 50  # Maximum number of bubbles at any time
GRID_LENGTH = 400  # Grid size for spawning bubbles
BUBBLE_SPEED = 50  # Speed of the bubble's vertical movement (in pixels per second)

# Bubble list: each bubble is a dictionary containing position, velocity, size, and ttl
bubble_list = []

# Area limits for bubble spawning
X_LIMIT = 200  # X-axis limit for bubble spawning
Y_LIMIT = 200  # Y-axis limit for bubble spawning
Z_MIN = -300   # Minimum Z position for bubble spawning
Z_MAX = 100    # Maximum Z position for bubble spawning (just below water surface)

# Random seed
random.seed(423)

def render_bubble(bubble):
    """Render a bubble with a grey outer line and pale sky blue inside"""
    glPushMatrix()
    glTranslatef(bubble["x"], bubble["y"], bubble["z"])

    # Render the grey outer line (wireframe mode)
    glColor3f(0.53, 0.81, 0.98)  # Grey color for the outer line
    glutWireSphere(bubble["radius"], 10, 8)  # Wireframe bubble

    # Render the inner fill (pale sky blue color)
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
    """Set up the camera position and perspective"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.25, 0.1, 2000)  # Set the field of view to 60
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Camera position: Move the camera back so we can see the objects
    glTranslatef(0.0, 0.0, -500)


def draw_scene():
    """Draw the scene including bubbles"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear both color and depth buffers
    glLoadIdentity()

    # Set the camera position
    setupCamera()

    # Draw bubbles
    for bubble in bubble_list:
        render_bubble(bubble)

    glutSwapBuffers()


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

    glutPostRedisplay()  # Trigger screen redraw


def main():
    """Initialize and start the OpenGL main loop"""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Bubble Generator")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Set the background color to black
    #glShadeModel(GL_SMOOTH)  # Use smooth shading for better lighting effects

    glutDisplayFunc(draw_scene)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()
