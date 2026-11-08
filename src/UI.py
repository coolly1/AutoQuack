import os
from zoneinfo import available_timezones

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from Units import COLOR, UNIT, TARGET, SPECIAL
from dataclasses import dataclass
from pygame.math import Vector2
from accessories import (get_accessories, animation_for, special_animation_for, AttackContext, Pose,
                         DUCK_DISPLAY_SIZE, DUCK_SCALE, TRAINING_DUCK_SCALE)

class ui():
    clock = pygame.time.Clock()
    colorPaths = {
        COLOR.YELLOW: "..\\sprites\\ducks\\skins\\yellow_duck.png",
        COLOR.MALLARD: "..\\sprites\\ducks\\skins\\mallard_duck.png",
        COLOR.COMS: "..\\sprites\\ducks\\skins\\coms_duck.png",
        COLOR.BROWN: "..\\sprites\\ducks\\skins\\brown_duck.png"
    }
    
    flippedColorImages2 = {}
    colorImages3 = {}
    flippedColorImages3 = {}
    
    player: list[UNIT]
    
    def __init__(self, player: list[UNIT]):
        pygame.init()
        
        self.player = player
        
        pygame.display.set_caption('Quick Start')
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        self.THEME_PATH = os.path.join(BASE_DIR, "../data/UI_Theme.json")
        self.THEME_PATH = os.path.abspath(self.THEME_PATH)
        
        self.window_surface = pygame.display.set_mode((800, 600))
    
        self.background = pygame.Surface((800, 600))
        self.background.fill(pygame.Color('#000000'))
        self.rewards = rewards_panel(bbox=(200,100,400,400), color=(255,255,255), screen=self.window_surface)
        self.is_running = True
        
        
        for color, path in self.colorPaths.items():
            full_path = os.path.join(BASE_DIR, path)
            full_path = os.path.abspath(full_path)
            self.colorImages3[color] = pygame.image.load(full_path).convert_alpha()
            self.flippedColorImages2[color] = pygame.transform.flip(self.colorImages3[color], True, False)
            self.flippedColorImages2[color] = pygame.transform.scale(self.flippedColorImages2[color], (self.flippedColorImages2[color].get_width() / 2, self.flippedColorImages2[color].get_height() / 2))
            self.colorImages3[color] = pygame.transform.scale(self.colorImages3[color], (self.colorImages3[color].get_width() / 3, self.colorImages3[color].get_height() / 3))
            self.flippedColorImages3[color] = pygame.transform.flip(self.colorImages3[color], True, False)
        
    
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
        manager = pygame_gui.UIManager((800, 600), theme_path=self.THEME_PATH)
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
            duck_buttons.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((45 + (i * 150), 395), (110, 110)),
                                                     text='',
                                                     manager=manager,
                                                     object_id=ObjectID(class_id="@transparent_btn")))
        
        unit = -1
        highlighted_unit = -1

        while self.is_running:
            time_delta = self.clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if unit >= 0:
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
                                if(unit == i):
                                    unit = -1
                                else:
                                    duck = self.player[i]
                                    self.player[i] = self.player[unit]
                                    self.player[unit] = duck
                                    unit = -1
                            else:
                                unit = i
    
                manager.process_events(event)

            # outline the selected duck; only re-theme the buttons when the selection actually changes
            if unit != highlighted_unit:
                for i in range(4):
                    if i == unit:
                        duck_buttons[i].change_object_id(ObjectID(class_id="@transparent_border_btn", object_id="#selected"))
                    else:
                        duck_buttons[i].change_object_id(ObjectID(class_id="@transparent_btn"))
                highlighted_unit = unit
            manager.update(time_delta)

            self.window_surface.blit(self.background, (0, 0))
            for i in range(4):
                self.draw_duck2(self.player[i], 50 + 150 * i, 400)
            manager.draw_ui(self.window_surface)
            
            pygame.display.update()
                
    def minigame_1(self, unit: int):
        manager = pygame_gui.UIManager((800, 600))
        self.background.fill(pygame.Color('#87CEEB'))
        time_bar = progress_bar(bbox=(105, 90, 189, 34), inner_color=(255,0,0), inner_offset=3, outer_color=(217,217,217), screen=self.window_surface)
        completion_bar = progress_bar(bbox=(505, 90, 189, 34), inner_color=(0,255,0), inner_offset=3, outer_color=(217,217,217), screen=self.window_surface)
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                
        cloud = os.path.join(BASE_DIR, "../sprites/cloud")
        cloud = os.path.abspath(cloud)
        
        cloud_1 = Clouds(image=pygame.transform.scale(pygame.image.load(cloud + "1.png").convert_alpha(), (269, 153)), screen=self.window_surface, x=69, y=200)
        cloud_2 = Clouds(image=pygame.transform.scale(pygame.image.load(cloud + "2.png").convert_alpha(), (179, 146)), screen=self.window_surface, x=491, y=353)
        cloud_3 = Clouds(image=pygame.transform.scale(pygame.image.load(cloud + "3.png").convert_alpha(), (179, 146)), screen=self.window_surface, x=891, y=213)
        cloud_4 = Clouds(image=pygame.transform.scale(pygame.image.load(cloud + "4.png").convert_alpha(), (179, 146)), screen=self.window_surface, x=1100, y=323)

        flaps_needed = 4
        is_up_last_pressed = False
        cur_flaps = 0
        elapsed_time = 0.0
        TIMEOUT = 5.0
        is_minigame_finished = False
        return_button = None
        score = 0.0

        while self.is_running:
            time_second = self.clock.tick(60)/1000.0
            elapsed_time += time_second
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if return_button and event.ui_element == return_button:
                        return score
                manager.process_events(event)

            manager.update(time_second)

            if(elapsed_time < TIMEOUT):
                keys = pygame.key.get_just_pressed()

                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    is_up_last_pressed = True

                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    if(is_up_last_pressed):
                        is_up_last_pressed = False
                        cur_flaps += 1
                        if(cur_flaps >= flaps_needed):
                            score += 1
                            elapsed_time = 0
                            cur_flaps = 0
                            flaps_needed *= 1.2

                self.window_surface.blit(self.background, (0, 0))

                # start drawing
                time_bar.draw(max(0.0, (TIMEOUT-elapsed_time)/TIMEOUT))
                completion_bar.draw(max(0.0, (cur_flaps)/flaps_needed))
                cloud_1.draw(score+1)
                cloud_2.draw(score+1)

                # Draw panel
                border_rect = pygame.Rect(343, 76, 93, 93)
                pygame.draw.rect(self.window_surface, (217,217,217), border_rect)

                # calc text
                font = pygame.font.Font(None, 50)
                text_surface = font.render(str(score), True, (0, 0, 0))

                # get the text rectangle
                text_rect = text_surface.get_rect()
                text_rect.center = (343 + 93/2, 76 + 93/2)

                # draw the text
                self.window_surface.blit(text_surface, text_rect)

                self.draw_duck2(self.player[unit], 352, 253)

            elif(not is_minigame_finished):
                return_button = self.rewards.draw_button(manager)
                is_minigame_finished = True
            else:
                self.rewards.draw(score)

            manager.draw_ui(self.window_surface)
            pygame.display.update()

    def minigame_2(self, unit: int):
        manager = pygame_gui.UIManager((800, 600))
        self.background.fill(pygame.Color('#87CEEB'))

        sprite_bar = SpriteGrid(
            bbox=(150, 220, 500, 200),
            inner_offset=12,
            inner_color = (50, 50, 70),
            outer_color= (255, 255, 255),
            screen = self.window_surface,
            sprite_size= 48,
            columns=5
        )

        elapsed_time = 0.0
        MEMORIZE_TIME = 5.0 #Time to memorize the sequence
        PLAY_TIME = 10.0 #Time to input sequence
        total_time_limit = MEMORIZE_TIME + PLAY_TIME

        is_minigame_finished = False
        return_button = None
        score = 0.0


        target_sequence = [0, 0, 0]

        current_step = 0

        while self.is_running:
            time_second = self.clock.tick(60) / 1000.0
            elapsed_time += time_second
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if return_button and event.ui_element == return_button:
                        return score

                if total_time_limit >= elapsed_time > MEMORIZE_TIME and not is_minigame_finished:
                    if event.type == pygame.KEYDOWN:
                        try:
                            #Change keypress into index space
                            pressed_index = available_keys.index(event.key)
                            #Comparing index spaces
                            if pressed_index == target_sequence[current_step]:
                                current_step += 1

                                #YOU DID IT
                                if current_step == len(target_sequence):
                                    score = 100
                                    is_minigame_finished = True
                            else:
                                #Fail
                                score = 0.0
                                is_minigame_finished = True

                        except ValueError:
                            #Here to ignore keys that dont pertain to video game
                            pass


                manager.process_events(event)

            manager.update(time_second)

            time_expired = (elapsed_time > total_time_limit and not is_minigame_finished)

            if time_expired:
                score = 0.0
                return_button = self.rewards.draw_button(manager)
                is_minigame_finished = True

            elif (not is_minigame_finished):
                pass

            else:
                if not return_button:
                    return_button = self.rewards.draw_button(manager)
                self.rewards.draw(score)

            manager.draw_ui(self.window_surface)
            pygame.display.update()


    def draw_duck2(self, unit:UNIT, x:int, y:int):
        """Training-scene duck (half size, faces right) with its hat and weapon at rest."""
        self.window_surface.blit(self.flippedColorImages2[unit.color], (x, y))
        self._draw_accessories(unit, x, y, mirrored=False, scale=TRAINING_DUCK_SCALE)

    def _draw_accessories(self, unit:UNIT, x:int, y:int, mirrored:bool, pose: Pose = None, scale: float = DUCK_SCALE):
        acc = get_accessories(unit.path)
        if acc is None:
            return
        if pose is None or pose.weapon_visible:
            delta = pose.angle if pose else 0
            acc.draw_weapon(self.window_surface, (x, y), mirrored, acc.rest_angle + delta, scale)
        acc.draw_hat(self.window_surface, (x, y), mirrored, scale)

    def draw_duck(self, unit:UNIT, x:int, y:int, flipped:bool = False, pose: Pose = None):
        """flipped=True means the duck faces right (player side).
        pose=None draws the accessories at rest; pass a Pose to animate the weapon."""
        if not flipped:
            self.window_surface.blit(self.colorImages3[unit.color], (x, y))
        else:
            self.window_surface.blit(self.flippedColorImages3[unit.color], (x, y))

        self._draw_accessories(unit, x, y, mirrored=not flipped, pose=pose)  # accessories are authored right-facing

    @staticmethod
    def _slot_pos(idx: int) -> Vector2:
        """Top-left of the duck in slot idx (0-3 player, 4-7 enemy)."""
        return Vector2(50 + 75 * idx, 400) if idx < 4 else Vector2(450 + 75 * (idx - 4), 400)

    def show_battle(self, active_unit, affected_units, is_special, enemy_team):
        units = list(self.player) + list(enemy_team)
        facing = 1 if active_unit < 4 else -1
        active = units[active_unit]

        acc = get_accessories(active.path)
        anim = special_animation_for(acc) if is_special else animation_for(acc)
        if anim is None:
            return  # TODO: specials without their own animation yet are skipped

        manager = pygame_gui.UIManager((800, 600), theme_path=self.THEME_PATH)
        duration = anim.duration
        ctx = None
        if acc is not None:
            targets = [self._slot_pos(i) + DUCK_DISPLAY_SIZE / 2
                       for i, u in enumerate(units)
                       if (i != active_unit or anim.targets_include_self) and any(u is a for a in affected_units)]
            ctx = AttackContext(acc, anim, self._slot_pos(active_unit), facing, targets)

        elapsed = 0.0
        anim_finished = False

        while self.is_running and not anim_finished:
            time_delta = self.clock.tick(60)/1000.0
            elapsed += time_delta
            progress = min(elapsed / duration, 1.0)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    pass

                manager.process_events(event)

            manager.update(time_delta)

            self.window_surface.blit(self.background, (0, 0))
            pose = anim.pose(progress)
            if ctx is not None:
                anim.draw_under(self.window_surface, progress, ctx)
            # draw the attacker last so it (and its lunge) is on top
            for i in [i for i in range(8) if i != active_unit] + [active_unit]:
                pos = self._slot_pos(i)
                if i == active_unit:
                    self.draw_duck(units[i], pos.x + pose.dx * facing, pos.y, i < 4, pose)
                else:
                    if not units[i].is_dead():
                        self.draw_duck(units[i], pos.x, pos.y, i < 4)
            if ctx is not None:
                anim.draw_effects(self.window_surface, progress, ctx)
            manager.draw_ui(self.window_surface)

            pygame.display.update()
            anim_finished = progress >= 1.0


