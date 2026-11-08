"""
Duck accessories (hat + weapon) and the attack animations that drive them.

Coordinate conventions (important when editing positions.json):
  * All pixel numbers in positions.json are in SOURCE sprite pixels
    (duck skin = 193 px wide, weapon.png / hat.png at their native size).
  * Everything is authored for a duck FACING RIGHT (the player side).
    Enemies are mirrored automatically (images flipped, x mirrored, angles negated).
  * Angles are degrees, counter-clockwise positive, 0 = weapon pointing straight up.
    So the knight's rest_angle of -75 tips the sword 75 degrees clockwise (forward).

positions.json layout:
{
  "weapon": {"scale": 0.4, "rest_angle": -75,
             "grip": [x, y],    # pixel ON weapon.png that sits in the duck's hand (pivot)
             "tip":  [x, y],    # pixel ON weapon.png where projectiles spawn
             "mount": [x, y]},  # pixel ON the duck skin where the grip attaches
  "hat":    {"scale": 0.75,
             "anchor": [x, y],  # pixel ON hat.png
             "mount": [x, y],   # pixel ON the duck skin
             "art_faces_left": true}, # optional: hat.png was drawn facing left (default false)
  "projectile": {"scale": 2.0}      # optional: projectile.png scale (same units as the weapon scale)
}
"""
import json
import math
import os
from dataclasses import dataclass

import pygame
from pygame.math import Vector2

DUCK_SRC_W = 193          # width of the skin png before UI scales it down
DUCK_SCALE = 1 / 3        # must match the scale UI applies to the skin
DUCK_DISPLAY_SIZE = Vector2(64, 65)

SPRITES_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sprites"))

DEFAULT_CONFIG = {
    "weapon": {"scale": 1.0, "rest_angle": 0, "grip": [0, 0], "tip": [0, 0], "mount": [100, 130]},
    "hat": {"scale": 1.0, "anchor": [0, 0], "mount": [100, 20]},
    "projectile": {"scale": 2.0},
}


# --------------------------------------------------------------------------- helpers
def resolve_unit_folder(path: str):
    """Turn a UNIT.path (e.g. 'AutoQuack/sprites/ducks/units/mage') into a real folder, or None."""
    norm = path.replace("\\", "/")
    i = norm.find("sprites/")
    rel = norm[i + len("sprites/"):] if i >= 0 else norm
    folder = os.path.join(SPRITES_ROOT, rel)
    return folder if os.path.isdir(folder) else None


def _blit_rotated(surf, img, pivot, target, angle):
    """Blit img rotated CCW by `angle`, keeping the image pixel `pivot` pinned at screen point `target`."""
    offset = Vector2(pivot) - Vector2(img.get_size()) / 2
    rotated = pygame.transform.rotate(img, angle)
    rect = rotated.get_rect(center=Vector2(target) - offset.rotate(-angle))
    surf.blit(rotated, rect)


def _scaled(img, factor):
    size = (max(1, round(img.get_width() * factor)), max(1, round(img.get_height() * factor)))
    return pygame.transform.smoothscale(img, size), (size[0] / img.get_width(), size[1] / img.get_height())


def keyframes(frames, p):
    """frames = [(progress, value), ...] sorted by progress. Smoothstep between keys."""
    if p <= frames[0][0]:
        return frames[0][1]
    for (t0, v0), (t1, v1) in zip(frames, frames[1:]):
        if p <= t1:
            q = (p - t0) / (t1 - t0) if t1 > t0 else 1.0
            q = q * q * (3 - 2 * q)
            return v0 + (v1 - v0) * q
    return frames[-1][1]


# --------------------------------------------------------------------------- accessory set
@dataclass
class _Oriented:
    hat: pygame.Surface | None
    hat_anchor: Vector2
    hat_mount: Vector2
    wep: pygame.Surface | None
    grip: Vector2
    tip: Vector2
    hand_mount: Vector2
    proj: pygame.Surface | None = None


