from enum import Enum
from collections.abc import Callable

class STATUS_TRIGGERS(Enum):
    ON_ACTION = 0, # when duck takes a turn
    ON_RECV_DAMAGE = 1,
    ON_SPECIAL = 2,
    ON_ATTACK = 3,
    ON_RECV_STATUS = 4,

class STATUS_TYPE:
    DEFENSE = 1

class Status:
    trigger: STATUS_TRIGGERS
    # effect: EFFECT_AREA
    apply_func: Callable
    count: int

    def __init__(self, trigger, count, func):
        self.trigger = trigger
        # self.effect = effect
        self.apply_func = func
        self.count = count

    def apply(self, unit, extra):
        """
        :param unit: the unit that is being apply to
        :param extra: if there is extra info needed for the trigger
        :return: something if extra was supplied
        """

        return self.apply_func(unit, extra, self.count)

        # match self.effect:
        #     case EFFECT_AREA.MAX_HP:
        #         pass
        #     case EFFECT_AREA.CUR_HP:
        #         pass
        #     case EFFECT_AREA.ACTION:
        #         pass
        #     case EFFECT_AREA.DAMAGE:
        #         pass
        #     case EFFECT_AREA.SPD:
        #         pass
        #     case EFFECT_AREA.SPK:
        #         pass
        #     case EFFECT_AREA.ATK:
        #         pass

def defense(unit, damage, count):
    if(damage > 0):
        return max(0, damage-count)
    else:
        return damage


# Defense: ON_RECV_DAMAGE, DAMAGE, -5
# Silence: ON_SPECIAL, ACTION, Do_Nothing
# Slowing: ON_RECV_STATUS, SPD, SPD - 5
# Poison: ON_ACTION, CUR_HP, CUR_HP - 5
defense_5 = Status(STATUS_TRIGGERS.ON_RECV_DAMAGE, 5, defense)