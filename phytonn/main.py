import pygame
import random
import cv2
import mediapipe as mp
import numpy as np

# ================= INIT =================
pygame.init()

# ================= WINDOW =================
WIDTH, HEIGHT = 1000, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Particle Visualizer")

clock = pygame.time.Clock()

# ================= COLORS =================
BLACK = (0, 0, 0)
PINK = (255, 170, 220)
WHITE = (255, 255, 255)

# ================= FONT =================
font = pygame.font.SysFont("Arial", 90, bold=True)

# ================= PARTICLE =================
class Particle:

    def __init__(self):

        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)

        self.tx = self.x
        self.ty = self.y

        self.size = random.randint(1, 2)

        self.speed = random.uniform(0.03, 0.08)

    def move(self):

        self.x += (self.tx - self.x) * self.speed
        self.y += (self.ty - self.y) * self.speed

    def draw(self, surface):

        glow = pygame.Surface((10, 10), pygame.SRCALPHA)

        pygame.draw.circle(
            glow,
            (255, 180, 220, 40),
            (5, 5),
            5
        )

        surface.blit(glow, (self.x - 5, self.y - 5))

        pygame.draw.circle(
            surface,
            PINK,
            (int(self.x), int(self.y)),
            self.size
        )

# ================= PARTICLES =================
particles = [Particle() for _ in range(3500)]

# ================= TEXT POINTS =================
def create_text_points(text):

    text_surface = font.render(text, True, WHITE)

    mask = pygame.mask.from_surface(text_surface)

    points = []

    for x in range(0, text_surface.get_width(), 5):
        for y in range(0, text_surface.get_height(), 5):

            if mask.get_at((x, y)):

                px = WIDTH // 2 - text_surface.get_width() // 2 + x
                py = HEIGHT // 2 - text_surface.get_height() // 2 + y

                points.append((px, py))

    return points

# ================= PARTICLE MODES =================
def scatter_particles():

    for p in particles:

        p.tx = random.randint(0, WIDTH)
        p.ty = random.randint(0, HEIGHT)

def center_particles():

    for p in particles:

        p.tx = WIDTH // 2
        p.ty = HEIGHT // 2

def text_particles(text):

    points = create_text_points(text)

    for i, p in enumerate(particles):

        target = points[i % len(points)]

        p.tx, p.ty = target

# ================= CAMERA =================
cap = cv2.VideoCapture(0)

# ================= MEDIAPIPE =================
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# ================= DETECT FINGER =================
def finger_up(landmarks, tip, pip):

    return landmarks[tip].y < landmarks[pip].y

# ================= GESTURE =================
def detect_gesture(hand_landmarks):

    lm = hand_landmarks.landmark

    thumb = lm[4].x < lm[3].x
    index = finger_up(lm, 8, 6)
    middle = finger_up(lm, 12, 10)
    ring = finger_up(lm, 16, 14)
    pinky = finger_up(lm, 20, 18)

    fingers = [thumb, index, middle, ring, pinky]

    # ✊ Kepal
    if fingers == [False, False, False, False, False]:
        return "fist"

    # 🖐 Lima jari
    if fingers == [True, True, True, True, True]:
        return "five"

    # 👍 Jempol
    if fingers == [True, False, False, False, False]:
        return "thumb"

    # 🤟 Metal
    if fingers == [True, True, False, False, True]:
        return "metal"

    return "none"

# ================= START =================
scatter_particles()

current_mode = "scatter"

running = True

# ================= MAIN LOOP =================
while running:

    screen.fill(BLACK)

    # ================= EVENTS =================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

    # ================= CAMERA =================
    ret, frame = cap.read()

    if ret:

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb)

        gesture = "none"

        # ================= HAND DETECTION =================
        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                gesture = detect_gesture(hand_landmarks)

                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

        # ================= GESTURE ACTION =================
        if gesture == "fist":

            if current_mode != "fist":

                center_particles()

                current_mode = "fist"

        elif gesture == "five":

            if current_mode != "five":

                text_particles("HAIII!!!")

                current_mode = "five"
 
        elif gesture == "thumb":

            if current_mode != "thumb":

                text_particles("I'M JANE")

                current_mode = "thumb"

        elif gesture == "metal":

            if current_mode != "metal":

                text_particles("I LOVE YOU")

                current_mode = "metal"

        else:

            if current_mode != "scatter":

                scatter_particles()

                current_mode = "scatter"

        # ================= CAMERA PREVIEW =================
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame = np.rot90(frame)

        frame_surface = pygame.surfarray.make_surface(frame)

        frame_surface = pygame.transform.scale(
            frame_surface,
            (250, 180)
        )

        screen.blit(frame_surface, (20, 20))

    # ================= PARTICLES =================
    camera_area = pygame.Rect(20, 20, 250, 180)

    for p in particles:

        p.move()

        if not camera_area.collidepoint(p.x, p.y):
            p.draw(screen)

    # ================= CAMERA BORDER =================
    pygame.draw.rect(
        screen,
        PINK,
        (20, 20, 250, 180),
        3
    )

    # ================= UPDATE =================
    pygame.display.flip()

    clock.tick(60)

# ================= CLOSE =================
cap.release()

pygame.quit()
