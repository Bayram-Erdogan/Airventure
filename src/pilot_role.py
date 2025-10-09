import random
import time
from decimal import Decimal
from geopy.distance import geodesic

from assets import country_flags
import sql_queries
from player import Player
from utilities import connection_to_db
import utilities

connection = connection_to_db()
cursor = connection.cursor(buffered=True)

# This function will allow the game to be played and the data to be updated.
def start_game(chosen_game):
    plane=utilities.get_plane_by_plane_id(chosen_game[6])
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

    ticket_price=utilities.get_ticket_price_by_plane_id(plane[0])
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

        post_flight_log(chosen_game, arrival_airport_ident, flight_duration, co2_consumed, passenger_count, revenue, weather_condition)
        update_game_by_game_id(arrival_municipality, arrival_airport_ident, current_fuel, co2_consumed, co2_budget,
                               flight_duration_minutes, chosen_game[0])
        utilities.update_user_balance_by_user_id(chosen_game[3], revenue)
        post_goal_reached(chosen_game[0], goal_id, chosen_game[3])
        check_next_plane(chosen_game[0],chosen_game[3],chosen_game[6])

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

# This function finds the country the player wants from the country database and returns the iso_country code of the
# country.
def get_iso_country_code_by_country_name(country):
    sql= sql_queries.get_iso_country_by_country_name
    cursor.execute(sql, (country,))
    result = cursor.fetchone()[0]
    return result

# This function calculates the distance from the user's departure location to the destination.
def get_km_by_ident(ident_1, ident_2):
    location_1 = get_location_by_ident(ident_1)
    location_2 = get_location_by_ident(ident_2)

    if location_1 and location_2:
        km = geodesic(location_1, location_2).km
        km = round(km, 2)
        return km
    else:
        print("Invalid ICAO codes provided!")
        return None

# This function returns the departure airport from the database.
def get_departure_airport_ident_by_game_id(game_id):
    sql=sql_queries.get_departure_airport_ident_by_game_id
    cursor.execute(sql, (game_id,))
    result = cursor.fetchone()
    return result[0]

# This function retrieves the coordinates of the airport from the database and returns them.
def get_location_by_ident(ident):
    sql = sql_queries.get_locations_by_ident
    cursor.execute(sql, (ident,))
    result = cursor.fetchone()

    if result is None:
        print(f"Invalid ICAO code: {ident}")
        return None

    location = (result[0], result[1])
    return location

# This function retrieves the current fuel amount according to the game id from the database and returns it.
def get_current_fuel_by_game_id(id):
    sql=sql_queries.get_current_fuel
    cursor.execute(sql, (id,))
    result = cursor.fetchone()
    return result[0]

# This function calculates how much it costs to fill the plane's fuel tank.
def calculate_refueling_cost(tank_capacity, current_fuel, refueling_cost):
    used_fuel = tank_capacity - current_fuel
    cost = (used_fuel / tank_capacity) * refueling_cost
    return cost

# This function updates the amount of fuel in the plane's fuel tank.
def update_current_fuel_by_game_id(current_fuel, chosen_game):
    sql = sql_queries.update_current_fuel
    cursor.execute(sql, (current_fuel, chosen_game,))

# This function retrieves the ISO code of a country from the database according to the airport's ID information and
# returns it.
def get_iso_country_by_airport_ident(ident):
    sql=sql_queries.get_iso_country_by_airport_ident
    cursor.execute(sql, (ident,))
    result = cursor.fetchone()
    return result[0]

# This function retrieves the information of an airport from the database according to the ID information of that
# airport and returns it.
def get_airport_by_ident(ident):
    sql=sql_queries.get_airport_by_ident
    cursor.execute(sql, (ident,))
    result = cursor.fetchone()
    return result

# This function sends the information about the flight to the flight_log table.
def post_flight_log(chosen_game, arrival_airport_ident, flight_duration,co2_consumed, passenger_count, revenue, weather):
    game_id=chosen_game[0]
    plane_id=chosen_game[6]
    departure_airport=chosen_game[7]

    sql = sql_queries.post_flight_log
    cursor.execute(sql,(game_id, plane_id, departure_airport, arrival_airport_ident,
                        flight_duration,co2_consumed, passenger_count, revenue, weather))
    return

# This function retrieves the weather data from the database to randomly determine the weather conditions during the
# flight and returns it.
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

# This function calculates the CO2 produced during the flight.
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

# This function retrieves the weather id from the database based on the weather condition and returns it.
def get_goal_id(weather):
    sql=sql_queries.get_goal_id
    cursor.execute(sql, (weather,))
    result = cursor.fetchone()
    return result[0]

# This function adds the flights made according to the weather conditions to the goal reached table.
def post_goal_reached(game_id, goal_id, user_id,):
    cursor.execute(sql_queries.get_goal_reached, (game_id, goal_id,))
    result = cursor.fetchone()
    if result is None:
        sql=sql_queries.post_goal_reached
        cursor.execute(sql, (game_id, goal_id, user_id))

