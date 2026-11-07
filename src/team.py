from Units import unit
from Units import Trainable_Stat
class player():
    team: list[unit]

    def __init__(self, units: list[unit]):
        self.team = units

    def train(self, unit_idx, stats_num: Trainable_Stat, amount):
        self.team[unit_idx]



