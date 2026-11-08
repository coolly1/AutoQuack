from UI import ui
from Units import load_unit, TRAINABLE_STAT
from battler import battler

MAX_ROUNDS = 3

def main():
    
    # pick ducks screens

    #init_player
    player = [load_unit("../data/cleric.csv"), 
              load_unit("../data/rogue.csv"),
              load_unit("../data/mage.csv"), 
              load_unit("../data/knight.csv")]

    # show start screen
    UI = ui(player)
    UI.main_menu()


    battler_obj = battler(player, UI)

    for round_num in range(MAX_ROUNDS):
        # reset unit damage and charge

        # show training, training_state = 0 exit
        training_count = 3
        for train_number in range(training_count):
            training_state, unit = UI.show_training()
            match training_state:
                case 1:
                    score = UI.minigame_4(unit)
                    player[unit].train(TRAINABLE_STAT.HP, score)
                case 2:
                    score = UI.minigame_1(unit)
                    player[unit].train(TRAINABLE_STAT.ATK, score)
                case 3:
                    score = UI.minigame_3(unit)
                    player[unit].train(TRAINABLE_STAT.SPD, score)
                case 4:
                    score = UI.minigame_2(unit)
                    player[unit].train(TRAINABLE_STAT.SPK, score)
                case 0:
                    break

        # w
        battler_obj.start_battle(round_num)

    # show training, a

if __name__ == '__main__':
    main()



# player
# - team
# - set_training
# -
# parties


# start
# show home
# wait for user input
# if start show training screen

# training screen
# wait 