import pygame
import json
import os
from constants import *
from states import MainMenu, CharacterSelect, LevelMap, Gameplay, InventoryScreen, LevelEditor, CustomCatalog

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Side Scroller")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Shared game data (could be moved to a save state system later)
        self.player_data = {
            "character": None,
            "lives": 3,
            "score": 0,
            "inventory": [],
            "unlocked_levels": 1,
            "current_level": 1
        }
        
        # Initialize states
        self.states = {
            STATE_MAIN_MENU: MainMenu(self),
            STATE_CHARACTER_SELECT: CharacterSelect(self),
            STATE_LEVEL_MAP: LevelMap(self),
            STATE_GAMEPLAY: Gameplay(self),
            STATE_INVENTORY: InventoryScreen(self),
            STATE_LEVEL_EDITOR: LevelEditor(self),
            STATE_CUSTOM_CATALOG: CustomCatalog(self)
        }
        
        self.current_state_name = STATE_MAIN_MENU
        self.current_state = self.states[self.current_state_name]
        self.current_state.enter()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    
            self.current_state.handle_events(events)
            self.current_state.update(dt)
            
            # State transition
            if self.current_state.next_state is not None:
                self.change_state(self.current_state.next_state)
            
            self.current_state.render(self.screen)
            pygame.display.flip()
            
        pygame.quit()

    def change_state(self, next_state_name):
        self.current_state.exit()
        self.current_state.next_state = None # Reset
        self.current_state_name = next_state_name
        self.current_state = self.states[self.current_state_name]
        self.current_state.enter()

    def save_game(self):
        with open('savegame.json', 'w') as f:
            json.dump(self.player_data, f)

    def load_game(self):
        if os.path.exists('savegame.json'):
            with open('savegame.json', 'r') as f:
                self.player_data = json.load(f)
            return True
        return False
