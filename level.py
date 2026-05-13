import pygame
import math
from constants import *
from enemy import Enemy, Troll, GiantSnake, Dragon
import random

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 215, 0)) # Gold color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.item_type = item_type
        self.image = pygame.Surface((20, 20))
        if item_type == "health":
            self.image.fill((0, 255, 0))
        elif item_type == "weapon":
            self.image.fill((0, 255, 255))
        elif item_type == "jump":
            self.image.fill((255, 0, 255)) # Magenta
        self.rect = self.image.get_rect()
        self.rect.x = x + 10
        self.rect.y = y + 20

class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        try:
            self.base_image = pygame.image.load("assets/characters/boss.png").convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, (64, 64))
            self.base_image.set_colorkey((255, 255, 255))
        except FileNotFoundError:
            self.base_image = pygame.Surface((64, 64))
            self.base_image.fill((139, 0, 0)) # Dark red
            
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 5
        self.speed = 150
        self.patrol_distance = 300
        self.start_x = x
        
    def update(self, dt):
        self.rect.x += self.speed * self.direction * dt
        if abs(self.rect.x - self.start_x) > self.patrol_distance:
            self.direction *= -1
            
        # Breathing animation
        scale_mod = 1.0 + math.sin(pygame.time.get_ticks() * 0.005) * 0.1
        new_size = (int(64 * scale_mod), int(64 * scale_mod))
        img = pygame.transform.scale(self.base_image, new_size)
        if self.direction == -1:
            img = pygame.transform.flip(img, True, False)
            
        self.image = img
        center = self.rect.center
        self.rect = self.image.get_rect(center=center)

class Level:
    def __init__(self, filepath, level_num=1):
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.goals = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.start_x = -1
        self.start_y = -1
        self.tile_size = 40
        self.width = 0
        self.height = 0
        self.load_level(filepath, level_num)
        
    def load_level(self, filepath, level_num):
        try:
            with open(filepath, 'r') as f:
                layout = f.readlines()
                
            self.width = max(len(row.rstrip('\n')) for row in layout) * self.tile_size
            self.height = len(layout) * self.tile_size
            for row_idx, row in enumerate(layout):
                for col_idx, col in enumerate(row.rstrip('\n')):
                    x = col_idx * self.tile_size
                    y = row_idx * self.tile_size
                    
                    if col == 'P':
                        platform = Platform(x, y, self.tile_size, self.tile_size)
                        self.platforms.add(platform)
                        # 2% chance to spawn a jump power-up on top of a platform
                        if random.random() < 0.02:
                            self.items.add(Item(x, y - self.tile_size, "jump"))
                    elif col == 'E':
                        # Dynamic difficulty scaling
                        if level_num >= 4:
                            choice = random.choices(['E', 'T', 'N', 'D'], weights=[10, 30, 30, 30])[0]
                        elif level_num == 3:
                            choice = random.choices(['E', 'T', 'N'], weights=[30, 40, 30])[0]
                        elif level_num == 2:
                            choice = random.choices(['E', 'T'], weights=[60, 40])[0]
                        else:
                            choice = 'E'
                            
                        if choice == 'T':
                            self.enemies.add(Troll(x, y))
                        elif choice == 'N':
                            self.enemies.add(GiantSnake(x, y))
                        elif choice == 'D':
                            self.enemies.add(Dragon(x, y))
                        else:
                            self.enemies.add(Enemy(x, y))
                    elif col == 'T':
                        self.enemies.add(Troll(x, y))
                    elif col == 'N':
                        self.enemies.add(GiantSnake(x, y))
                    elif col == 'D':
                        self.enemies.add(Dragon(x, y))
                    elif col == 'S':
                        if self.start_x == -1: # Only use the first S found
                            self.start_x = x
                            self.start_y = y
                    elif col == 'G':
                        goal = Goal(x, y)
                        self.goals.add(goal)
                    elif col == '+':
                        self.items.add(Item(x, y, "health"))
                    elif col == 'W':
                        self.items.add(Item(x, y, "weapon"))
                    elif col == 'J':
                        self.items.add(Item(x, y, "jump"))
                    elif col == 'B':
                        self.enemies.add(Boss(x, y))
                        
        except FileNotFoundError:
            print(f"Error loading level {filepath}. Using fallback layout.")
            # Fallback level
            self.width = SCREEN_WIDTH * 2
            self.height = SCREEN_HEIGHT
        if self.start_x == -1:
            self.start_x = 50
            self.start_y = SCREEN_HEIGHT - 100
            self.platforms.add(Platform(0, SCREEN_HEIGHT - 40, self.width, 40))
            self.platforms.add(Platform(200, 400, 100, 20))
            self.enemies.add(Enemy(300, SCREEN_HEIGHT - 72))

    def update(self, dt):
        self.enemies.update(dt)

    def draw(self, surface, camera_x):
        for p in self.platforms:
            surface.blit(p.image, (p.rect.x - camera_x, p.rect.y))
        for g in self.goals:
            surface.blit(g.image, (g.rect.x - camera_x, g.rect.y))
        for i in self.items:
            surface.blit(i.image, (i.rect.x - camera_x, i.rect.y))
        for enemy in self.enemies:
            surface.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y))