class Accessories:
    """Hat + weapon sprites for one unit type. Built once, cached, drawn every frame."""

    def __init__(self, folder: str):
        self.config = {k: dict(v) for k, v in DEFAULT_CONFIG.items()}
        cfg_path = os.path.join(folder, "positions.json")
        try:
            with open(cfg_path, "r") as f:
                loaded = json.load(f)
            for section in ("weapon", "hat", "projectile"):
                self.config[section].update(loaded.get(section, {}))
        except (OSError, ValueError):
            pass  # empty / missing / invalid json -> defaults

        self.hat_src = self._load(os.path.join(folder, "hat.png"))
        self.wep_src = self._load(os.path.join(folder, "weapon.png"))
        self.proj_src = self._load(os.path.join(folder, "projectile.png"))
        self.rest_angle = float(self.config["weapon"]["rest_angle"])
        self.name = os.path.basename(os.path.normpath(folder)).lower()
        self._cache = {}

    @staticmethod
    def _load(path):
        try:
            return pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            return None

    def oriented(self, mirrored: bool) -> _Oriented:
        if mirrored not in self._cache:
            self._cache[mirrored] = self._build(mirrored)
        return self._cache[mirrored]

    def _build(self, mirrored):
        cfg_w, cfg_h = self.config["weapon"], self.config["hat"]
        duck_w = DUCK_SRC_W * DUCK_SCALE

        def prep(src, scale, points, art_faces_left=False):
            if src is None:
                return None, [Vector2() for _ in points]
            img, (rx, ry) = _scaled(src, scale * DUCK_SCALE)
            pts = [Vector2(p[0] * rx, p[1] * ry) for p in points]
            # the image must be flipped when the duck's facing differs from the way the art was drawn
            if mirrored != art_faces_left:
                img = pygame.transform.flip(img, True, False)
                pts = [Vector2(img.get_width() - p.x, p.y) for p in pts]
            return img, pts

        wep, (grip, tip) = prep(self.wep_src, cfg_w["scale"], [cfg_w["grip"], cfg_w["tip"]])
        hat, (anchor,) = prep(self.hat_src, cfg_h["scale"], [cfg_h["anchor"]],
                              art_faces_left=cfg_h.get("art_faces_left", False))

        def mount(m):
            v = Vector2(m) * DUCK_SCALE
            return Vector2(duck_w - v.x, v.y) if mirrored else v

        proj, _ = prep(self.proj_src, self.config["projectile"]["scale"], [])

        return _Oriented(hat, anchor, mount(cfg_h["mount"]), wep, grip, tip, mount(cfg_w["mount"]), proj)

    # ---- drawing
    def weapon_tip(self, duck_pos, mirrored, angle) -> Vector2:
        o = self.oriented(mirrored)
        a = -angle if mirrored else angle
        return Vector2(duck_pos) + o.hand_mount + (o.tip - o.grip).rotate(-a)

    def draw_weapon(self, surf, duck_pos, mirrored, angle):
        """angle is in the right-facing frame (absolute, rest angle already included)."""
        o = self.oriented(mirrored)
        if o.wep is None:
            return
        a = -angle if mirrored else angle
        _blit_rotated(surf, o.wep, o.grip, Vector2(duck_pos) + o.hand_mount, a)

    def draw_weapon_free(self, surf, center, mirrored, angle):
        """Weapon spinning about its own center at an arbitrary screen point (thrown daggers)."""
        o = self.oriented(mirrored)
        if o.wep is None:
            return
        a = -angle if mirrored else angle
        _blit_rotated(surf, o.wep, Vector2(o.wep.get_size()) / 2, center, a)

    @property
    def has_projectile(self):
        return self.proj_src is not None

    def draw_projectile(self, surf, center, mirrored, angle=0):
        """projectile.png centered on a screen point, optionally spinning (angle in the right-facing frame)."""
        o = self.oriented(mirrored)
        if o.proj is None:
            return
        a = -angle if mirrored else angle
        _blit_rotated(surf, o.proj, Vector2(o.proj.get_size()) / 2, center, a)

    def draw_hat(self, surf, duck_pos, mirrored):
        o = self.oriented(mirrored)
        if o.hat is not None:
            surf.blit(o.hat, Vector2(duck_pos) + o.hat_mount - o.hat_anchor)


_cache: dict = {}


def get_accessories(unit_path: str):
    """Cached lookup. Returns None when the unit has no accessory folder."""
    if unit_path not in _cache:
        folder = resolve_unit_folder(unit_path)
        _cache[unit_path] = Accessories(folder) if folder else None
    return _cache[unit_path]


# --------------------------------------------------------------------------- animations
@dataclass
class Pose:
    dx: float = 0.0                # forward lunge in px (forward = toward the enemy)
    angle: float = 0.0             # weapon angle relative to rest_angle
    weapon_visible: bool = True


@dataclass
class AttackContext:
    acc: Accessories
    anim: "Animation"
    duck_pos: Vector2              # active duck's resting top-left
    facing: int                    # +1 = faces right (player), -1 = faces left (enemy)
    targets: list                  # screen points (duck centers) of affected ducks

    @property
    def mirrored(self):
        return self.facing < 0

    def tip_at(self, p) -> Vector2:
        pose = self.anim.pose(p)
        pos = self.duck_pos + Vector2(pose.dx * self.facing, 0)
        return self.acc.weapon_tip(pos, self.mirrored, self.acc.rest_angle + pose.angle)


