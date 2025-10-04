import geopy
import mysql.connector
from dotenv import load_dotenv
import os
import random
import sql_queries
from player import Player
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="X")

load_dotenv()

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_DATABASE")
user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# This function performs database connection.
def connection_to_db():
    connection = mysql.connector.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=db_password,
        autocommit=True
    )
    return connection

connection = connection_to_db()
cursor = connection.cursor()

# This function ensures that new users are created and sent to the database.
def sign_up(username):
    player1 =Player(username)
    sql=sql_queries.post_user
    cursor.execute(sql, (player1.username, player1.co2_consumed, player1.plane_id, player1.balance))
    print("Registered successfully")
    return

# This function searches for the user in the users table and if it finds the user, it returns the login successful.
def sign_in(username):
    sql = sql_queries.get_usernames
    cursor.execute(sql)
    users = cursor.fetchall()

    user_list = [user[0] for user in users]

    if username in user_list:
        return "Login successful"
    else:
        return "Username is incorrect"

# This function allows the player to create a game according to the role she/he/it wants.
def create_player_role(username):
    player_role = input("Please enter your role : P = Pilot, S= Smuggler. ").strip().lower()
    if player_role == "p":
        create_a_game_for_pilot_role(username)
    elif player_role == "s":
        create_a_game_for_smuggler_role(username)
    else:
        print("You have made an invalid selection. Press P = Pilot, S= Smuggler")

# This function allows the player to create a game with the pilot role.
def create_a_game_for_pilot_role(username):
    game_name = input("Please enter your game name : ")
    plane_id=1
    player_role = "PILOT"

    plane=get_plane_by_plane_id(plane_id)
    current_fuel=plane[5]
    player = Player(username=username)

    co2_budget=player.co2_budget
    co2_consumed=player.co2_consumed
    user=get_user_by_username(username)

    user_id=user[0]
    post_game_to_game_for_pilot(
        user_id, username, game_name, player_role, plane_id, current_fuel, co2_budget, co2_consumed
    )

    country_identifier(game_name, player_role)

# This function allows the player to create a game with the smuggler role.
def create_a_game_for_smuggler_role(username):
    game_name = input("Please enter your game name : ")
    player_role = "SMUGGLER"
    user=get_user_by_username(username)
    user_id=user[0]
    post_game_to_game_for_smuggler(user_id, username, game_name, player_role)

    country_identifier(game_name, player_role)

# This function retrieves the player by username from the users table.
def get_user_by_username(username):
    sql= sql_queries.get_user_by_username
    cursor.execute(sql,(username,))
    result = cursor.fetchone()
    return result

# This function opens a game record in the table by sending the information generated according to the pilot role
# to the game table.
def post_game_to_game_for_pilot (user_id,username, game_name,player_role,plane_id,current_fuel,co2_budget,co2_consumed):
    sql= sql_queries.post_game_to_game_tbl_for_pilot
    cursor.execute(sql, (user_id,username, game_name,player_role,plane_id,current_fuel,co2_budget,co2_consumed))
    connection.commit()

# This function opens a game record in the table by sending the information generated according to the smuggler role
# to the game table.
def post_game_to_game_for_smuggler(user_id, username, game_name,player_role):
    sql= sql_queries.post_game_to_game_tbl_for_smuggler
    cursor.execute(sql, (user_id,username, game_name,player_role))
    connection.commit()

# This function returns the airport chosen from a list of 5 randomly selected airports in the desired country.
def choose_airport_for_arriving():
    country = input("Please select arrival country : ")
    iso_country = get_iso_country_code_by_country_name(country)
    airports=airports_for_arriving(iso_country)

    i=1
    for airport in airports:
        print(f" Press {i} for: {airport}")
        i+=1

    chosen_airport = int(input("Please select airport: "))
    while True:
        if 1 <= chosen_airport <= len(airports):
            return airports[chosen_airport - 1]
        chosen_airport = int(input("Please select from valid ranges: 1-5 "))

# This function randomly selects five airports in the desired country and returns them as a list.
def airports_for_arriving(iso_country):
    sql= sql_queries.get_airports_ident
    cursor.execute(sql,(iso_country,))
    result = cursor.fetchall()
    connection.commit()

    airports=[]
    for row in range(5):
        r_number = random.randint(0, len(result))
        airports.append(result[r_number][0])

    return airports

# This function finds the country the player wants from the country database and returns the iso_country code of the
# country.
def get_iso_country_code_by_country_name(country):
    sql= sql_queries.get_iso_country_by_country_name
    cursor.execute(sql, (country,))
    result = cursor.fetchone()[0]
    return result

# This function takes the number of passengers that the plane can carry according to the plane ID and determines the
# number of random passengers according to this amount.
def create_passenger(plane_id):
    sql=sql_queries.get_passenger_capacity_by_plane_id
    cursor.execute(sql,(plane_id,))
    result = cursor.fetchone()
    connection.commit()

    passenger_capacity=result[0]
    passenger_capacity=random.randint(1,passenger_capacity)
    return passenger_capacity

