from enum import Enum

class Target(Enum):
    FRONT = 1
    BACK = 2
    RANDOM = 3
    ALL = 4
    SELF = 5

class Trainable_Stat(Enum):
    ATK = 1
    SPK = 2

class unit:
    max_health: int
    current_health: int
    attack_dmg: int
    attack_dmg_growth: int
    ability_power: int
    ability_power_growth: int
    speed: int
    max_charge: int
    current_charge: int = 0
    path: str
    normal_target: str
    special_action: str



    def __init__(self, max_health, attack_dmg, ability_power, speed, max_charge, normal_target: TARGET, special_action: SPECIAL, pat):
        self.base_max_health = max_health
        
        self.reset_for_battle()
        pass

    def train(self, stat_num: Trainable_Stat, score):
        match stat_num:
            case Trainable_Stat.ATK:
                self.attack_dmg += self.attack_dmg_growth * score

            case Trainable_Stat.SPK:
                self.ability_power += self.ability_power_growth * score
        pass

    def reset_for_battle(self):
        self.current_health = self.max_health
        self.ability_power
        self.attack_dmg
        self.speed


    def execute_turn(self):
        if self.current_charge >= self.max_charge:
            self.current_charge = 0
            return self.special_action(self)
        else:
            self.current_charge += 1
            return [self.attack_dmg, self.normal_target, False]
    

def zoomies(caster):

        
        

    """Future Stats maybe
     -Defense
     -Bebuffs
     -Passive
     -Defense
     -Speed Training
     -Health training
     """


special_action1 = class(special)


unit_A = unit(max_health=1, attack_dmg=1, ability_power=1, speed=1, max_charge=1, normal_target=FRONT, special_action=Type)
unit_B = unit(max_health=1, attack_dmg=1, ability_power=1, speed=1, max_charge=1, normal_target=FRONT, special_action=Type)