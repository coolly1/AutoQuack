"""
Headless preview of duck accessories and attack animations (no window opens).

Run from anywhere:   python tools/render_preview.py
Output PNGs go to:   tools/preview_out/
  static.png          all four classes at rest (players left, enemies right)
  training.png        the training-scene ducks (draw_duck2, half size)
  <name>_strip.png    one row per animation frame
  special_<name>_strip.png   same, for special attacks

Edit positions.json in sprites/ducks/units/<class>/ and re-run to see the change.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "tools", "preview_out")
os.makedirs(OUT, exist_ok=True)

import pygame

pygame.init()
pygame.display.set_mode((800, 600))

import UI
from Units import UNIT, TARGET, SPECIAL

BG = (90, 140, 90)
PROGRESS_STEPS = [0, 0.3, 0.5, 0.65, 0.8]


def mk(name):
    return UNIT(10, 1, 1, 1, 1, 1, 1, f"AutoQuack/sprites/ducks/units/{name}", TARGET.FRONT, SPECIAL.BILL_BEATDOWN)


player = [mk("knight"), mk("mage"), mk("cleric"), mk("rogue")]
enemy = [mk("rogue"), mk("cleric"), mk("mage"), mk("knight")]
units = player + enemy
g = UI.ui(player)
surf = g.window_surface


def save(img, name):
    pygame.image.save(img, os.path.join(OUT, name))


# static pose of every class on both teams, 2x zoom
surf.fill(BG)
for i in range(4):
    g.draw_duck(player[i], 50 + 75 * i, 400, True)
    g.draw_duck(enemy[i], 450 + 75 * i, 400, False)
crop = surf.subsurface(pygame.Rect(30, 370, 740, 130)).copy()
save(pygame.transform.scale(crop, (crop.get_width() * 2, crop.get_height() * 2)), "static.png")


# training scene ducks (draw_duck2)
surf.fill(BG)
for i in range(4):
    g.draw_duck2(player[i], 50 + 150 * i, 400)
save(surf.subsurface(pygame.Rect(0, 340, 700, 200)).copy(), "training.png")


def frame(active, targets, p, special=False, top=360):
    facing = 1 if active < 4 else -1
    acc = UI.get_accessories(units[active].path)
    anim = UI.special_animation_for(acc) if special else UI.animation_for(acc)
    if not anim.targets_include_self:
        targets = [t for t in targets if t != active]
    pose = anim.pose(p)
    ctx = UI.AttackContext(acc, anim, g._slot_pos(active), facing,
                           [g._slot_pos(t) + UI.DUCK_DISPLAY_SIZE / 2 for t in targets])
    surf.fill(BG)
    anim.draw_under(surf, p, ctx)
    for i in [i for i in range(8) if i != active] + [active]:
        pos = g._slot_pos(i)
        if i == active:
            g.draw_duck(units[i], pos.x + pose.dx * facing, pos.y, i < 4, pose)
        else:
            g.draw_duck(units[i], pos.x, pos.y, i < 4)
    anim.draw_effects(surf, p, ctx)
    return surf.subsurface(pygame.Rect(0, top, 800, 500 - top)).copy()


# (file name, active slot 0-7, target slots)
ATTACKS = [
    ("knight", 0, [4]),
    ("mage", 1, [4, 5]),
    ("cleric", 2, [4]),
    ("rogue", 3, [4]),
    ("enemy_rogue", 4, [0]),
    ("enemy_cleric", 5, [0]),
    ("enemy_mage", 6, [0, 1]),
    ("enemy_knight", 7, [0]),
]
for name, active, targets in ATTACKS:
    strip = pygame.Surface((800, 140 * len(PROGRESS_STEPS)))
    for k, p in enumerate(PROGRESS_STEPS):
        strip.blit(frame(active, targets, p), (0, 140 * k))
    save(strip, f"{name}_strip.png")

# special attacks (taller crop so overlays above the ducks are visible)
SPECIALS = [
    ("special_cleric", 2, [0, 1, 2, 3]),
]
SPECIAL_STEPS = [0.1, 0.3, 0.45, 0.6, 0.75, 0.95]
for name, active, targets in SPECIALS:
    strip = pygame.Surface((800, 250 * len(SPECIAL_STEPS)))
    for k, p in enumerate(SPECIAL_STEPS):
        strip.blit(frame(active, targets, p, special=True, top=250), (0, 250 * k))
    save(strip, f"{name}_strip.png")

print(f"Wrote previews to {OUT}")