@dataclass
class progress_bar():
    bbox: tuple[int, int, int, int]
    inner_offset: int
    inner_color: tuple[int, int, int]
    outer_color: tuple[int, int, int]
    screen: pygame.Surface

    def draw(self, percent):

        current_bar_width = int((self.bbox[2] - 2*self.inner_offset) * percent)

        # Draw outer border
        border_rect = pygame.Rect(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3])
        pygame.draw.rect(self.screen, self.outer_color, border_rect, 2)

        # Draw active time bar
        if current_bar_width > 0:
            inner_rect = pygame.Rect(self.bbox[0]+self.inner_offset, self.bbox[1]+self.inner_offset, current_bar_width, (self.bbox[3] - 2*self.inner_offset))
            pygame.draw.rect(self.screen, self.inner_color, inner_rect)

@dataclass
class rewards_panel():
    bbox: tuple[int, int, int, int]
    color: tuple[int, int, int]
    screen: pygame.Surface

    def draw(self, score):

        # Draw panel
        border_rect = pygame.Rect(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3])
        pygame.draw.rect(self.screen, self.color, border_rect)

        # calc text
        font = pygame.font.Font(None, 50)
        text_surface = font.render(str(score), True, (0,0,0))

        # get the text rectangle
        text_rect = text_surface.get_rect()
        text_rect.center = (self.bbox[0] + self.bbox[2]/2, self.bbox[1] + self.bbox[3]/2)

        # draw the text
        self.screen.blit(text_surface, text_rect)

    def draw_button(self, manager):
        return pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.bbox[0] + self.bbox[2]/2 - 50,
                                                                       self.bbox[1] + self.bbox[3]/2 + 100),
                                                                      (100, 50)),
                                                    text='Return!',
                                                    manager=manager)




@dataclass
class SpriteGrid:
    bbox: tuple[int, int, int, int]
    inner_offset: int
    inner_color: tuple[int, int, int]
    outer_color: tuple[int, int, int]
    screen: pygame.surface

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

@dataclass
class Clouds:
    screen: pygame.display
    image: pygame.image
    x: int
    y: int

    def draw(self, movement):

        self.x -= movement
        if(self.x < -200):
            self.x = 1000

        image_rect = self.image.get_rect()
        image_rect.topleft = (self.x, self.y)
        self.screen.blit(self.image, image_rect)