# This function allows the game's starting airport and city to be updated according to the player's chosen country
# and role.
def country_identifier(game_name,player_role):
    country_name = input("Country name: ")
    iso_code = identify_iso_country(country_name)
    airports = select_airports(iso_code)
    if player_role == "PILOT":
        icao_code=choose_three_options(airports)
        municipality=get_municipality_by_ident(icao_code)
        update_starting_location(icao_code, municipality, game_name)
    elif player_role == "SMUGGLER":
        icao_code = choose_three_options(airports)
        municipality = get_municipality_by_ident(icao_code)
        update_starting_location(None, municipality, game_name)

    #return icao_code

# This function determines the iso_code according to the country name.
def identify_iso_country(country_name):
    sql = sql_queries.get_iso_country_by_country_name
    cursor.execute(sql, (country_name,))
    row = cursor.fetchone()
    return row[0] if row else None

# This function randomly returns 3 of the airports in the country.
def select_airports(country_code):
    sql = sql_queries.get_airports_ident
    cursor.execute(sql, (country_code,))
    airports = cursor.fetchall()
    selection = []

    for _ in range(3):
        random_index = random.randint(0, len(airports) - 1)
        selection.append(airports[random_index])

    selection = [t[0] for t in selection]
    return selection

# This function gives the user 3 airports and allows her/him/its to choose one of them.
def choose_three_options(options):
    airports_list = []
    count = 1

    for option in options:
        airports_list.append(option)
        print(f"Press {count} if you want to choose {option}")
        count += 1

    chosen_index = int(input("Choose an airport by typing its number: "))
    chosen_icao = airports_list[chosen_index - 1]

    return chosen_icao

# This function updates the airport and city according to the game name.
def update_starting_location(icao_code, municipality, game_name):
    sql = sql_queries.update_game_airport_municipality
    cursor.execute(sql, (icao_code, municipality, game_name))

# This function returns the city where the airport is located based on the airport code.
def get_municipality_by_ident(ident):
    sql = sql_queries.get_municipality_by_ident
    cursor.execute(sql,(ident,))
    row = cursor.fetchone()
    return row[0] if row else None

# This function allows the user to view existing games and select one or create a new game.
def player_selection(username):
    player_choice = int(input("Press 1 to view your games, or 2 for a new game.\n"))
    user_id = (get_user_by_username(username))[0]

    if player_choice == 1:
        print("=== Your saved games === ")
        get_games_by_user_id(user_id)
        return get_game_to_be_chosen()
    elif player_choice == 2:
        print("You are starting a new game. ")
        player_role = input("Please enter your role : P = Pilot, S= Smuggler. ").strip().lower()
        if player_role == "p":
            create_a_game_for_pilot_role(username)
            get_games_by_user_id(user_id)
            return get_game_to_be_chosen()
        elif player_role == "s":
            create_a_game_for_smuggler_role(username)
            get_games_by_user_id(user_id)
            return get_game_to_be_chosen()

# This function returns the user's saved games based on their id number.
def get_games_by_user_id(user_id):
    connection = connection_to_db()
    sql=sql_queries.get_games_by_user_id
    cursor = connection.cursor()
    cursor.execute(sql, (user_id,))
    result = cursor.fetchall()

    for game in result:
        print(f"{game[1]} - {game[4]}")
    return result

# This function allows the user to select one of her saved games based on her/him/its user id.
def get_game_to_be_chosen():
    game_to_be_chosen = input("\nWhich game would you like to play? Write its name : ")
    chosen_game = get_game_by_game_name(game_to_be_chosen)
    return chosen_game

# This function returns the game selected by the user based on the game name.
def get_game_by_game_name(game_name):
    sql=sql_queries.get_game_by_game_name
    cursor.execute(sql, (game_name,))
    result = cursor.fetchone()
    return result

# This function returns aircraft information based on plane id.
def get_plane_by_plane_id(plane_id):
    sql=sql_queries.get_plane_by_plane_id
    cursor.execute(sql, (plane_id,))
    result = cursor.fetchone()
    return result

# This function will allow the game to be played and the data to be updated.
def start_game(chosen_game):
    plane=get_plane_by_plane_id(chosen_game[6])
    tank_capacity=plane[4]
    refueling=plane[8]
    departure_airport=chosen_game[7]
    arrival_airport_ident = choose_airport_for_arriving()
    km=get_km_by_ident(departure_airport, arrival_airport_ident)

    print("\nKM :", km)

# This function calculates the distance from the user's departure location to the destination.
def get_km_by_ident(ident_1, ident_2):
    sql_1 = sql_queries.get_locations_by_ident
    cursor.execute(sql_1, (ident_1,))
    result_1 = cursor.fetchone()

    if result_1 is None:
        print(f"Invalid ICAO code: {ident_1}")
        return None

    location_1 = (result_1[0], result_1[1])

    sql_2 = sql_queries.get_locations_by_ident
    cursor.execute(sql_2, (ident_2,))
    result_2 = cursor.fetchone()

    if result_2 is None:
        print(f"Invalid ICAO code: {ident_2}")
        return None

    location_2 = (result_2[0], result_2[1])

    if result_1 and result_2:
        km = geopy.distance.geodesic(location_1, location_2).kilometers
        km = round(km, 2)
        return km
    else:
        print("Invalid ICAO codes provided!")
        return None