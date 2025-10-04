import utilities

sign_option = int(input("Enter 1 to sign up or 2 for existing player: "))
username = input("Enter your username : ").strip()

if sign_option == 1:
    utilities.sign_up(username)
    player_role=input("Please enter your role : P = Pilot, S= Smuggler. ").strip().lower()

    if player_role == "p":
        utilities.create_a_game_for_pilot_role(username)

    elif player_role == "s":
        utilities.create_a_game_for_smuggler_role(username)

elif sign_option == 2:
    check_login=utilities.sign_in(username)
    print(check_login,"\n")

    if check_login == "Login successful":
        chosen_game=utilities.player_selection(username)
        #chosen_game_id=chosen_game[0]
        player_role=chosen_game[4]
        game_option = input("Do you want to start the game? (Y/N)\n").lower().strip()
        if game_option == "y" and player_role == "PILOT":
            utilities.start_game(chosen_game)
            print("It will be continue from here...")
