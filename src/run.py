import utilities

sign_option = int(input("Enter 1 to sign up or 2 for existing player: "))

if sign_option == 1:
    while True:
        username = input("Enter your username: ").strip()
        registered_successfully = utilities.sign_up(username)
        if registered_successfully:
            break
        else:
            print("Username already exists. Please try a different one.")

    player_role = None
    while player_role not in ("p", "s"):
        player_role = input("Please enter your role: P = Pilot, S = Smuggler: ").strip().lower()
        if player_role not in ("p", "s"):
            print("Invalid role. Please enter P or S.")

    if player_role == "p":
        utilities.create_a_game_for_pilot_role(username)
    else:
        utilities.create_a_game_for_smuggler_role(username)

    continue_game_choice = input("Would you like to continue to the game now? (y/n): ").lower()
    if continue_game_choice == "y":
        utilities.login_successfully(username)
    else:
        print("You chose not to start the game. Exiting.")

elif sign_option == 2:
    username = input("Enter your username : ").strip()
    check_login=utilities.sign_in(username)

    if check_login == "Login successful":
        utilities.login_successfully(username)