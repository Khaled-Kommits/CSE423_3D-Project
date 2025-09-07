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
EYE_HEIGHT = 150
FP_SPEED   = 25.0
FP_ANGLE   = 0.0
ROT_SPEED  = 5.0

#Trash cleaning
TRASH_SPAWN_INTERVAL_MS =3000
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

######## feature 3 #########
# Sharks
SHARK_SPAWN_INTERVAL_MS = 15000 
MAX_SHARKS = 4  
sharks = [] 
_last_shark_spawn_ms = 0  
SHARK_SPEED = 50.0 
last_update_time = time.perf_counter() 

##### feature 4 #######
MAX_BUBBLES = 60
bubble_list = []

BUBBLE_MIN_SIZE = 2
BUBBLE_MAX_SIZE = 6
BUBBLE_SPEED = 1.0  
bubble_speed_multiplier = 1.0

##### feature 10 #######
feeding_mode = False
food_items = []  #[x, y, z, is_active]
FOOD_RADIUS = 8
FOOD_FALL_SPEED = 2.5
FOOD_SPAWN_INTERVAL_MS = 3000
MAX_FOOD_ITEMS = 10

#### feature 13 #########
treasure_mode=False
TREASURE_SIZE = 60
treasure_pos = [0, 0, 0]
TREASURE_STEP = 10  
collison=False

####### feature 12 ###########
TRASH_CAP_START = 10
def get_dynamic_max_fish():
    t = len(trash_items)
    if t < TRASH_CAP_START:
        return MAX_FISH
    steps = 1 + (t - TRASH_CAP_START) // 5   
    return max(0, MAX_FISH - 5 * steps)

