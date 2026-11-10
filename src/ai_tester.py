from Units import *
from battler import battler

import copy
import heapq
import time


CLASSES = [
    "../data/cleric.csv",
    "../data/rogue.csv",
    "../data/mage.csv",
    "../data/knight.csv",
]

AVG_TRAINING = 10
BEAM_WIDTH = 20
TRAINING_ITERATIONS = 100
NUMBER_OF_BEST_TEAMS = 16


class Team:
    def __init__(self, team, self_copy=None):
        if self_copy is not None:
            # A copied Team must have independent UNIT objects. Otherwise,
            # training one Team can accidentally change another Team.
            self.team = copy.deepcopy(self_copy.team)

            self.num_training = self_copy.num_training
            self.num_strength = self_copy.num_strength.copy()
            self.num_magic = self_copy.num_magic.copy()
            self.num_health = self_copy.num_health.copy()
            self.num_agility = self_copy.num_agility.copy()

            # Preserve all alternative cumulative allocations.
            self.beam = copy.deepcopy(self_copy.beam)
        else:
            self.team = team

            self.num_strength = [0, 0, 0, 0]
            self.num_magic = [0, 0, 0, 0]
            self.num_health = [0, 0, 0, 0]
            self.num_agility = [0, 0, 0, 0]

            self.num_training = 0

            # Each beam entry is (complete_allocation, score).
            # Allocation order for each unit is HP, ATK, SPD, SPK.
            self.beam = [([0] * 16, float("-inf"))]

    def apply_trainings(self, scale):
        """Apply or undo this Team's cumulative training to its UNIT objects."""
        for unit_idx in range(len(self.team)):
            self.team[unit_idx].train(
                TRAINABLE_STAT.HP,
                scale * self.num_health[unit_idx],
            )
            self.team[unit_idx].train(
                TRAINABLE_STAT.ATK,
                scale * self.num_strength[unit_idx],
            )
            self.team[unit_idx].train(
                TRAINABLE_STAT.SPD,
                scale * self.num_agility[unit_idx],
            )
            self.team[unit_idx].train(
                TRAINABLE_STAT.SPK,
                scale * self.num_magic[unit_idx],
            )

    def find_team_score(self, opponents):
        """
        Score this Team against the supplied opponents.

        Training is applied temporarily and undone even if a battle raises
        an exception. The Team's stored allocation arrays are not modified.
        """
        self.apply_trainings(AVG_TRAINING)

        try:
            team_battler = battler(player_team=self.team, gui=None)
            score = 0.0

            for opponent in opponents:
                # Avoid a team fighting itself when the same Team object is
                # present in both the candidate list and opponent list.
                if opponent is self:
                    continue

                opponent.apply_trainings(AVG_TRAINING)
                try:
                    score += team_battler.start_battle(1, opponent.team)
                finally:
                    opponent.apply_trainings(-AVG_TRAINING)

            return score
        finally:
            self.apply_trainings(-AVG_TRAINING)

    @staticmethod
    def allocation_to_arrays(allocation):
        """
        Convert a 16-element allocation into the four per-unit arrays.

        Slot order:
            unit 0: HP, ATK, SPD, SPK
            unit 1: HP, ATK, SPD, SPK
            unit 2: HP, ATK, SPD, SPK
            unit 3: HP, ATK, SPD, SPK
        """
        if len(allocation) != 16:
            raise ValueError(
                f"Expected 16 allocation values, received {len(allocation)}"
            )

        health = [allocation[i * 4] for i in range(4)]
        strength = [allocation[i * 4 + 1] for i in range(4)]
        agility = [allocation[i * 4 + 2] for i in range(4)]
        magic = [allocation[i * 4 + 3] for i in range(4)]

        return health, strength, agility, magic

    def evaluate_allocation(self, allocation, opponents):
        """
        Evaluate a complete cumulative allocation without committing it.

        The allocation is absolute (total points per slot), not an increment.
        """
        old_health = self.num_health
        old_strength = self.num_strength
        old_agility = self.num_agility
        old_magic = self.num_magic

        (
            self.num_health,
            self.num_strength,
            self.num_agility,
            self.num_magic,
        ) = self.allocation_to_arrays(allocation)

        try:
            return self.find_team_score(opponents)
        finally:
            self.num_health = old_health
            self.num_strength = old_strength
            self.num_agility = old_agility
            self.num_magic = old_magic

    def set_allocation(self, allocation):
        """Commit a complete cumulative allocation to this Team."""
        (
            self.num_health,
            self.num_strength,
            self.num_agility,
            self.num_magic,
        ) = self.allocation_to_arrays(allocation)

        self.num_training = sum(allocation)

    def __str__(self):
        result = ""

        for unit_idx, unit in enumerate(self.team):
            unit_type = unit.path.strip().split("/")[-1]
            result += (
                f"{unit_type} "
                f"[HP:{self.num_health[unit_idx]},"
                f"ATK:{self.num_strength[unit_idx]},"
                f"SPD:{self.num_agility[unit_idx]},"
                f"SPK:{self.num_magic[unit_idx]}]\n"
            )

        result += f"Total training: {self.num_training}\n"
        return result


