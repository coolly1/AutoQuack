from enum import Enum


def load_unit(file):
    data = []
    with open(file, "r") as file:
        content = file.readline()
        content = file.read()

        data = content.strip().split(",")

    unit = UNIT(base_health=int(data[0]), base_attack_dmg=int(data[1]), attack_dmg_growth=int(data[2]), base_special_attack=int(data[3]), special_attack_growth=int(data[4]),
                base_speed = int(data[5]), max_charge= int(data[6]), path = str(data[7]), normal_target = TARGET(int(data[8])),
                special_action=SPECIAL(data[9]))
    return unit

class TARGET(Enum):
    FRONT = 1
    BACK = 2
    RANDOM = 3
    ALL = 4
    SELF = 5
    TEAM = 6
    
class COLOR(Enum):
    YELLOW = 1
    MALLARD = 2
    COMS = 3


class TRAINABLE_STAT(Enum):
    ATK = 1
    SPK = 2

class SPECIAL(Enum):
    SOOTHING_QUACK = "Soothing Quack"
    FINAL_QUACK = "The Final Quack"
    BILL_BEATDOWN = "Bill Beatdown"
    ABYSSAL_SPLASH = "Abyssal Splash"
    DUCKY_DEFENSE = "Ducky Defense"

#SPECIAL ACTION FUNCTIONS
def soothing_quack(caster):
    """Heals FRONT teammate based on special attack power."""
    heal_amount = caster.special_attack * 2
    return (round(heal_amount), TARGET.FRONT, False, True)

def final_quack(caster):
    """Deals large Single Target damage to the BACK of enemy team"""
    damage = caster.special_attack * 3.5
    return (round(damage), TARGET.BACK, False, True)

def bill_beatdown(caster):
    """Deals single target damage to the FRONT of the enemy team"""
    damage = caster.special_attack *1.5
    return (round(damage), TARGET.FRONT, False, True)

def abyssal_splash(caster):
    """Deals medium damage to all targets on enemy team"""
    damage = caster.special_attack * 2.5
    return (round(damage), TARGET.TEAM, False, True)

def ducky_defense(caster):
    """Increases duck's defense by a moderate amount"""
    buff = caster.special_attack * 1.5
    return (round(buff), TARGET.SELF, True, True)

class UNIT:
    max_health: int
    base_health: int
    current_health: int
    #health growth

    attack_dmg: int
    base_attack_dmg: int
    attack_dmg_growth: int

    special_attack: int
    base_special_attack: int
    special_attack_growth: int
    special_action: SPECIAL

    speed: int
    base_speed: int
    #speed growth

    max_charge: int
    current_charge: int = 0

    path: str
    normal_target: TARGET
    color: COLOR = COLOR.YELLOW

    def __init__(self, base_health, base_attack_dmg, attack_dmg_growth, base_special_attack, special_attack_growth, base_speed, max_charge, path, normal_target: TARGET,special_action: SPECIAL):

        self.base_max_health = base_health
        self.base_attack_dmg = base_attack_dmg
        self.base_special_attack = base_special_attack
        self.base_speed = base_speed

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
                self.base_attack_dmg += self.attack_dmg_growth * score

            case TRAINABLE_STAT.SPK:
                self.base_special_attack += self.special_attack_growth * score
            case _:
                print("bad")
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
        return (damage, target, is_self, is_special)
        """

        if self.current_charge >= self.max_charge:
            self.current_charge = 0

            match self.special_action:
                case SPECIAL.HEALING_QUACK:
                    return healing_quack(self)
                case SPECIAL.FINAL_QUACK:
                    return final_quack(self)
                case SPECIAL.BILL_BEATDOWN:
                    return bill_beatdown(self)
                case SPECIAL.ABYSSAL_SPLASH:
                    return abyssal_splash(self)
                case SPECIAL.DUCKY_DEFENSE:
                    return ducky_defense(self)
                case _:
                    print("bad")

        else:
            self.current_charge += 1
            return (self.attack_dmg, self.normal_target, False, False)

    def is_dead(self):
        return self.current_health <= 0

    def apply_damage(self, amount):
        self.current_health = max(0, self.current_health - amount)
        pass

    def __str__(self):
        return str("current health: ") + str(self.current_health) + str(", current charge: ") + str(self.current_charge)

    #def zoomies(caster):
    #pass

    """Future Stats maybe
     -Defense
     -Bebuffs
     -Passive
     -Defense
     -Speed Training
     -Health training
     """