import math
import random
from pygame import Rect
import sounds
import music 

screen = None # Apenas para o editor parar de reclamar
WIDTH = 900
HEIGHT = 600
TITLE = "Aventura na Floresta (PgZero)"

HERO_SPEED = 220.0
ENEMY_SPEED = 140.0

COIN_COUNT = 6
COIN_PICK_RADIUS = 28

BG_COLOR_MENU = (18, 18, 28)
BG_COLOR_GAME = (20, 35, 30)
TEXT_COLOR = (235, 235, 240)

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_WIN = "win"
STATE_LOSE = "lose"
STATE_ERROR = "error"

audio_enabled = True
game_state = STATE_MENU
error_message = ""

btn_start = Rect(0, 0, 320, 56)
btn_audio = Rect(0, 0, 320, 56)
btn_exit = Rect(0, 0, 320, 56)


def center_menu_buttons():
    cx = WIDTH // 2 - btn_start.w // 2
    cy = HEIGHT // 2 - 70
    btn_start.x, btn_start.y = cx, cy
    btn_audio.x, btn_audio.y = cx, cy + 80
    btn_exit.x, btn_exit.y = cx, cy + 160


center_menu_buttons()


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def play_sfx(name):
    # Segurança: se o áudio der ruim, não deixa o jogo morrer.
    if not audio_enabled:
        return
    try:
        getattr(sounds, name).play()
    except Exception as err:
        print(f"SFX error ({name}):", err)


def set_music(on):
    global audio_enabled
    audio_enabled = on
    # Segurança: se música der ruim, não fecha o jogo.
    try:
        if audio_enabled:
            music.play("bgm")
            music.set_volume(0.6)
        else:
            music.stop()
    except Exception as err:
        print("Music error:", err)
        audio_enabled = False


class AnimatedEntity:
    def __init__(self, x, y, idle_frames, move_frames, frame_delay=0.11):
        self.actor = Actor(idle_frames[0], (x, y))
        self.idle_frames = idle_frames
        self.move_frames = move_frames
        self.frame_delay = frame_delay

        self._anim_time = 0.0
        self._frame_index = 0
        self._moving = False

    def _set_frame(self, frames):
        self.actor.image = frames[self._frame_index % len(frames)]

    def update_animation(self, dt, moving):
        frames = self.move_frames if moving else self.idle_frames

        if moving != self._moving:
            self._moving = moving
            self._frame_index = 0
            self._anim_time = 0.0
            self._set_frame(frames)
            return

        self._anim_time += dt
        if self._anim_time >= self.frame_delay:
            self._anim_time -= self.frame_delay
            self._frame_index = (self._frame_index + 1) % len(frames)
            self._set_frame(frames)


class Hero(AnimatedEntity):
    def __init__(self, x, y):
        idle = [f"hero_idle_{i}" for i in range(4)]
        move = [f"hero_move_{i}" for i in range(6)]
        super().__init__(x, y, idle, move, frame_delay=0.10)
        self.target = (x, y)

    def set_target(self, pos):
        self.target = pos

    def update(self, dt):
        dx = self.target[0] - self.actor.x
        dy = self.target[1] - self.actor.y
        dist = math.hypot(dx, dy)

        moving = dist > 2.0
        if moving:
            step = HERO_SPEED * dt
            if step >= dist:
                self.actor.pos = self.target
            else:
                nx = dx / dist
                ny = dy / dist
                self.actor.x += nx * step
                self.actor.y += ny * step

        self.actor.x = clamp(self.actor.x, 20, WIDTH - 20)
        self.actor.y = clamp(self.actor.y, 20, HEIGHT - 20)

        self.update_animation(dt, moving)


class Enemy(AnimatedEntity):
    def __init__(self, territory_rect):
        idle = [f"slime_idle_{i}" for i in range(4)]
        move = [f"slime_move_{i}" for i in range(4)]

        x = random.randint(territory_rect.left + 30, territory_rect.right - 30)
        y = random.randint(territory_rect.top + 30, territory_rect.bottom - 30)
        super().__init__(x, y, idle, move, frame_delay=0.12)

        self.territory = territory_rect
        self.target = self._random_point()

    def _random_point(self):
        return (
            random.randint(self.territory.left + 25, self.territory.right - 25),
            random.randint(self.territory.top + 25, self.territory.bottom - 25),
        )

    def update(self, dt):
        dx = self.target[0] - self.actor.x
        dy = self.target[1] - self.actor.y
        dist = math.hypot(dx, dy)

        if dist < 6.0:
            self.target = self._random_point()
            dist = 0.0

        moving = dist > 0.0
        if moving:
            step = ENEMY_SPEED * dt
            if step >= dist:
                self.actor.pos = self.target
            else:
                nx = dx / dist
                ny = dy / dist
                self.actor.x += nx * step
                self.actor.y += ny * step

        self.update_animation(dt, moving)


# IMPORTANTE: nada de Actor aqui em cima (safe boot)
hero = None
enemies = []
coins = []
portal = None
portal_active = False
collected = 0