def get_required_hour_by_plane_id(plane_id):
    plane_id+=1
    sql=sql_queries.get_required_hour_by_plane_id
    cursor.execute(sql, (plane_id,))
    result = cursor.fetchall()
    requested_hour = result[0][0]
    return requested_hour

def get_plane_price_by_plane_id(plane_id):
    sql=sql_queries.get_plane_price_by_plane_id
    cursor.execute(sql, (plane_id,))
    result = cursor.fetchone()
    plane_price = result[0]
    return plane_price

def check_next_plane(game_id,user_id,plane_id):
    plane_id+=1
    plane_price = get_plane_price_by_plane_id(plane_id)
    required_hour = get_required_hour_by_plane_id(plane_id)
    flight_duration_minutes=get_flight_duration_minutes_by_game_id(game_id)
    balance = utilities.get_user_balance(user_id)

    if balance>=plane_price:
        if flight_duration_minutes>=required_hour:
            plane=input("Would you like to buy a next plane?: (Y/N)\n").lower().strip()
            if plane == "y":
                utilities.update_user_plane_id(plane_id, user_id)
                update_game_plane_id(game_id, plane_id)
                balance=balance-plane_price
                utilities.update_balance(balance, user_id)

def update_game_plane_id(game_id,plane_id):
    sql=sql_queries.update_game_plane_id
    cursor.execute(sql, (plane_id,game_id,))

def get_random_municipality_by_iso_country(iso_country):
    sql=sql_queries.get_municipality_by_iso_country
    cursor.execute(sql,(iso_country,))
    result=cursor.fetchall()
    selection = []

    for _ in range(3):
        random_index = random.randint(0, len(result) - 1)
        selection.append(result[random_index])

    selection = [t[0] for t in selection]
    return selection

# This function updates game information based on game id.
def update_game_by_game_id(arrival_municipality,arrival_airport_ident, current_fuel, co2_consumed, co2_budget,
                           flight_duration, id):
    sql = sql_queries.update_game_by_game_id
    cursor.execute(sql, (arrival_municipality,arrival_airport_ident, current_fuel, co2_consumed, co2_budget,
                         flight_duration, id))

# This function retrieves the flight hours from the database and returns them to the game account that the user has
# played.
def get_flight_duration_minutes_by_game_id(chosen_game):
    sql=sql_queries.get_flight_duration_minutes_by_game_id
    cursor.execute(sql, (chosen_game,))
    result = cursor.fetchone()
    return result[0]

# This function returns the city where the airport is located based on the airport code.
def get_municipality_by_ident(ident):
    sql = sql_queries.get_municipality_by_ident
    cursor.execute(sql,(ident,))
    row = cursor.fetchone()
    return row[0] if row else None

# This function takes the number of passengers that the plane can carry according to the plane ID and determines the
# number of random passengers according to this amount.
def create_passenger(plane_id):
    sql=sql_queries.get_passenger_capacity_by_plane_id
    cursor.execute(sql,(plane_id,))
    result = cursor.fetchone()

    passenger_capacity=result[0]
    passenger_capacity=random.randint(1,passenger_capacity)
    return passenger_capacity

# This function updates the flight times of the player during the game according to the game id.
def update_flight_duration_minutes_by_game_id(chosen_game,km):
    flight_duration_minutes_db=get_flight_duration_minutes_by_game_id(chosen_game[0])
    flight_duration = calculate_travel_time(km,chosen_game[6])
    flight_duration_minutes=flight_duration_minutes_db + flight_duration
    return flight_duration,flight_duration_minutes

# This function calculates the flight time that the user has spent during the flight.
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

# This function retrieves the max_speed of a plane from the database and returns it.
def get_max_speed_by_plane_id(plane_id):
    sql=sql_queries.get_max_speed_by_plane_id
    cursor.execute(sql, (plane_id,))
    result = cursor.fetchone()
    return result[0]

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

# This function allows the player to create a game with the pilot role.
def create_a_game_for_pilot_role(username):
    game_name = input("Please enter your game name : ")
    plane_id=1
    player_role = "PILOT"

    plane=utilities.get_plane_by_plane_id(plane_id)
    current_fuel=plane[5]
    player = Player(username=username)

    co2_budget=player.co2_budget
    co2_consumed=player.co2_consumed
    user=utilities.get_user_by_username(username)

    user_id=user[0]
    post_game_to_game_for_pilot(
        user_id, username, game_name, player_role, plane_id, current_fuel, co2_budget, co2_consumed
    )

    utilities.update_user_plane_id(plane_id,user_id)

    utilities.country_identifier(game_name, player_role)

# This function opens a game record in the table by sending the information generated according to the pilot role
# to the game table.
def post_game_to_game_for_pilot (user_id,username, game_name,player_role,plane_id,current_fuel,co2_budget,co2_consumed):
    sql= sql_queries.post_game_to_game_tbl_for_pilot
    cursor.execute(sql, (user_id,username, game_name,player_role,plane_id,current_fuel,co2_budget,co2_consumed))