from random import randint
from pygame import *
import pygame
from time import time as timer

# Инициализация
mixer.init()
font.init()

# Настройки окна
window = display.set_mode((700, 500))
display.set_caption('Шутер')
galaxy = transform.scale(image.load('galaxy.jpg'), (700, 500))

# Игровые переменные
game = True
finish = False
lost = 0
score = 0   
player_speed = 4.5
num_fire = 0
rel_time = False
reload_start = 0
reload_time = 3
lives = 3
last_shot_time = 0
shot_delay = 0.2

# Группы спрайтов
monsters = sprite.Group()
asteroids = sprite.Group()
bullets = sprite.Group()

# Шрифты
font_main = font.Font(None, 36)
font_big = font.Font(None, 50)

# Кадры в секунду
clock = pygame.time.Clock()
FPS = 60

# Звуки
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

# ==========================================
# ФУНКЦИЯ РЕСТАРТА
# ==========================================

def reset_game():
    global lost, score, finish, monsters, asteroids, bullets, player, num_fire, rel_time, lives
    
    # Сбрасываем переменные
    lost = 0
    score = 0
    finish = False
    num_fire = 0
    rel_time = False
    lives = 3
    
    # Очищаем группы спрайтов
    monsters.empty()
    asteroids.empty()
    bullets.empty()
    
    # Создаём игрока заново
    player = Player('rocket.png', 100, 400, 80, 90, player_speed)
    
    # Создаём новых монстров
    for i in range(5):
        monster = Enemy('ufo.png', randint(80, 600), 0, 80, 60, randint(1, 2))
        monsters.add(monster)
    
    # Создаём астероиды
    for i in range(3):
        asteroid = Enemy('asteroid.png', randint(80, 600), 0, 60, 60, randint(1, 2))
        asteroids.add(asteroid)

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
    

class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)

    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < 620:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet('bullet.png', self.rect.centerx - 7, self.rect.top, 15, 20, 15)
        bullets.add(bullet)
        fire_sound.play()


class Enemy(GameSprite):
    def update(self):
        global lost
        self.rect.y += self.speed
        if self.rect.y >= 500:
            self.rect.y = 0
            self.rect.x = randint(0, 600)
            lost += 1


class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()


# ==========================================
# СОЗДАНИЕ ОБЪЕКТОВ
# ==========================================

player = Player('rocket.png', 100, 400, 80, 90, player_speed)

for i in range(5):
    monster = Enemy('ufo.png', randint(80, 600), 0, 80, 60, randint(1, 2))
    monsters.add(monster)

for i in range(3):
    asteroid = Enemy('asteroid.png', randint(80, 600), 0, 60, 60, randint(1, 2))
    asteroids.add(asteroid)


# ==========================================
# ИГРОВОЙ ЦИКЛ
# ==========================================

while game:
    
    # Обработка событий
    for e in event.get():
        if e.type == QUIT:
            game = False
        
        # РЕСТАРТ ПО КНОПКЕ R
        if e.type == KEYDOWN:
            if e.key == K_r:
                reset_game()

    if not finish:
        # 1. УПРАВЛЕНИЕ
        keys = key.get_pressed()
        
        if keys[K_SPACE]:
            now = timer()
            # ЗАДЕРЖКА МЕЖДУ ВЫСТРЕЛАМИ
            if now - last_shot_time > shot_delay:
                if rel_time == False:
                    player.fire()
                    num_fire += 1
                    last_shot_time = now
                    
                    if num_fire >= 5:
                        rel_time = True      
                        reload_start = timer()
                        num_fire = 0
        
        # Проверяем, закончилась ли перезарядка
        if rel_time:
            now = timer()
            if now - reload_start >= reload_time:
                rel_time = False


        # 2. ОБНОВЛЕНИЕ ОБЪЕКТОВ
        player.update()
        monsters.update()
        asteroids.update()
        bullets.update()

        # 3. СТОЛКНОВЕНИЯ
        
        # Пули с монстрами
        collisions = sprite.groupcollide(bullets, monsters, True, True)
        for i in range(len(collisions)):
            new_monster = Enemy('ufo.png', randint(80, 600), 0, 80, 60, randint(1, 2))
            monsters.add(new_monster)
            score += 1
        
        # Игрок с монстрами
        crash_monster = sprite.spritecollide(player, monsters, True)
        if crash_monster:
            lives -= 1
            # Создаём нового монстра вместо убитого
            for i in range(len(crash_monster)):
                new_monster = Enemy('ufo.png', randint(80, 600), 0, 80, 60, randint(1, 2))
                monsters.add(new_monster)
        
        # Игрок с астероидами
        crash_asteroid = sprite.spritecollide(player, asteroids, True)
        if crash_asteroid:
            lives -= 1
            # Создаём новый астероид вместо убитого
            for i in range(len(crash_asteroid)):
                new_asteroid = Enemy('asteroid.png', randint(80, 600), 0, 60, 60, randint(1, 2))
                asteroids.add(new_asteroid)

        # 4. ПРОВЕРКА УСЛОВИЙ ПОБЕДЫ/ПОРАЖЕНИЯ
        if lives <= 0 or lost >= 3:
            finish = True
            result_text = font_big.render('ПРОИГРЫШ!', 1, (255, 0, 0))
        
        elif score >= 30:
            finish = True
            result_text = font_big.render('ПОБЕДА!', 1, (0, 255, 0))

        # 5. ОТРИСОВКА
        window.blit(galaxy, (0, 0))
        
        player.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)
        
        # Текстовая информация
        text_lost = font_main.render('Пропущено: ' + str(lost), 1, (255, 255, 255))
        window.blit(text_lost, (10, 10))
        
        text_score = font_main.render('Счет: ' + str(score), 1, (255, 255, 255))
        window.blit(text_score, (10, 50))
        
        # ЖИЗНИ
        text_lives = font_main.render('Жизни: ' + str(lives), 1, (255, 255, 255))
        window.blit(text_lives, (10, 90))
        
        display.update()
    
    else:
        # ЭКРАН РЕЗУЛЬТАТА
        window.blit(galaxy, (0, 0))
        
        # Рисуем всё, что было на момент окончания
        player.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)
        
        # Текстовая информация
        window.blit(font_main.render('Пропущено: ' + str(lost), 1, (255, 255, 255)), (10, 10))
        window.blit(font_main.render('Счет: ' + str(score), 1, (255, 255, 255)), (10, 50))
        window.blit(font_main.render('Жизни: ' + str(lives), 1, (255, 255, 255)), (10, 90))
        
        # Результат поверх всего
        window.blit(result_text, (250, 200))
        
        # Подсказка для рестарта
        restart_text = font_main.render('Нажми R для рестарта', 1, (200, 200, 200))
        window.blit(restart_text, (220, 400))
        
        display.update()
    
    clock.tick(FPS)
