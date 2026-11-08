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
             "mount": [x, y],   # pixel ON the duck skin where the grip attaches
             "spawn_offset": [x, y]},  # optional: shift where projectiles spawn (source px, right-facing; -y = higher)
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
import random
from dataclasses import dataclass, field

import pygame
from pygame.math import Vector2

DUCK_SRC_W = 193          # width of the skin png before UI scales it down
DUCK_SCALE = 1 / 3        # battle scene: must match the scale UI applies to the skin
TRAINING_DUCK_SCALE = 1 / 2   # training scene (draw_duck2)
DUCK_DISPLAY_SIZE = Vector2(64, 65)
SCREEN_W = 800
# x-range of the team a duck facing +1 (player side) / -1 (enemy side) is attacking
TEAM_X_SPAN = {1: (450, 450 + 75 * 3 + 64), -1: (50, 50 + 75 * 3 + 64)}

SPRITES_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sprites"))

DEFAULT_CONFIG = {
    "weapon": {"scale": 1.0, "rest_angle": 0, "grip": [0, 0], "tip": [0, 0], "mount": [100, 130],
               "spawn_offset": [0, 0]},
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
    spawn: Vector2 = field(default_factory=Vector2)


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
        self.folder = folder
        self._cache = {}
        self._effects = {}

    def effect_image(self, filename: str, scale: float = 1.0):
        """Extra sprite from the unit folder (special-attack art), scaled in screen px. None if missing."""
        key = (filename, scale)
        if key not in self._effects:
            src = self._load(os.path.join(self.folder, filename))
            self._effects[key] = _scaled(src, scale)[0] if src is not None else None
        return self._effects[key]

    @staticmethod
    def _load(path):
        try:
            return pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            return None

    def oriented(self, mirrored: bool, scale: float = DUCK_SCALE) -> _Oriented:
        key = (mirrored, scale)
        if key not in self._cache:
            self._cache[key] = self._build(mirrored, scale)
        return self._cache[key]

    def _build(self, mirrored, duck_scale):
        cfg_w, cfg_h = self.config["weapon"], self.config["hat"]
        duck_w = DUCK_SRC_W * duck_scale

        def prep(src, scale, points, art_faces_left=False):
            if src is None:
                return None, [Vector2() for _ in points]
            img, (rx, ry) = _scaled(src, scale * duck_scale)
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
            v = Vector2(m) * duck_scale
            return Vector2(duck_w - v.x, v.y) if mirrored else v

        proj, _ = prep(self.proj_src, self.config["projectile"]["scale"], [])
        sx, sy = cfg_w.get("spawn_offset", [0, 0])
        spawn = Vector2(-sx if mirrored else sx, sy) * duck_scale

        return _Oriented(hat, anchor, mount(cfg_h["mount"]), wep, grip, tip, mount(cfg_w["mount"]), proj, spawn)

    # ---- drawing
    def weapon_tip(self, duck_pos, mirrored, angle, scale=DUCK_SCALE) -> Vector2:
        """Where projectiles spawn: the weapon tip plus the optional spawn_offset."""
        o = self.oriented(mirrored, scale)
        a = -angle if mirrored else angle
        return Vector2(duck_pos) + o.hand_mount + (o.tip - o.grip).rotate(-a) + o.spawn

    def draw_weapon(self, surf, duck_pos, mirrored, angle, scale=DUCK_SCALE):
        """angle is in the right-facing frame (absolute, rest angle already included)."""
        o = self.oriented(mirrored, scale)
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

    def draw_hat(self, surf, duck_pos, mirrored, scale=DUCK_SCALE):
        o = self.oriented(mirrored, scale)
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
    # teleport support (rogue special): where the whole duck is drawn, which way it faces, and whether it shows
    offset: Vector2 = field(default_factory=Vector2)   # screen offset from the duck's slot
    flip: bool = False                                  # face the opposite way from its team
    visible: bool = True
    behind: bool = False                                # draw this duck BEFORE the others (so they cover it)


@dataclass
class AttackContext:
    acc: Accessories
    anim: "Animation"
    duck_pos: Vector2              # active duck's resting top-left
    facing: int                    # +1 = faces right (player), -1 = faces left (enemy)
    targets: list                  # screen points (duck centers) of affected ducks

    def __post_init__(self):
        self.anim.ctx = self       # lets an animation look up where its targets are

    @property
    def mirrored(self):
        return self.facing < 0

    def tip_at(self, p) -> Vector2:
        pose = self.anim.pose(p)
        pos = self.duck_pos + Vector2(pose.dx * self.facing, 0)
        return self.acc.weapon_tip(pos, self.mirrored, self.acc.rest_angle + pose.angle)


class Animation:
    duration = 0.7
    targets_include_self = False   # True for team-wide effects (heals) that also affect the caster
    ctx = None                     # set by AttackContext; gives pose() access to targets / positions

    def pose(self, p: float) -> Pose:
        return Pose()

    def draw_under(self, surf, p: float, ctx: AttackContext):
        """Drawn BEFORE the ducks (ground effects such as healing circles)."""

    def draw_effects(self, surf, p: float, ctx: AttackContext):
        """Drawn AFTER the ducks (projectiles, particles, overlays)."""

    # shared projectile/impact helpers
    @staticmethod
    def _fly(p, launch, land, ctx, draw, start_for=None):
        """Move a projectile per target. start_for(j, target) -> spawn point; default is the weapon tip."""
        if not (launch <= p < land):
            return
        q = (p - launch) / (land - launch)
        tip = ctx.tip_at(launch) if start_for is None else None
        for j, tgt in enumerate(ctx.targets):
            start = tip if tip is not None else start_for(j, tgt)
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
    duration = 0.8                 # orb flight takes (LAND - LAUNCH) * duration = 0.18 s (was 0.35 s)
    LAUNCH, LAND = 0.5, 0.72

    def pose(self, p):
        return Pose(angle=keyframes([(0, 0), (0.3, 55), (0.5, -35), (0.75, -35), (1, 0)], p))

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
    duration = 1.0                 # bolt flight takes (LAND - LAUNCH) * duration = 0.40 s (was 0.72 s)
    LAUNCH, LAND = 0.36, 0.76
    SPAWN_Y = 10                   # bolts fall from the very top of the screen

    def __init__(self):
        self._spawn_u = [random.random() for _ in range(8)]   # one random spot per target, fixed for this attack

    def _spawn_point(self, ctx, j):
        lo, hi = TEAM_X_SPAN[ctx.facing]                       # above the OTHER team
        return Vector2(lo + self._spawn_u[j % 8] * (hi - lo), self.SPAWN_Y)

    def pose(self, p):
        return Pose(angle=keyframes([(0, 0), (0.23, 20), (0.36, -20), (0.65, -20), (1, 0)], p))

    def draw_effects(self, surf, p, ctx):
        r = 6

        def bolt(pos, q, vec):
            if ctx.acc.has_projectile:
                ctx.acc.draw_projectile(surf, pos, ctx.mirrored, 360 * q)  # sparkle slowly turns in flight
                return
            pygame.draw.circle(surf, (230, 180, 40), pos, r + 3)
            pygame.draw.circle(surf, (255, 245, 170), pos, r)

        self._fly(p, self.LAUNCH, self.LAND, ctx, bolt, start_for=lambda j, tgt: self._spawn_point(ctx, j))
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


def _trapezoid(p, in0, in1, out0, out1):
    """0 before in0, ramps to 1 by in1, holds, ramps back to 0 between out0 and out1."""
    if p <= in0 or p >= out1:
        return 0.0
    if p < in1:
        return (p - in0) / (in1 - in0)
    if p > out0:
        return (out1 - p) / (out1 - out0)
    return 1.0


def _blit_faded(surf, img, center, alpha, zoom=1.0):
    """Blit img centered at `center` with 0..1 alpha and an optional zoom factor."""
    if img is None or alpha <= 0:
        return
    if zoom != 1.0:
        img = pygame.transform.smoothscale(img, (max(1, round(img.get_width() * zoom)),
                                                  max(1, round(img.get_height() * zoom))))
    else:
        img = img.copy()
    img.set_alpha(int(255 * min(alpha, 1.0)))
    surf.blit(img, img.get_rect(center=center))


class ClericSpecialAnim(Animation):
    """Soothing Quack: an ethereal cross shines over the party, a healing circle appears under every
    teammate, and healing particles drift up around each of them. Sprites live in the cleric folder."""
    duration = 2.0
    targets_include_self = True

    CROSS_FILE, CIRCLE_FILE, PARTICLE_FILE = "etherial_cross.png", "healing_circle.png", "healing_particle.png"
    CROSS_SCALE, CIRCLE_SCALE, PARTICLE_SCALE = 1.5, 1.15, 1.0   # on-screen scale of the png (circle ~ duck width)
    CROSS_HEIGHT_ABOVE_DUCKS = 120     # px from the ducks' centers up to the cross center
    PARTICLES_PER_DUCK = 5

    @staticmethod
    def _party_center(ctx):
        n = max(1, len(ctx.targets))
        return Vector2(sum(t.x for t in ctx.targets) / n, min((t.y for t in ctx.targets), default=0))

    def draw_under(self, surf, p, ctx):
        circle = ctx.acc.effect_image(self.CIRCLE_FILE, self.CIRCLE_SCALE)
        a = _trapezoid(p, 0.30, 0.42, 0.88, 1.0)
        for tgt in ctx.targets:
            feet = Vector2(tgt.x, tgt.y + DUCK_DISPLAY_SIZE.y / 2 - 3)
            _blit_faded(surf, circle, feet, a, zoom=0.6 + 0.4 * min(1.0, a * 1.5))   # grows as it fades in

    def draw_effects(self, surf, p, ctx):
        # ethereal cross: soft glow + cross, fades in, pulses, fades out
        a = _trapezoid(p, 0.0, 0.18, 0.5, 0.66)
        if a > 0:
            center = self._party_center(ctx) - Vector2(0, self.CROSS_HEIGHT_ABOVE_DUCKS)
            pulse = 1.0 + 0.08 * math.sin(p * 40)
            cross = ctx.acc.effect_image(self.CROSS_FILE, self.CROSS_SCALE)
            glow_r = int(55 * pulse)
            glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            for k in range(12, 0, -1):                      # many faint concentric rings = soft edge
                pygame.draw.circle(glow, (255, 240, 150, int(a * 11)), (glow_r, glow_r), int(glow_r * k / 12))
            surf.blit(glow, glow.get_rect(center=center))
            _blit_faded(surf, cross, center, a, zoom=pulse)

        # healing particles rising around each teammate
        particle = ctx.acc.effect_image(self.PARTICLE_FILE, self.PARTICLE_SCALE)
        for j, tgt in enumerate(ctx.targets):
            for k in range(self.PARTICLES_PER_DUCK):
                t0 = 0.45 + 0.06 * k + 0.02 * j
                q = (p - t0) / 0.3
                if not 0 <= q < 1:
                    continue
                dx = ((k * 37 + j * 13) % 11 - 5) * 5               # fixed spread, -25..25 px
                y0 = tgt.y + 20 - (k % 3) * 14
                pos = Vector2(tgt.x + dx, y0 - 40 * q)
                _blit_faded(surf, particle, pos, math.sin(math.pi * q))


ANIMATIONS = {
    "knight": KnightAnim,
    "mage": MageAnim,
    "cleric": ClericAnim,
    "rogue": RogueAnim,
}


class RogueSpecialAnim(Animation):
    """The Final Quack: vanish in smoke, reappear just BEHIND the back enemy (facing it), stab, then
    smoke back home. Needs smoke.png in the rogue folder."""
    duration = 2.4

    SMOKE_FILE, SMOKE_SCALE = "smoke.png", 0.3        # ~136 px wide, covers a duck
    BEHIND_PX = 60                                      # how far past the target the rogue stands
    GONE_FROM, BACK_AT = 0.105, 0.80                    # the rogue is away from home in [GONE_FROM, BACK_AT)
    STAB_AT = 0.53                                      # the moment the dagger lands
    # smoke puffs: (fade in start, fully opaque, start fading out, gone)
    OUT_SMOKE = (0.00, 0.07, 0.14, 0.24)                # leaving: covers the swap at GONE_FROM
    IN_SMOKE = (0.70, 0.77, 0.84, 0.95)                 # returning: covers the swap at BACK_AT

    def _dest_offset(self):
        ctx = self.ctx
        if ctx is None or not ctx.targets:
            return Vector2()
        top_left = ctx.targets[0] - DUCK_DISPLAY_SIZE / 2
        x = max(0, min(SCREEN_W - DUCK_DISPLAY_SIZE.x, top_left.x + ctx.facing * self.BEHIND_PX))
        return Vector2(x, top_left.y) - ctx.duck_pos

    def pose(self, p):
        # dagger stab: pull back and raise, then thrust forward (angle is relative to the rest angle)
        dx = keyframes([(0, 0), (0.36, 0), (0.46, -8), (0.53, 14), (0.62, 14), (0.72, 0)], p)
        angle = keyframes([(0, 0), (0.36, 0), (0.46, 55), (0.53, -30), (0.62, -30), (0.72, 0)], p)
        if self.GONE_FROM <= p < self.BACK_AT:
            return Pose(dx, angle, offset=self._dest_offset(), flip=True, behind=True)  # behind the enemy, facing it
        return Pose()

    def _puff(self, surf, p, ctx, window, center):
        a = _trapezoid(p, *window)
        if a <= 0:
            return
        t = (p - window[0]) / (window[3] - window[0])
        _blit_faded(surf, ctx.acc.effect_image(self.SMOKE_FILE, self.SMOKE_SCALE), center, a, zoom=0.7 + 0.6 * t)

    def draw_effects(self, surf, p, ctx):
        home = ctx.duck_pos + DUCK_DISPLAY_SIZE / 2
        away = home + self._dest_offset()
        for window in (self.OUT_SMOKE, self.IN_SMOKE):
            self._puff(surf, p, ctx, window, home)
            self._puff(surf, p, ctx, window, away)
        self._impact(surf, p, self.STAB_AT, ctx, (230, 230, 230), span=0.08)


class KnightSpecialAnim(Animation):
    """Leap into the air above the target, chop down with sword_slash.png trailing the blade, hop home.
    Needs sword_slash.png in the knight folder."""
    duration = 1.5

    SLASH_FILE = "sword_slash.png"
    SLASH_SRC = (271, 385)             # sprite size, its pivot (blade base) and the direction of its leading edge
    SLASH_PIVOT = (47, 385)
    SLASH_LEAD_DEG = 38                # leading edge points this many degrees clockwise of straight up
    SLASH_SIZE = 1.05                  # slash radius relative to the sword length
    LAND_AT = 0.6                      # the moment the sword hits
    SWING = (0.5, 0.6)                 # sword sweeps down in this window
    STAND_OFF = 50                     # px in front of the target the knight lands

    def _dest_x(self):
        ctx = self.ctx
        if ctx is None or not ctx.targets:
            return 0.0
        return ctx.targets[0].x - ctx.facing * self.STAND_OFF - DUCK_DISPLAY_SIZE.x / 2 - ctx.duck_pos.x

    def pose(self, p):
        x = keyframes([(0, 0), (0.1, 0), (0.5, self._dest_x()), (0.76, self._dest_x()), (1, 0)], p)
        y = keyframes([(0, 0), (0.1, 5), (0.42, -210), (0.5, -200), (0.6, 0), (0.76, 0), (0.88, -40), (1, 0)], p)
        angle = keyframes([(0, 0), (0.1, 110), (0.5, 110), (0.6, -75), (0.76, -75), (1, 0)], p)
        return Pose(angle=angle, offset=Vector2(x, y))

    def draw_effects(self, surf, p, ctx):
        alpha = _trapezoid(p, 0.49, 0.52, self.SWING[1], 0.72)
        o = ctx.acc.oriented(ctx.mirrored)
        if alpha > 0 and o.wep is not None:
            pose = self.pose(p)
            reach = (o.tip - o.grip).length()
            img = ctx.acc.effect_image(self.SLASH_FILE, reach * self.SLASH_SIZE / math.hypot(224, 285))
            if img is not None:
                pivot = Vector2(self.SLASH_PIVOT[0] * img.get_width() / self.SLASH_SRC[0],
                                self.SLASH_PIVOT[1] * img.get_height() / self.SLASH_SRC[1])
                theta = ctx.acc.rest_angle + pose.angle + self.SLASH_LEAD_DEG     # CCW, right-facing frame
                if ctx.mirrored:                                                   # art is right-facing
                    img = pygame.transform.flip(img, True, False)
                    pivot.x = img.get_width() - pivot.x
                    theta = -theta
                img = img.copy()
                img.set_alpha(int(220 * alpha))
                _blit_rotated(surf, img, pivot, ctx.duck_pos + pose.offset + o.hand_mount, theta)
        self._impact(surf, p, self.LAND_AT, ctx, (255, 255, 255), span=0.1)


class MageSpecialAnim(Animation):
    """Abyssal Splash: the mage floats up, opens a portal in front of itself, and the geyser shoots out of it
    as abyssal_splash.png is revealed by a crop box growing from just the ellipse to the full sprite."""
    duration = 2.2

    GEYSER_FILE = "abyssal_splash.png"
    CAP_SRC_W = 26                     # width (source px) of the portal ellipse on the left of the sprite
    HEIGHT = 105                       # on-screen height of the geyser
    TILT_DEG = 5                       # geyser points this many degrees below horizontal
    GROW_FROM, GROW_TO = 0.30, 0.54    # crop box expands over this window (progress)
    # the geyser then holds at full length until the fade-out window starts at 0.78
    RISE = 28                          # px the mage floats off the ground
    PORTAL_GAP = 2                     # px between the duck and the portal

    def __init__(self):
        self._comp = {}

    def pose(self, p):
        return Pose(angle=keyframes([(0, 0), (0.2, 40), (0.85, 40), (1, 0)], p),
                    offset=Vector2(0, keyframes([(0, 0), (0.2, -self.RISE), (0.88, -self.RISE), (1, 0)], p)))

    def _geyser(self, ctx, length):
        """Portal cap + stretched body at the right length, facing the attack direction."""
        key = (round(length), ctx.mirrored)
        if key not in self._comp:
            src = ctx.acc.effect_image(self.GEYSER_FILE, 1.0)
            s = self.HEIGHT / src.get_height()
            cap_w = max(1, round(self.CAP_SRC_W * s))
            cap = pygame.transform.smoothscale(src.subsurface(0, 0, self.CAP_SRC_W, src.get_height()), (cap_w, self.HEIGHT))
            body = pygame.transform.smoothscale(
                src.subsurface(self.CAP_SRC_W, 0, src.get_width() - self.CAP_SRC_W, src.get_height()),
                (max(1, round(length) - cap_w), self.HEIGHT))
            comp = pygame.Surface((cap_w + body.get_width(), self.HEIGHT), pygame.SRCALPHA)
            comp.blit(cap, (0, 0))
            comp.blit(body, (cap_w, 0))
            if ctx.mirrored:
                comp = pygame.transform.flip(comp, True, False)
            self._comp[key] = (comp, cap_w)
        return self._comp[key]

    def draw_effects(self, surf, p, ctx):
        fade = _trapezoid(p, 0.15, 0.3, 0.78, 0.91)
        if fade <= 0 or not ctx.targets:
            return
        pose = self.pose(p)
        center_y = ctx.duck_pos.y + DUCK_DISPLAY_SIZE.y / 2 + pose.offset.y
        if ctx.facing > 0:
            edge = ctx.duck_pos.x + DUCK_DISPLAY_SIZE.x + self.PORTAL_GAP        # portal's left edge
            reach = max(t.x for t in ctx.targets) + 40 - edge
        else:
            edge = ctx.duck_pos.x - self.PORTAL_GAP                              # portal's right edge
            reach = edge - (min(t.x for t in ctx.targets) - 40)
        comp, cap_w = self._geyser(ctx, max(reach, 120))
        grow = keyframes([(self.GROW_FROM, 0), (self.GROW_TO, 1)], p)          # crop box: ellipse -> full sprite
        w = max(1, round(cap_w + (comp.get_width() - cap_w) * grow))
        if ctx.facing > 0:
            crop = comp.subsurface(0, 0, w, self.HEIGHT).copy()
            pivot = Vector2(0, self.HEIGHT / 2)                                   # portal end, left
        else:
            crop = comp.subsurface(comp.get_width() - w, 0, w, self.HEIGHT).copy()
            pivot = Vector2(w, self.HEIGHT / 2)                                   # portal end, right
        crop.set_alpha(int(255 * min(fade * 1.5, 1.0) if p < 0.5 else 255 * fade))
        # tilt the geyser downward about the portal (clockwise facing right, counter-clockwise facing left)
        _blit_rotated(surf, crop, pivot, Vector2(edge, center_y), -self.TILT_DEG * ctx.facing)


SPECIAL_ANIMATIONS = {
    "knight": KnightSpecialAnim,
    "mage": MageSpecialAnim,
    "cleric": ClericSpecialAnim,
    "rogue": RogueSpecialAnim,
}


def special_animation_for(acc):
    """Special-attack animation for this unit folder, or None if it doesn't have one yet."""
    cls = SPECIAL_ANIMATIONS.get(acc.name if acc else "")
    return cls() if cls else None


def animation_for(acc) -> Animation:
    """Pick the animation from the unit folder name; any unit can be on either team."""
    cls = ANIMATIONS.get(acc.name if acc else "", BasicAnim)
    return cls()
