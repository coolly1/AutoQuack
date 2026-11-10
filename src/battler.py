MAX_TURNS = 200

from Units import UNIT, TARGET, load_unit, TRAINABLE_STAT
from UI import ui
import heapq
import random

SEED_RAND = 0

enemy_lists = []

class battler():
    # this is used to prevent ties
    turn_id: int
    turn_order_pq: list[(float, int, int, UNIT)]
    player_team: list[UNIT]
    units: list[UNIT]
    GUI: ui

    def __init__(self, player_team: list, gui: ui | None):
        self.player_team = player_team
        self.gui = gui
        random.seed(SEED_RAND)

    def get_enemy_list(self, round_idx: int) -> list[UNIT]:
        average_score = 8
        match round_idx:
            case 0:
                 enemy = [load_unit("../data/cleric.csv"), load_unit("../data/cleric.csv"),
                          load_unit("../data/knight.csv"), load_unit("../data/mage.csv")]
                 enemy[2].train(TRAINABLE_STAT.SPD, average_score)
                 enemy[2].train(TRAINABLE_STAT.ATK, average_score)
                 enemy[0].train(TRAINABLE_STAT.HP, average_score)
                 enemy[3].train(TRAINABLE_STAT.HP, average_score)
                 return enemy
            case 1:
                enemy = [load_unit("../data/knight.csv"), load_unit("../data/cleric.csv"),
                         load_unit("../data/cleric.csv"), load_unit("../data/knight.csv")]
                return enemy
            case 2:
                enemy = [load_unit("../data/knight.csv"), load_unit("../data/rogue.csv"),
                         load_unit("../data/cleric.csv"), load_unit("../data/mage.csv")]
                return enemy

    def start_battle(self, round_idx: int, enemy_team: list[UNIT]) -> bool:
        """
        :return: bool if player won or loss
        """

        # get the enemies
        if(enemy_team == []):
            enemy_team = self.get_enemy_list(round_idx)

        self.turn_id = 0
        self.turn_order_pq =[]
        self.units = self.player_team + enemy_team

        fronts = [3, 0]
        backs = [0, 3]

        teams = [self.player_team, enemy_team]

        # add player, and enemy
        for unit_idx in range(len(self.units)):
            self.schedule_unit(unit_idx, 0.0)
            self.units[unit_idx].reset_for_battle()

        for turn_order in range(MAX_TURNS):
            prev_priority, turn_id, active_unit_idx = heapq.heappop(self.turn_order_pq)

            # if UNIT is dead then continue
            if(self.units[active_unit_idx].is_dead()):
                continue

            (damage, target, is_self, is_special) = self.units[active_unit_idx].execute_turn()

            # what team we are targeting
            target_team: int

            if(is_self):
                target_team = active_unit_idx >= 4
            else:
                target_team = active_unit_idx < 4

            # find effected units
            affected_units: list[UNIT] = []

            match target:
                case TARGET.FRONT:
                    affected_units.append(teams[target_team][fronts[target_team]])
                    # print(f"Duck Idx {active_unit_idx} dealt to {fronts[target_team] + target_team * 4} idx, health was {teams[target_team][fronts[target_team]].current_health}")
                case TARGET.BACK:
                    affected_units.append(teams[target_team][backs[target_team]])
                case TARGET.SELF:
                    affected_units.append(teams[target_team][active_unit_idx % 4])
                case TARGET.RANDOM:
                    while(True):
                        target = random.randint(0, 3)
                        if(teams[target_team][target].is_dead()):
                            continue

                        affected_units.append(teams[target_team][target])
                        break
                case TARGET.TEAM:
                    for unit_idx in range(4):
                        affected_units.append(teams[target_team][unit_idx])
                case TARGET.ALL:
                    for team_idx in range(2):
                        for unit_idx in range(4):
                            affected_units.append(teams[team_idx][unit_idx])
                case _:
                    print("BAD")

            
            # call GUI
            if(self.gui):
                self.gui.show_battle(active_unit_idx, affected_units, is_special, enemy_team)
            
            # apply effects
            for unit in affected_units:
                unit.apply_damage(damage)

            # check if player alive and adjust pointers
            team_idx = 0
            while(teams[team_idx][fronts[team_idx]].is_dead()):
                fronts[team_idx] -= 1
                if(fronts[team_idx] < backs[team_idx]):
                    # print(team_idx == 1)
                    return team_idx == 1

            while(teams[team_idx][backs[team_idx]].is_dead()):
                backs[team_idx] += 1

            team_idx = 1
            # check if enemy alive and adjust pointers
            while(teams[team_idx][fronts[team_idx]].is_dead()):
                fronts[team_idx] += 1
                if(fronts[team_idx] > backs[team_idx]):
                    # print(team_idx == 1)
                    return team_idx == 1

            while(teams[team_idx][backs[team_idx]].is_dead()):
                backs[team_idx] -= 1


            # schedule the unit again
            self.schedule_unit(active_unit_idx, prev_priority=prev_priority)

        return False

    def schedule_unit(self, unit_idx, prev_priority):

        unit = self.units[unit_idx]
        heapq.heappush(self.turn_order_pq, (prev_priority + (1 / unit.speed), self.turn_id, unit_idx))
        self.turn_id += 1
