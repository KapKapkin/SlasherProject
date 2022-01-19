import pygame
import pytmx
import os
import sys


class Menu(pygame.sprite.Sprite):
    def __init__(self):
        # 960 480
        self.running = True
        self.background = pytmx.load_pygame('data/maps/new.tmx')
        self.tiles = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        self.buttons.add([Button(380, 130, play), Button(380, 250, options)])
        self.render()

    def render(self):
        for layer in self.background:
            for x, y, image in layer.tiles():
                image = pygame.transform.scale(image, (32, 32))
                a = Block(x * 32, y * 32, image, self.tiles)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    return
                if event.type == pygame.MOUSEMOTION:
                    for i in self.buttons:
                        i.hover(event.pos)

            screen.fill('black')
            self.tiles.draw(screen)
            self.buttons.draw(screen)
            pygame.display.update()
            clock.tick(15)



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
                if not (r < 20 and g < 20 and b < 20):
                    maxx = x if x > maxx else maxx
                    maxy = y if y > maxy else maxy
                    minx = x if x < minx else minx
                    miny = y if y < miny else miny
    print(minx, miny, maxx - minx + 1, maxy - miny + 1)
    return minx, miny, maxx - minx + 1, maxy - miny + 1


def load_char(name: str, frames, char='hobbit'):
    lst = [load_image(f'data/{char}', name + str(i))
           for i in range(1, frames + 1)]
    x, y, w, h = find_borders(lst)
    if not name.startswith('bullet'):
        lst = [pygame.transform.scale(i.subsurface(
            pygame.Rect(x, y, w, h)), (36 * (w / h), 36)) for i in lst]
    else:
        lst = pygame.transform.scale(lst[0].subsurface(
            pygame.Rect(x, y, w, h)), (10 * (w / h), 10))
    return lst

# создание класса карты


class Map():
    def __init__(self, filename, finish_tile=0):
        # загрузка tmx файла
        self.map = pytmx.load_pygame(f'{MAPS_DIR}/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = 32
        self.finish_title = finish_tile
        self.screen = screen
        self.flag = True
        self.water = 1

    # получение списков блоков для дальнейшей отрисовки
    def render(self):
        for layer in self.map.layers:

            for x, y, image in layer.tiles():
                image = pygame.transform.scale(image, (32, 32))

                if layer.id == 1 and self.get_tile_id((x, y), 1) in [20, 21]:
                    Block(x * self.tile_size, y *
                          self.tile_size, image, stairs)

                elif self.map.layers[1] == layer:
                    Block(x * self.tile_size, y *
                          self.tile_size, image, blocks)
                    Wall(x * self.tile_size, y * self.tile_size, 0)
                    Wall(x * self.tile_size, y * self.tile_size, 1)

                elif self.map.layers[0] == layer:
                    Block(x * self.tile_size, y *
                          self.tile_size, image, background)

                elif self.map.layers[2] == layer:
                    Block(x * self.tile_size, y *
                          self.tile_size, image, falls1)

                elif self.map.layers[3] == layer:
                    Block(x * self.tile_size, y *
                          self.tile_size, image, falls2)
                else:
                    Block(x * self.tile_size, y * self.tile_size, image, decor)

    # отрисовка блоков и создание некоторых анимаций(водопады)
    def draw(self, screen):
        background.draw(screen)
        blocks.draw(screen)
        stairs.draw(screen)

    def draw_falls(self, screen):
        if self.water:
            falls1.draw(screen)
        else:
            falls2.draw(screen)
        self.water = 1 if self.water == 0 else 0

    def get_tile_id(self, position, layer):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, layer)]

    def is_free(self, position, layer):
        return self.get_tile_id(position, layer) in self.free_titles

# класс для создания каждого блока


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, image: pygame.Surface, group):
        super().__init__(all_sprites, group)
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
        group = left_walls if self.orientation == 0 else right_walls
        super().__init__(all_sprites, group)
        self.height = 25
        self.weigth = 1
        self.rect = pygame.Rect(x + 1 + 30 * orientation,
                                y + 5, self.weigth, self.height)
        self.image = pygame.Surface(
            (self.weigth, self.height), masks=pygame.Color(0, 0, 0))

# класс любого юнита на карте


