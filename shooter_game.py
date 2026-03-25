from random import randint
from pygame import *
import pygame
from time import time as timer
import math

# Инициализация
mixer.init()
font.init()
pygame.init()

# Настройки окна (начальные)
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
window = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display.set_caption('Shooter')

# Загрузка фона
galaxy = transform.scale(image.load('galaxy.jpg'), (WINDOW_WIDTH, WINDOW_HEIGHT))

# Игровые переменные
game = True
game_state = "MENU"  # MENU, GAME, UPGRADE, LEVEL_MENU
level_menu_active = False
next_level_num = 1
lost = 0
score = 0   
current_level_score = 0
player_speed = 5
num_fire = 0
rel_time = False
reload_start = 0
reload_time = 0.7
lives = 3
max_lives = 3
last_shot_time = 0
shot_delay = 0.3
upgrade_points = 0

# Настройки уровней
current_level = 1
MAX_MONSTERS = 2
MAX_ASTEROIDS = 0
target_score = 10
boss_active = False
boss_hp = 0
boss_max_hp = 0
boss_shoot_timer = 0
boss_shoot_delay = 1.5
boss_bullet_speed = 5

# Группы спрайтов
monsters = sprite.Group()
asteroids = sprite.Group()
bullets = sprite.Group()
enemy_bullets = sprite.Group()
boss_group = sprite.Group()

# Шрифты
font_main = font.SysFont('Arial Black', 24)
font_big = font.SysFont('Arial Black', 36)
font_title = font.SysFont('Arial Black', 48)
font_menu = font.SysFont('Arial Black', 32)
font_small = font.SysFont('Arial Black', 18)
font_tiny = font.SysFont('Arial Black', 16)

# Кадры в секунду
clock = pygame.time.Clock()
FPS = 60

# Звуки
try:
    mixer.music.load('space.ogg')
    mixer.music.play(-1)
    fire_sound = mixer.Sound('fire.ogg')
except:
    print("Звуковые файлы не найдены")

# ==========================================
# ФУНКЦИЯ ОБНОВЛЕНИЯ РАЗМЕРОВ ЭКРАНА
# ==========================================

def update_window_size():
    global window, galaxy, player, game_state
    window = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    galaxy = transform.scale(image.load('galaxy.jpg'), (WINDOW_WIDTH, WINDOW_HEIGHT))
    display.set_caption('Shooter')
    
    # Обновляем позицию игрока после изменения размера окна
    if player:
        player.rect.y = WINDOW_HEIGHT - 100

def upgrade_screen():
    global WINDOW_HEIGHT, upgrade_points, player, game_state
    
    if upgrade_points >= 30 and WINDOW_HEIGHT < 800:
        WINDOW_HEIGHT += 50
        update_window_size()  # Здесь уже обновляется позиция игрока
        upgrade_points -= 30
        
        # Если игрок существует (даже в меню), обновляем его позицию
        if player:
            player.rect.y = WINDOW_HEIGHT - 100
        
        return True
    return False

def add_points():
    global upgrade_points
    upgrade_points += 1000

# ==========================================
# ФУНКЦИЯ РЕСТАРТА
# ==========================================

