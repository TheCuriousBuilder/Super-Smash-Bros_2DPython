import pygame
import random

pygame.init()

# =========================
# WINDOW
# =========================
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Smash")
clock = pygame.time.Clock()

# =========================
# STATES
# =========================
MENU = 0
PLAYING = 1
GAME_OVER = 2

game_state = MENU

# =========================
# COLORS
# =========================
WHITE=(255,255,255)
BLACK=(0,0,0)
RED=(220,70,70)
BLUE=(70,120,255)
GREEN=(60,220,100)
YELLOW=(255,220,50)
SKY=(120,190,255)

# =========================
# FONTS
# =========================
title_font = pygame.font.SysFont(None, 72)
menu_font = pygame.font.SysFont(None, 40)
hud_font = pygame.font.SysFont(None, 30)

# =========================
# DIFFICULTY
# =========================
DIFFICULTIES = ["EASY","MEDIUM","HARD"]
difficulty_index = 0

# =========================
# PHYSICS
# =========================
GRAVITY = 0.7
MOVE_SPEED = 6
JUMP_POWER = -15

BASE_KB = 6
KB_SCALE = 0.35

# =========================
# STAGE
# =========================
platforms = [
    pygame.Rect(0,580,1000,70),
    pygame.Rect(250,430,180,18),
    pygame.Rect(570,430,180,18),
    pygame.Rect(410,300,180,18),
]

particles = []
projectiles = []

winner_text = ""

# =========================
# PARTICLE
# =========================
class Particle:

    def __init__(self,x,y,color):
        self.x=x
        self.y=y
        self.vx=random.uniform(-4,4)
        self.vy=random.uniform(-4,4)
        self.life=25
        self.color=color

    def update(self):
        self.x+=self.vx
        self.y+=self.vy
        self.vy+=0.15
        self.life-=1

    def draw(self):
        if self.life>0:
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.x),int(self.y)),
                3
            )

# =========================
# PROJECTILE
# =========================
class Projectile:

    def __init__(self,x,y,direction,owner):
        self.owner=owner
        self.rect=pygame.Rect(x,y,32,32)
        self.vx=10*direction

    def update(self):
        self.rect.x+=self.vx

    def draw(self):
        pygame.draw.rect(
            screen,
            YELLOW,
            self.rect,
            border_radius=6
        )

