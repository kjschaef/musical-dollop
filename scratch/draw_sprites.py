import pygame
import os

pygame.init()
pygame.display.set_mode((1, 1))

base_dir = "assets/characters"
os.makedirs(base_dir, exist_ok=True)

def create_sprite(filename, layout, color_map, scale=1):
    width = len(layout[0])
    height = len(layout)
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y, row in enumerate(layout):
        for x, char in enumerate(row):
            if char in color_map:
                surface.set_at((x, y), color_map[char])
                
    if scale > 1:
        surface = pygame.transform.scale(surface, (width * scale, height * scale))
        
    filepath = os.path.join(base_dir, filename)
    pygame.image.save(surface, filepath)
    print(f"Saved {filepath}")

# Octorok (Enemy) - Red
octorok_layout = [
    "  RRRR  ",
    " RRRRRR ",
    " RRWRRW ",
    " RRRRRR ",
    "R RRRR R",
    "R RRRR R",
    "   RR   ",
    "  RRRR  "
]
octorok_colors = {'R': (200, 50, 50, 255), 'W': (255, 255, 255, 255)}

# Moblin (Troll) - Green
moblin_layout = [
    "  GGGG  ",
    " GGGGGG ",
    " GGWGGW ",
    " GGGGGG ",
    "GGGGGGGG",
    "GG    GG",
    "GG    GG",
    " GG  GG "
]
moblin_colors = {'G': (50, 150, 50, 255), 'W': (255, 255, 255, 255)}

# Snake (Rope) - Yellow/Green
snake_layout = [
    "   YY   ",
    "  YYYY  ",
    " YYYYW  ",
    "YYYYY   ",
    " YYYY   ",
    "  YYYY  ",
    "   YYY  ",
    "  YYY   "
]
snake_colors = {'Y': (150, 200, 50, 255), 'W': (255, 255, 255, 255)}

# Dragon (Aquamentus) - Purple
dragon_layout = [
    "  P     ",
    "  PP    ",
    "  PPW   ",
    " PPP    ",
    "PPPPPPPP",
    " PPPPPP ",
    " PP  PP ",
    " P    P "
]
dragon_colors = {'P': (150, 50, 150, 255), 'W': (255, 255, 255, 255)}

create_sprite("enemy.png", octorok_layout, octorok_colors, scale=4)
create_sprite("troll.png", moblin_layout, moblin_colors, scale=6)
create_sprite("snake.png", snake_layout, snake_colors, scale=4)
create_sprite("dragon.png", dragon_layout, dragon_colors, scale=7)

pygame.quit()