class Creature(pygame.sprite.Sprite):
    def __init__(self, coords, group):
        super().__init__(all_sprites, group)
        self.health = 10
        self.max_hp = 10
        self.group = group
        self.frames = []
        self.cur_frame = 0
        self.vector = 1
        self.vector_y = 1
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

        if self.cur_func == 8:
            if self.cur_frame == 11:
                enemies.remove(self)
                return

        if self.cur_func == 7:
            if self.cur_frame - 1 == 0:
                self.stay()
            if self.health <= 0:
                self.death()

        if self.cur_func == 5:
            if self.cur_frame == 16:
                self.stay()
            if self.cur_frame == 12:
                Bullet((self.rect.x + 12 + self.vector *
                       12, self.rect.y + 12), self.vector)

        if self.cur_func == 6:
            if pygame.sprite.spritecollideany(self, stairs):
                for stair in stairs:
                    if stair.rect.colliderect(pygame.Rect(self.rect.x + 16, self.rect.y, 1, 32)):
                        if (not self.check_stay() and self.vector_y == 1) or self.vector_y == -1:
                            self.rect.y += 10 * self.vector_y
                            break
                else:
                    self.stay()

        if self.cur_func == 4:
            pass

        elif not self.check_stay() and not self.cur_func == 6:
            self.fall()
            self.rect.y += 8

        if self.cur_func == 2:
            group = left_walls if self.vector == 1 else right_walls
            if not pygame.sprite.spritecollideany(self, group):
                self.rect.x += 10 * self.vector
            else:
                print(group)
                self.stay()

    def stay(self):
        self.cur_func = 1
        self.cut_sheet(load_char('Hobbit - Idle', 4))

    def run(self):
        self.cur_func = 2
        self.cut_sheet(load_char('Hobbit - run', 10))

    def fall(self):
        self.cur_func = 3

    def jump(self):
        pass

    def attack(self, attack=0):
        self.cur_func = 5
        if attack == 0:
            self.cut_sheet(load_char('Hobbit - attack', 17))

    def claimbing(self, flag=1):
        self.cur_func = 6
        self.vector_y = flag

    def hit(self, damage):
        self.health -= damage
        self.cur_func = 7
        self.cut_sheet(load_char('Hobbit - hit', 4))

    def death(self):
        self.cur_func = 8
        self.cut_sheet(load_char('Hobbit - death', 12))

    def check_stay(self):
        return pygame.sprite.spritecollideany(self, blocks)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, coords, vector):
        super().__init__(all_sprites, balls)
        self.image = load_char('bullet - ', 1)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = coords
        self.cur_distance = 0
        self.vector = vector

    def update(self):
        self.rect.x += self.vector * 15
        self.cur_distance += 15
        enemy = pygame.sprite.spritecollideany(self, enemies)
        if self.cur_distance // 32 > 8 or pygame.sprite.spritecollideany(self, blocks):
            balls.remove(self)
        if enemy:
            enemy.hit(10)
            balls.remove(self)


class Interface(pygame.sprite.Sprite):
    def __init__(self, char):
        self.hp = char.max_hp
        self.hearts = [Health(2, i) for i in range(self.hp // 2)]


class Health(pygame.sprite.Sprite):
    def __init__(self, hp, coord):
        super().__init__(hearts)
        self.hp = hp
        self.frames = load_image(
            'data/hearts/animated/border', 'heart_animated_2')
        self.frames = [pygame.transform.scale(self.frames.subsurface(pygame.Rect(
            i, 0, 17, 17)), (32, 32)) for i in range(0, self.frames.get_width(), self.frames.get_width() // 5)]
        self.hp1 = self.frames[2]
        self.image = self.frames[0]
        self.rect = self.hp1.get_rect()
        self.rect.x = coord * 32

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, func):
        super().__init__(buttons)
        if func == play: name = 'play'
        elif func == options: name = 'options'
        self.image1 = pygame.transform.scale(load_image('data/buttons/menug', name), (150, 75))
        self.image2 = pygame.transform.scale(load_image('data/buttons/menug', name + '_pressed'), (150, 75))
        self.rect = self.image1.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hover((0, 0))

    def hover(self, pos):
        if self.rect.collidepoint(*pos):
            self.image = self.image2
        else: self.image = self.image1


class Camera:
    def __init__(self):
        self.dx = 0

    def apply(self, obj):
        obj.rect.x += self.dx

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - 32 // 2) + 50


pygame.init()
pygame.display.set_caption('CaveFighter')

all_sprites = pygame.sprite.Group()
# units
heroes = pygame.sprite.Group()
enemies = pygame.sprite.Group()
balls = pygame.sprite.Group()
# map
blocks = pygame.sprite.Group()
background = pygame.sprite.Group()
left_walls = pygame.sprite.Group()
right_walls = pygame.sprite.Group()
decor = pygame.sprite.Group()
stairs = pygame.sprite.Group()

# falls
falls1 = pygame.sprite.Group()
falls2 = pygame.sprite.Group()

# Interface
hearts = pygame.sprite.Group()
buttons = pygame.sprite.Group()

# CONSTS
MAPS_DIR = 'data/maps'
HERO_DIR = 'data/hobbit'
FPS = 60
SIZE = WIDTH, HEIGHT = 960, 480

#Custom Events
play = pygame.USEREVENT + 1
pause = pygame.USEREVENT + 2
options = pygame.USEREVENT + 3

running = True
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SIZE)


hero = Creature((64, 7 * 32), heroes)
enemy = Creature((4 * 32, 7 * 32), enemies)
camera = Camera()
menu = Menu()
map = Map('first.tmx')


interface = Interface(hero)

map.render()

while running:
    screen.fill('#000000')
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # элементы движения
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                hero.run()
                hero.vector = 1
            if event.key == pygame.K_a:
                hero.run()
                hero.vector = -1
            if event.key == pygame.K_f:
                hero.attack()
            if event.key == pygame.K_w:
                hero.claimbing(-1)
            if event.key == pygame.K_s:
                hero.claimbing(1)
            if event.key == pygame.K_SPACE:
                hero.jump()
            if event.key == pygame.K_ESCAPE:
                menu.run()

        if (event.type == pygame.KEYUP and not hero.cur_func in [4, 5]):
            hero.stay()

    camera.update(hero)
    for sprite in all_sprites:
        camera.apply(sprite)

    map.draw(screen)
    decor.draw(screen)

    heroes.update()
    enemies.update()
    balls.update()
    balls.draw(screen)

    enemies.draw(screen)
    heroes.draw(screen)
    map.draw_falls(screen)

    hearts.draw(screen)

    clock.tick(10)
    pygame.display.flip()
pygame.quit()
