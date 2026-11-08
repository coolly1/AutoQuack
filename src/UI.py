import os
import pygame
import pygame_gui
from Units import COLOR, UNIT, TARGET, SPECIAL

class ui():
    clock = pygame.time.Clock()
    colorPaths = {
        COLOR.YELLOW: "..\\sprites\\ducks\\skins\\yellow_duck.png",
        #COLOR.MALLARD: "..\\sprites\\ducks\\skins\\mallard_duck.png",
        #COLOR.COMS: "..\\sprites\\ducks\\skins\\coms_duck.png"
    }
    
    colorImages = {}
    flippedColorImages = {}
    
    def __init__(self):
        pygame.init()
        
        pygame.display.set_caption('Quick Start')
        self.window_surface = pygame.display.set_mode((800, 600))
    
        self.background = pygame.Surface((800, 600))
        self.background.fill(pygame.Color('#000000'))
        
        self.is_running = True
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        for color, path in self.colorPaths.items():
            full_path = os.path.join(BASE_DIR, path)
            full_path = os.path.abspath(full_path)
            self.colorImages[color] = pygame.image.load(full_path).convert_alpha()
            self.flippedColorImages[color] = pygame.transform.flip(self.colorImages[color], True, False)
        
    
    def main_menu(self):
        manager = pygame_gui.UIManager((800, 600))
        start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                                     text='Start Game',
                                                     manager=manager)
        
        while self.is_running:
            time_delta = self.clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_button:
                        return;
    
                manager.process_events(event)
    
            manager.update(time_delta)
    
            self.window_surface.blit(self.background, (0, 0))
            manager.draw_ui(self.window_surface)
            
            pygame.display.update()
    
    def show_training(self, player):
        manager = pygame_gui.UIManager((800, 600))
        train_button_1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 50), (150, 75)),
                                                     text='Train Health',
                                                     manager=manager)
        
        train_button_2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, 50), (150, 75)),
                                                     text='Train Attack',
                                                     manager=manager)
        
        train_button_3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 150), (150, 75)),
                                                     text='Train Speed',
                                                     manager=manager)
        
        train_button_4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, 150), (150, 75)),
                                                     text='Train Ability',
                                                     manager=manager)
        
        fight_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((600, 275), (150, 50)),
                                                     text='FIGHT!',
                                                     manager=manager)
        
        duck_buttons = []
        
        for i in range(4):
            duck_buttons.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50 + (i * 100), 400), (80, 80)),
                                                     text='Duck ' + str(i + 1),
                                                     manager=manager))
        
        unit = -1
        
        while self.is_running:
            time_delta = self.clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == train_button_1:
                        return 1, unit
                    if event.ui_element == train_button_2:
                        return 2, unit
                    if event.ui_element == train_button_3:
                        return 3, unit
                    if event.ui_element == train_button_4:
                        return 4, unit
                    if event.ui_element == fight_button:
                        return 0, -1
                    for i in range(4):
                        if event.ui_element == duck_buttons[i]:
                            if(unit > -1):
                                pass
                            unit = i
    
                manager.process_events(event)
    
            manager.update(time_delta)

            self.window_surface.blit(self.background, (0, 0))
            self.draw_duck(player[unit], 50, 400, 1/3, True)
            manager.draw_ui(self.window_surface)
            
            pygame.display.update()
                
    def minigame_1(self, unit: int):
        manager = pygame_gui.UIManager((800, 600))
        
        while self.is_running:
            time_delta = self.clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    pass
    
                manager.process_events(event)
    
            manager.update(time_delta)
    
            self.window_surface.blit(self.background, (0, 0))
            manager.draw_ui(self.window_surface)
            
            pygame.display.update()
    
    def draw_duck(self, unit:UNIT, x:int, y:int, scale:float, flipped:bool = False):
        if flipped:
            self.window_surface.blit(self.colorImages[unit.color], (x, y), pygame.Rect(0, 0, self.colorImages[unit.color].get_width() * scale, self.colorImages[unit.color].get_height() * scale))
        else:
            self.window_surface.blit(self.flippedColorImages[unit.color], (x, y), pygame.Rect(0, 0, self.flippedColorImages[unit.color].get_width() * scale, self.flippedColorImages[unit.color].get_height() * scale))
        pass
    
    def show_battle(self, active_unit, affected_units, is_special):
        pass
    