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

fp_active = False
camera = [0.0, 0.0]
EYE_HEIGHT = 150
FP_SPEED   = 25.0
FP_ANGLE   = 0.0
ROT_SPEED  = 5.0

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

SHARK_SCALE = 4.0
SHARK_LOCAL_Z_CENTER = 40.0
SHARK_Z_CATCHUP = 0.08
# Aggro (attack mode when FP cam is near treasure)
SHARK_AGGRO_TRIGGER_DIST = 250.0
SHARK_AGGRO_RELEASE_DIST = 320.0
SHARK_ATTACK_SPEED_MULT  = 1.8
sharks_aggro = False


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
TREASURE_SIZE = 60
treasure_pos = [0, 0, 0]
treasure_mode = False
TREASURE_STEP = 10  #
collison=False
treasure_falling = False
treasure_fall_speed = 0
treasure_start_height = 800
treasure_rotation = 0

MAX_COINS = 500
coins = []
coin_generation_rate = 10.0
coin_speed_multiplier = 1.0
last_coin_time = 0
collected_coins = 0
coins_per_generation = 5

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

    # Draw back face (y = w2)
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

    # Draw side faces
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

def spawn_shark(z_override=None):
    x = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
    y = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
    z = random.uniform(100, WATER_HEIGHT - 50) if z_override is None else z_override
    angle = random.uniform(0, 360)
    sharks.append([x, y, z, angle])

def update_sharks(dt):
    global _last_shark_spawn_ms, sharks_aggro
    now = get_time_ms()

    # Distance-based aggro (FP + near treasure)
    if fp_active and treasure_mode:
        camx, camy = camera[0], camera[1]
        tx,  ty  = treasure_pos[0], treasure_pos[1]
        d2 = (camx - tx) * (camx - tx) + (camy - ty) * (camy - ty)
        if not sharks_aggro and d2 <= (SHARK_AGGRO_TRIGGER_DIST ** 2):
            sharks_aggro = True
        elif sharks_aggro and d2 > (SHARK_AGGRO_RELEASE_DIST ** 2):
            sharks_aggro = False
    else:
        sharks_aggro = False

    # Height we want the shark's pivot at so the BODY aligns with the camera
    target_pivot_z = EYE_HEIGHT - SHARK_LOCAL_Z_CENTER * SHARK_SCALE

    # Spawning (spawn at camera height while aggro)
    if len(sharks) < MAX_SHARKS and now - _last_shark_spawn_ms >= SHARK_SPAWN_INTERVAL_MS:
        if sharks_aggro:
            spawn_shark(z_override=target_pivot_z)
        else:
            spawn_shark()
        _last_shark_spawn_ms = now

    # Update movement
    new_sharks = []
    for shark in sharks:
        x, y, z, angle = shark

        if sharks_aggro:
            # Turn toward camera in XY
            camx, camy = camera[0], camera[1]
            vx, vy = camx - x, camy - y
            target_angle = math.degrees(math.atan2(vy, vx)) + 180.0
            shark[3] = target_angle
            rad = math.radians(target_angle)
            speed = SHARK_SPEED * SHARK_ATTACK_SPEED_MULT

            # Glide Z toward the camera's height (compensated for model offset)
            shark[2] += (target_pivot_z - shark[2]) * SHARK_Z_CATCHUP
            shark[2] = max(50.0, min(WATER_HEIGHT - 50.0, shark[2]))  # keep in water
        else:
            rad = math.radians(angle)
            speed = SHARK_SPEED

        dx = -math.cos(rad) * speed * dt
        dy = -math.sin(rad) * speed * dt
        new_x, new_y = x + dx, y + dy

        if abs(new_x) < GRID_LENGTH and abs(new_y) < GRID_LENGTH:
            shark[0], shark[1] = new_x, new_y
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
def spawn_treasure_bottom():
    global treasure_pos, treasure_falling, treasure_fall_speed, treasure_rotation, coins, collected_coins
    x = random.uniform(-GRID_LENGTH, GRID_LENGTH)
    y = random.uniform(-GRID_LENGTH, GRID_LENGTH)
    treasure_pos = [x, y, treasure_start_height]
    treasure_falling = True
    treasure_fall_speed = 0
    treasure_rotation = 0
    coins = []
    collected_coins = 0
    print("Treasure mode started! Collect gold coins!")
def update_treasure_fall():
    global treasure_pos, treasure_falling, treasure_fall_speed, treasure_rotation

    if treasure_falling:
        treasure_fall_speed += 0.5
        treasure_pos[2] -= treasure_fall_speed
        treasure_rotation += treasure_fall_speed * 0.5

        if treasure_pos[2] <= 0:
            treasure_pos[2] = 0
            treasure_falling = False
            treasure_fall_speed = -treasure_fall_speed * 0.3

            if abs(treasure_fall_speed) < 1:
                treasure_fall_speed = 0

