import pygame
import math
from constants import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.base_image = pygame.image.load("assets/characters/enemy.png").convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, (32, 32))
            self.base_image.set_colorkey((255, 255, 255))
        except FileNotFoundError:
            self.base_image = pygame.Surface((32, 32))
            self.base_image.fill(RED)
            
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.start_x = x
        self.speed = 100
        self.direction = 1
        self.patrol_distance = 150
        
    def update(self, dt):
        self.rect.x += self.speed * self.direction * dt
        
        # Simple patrol AI
        if abs(self.rect.x - self.start_x) > self.patrol_distance:
            self.direction *= -1
            
        # Waddling animation
        angle = math.sin(pygame.time.get_ticks() * 0.01) * 15
        img = pygame.transform.rotate(self.base_image, angle)
        if self.direction == 1:
            img = pygame.transform.flip(img, True, False)
            
        self.image = img
        center = self.rect.center
        self.rect = self.image.get_rect(center=center)
            
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Troll(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        try:
            self.base_image = pygame.image.load("assets/characters/troll.png").convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, (48, 48))
            self.base_image.set_colorkey((255, 255, 255))
        except FileNotFoundError:
            self.base_image = pygame.Surface((48, 48))
            self.base_image.fill((0, 100, 0)) # Dark green
            
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - 16 # Adjust for larger size
        
        self.start_x = x
        self.speed = 50 # Slow
        self.health = 3
        self.direction = 1
        self.patrol_distance = 100

class GiantSnake(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        try:
            self.base_image = pygame.image.load("assets/characters/snake.png").convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, (32, 16))
            self.base_image.set_colorkey((255, 255, 255))
        except FileNotFoundError:
            self.base_image = pygame.Surface((32, 16))
            self.base_image.fill((173, 255, 47)) # Yellow green
            
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y + 16 # Adjust for shorter size
        
        self.start_x = x
        self.speed = 200 # Fast
        self.health = 1
        self.direction = 1
        self.patrol_distance = 250

class Dragon(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        try:
            self.base_image = pygame.image.load("assets/characters/dragon.png").convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, (56, 56))
            self.base_image.set_colorkey((255, 255, 255))
        except FileNotFoundError:
            self.base_image = pygame.Surface((56, 56))
            self.base_image.fill((128, 0, 128)) # Purple
            
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - 24 # Adjust for larger size
        
        self.start_x = x
        self.speed = 150 # Fast
        self.health = 5
        self.direction = 1
        self.patrol_distance = 350

