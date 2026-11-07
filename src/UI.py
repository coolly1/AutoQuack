import pygame
import pygame_gui

class ui():
    clock = pygame.time.Clock()
    
    def __init__(self):
        pygame.init()
        
        pygame.display.set_caption('Quick Start')
        self.window_surface = pygame.display.set_mode((800, 600))
    
        self.background = pygame.Surface((800, 600))
        self.background.fill(pygame.Color('#000000'))
    
    def main_menu(self):
        manager = pygame_gui.UIManager((800, 600))
        start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                                     text='Start Game',
                                                     manager=manager)
        is_running = True
        
        while is_running:
                time_delta = self.clock.tick(60)/1000.0
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        is_running = False
                    if event.type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == start_button:
                            return;
        
                    manager.process_events(event)
        
                manager.update(time_delta)
        
                self.window_surface.blit(self.background, (0, 0))
                manager.draw_ui(self.window_surface)
                
                pygame.display.update()