import csv
from time import time
import pygame
import pytmx
import os
import sys
import random

MAPS_DIR = 'data/maps'
HERO_DIR = 'data/hobbit'
CUR_DIR = os.getcwd()
FPS = 60
SIZE = WIDTH, HEIGHT = 960, 480

pygame.init()
pygame.display.set_caption('CaveFighter')
screen = pygame.display.set_mode(SIZE)


class Menu(pygame.sprite.Sprite):
    def __init__(self):
        # 960 480
        self.cur_frame = 0
        self.background = pytmx.load_pygame(f'{CUR_DIR}/data/maps/new.tmx')
        self.tiles = pygame.sprite.Group()
        self.buttons = [pygame.sprite.Group(), pygame.sprite.Group(),
                        pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()]
        self.buttons[0].add([Button(380, 80, self.play, 'play'), Button(
            380, 200, self.options, 'options'), Button(380, 320, self.exit, 'exit')])

        self.buttons[1].add([Button(465, 80, self.restart, 'restart_mini'), Button(375, 80, self.play, 'play_mini'), Button(
            380, 200, self.options, 'options'), Button(380, 320, self.exit, 'exit')])

        self.buttons[2].add([Button(465, 80, self.restart, 'restart_mini'), Button(375, 80, self.next, 'next'), Button(
            380, 170, self.options, 'options'), Button(380, 260, self.exit, 'exit')])

        self.buttons[3].add([Button(280, 80, game.minus_color, '65'), Button(580, 80, game.plus_color, '64'),
                             Button(280, 180, game.plus_hard, '65'), Button(
                                 580, 180, game.minus_hard, '64'),
                             Button(280, 280, game.plus_lvl, '65'), Button(580, 280, game.minus_lvl, '64')])
        
        self.buttons[4].add([Button(330, 80, self.restart, 'restart_mini'), Button(500, 80, self.options, 'options')])


        game.sliders.add([Slider(320, 80, None, 4), Slider(
            320, 180, None, 4), Slider(360, 280, None, 3)])
        self.sliders = game.sliders.sprites()
        self.render()

    def render(self):
        for layer in self.background:
            for x, y, image in layer.tiles():
                image = pygame.transform.scale(image, (32, 32))
                Block(x * 32, y * 32, image, self.tiles, False)

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i in self.buttons[self.cur_frame]:
                        btn = i.rect.collidepoint(*event.pos)
                        if btn:
                            i.func()
                if event.type == pygame.MOUSEMOTION:
                    for i in self.buttons[self.cur_frame]:
                        i.hover(event.pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            screen.fill('black')
            self.tiles.draw(screen)
            self.buttons[self.cur_frame].update()
            self.buttons[self.cur_frame].draw(screen)
            self.sliders[0].update(game.theme_lst.index(game.color))
            self.sliders[1].update(game.hard_level)
            self.sliders[2].update(game.cur_map)
            if self.cur_frame == 3:
                game.sliders.draw(screen)
            if self.cur_frame == 4:
                img = load_image('data', 'tanos')
                screen.blit(img, (240, 180))
            pygame.display.update()
            game.clock.tick(15)

    def play(self):
        self.running = False

    def pause(self):
        self.running = True
        self.cur_frame = 1
        self.run()

    def restart(self):
        self.running = False
        game.all_sprites.empty()
        game.setup()

    def exit(self):
        pygame.quit()
        quit()

    def options(self):
        self.cur_frame = 3

    def death(self):
        self.running = True
        self.cur_frame = 1
        self.run()

    def finish(self):
        self.cur_frame = 2
        self.running = True
        self.run()

    def next(self):
        self.running = False
        game.all_sprites.empty()
        game.cur_map += 1
        game.setup()

    def endgame(self):
        self.running = True
        self.cur_frame = 4
        game.cur_map = 0
        self.run()


def load_image(folder_name, name, colorkey=None) -> pygame.Surface:
    fullname = os.path.join(folder_name, name + '.png')
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image

# загрузка персонажей


def find_borders(list):
    maxx, maxy, minx, miny = 0, 0, 63, 63
    for i in list:
        for y in range(i.get_height()):
            for x in range(i.get_width()):
                r, g, b, a = i.get_at((x, y))
                if a:
                    maxx = x if x > maxx else maxx
                    maxy = y if y > maxy else maxy
                    minx = x if x < minx else minx
                    miny = y if y < miny else miny
    return minx, miny, maxx - minx + 1, maxy - miny + 1


def load_char(name: str, frames, char='Hobbit'):
    lst = [load_image(f'{CUR_DIR}/data/{char}', name + str(i))
           for i in range(1, frames + 1)]
    x, y, w, h = find_borders(lst)

    if name.startswith('Knight'):
        lst = [pygame.transform.scale(i.subsurface(
            pygame.Rect(x, y, w, h)), (100 * (w / h), 96)) for i in lst]
    elif not name.startswith('bullet'):
        lst = [pygame.transform.scale(i.subsurface(
            pygame.Rect(x, y, w, h)), (36 * (w / h), 36)) for i in lst]
    else:
        lst = pygame.transform.scale(lst[0].subsurface(
            pygame.Rect(x, y, w, h)), (10 * (w / h), 10))
    return lst


def create_particles(position):
    particle_count = 20
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))

