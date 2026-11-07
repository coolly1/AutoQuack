from enum import Enum


class TARGET(Enum):
    FRONT = 1
    BACK = 2
    RANDOM = 3
    ALL = 4
    SELF = 5
    TEAM = 6


class TRAINABLE_STAT(Enum):
    ATK = 1
    SPK = 2

class SPECIAL(Enum):
    SPECIAL_1 = 1

class UNIT:
    max_health: int
    current_health: int

    attack_dmg: int
    base_attack_dmg: int
    attack_dmg_growth: int

    special_attack: int
    base_special_attack: int
    special_attack_growth: int

    speed: int
    base_speed: int

    max_charge: int
    current_charge: int = 0

    path: str
    normal_target: TARGET

    # for future

    def __init__(self, max_health, attack_dmg, special_attack, speed, max_charge, normal_target: TARGET,
                 special_action: SPECIAL, path, base_speed, base_ability_power, attack_dmg_growth,
                 special_attack_growth):

        self.base_max_health = max_health
        self.base_attack_dmg = attack_dmg
        self.base_special_attack = special_attack
        self.base_speed = speed

        self.attack_dmg_growth = attack_dmg_growth
        self.special_attack_growth = special_attack_growth

        self.max_charge = max_charge
        self.normal_target = normal_target
        self.special_action = special_action
        self.path = path
        self.reset_for_battle()

    def train(self, stat_num: TRAINABLE_STAT, score):
        match stat_num:
            case TRAINABLE_STAT.ATK:
                self.attack_dmg += self.attack_dmg_growth * score

            case TRAINABLE_STAT.SPK:
                self.special_attack += self.special_attack_growth * score
        self.reset_for_battle()

    def reset_for_battle(self):
        self.current_health = self.base_max_health
        self.max_health = self.base_max_health
        self.special_attack = self.base_special_attack
        self.attack_dmg = self.base_attack_dmg
        self.speed = self.base_speed
        self.current_charge = 0

    def execute_turn(self) -> tuple:

        """
        Comment for tyler-poo
        return (damage, target, is_self)
        """

        if self.current_charge >= self.max_charge:
            self.current_charge = 0
            return self.special_action
        else:
            self.current_charge += 1
            return (self.attack_dmg, self.normal_target, False)

    def is_dead(self):
        return self.current_health <= 0

    def apply_damage(self, amount):
        self.current_health += max(0, self.current_health - amount)
        pass


def zoomies(caster):
    """Future Stats maybe
     -Defense
     -Bebuffs
     -Passive
     -Defense
     -Speed Training
     -Health training
     """


unit_A = unit(max_health=1, attack_dmg=1, ability_power=1, speed=1, max_charge=1, normal_target=FRONT,
              special_action=Type)
unit_B = unit(max_health=1, attack_dmg=1, ability_power=1, speed=1, max_charge=1, normal_target=FRONT,
              special_action=Type)
