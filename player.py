import pygame
import math
import os
import random
from constants import *

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 500
        self.direction = direction

    def update(self, dt):
        self.rect.x += self.speed * self.direction * dt

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character_type):
        super().__init__()
        self.character_type = character_type
        
        self.start_x = x
        self.start_y = y
        
        # Animations
        self.state = "idle"
        self.animation_timer = 0
        self.current_frame = 0
        self.animation_frames = {"idle": [], "walk": [], "jump": [], "attack": []}
        self._load_animations()
        
        self.particles = []
        self.shoot_cooldown = 0
        self.facing_direction = 1 # 1 for right, -1 for left
        
        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 300
        self.jump_power = -600
        self.gravity = 1500
        self.on_ground = False
        
        # Stats
        self.lives = 3
        self.score = 0
        self.health = 100
        self.inventory = []
        
        self.projectiles = pygame.sprite.Group()
        
    def _load_animations(self):
        # Using original character art as requested
        try:
            self.image = pygame.image.load(f"assets/characters/{self.character_type.lower()}.png").convert_alpha()
            # Visual size is 48x48
            self.image = pygame.transform.scale(self.image, (48, 48))
        except:
            self.image = pygame.Surface((48, 48))
            self.image.fill(GREEN)
            
        self.base_image = self.image.copy()
        
        # Use a collision box that is slightly smaller than the visual image
        self.rect = pygame.Rect(0, 0, 28, 40)
        # Place player precisely in the starting tile
        self.rect.midbottom = (self.start_x + 20, self.start_y + 40)

    def _animate(self, dt):
        # Advanced Programmatic Animation State Machine
        self.animation_timer += dt
        
        # Base effects
        self.bob_y = 0
        self.tilt_angle = 0
        self.scale_x, self.scale_y = 1.0, 1.0
        
        if not self.on_ground:
            # Jumping/Falling squash and stretch
            if self.velocity_y < -100: # Stretching up
                self.scale_x, self.scale_y = 0.8, 1.2
            elif self.velocity_y > 100: # Squashing down
                self.scale_x, self.scale_y = 1.2, 0.8
        elif abs(self.velocity_x) > 0:
            # Walking bob and tilt
            self.bob_y = math.sin(self.animation_timer * 15) * 4
            self.tilt_angle = math.sin(self.animation_timer * 15) * 10
            # Slight squash/stretch during walk
            self.scale_x = 1.0 + math.sin(self.animation_timer * 15) * 0.05
            self.scale_y = 1.0 - math.sin(self.animation_timer * 15) * 0.05
        else:
            # Idle breathing
            self.scale_y = 1.0 + math.sin(self.animation_timer * 3) * 0.03
            self.bob_y = math.sin(self.animation_timer * 3) * 2

    def update(self, dt, platforms, enemies, items, level_width, level_height):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            
        self.handle_input()
        
        # Particles update
        for p in self.particles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
            if p['life'] <= 0:
                self.particles.remove(p)
                
        self.projectiles.update(dt)
        for p in list(self.projectiles):
            if p.rect.right < 0 or p.rect.left > level_width:
                p.kill()
                
        self.velocity_y += self.gravity * dt
        
        self.rect.x += self.velocity_x * dt
        self.check_collisions_x(platforms)
        
        was_on_ground = self.on_ground
        self.rect.y += self.velocity_y * dt
        self.check_collisions_y(platforms)
        
        # Landing juice
        if not was_on_ground and self.on_ground:
            self._spawn_dust()
            
        self.check_enemy_collisions(enemies)
        self.check_item_collisions(items)
        
        if self.rect.bottom > level_height + 100: # Fall off world (relative to level height)
            self.lives -= 1
            self.health = 100
            # Reset to start position
            self.rect.midbottom = (self.start_x + 20, self.start_y + 40)
            self.velocity_y = 0
            
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > level_width: self.rect.right = level_width
        
        self._animate(dt)

    def _animate(self, dt):
        # State machine for animation
        if self.shoot_cooldown > 0.3: # Attacking
            self.state = "attack"
        elif not self.on_ground:
            self.state = "jump"
        elif abs(self.velocity_x) > 0:
            self.state = "walk"
        else:
            self.state = "idle"
            
        frames = self.animation_frames.get(self.state, self.animation_frames["idle"])
        if frames:
            self.animation_timer += dt
            speed = 0.1 # seconds per frame
            self.current_frame = int(self.animation_timer / speed) % len(frames)
            self.image = frames[self.current_frame]

    def _spawn_dust(self):
        for _ in range(5):
            self.particles.append({
                'x': self.rect.centerx,
                'y': self.rect.bottom,
                'vx': (random.random() - 0.5) * 100,
                'vy': -random.random() * 50,
                'life': 0.3,
                'color': (200, 200, 200)
            })

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        self.velocity_x = 0
        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
            self.facing_direction = -1
        if keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed
            self.facing_direction = 1
            
    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False
            self._spawn_dust()

    def shoot(self):
        if self.shoot_cooldown <= 0:
            proj = Projectile(self.rect.centerx, self.rect.centery, self.facing_direction)
            self.projectiles.add(proj)
            self.shoot_cooldown = 0.5 # half second cooldown

    def check_collisions_x(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right
                self.velocity_x = 0

    def check_collisions_y(self, platforms):
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0: # Falling
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.velocity_y = 0
                elif self.velocity_y < 0: # Jumping up and hitting ceiling
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

    def check_enemy_collisions(self, enemies):
        # Projectile hits enemy
        for proj in self.projectiles:
            hit_list = pygame.sprite.spritecollide(proj, enemies, False)
            if hit_list:
                proj.kill()
                for e in hit_list:
                    if hasattr(e, 'health'):
                        e.health -= 1
                        if e.health <= 0:
                            e.kill()
                            self.score += 500
                    else:
                        e.kill()
                        self.score += 50
                
        # Player body hits enemy
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                # Check if jumping on head
                if self.velocity_y > 0 and self.rect.bottom <= enemy.rect.top + 20:
                    if hasattr(enemy, 'health'):
                        enemy.health -= 1
                        if enemy.health <= 0:
                            enemy.kill()
                            self.score += 1000
                    else:
                        enemy.kill()
                        self.score += 100
                    self.velocity_y = self.jump_power * 0.7 # Bounce
                else:
                    # Player takes damage
                    self.health -= 10
                    self.rect.x = self.start_x
                    self.rect.y = self.start_y
                    if self.health <= 0:
                        self.lives -= 1
                        self.health = 100
                        if self.lives < 0:
                            # Game Over logic to be handled in state
                            pass

    def check_goal_collision(self, goals):
        for goal in goals:
            if self.rect.colliderect(goal.rect):
                return True
        return False

    def check_item_collisions(self, items):
        hit_list = pygame.sprite.spritecollide(self, items, True)
        for item in hit_list:
            if item.item_type == "health":
                self.health = min(100, self.health + 50)
            else:
                self.inventory.append(item.item_type)
                self.score += 200

    def draw(self, surface, camera_x):
        # Zelda-style dynamic effects
        current_image = self.base_image
        
        # Flip direction
        if self.facing_direction == -1:
            current_image = pygame.transform.flip(current_image, True, False)
            
        # Apply programmatic squash/stretch and tilt
        w, h = current_image.get_size()
        current_image = pygame.transform.scale(current_image, (int(w * self.scale_x), int(h * self.scale_y)))
        if self.tilt_angle != 0:
            current_image = pygame.transform.rotate(current_image, self.tilt_angle)
            
        # Draw shadow
        shadow_rect = pygame.Rect(0, 0, 32, 8)
        shadow_rect.centerx = self.rect.centerx - camera_x
        shadow_rect.bottom = self.rect.bottom + 2
        pygame.draw.ellipse(surface, (0, 0, 0, 100), shadow_rect)
        
        # Draw with offset including bobbing
        rect = current_image.get_rect(midbottom=(self.rect.centerx - camera_x, self.rect.bottom + self.bob_y))
        surface.blit(current_image, rect)
        
        # Draw particles
        for p in self.particles:
            pygame.draw.rect(surface, p['color'], (p['x'] - camera_x, p['y'], 4, 4))
            
        for proj in self.projectiles:
            surface.blit(proj.image, (proj.rect.x - camera_x, proj.rect.y))