class Animation:
    duration = 0.7

    def pose(self, p: float) -> Pose:
        return Pose()

    def draw_effects(self, surf, p: float, ctx: AttackContext):
        pass

    # shared projectile/impact helpers
    @staticmethod
    def _fly(p, launch, land, ctx, draw):
        if not (launch <= p < land):
            return
        q = (p - launch) / (land - launch)
        start = ctx.tip_at(launch)
        for tgt in ctx.targets:
            draw(start.lerp(tgt, q), q, tgt - start)

    @staticmethod
    def _impact(surf, p, land, ctx, color, span=0.12):
        if not (land <= p < land + span):
            return
        q = (p - land) / span
        for tgt in ctx.targets:
            pygame.draw.circle(surf, color, tgt, int(6 + 22 * q), max(1, int(4 * (1 - q))))


class BasicAnim(Animation):
    """Fallback: tiny weapon waggle."""
    duration = 0.4

    def pose(self, p):
        return Pose(angle=keyframes([(0, 0), (0.5, -40), (1, 0)], p))


class KnightAnim(Animation):
    """Lunge forward, wind the sword back, then chop down."""
    duration = 0.8

    def pose(self, p):
        dx = keyframes([(0, 0), (0.25, 0), (0.45, 28), (0.65, 28), (1, 0)], p)
        angle = keyframes([(0, 0), (0.25, 110), (0.45, -75), (0.65, -75), (1, 0)], p)
        return Pose(dx, angle)


class MageAnim(Animation):
    """Raise the wand, flick it forward, shoot an orb."""
    duration = 1.0
    LAUNCH, LAND = 0.45, 0.8

    def pose(self, p):
        return Pose(angle=keyframes([(0, 0), (0.3, 55), (0.45, -35), (0.7, -35), (1, 0)], p))

    def draw_effects(self, surf, p, ctx):
        r = 7

        def orb(pos, q, vec):
            if ctx.acc.has_projectile:
                ctx.acc.draw_projectile(surf, pos, ctx.mirrored)
                return
            pygame.draw.circle(surf, (20, 70, 200), pos, r + 3)
            pygame.draw.circle(surf, (60, 150, 255), pos, r)
            pygame.draw.circle(surf, (200, 230, 255), pos - Vector2(r * 0.3, r * 0.3), max(2, r // 3))

        self._fly(p, self.LAUNCH, self.LAND, ctx, orb)
        self._impact(surf, p, self.LAND, ctx, (120, 190, 255))


class ClericAnim(Animation):
    """Small cross swing, then a golden bolt."""
    duration = 0.9
    LAUNCH, LAND = 0.4, 0.75

    def pose(self, p):
        return Pose(angle=keyframes([(0, 0), (0.25, 20), (0.4, -20), (0.65, -20), (1, 0)], p))

    def draw_effects(self, surf, p, ctx):
        r = 6

        def bolt(pos, q, vec):
            if ctx.acc.has_projectile:
                ctx.acc.draw_projectile(surf, pos, ctx.mirrored, 360 * q)  # sparkle slowly turns in flight
                return
            pygame.draw.circle(surf, (230, 180, 40), pos, r + 3)
            pygame.draw.circle(surf, (255, 245, 170), pos, r)

        self._fly(p, self.LAUNCH, self.LAND, ctx, bolt)
        self._impact(surf, p, self.LAND, ctx, (255, 240, 150))


class RogueAnim(Animation):
    """Wind up, throw the dagger (flies point-first to the target), dagger reappears in hand."""
    duration = 0.9
    LAUNCH, LAND, RETURN = 0.3, 0.65, 0.85

    def pose(self, p):
        angle = keyframes([(0, 0), (0.2, 70), (0.3, -60), (0.85, -60), (1, 0)], p)
        return Pose(angle=angle, weapon_visible=not (self.LAUNCH <= p < self.RETURN))

    def draw_effects(self, surf, p, ctx):
        def dagger(pos, q, vec):
            # no spin: point the dagger along its flight path (art points up at angle 0)
            heading = math.degrees(math.atan2(-vec.x, -vec.y))
            angle = -heading if ctx.mirrored else heading     # draw_* expects the right-facing frame
            if ctx.acc.has_projectile:
                ctx.acc.draw_projectile(surf, pos, ctx.mirrored, angle)
            else:
                ctx.acc.draw_weapon_free(surf, pos, ctx.mirrored, angle)

        self._fly(p, self.LAUNCH, self.LAND, ctx, dagger)
        self._impact(surf, p, self.LAND, ctx, (220, 220, 220), span=0.1)


ANIMATIONS = {
    "knight": KnightAnim,
    "mage": MageAnim,
    "cleric": ClericAnim,
    "rogue": RogueAnim,
}


def animation_for(acc) -> Animation:
    """Pick the animation from the unit folder name; any unit can be on either team."""
    cls = ANIMATIONS.get(acc.name if acc else "", BasicAnim)
    return cls()