# создание класса карты


class Map():
    def __init__(self, filename, start_pos, finish_tile=0):
        # загрузка tmx файла
        self.map = pytmx.load_pygame(f'{CUR_DIR}/{MAPS_DIR}/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = 32
        self.finish_tile = finish_tile
        self.screen = screen
        self.flag = True
        self.water = 1
        self.start_pos = start_pos

    # получение списков блоков для дальнейшей отрисовки
    def render(self):
        for layer in self.map.layers:

            for x, y, image in layer.tiles():
                image = pygame.transform.scale(image, (32, 32))

                if layer.id == 2 and self.get_tile_id((x, y), 1) in [19, 20, 21]:
                    Block(x * self.tile_size, y *
                          self.tile_size, image, game.stairs)

                elif self.map.layers[1] == layer:
                    Block(x * self.tile_size, y *
                          self.tile_size, image, game.blocks)
                    Wall(x * self.tile_size, y * self.tile_size, 0)
                    Wall(x * self.tile_size, y * self.tile_size, 1)
                    Floor(x * self.tile_size, y * self.tile_size)

                elif self.map.layers[0] == layer:
                    if (x, y) == self.finish_tile:
                        bgroup = game.finish_tile
                    else:
                        bgroup = game.background
                    Block(x * self.tile_size, y *
                          self.tile_size, image, bgroup)

                elif self.map.layers[2] == layer:
                    Block(x * self.tile_size, y *
                          self.tile_size, image, game.falls1)

                elif self.map.layers[3] == layer:
                    Block(x * self.tile_size, y *
                          self.tile_size, image, game.falls2)
                else:
                    Block(x * self.tile_size, y *
                          self.tile_size, image, game.decor)

    # отрисовка блоков и создание некоторых анимаций(водопады)
    def draw(self, screen):
        game.background.draw(screen)
        game.blocks.draw(screen)
        game.stairs.draw(screen)
        game.finish_tile.draw(screen)

    def draw_falls(self, screen):
        if self.water:
            game.falls1.draw(screen)
        else:
            game.falls2.draw(screen)
        self.water = 1 if self.water == 0 else 0

    def get_tile_id(self, position, layer):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, layer)]

    def is_free(self, position, layer):
        return self.get_tile_id(position, layer) in self.free_titles

# класс для создания каждого блока


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, image: pygame.Surface, group, flag=True):
        if flag:
            super().__init__(game.all_sprites, group)
        else:
            super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

# класс стены


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, orientation):
        self.orientation = orientation
        self.vector_y = 1
        group = game.left_walls if self.orientation == 0 else game.right_walls
        super().__init__(game.all_sprites, group)
        self.height = 20
        self.weigth = 1
        self.rect = pygame.Rect(x + 1 + 30 * orientation,
                                y + 6, self.weigth, self.height)
        self.image = pygame.Surface(
            (self.weigth, self.height), masks=pygame.Color(0, 0, 0))


class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(game.all_sprites, game.floors)
        self.rect = pygame.Rect(x + 1, y + 1, 30, 1)
        self.image = pygame.Surface((30, 1), masks=pygame.Color(0, 0, 0))

# класс любого юнита на карте