# =========================
# PLAYER
# =========================
class Player:

    def __init__(
        self,
        x,
        y,
        color,
        controls=None,
        ai=False,
        difficulty="EASY"
    ):

        self.rect=pygame.Rect(x,y,50,60)

        self.color=color
        self.controls=controls

        self.ai=ai
        self.difficulty=difficulty

        self.vx=0
        self.vy=0

        self.damage=0
        self.stocks=3

        self.hitstun=0
        self.on_ground=False

        self.special_cd=0

        self.facing=1

    def update(self,keys,opponent):

        if self.hitstun>0:
            self.hitstun-=1

        if self.special_cd>0:
            self.special_cd-=1

        self.vy+=GRAVITY

        if self.ai:
            self.ai_logic(opponent)
        else:
            self.player_input(keys,opponent)

        self.rect.x+=int(self.vx)
        self.rect.y+=int(self.vy)

        self.platform_collision()

    def player_input(self,keys,opponent):

        if self.hitstun>0:
            return

        if keys[self.controls["left"]]:
            self.vx=-MOVE_SPEED
            self.facing=-1

        elif keys[self.controls["right"]]:
            self.vx=MOVE_SPEED
            self.facing=1

        else:
            self.vx*=0.85

        if keys[self.controls["jump"]]:
            if self.on_ground:
                self.vy=JUMP_POWER
                self.on_ground=False

        if keys[self.controls["attack"]]:
            self.attack(opponent)

        if keys[self.controls["special"]]:
            self.special()

    def ai_logic(self,opponent):

        if self.hitstun>0:
            return

        if self.difficulty == "EASY":
            speed = 3
            attack_chance = 0.50
            special_chance = 0.

        elif self.difficulty == "MEDIUM":
            speed = 6
            attack_chance = 0.75
            special_chance = 0.40

        else:  # HARD
            speed = 10
            attack_chance = 1
            special_chance = 0.5

        dx=opponent.rect.centerx-self.rect.centerx

        if abs(dx)>80:
            self.vx=speed if dx>0 else -speed
            self.facing=1 if dx>0 else -1
        else:
            self.vx*=0.8

            if random.random() < attack_chance:
                self.attack(opponent)

        if (
            opponent.rect.y <
            self.rect.y-20 and
            self.on_ground
        ):
            self.vy=JUMP_POWER

        if self.special_cd == 0 and random.random() < special_chance:
            self.special()

    def attack(self,opponent):

        hitbox=pygame.Rect(
            self.rect.centerx+self.facing*35,
            self.rect.y+10,
            45,
            30
        )

        if hitbox.colliderect(opponent.rect):
            opponent.take_hit(self)

    def special(self):

        if self.special_cd>0:
            return

        projectiles.append(
            Projectile(
                self.rect.centerx,
                self.rect.centery,
                self.facing,
                self
            )
        )

        self.special_cd=120

    def take_hit(self,attacker):

        self.damage+=10

        power=BASE_KB+self.damage*KB_SCALE

        direction=1

        if attacker.rect.centerx>self.rect.centerx:
            direction=-1

        self.vx=direction*power
        self.vy=-power*0.7

        self.hitstun=10+int(self.damage*0.12)

        for _ in range(15):
            particles.append(
                Particle(
                    self.rect.centerx,
                    self.rect.centery,
                    self.color
                )
            )
    def platform_collision(self):

        self.on_ground = False

        for platform in platforms:

            if (
                self.rect.colliderect(platform)
                and self.vy > 0
            ):
                self.rect.bottom = platform.top
                self.vy = 0
                self.on_ground = True

        if self.on_ground:
            self.vx *= 0.88

    def check_ko(self):

        if (
            self.rect.y > HEIGHT + 200
            or self.rect.x < -300
            or self.rect.x > WIDTH + 300
        ):
            self.stocks -= 1
            self.damage = 0

            if self.ai:
                self.rect.center = (750, 200)
            else:
                self.rect.center = (250, 200)

            self.vx = 0
            self.vy = 0

    def draw(self):

        outline = pygame.Rect(
            self.rect.x - 2,
            self.rect.y - 2,
            self.rect.width + 4,
            self.rect.height + 4
        )

        pygame.draw.rect(
            screen,
            BLACK,
            outline,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=8
        )

        eye_x = self.rect.centerx + (8 * self.facing)

        pygame.draw.circle(
            screen,
            WHITE,
            (eye_x, self.rect.y + 18),
            4
        )

# =========================
# DRAWING
# =========================
def draw_background():

    screen.fill(SKY)

    pygame.draw.circle(
        screen,
        (255,240,120),
        (850,100),
        50
    )

    pygame.draw.rect(
        screen,
        (90,180,90),
        (0,560,WIDTH,90)
    )

def draw_stage():

    for platform in platforms:

        shadow = pygame.Rect(
            platform.x,
            platform.y + 4,
            platform.width,
            platform.height
        )

        pygame.draw.rect(
            screen,
            (40,40,40),
            shadow,
            border_radius=4
        )

        pygame.draw.rect(
            screen,
            (90,90,90),
            platform,
            border_radius=4
        )

def update_particles():

    for particle in particles[:]:

        particle.update()

        if particle.life <= 0:
            particles.remove(particle)

def draw_particles():

    for particle in particles:
        particle.draw()

def update_projectiles(player, ai):

    for projectile in projectiles[:]:

        projectile.update()

        if projectile.rect.right < -50:
            projectiles.remove(projectile)
            continue

        if projectile.rect.left > WIDTH + 50:
            projectiles.remove(projectile)
            continue

        if (
            projectile.owner != player
            and projectile.rect.colliderect(player.rect)
        ):
            player.take_hit(projectile.owner)

            if projectile in projectiles:
                projectiles.remove(projectile)

        elif (
            projectile.owner != ai
            and projectile.rect.colliderect(ai.rect)
        ):
            ai.take_hit(projectile.owner)

            if projectile in projectiles:
                projectiles.remove(projectile)

def draw_projectiles():

    for projectile in projectiles:
        projectile.draw()

