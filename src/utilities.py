import mysql.connector
from dotenv import load_dotenv
import os
import random
from src import sql_queries
from geopy.geocoders import Nominatim
from decimal import Decimal

#import pilot_role
import smuggler_role

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

# This function retrieves the player by username from the users table.
def get_user_by_username(username):
    sql= sql_queries.get_user_by_username
    cursor.execute(sql,(username,))
    result = cursor.fetchone()
    return result

# This function updates the user's aircraft.
def update_user_plane_id(plane_id, user_id):
    sql= sql_queries.update_user_plane_id
    cursor.execute(sql, (plane_id,user_id,))

# This function allows the game's starting airport and city to be updated according to the player's chosen country
# and role.
def country_identifier(game_name,player_role):
    import pilot_role
    country_name = input("Country name: ")
    iso_code = identify_iso_country(country_name)

    if player_role == "PILOT":
        airports = select_airports(iso_code)
        icao_code=choose_three_options(airports)
        municipality=pilot_role.get_municipality_by_ident(icao_code)
        update_starting_location(icao_code, municipality, game_name)
    elif player_role == "SMUGGLER":
        list = pilot_role.get_random_municipality_by_iso_country(iso_code)
        municipality=choose_three_options(list)
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
    list = []
    count = 1

    for option in options:
        list.append(option)
        print(f"Press {count} if you want to choose {option}")
        count += 1

    chosen_index = int(input("Choose an airport by typing its number: "))
    chosen = list[chosen_index - 1]

    return chosen

# This function updates the airport and city according to the game name.
def update_starting_location(icao_code, municipality, game_name):
    sql = sql_queries.update_game_airport_municipality
    cursor.execute(sql, (icao_code, municipality, game_name))

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

# This function retrieves game information from the database according to the game id and returns it.
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

# This function retrieves the ticket price from the database according to the plane ID and returns it.
def get_ticket_price_by_plane_id(plane_id):
    sql=sql_queries.get_ticket_price_by_plane_id
    cursor.execute(sql, (plane_id,))
    result = cursor.fetchone()[0]

    if result is None:
        print(f"Invalid ICAO code: {plane_id}")
        return None
    return result

# This function updates the amount of money in the user's account.
def update_user_balance_by_user_id(user_id: object, income: object) -> None:
    balance=get_user_balance(user_id)
    income = Decimal(str(income))
    balance = balance + income

    sql_update_balance = sql_queries.update_user_balance_by_user_id
    cursor.execute(sql_update_balance, (balance, user_id))

def get_user_balance(user_id):
    sql=sql_queries.get_balance
    cursor.execute(sql, (user_id,))
    result = cursor.fetchone()
    balance = result[0]
    return balance

def update_balance(balance,user_id):
    sql=sql_queries.update_balance
    cursor.execute(sql,(balance,user_id))