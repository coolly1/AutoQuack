MAX_TURNS = 100

from Units import unit
import heapq

enemy_lists = []

class battler():
    # this is used to prevent ties
    turn_id: int
    turn_order_pq: list
    player_team: list

    def __init__(self, player_team: list):
        self.player_team = player_team

    def start_battle(self, round_idx) -> bool:
        """

        :return: bool if player won or loss
        """

        self.turn_id = 0
        self.turn_order_pq =[]

        # get the enemies
        enemy_team: list[unit] = []

        # add player, and enemy
        for player_unit in self.player_team:
            self.schedule_unit(player_unit, 0.0)

        for enemy_unit in enemy_team:
            self.schedule_unit(enemy_unit, 0.0)



        for turn_order in range(MAX_TURNS):
            (time, turn_id, next_unit) = heapq.heappop(self.turn_order_pq)

            active_unit:unit = next_unit

            # if unit is dead then continue
            if(active_unit.current_health <= 0):
                continue

            active_unit.execute_turn()


    def schedule_unit(self, schedule_unit, prev_priority):
        heapq.heappush(self.turn_order_pq, (prev_priority + (1 / schedule_unit.speed), self.turn_id, schedule_unit))
        self.turn_id += 1
