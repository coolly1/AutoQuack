from UI import ui
from Units import load_unit
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
        training_state = -1
        training_count = 3
        while(training_state != 0):


            training_state, unit = UI.show_training()
            training_count -= 1
            match training_state:
                case 1:
                    UI.minigame_1(unit)
                case 2:
                    UI.minigame_2(unit)
                case 3:
                    UI.minigame_3(unit)
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