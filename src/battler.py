MAX_TURNS = 100

from Units import unit
from Units import Target
import heapq
import random

SEED_RAND = 0

enemy_lists = []

class battler():
    # this is used to prevent ties
    turn_id: int
    turn_order_pq: list[(float, int, int, unit)]
    player_team: list[unit]
    units: list[unit]

    def __init__(self, player_team: list):
        self.player_team = player_team
        random.seed(SEED_RAND)

    def start_battle(self, round_idx) -> bool:
        """

        :return: bool if player won or loss
        """

        # get the enemies
        enemy_team: list[unit] = []

        self.turn_id = 0
        self.turn_order_pq =[]
        self.units = self.player_team + enemy_lists

        fronts = [0, 0]
        backs = [3, 3]

        teams = [self.player_team, enemy_team]

        # add player, and enemy
        for unit_idx in range(len(self.units)):
            self.schedule_unit(unit_idx, 0.0)

        for turn_order in range(MAX_TURNS):
            (prev_priority, turn_id, active_unit_idx) = heapq.heappop(self.turn_order_pq)

            # if unit is dead then continue
            if(self.units[active_unit_idx].is_dead()):
                continue

            (damage, target, is_self) = self.units[active_unit_idx].execute_turn()

            # what team we are targeting
            target_team: int

            if(is_self):
                target_team = active_unit_idx < 4
            else:
                target_team = active_unit_idx >= 4

            match target:
                case Target.FRONT:
                    teams[target_team][fronts[target_team]].apply_damage(damage)
                case Target.BACK:
                    teams[target_team][backs[target_team]].apply_damage(damage)
                case Target.SELF:
                    teams[target_team][active_unit_idx % 4].apply_damage(damage)
                case Target.RANDOM:
                    while(True):
                        target = random.randint(0, 3)
                        if(teams[target_team][target].is_dead()):
                            continue

                        teams[target_team][target].apply_damage(damage)
                        break
                case Target.TEAM:
                    for unit_idx
                case Target.ALL:

                    teams[target_team][1].apply_damage(damage)

            for team_idx in range(2):
                while(self.player_team[fronts[team_idx]].is_dead()):
                    fronts[team_idx] += 1
                    if(fronts[team_idx] > backs[team_idx]):
                        return team_idx == 1

                while(self.player_team[backs[team_idx]].is_dead()):
                    backs[team_idx] -= 1

            self.schedule_unit(active_unit, prev_priority=prev_priority)

    def schedule_unit(self, unit_idx, prev_priority):

        unit = self.units
        heapq.heappush(self.turn_order_pq, (prev_priority + (1 / schedule_unit.speed), self.turn_id, unit_idx, schedule_unit))
        self.turn_id += 1
