import pygame
import random
import math

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

pygame.init()

SOUND_OK = False
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    SOUND_OK = True
except Exception:
    SOUND_OK = False

# =========================
# WINDOW
# =========================
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Smash")
clock = pygame.time.Clock()

render_surface = pygame.Surface((WIDTH, HEIGHT))

# =========================
# STATES
# =========================
MODE_SELECT = -1
MENU = 0
PLAYING = 1
GAME_OVER = 2
CHAR_SELECT = 3
STAGE_SELECT = 4

game_state = MODE_SELECT

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
ORANGE=(255,150,50)

# =========================
# FONTS
# =========================
title_font = pygame.font.SysFont(None, 72)
menu_font = pygame.font.SysFont(None, 40)
hud_font = pygame.font.SysFont(None, 30)

# =========================
# SOUND
# =========================
def make_tone(freq=440, duration=0.08, volume=0.4):
    if not (SOUND_OK and HAS_NUMPY):
        return None
    try:
        sample_rate = 44100
        n = int(sample_rate * duration)
        t = np.linspace(0, duration, n, False)
        tone = np.sin(freq * t * 2 * np.pi)
        fade = np.linspace(1, 0, n)
        audio = (tone * fade * volume * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(audio)
    except Exception:
        return None

SOUNDS = {
    "jump": make_tone(520, 0.07, 0.3),
    "hit": make_tone(150, 0.09, 0.45),
    "grab": make_tone(300, 0.08, 0.4),
    "ko": make_tone(110, 0.35, 0.5),
    "select": make_tone(700, 0.04, 0.25),
    "confirm": make_tone(900, 0.08, 0.3),
    "shield_break": make_tone(90, 0.3, 0.45),
}

def play_sound(name):
    snd = SOUNDS.get(name)
    if snd:
        try:
            snd.play()
        except Exception:
            pass

# =========================
# DIFFICULTY
# =========================
DIFFICULTIES = ["EASY","MEDIUM","HARD"]
difficulty_index = 0

# =========================
# CHARACTERS (ability + debuff)
# =========================
CHARACTERS = [
    {
        "name": "BLAZE",
        "ability": "Quick Feet: +30% move speed",
        "debuff": "Fragile: takes +20% knockback",
        "speed_mult": 1.3, "weight_mult": 0.83, "jump_mult": 1.0,
        "special_cd_mult": 1.0, "jab_dmg_mult": 1.0, "air_jump_bonus": 0,
        "shield_mult": 1.0, "shield_regen_mult": 1.0, "grab_range_mult": 1.0, "rage_mult": 1.0,
    },
    {
        "name": "TITAN",
        "ability": "Heavyweight: takes -25% knockback",
        "debuff": "Slow: -25% speed, lower jumps",
        "speed_mult": 0.75, "weight_mult": 1.35, "jump_mult": 0.85,
        "special_cd_mult": 1.0, "jab_dmg_mult": 1.0, "air_jump_bonus": 0,
        "shield_mult": 1.0, "shield_regen_mult": 1.0, "grab_range_mult": 1.0, "rage_mult": 1.0,
    },
    {
        "name": "VOLT",
        "ability": "Energized: special recharges 2x faster",
        "debuff": "Glass Cannon: -40% jab damage",
        "speed_mult": 1.0, "weight_mult": 1.0, "jump_mult": 1.0,
        "special_cd_mult": 0.5, "jab_dmg_mult": 0.6, "air_jump_bonus": 0,
        "shield_mult": 1.0, "shield_regen_mult": 1.0, "grab_range_mult": 1.0, "rage_mult": 1.0,
    },
    {
        "name": "ACE",
        "ability": "Aerialist: +1 extra air jump",
        "debuff": "Weak Guard: -40% shield HP",
        "speed_mult": 1.0, "weight_mult": 1.0, "jump_mult": 1.0,
        "special_cd_mult": 1.0, "jab_dmg_mult": 1.0, "air_jump_bonus": 1,
        "shield_mult": 0.6, "shield_regen_mult": 1.0, "grab_range_mult": 1.0, "rage_mult": 1.0,
    },
    {
        "name": "HOOK",
        "ability": "Long Reach: +40% grab range",
        "debuff": "Brittle Guard: -30% shield regen",
        "speed_mult": 1.0, "weight_mult": 1.0, "jump_mult": 1.0,
        "special_cd_mult": 1.0, "jab_dmg_mult": 1.0, "air_jump_bonus": 0,
        "shield_mult": 1.0, "shield_regen_mult": 0.7, "grab_range_mult": 1.4, "rage_mult": 1.0,
    },
    {
        "name": "NOVA",
        "ability": "Berserker: rage builds 2x faster",
        "debuff": "Short Fuse: special cooldown +50%",
        "speed_mult": 1.0, "weight_mult": 1.0, "jump_mult": 1.0,
        "special_cd_mult": 1.5, "jab_dmg_mult": 1.0, "air_jump_bonus": 0,
        "shield_mult": 1.0, "shield_regen_mult": 1.0, "grab_range_mult": 1.0, "rage_mult": 2.0,
    },
]

char_index = 0
char_index2 = 0
selecting_player = 1

# =========================
# STAGES
# =========================
def make_stage_battlefield():
    return [
        pygame.Rect(0,580,1000,70),
        pygame.Rect(250,430,180,18),
        pygame.Rect(570,430,180,18),
        pygame.Rect(410,300,180,18),
    ]

def make_stage_final():
    return [
        pygame.Rect(0,580,1000,70),
    ]

def make_stage_sky():
    return [
        pygame.Rect(0,580,1000,70),
        pygame.Rect(120,400,160,18),
        pygame.Rect(720,400,160,18),
        pygame.Rect(400,260,160,18),
    ]

STAGES = [
    {"name":"BATTLEFIELD", "build":make_stage_battlefield, "moving_index":None},
    {"name":"FINAL STAGE", "build":make_stage_final, "moving_index":None},
    {"name":"SKY ARENA", "build":make_stage_sky, "moving_index":3, "move_range":(250,650), "move_speed":2.2},
]
stage_index = 0
moving_platform_dir = 1

# =========================
# PHYSICS
# =========================
GRAVITY = 0.7
FAST_FALL_GRAVITY = 1.6
MOVE_SPEED = 6
JUMP_POWER = -15
AIR_JUMP_POWER = -13
MAX_AIR_JUMPS = 1
BASE_WEIGHT = 100

def calc_knockback(percent_after_hit, move_damage, kb_base, kb_growth, weight):
    p = percent_after_hit
    kb = (((p / 10) + (p * move_damage / 20)) * (200 / (weight + 100)) * 1.4 + 18) * kb_growth + kb_base
    return kb

JAB_MOVE = {"damage": 8, "kb_base": 8, "kb_growth": 1.0, "angle": 35}
SPECIAL_MOVE = {"damage": 8, "kb_base": 10, "kb_growth": 1.0, "angle": 38}
GRAB_MOVE = {"damage": 7, "kb_base": 13, "kb_growth": 1.0, "angle": 20}

SHIELD_MAX = 100
SHIELD_DRAIN = 1.1
SHIELD_REGEN = 0.5
SPOT_DODGE_FRAMES = 18
SPOT_DODGE_COOLDOWN = 40
GRAB_RANGE = 70
GRAB_COOLDOWN = 40
LEDGE_SAVE_FRAMES = 30
LEDGE_COOLDOWN = 70

LEDGE_LEFT_X = 0
LEDGE_RIGHT_X = 0
LEDGE_Y = 0

# =========================
# RUNTIME STATE
# =========================
platforms = []
particles = []
projectiles = []
combo_popups = []

winner_text = ""
mode = "AI"
label1 = "PLAYER"
label2 = "AI"

hit_pause_timer = 0
shake_timer = 0

p1 = None
p2 = None

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
        difficulty="EASY",
        character=None
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

        # --- character stats (ability + debuff) ---
        character = character or CHARACTERS[0]
        self.character = character
        self.move_speed = MOVE_SPEED * character["speed_mult"]
        self.jump_power = JUMP_POWER * character["jump_mult"]
        self.air_jump_power = AIR_JUMP_POWER * character["jump_mult"]
        self.weight = BASE_WEIGHT * character["weight_mult"]
        self.special_cd_max = int(120 * character["special_cd_mult"])
        self.jab_damage = JAB_MOVE["damage"] * character["jab_dmg_mult"]
        self.max_air_jumps = MAX_AIR_JUMPS + character["air_jump_bonus"]
        self.shield_max = SHIELD_MAX * character["shield_mult"]
        self.shield_regen = SHIELD_REGEN * character["shield_regen_mult"]
        self.grab_range = GRAB_RANGE * character["grab_range_mult"]
        self.rage_mult = character["rage_mult"]

        # --- smash-style additions ---
        self.air_jumps_left = self.max_air_jumps
        self.fast_falling = False

        self.shielding = False
        self.shield_hp = self.shield_max
        self.shield_broken_timer = 0

        self.dodge_frames = 0
        self.dodge_cd = 0
        self.invincible = False

        self.grab_cd = 0
        self.ledge_cd = 0

        self.grabbing = False
        self.grabbed = False
        self.grab_timer = 0

        self.squash = 0.0

        self.prev_jump_held = False
        self.prev_shield_held = False

        # stats / combo tracking
        self.damage_dealt = 0.0
        self.biggest_hit = 0.0
        self.combo_count = 0
        self.max_combo = 0
        self.combo_target = None
        self.combo_timer = 0
        self.attack_cd = 0
        self.coyote_timer = 0
        self.jump_buffer = 0

    def update(self,keys,opponent):

        if self.grabbed:
            self.vx = 0
            self.vy = 0
            self.grab_timer -= 1
            if self.grab_timer <= 0:
                self.grabbed = False
            return

        if self.grabbing:
            self.grab_timer -= 1
            if self.grab_timer <= 0:
                self.grabbing = False

        if self.hitstun>0:
            self.hitstun-=1

        if self.special_cd>0:
            self.special_cd-=1

        if self.attack_cd > 0:
            self.attack_cd -= 1

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0
            self.combo_target = None

        if self.shield_broken_timer>0:
            self.shield_broken_timer-=1

        if self.dodge_frames>0:
            self.dodge_frames-=1
            if self.dodge_frames==0:
                self.invincible=False

        if self.dodge_cd>0:
            self.dodge_cd-=1

        if self.grab_cd>0:
            self.grab_cd-=1

        if self.ledge_cd>0:
            self.ledge_cd-=1

        if not self.shielding:
            self.shield_hp = min(self.shield_max, self.shield_hp + self.shield_regen)

        self.squash *= 0.8

        self.vy += FAST_FALL_GRAVITY if (self.fast_falling and self.vy > 0) else GRAVITY

        if self.ai:
            self.ai_logic(opponent)
        else:
            self.player_input(keys,opponent)

        self.rect.x+=int(self.vx)

        fall_speed = self.vy
        self.rect.y+=int(self.vy)

        was_grounded = self.on_ground
        self.platform_collision()

        if self.on_ground and not was_grounded:
            self.fast_falling = False
            if fall_speed > 10:
                self.squash = 0.35

        if self.on_ground:
            self.air_jumps_left = self.max_air_jumps
            self.fast_falling = False
            self.coyote_timer = 6
        else:
            self.coyote_timer = max(0, self.coyote_timer - 1)

        self.check_ledge_grab()

    # ------------------------------------------------------------
    # shared action helpers (used by both human input and AI)
    # ------------------------------------------------------------

    def try_jump(self, just_pressed):
        if not just_pressed:
            return
        if self.on_ground or self.coyote_timer > 0:
            self.vy = self.jump_power
            self.on_ground = False
            self.squash = -0.25
            play_sound("jump")
        elif self.air_jumps_left > 0:
            self.vy = self.air_jump_power
            self.air_jumps_left -= 1
            self.squash = -0.25
            play_sound("jump")
            for _ in range(8):
                particles.append(Particle(self.rect.centerx, self.rect.bottom, self.color))

    def try_spot_dodge(self):
        if self.on_ground and self.dodge_cd == 0:
            self.dodge_frames = SPOT_DODGE_FRAMES
            self.dodge_cd = SPOT_DODGE_COOLDOWN
            self.invincible = True
            self.shielding = False
            return True
        return False

    def check_ledge_grab(self):
        if self.on_ground or self.ledge_cd > 0 or self.vy <= 0:
            return

        near_left = (LEDGE_LEFT_X-45 < self.rect.centerx < LEDGE_LEFT_X+15) and abs(self.rect.bottom-LEDGE_Y) < 70
        near_right = (LEDGE_RIGHT_X-15 < self.rect.centerx < LEDGE_RIGHT_X+45) and abs(self.rect.bottom-LEDGE_Y) < 70

        if near_left or near_right:
            self.rect.centerx = (LEDGE_LEFT_X+30) if near_left else (LEDGE_RIGHT_X-30)
            self.rect.bottom = LEDGE_Y
            self.vx = 0
            self.vy = 0
            self.on_ground = True
            self.dodge_frames = LEDGE_SAVE_FRAMES
            self.invincible = True
            self.ledge_cd = LEDGE_COOLDOWN
            self.air_jumps_left = self.max_air_jumps
            for _ in range(10):
                particles.append(Particle(self.rect.centerx, self.rect.bottom, WHITE))

    def update_shield(self, held):
        if self.shield_broken_timer > 0:
            self.shielding = False
            return
        if held and self.on_ground and self.dodge_frames == 0:
            self.shielding = True
            self.vx *= 0.4
            self.shield_hp -= SHIELD_DRAIN
            if self.shield_hp <= 0:
                self.shield_hp = 0
                self.shield_broken_timer = 100
                self.hitstun = 80
                self.shielding = False
                play_sound("shield_break")
        else:
            self.shielding = False

    def attack(self,opponent):

        if self.shielding or self.dodge_frames>0 or self.attack_cd > 0:
            return

        hitbox=pygame.Rect(
            self.rect.centerx+self.facing*35,
            self.rect.y+10,
            45,
            30
        )

        if hitbox.colliderect(opponent.rect):
            self.attack_cd = 12
            move = dict(JAB_MOVE)
            move["damage"] = self.jab_damage
            opponent.take_hit(self, move)

    def try_grab(self, opponent):

        if self.grab_cd>0 or self.shielding or self.dodge_frames>0:
            return

        self.grab_cd = GRAB_COOLDOWN

        if self.facing > 0:
            hitbox = pygame.Rect(self.rect.centerx, self.rect.y, self.grab_range, self.rect.height)
        else:
            hitbox = pygame.Rect(self.rect.centerx-self.grab_range, self.rect.y, self.grab_range, self.rect.height)

        if hitbox.colliderect(opponent.rect):
            self.attack_cd = 12
            play_sound("grab")
            self.grabbing = True
            self.grab_timer = 60
            opponent.grabbed = True
            opponent.grab_timer = 60
            opponent.vx = 0
            opponent.vy = 0

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

        self.special_cd=self.special_cd_max

    def player_input(self,keys,opponent):

        shield_held = keys[self.controls["shield"]]
        down_held = keys[self.controls["down"]]
        jump_held = keys[self.controls["jump"]]

        jump_just_pressed = jump_held and not self.prev_jump_held
        shield_just_pressed = shield_held and not self.prev_shield_held

        if self.hitstun>0:
            self.prev_jump_held = jump_held
            self.prev_shield_held = shield_held
            return

        # spot dodge: tap shield
        if shield_just_pressed:
            self.try_spot_dodge()

        self.update_shield(shield_held)

        if self.shielding or self.dodge_frames>0:
            self.vx*=0.85
        else:
            if keys[self.controls["left"]]:
                self.vx=-self.move_speed
                self.facing=-1

            elif keys[self.controls["right"]]:
                self.vx=self.move_speed
                self.facing=1

            else:
                self.vx*=0.85

            self.try_jump(jump_just_pressed)

            if not self.on_ground and self.vy>0 and down_held:
                self.fast_falling = True

            if keys[self.controls["attack"]]:
                self.attack(opponent)

            if keys[self.controls["special"]]:
                self.special()

            if keys[self.controls["grab"]]:
                self.try_grab(opponent)

        self.prev_jump_held = jump_held
        self.prev_shield_held = shield_held

    def ai_logic(self,opponent):

        if self.hitstun>0:
            return

        if self.difficulty == "EASY":
            speed = 3 * self.character["speed_mult"]
            attack_chance = 0.50
            special_chance = 0.10
            shield_chance = 0.0
            dodge_chance = 0.0
            grab_chance = 0.10

        elif self.difficulty == "MEDIUM":
            speed = 6 * self.character["speed_mult"]
            attack_chance = 0.70
            special_chance = 0.30
            shield_chance = 0.25
            dodge_chance = 0.15
            grab_chance = 0.30

        else:  # HARD
            speed = 9 * self.character["speed_mult"]
            attack_chance = 0.85
            special_chance = 0.45
            shield_chance = 0.5
            dodge_chance = 0.35
            grab_chance = 0.55

        incoming = any(
            p.owner is not self and
            abs(p.rect.centerx - self.rect.centerx) < 140 and
            abs(p.rect.centery - self.rect.centery) < 80
            for p in projectiles
        )

        if incoming and self.on_ground:
            if random.random() < dodge_chance and self.dodge_cd == 0:
                self.try_spot_dodge()
                return
            elif random.random() < shield_chance:
                self.update_shield(True)
                return

        self.update_shield(False)

        dx=opponent.rect.centerx-self.rect.centerx
        dy=opponent.rect.centery-self.rect.centery

        if abs(dx)>80:
            self.vx=speed if dx>0 else -speed
            self.facing=1 if dx>0 else -1
        else:
            self.vx*=0.8

            if opponent.shielding and random.random() < grab_chance:
                self.try_grab(opponent)
            elif random.random() < attack_chance:
                if random.random() < grab_chance*0.4:
                    self.try_grab(opponent)
                else:
                    self.attack(opponent)

        if dy < -20 and (self.on_ground or self.air_jumps_left>0):
            self.try_jump(True)
        elif self.rect.x < -150 or self.rect.x > WIDTH+150 or self.rect.y > HEIGHT:
            if self.air_jumps_left>0 and self.vy>0:
                self.try_jump(True)

        if self.special_cd == 0 and random.random() < special_chance:
            self.special()

    def take_hit(self,attacker,move=None,is_grab=False):

        if self.invincible:
            return

        if move is None:
            move = JAB_MOVE

        if self.shielding and self.shield_hp > 0 and not is_grab:
            self.shield_hp -= move["damage"] * 2.5
            if self.shield_hp <= 0:
                self.shield_hp = 0
                self.shield_broken_timer = 100
                self.shielding = False
                self.hitstun = 80
                play_sound("shield_break")
            for _ in range(6):
                particles.append(Particle(self.rect.centerx, self.rect.y, YELLOW))
            return

        prev_hitstun = self.hitstun

        self.damage += move["damage"]

        kb = calc_knockback(self.damage, move["damage"], move["kb_base"], move["kb_growth"], self.weight)

        rage_factor = 1 + min(0.5, (attacker.damage / 300) * attacker.rage_mult)
        kb *= rage_factor

        direction=1
        if attacker.rect.centerx>self.rect.centerx:
            direction=-1

        angle_rad = math.radians(move["angle"])
        self.vx = direction * kb * math.cos(angle_rad)
        self.vy = -kb * math.sin(angle_rad)

        self.hitstun = int(kb * 0.4) + 4

        # combo tracking on the attacker
        if attacker.combo_target is self and prev_hitstun > 0:
            attacker.combo_count += 1
        else:
            attacker.combo_count = 1
        attacker.combo_target = self
        attacker.max_combo = max(attacker.max_combo, attacker.combo_count)
        attacker.damage_dealt += move["damage"]
        attacker.biggest_hit = max(attacker.biggest_hit, move["damage"])

        if attacker.combo_count >= 2:
            combo_popups.append({
                "text": f"{attacker.combo_count} HIT COMBO!",
                "x": self.rect.centerx,
                "y": self.rect.y - 30,
                "timer": 40,
                "color": attacker.color
            })

        play_sound("hit")

        global hit_pause_timer, shake_timer
        hit_pause_timer = max(hit_pause_timer, 7 if is_grab else 5)
        shake_timer = max(shake_timer, 8)

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
            play_sound("ko")

            global shake_timer
            shake_timer = max(shake_timer, 14)

            if self.ai:
                self.rect.center = (750, 200)
            else:
                self.rect.center = (250, 200)

            self.vx = 0
            self.vy = 0
            self.air_jumps_left = self.max_air_jumps
            self.shield_hp = self.shield_max
            self.shielding = False
            self.fast_falling = False
            self.combo_target = None
            self.combo_count = 0

    def draw(self):

        w = self.rect.width * (1 + self.squash)
        h = self.rect.height * (1 - self.squash)

        draw_rect = pygame.Rect(0, 0, max(10, w), max(10, h))
        draw_rect.midbottom = self.rect.midbottom

        outline = draw_rect.inflate(4, 4)

        pygame.draw.rect(
            screen,
            BLACK,
            outline,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            self.color,
            draw_rect,
            border_radius=8
        )

        eye_x = draw_rect.centerx + (8 * self.facing)

        pygame.draw.circle(
            screen,
            WHITE,
            (eye_x, draw_rect.y + 18),
            4
        )

        # shield bubble (only shown while actively shielding)
        if self.shielding and self.shield_hp > 0:
            shield_surf = pygame.Surface((90,90), pygame.SRCALPHA)
            alpha = int(120 * (self.shield_hp/self.shield_max) + 40)
            pygame.draw.circle(shield_surf, (120,200,255,alpha), (45,45), 45)
            screen.blit(shield_surf, (self.rect.centerx-45, self.rect.centery-45))

        # brief invincibility flash during a dodge / ledge-save
        if self.invincible:
            flash = pygame.Surface((self.rect.width+8,self.rect.height+8), pygame.SRCALPHA)
            pygame.draw.rect(flash, (255,255,255,90), flash.get_rect(), border_radius=10)
            screen.blit(flash, (self.rect.x-4, self.rect.y-4))

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

def update_moving_platform():
    global moving_platform_dir

    info = STAGES[stage_index]
    idx = info.get("moving_index")

    if idx is None or idx >= len(platforms):
        return

    plat = platforms[idx]
    lo, hi = info["move_range"]

    plat.x += int(info["move_speed"] * moving_platform_dir)

    if plat.x <= lo or plat.x >= hi:
        moving_platform_dir *= -1

def update_particles():

    for particle in particles[:]:

        particle.update()

        if particle.life <= 0:
            particles.remove(particle)

def draw_particles():

    for particle in particles:
        particle.draw()

def update_projectiles(player, opponent):

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
            player.take_hit(projectile.owner, SPECIAL_MOVE)

            if projectile in projectiles:
                projectiles.remove(projectile)
                continue

        elif (
            projectile.owner != opponent
            and projectile.rect.colliderect(opponent.rect)
        ):
            opponent.take_hit(projectile.owner, SPECIAL_MOVE)

            if projectile in projectiles:
                projectiles.remove(projectile)
                continue

def draw_projectiles():

    for projectile in projectiles:
        projectile.draw()

def update_combo_popups():

    for c in combo_popups[:]:
        c["y"] -= 1
        c["timer"] -= 1
        if c["timer"] <= 0:
            combo_popups.remove(c)

def draw_combo_popups():

    for c in combo_popups:
        alpha = max(0, min(255, int(255 * (c["timer"] / 40))))
        surf = hud_font.render(c["text"], True, c["color"])
        surf.set_alpha(alpha)
        screen.blit(surf, (c["x"] - surf.get_width()//2, c["y"]))

# =========================
# HUD
# =========================
def damage_color(pct):
    if pct < 40:
        return WHITE
    elif pct < 80:
        return YELLOW
    elif pct < 120:
        return ORANGE
    else:
        return RED

def draw_hud(player, opponent):

    player_text = hud_font.render(
        f"{label1} {int(player.damage)}%",
        True,
        damage_color(player.damage)
    )

    screen.blit(player_text, (20,20))

    for i in range(player.stocks):
        pygame.draw.circle(screen, player.color, (32+i*22, 58), 8)
        pygame.draw.circle(screen, BLACK, (32+i*22, 58), 8, 2)

    opp_text = hud_font.render(
        f"{label2} {int(opponent.damage)}%",
        True,
        damage_color(opponent.damage)
    )

    screen.blit(opp_text, (820,20))

    for i in range(opponent.stocks):
        pygame.draw.circle(screen, opponent.color, (978-i*22, 58), 8)
        pygame.draw.circle(screen, BLACK, (978-i*22, 58), 8, 2)

    # special bar
    pygame.draw.rect(
        screen,
        BLACK,
        (20,90,200,18)
    )

    progress = max(
        0,
        200 * (1 - player.special_cd / player.special_cd_max)
    )

    pygame.draw.rect(
        screen,
        YELLOW,
        (20,90,progress,18)
    )

# =========================
# MODE SELECT
# =========================
def draw_mode_select():

    screen.fill((20,20,40))

    title = title_font.render("PYTHON SMASH", True, WHITE)
    screen.blit(title, (250,120))

    options = ["VS AI", "VS PLAYER 2"]
    selected_i = 0 if mode == "AI" else 1

    for i, opt in enumerate(options):
        selected = (i == selected_i)
        color = YELLOW if selected else WHITE
        prefix = "> " if selected else "  "
        text = menu_font.render(prefix + opt, True, color)
        screen.blit(text, (400,300 + i*60))

    start = menu_font.render("ENTER TO CONTINUE", True, WHITE)
    screen.blit(start, (320,520))

# =========================
# MENU (difficulty)
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
        "ENTER TO CONTINUE",
        True,
        WHITE
    )

    screen.blit(start, (320,520))

# =========================
# CHARACTER SELECT
# =========================
def draw_char_select():

    screen.fill((20,20,40))

    label = f"P{selecting_player}: CHOOSE YOUR FIGHTER" if mode == "2P" else "CHOOSE YOUR FIGHTER"

    title = title_font.render(label, True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

    idx = char_index if selecting_player == 1 else char_index2

    for i, c in enumerate(CHARACTERS):

        selected = (i == idx)
        color = YELLOW if selected else WHITE
        prefix = "> " if selected else "  "

        text = menu_font.render(
            prefix + c["name"],
            True,
            color
        )

        screen.blit(text, (WIDTH//2 - 140, 140 + i * 42))

    chosen = CHARACTERS[idx]

    ability_text = hud_font.render(
        "ABILITY: " + chosen["ability"],
        True,
        GREEN
    )

    debuff_text = hud_font.render(
        "DEBUFF: " + chosen["debuff"],
        True,
        RED
    )

    screen.blit(ability_text, (WIDTH//2 - 230, 440))
    screen.blit(debuff_text, (WIDTH//2 - 230, 475))

    start = menu_font.render(
        "ENTER TO CONTINUE",
        True,
        WHITE
    )

    screen.blit(start, (WIDTH//2 - start.get_width()//2, 555))

# =========================
# STAGE SELECT
# =========================
def draw_stage_select():

    screen.fill((20,20,40))

    title = title_font.render("CHOOSE YOUR STAGE", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))

    for i, s in enumerate(STAGES):

        selected = (i == stage_index)
        color = YELLOW if selected else WHITE
        prefix = "> " if selected else "  "

        text = menu_font.render(
            prefix + s["name"],
            True,
            color
        )

        screen.blit(text, (WIDTH//2 - 140, 220 + i * 50))

    start = menu_font.render(
        "ENTER TO FIGHT",
        True,
        WHITE
    )

    screen.blit(start, (WIDTH//2 - start.get_width()//2, 520))

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
            100
        )
    )

    if p1 is not None and p2 is not None:

        stats = [
            f"{label1}  DAMAGE DEALT: {int(p1.damage_dealt)}%   BIGGEST HIT: {int(p1.biggest_hit)}%   BEST COMBO: {p1.max_combo}",
            f"{label2}  DAMAGE DEALT: {int(p2.damage_dealt)}%   BIGGEST HIT: {int(p2.biggest_hit)}%   BEST COMBO: {p2.max_combo}",
        ]

        for i, s in enumerate(stats):
            t = hud_font.render(s, True, WHITE)
            screen.blit(t, (WIDTH//2 - t.get_width()//2, 260 + i*36))

    restart = menu_font.render(
        "PRESS R FOR MENU",
        True,
        WHITE
    )

    screen.blit(
        restart,
        (
            WIDTH//2 - restart.get_width()//2,
            420
        )
    )

# =========================
# CONTROLS
# =========================
controls = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "jump": pygame.K_w,
    "down": pygame.K_s,
    "attack": pygame.K_j,
    "special": pygame.K_k,
    "shield": pygame.K_l,
    "grab": pygame.K_i,
}

controls_p2 = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "jump": pygame.K_UP,
    "down": pygame.K_DOWN,
    "attack": pygame.K_PERIOD,
    "special": pygame.K_SLASH,
    "shield": pygame.K_RSHIFT,
    "grab": pygame.K_RCTRL,
}

def start_match():

    global p1, p2, platforms, moving_platform_dir
    global LEDGE_LEFT_X, LEDGE_RIGHT_X, LEDGE_Y
    global label1, label2

    particles.clear()
    projectiles.clear()
    combo_popups.clear()

    stage = STAGES[stage_index]
    platforms = stage["build"]()
    moving_platform_dir = 1

    LEDGE_LEFT_X = platforms[0].left
    LEDGE_RIGHT_X = platforms[0].right
    LEDGE_Y = platforms[0].top

    p1_character = CHARACTERS[char_index]

    p1 = Player(
        250,
        200,
        BLUE,
        controls,
        False,
        character=p1_character
    )

    if mode == "2P":

        p2_character = CHARACTERS[char_index2]

        p2 = Player(
            750,
            200,
            RED,
            controls_p2,
            False,
            character=p2_character
        )

        label1, label2 = "P1", "P2"

    else:

        difficulty = DIFFICULTIES[difficulty_index]
        p2_character = random.choice(CHARACTERS)

        p2 = Player(
            750,
            200,
            RED,
            None,
            True,
            difficulty,
            character=p2_character
        )

        label1, label2 = "PLAYER", "AI"

# =========================
# MAIN LOOP
# =========================
running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if game_state == MODE_SELECT:

            if event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    mode = "2P" if mode == "AI" else "AI"
                    play_sound("select")

                elif event.key == pygame.K_RETURN:
                    play_sound("confirm")
                    selecting_player = 1
                    game_state = MENU if mode == "AI" else CHAR_SELECT

        elif game_state == MENU:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    difficulty_index = max(0, difficulty_index - 1)
                    play_sound("select")

                elif event.key == pygame.K_DOWN:
                    difficulty_index = min(len(DIFFICULTIES)-1, difficulty_index + 1)
                    play_sound("select")

                elif event.key == pygame.K_BACKSPACE:
                    game_state = MODE_SELECT

                elif event.key == pygame.K_RETURN:
                    play_sound("confirm")
                    game_state = CHAR_SELECT

        elif game_state == CHAR_SELECT:

            if event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_UP, pygame.K_LEFT):
                    if selecting_player == 1:
                        char_index = max(0, char_index - 1)
                    else:
                        char_index2 = max(0, char_index2 - 1)
                    play_sound("select")

                elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                    if selecting_player == 1:
                        char_index = min(len(CHARACTERS)-1, char_index + 1)
                    else:
                        char_index2 = min(len(CHARACTERS)-1, char_index2 + 1)
                    play_sound("select")

                elif event.key == pygame.K_BACKSPACE:
                    if selecting_player == 2:
                        selecting_player = 1
                    else:
                        game_state = MENU if mode == "AI" else MODE_SELECT

                elif event.key == pygame.K_RETURN:
                    play_sound("confirm")
                    if mode == "2P" and selecting_player == 1:
                        selecting_player = 2
                    else:
                        game_state = STAGE_SELECT

        elif game_state == STAGE_SELECT:

            if event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_UP, pygame.K_LEFT):
                    stage_index = max(0, stage_index - 1)
                    play_sound("select")

                elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                    stage_index = min(len(STAGES)-1, stage_index + 1)
                    play_sound("select")

                elif event.key == pygame.K_BACKSPACE:
                    selecting_player = 2 if mode == "2P" else 1
                    game_state = CHAR_SELECT

                elif event.key == pygame.K_RETURN:
                    play_sound("confirm")
                    start_match()
                    game_state = PLAYING

        elif game_state == GAME_OVER:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    game_state = MODE_SELECT

    # MODE SELECT
    if game_state == MODE_SELECT:
        draw_mode_select()
        pygame.display.flip()
        continue

    # DIFFICULTY MENU
    if game_state == MENU:
        draw_menu()
        pygame.display.flip()
        continue

    # CHARACTER SELECT
    if game_state == CHAR_SELECT:
        draw_char_select()
        pygame.display.flip()
        continue

    # STAGE SELECT
    if game_state == STAGE_SELECT:
        draw_stage_select()
        pygame.display.flip()
        continue

    # GAME OVER
    if game_state == GAME_OVER:
        draw_game_over()
        pygame.display.flip()
        continue

    # PLAYING
    if hit_pause_timer > 0:
        hit_pause_timer -= 1
    else:
        keys = pygame.key.get_pressed()

        update_moving_platform()

        p1.update(keys, p2)
        p2.update(keys if mode == "2P" else None, p1)

        p1.check_ko()
        p2.check_ko()

        update_projectiles(p1, p2)
        update_particles()
        update_combo_popups()

        if p1.stocks <= 0:
            winner_text = f"{label2} WINS!"
            game_state = GAME_OVER

        elif p2.stocks <= 0:
            winner_text = f"{label1} WINS!"
            game_state = GAME_OVER

    real_screen = screen
    screen = render_surface

    draw_background()
    draw_stage()

    draw_projectiles()
    draw_particles()

    p1.draw()
    p2.draw()

    draw_hud(p1, p2)

    if p1.grabbing:
        text = title_font.render("GRABBING!", True, YELLOW)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 100))

    if p2.grabbing:
        text = title_font.render("GRABBING!", True, RED)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 100))

    draw_combo_popups()

    screen = real_screen

    if shake_timer > 0:
        shake_timer -= 1
        offset = (random.randint(-6,6), random.randint(-6,6))
    else:
        offset = (0,0)

    screen.fill(BLACK)
    screen.blit(render_surface, offset)

    pygame.display.flip()

pygame.quit()
