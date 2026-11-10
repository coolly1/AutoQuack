from Units import *
from battler import battler
import heapq
import time

classes = ["../data/cleric.csv",
           "../data/rogue.csv",
           "../data/mage.csv",
           "../data/knight.csv"]


AVG_TRAINING = 8

class Team():
    num_strength: list
    num_agility: list
    num_health: list
    num_magic: list
    team: list[UNIT]
    num_training: int
    def __init__(self, team, self_copy):
        if(self_copy):
            self.team = self_copy.team
            self.num_training = self_copy.num_training

            self.num_strength = []
            self.num_magic =    []
            self.num_health =   []
            self.num_agility =  []
            for unit_idx in range(len(self.team)):
                self.num_strength.append(self_copy.num_strength[unit_idx])
                self.num_magic.append(self_copy.num_magic[unit_idx])
                self.num_health.append(self_copy.num_health[unit_idx])
                self.num_agility.append(self_copy.num_agility[unit_idx])

        else:
            self.team = team
            self.num_strength = [0,0,0,0]
            self.num_magic =    [0,0,0,0]
            self.num_health =   [0,0,0,0]
            self.num_agility =  [0,0,0,0]
            self.num_training = 0

    def apply_trainings(self, scale):
        for unit_idx in range(len(self.team)):
            self.team[unit_idx].train(TRAINABLE_STAT.HP, scale*self.num_health[unit_idx])
            self.team[unit_idx].train(TRAINABLE_STAT.ATK, scale*self.num_strength[unit_idx])
            self.team[unit_idx].train(TRAINABLE_STAT.SPD, scale*self.num_agility[unit_idx])
            self.team[unit_idx].train(TRAINABLE_STAT.SPK, scale*self.num_magic[unit_idx])

    def find_team_score(self, best_teams):
        self.apply_trainings(AVG_TRAINING)

        team_battler = battler(player_team=self.team, gui=None)
        score = 0.0
        for opponent in best_teams:
            opponent.apply_trainings(AVG_TRAINING)
            score += team_battler.start_battle(1, opponent.team) * 1
            opponent.apply_trainings(-AVG_TRAINING)

        self.apply_trainings(-AVG_TRAINING)
        return score

    def find_best_training(self, best_teams):
        self.num_training += 1
        team_idx = 0
        team_scores = []

        for unit_idx in range(len(self.team)):
            for stat in TRAINABLE_STAT:
                self.team[unit_idx].train(stat, AVG_TRAINING)
                team_idx += 1

                score = self.find_team_score(best_teams)

                heapq.heappush(team_scores, (score, team_idx, unit_idx, stat))

                if (len(team_scores) > 1):
                    heapq.heappop(team_scores)
                self.team[unit_idx].train(stat, -AVG_TRAINING)

        score, team_idx, unit_idx, stat = heapq.heappop(team_scores)
        if(stat == TRAINABLE_STAT.HP):
            self.num_health[unit_idx] += 1
        if(stat == TRAINABLE_STAT.SPD):
            self.num_agility[unit_idx] += 1
        if(stat == TRAINABLE_STAT.ATK):
            self.num_strength[unit_idx] += 1
        if(stat == TRAINABLE_STAT.SPK):
            self.num_magic[unit_idx] += 1

    def __str__(self):
        result = ""
        for unit_idx in range(len(self.team)):
            type = self.team[unit_idx].path.strip().split("/")[-1]
            result = result + f"{type} [HP:{self.num_health[unit_idx]},ATK:{self.num_strength[unit_idx]},SPD:{self.num_agility[unit_idx]},SPK:{self.num_magic[unit_idx]}]\n"
        return result


def find_best_teams(teams: list[Team], number_teams) -> list[Team]:
    team_scores = []
    team_idx = 0
    for team in teams:
        team_idx += 1

        score = team.find_team_score(teams)

        heapq.heappush(team_scores, (score, team_idx, team))

        if(len(team_scores) > number_teams):
            heapq.heappop(team_scores)

    best_teams = []

    while team_scores:
        score, team_idx, team = heapq.heappop(team_scores)
        best_teams.append(team)

    return best_teams


def apply_iteration_of_training(best_teams, unique_teams):
    # copy best teams
    copy_best_teams = []
    for best_team in best_teams:
        copy_best_teams.append(Team(None, best_team))

    start_time = time.time()

    # train the copy best team
    for copy_best in copy_best_teams:
        copy_best.find_best_training(best_teams)

    end_time = time.time()
    print("Best Train Time")
    print(end_time-start_time)
    start_time = time.time()

    # train all of the teams with the copy trained team
    for team in unique_teams:
        team.find_best_training(copy_best_teams)

    end_time = time.time()
    print("Unique Train Time")
    print(end_time-start_time)
    start_time = time.time()

    # find the new best
    best_teams = find_best_teams(unique_teams, 16)

    end_time = time.time()
    print("Find Best Time")
    print(end_time-start_time)

    return (best_teams,unique_teams)
def main():
    unique_teams = []
    for idx_1 in range(len(classes)):
        for idx_2 in range(len(classes)):
            for idx_3 in range(len(classes)):
                for idx_4 in range(len(classes)):
                    units = [load_unit(classes[idx_1]), load_unit(classes[idx_2]),
                            load_unit(classes[idx_3]), load_unit(classes[idx_4])]
                    team = Team(units, None)
                    unique_teams.append(team)

    start_time = time.time()
    best_teams = find_best_teams(unique_teams, 16)
    end_time = time.time()
    print(end_time-start_time)

    print("Best Teams")
    for best_idx in range(len(best_teams)):
        print("Team_idx" + str(best_idx))
        best_team = best_teams[-1 - best_idx]
        print(best_team)

    for round_idx in range(3):
        for training_idx in range(3):
            best_teams, unique_teams = apply_iteration_of_training(best_teams, unique_teams)

            print(f"Best Teams at round: {round_idx}, training: {training_idx}")
            for best_idx in range(len(best_teams)):
                print("Team_idx" + str(best_idx))
                best_team = best_teams[-1 - best_idx]
                print(best_team)


if __name__ == '__main__':
    main()