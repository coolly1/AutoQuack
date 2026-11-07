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


    def __init__(self, max_health, attack_dmg, attack_dmg_growth, ability_power, ability_power_growth, speed, max_charge):
        pass

    def train(self, stat_num: Trainable_Stat, score):
        if stat_num == Trainable_Stat.ATK:
            self.attack_dmg += self.attack_dmg_growth * score
        elif stat_num == Trainable_Stat.SPK:
            self.ability_power += self.ability_power_growth * score
        pass

    def get_attack():
        

        """
        This is a multi comment
        Returns: [damage, target, is_self]
        """
        
        
        

    #Future Stats maybe
    # -Defense
    # -Bebuffs
    # -Passive

    
