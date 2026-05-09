import pygame
import math
import os
import random
from constants import *
from player import Player
from level import Level

class State:
    def __init__(self, game):
        self.game = game
        self.next_state = None

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def render(self, surface):
        pass

class MainMenu(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.next_state = STATE_CHARACTER_SELECT
                elif event.key == pygame.K_l:
                    if self.game.load_game():
                        self.next_state = STATE_LEVEL_MAP
                elif event.key == pygame.K_e:
                    self.next_state = STATE_LEVEL_EDITOR

    def render(self, surface):
        # Premium Gradient Background
        for y in range(SCREEN_HEIGHT):
            color = (max(0, 10 - y // 60), max(0, 20 - y // 30), max(0, 40 - y // 15))
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
            
        title = self.font.render("MYTHIC ADVENTURE", True, WHITE)
        prompt = self.small_font.render("Press ENTER to Start | L to Load | E for Editor", True, GRAY)
        
        # Subtle floating effect for title
        offset_y = math.sin(pygame.time.get_ticks() * 0.002) * 10
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200 + offset_y))
        surface.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 400))

class CharacterSelect(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.characters = ["Warrior", "Mage", "Rogue", "Baby"]
        self.selected_index = 0
        self.char_images = {}
        self.load_images()

    def load_images(self):
        for char in self.characters:
            try:
                img = pygame.image.load(f"assets/characters/{char.lower()}.png").convert_alpha()
                img = pygame.transform.scale(img, (128, 128))
                self.char_images[char] = img
            except:
                img = pygame.Surface((128, 128))
                img.fill(GREEN)
                self.char_images[char] = img

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.selected_index = (self.selected_index + 1) % len(self.characters)
                elif event.key == pygame.K_LEFT:
                    self.selected_index = (self.selected_index - 1) % len(self.characters)
                elif event.key == pygame.K_RETURN:
                    self.game.player_data["character"] = self.characters[self.selected_index]
                    self.next_state = STATE_LEVEL_MAP

    def render(self, surface):
        # Background
        for y in range(SCREEN_HEIGHT):
            color = (max(0, 30 - y // 20), max(0, 10 - y // 40), max(0, 50 - y // 10))
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
            
        title = self.font.render("Choose Your Hero", True, WHITE)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        char_name = self.characters[self.selected_index]
        char_text = self.font.render(char_name, True, GREEN)
        
        # Draw Character Image with animation
        img = self.char_images.get(char_name)
        if img:
            # Zelda-style breathing/bobbing
            bob = math.sin(pygame.time.get_ticks() * 0.005) * 5
            scale = 1.0 + math.sin(pygame.time.get_ticks() * 0.005) * 0.05
            scaled_img = pygame.transform.scale(img, (int(128 * scale), int(128 * scale)))
            rect = scaled_img.get_rect(center=(SCREEN_WIDTH//2, 300 + bob))
            surface.blit(scaled_img, rect)
            
        surface.blit(char_text, (SCREEN_WIDTH//2 - char_text.get_width()//2, 450))
        
        prompt = self.small_font.render("Press ENTER to Confirm", True, GRAY)
        surface.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 530))

class LevelMap(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.max_levels = 20
        self.camera_x = 0
        self.target_camera_x = 0
        self.preview_surface = None
        self.last_previewed_level = None

    def handle_events(self, events):
        unlocked = self.game.player_data["unlocked_levels"]
        current = self.game.player_data["current_level"]
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Check if level is unlocked
                    if isinstance(current, str) or current <= unlocked:
                        self.next_state = STATE_GAMEPLAY
                elif event.key == pygame.K_ESCAPE:
                    self.next_state = STATE_MAIN_MENU
                elif event.key == pygame.K_RIGHT:
                    if isinstance(current, int) and current < self.max_levels:
                        self.game.player_data["current_level"] += 1
                elif event.key == pygame.K_LEFT:
                    if isinstance(current, int) and current > 1:
                        self.game.player_data["current_level"] -= 1
                elif event.key == pygame.K_c:
                    self.next_state = STATE_CUSTOM_CATALOG
                elif event.key == pygame.K_UP:
                    if isinstance(current, str):
                        self.game.player_data["current_level"] = unlocked

        # Update target camera
        current = self.game.player_data["current_level"]
        if isinstance(current, int):
            node_x = 200 + (current - 1) * 200
            self.target_camera_x = node_x - SCREEN_WIDTH // 2

    def update(self, dt):
        lerp_speed = 8.0
        self.camera_x += (self.target_camera_x - self.camera_x) * lerp_speed * dt

    def _generate_preview(self, level_id):
        preview_width = 300
        preview_height = 150
        surf = pygame.Surface((preview_width, preview_height))
        surf.fill((20, 20, 20))
        
        filepath = f"assets/levels/level{level_id}.txt" if isinstance(level_id, int) else f"assets/levels/{level_id}"
        
        try:
            if not os.path.exists(filepath): return surf
            with open(filepath, 'r') as f:
                layout = [line.strip('\n') for line in f.readlines()]
            
            if not layout: return surf
            rows = len(layout)
            cols = max(len(row) for row in layout)
            tile_size = min(preview_width / cols, preview_height / rows)
            
            offset_x = (preview_width - cols * tile_size) / 2
            offset_y = (preview_height - rows * tile_size) / 2
            
            for r, row in enumerate(layout):
                for c, char in enumerate(row):
                    if char == ' ': continue
                    rect = pygame.Rect(offset_x + c * tile_size, offset_y + r * tile_size, tile_size, tile_size)
                    color = GRAY
                    if char == 'P': color = (120, 120, 120)
                    elif char in ['E', 'T', 'N', 'D']: color = RED
                    elif char == 'G': color = (255, 215, 0)
                    elif char == 'S': color = BLUE
                    elif char == 'B': color = (139, 0, 0)
                    elif char == '+': color = GREEN
                    elif char == 'W': color = (0, 255, 255)
                    pygame.draw.rect(surf, color, rect)
        except:
            pass
        return surf

    def render(self, surface):
        # 1. Background Gradient
        for y in range(SCREEN_HEIGHT):
            color = (max(0, 20 - y // 20), max(0, 30 - y // 15), max(0, 60 - y // 10))
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

        title = self.font.render("World Exploration", True, WHITE)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        current = self.game.player_data["current_level"]
        unlocked = self.game.player_data["unlocked_levels"]
        
        # 2. Connection Lines
        line_y = 250
        for i in range(1, self.max_levels):
            x1 = 200 + (i - 1) * 200 - self.camera_x
            x2 = 200 + i * 200 - self.camera_x
            color = GREEN if i < unlocked else (40, 40, 40)
            pygame.draw.line(surface, color, (int(x1), line_y), (int(x2), line_y), 4)

        # 3. Nodes
        for i in range(1, self.max_levels + 1):
            x = 200 + (i - 1) * 200 - self.camera_x
            y = line_y
            
            is_current = (i == current)
            is_unlocked = (i <= unlocked)
            
            color = GREEN if is_unlocked else (100, 50, 50)
            
            if is_current:
                glow = 35 + math.sin(pygame.time.get_ticks() * 0.01) * 5
                pygame.draw.circle(surface, (255, 255, 255, 100), (int(x), y), int(glow), 2)
                pygame.draw.circle(surface, WHITE, (int(x), y), 32, 3)
            
            pygame.draw.circle(surface, color, (int(x), y), 25)
            num_text = self.small_font.render(str(i), True, WHITE if is_unlocked else GRAY)
            surface.blit(num_text, (int(x) - num_text.get_width()//2, y - num_text.get_height()//2))

        # 4. Preview Card
        preview_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, 350, 400, 220)
        overlay = pygame.Surface((preview_rect.width, preview_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (255, 255, 255, 40), overlay.get_rect(), border_radius=15)
        surface.blit(overlay, preview_rect.topleft)
        pygame.draw.rect(surface, (255, 255, 255, 100), preview_rect, 2, border_radius=15)
        
        if self.last_previewed_level != current:
            self.preview_surface = self._generate_preview(current)
            self.last_previewed_level = current
            
        if self.preview_surface:
            surface.blit(self.preview_surface, (preview_rect.centerx - 150, preview_rect.y + 50))
            
        lvl_label = f"LEVEL {current}" if isinstance(current, int) else str(current).upper()
        name_text = self.small_font.render(lvl_label, True, GREEN if (isinstance(current, int) and current <= unlocked) or isinstance(current, str) else RED)
        surface.blit(name_text, (preview_rect.centerx - name_text.get_width()//2, preview_rect.y + 15))
        
        prompt_text = "Press ENTER to Start" if (isinstance(current, int) and current <= unlocked) or isinstance(current, str) else "LEVEL LOCKED"
        prompt = self.small_font.render(prompt_text, True, WHITE if prompt_text != "LEVEL LOCKED" else RED)
        surface.blit(prompt, (preview_rect.centerx - prompt.get_width()//2, preview_rect.bottom - 30))

class Gameplay(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 30)
        self.level = None
        self.player = None
        self.camera_x = 0
        self.bg_elements = []
        self._init_background()

    def _init_background(self):
        # Create some random clouds/mountains for parallax
        for _ in range(15):
            self.bg_elements.append({
                'x': random.randint(0, 5000),
                'y': random.randint(50, 200),
                'speed': random.uniform(0.2, 0.5),
                'size': (random.randint(100, 200), random.randint(40, 80)),
                'color': (255, 255, 255, 100)
            })

    def enter(self):
        lvl = self.game.player_data["current_level"]
        if isinstance(lvl, str) and lvl.startswith("custom"):
            self.level = Level(f"assets/levels/{lvl}", level_num=1)
        else:
            self.level = Level(f"assets/levels/level{lvl}.txt", level_num=lvl)
        char_type = self.game.player_data.get("character") or "Warrior"
        self.player = Player(self.level.start_x, self.level.start_y, char_type)
        self.player.lives = self.game.player_data["lives"]
        self.player.score = self.game.player_data["score"]
        self.player.inventory = self.game.player_data.get("inventory", [])
        self.player.health = self.game.player_data.get("health", 100)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.player_data["lives"] = self.player.lives
                    self.game.player_data["score"] = self.player.score
                    self.game.save_game()
                    self.next_state = STATE_LEVEL_MAP
                elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    self.player.jump()
                elif event.key == pygame.K_w or event.key == pygame.K_x:
                    self.player.shoot()
                elif event.key == pygame.K_i:
                    self.game.player_data["lives"] = self.player.lives
                    self.game.player_data["score"] = self.player.score
                    self.game.player_data["health"] = self.player.health
                    self.game.player_data["inventory"] = self.player.inventory
                    self.next_state = STATE_INVENTORY

    def update(self, dt):
        self.level.update(dt)
        self.player.update(dt, self.level.platforms, self.level.enemies, self.level.items, self.level.width, self.level.height)
        self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_x = max(0, min(self.camera_x, self.level.width - SCREEN_WIDTH))
        
        if self.player.check_goal_collision(self.level.goals):
            self.player.score += 1000
            if self.game.player_data["current_level"] == self.game.player_data["unlocked_levels"]:
                self.game.player_data["unlocked_levels"] += 1
            self.game.player_data["lives"] = self.player.lives
            self.game.player_data["score"] = self.player.score
            self.game.save_game()
            self.next_state = STATE_LEVEL_MAP

        if self.player.lives < 0:
            self.next_state = STATE_MAIN_MENU

    def render(self, surface):
        # Sky Gradient
        for y in range(SCREEN_HEIGHT):
            color = (135, 206, max(0, 255 - y // 4))
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
            
        # Parallax Background Elements
        for bg in self.bg_elements:
            # Offset by camera * speed for parallax effect
            draw_x = (bg['x'] - self.camera_x * bg['speed']) % 1200 - 200
            pygame.draw.ellipse(surface, (255, 255, 255, 150), (draw_x, bg['y'], bg['size'][0], bg['size'][1]))

        self.level.draw(surface, self.camera_x)
        self.player.draw(surface, self.camera_x)
        
        # HUD Overlay (Glassmorphism)
        hud_surf = pygame.Surface((250, 80), pygame.SRCALPHA)
        pygame.draw.rect(hud_surf, (0, 0, 0, 100), hud_surf.get_rect(), border_radius=10)
        surface.blit(hud_surf, (10, 10))
        
        score_text = self.font.render(f"SCORE: {self.player.score}", True, WHITE)
        lives_text = self.font.render(f"LIVES: {self.player.lives}", True, WHITE)
        health_text = self.font.render(f"HP: {self.player.health}", True, (255, 100, 100))
        
        surface.blit(score_text, (25, 20))
        surface.blit(lives_text, (25, 40))
        surface.blit(health_text, (25, 60))

class InventoryScreen(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 36)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                    self.next_state = STATE_GAMEPLAY

    def render(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        title = self.font.render("Inventory", True, WHITE)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        inventory = self.game.player_data.get("inventory", [])
        if not inventory:
            empty_text = self.small_font.render("Inventory is empty", True, GRAY)
            surface.blit(empty_text, (SCREEN_WIDTH//2 - empty_text.get_width()//2, 200))
        else:
            y = 200
            for item in inventory:
                item_text = self.small_font.render(f"- {item}", True, GREEN)
                surface.blit(item_text, (SCREEN_WIDTH//2 - 100, y))
                y += 40
        
        prompt = self.small_font.render("Press I to return to game", True, GRAY)
        surface.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT - 100))

class LevelEditor(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 24)
        self.tile_size = 40
        self.camera_x = 0
        self.grid_width = 100
        self.grid_height = 15
        self.grid = [[' ' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.tiles = {
            pygame.K_1: ('P', "Platform", GRAY),
            pygame.K_2: ('E', "Enemy", RED),
            pygame.K_3: ('B', "Boss", (139, 0, 0)),
            pygame.K_4: ('S', "Start", BLUE),
            pygame.K_5: ('G', "Goal", (255, 215, 0)),
            pygame.K_6: ('+', "Health", GREEN),
            pygame.K_7: ('W', "Weapon", (0, 255, 255)),
            pygame.K_8: ('T', "Troll", (0, 100, 0)),
            pygame.K_9: ('N', "Snake", (173, 255, 47)),
            pygame.K_0: ('D', "Dragon", (128, 0, 128))
        }
        self.current_tile = 'P'
        self.save_timer = 0
        self.current_filename = None

    def handle_events(self, events):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]: self.camera_x += 10
        if keys[pygame.K_LEFT]: self.camera_x -= 10
        self.camera_x = max(0, self.camera_x)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.next_state = STATE_MAIN_MENU
                elif event.key == pygame.K_s:
                    self.save_level()
                    self.save_timer = 60
                elif event.key in self.tiles: self.current_tile = self.tiles[event.key][0]
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] or mouse_buttons[2]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_y < SCREEN_HEIGHT - 60:
                grid_x = (mouse_x + self.camera_x) // self.tile_size
                grid_y = mouse_y // self.tile_size
                if 0 <= grid_y < self.grid_height:
                    while grid_x >= len(self.grid[0]):
                        for row in self.grid: row.append(' ')
                    if mouse_buttons[0]: self.grid[grid_y][grid_x] = self.current_tile
                    else: self.grid[grid_y][grid_x] = ' '

    def save_level(self):
        import glob
        if not self.current_filename:
            existing = glob.glob('assets/levels/custom_*.txt')
            nums = [int(f.split('_')[-1].split('.')[0]) for f in existing if f.split('_')[-1].split('.')[0].isdigit()]
            next_num = max(nums) + 1 if nums else 1
            self.current_filename = f'custom_{next_num}.txt'
        filepath = os.path.join('assets/levels', self.current_filename)
        with open(filepath, 'w') as f:
            for row in self.grid: f.write("".join(row) + "\n")

    def render(self, surface):
        surface.fill((50, 50, 50))
        for y, row in enumerate(self.grid):
            for x, char in enumerate(row):
                if char != ' ':
                    color = WHITE
                    for val in self.tiles.values():
                        if val[0] == char: color = val[2]; break
                    pygame.draw.rect(surface, color, (x * self.tile_size - self.camera_x, y * self.tile_size, self.tile_size, self.tile_size))
        pygame.draw.rect(surface, BLACK, (0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60))
        ui_text = " ".join([f"{pygame.key.name(k).upper()}={v[1]}" for k,v in self.tiles.items()])
        text = self.font.render(ui_text, True, WHITE)
        surface.blit(text, (10, SCREEN_HEIGHT - 50))
        info = self.font.render(f"Current: {self.current_tile} | L/R Arrows: Scroll | S: Save | ESC: Menu", True, GREEN)
        surface.blit(info, (10, SCREEN_HEIGHT - 25))
        if self.save_timer > 0:
            saved_text = self.font.render("LEVEL SAVED!", True, (0, 255, 255))
            surface.blit(saved_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40))
            self.save_timer -= 1

class CustomCatalog(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 36)
        self.custom_levels = []
        self.selected_index = 0

    def enter(self):
        self.custom_levels = []
        if os.path.exists('assets/levels'):
            for f in os.listdir('assets/levels'):
                if f.startswith('custom') and f.endswith('.txt'): self.custom_levels.append(f)
        self.custom_levels.sort()
        self.selected_index = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.next_state = STATE_LEVEL_MAP
                elif event.key == pygame.K_DOWN:
                    if self.custom_levels: self.selected_index = (self.selected_index + 1) % len(self.custom_levels)
                elif event.key == pygame.K_UP:
                    if self.custom_levels: self.selected_index = (self.selected_index - 1) % len(self.custom_levels)
                elif event.key == pygame.K_RETURN:
                    if self.custom_levels:
                        self.game.player_data["current_level"] = self.custom_levels[self.selected_index]
                        self.next_state = STATE_GAMEPLAY

    def render(self, surface):
        surface.fill(BLACK)
        title = self.font.render("Custom Worlds Catalog", True, WHITE)
        prompt = self.small_font.render("ENTER: Play | ESC: Back | UP/DOWN: Select", True, GRAY)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        surface.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT - 50))
        if not self.custom_levels:
            empty_text = self.small_font.render("No custom worlds found.", True, RED)
            surface.blit(empty_text, (SCREEN_WIDTH//2 - empty_text.get_width()//2, 200))
        else:
            start_y = 150
            for i, level_file in enumerate(self.custom_levels):
                color = GREEN if i == self.selected_index else WHITE
                text = f"> {level_file} <" if i == self.selected_index else level_file
                level_text = self.small_font.render(text, True, color)
                surface.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, start_y + i * 40))