def generate_gold_coins():
    global coins, last_coin_time, coin_generation_rate

    current_time = time.time()
    if current_time - last_coin_time > 0.05:
        last_coin_time = current_time

        if len(coins) < MAX_COINS:
            for _ in range(coins_per_generation):
                x = random.uniform(-GRID_LENGTH, GRID_LENGTH)
                y = random.uniform(-GRID_LENGTH, GRID_LENGTH)
                z = WATER_HEIGHT + random.uniform(50, 200)

                coins.append([
                    x, y, z,
                    random.uniform(0, 360),
                    random.uniform(1.5, 4.0) * coin_speed_multiplier,
                    False])

def update_gold_coins():
    global coins, collected_coins

    for i in range(len(coins)-1, -1, -1):
        if coins[i][5]:
            coins.pop(i)
            continue

        # Update coin position
        coins[i][2] -= coins[i][4]
        coins[i][3] += coins[i][4] * 4

        tx, ty, tz = treasure_pos
        treasure_x_min = tx - TREASURE_SIZE/2
        treasure_x_max = tx + TREASURE_SIZE/2
        treasure_y_min = ty - TREASURE_SIZE/2
        treasure_y_max = ty + TREASURE_SIZE/2
        treasure_z_min = tz
        treasure_z_max = tz + TREASURE_SIZE

        coin_x, coin_y, coin_z = coins[i][0], coins[i][1], coins[i][2]

        if (treasure_x_min <= coin_x <= treasure_x_max and
            treasure_y_min <= coin_y <= treasure_y_max and
            treasure_z_min <= coin_z <= treasure_z_max):
            coins[i][5] = True
            collected_coins += 1
            if collected_coins % 10 == 0:
                print(f"Coins collected: {collected_coins}")
            continue

        if coins[i][2] <= 0:
            coins.pop(i)

def check_wall_collision(new_x, new_y):

    half = GRID_LENGTH
    if new_x - TREASURE_SIZE/2 < -half or new_x + TREASURE_SIZE/2 > half:
        return True
    if new_y - TREASURE_SIZE/2 < -half or new_y + TREASURE_SIZE/2 > half:
        return True
    return False

def check_obstacle_collision(x, y):

    for cx, cy in coral_positions:
        if abs(x - cx) < TREASURE_SIZE + 15 and abs(y - cy) < TREASURE_SIZE + 15:
            return True
    for rx, ry in rock_positions:
        if abs(x - rx) < TREASURE_SIZE + 25 and abs(y - ry) < TREASURE_SIZE + 25:
            return True
    return False

def draw_gold_coin(x, y, z, rotation, collected=False):
    if collected:
        return
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)

    # Gold coin color
    if is_night_mode:
        glColor3f(1, 1, 1)  # White for night mode
    else:
        glColor3f(1.0, 0.84, 0.0)  # Gold color
    # Draw the main body of the coin
    glPushMatrix()
    glScalef(3, 3, 0.4)
    glutSolidSphere(1, 16, 8)
    glPopMatrix()

    glPopMatrix()
def draw_treasure():
    x, y, z = treasure_pos
    glPushMatrix()
    glTranslatef(x, y, z + TREASURE_SIZE / 2)
    if treasure_falling:
        glRotatef(treasure_rotation, 1, 0.5, 0.2)

    if is_night_mode:
        glColor3f(0.5, 0.35, 0.2)  # brown color
    else:
        glColor3f(1.0, 0.84, 0.0)  # gold color

    # Draw the treasure box
    glutSolidCube(TREASURE_SIZE)

    # Draw a simple lock
    glPushMatrix()
    glTranslatef(0, TREASURE_SIZE/2 - 5, TREASURE_SIZE/4)
    glColor3f(0.3, 0.3, 0.3)
    glutSolidCube(10)
    glPopMatrix()

    glPopMatrix()

def draw_gold_coins():
    for coin in coins:
        draw_gold_coin(coin[0], coin[1], coin[2], coin[3], coin[5])