def fail_to_error_screen(msg):
    global game_state, error_message
    game_state = STATE_ERROR
    error_message = msg
    print("BOOT ERROR:", msg)


def reset_game():
    global hero, enemies, coins, portal, portal_active, collected, game_state

    try:
        hero = Hero(90, 90)
        portal = Actor("portal", (WIDTH - 70, HEIGHT - 70))

        enemies = [
            Enemy(Rect(80, 260, 260, 260)),
            Enemy(Rect(360, 60, 260, 220)),
            Enemy(Rect(360, 320, 260, 240)),
            Enemy(Rect(660, 120, 200, 360)),
        ]

        coins = []
        for _ in range(COIN_COUNT):
            x = random.randint(120, WIDTH - 120)
            y = random.randint(120, HEIGHT - 120)
            coins.append(Actor("coin", (x, y)))

        portal_active = False
        collected = 0
        game_state = STATE_PLAYING

        # Música só quando começa o jogo
        if audio_enabled:
            set_music(True)

    except Exception as err:
        fail_to_error_screen(str(err))


def draw_button(rect, label):
    screen.draw.filled_rect(rect, (55, 60, 90))
    screen.draw.rect(rect, (180, 190, 220))
    screen.draw.text(label, center=rect.center, fontsize=34, color=TEXT_COLOR)


def draw():
    if game_state == STATE_MENU:
        screen.fill(BG_COLOR_MENU)

        screen.draw.text("AVENTURA NA FLORESTA",
                         center=(WIDTH // 2, 120),
                         fontsize=56,
                         color=TEXT_COLOR)

        screen.draw.text("Clique para andar. Pegue moedas. Fuja dos slimes.",
                         center=(WIDTH // 2, 170),
                         fontsize=28,
                         color=(210, 210, 220))

        draw_button(btn_start, "Começar o jogo")
        label = "Áudio: LIGADO" if audio_enabled else "Áudio: DESLIGADO"
        draw_button(btn_audio, label)
        draw_button(btn_exit, "Sair")

    elif game_state == STATE_ERROR:
        screen.fill((40, 10, 10))
        screen.draw.text("ERRO AO INICIAR",
                         center=(WIDTH // 2, 120),
                         fontsize=60,
                         color=(255, 220, 220))
        screen.draw.text("Provável problema de asset (imagem/som) ou áudio.",
                         center=(WIDTH // 2, 190),
                         fontsize=28,
                         color=(255, 230, 230))
        screen.draw.text(f"Detalhe: {error_message}",
                         center=(WIDTH // 2, 260),
                         fontsize=22,
                         color=(255, 240, 240))
        screen.draw.text("Clique para voltar ao menu.",
                         center=(WIDTH // 2, 340),
                         fontsize=28,
                         color=(255, 230, 230))

    else:
        screen.fill(BG_COLOR_GAME)

        for c in coins:
            c.draw()

        if portal_active and portal is not None:
            portal.draw()

        for e in enemies:
            e.actor.draw()

        hero.actor.draw()

        screen.draw.text(f"Moedas: {collected}/{COIN_COUNT}",
                         topleft=(16, 12),
                         fontsize=32,
                         color=TEXT_COLOR)

        if game_state == STATE_WIN:
            screen.draw.text("VOCÊ VENCEU! (clique para menu)",
                             center=(WIDTH // 2, HEIGHT // 2),
                             fontsize=52,
                             color=(235, 255, 235))
        elif game_state == STATE_LOSE:
            screen.draw.text("VOCÊ PERDEU! (clique para menu)",
                             center=(WIDTH // 2, HEIGHT // 2),
                             fontsize=52,
                             color=(255, 230, 230))


def update(dt):
    global collected, portal_active, game_state

    if game_state != STATE_PLAYING:
        return

    hero.update(dt)

    for e in enemies:
        e.update(dt)
        if hero.actor.colliderect(e.actor):
            play_sfx("hit")
            game_state = STATE_LOSE
            return

    remaining = []
    for c in coins:
        if math.hypot(hero.actor.x - c.x, hero.actor.y - c.y) <= COIN_PICK_RADIUS:
            collected += 1
            play_sfx("pickup")
        else:
            remaining.append(c)
    coins[:] = remaining

    if collected >= COIN_COUNT:
        portal_active = True

    if portal_active and portal is not None and hero.actor.colliderect(portal):
        game_state = STATE_WIN


def on_mouse_down(pos, button):
    global game_state

    if game_state == STATE_MENU:
        if btn_start.collidepoint(pos):
            play_sfx("click")
            reset_game()
        elif btn_audio.collidepoint(pos):
            play_sfx("click")
            if audio_enabled:
                set_music(False)
            else:
                set_music(True)
        elif btn_exit.collidepoint(pos):
            raise SystemExit
        return

    if game_state in (STATE_WIN, STATE_LOSE, STATE_ERROR):
        play_sfx("click")
        game_state = STATE_MENU
        return

    if game_state == STATE_PLAYING:
        hero.set_target(pos)