class Creature(pygame.sprite.Sprite):
    def __init__(self, coords, group, name='Hobbit'):
        super().__init__(game.all_sprites, group)
        self.health = 10
        self.max_hp = 10
        self.group = group
        self.frames = []
        self.cur_frame = 0
        self.frame_dict = {'Idle': 4, 'run': 10,
                           'attack': 17, 'death': 12, 'hit': 4}
        self.speed = 10
        self.vector = 1
        self.vector_y = 1
        self.jumping = False
        self.jumping_frame = 0
        self.name = name

        self.falling = False
        #self.jumping_frames = [40 - (8 * i**2) / 2 for i in range(1, 8)]
        self.jumping_frames = [-8, -8, -8, -8, -8, -8, -8, -8]

        self.stay()
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = coords
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, command):
        self.frames.clear()
        self.frames = command

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame] if self.vector > 0 else pygame.transform.flip(
            self.frames[self.cur_frame], True, False)

        if not self.check_stay() and self.cur_func != 6 and not self.jumping:
            self.falling = True
        else:
            self.falling = False

        if self.falling:
            self.rect.y += 8

        if self.jumping:
            self.rect.y += self.jumping_frames[self.jumping_frame]
            self.jumping_frame += 1
            if self.jumping_frame >= 8:
                self.jumping = False
                self.jumping_frame = 0

        if self.cur_func == 8:
            if self.cur_frame == 11:
                self.group.remove(self)
                if self.group == game.heroes:
                    game.menu.death()
            if self.name == 'Knight':
                if self.timer:
                    game.enemies.remove(self)
                    if time() - self.timer > 3:
                        game.menu.endgame()
                        self.kill()
                        
                

        if self.cur_func == 7:
            if self.cur_frame - 1 == 0:
                self.stay()
            if self.health <= 0:
                self.death()

        if self.cur_func == 5:
            if self.name == 'Knight':
                if self.cur_frame == 4:
                    if pygame.sprite.spritecollideany(self, game.heroes):
                        game.hero.hit(2 + 1 * game.hard_level)
            if self.cur_frame == self.frame_dict['attack'] - 1:
                self.stay()
            if self.cur_frame == 12:
                Bullet((self.rect.x + 12 + self.vector *
                       12, self.rect.y + 12), self.vector, self.group)

        if self.cur_func == 6:
            if pygame.sprite.spritecollideany(self, game.stairs):
                for stair in game.stairs:
                    if stair.rect.colliderect(pygame.Rect(self.rect.x + 16, self.rect.y, 1, 33)):
                        if (not self.check_stay() and self.vector_y == 1) or self.vector_y == -1:
                            self.rect.y += 10 * self.vector_y
                            break
                else:
                    self.stay()

        if self.cur_func == 2:
            group = game.left_walls if self.vector == 1 else game.right_walls
            if not pygame.sprite.spritecollideany(self, group):
                self.rect.x += self.speed * \
                    self.vector if not self.jumping and not self.falling else 5 * self.vector
            else:
                self.stay()

        self.check_finish()
        self.check_death()

    def stay(self):
        self.cur_func = 1
        self.cut_sheet(
            load_char(f'{self.name} - Idle', self.frame_dict['Idle'], char=self.name))

    def run(self):
        self.cur_func = 2
        self.cut_sheet(
            load_char(f'{self.name} - run', self.frame_dict['run'], char=self.name))

    def fall(self):
        self.falling = True

    def jump(self):
        if self.check_stay():
            self.jumping = True

    def attack(self, attack=0):
        self.cur_func = 5

        if attack == 0:
            self.cut_sheet(
                load_char(f'{self.name} - attack', self.frame_dict['attack'], char=self.name))

    def claimbing(self, flag=1):
        self.cur_func = 6
        self.vector_y = flag

    def hit(self, damage):
        if self.cur_func != 8:
            self.health -= damage
            if self.group == game.heroes:
                game.interface.change_hp(-damage)

            self.cur_func = 7
            self.cut_sheet(
                load_char(f'{self.name} - hit', self.frame_dict['hit'], char=self.name))

    def death(self):
        if self.cur_func != 8:
            self.cur_func = 8
            self.cut_sheet(
                load_char(f'{self.name} - death', self.frame_dict['death'], char=self.name))

    def check_stay(self):
        return pygame.sprite.spritecollideany(self, game.floors)

    def check_death(self):
        if self.rect.y >= 480 and self.name == 'Hobbit':
            game.menu.death()
        elif self.name in ['Knight', 'DarkHobbit']:
            if self.health <= 0:
                self.death()

    def check_finish(self):
        if pygame.sprite.spritecollideany(self, game.finish_tile):
            game.menu.finish()