def beam_search(team, opponents, beam_width=BEAM_WIDTH):
    """
    Spend exactly one additional training point.

    The Team's beam stores complete cumulative allocations, so alternative
    training histories survive between calls to this function.
    """
    candidates = {}

    for allocation, _ in team.beam:
        for slot_idx in range(16):
            new_allocation = allocation.copy()
            new_allocation[slot_idx] += 1

            key = tuple(new_allocation)

            # Different parent candidates can produce the same allocation.
            if key in candidates:
                continue

            score = team.evaluate_allocation(new_allocation, opponents)
            candidates[key] = (new_allocation, score)

    if not candidates:
        raise RuntimeError("Beam search produced no candidate allocations")

    # Keep the highest-scoring distinct cumulative allocations.
    team.beam = heapq.nlargest(
        beam_width,
        candidates.values(),
        key=lambda candidate: candidate[1],
    )

    # The Team's visible/current allocation is the best member of the beam.
    best_allocation, best_score = team.beam[0]
    team.set_allocation(best_allocation)

    return best_score


def find_best_teams(teams, number_teams):
    """Return the highest-scoring teams, ordered from lowest to highest."""
    team_scores = []

    for team_idx, team in enumerate(teams):
        score = team.find_team_score(teams)

        heapq.heappush(team_scores, (score, team_idx, team))

        if len(team_scores) > number_teams:
            heapq.heappop(team_scores)

    best_teams = []

    while team_scores:
        _, _, team = heapq.heappop(team_scores)
        best_teams.append(team)

    return best_teams


def apply_iteration_of_training(best_teams, unique_teams):
    """
    Advance every Team by one training point.

    First, make independently trained copies of the current best teams.
    Those copies are then used as opponents while training all unique teams.
    """
    copy_best_teams = [
        Team(None, best_team)
        for best_team in best_teams
    ]

    start_time = time.time()

    for copy_best in copy_best_teams:
        beam_search(
            copy_best,
            best_teams,
            beam_width=BEAM_WIDTH,
        )

    print("Best Train Time:", time.time() - start_time)

    start_time = time.time()

    for team in unique_teams:
        beam_search(
            team,
            copy_best_teams,
            beam_width=BEAM_WIDTH,
        )

    print("Unique Train Time:", time.time() - start_time)

    start_time = time.time()

    best_teams = find_best_teams(
        unique_teams,
        NUMBER_OF_BEST_TEAMS,
    )

    print("Find Best Time:", time.time() - start_time)

    return best_teams, unique_teams


def main():
    unique_teams = []

    # Generate all 4^4 ordered team compositions.
    for idx_1 in range(len(CLASSES)):
        for idx_2 in range(len(CLASSES)):
            for idx_3 in range(len(CLASSES)):
                for idx_4 in range(len(CLASSES)):
                    units = [
                        load_unit(CLASSES[idx_1]),
                        load_unit(CLASSES[idx_2]),
                        load_unit(CLASSES[idx_3]),
                        load_unit(CLASSES[idx_4]),
                    ]

                    unique_teams.append(Team(units))

    start_time = time.time()
    best_teams = find_best_teams(
        unique_teams,
        NUMBER_OF_BEST_TEAMS,
    )
    print("Initial team evaluation time:", time.time() - start_time)

    print("\nInitial Best Teams")
    for best_idx, best_team in enumerate(reversed(best_teams)):
        print(f"Team_idx {best_idx}")
        print(best_team)

    for training_idx in range(TRAINING_ITERATIONS):
        best_teams, unique_teams = apply_iteration_of_training(
            best_teams,
            unique_teams,
        )

        print(f"\nBest Teams after training level {training_idx + 1}")
        for best_idx, best_team in enumerate(reversed(best_teams)):
            print(f"Team_idx {best_idx}")
            print(best_team)


if __name__ == "__main__":
    main()