# =========================
# HUD
# =========================
def draw_hud(player, ai):

    player_text = hud_font.render(
        f"PLAYER {player.damage}%",
        True,
        BLACK
    )

    screen.blit(player_text, (20,20))

    player_stocks = hud_font.render(
        f"STOCKS: {player.stocks}",
        True,
        BLACK
    )

    screen.blit(player_stocks, (20,50))

    ai_text = hud_font.render(
        f"AI {ai.damage}%",
        True,
        BLACK
    )

    screen.blit(ai_text, (820,20))

    ai_stocks = hud_font.render(
        f"STOCKS: {ai.stocks}",
        True,
        BLACK
    )

    screen.blit(ai_stocks, (820,50))

    # special bar
    pygame.draw.rect(
        screen,
        BLACK,
        (20,90,200,18)
    )

    progress = max(
        0,
        200 * (1 - player.special_cd / 120)
    )

    pygame.draw.rect(
        screen,
        YELLOW,
        (20,90,progress,18)
    )

# =========================
# MENU
# =========================
def draw_menu():

    screen.fill((20,20,40))

    title = title_font.render(
        "PYTHON SMASH",
        True,
        WHITE
    )

    screen.blit(title, (250,120))

    for i, diff in enumerate(DIFFICULTIES):

        selected = (i == difficulty_index)

        color = WHITE

        if selected:

            if diff == "EASY":
                color = GREEN

            elif diff == "MEDIUM":
                color = YELLOW

            else:
                color = RED

        prefix = "> " if selected else "  "

        text = menu_font.render(
            prefix + diff,
            True,
            color
        )

        screen.blit(
            text,
            (400,300 + i * 60)
        )

    start = menu_font.render(
        "ENTER TO START",
        True,
        WHITE
    )

    screen.blit(start, (330,520))

# =========================
# WIN SCREEN
# =========================
def draw_game_over():

    screen.fill((10,10,25))

    title = title_font.render(
        winner_text,
        True,
        WHITE
    )

    screen.blit(
        title,
        (
            WIDTH//2 - title.get_width()//2,
            180
        )
    )

    restart = menu_font.render(
        "PRESS R FOR MENU",
        True,
        WHITE
    )

    screen.blit(
        restart,
        (
            WIDTH//2 - restart.get_width()//2,
            320
        )
    )

# =========================
# CONTROLS
# =========================
controls = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "jump": pygame.K_w,
    "attack": pygame.K_j,
    "special": pygame.K_k
}

player = None
ai = None

def start_match():

    global player
    global ai

    difficulty = DIFFICULTIES[difficulty_index]

    particles.clear()
    projectiles.clear()

    player = Player(
        250,
        200,
        BLUE,
        controls,
        False
    )

    ai = Player(
        750,
        200,
        RED,
        None,
        True,
        difficulty
    )

# =========================
# MAIN LOOP
# =========================
running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if game_state == MENU:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    difficulty_index = max(
                        0,
                        difficulty_index - 1
                    )

                elif event.key == pygame.K_DOWN:
                    difficulty_index = min(
                        len(DIFFICULTIES)-1,
                        difficulty_index + 1
                    )

                elif event.key == pygame.K_RETURN:

                    start_match()
                    game_state = PLAYING

        elif game_state == GAME_OVER:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    game_state = MENU

    # MENU
    if game_state == MENU:

        draw_menu()
        pygame.display.flip()
        continue

    # GAME OVER
    if game_state == GAME_OVER:

        draw_game_over()
        pygame.display.flip()
        continue

    # PLAYING
    keys = pygame.key.get_pressed()

    player.update(keys, ai)
    ai.update(None, player)

    player.check_ko()
    ai.check_ko()

    update_projectiles(player, ai)
    update_particles()

    if player.stocks <= 0:
        winner_text = "AI WINS!"
        game_state = GAME_OVER

    elif ai.stocks <= 0:
        winner_text = "PLAYER WINS!"
        game_state = GAME_OVER

    draw_background()
    draw_stage()

    draw_projectiles()
    draw_particles()

    player.draw()
    ai.draw()

    draw_hud(player, ai)

    pygame.display.flip()

pygame.quit()