class Enemy(Creature):
    def find_hero(self):
        for i in range(self.rect.x - 8 * 32, self.rect.x + 8 * 32):
            if game.hero.rect.collidepoint(i, self.rect.y + 2 / 3 * self.rect.h):
                if abs(self.rect.x - i) > self.attack_range * 32 and self.cur_func != 2 and self.cur_func != 5:
                    self.vector = -1 if self.rect.x > i else 1
                    self.run()
                    break
                elif self.cur_func == 1:
                    self.vector = -1 if self.rect.x > i else 1
                    if self.cur_func != 5:
                        self.attack()
                else:
                    if self.cur_func != 1 and self.cur_func != 5:
                        self.stay()

    def death(self):
        self.cur_func = 8
        create_particles((self.rect.x + 10, self.rect.y + 30))
        if self.name == 'Knight':
            if self.timer == False:
                self.timer = time()
        else:
            self.kill()    
        


class Particle(pygame.sprite.Sprite):
    fire = [load_image("data/Knight", "star")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(game.particles)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        self.gravity = 1

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen.get_rect()):
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, coords, vector, group):
        super().__init__(game.all_sprites, game.balls)
        self.image = load_char('bullet - ', 1)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = coords
        self.cur_distance = 0
        self.vector = vector
        if group == game.enemies:
            self.group = game.heroes
        else:
            self.group = game.enemies

    def update(self):
        self.rect.x += self.vector * 15
        self.cur_distance += 15
        char = pygame.sprite.spritecollideany(self, self.group)

        if self.cur_distance // 32 > 8 or pygame.sprite.spritecollideany(self, game.blocks):
            game.balls.remove(self)
        if char:
            if self.group == game.heroes:
                char.hit(1 * game.hard_level + 1)
            else:
                char.hit(1)
            game.balls.remove(self)


