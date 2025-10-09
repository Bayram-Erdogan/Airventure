import datetime
import utilities
import pilot_role
import smuggler_role
import sql_queries
from player import Player
from utilities import connection_to_db

connection = connection_to_db()
cursor = connection.cursor(buffered=True)

sign_option = int(input("Enter 1 to sign up or 2 for existing player: "))

# This function ensures that new users are created and sent to the database.
def sign_up(username):
    sql = sql_queries.get_user_id_by_username
    cursor.execute(sql, (username,))
    user = cursor.fetchone()

    if user:
        return False
    else:
        player1 =Player(username)
        sql=sql_queries.post_user
        cursor.execute(sql, (player1.username, player1.co2_consumed, player1.plane_id, player1.balance))
        print("Registered successfully")
        return True

# This function searches for the user in the users table and if it finds the user, it returns the login successful.
def sign_in(username):
    sql = sql_queries.get_user_id_by_username
    cursor.execute(sql, (username,))
    user= cursor.fetchone()

    if user:
        user_id = user[0]
        now = datetime.datetime.now()
        last_login = sql_queries.update_user_last_login
        cursor.execute(last_login, (now, user_id))
        return "Login successful"
    else:
        return "Username is incorrect"

# This function regulates the game flow after the user successfully enters the game.
def login_successfully(username):
    chosen_game =player_selection(username)
    player_role = chosen_game[4]

    while True:
        game_option = input("Do you want to start the game? (Y/N)\n").lower().strip()
        if game_option == "y":
            if player_role == "PILOT":
                chosen_game = utilities.get_game_by_game_id(chosen_game[0])
                pilot_role.start_game(chosen_game)
            elif player_role == "SMUGGLER":
                chosen_game = utilities.get_game_by_game_id(chosen_game[0])
                smuggler_role.start_for_smuggler(chosen_game[0], chosen_game[5])
            else:
                print(f"Game start logic for role {player_role} not implemented yet.")
                break
        elif game_option == "n":
            print("You chose not to start the game. Exiting.")
            break
        else:
            print("Invalid input. Please enter Y or N.")

# This function allows the user to view existing games and select one or create a new game.
def player_selection(username):
    player_choice = int(input("Press 1 to view your games, or 2 for a new game.\n"))
    user_id = (utilities.get_user_by_username(username))[0]

    if player_choice == 1:
        print("=== Your saved games === ")
        utilities.get_games_by_user_id(user_id)
        return utilities.get_game_to_be_chosen()
    elif player_choice == 2:
        print("You are starting a new game. ")
        player_role = input("Please enter your role : P = Pilot, S= Smuggler. ").strip().lower()
        if player_role == "p":
            pilot_role.create_a_game_for_pilot_role(username)
            utilities.get_games_by_user_id(user_id)
            return utilities.get_game_to_be_chosen()
        elif player_role == "s":
            smuggler_role.create_a_game_for_smuggler_role(username)
            utilities.get_games_by_user_id(user_id)
            return utilities.get_game_to_be_chosen()

if sign_option == 1:
    while True:
        username = input("Enter your username: ").strip()
        registered_successfully = sign_up(username)
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
        pilot_role.create_a_game_for_pilot_role(username)
    else:
        smuggler_role.create_a_game_for_smuggler_role(username)

    continue_game_choice = input("Would you like to continue to the game now? (y/n): ").lower()
    if continue_game_choice == "y":
        login_successfully(username)
    else:
        print("You chose not to start the game. Exiting.")
elif sign_option == 2:
    username = input("Enter your username : ").strip()
    check_login=sign_in(username)

    if check_login == "Login successful":
        login_successfully(username)

# This function allows the player to create a game according to the role she/he/it wants.
def create_player_role(username):
    player_role = input("Please enter your role : P = Pilot, S= Smuggler. ").strip().lower()
    if player_role == "p":
        pilot_role.create_a_game_for_pilot_role(username)
    elif player_role == "s":
        smuggler_role.create_a_game_for_smuggler_role(username)
    else:
        print("You have made an invalid selection. Press P = Pilot, S= Smuggler")