def reset_game():
    global lost, score, finish, monsters, asteroids, bullets, player, num_fire, rel_time, lives, game_state, current_level, upgrade_points, current_level_score, boss_active, boss_group, enemy_bullets, player_speed, shot_delay, reload_time, max_lives
    
    lost = 0
    score = 0
    current_level_score = 0
    finish = False
    num_fire = 0
    rel_time = False
    lives = max_lives
    current_level = 1
    game_state = "GAME"
    boss_active = False
    boss_group.empty()
    enemy_bullets.empty()
    
    # Обновляем параметры уровня (но не сбрасываем прокачку!)
    update_level_preserve_upgrades()
    
    monsters.empty()
    asteroids.empty()
    bullets.empty()
    
    player = Player('rocket.png', 100, WINDOW_HEIGHT - 100, 80, 90, player_speed)
    
    if not boss_active:
        for i in range(MAX_MONSTERS):
            enemy_speed = randint(1, 2 + current_level // 3)
            monster = Enemy('ufo.png', randint(80, WINDOW_WIDTH - 80), randint(-200, -50), 80, 60, enemy_speed)
            monsters.add(monster)
        
        for i in range(MAX_ASTEROIDS):
            asteroid_speed = randint(1, 1 + current_level // 4)
            asteroid = Asteroid('asteroid.png', randint(80, WINDOW_WIDTH - 80), randint(-300, -100), 60, 60, asteroid_speed)
            asteroids.add(asteroid)
    else:
        boss = Boss('boss.png', WINDOW_WIDTH // 2 - 125, -100, 250, 150, 1)
        boss_group.add(boss)

def update_level_preserve_upgrades():
    global MAX_MONSTERS, MAX_ASTEROIDS, target_score, boss_active, boss_max_hp, boss_shoot_delay, boss_bullet_speed, current_level
    
    boss_active = False
    
    if current_level == 1:
        MAX_MONSTERS = 2
        MAX_ASTEROIDS = 0
        target_score = 10
    
    elif current_level == 2:
        MAX_MONSTERS = 3
        MAX_ASTEROIDS = 0
        target_score = 15
    
    elif current_level == 3:
        MAX_MONSTERS = 4
        MAX_ASTEROIDS = 0
        target_score = 18
    
    elif current_level == 4:
        MAX_MONSTERS = 5
        MAX_ASTEROIDS = 1
        target_score = 22
    
    elif current_level == 5:
        boss_active = True
        boss_max_hp = 40  # Увеличено с 30
        boss_shoot_delay = 1.3  # Уменьшено с 1.5
        boss_bullet_speed = 7  # Увеличено с 5
        target_score = 1
    
    elif current_level == 6:
        MAX_MONSTERS = 5
        MAX_ASTEROIDS = 1
        target_score = 22
    
    elif current_level == 7:
        MAX_MONSTERS = 6
        MAX_ASTEROIDS = 1
        target_score = 25
    
    elif current_level == 8:
        MAX_MONSTERS = 7
        MAX_ASTEROIDS = 2
        target_score = 28
    
    elif current_level == 9:
        MAX_MONSTERS = 8
        MAX_ASTEROIDS = 2
        target_score = 32
    
    elif current_level == 10:
        boss_active = True
        boss_max_hp = 50  # Увеличено с 45
        boss_shoot_delay = 1  # Уменьшено с 1.3
        boss_bullet_speed = 10  # Увеличено с 6
        target_score = 1
    
    elif current_level == 11:
        MAX_MONSTERS = 8
        MAX_ASTEROIDS = 2
        target_score = 32
    
    elif current_level == 12:
        MAX_MONSTERS = 9
        MAX_ASTEROIDS = 3
        target_score = 35
    
    elif current_level == 13:
        MAX_MONSTERS = 10
        MAX_ASTEROIDS = 3
        target_score = 38
    
    elif current_level == 14:
        MAX_MONSTERS = 11
        MAX_ASTEROIDS = 4
        target_score = 42
    
    elif current_level == 15:
        boss_active = True
        boss_max_hp = 70  # Увеличено с 65
        boss_shoot_delay = 0.8  # Уменьшено с 1.1
        boss_bullet_speed = 13  # Увеличено с 7
        target_score = 1
    
    elif current_level == 16:
        MAX_MONSTERS = 11
        MAX_ASTEROIDS = 4
        target_score = 42
    
    elif current_level == 17:
        MAX_MONSTERS = 12
        MAX_ASTEROIDS = 4
        target_score = 45
    
    elif current_level == 18:
        MAX_MONSTERS = 13
        MAX_ASTEROIDS = 5
        target_score = 48
    
    elif current_level == 19:
        MAX_MONSTERS = 14
        MAX_ASTEROIDS = 5
        target_score = 52
    
    elif current_level == 20:
        boss_active = True
        boss_max_hp = 100  # Увеличено с 100
        boss_shoot_delay = 0.5  # Уменьшено с 0.8
        boss_bullet_speed = 15  # Увеличено с 8
        target_score = 1

def show_level_menu(level_num):
    global game_state, level_menu_active, next_level_num
    next_level_num = level_num
    game_state = "LEVEL_MENU"
    level_menu_active = True

def start_level():
    global game_state, level_menu_active, finish, score, current_level_score, lost, monsters, asteroids, bullets, boss_active, boss_group, enemy_bullets, boss_shoot_timer, player
    
    game_state = "GAME"
    level_menu_active = False
    finish = False
    score = 0
    current_level_score = 0
    lost = 0
    boss_shoot_timer = 0
    
    monsters.empty()
    asteroids.empty()
    bullets.empty()
    boss_group.empty()
    enemy_bullets.empty()
    
    if not boss_active:
        for i in range(MAX_MONSTERS):
            enemy_speed = randint(1, 2 + current_level // 3)
            monster = Enemy('ufo.png', randint(80, WINDOW_WIDTH - 80), randint(-200, -50), 80, 60, enemy_speed)
            monsters.add(monster)
        
        for i in range(MAX_ASTEROIDS):
            asteroid_speed = randint(1, 1 + current_level // 4)
            asteroid = Asteroid('asteroid.png', randint(80, WINDOW_WIDTH - 80), randint(-300, -100), 60, 60, asteroid_speed)
            asteroids.add(asteroid)
    else:
        boss = Boss('boss.png', WINDOW_WIDTH // 2 - 125, -100, 250, 150, 1)
        boss_group.add(boss)
    
    # Обновляем позицию игрока (на случай, если экран был расширен в меню)
    if player:
        player.rect.y = WINDOW_HEIGHT - 100

def next_level():
    global current_level, score, finish, game_state, upgrade_points, current_level_score, boss_active
    
    if lives > 0:
        upgrade_points += 15
    
    current_level += 1
    
    if current_level <= 20:
        update_level_preserve_upgrades()  # Не сбрасываем прокачку!
        show_level_menu(current_level)
        finish = True
    else:
        finish = True
        result_text = font_big.render('ИГРА ПРОЙДЕНА!', 1, (255, 215, 0))

# ==========================================
# ФУНКЦИИ ПРОКАЧКИ С ОГРАНИЧЕНИЯМИ
# ==========================================

def upgrade_speed():
    global player_speed, upgrade_points
    if upgrade_points >= 10 and player_speed < 15:
        player_speed += 1
        upgrade_points -= 10
        return True
    return False

def upgrade_fire_rate():
    global shot_delay, upgrade_points
    if upgrade_points >= 15 and shot_delay > 0.09:
        shot_delay -= 0.03
        upgrade_points -= 15
        return True
    return False

def upgrade_reload():
    global reload_time, upgrade_points
    if upgrade_points >= 15 and reload_time > 0.30:
        reload_time -= 0.05
        upgrade_points -= 15
        return True
    return False

def upgrade_health():
    global max_lives, lives, upgrade_points
    if upgrade_points >= 20 and max_lives < 10:
        max_lives += 1
        lives += 1
        upgrade_points -= 20
        return True
    return False

# ==========================================
# КЛАССЫ
# ==========================================

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
    
    def update(self):
        pass

class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)

    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < WINDOW_WIDTH - 85:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet('bullet.png', self.rect.centerx - 7, self.rect.top, 15, 20, 15)
        bullets.add(bullet)
        fire_sound.play()

class Enemy(GameSprite):
    def update(self):
        global lost
        self.rect.y += self.speed
        if self.rect.y >= WINDOW_HEIGHT:
            self.kill()
            lost += 1

class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= WINDOW_HEIGHT:
            self.kill()

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

class EnemyBullet(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, target_x, target_y):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        if distance != 0:
            self.vx = (dx / distance) * player_speed
            self.vy = (dy / distance) * player_speed
        else:
            self.vx = 0
            self.vy = player_speed
    
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.y > WINDOW_HEIGHT or self.rect.y < 0 or self.rect.x > WINDOW_WIDTH or self.rect.x < 0:
            self.kill()

class Boss(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.hp = boss_max_hp
        self.max_hp = boss_max_hp
        temp_image = image.load(player_image).convert()
        temp_image.set_colorkey((0, 255, 0))
        self.image = transform.scale(temp_image, (size_x, size_y))
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > 50:
            self.speed = 1
            self.rect.y = 50
    
    def shoot(self, target_x, target_y):
        bullet = EnemyBullet('bullet.png', self.rect.centerx - 7, self.rect.bottom, 15, 20, boss_bullet_speed, target_x, target_y)
        enemy_bullets.add(bullet)
    
    def draw_health(self):
        bar_width = 400
        bar_height = 30
        bar_x = WINDOW_WIDTH // 2 - bar_width // 2
        bar_y = 15
        
        # Фон полоски здоровья
        pygame.draw.rect(window, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Текущее здоровье
        current_width = int(bar_width * (self.hp / self.max_hp))
        pygame.draw.rect(window, (255, 0, 0), (bar_x, bar_y, current_width, bar_height))
        
        # Текст HP
        hp_text = font_big.render(f'BOSS HP: {self.hp}/{self.max_hp}', True, (255, 255, 255))
        text_rect = hp_text.get_rect(center=(WINDOW_WIDTH // 2, bar_y + bar_height + 10))
        window.blit(hp_text, text_rect)
    
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
        self.draw_health()

# ==========================================
# КЛАССЫ ДЛЯ МЕНЮ
# ==========================================

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font
        self.is_hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

# ==========================================
# ФУНКЦИИ ОТРИСОВКИ МЕНЮ
# ==========================================

def draw_menu():
    window.blit(galaxy, (0, 0))
    
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    window.blit(overlay, (0, 0))
    
    title_text = font_title.render('SPACE SHOOTER', True, (255, 255, 0))
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 80))
    window.blit(title_text, title_rect)
    
    play_button.draw(window)
    upgrade_button.draw(window)
    
    hint_text = font_small.render('Upgrade system - earn points by killing enemies!', True, (150, 150, 150))
    hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
    window.blit(hint_text, hint_rect)

def draw_level_menu():
    window.blit(galaxy, (0, 0))
    
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    window.blit(overlay, (0, 0))
    
    title_text = font_title.render(f'УРОВЕНЬ {next_level_num}', True, (255, 255, 0))
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 60))
    window.blit(title_text, title_rect)
    
    level_play_button.draw(window)
    level_upgrade_button.draw(window)
    
    y_offset = WINDOW_HEIGHT - 120
    if next_level_num % 5 == 0:
        info_text = font_big.render('BOSS FIGHT!', True, (255, 0, 0))
        info_rect = info_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
        window.blit(info_text, info_rect)
        
        hint_text = font_small.render('Осторожно! Босс очень опасен!', True, (255, 200, 0))
        hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset + 40))
        window.blit(hint_text, hint_rect)
    else:
        info_text = font_main.render(f'Врагов: {MAX_MONSTERS}  Астероидов: {MAX_ASTEROIDS}', True, (255, 255, 255))
        info_rect = info_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
        window.blit(info_text, info_rect)

def draw_upgrade_menu():
    window.blit(galaxy, (0, 0))
    
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    window.blit(overlay, (0, 0))
    
    title_text = font_big.render('ПРОКАЧКА', True, (255, 255, 0))
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 40))
    window.blit(title_text, title_rect)
    
    points_text = font_main.render(f'ОЧКИ ПРОКАЧКИ: {upgrade_points}', True, (0, 255, 0))
    points_rect = points_text.get_rect(center=(WINDOW_WIDTH // 2, 90))
    window.blit(points_text, points_rect)
    
    y_offset = 140
    stats = [
        f'Скорость игрока: {player_speed}/15',
        f'Скорострельность: {shot_delay:.2f}/0.09 сек',
        f'Перезарядка: {reload_time:.2f}/0.30 сек',
        f'Макс. здоровье: {max_lives}/10',
        f'Высота экрана: {WINDOW_HEIGHT}/800'
    ]
    
    for stat in stats:
        stat_text = font_small.render(stat, True, (255, 255, 255))
        stat_rect = stat_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
        window.blit(stat_text, stat_rect)
        y_offset += 30
    
    button_width = 150
    button_height = 40
    left_x = WINDOW_WIDTH // 2 - button_width - 20
    right_x = WINDOW_WIDTH // 2 + 20
    start_y = 300
    
    speed_button.rect.x = left_x
    speed_button.rect.y = start_y
    speed_button.draw(window)
    
    fire_rate_button.rect.x = right_x
    fire_rate_button.rect.y = start_y
    fire_rate_button.draw(window)
    
    reload_button.rect.x = left_x
    reload_button.rect.y = start_y + 50
    reload_button.draw(window)
    
    health_button.rect.x = right_x
    health_button.rect.y = start_y + 50
    health_button.draw(window)
    
    screen_button.rect.x = left_x
    screen_button.rect.y = start_y + 100
    screen_button.draw(window)
    
    back_button.draw(window)

# ==========================================
# СОЗДАНИЕ КНОПОК
# ==========================================

button_width = 200
button_height = 60
button_y = 200

# Главное меню
play_button = Button(
    WINDOW_WIDTH // 2 - button_width // 2,
    button_y,
    button_width,
    button_height,
    'PLAY',
    (0, 100, 0),
    (0, 150, 0),
    font_menu
)

upgrade_button = Button(
    WINDOW_WIDTH // 2 - button_width // 2,
    button_y + 80,
    button_width,
    button_height,
    'UPGRADES',
    (100, 50, 0),
    (150, 75, 0),
    font_menu
)

# Кнопки прокачки
speed_button = Button(
    0, 0, 150, 40,
    'СКОРОСТЬ (10)',
    (0, 80, 80),
    (0, 120, 120),
    font_tiny
)

fire_rate_button = Button(
    0, 0, 150, 40,
    'СКОРОСТРЕЛ. (15)',
    (80, 80, 0),
    (120, 120, 0),
    font_tiny
)

reload_button = Button(
    0, 0, 150, 40,
    'ПЕРЕЗАРЯДКА (15)',
    (80, 0, 80),
    (120, 0, 120),
    font_tiny
)

health_button = Button(
    0, 0, 150, 40,
    'ЗДОРОВЬЕ (20)',
    (0, 80, 0),
    (0, 120, 0),
    font_tiny
)

screen_button = Button(
    0, 0, 150, 40,
    'РАСШИРИТЬ (30)',
    (100, 100, 0),
    (150, 150, 0),
    font_tiny
)

back_button = Button(
    WINDOW_WIDTH // 2 - button_width // 2,
    WINDOW_HEIGHT - 70,
    button_width,
    button_height,
    'BACK',
    (100, 50, 50),
    (150, 75, 75),
    font_menu
)

# Кнопки меню уровня
level_play_button = Button(
    WINDOW_WIDTH // 2 - button_width // 2,
    180,
    button_width,
    button_height,
    'ИГРАТЬ',
    (0, 100, 0),
    (0, 150, 0),
    font_menu
)

level_upgrade_button = Button(
    WINDOW_WIDTH // 2 - button_width // 2,
    260,
    button_width,
    button_height,
    'ПРОКАЧКА',
    (100, 50, 0),
    (150, 75, 0),
    font_menu
)

# ==========================================
# ИНИЦИАЛИЗАЦИЯ ИГРЫ
# ==========================================

player = None
finish = False
result_text = None

# ==========================================
# ИГРОВОЙ ЦИКЛ
# ==========================================

while game:
    
    for e in event.get():
        if e.type == QUIT:
            game = False
        
        if e.type == KEYDOWN:
            if e.key == K_MINUS:  # Клавиша "-"
                add_points()
        
        if game_state == "MENU":
            if play_button.handle_event(e):
                reset_game()
            
            if upgrade_button.handle_event(e):
                game_state = "UPGRADE"
        
        elif game_state == "LEVEL_MENU":
            if level_play_button.handle_event(e):
                start_level()
            
            if level_upgrade_button.handle_event(e):
                game_state = "UPGRADE"
        
        elif game_state == "UPGRADE":
            if speed_button.handle_event(e):
                upgrade_speed()
            
            if fire_rate_button.handle_event(e):
                upgrade_fire_rate()
            
            if reload_button.handle_event(e):
                upgrade_reload()
            
            if health_button.handle_event(e):
                upgrade_health()
            
            if screen_button.handle_event(e):
                upgrade_screen()
                # Обновляем позиции кнопок после изменения размера окна
                back_button.rect.x = WINDOW_WIDTH // 2 - button_width // 2
                back_button.rect.y = WINDOW_HEIGHT - 70
                level_play_button.rect.x = WINDOW_WIDTH // 2 - button_width // 2
                level_upgrade_button.rect.x = WINDOW_WIDTH // 2 - button_width // 2
            
            if back_button.handle_event(e):
                if level_menu_active:
                    game_state = "LEVEL_MENU"
                else:
                    game_state = "MENU"
        
        elif game_state == "GAME":
            if e.type == KEYDOWN:
                if e.key == K_r:
                    reset_game()
    
    if game_state == "MENU":
        draw_menu()
        display.update()
    
    elif game_state == "LEVEL_MENU":
        draw_level_menu()
        display.update()
    
    elif game_state == "UPGRADE":
        draw_upgrade_menu()
        display.update()
    
    elif game_state == "GAME":
        if not finish:
            keys = key.get_pressed()
            
            if keys[K_SPACE]:
                now = timer()
                if now - last_shot_time > shot_delay:
                    if not rel_time:
                        player.fire()
                        num_fire += 1
                        last_shot_time = now
                        
                        if num_fire >= 5:
                            rel_time = True      
                            reload_start = timer()
                            num_fire = 0
            
            if rel_time:
                now = timer()
                if now - reload_start >= reload_time:
                    rel_time = False

            player.update()
            monsters.update()
            asteroids.update()
            bullets.update()
            enemy_bullets.update()
            boss_group.update()
            
            if boss_active and len(boss_group) > 0:
                now = timer()
                if now - boss_shoot_timer > boss_shoot_delay:
                    for boss_sprite in boss_group:
                        boss_sprite.shoot(player.rect.centerx, player.rect.centery)
                    boss_shoot_timer = now

            collisions = sprite.groupcollide(bullets, monsters, True, True)
            if collisions:
                destroyed_count = sum(len(monsters_list) for monsters_list in collisions.values())
                score += destroyed_count
                current_level_score += destroyed_count
                # Даём 3 очка за 2 убийства (1.5 за каждого)
                upgrade_points += (destroyed_count * 3) // 2
            
            if boss_active:
                boss_collisions = sprite.groupcollide(bullets, boss_group, True, False)
                if boss_collisions:
                    for boss_sprite in boss_group:
                        boss_sprite.hp -= len(boss_collisions)
                        if boss_sprite.hp <= 0:
                            boss_sprite.kill()
                            score += 1
                            current_level_score += 1
                            upgrade_points += 35  # Больше очков за босса
                            boss_active = False
            
            hit_player = sprite.spritecollide(player, enemy_bullets, True)
            if hit_player:
                lives -= len(hit_player)
                if lives <= 0:
                    upgrade_points -= current_level_score
                    if upgrade_points < 0:
                        upgrade_points = 0
                    finish = True
                    result_text = font_big.render('GAME OVER!', 1, (255, 0, 0))
            
            crash_monster = sprite.spritecollide(player, monsters, True)
            if crash_monster:
                lives -= len(crash_monster)
                if lives <= 0:
                    upgrade_points -= current_level_score
                    if upgrade_points < 0:
                        upgrade_points = 0
                    finish = True
                    result_text = font_big.render('GAME OVER!', 1, (255, 0, 0))
            
            crash_asteroid = sprite.spritecollide(player, asteroids, True)
            if crash_asteroid:
                lives -= len(crash_asteroid)
                if lives <= 0:
                    upgrade_points -= current_level_score
                    if upgrade_points < 0:
                        upgrade_points = 0
                    finish = True
                    result_text = font_big.render('GAME OVER!', 1, (255, 0, 0))
            
            if boss_active:
                crash_boss = sprite.spritecollide(player, boss_group, False)
                if crash_boss:
                    lives -= 1
                    if lives <= 0:
                        upgrade_points -= current_level_score
                        if upgrade_points < 0:
                            upgrade_points = 0
                        finish = True
                        result_text = font_big.render('GAME OVER!', 1, (255, 0, 0))
            
            if not boss_active and len(monsters) == 0 and not finish:
                if current_level < 20:
                    next_level()
                elif current_level == 20:
                    finish = True
                    result_text = font_big.render('ПОБЕДА!', 1, (0, 255, 0))
            
            if boss_active and len(boss_group) == 0 and not finish:
                if current_level < 20:
                    next_level()
                elif current_level == 20:
                    finish = True
                    result_text = font_big.render('ПОБЕДА!', 1, (0, 255, 0))
            
            if lost >= 5:
                upgrade_points -= current_level_score
                if upgrade_points < 0:
                    upgrade_points = 0
                finish = True
                result_text = font_big.render('GAME OVER!', 1, (255, 0, 0))
            
            window.blit(galaxy, (0, 0))
            
            player.reset()
            monsters.draw(window)
            asteroids.draw(window)
            bullets.draw(window)
            enemy_bullets.draw(window)
            boss_group.draw(window)
            
            text_lost = font_main.render('Пропущено НЛО: ' + str(lost) + ' / 5', 1, (255, 255, 255))
            window.blit(text_lost, (10, 10))
            
            text_score = font_main.render('Счёт: ' + str(score) + ' / ' + str(target_score), 1, (255, 255, 255))
            window.blit(text_score, (10, 40))
            
            level_text = font_main.render(str(current_level), 1, (255, 255, 0))
            level_rect = level_text.get_rect(center=(WINDOW_WIDTH // 2, 25))
            window.blit(level_text, level_rect)
            
            text_lives = font_main.render('Жизни: ' + str(lives), 1, (255, 255, 255))
            window.blit(text_lives, (10, 70))
            
            text_points = font_main.render('Очки прокачки: ' + str(upgrade_points), 1, (0, 255, 0))
            window.blit(text_points, (10, 100))
            
            if rel_time:
                reload_text = font_main.render('ПЕРЕЗАРЯДКА...', 1, (255, 100, 0))
                text_width = reload_text.get_width()
                window.blit(reload_text, ((WINDOW_WIDTH - text_width) // 2, WINDOW_HEIGHT - 50))
            
            display.update()
        
        else:
            window.blit(galaxy, (0, 0))
            
            if player:
                player.reset()
            monsters.draw(window)
            asteroids.draw(window)
            bullets.draw(window)
            
            window.blit(font_main.render('Пропущено НЛО: ' + str(lost) + ' / 5', 1, (255, 255, 255)), (10, 10))
            window.blit(font_main.render('Счёт: ' + str(score) + ' / ' + str(target_score), 1, (255, 255, 255)), (10, 40))
            window.blit(font_main.render('Жизни: ' + str(lives), 1, (255, 255, 255)), (10, 70))
            
            if result_text:
                result_width = result_text.get_width()
                result_height = result_text.get_height()
                window.blit(result_text, ((WINDOW_WIDTH - result_width) // 2, (WINDOW_HEIGHT - result_height) // 2 - 30))
            
            restart_text = font_main.render('Нажми R для рестарта', 1, (200, 200, 200))
            restart_width = restart_text.get_width()
            window.blit(restart_text, ((WINDOW_WIDTH - restart_width) // 2, WINDOW_HEIGHT - 100))
            
            menu_text = font_main.render('Нажми M для выхода в меню', 1, (200, 200, 200))
            menu_width = menu_text.get_width()
            window.blit(menu_text, ((WINDOW_WIDTH - menu_width) // 2, WINDOW_HEIGHT - 60))
            
            display.update()
            
            keys = key.get_pressed()
            if keys[K_m]:
                game_state = "MENU"
                level_menu_active = False
    
    clock.tick(FPS)

pygame.quit()