####### feature 10 #########
def spawn_food():
    if not fish_list:
        rand_x = random.randint(-GRID_LENGTH // 2, GRID_LENGTH // 2)
        rand_y = random.randint(-GRID_LENGTH // 2, GRID_LENGTH // 2)
    else:
        fish = random.choice(fish_list)
        rand_x = fish["x"]
        rand_y = fish["y"]
    
    food_items.append([rand_x, rand_y, WATER_HEIGHT - 20, True])

def update_and_draw_food():
    global food_items
    if not feeding_mode:
        return
    active_food_count = sum(1 for food in food_items if food[3])
    if active_food_count == 0:
        food_items.clear()
        for _ in range(MAX_FOOD_ITEMS):
            spawn_food()

    for food in food_items:
        if not food[3]:
            continue
        # Move food down
        food[2] -= FOOD_FALL_SPEED
        if food[2] <= 0:
            food[3] = False
            continue
        # Draw food
        glPushMatrix()
        glTranslatef(food[0], food[1], food[2])
        glColor3f(1, 0.3, 0.1) 
        glutSolidSphere(FOOD_RADIUS, 10, 10)
        glPopMatrix()
        # Check collision with fish
        for fish in fish_list:
            dx = food[0] - fish["x"]
            dy = food[1] - fish["y"]
            dz = food[2] - fish["z"]
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            if distance < fish["size"] + 5:
                food[3] = False
                break
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

###### feature 9 #########
def draw_water_volume():
    global is_night_mode
    half = GRID_LENGTH
    overall_base_z = 0.0
    overall_top_z = overall_base_z + WATER_HEIGHT

    # Four layers with colors from darker (bottom) to lighter (top)
    num_layers = 4
    layer_height = WATER_HEIGHT / num_layers
    colors = [
        (0.2, 0.4, 0.6),  
        (0.25, 0.5, 0.7), 
        (0.3, 0.6, 0.8),  
        (0.35, 0.7, 0.9) ]
    night_color= [
       (0.08, 0.24, 0.48),  
       (0.1, 0.3, 0.56),     
       (0.12, 0.36, 0.64),   
       (0.14, 0.42, 0.72)]

    for l in range(num_layers):
        base_z = overall_base_z + l * layer_height
        top_z = base_z + layer_height
        if is_night_mode:
            glColor3f(*night_color[l])
        else:
            glColor3f(*colors[l])
        glBegin(GL_QUADS)
        # +X
        glVertex3f(half, -half, base_z)
        glVertex3f(half, half, base_z)
        glVertex3f(half, half, top_z)
        glVertex3f(half, -half, top_z)
        # -X
        glVertex3f(-half, -half, base_z)
        glVertex3f(-half, half, base_z)
        glVertex3f(-half, half, top_z)
        glVertex3f(-half, -half, top_z)
        # +Y
        glVertex3f(-half, half, base_z)
        glVertex3f(half, half, base_z)
        glVertex3f(half, half, top_z)
        glVertex3f(-half, half, top_z)
        # -Y
        glVertex3f(-half, -half, base_z)
        glVertex3f(half, -half, base_z)
        glVertex3f(half, -half, top_z)
        glVertex3f(-half, -half, top_z)
        glEnd()

    # Wavy surface
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

            z00 = overall_top_z + math.sin((x0*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y0*0.015 - t*1.5)) * WAVE_AMPLITUDE
            z01 = overall_top_z + math.sin((x0*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y1*0.015 - t*1.5)) * WAVE_AMPLITUDE
            z10 = overall_top_z + math.sin((x1*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y0*0.015 - t*1.5)) * WAVE_AMPLITUDE
            z11 = overall_top_z + math.sin((x1*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y1*0.015 - t*1.5)) * WAVE_AMPLITUDE
            if is_night_mode:
                glColor3f(0.0, 0.0, 0.5)
            else:
                glColor3f(0.4, 0.7, 0.9) #light blue
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

####### feature 3 #########
def draw_shark():
    glColor3f(0.4, 0.4, 0.5)  
    w2 = 1.5
  
    glScalef(4.0, 4.0, 4.0)

    p0 = (10, 40)
    p1 = (20, 45)
    p2 = (35, 40)
    p3 = (20, 35)
    p4 = (15, 35)
    p5 = (18, 38)

    glBegin(GL_TRIANGLES)
    # Upper body
    glVertex3f(p0[0], -w2, p0[1])
    glVertex3f(p1[0], -w2, p1[1])
    glVertex3f(p2[0], -w2, p2[1])
    # Lower body
    glVertex3f(p4[0], -w2, p4[1])
    glVertex3f(p3[0], -w2, p3[1])
    glVertex3f(p2[0], -w2, p2[1])
    # Face
    glVertex3f(p0[0], -w2, p0[1])
    glVertex3f(p5[0], -w2, p5[1])
    glVertex3f(p4[0], -w2, p4[1])
    glEnd()

    # Draw back face (y = w2) using triangles
    glBegin(GL_TRIANGLES)
    # Upper body
    glVertex3f(p0[0], w2, p0[1])
    glVertex3f(p1[0], w2, p1[1])
    glVertex3f(p2[0], w2, p2[1])
    # Lower body
    glVertex3f(p4[0], w2, p4[1])
    glVertex3f(p3[0], w2, p3[1])
    glVertex3f(p2[0], w2, p2[1])
    # Face
    glVertex3f(p0[0], w2, p0[1])
    glVertex3f(p5[0], w2, p5[1])
    glVertex3f(p4[0], w2, p4[1])
    glEnd()

    # Draw side faces using quads (connecting front and back)
    body_points = [p0, p1, p2, p3, p4, p5]
    glBegin(GL_QUADS)
    for i in range(len(body_points)):
        x1, z1 = body_points[i]
        x2, z2 = body_points[(i + 1) % len(body_points)]
        glVertex3f(x1, -w2, z1)
        glVertex3f(x2, -w2, z2)
        glVertex3f(x2, w2, z2)
        glVertex3f(x1, w2, z1)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex3f(15, 0, 36)
    glVertex3f(30, 0, 36)
    glVertex3f(18, 0, 55)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex3f(18, 0, 36)
    glVertex3f(20, 0, 7)
    glVertex3f(25, 0, 36)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex3f(35, 0, 40)
    glVertex3f(45, 0, 50)
    glVertex3f(45, 0, 30)
    glEnd()

def spawn_shark():
    x = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
    y = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
    z = random.uniform(100, WATER_HEIGHT - 50)
    angle = random.uniform(0, 360)
    sharks.append([x, y, z, angle])  

def update_sharks(dt):
    global _last_shark_spawn_ms
    now = get_time_ms()
    if len(sharks) < MAX_SHARKS and now - _last_shark_spawn_ms >= SHARK_SPAWN_INTERVAL_MS:
        spawn_shark()
        _last_shark_spawn_ms = now

    new_sharks = []
    for shark in sharks:
        x, y, z, angle = shark
        rad = math.radians(angle)
        dx = -math.cos(rad) * SHARK_SPEED * dt  
        dy = -math.sin(rad) * SHARK_SPEED * dt
        new_x = x + dx
        new_y = y + dy
        if abs(new_x) < GRID_LENGTH and abs(new_y) < GRID_LENGTH:
            shark[0] = new_x
            shark[1] = new_y
            new_sharks.append(shark)
    sharks[:] = new_sharks

def draw_sharks():
    for shark in sharks:
        x, y, z, angle = shark
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(angle, 0, 0, 1)
        draw_shark()
        glPopMatrix()

######## feature 4 ##########
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

###feature 13 ####
###################################################################
def spawn_treasure_bottom():
    global treasure_pos,collison
    x = random.uniform(-GRID_LENGTH, GRID_LENGTH)
    y = random.uniform(-GRID_LENGTH, GRID_LENGTH)
    treasure_pos = [x, y, 0]

def draw_treasure():
    x, y, z = treasure_pos
    glPushMatrix()
    glTranslatef(x, y, z + TREASURE_SIZE / 2)  
    if is_night_mode:
        glColor3f(1.0, 0.6, 0.4)  # brown color
    else:
        glColor3f(1.0, 0.84, 0.0)  
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
    if treasure_mode:
        draw_treasure()
    else:
        for fish in fish_list:
            glEnable(GL_DEPTH_TEST)
            draw_fish(fish["x"], fish["y"], fish["z"], fish["size"], fish["speed"], fish["body_color"], fish["tail_color"], fish["rotation"])
            glDisable(GL_DEPTH_TEST)
        trash_cleaning()
        draw_bubbles()

########### Feature 7 ###############
def setupCamera():
    global camera_radius, camera_angle, camera_height, fp_active, camera
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

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
    speed_multiplier = 10.0 if len(sharks) > 0 else 1.0  # Double fish speed if any shark is present
    for fish in fish_list:
        radians = math.radians(fish["rotation"])
        fish["x"] += fish["speed"] * speed_multiplier * math.cos(radians)  
        fish["y"] += fish["speed"] * speed_multiplier * math.sin(radians) 
        if fish["x"] < -GRID_LENGTH + fish["size"] or fish["x"] > GRID_LENGTH - fish["size"]: 
            fish["rotation"] += 180 
        if fish["y"] < -GRID_LENGTH + fish["size"] or fish["y"] > GRID_LENGTH - fish["size"]:  
            fish["rotation"] += 180  
    if len(fish_list) > MAX_FISH:
        fish_list.pop(0)
    # Enforce dynamic cap derived from MAX_FISH and trash count
    dyn_max = get_dynamic_max_fish()
    while len(fish_list) > dyn_max:
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
    global camera, fp_active, FP_ANGLE, trash_items,draw_trash_enabled, is_night_mode,feeding_mode,_last_trash_spawn_ms,bubble_speed_multiplier,treasure_mode
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
    elif key == b'i':  # Speed up bubbles
        bubble_speed_multiplier *= 2.0
    elif key == b'r':  # Reset bubbles to normal speed
        bubble_speed_multiplier = 1.0
    if key == b'f':
        fp_active = not fp_active  # first-person mode
        return
    elif key == b'c':
        trash_items.clear()
        draw_trash_enabled = True
        _last_trash_spawn_ms = get_time_ms() - TRASH_SPAWN_INTERVAL_MS
        return
    elif key == b't' or key == b'T':  # Toggle treasure mode (works in both modes)
        treasure_mode = not treasure_mode
        if treasure_mode:
            spawn_treasure_bottom()
        print("Treasure Mode:", "ON" if treasure_mode else "OFF")
        return
    
    if not treasure_mode:
        if key == b'i' or key == b'I':  # Speed up bubbles
            bubble_speed_multiplier *= 2.0
        elif key == b'r' or key == b'R':  # Reset bubbles to normal speed
            bubble_speed_multiplier = 1.0
        elif is_night_mode == False:
            for fish in fish_list:
                fish["body_color"] = random.choice(day_colors)
                fish["tail_color"] = random.choice(tail_colors)
        elif is_night_mode == True:
            for fish in fish_list:
                fish["body_color"] = random.choice(neon_colors)
                fish["tail_color"] = random.choice(neon_colors)
    elif treasure_mode:  # In treasure mode
        new_x, new_y = treasure_pos[0], treasure_pos[1]

        if key == b'j' or key == b'J':  # Move left
            new_x -= TREASURE_STEP
        elif key == b'p' or key == b'P':  # Move right
            new_x += TREASURE_STEP
        elif key == b'k' or key == b'K':  # Move forward (+y)
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
    global feeding_mode
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        rand_x = random.randint(-GRID_LENGTH // 2, GRID_LENGTH // 2)
        rand_y = random.randint(-GRID_LENGTH // 2, GRID_LENGTH // 2)
        generate_fish(rand_x, rand_y,random.uniform(150, WATER_HEIGHT - 150)) 
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        feeding_mode = not feeding_mode

def idle():
    global last_update_time
    current_time = time.perf_counter()
    dt = current_time - last_update_time
    last_update_time = current_time
    update_sharks(dt)  
    update_fish_positions() 
    update_bubbles()
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
    update_and_draw_food()
    draw_ocean_objects()
    draw_sharks()
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