def draw_shapes():
    draw_water_volume()
    if treasure_mode:
        draw_treasure()
        draw_gold_coins()
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
    # Fish body
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(body_color[0], body_color[1], body_color[2])
    gluSphere(gluNewQuadric(), size, 20, 20)
    glPopMatrix()

    # Draw fish tail using triangles
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)

    # Calculate tail vertices
    tail_length = size * 1.2
    tail_width = size * 0.8

    # Tail vertices
    tail_base_left = (size, -tail_width/2, 0)
    tail_base_right = (size, tail_width/2, 0)
    tail_tip = (size + tail_length, 0, 0)

    # Draw tail
    glColor3f(tail_color[0], tail_color[1], tail_color[2])
    glBegin(GL_TRIANGLES)
    glVertex3f(*tail_base_left)
    glVertex3f(*tail_base_right)
    glVertex3f(*tail_tip)
    glEnd()
    glPopMatrix()

    # Draw top fin using triangles
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)

    # Fin vertices
    fin_base_front = (-size/2, 0, size/2)
    fin_base_back = (size/3, 0, size/2)
    fin_tip = (0, 0, size + size/2)

    glColor3f(tail_color[0], tail_color[1], tail_color[2])
    glBegin(GL_TRIANGLES)
    glVertex3f(*fin_base_front)
    glVertex3f(*fin_base_back)
    glVertex3f(*fin_tip)
    glEnd()
    glPopMatrix()

    # Draw bottom fin using triangles
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)

    # Fin vertices
    fin_base_front = (-size/2, 0, -size/2)
    fin_base_back = (size/3, 0, -size/2)
    fin_tip = (0, 0, -size - size/2)

    glColor3f(tail_color[0], tail_color[1], tail_color[2])
    glBegin(GL_TRIANGLES)
    glVertex3f(*fin_base_front)
    glVertex3f(*fin_base_back)
    glVertex3f(*fin_tip)
    glEnd()
    glPopMatrix()

    # Draw side fins using triangles
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)

    # Left fin
    fin_base_near = (-size/2, -size/2, 0)
    fin_base_far = (size/4, -size/2, 0)
    fin_tip = (0, -size, 0)

    glColor3f(tail_color[0], tail_color[1], tail_color[2])
    glBegin(GL_TRIANGLES)
    glVertex3f(*fin_base_near)
    glVertex3f(*fin_base_far)
    glVertex3f(*fin_tip)
    glEnd()

    # Right fin
    fin_base_near = (-size/2, size/2, 0)
    fin_base_far = (size/4, size/2, 0)
    fin_tip = (0, size, 0)

    glBegin(GL_TRIANGLES)
    glVertex3f(*fin_base_near)
    glVertex3f(*fin_base_far)
    glVertex3f(*fin_tip)
    glEnd()
    glPopMatrix()

    # Draw fish eyes
    glPushMatrix()
    glTranslatef(x + size * 0.5, y + size * 0.3, z + size * 0.3)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), size * 0.1, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(x + size * 0.5, y - size * 0.3, z + size * 0.3)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), size * 0.1, 10, 10)
    glPopMatrix()

def update_fish_positions():
    global fish_list,feeding_mode
    speed_multiplier = 10.0 if len(sharks) and not feeding_mode > 0 else 1.0  # Double fish speed if any shark is present
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
    global camera, fp_active, FP_ANGLE, trash_items,draw_trash_enabled,feeding_mode,_last_trash_spawn_ms,bubble_speed_multiplier
    global treasure_mode, treasure_pos, is_night_mode, coin_speed_multiplier, coin_generation_rate, collected_coins

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
    elif key == b'e':  # Speed up bubbles
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
    elif key == b't' or key == b'T':
        if treasure_mode:
            # Print final score when closing treasure mode
            print(f"Treasure mode closed! Total coins collected: {collected_coins}")
        treasure_mode = not treasure_mode
        if treasure_mode:
            spawn_treasure_bottom()
        else:
            print(f"Final score: {collected_coins} coins collected!")
    elif key == b'z' or key == b'Z':
        coin_speed_multiplier += 0.5
        print(f"Coin speed increased to: {coin_speed_multiplier}")
    elif key == b'x' or key == b'X':
        coin_speed_multiplier = 1.0
        print("Coin speed reset to normal")

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
            print(f"Treasure mode closed! Total coins collected: {collected_coins}")
            treasure_mode = False
            return

        if check_wall_collision(new_x, new_y):
            print("Hit the wall! Movement blocked.")
            return

        if check_obstacle_collision(new_x, new_y):
            print("Hit an obstacle! Treasure will respawn.")
            spawn_treasure_bottom()
            return

        treasure_pos[0] = new_x
        treasure_pos[1] = new_y

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

    if treasure_falling:
        update_treasure_fall()

    if treasure_mode and not treasure_falling:
        generate_gold_coins()
        update_gold_coins()
    glutPostRedisplay()

NUM_STARS = 200
star_positions = [( random.uniform(-GRID_LENGTH * 2, GRID_LENGTH * 2),
    random.uniform(-GRID_LENGTH * 2, GRID_LENGTH * 2),
    random.uniform(WATER_HEIGHT + 300, WATER_HEIGHT + 1200))
    for _ in range(NUM_STARS)]

def draw_stars_and_sun():
    global star_positions
    if not is_night_mode:
        # Draw Sun
        glPushMatrix()
        glTranslatef(-GRID_LENGTH, -1500, 1500)
        glColor3f(1.0, 1.0, 0.0)
        glScalef(1.5, 1.5, 1.5)
        glutSolidSphere(40, 40, 40)
        glPopMatrix()
    else:
        glColor3f(1.0, 1.0, 1.0)
        glPointSize(0.5)
        glBegin(GL_POINTS)
        for x, y, z in star_positions:
            glVertex3f(x, y, z)
        glEnd()
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
    if not feeding_mode:
        draw_sharks()
    draw_stars_and_sun()
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

