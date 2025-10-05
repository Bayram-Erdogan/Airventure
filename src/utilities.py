import datetime
import time
import geopy
import mysql.connector
from dotenv import load_dotenv
import os
import random
import sql_queries
from assets import country_flags
from player import Player
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from decimal import Decimal

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

    update_user_plane_id(plane_id,user_id)

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

# This function opens a game record in the table by sending the information generated according to the smuggler role
# to the game table.
def post_game_to_game_for_smuggler(user_id, username, game_name,player_role):
    sql= sql_queries.post_game_to_game_tbl_for_smuggler
    cursor.execute(sql, (user_id,username, game_name,player_role))

def update_user_plane_id(plane_id, user_id):
    sql= sql_queries.update_user_plane_id
    cursor.execute(sql, (plane_id,user_id,))

def login_successfully(username):
    chosen_game =player_selection(username)
    player_role = chosen_game[4]

    while True:
        game_option = input("Do you want to start the game? (Y/N)\n").lower().strip()
        if game_option == "y":
            if player_role == "PILOT":
                chosen_game = get_game_by_game_id(chosen_game[0])
                start_game(chosen_game)
            elif player_role == "SMUGGLER":
                print("It will continue from here...")
            else:
                print(f"Game start logic for role {player_role} not implemented yet.")
                break
        elif game_option == "n":
            print("You chose not to start the game. Exiting.")
            break
        else:
            print("Invalid input. Please enter Y or N.")

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
    sql=sql_queries.get_games_by_user_id
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

def get_game_by_game_id(game_id):
    sql=sql_queries.get_game_by_game_id
    cursor.execute(sql, (game_id,))
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

    departure_airport = get_departure_airport_ident_by_game_id(chosen_game[0])
    arrival_airport_ident = choose_airport_for_arriving()

    departure_country = get_iso_country_by_airport_ident(departure_airport)
    arrival_country = get_iso_country_by_airport_ident(arrival_airport_ident)

    departure_airport_name = (get_airport_by_ident(departure_airport))[0]
    arrival_airport_name = (get_airport_by_ident(arrival_airport_ident))[0]
    arrival_municipality = (get_municipality_by_ident(arrival_airport_ident)
                            )
    km=get_km_by_ident(departure_airport, arrival_airport_ident)
    current_fuel = (get_current_fuel_by_game_id(chosen_game[0]))
    passenger_count=create_passenger(plane[0])

    ticket_price=get_ticket_price_by_plane_id(plane[0])
    step_distance = 125
    step_time = 1

    revenue = passenger_count * ticket_price
    weather_factor, weather_condition = get_weather()
    co2_consumed, co2_budget = calculate_co2_budget(km, plane, weather_factor)
    goal_id=get_goal_id(weather_condition)

    if current_fuel < (tank_capacity * 0.5):
        answer = input(
            "\nYour tank is running low (less than 50%). Would you like to fill it up? (Y/N) \n").lower().strip()

        if answer == "y":
            refuel_price = calculate_refueling_cost(tank_capacity, current_fuel, refueling)
            revenue = revenue - refuel_price
            print(f"Refuel complete {refuel_price:.2f} euros spent.\n")
            update_current_fuel_by_game_id(tank_capacity, chosen_game[0])
            current_fuel = (get_current_fuel_by_game_id(chosen_game[0]))

    print(f"{country_flags.flags[departure_country]['flag']}{departure_airport_name}  "
          f"----->  "
          f"{country_flags.flags[arrival_country]['flag']}{arrival_airport_name}\n")
    input("Press Enter to start the flight...")

    for i in range(3, 0, -1):
        print(i)
        time.sleep(1)

    print("Take off!\n")

    traveled = 0
    cloud = ""
    while traveled < km and current_fuel > 0:

        cloud+="☁️☁️☁️"
        remaining_distance = km - traveled
        step_fuel = min(step_distance, remaining_distance, current_fuel)

        if step_fuel == 0:
            print("Fuel depleted! Cannot continue.")
            break

        traveled += step_fuel
        current_fuel -= step_fuel

        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        CYAN = "\033[96m"
        RESET = "\033[0m"
        WHITE = "\033[97m"

        max_clouds = 30
        cloud_count = min(int((traveled / km) * max_clouds), max_clouds)
        flight_bar = f"{WHITE}{'☁' * cloud_count}✈️{RESET}"


        fuel_text = f"{YELLOW}Fuel: {current_fuel:.1f} km{RESET}".ljust(10)

        print(f"{CYAN}Traveled: {traveled:6.1f} km / {km:6.2f} km{RESET} | {fuel_text} {flight_bar}")

        time.sleep(step_time)

    if current_fuel <= 0:
        print("Mission failed! Not enough fuel.")
        actual_location = departure_airport_name
        return actual_location, current_fuel
    else:
        print(f"Mission complete! You reached {arrival_airport_name}.")
        flight_duration, flight_duration_minutes = update_flight_duration_minutes_by_game_id(chosen_game, km)
        flight_duration = int(flight_duration * weather_factor)

        post_flight_log(chosen_game, arrival_airport_ident, flight_duration, passenger_count, revenue, weather_condition)
        update_game_by_game_id(arrival_municipality, arrival_airport_ident, current_fuel, co2_consumed, co2_budget,
                               flight_duration_minutes, chosen_game[0])
        update_users_balance_by_user_id(chosen_game[3], revenue)
        post_goal_reached(chosen_game[0], goal_id, chosen_game[3])

