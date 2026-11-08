from UI import ui
from Units import load_unit
from battler import battler

MAX_ROUNDS = 2

def main():


    # show start screen
    UI = ui()
    UI.main_menu()

    # pick ducks screens

    #init_player
    player = [load_unit("../data/mega_peasant.csv"), load_unit("../data/peasant.csv"),
              load_unit("../data/peasant.csv"), load_unit("../data/peasant.csv")]

    battler_obj = battler(player, UI)

    for round_num in range(MAX_ROUNDS):
        # reset unit damage and charge

        # show training, training_state = 0 exit
        training_state = -1
        while(training_state != 0):


            training_state, unit = UI.show_training()
            match training_state:
                case 1:
                    UI.minigame_1(unit)
                
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