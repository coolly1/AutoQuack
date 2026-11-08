from UI import ui
from Units import load_unit, TRAINABLE_STAT
from battler import battler

MAX_ROUNDS = 3

def main():
    
    # pick ducks screens
    UI = ui()
    
    while True:
        UI.main_menu()

        UI.instruction_menu()

        classes = [load_unit("../data/cleric.csv"), 
                load_unit("../data/rogue.csv"),
                load_unit("../data/mage.csv"), 
                load_unit("../data/knight.csv")]
        
        player = UI.select_units(classes)
        
        #init_player
        # player = [load_unit("../data/cleric.csv"), 
        #           load_unit("../data/rogue.csv"),
        #           load_unit("../data/mage.csv"), 
        #           load_unit("../data/knight.csv")]

        # show start screen
        


        battler_obj = battler(player, UI)
        win = True

        for round_num in range(MAX_ROUNDS):
            # reset unit damage and charge

        # show training, training_state = 0 exit
            training_count = 3
            for train_number in range(training_count):
                training_state, unit = UI.show_training(training_count - train_number)
                match training_state:
                    case 1:
                        score = UI.minigame_4(unit)
                    case 2:
                        score = UI.minigame_1(unit)
                    case 3:
                        score = UI.minigame_3(unit)
                    case 4:
                        score = UI.minigame_2(unit)
                    case 0:
                        break

                # w
            win = battler_obj.start_battle(round_num)
            if(not win):
                break
        UI.show_end_screen(win);
        UI.player = []

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