import os
import pygame
import pygame_gui
from Units import COLOR, UNIT, TARGET, SPECIAL
from dataclasses import dataclass

class ui():
    clock = pygame.time.Clock()
    colorPaths = {
        COLOR.YELLOW: "..\\sprites\\ducks\\skins\\yellow_duck.png",
        #COLOR.MALLARD: "..\\sprites\\ducks\\skins\\mallard_duck.png",
        #COLOR.COMS: "..\\sprites\\ducks\\skins\\coms_duck.png"
    }
    
    colorImages = {}
    
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
    
    def show_training(self):
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
            self.draw_duck(UNIT(0, 0, 0, 0, 0, 0, 0, 0, "", TARGET.SELF, SPECIAL.NONE), 50, 400)
            manager.draw_ui(self.window_surface)
            
            pygame.display.update()
                
    def minigame_1(self, unit: int):
        manager = pygame_gui.UIManager((800, 600))

        time_bar = progress_bar(bbox=(100, 180, 400, 30), inner_color=(100,100,100), inner_offset=2, outer_color=(0,0,0), screen=self.window_surface)
        completion_bar = progress_bar(bbox=(600, 180, 400, 30), inner_color=(100,100,100), inner_offset=2, outer_color=(0,0,0), screen=self.window_surface)

        flaps_needed = 4
        is_up_last_pressed = False
        cur_flaps = 0
        # start_time =

        while self.is_running:
            time_second = self.clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    pass
                manager.process_events(event)

            keys = pygame.key.get_just_pressed()

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                is_up_last_pressed = True

            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if(is_up_last_pressed):
                    is_up_last_pressed = False
                    cur_flaps += 1



            manager.update(time_second)

            self.window_surface.blit(self.background, (0, 0))
            manager.draw_ui(self.window_surface)

            pygame.display.update()

    def draw_duck(self, unit:UNIT, x:int, y:int):
        self.window_surface.blit(self.colorImages[unit.color], (x, y))
        pass
    
    def show_battle(self, active_unit, affected_units, is_special):
        pass


@dataclass
class progress_bar():
    bbox: tuple[int, int, int, int]
    inner_offset: int
    inner_color: tuple[int, int, int]
    outer_color: tuple[int, int, int]
    screen: pygame.display

    def draw(self, percent):

        current_bar_width = int((self.bbox[2] - 2*self.inner_offset) * percent)

        # Draw outer border
        border_rect = pygame.Rect(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3])
        pygame.draw.rect(self.screen, self.outer_color, border_rect, 2)

        # Draw active time bar
        if current_bar_width > 0:
            inner_rect = pygame.Rect(self.bbox[0]+self.inner_offset, self.bbox[1]+self.inner_offset, current_bar_width, (self.bbox[2] - 2*self.inner_offset))
            pygame.draw.rect(self.screen, self.inner_color, inner_rect)


@dataclass
class SpriteGrid:
    bbox: tuple[int, int, int, int]
    inner_offset: int
    inner_color: tuple[int, int, int]
    outer_color: tuple[int, int, int]
    screen: pygame.display

    sprite_size: int = 64
    columns: int = 6

    def draw(self, sequence_array,image_dict):
        container_rect = pygame.Rect(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3])
        pygame.draw.rect(self.screen, self.inner_color, container_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.outer_color, container_rect, width=3, border_radius=8)

        for index, color_key in enumerate(sequence_array):
            row = index // self.columns
            col = index % self.columns

            x = self.bbox[0] + self.inner_offset + col * (self.sprite_size + self.inner_offset)
            y = self.bbox[1] + self.inner_offset + row * (self.sprite_size + self.inner_offset)

            sprite_surface = image_dict[color_key]
            self.screen.blit(sprite_surface, (x, y))