# This function calculates the distance from the user's departure location to the destination.
def get_km_by_ident(ident_1, ident_2):
    location_1 = get_location_by_ident(ident_1)
    location_2 = get_location_by_ident(ident_2)

    if location_1 and location_2:
        km = geopy.distance.geodesic(location_1, location_2).kilometers
        km = round(km, 2)
        return km
    else:
        print("Invalid ICAO codes provided!")
        return None

def get_departure_airport_ident_by_game_id(game_id):
    sql=sql_queries.get_departure_airport_ident_by_game_id
    cursor.execute(sql, (game_id,))
    result = cursor.fetchone()
    return result[0]


def get_location_by_ident(ident):
    sql = sql_queries.get_locations_by_ident
    cursor.execute(sql, (ident,))
    result = cursor.fetchone()

    if result is None:
        print(f"Invalid ICAO code: {ident}")
        return None

    location = (result[0], result[1])
    return location

def get_ticket_price_by_plane_id(plane_id):
    sql=sql_queries.get_ticket_price_by_plane_id
    cursor.execute(sql, (plane_id,))
    result = cursor.fetchone()[0]

    if result is None:
        print(f"Invalid ICAO code: {plane_id}")
        return None
    return result

def get_current_fuel_by_game_id(id):
    sql=sql_queries.get_current_fuel
    cursor.execute(sql, (id,))
    result = cursor.fetchone()
    return result[0]

def calculate_refueling_cost(tank_capacity, current_fuel, refueling_cost):
    used_fuel = tank_capacity - current_fuel
    cost = (used_fuel / tank_capacity) * refueling_cost
    return cost

def update_current_fuel_by_game_id(current_fuel, chosen_game):
    sql = sql_queries.update_current_fuel
    cursor.execute(sql, (current_fuel, chosen_game,))

def get_iso_country_by_airport_ident(ident):
    sql=sql_queries.get_iso_country_by_airport_ident
    cursor.execute(sql, (ident,))
    result = cursor.fetchone()
    return result[0]

def get_airport_by_ident(ident):
    sql=sql_queries.get_airport_by_ident
    cursor.execute(sql, (ident,))
    result = cursor.fetchone()
    return result