class Interface(pygame.sprite.Sprite):
    def __init__(self, char):
        self.max_hp = char.max_hp
        self.cur_hp = char.max_hp
        self.hearts = [Health(2, i) for i in range(self.max_hp // 2)]
        self.buttons = pygame.sprite.Group([Button(884, 10, game.menu.pause, 'pause_mini', 1), Button(
            926, 10, game.menu.restart, 'restart_mini', 1)])

    def change_hp(self, change):
        self.cur_hp += change
        count = 0
        for i in self.hearts:
            if self.cur_hp - count >= 2:
                i.change(2)

                count += 2
            elif self.cur_hp - count >= 1:
                i.change(1)
                count += 1
            else:
                i.change(0)


class Health(pygame.sprite.Sprite):
    def __init__(self, hp, coord):
        super().__init__(game.hearts)
        self.hp = hp
        self.frames = load_image(
            f'{CUR_DIR}/data/hearts/animated/border', 'heart_animated_2')
        self.frames = [pygame.transform.scale(self.frames.subsurface(pygame.Rect(
            i, 0, 17, 17)), (32, 32)) for i in range(0, self.frames.get_width(), self.frames.get_width() // 5)]
        self.hp1 = self.frames[2]
        self.hp2 = self.frames[0]
        self.hp0 = self.frames[4]
        self.image = self.frames[0] if self.hp == 2 else self.frames[2]
        self.rect = self.hp1.get_rect()
        self.rect.x = coord * 32

    def change(self, hp):
        self.hp = hp
        if self.hp == 2:
            self.image = self.hp2
        elif self.hp == 1:
            self.image = self.hp1
        else:
            self.image = self.hp0


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, func, name, koeff=2.5) -> None:
        super().__init__(game.buttons)
        self.koeff = koeff
        self.name = name
        self.func = func
        img1 = load_image(f'{CUR_DIR}/data/buttons/menu' + game.color, name)
        img2 = load_image(f'{CUR_DIR}/data/buttons/menu' +
                          game.color, name + '_pressed')
        self.w, self.h = img1.get_width(), img1.get_height()
        self.image1 = pygame.transform.scale(
            img1, (self.w * koeff, self.h * koeff))
        self.image2 = pygame.transform.scale(
            img2, (self.w * koeff, self.h * koeff))
        self.rect = self.image1.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hover((0, 0))

    def update_color(self):
        img1 = load_image(
            f'{CUR_DIR}/data/buttons/menu' + game.color, self.name)
        img2 = load_image(f'{CUR_DIR}/data/buttons/menu' +
                          game.color, self.name + '_pressed')
        self.image1 = pygame.transform.scale(
            img1, (self.w * self.koeff, self.h * self.koeff))
        self.image2 = pygame.transform.scale(
            img2, (self.w * self.koeff, self.h * self.koeff))

    def hover(self, pos):
        if self.rect.collidepoint(*pos):
            self.image = self.image2
            return True
        self.image = self.image1
        return False


class Slider(pygame.sprite.Sprite):
    def __init__(self, x, y, func, len) -> None:
        super().__init__(game.sliders)
        self.len = len
        self.coords = x, y
        self.func = func
        self.render()

    def render(self):
        self.left_border = pygame.transform.scale(load_image(
            f'{CUR_DIR}/data/buttons/menu' + game.color, '47'), (80, 80))
        self.centaral = pygame.transform.scale(load_image(
            f'{CUR_DIR}/data/buttons/menu' + game.color, '48'), (80, 80))
        self.right_border = pygame.transform.scale(load_image(
            f'{CUR_DIR}/data/buttons/menu' + game.color, '49'), (80, 80))

        self.centaral_empty = pygame.transform.scale(load_image(
            f'{CUR_DIR}/data/buttons/menu' + game.color, '54'), (80, 80))
        self.right_border_empty = pygame.transform.scale(load_image(
            f'{CUR_DIR}/data/buttons/menu' + game.color, '55'), (80, 80))

    def update(self, n):
        self.n = n
        self.image = pygame.Surface((80 * self.len, 80), pygame.SRCALPHA)
        self.image.blit(self.left_border, (0, 0))
        count = 0
        for i in range(self.len - 2):
            if count + 1 > n:
                self.image.blit(self.centaral_empty, ((i + 1) * 80 - 15, 0))
            else:
                self.image.blit(self.centaral, ((i + 1) * 80 - 15, 0))
                count += 1
        if count + 1 > n:
            self.image.blit(self.right_border_empty,
                            ((self.len - 1) * 80 - 30, 0))
        else:
            self.image.blit(self.right_border, ((self.len - 1) * 80 - 30, 0))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.coords


class Camera:
    def __init__(self):
        self.dx = 0
        self.change = 0

    def apply(self, obj):
        if self.change + self.dx > -3064510:
            obj.rect.x += self.dx
            self.change += self.dx

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - 32 // 2) + 200


class Game():
    def __init__(self):
        self.maps = [('second.tmx', (32 * 13, 7 * 32), (66, 14)),
                     ('third.tmx', (32 * 12, 0), (57, 1)),
                     ('fourth.tmx', (32 * 13, 13 * 32), (0, 0))]
        pygame.mixer.music.load(f'{CUR_DIR}/data/music/CaveStory.mp3')
        pygame.mixer.music.set_volume(0.03)
        pygame.mixer.music.play()
        self.theme_lst = ['b', 'g', 'p', 'r']
        self.color = 'b'
        self.cur_map = 0
        self.hard_level = 1
        self.start = True
        self.poses_lst = [[(27 * 32, 9 * 32), (38 * 32, 4 * 32)], [(28 * 32, 6 * 32), (48 * 32, 6 * 32), (17 * 32, 9 * 32)], [
            (41 * 32, 8 * 32), (47 * 32, 8 * 32), (36 * 32, 4 * 32), (52 * 32, 4 * 32)]]
        with open(f'{CUR_DIR}/data/data.csv') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for index, row in enumerate(reader):
                if row:
                    if row[0] == 'cur-map':
                        self.cur_map = int(row[1])
                    if row[0] == 'color':
                        self.color = row[1]
                    if row[0] == 'hard-level':
                        self.hard_level = int(row[1])

    def change_theme(self, n):
        cur_color = self.theme_lst.index(self.color)
        n += cur_color
        n %= 4
        self.color = self.theme_lst[n]

    def setup(self):
        self.all_sprites = pygame.sprite.Group()
        # units
        self.heroes = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        # map
        self.blocks = pygame.sprite.Group()
        self.background = pygame.sprite.Group()
        self.left_walls = pygame.sprite.Group()
        self.right_walls = pygame.sprite.Group()
        self.floors = pygame.sprite.Group()
        self.decor = pygame.sprite.Group()
        self.stairs = pygame.sprite.Group()
        self.finish_tile = pygame.sprite.Group()

        # falls
        self.falls1 = pygame.sprite.Group()
        self.falls2 = pygame.sprite.Group()

        # Interface
        self.hearts = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        self.sliders = pygame.sprite.Group()

        # CONSTS

        # Custom Events
        self.play = pygame.USEREVENT + 1
        self.pause = pygame.USEREVENT + 2
        self.options = pygame.USEREVENT + 3

        self.map = Map(*self.maps[self.cur_map])

        self.running = True
        self.clock = pygame.time.Clock()

        for i in self.poses_lst[self.cur_map]:
            enemy = Enemy(i, self.enemies, 'DarkHobbit')
            enemy.attack_range = 4
            enemy.health = 2

        self.hero = Creature(self.map.start_pos, self.heroes, 'Hobbit')

        if self.cur_map == 2:
            self.boss = Enemy((47 * 32, 310), self.enemies, 'Knight')
            self.boss.timer = False
            self.boss.attack_range = 1
            self.boss.frame_dict = {'Idle': 4, 'run': 8, 'attack': 7, 'hit': 2}
            self.boss.speed = 7

        self.camera = Camera()

        self.menu = Menu()
        if self.start:
            self.menu.run()

        self.interface = Interface(self.hero)
        self.map.render()
        self.start = False

    def plus_color(self):
        if self.color != 'r':
            self.color = self.theme_lst[self.theme_lst.index(self.color) + 1]
            for i in self.buttons:
                i.update_color()
            for i in self.sliders:
                i.render()
            self.changecsv()

    def minus_color(self):
        if self.color != 'b':
            self.color = self.theme_lst[self.theme_lst.index(self.color) - 1]
            for i in self.buttons:
                i.update_color()
            for i in self.sliders:
                i.render()
            self.changecsv()

    def plus_hard(self):
        if self.hard_level > 0:
            self.hard_level -= 1
            self.changecsv()

    def minus_hard(self):
        if self.hard_level < 3:
            self.hard_level += 1
            self.changecsv()

    def plus_lvl(self):
        if self.cur_map > 0:
            self.cur_map -= 1
            self.all_sprites.empty()
            self.setup()
            self.changecsv()
            self.run()

    def minus_lvl(self):
        if self.cur_map < 2:
            self.cur_map += 1
            self.all_sprites.empty()
            self.setup()
            self.changecsv()
            self.run()

    def changecsv(self):
        with open('data/data.csv', 'rt') as input_file:
            reader = csv.reader(input_file)
            with open('data/data.temp.csv', 'wt') as output_file:
                writer = csv.DictWriter(output_file, fieldnames=[
                                        'parameter', 'value'])
                for row in reader:
                    if row:
                        param, value = row
                        if param == 'color':
                            value = self.color
                        elif param == 'hard-level':
                            value = self.hard_level
                        elif param == 'cur-map':
                            value = self.cur_map
                        writer.writerow({'parameter': param, 'value': value})

        os.remove('data/data.csv')
        os.rename('data/data.temp.csv', 'data/data.csv')

    def run(self):
        while self.running:
            screen.fill('#000000')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # элементы движения
                if event.type == pygame.KEYDOWN and self.hero.cur_func != 8:
                    if event.key == pygame.K_d:
                        self.hero.run()
                        self.hero.vector = 1
                    if event.key == pygame.K_a:
                        self.hero.run()
                        self.hero.vector = -1
                    if event.key == pygame.K_f:
                        self.hero.attack()
                    if event.key == pygame.K_w:
                        self.hero.claimbing(-1)
                    if event.key == pygame.K_s:
                        self.hero.claimbing(1)
                    if event.key == pygame.K_SPACE or pygame.K_SPACE and pygame.key.get_mods() and pygame.K_d | pygame.K_a:
                        self.hero.jump()
                    if event.key == pygame.K_ESCAPE:
                        self.menu.pause()
                if (event.type == pygame.KEYUP and not self.hero.cur_func in [4, 5, 8]):
                    self.hero.stay()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i in game.interface.buttons:
                        btn = i.rect.collidepoint(*event.pos)
                        if btn:
                            i.func()

                if event.type == pygame.MOUSEMOTION:
                    for i in game.interface.buttons:
                        i.hover(event.pos)

            self.camera.update(self.hero)
            for sprite in self.all_sprites:
                self.camera.apply(sprite)

            for i in self.enemies:
                i.find_hero()

            self.map.draw(screen)
            self.decor.draw(screen)

            self.heroes.update()
            self.enemies.update()
            if self.cur_map == 2:
                self.boss.update()
            self.balls.update()
            self.balls.draw(screen)

            self.enemies.draw(screen)
            self.heroes.draw(screen)
            self.map.draw_falls(screen)
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()

            self.particles.update()
            self.particles.draw(screen)

            self.interface.buttons.draw(screen)
            self.hearts.draw(screen)

            self.clock.tick(15)
            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.setup()
    game.run()