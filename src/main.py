from UI import ui
MAX_ROUNDS = 2

def main():
    pass

    # show start screen
    UI = ui()
    UI.main_menu()

    #init_player
    
    round_num = 0
    for round_num in range(MAX_ROUNDS):
        # reset unit damage and charge

        # show training
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