def update_flight_duration_minutes_by_game_id(chosen_game,km):
    flight_duration_minutes_db=get_flight_duration_minutes_by_game_id(chosen_game[0])
    flight_duration = calculate_travel_time(km,chosen_game[6])
    flight_duration_minutes=flight_duration_minutes_db + flight_duration
    return flight_duration,flight_duration_minutes

def update_game_by_game_id(arrival_municipality,arrival_airport_ident, current_fuel, co2_consumed, co2_budget,
                           flight_duration, id):
    sql = sql_queries.update_game_by_game_id
    cursor.execute(sql, (arrival_municipality,arrival_airport_ident, current_fuel, co2_consumed, co2_budget,
                         flight_duration, id))

def post_flight_log(chosen_game, arrival_airport_ident, flight_duration, passenger_count, revenue, weather):
    game_id=chosen_game[0]
    plane_id=chosen_game[6]
    departure_airport=chosen_game[7]

    sql = sql_queries.post_flight_log
    cursor.execute(sql,(game_id, plane_id, departure_airport, arrival_airport_ident,
                        flight_duration, passenger_count, revenue, weather))
    return

def update_users_balance_by_user_id(user_id: object, income: object) -> None:
    sql_get_balance =sql_queries.get_balance
    cursor.execute(sql_get_balance, (user_id,))
    balance = cursor.fetchone()[0]

    income = Decimal(str(income))
    balance = balance + income

    sql_update_balance = sql_queries.update_user_balance_by_user_id
    cursor.execute(sql_update_balance, (balance, user_id))

def get_flight_duration_minutes_by_game_id(chosen_game):
    sql=sql_queries.get_flight_duration_minutes_by_game_id
    cursor.execute(sql, (chosen_game,))
    result = cursor.fetchone()
    return result[0]

def calculate_travel_time(km,plane_id):
    max_speed =get_max_speed_by_plane_id(plane_id)
    calculated_travel_time = km / max_speed

    hour_int = int(calculated_travel_time)
    minute = round((calculated_travel_time - hour_int) * 60)

    if minute == 60:
        hour_int += 1
        minute = 0

    flight_duration_minutes = hour_int * 60 + minute
    return flight_duration_minutes

def get_max_speed_by_plane_id(plane_id):
    sql=sql_queries.get_max_speed_by_plane_id
    cursor.execute(sql, (plane_id,))
    result = cursor.fetchone()
    return result[0]

def get_weather():
    sql=sql_queries.get_weather
    cursor.execute(sql)
    result = cursor.fetchall()
    weather=random.randint(0,len(result)-1)

    if result[weather][0] == "Wind blows more than 10 m/s" or result[weather][0] == "Temperature under -20C":
        return 2, result[weather][0]
    elif result[weather][0] == "Temperature exactly 0C" or result[weather][0] == "Cloudy":
        return 1.5, result[weather][0]
    else:
        return 1, result[weather][0]

def calculate_co2_budget(km,plane,weather):
    margin = Decimal('0.1')
    km = Decimal(km)
    co2_per_flight = plane[6] * km * plane[7]
    co2_budget = co2_per_flight * (1 + margin)


    if weather == "Wind blows more than 10 m/s" or weather == "Temperature under -20C":
        return co2_per_flight, co2_budget * Decimal('1.04')
    elif weather == "Temperature exactly 0C" or weather == "Cloudy":
        return co2_per_flight, co2_budget * Decimal('1.02')
    else:
        return co2_budget ,co2_per_flight

def get_goal_id(weather):
    sql=sql_queries.get_goal_id
    cursor.execute(sql, (weather,))
    result = cursor.fetchone()
    return result[0]

def post_goal_reached(game_id, goal_id, user_id,):
    cursor.execute(sql_queries.get_goal_reached, (game_id, goal_id,))
    result = cursor.fetchone()
    if result is None:
        sql=sql_queries.post_goal_reached
        cursor.execute(sql, (game_id, goal_id, user_id))
