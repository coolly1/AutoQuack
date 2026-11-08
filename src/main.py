from UI import ui
from Units import UNIT, TARGET, SPECIAL
from battler import battler

MAX_ROUNDS = 2

def main():


    # show start screen
    UI = ui()
    UI.main_menu()

    # pick ducks screens

    #init_player
    #player = [load_unit("file1"), load_unit("file2"), load_unit("file3"), load_unit("file4")]

    #battler = battler(ui, player)

    for round_num in range(MAX_ROUNDS):
        # reset unit damage and charge

        # show training, training_state = 0 exit
        training_state = -1
        while(training_state != 0):


            training_state, unit = UI.show_training()
            if training_state >= 1 and training_state <= 4:
                # train unit
                print("Training unit " + str(unit) + " with training state: " + str(training_state))
                pass
        pass
        # w

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