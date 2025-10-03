import mysql.connector
from dotenv import load_dotenv
import os
import random
import sql_queries
import player
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
    plane_id=1
    player_role = "PILOT"
    user=get_user_by_username(username)
    user_id=user[0]
    game_name = input("Please enter your game name : ")
    post_game_to_game_for_pilot(user_id,username, game_name, player_role, plane_id)

# This function allows the player to create a game with the smuggler role.
def create_a_game_for_smuggler_role(username):
    player_role = "SMUGGLER"
    user=get_user_by_username(username)
    user_id=user[0]
    game_name = input("Please enter your game name : ")
    post_game_to_game_for_smuggler(user_id,username, game_name, player_role)

# This function retrieves the player by username from the users table.
def get_user_by_username(username):
    sql= sql_queries.get_user_by_username
    cursor.execute(sql,(username,))
    result = cursor.fetchone()
    return result

# This function opens a game record in the table by sending the information generated according to the pilot role
# to the game table.
def post_game_to_game_for_pilot (user_id,username, game_name,player_role,plane_id):
    sql= sql_queries.post_game_to_game_tbl_for_pilot
    cursor.execute(sql, (user_id,username, game_name,player_role,plane_id))
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
        print(f"Press {i} for: {airport}")
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

def add_player(player_name):
    player1 = player.Player(player_name)
    sql = sql_queries.post_user
    cursor.execute(sql, (player1.username, player1.co2_consumed, player1.plane_id, player1.balance))
    print(f"Created player: {player1.username}")

def get_players():
    sql = sql_queries.get_username
    cursor.execute(sql)
    result = cursor.fetchall()
    print("Saved players:")
    for row in result:
        print(row[0])

def start_game():
    print("Starting the game...\n")
    choice = input("Start a new game (1) or continue previous (2)? ")

    if choice == "1":
        name = input("Enter player name: ")
        add_player(name)
        return name
    elif choice == "2":
        get_players()
        name = input("Which player do you want to continue with?: ")
        return name

def country_identifier(username):
    country_name = input("Country name: ")
    iso_code = identify_iso_country(country_name)
    airports = select_airports(iso_code)
    icao_code = choose_three_options(airports)
    municipality = get_municipality_by_ident(icao_code)
    update_starting_location(icao_code, municipality, username)

    return icao_code

def identify_iso_country(country_name):
    sql = sql_queries.get_iso_country_by_country_name
    cursor.execute(sql, (country_name,))
    row = cursor.fetchone()
    return row[0] if row else None

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

def update_starting_location(icao_code, municipality, username):
    sql = sql_queries.update_game_airport
    cursor.execute(sql, (icao_code, municipality, username))

def get_municipality_by_ident(ident):
    sql = sql_queries.get_municipality_by_ident
    cursor.execute(sql,(ident,))
    row = cursor.fetchone()
    return row[0] if row else None
def matkan_pituus(pelaaja,new_Airport):
    sql=sql_queries.get_municipality_by_name
    cursor.execute(sql, (pelaaja,))
    cursor.fetchone()
    paikaA = cursor.fetchone()[0]
    paika1 = geolocator.geocode(paikaA)
    sql2=sql_queries.get_municipality_by_ident
    cursor.execute(sql2, (new_Airport,))
    sq = cursor.fetchone()
    paikaB = sq[0]
    paika2 = geolocator.geocode(paikaB)

    coords_a = (paika1.latitude, paika2.longitude)
    coords_b = (paika2.latitude, paika2.longitude)
    distance = geodesic(coords_a, coords_b).kilometers
    sql3=sql_queries.update_place_B
    cursor.execute(sql3,
                   (paikaB, new_Airport, pelaaja))
    cursor.fetchall()

    print(f"  matka stä iin  kestä  {distance:.2f} Km")
    return distance // 1


def Balance(pelaaja):
    sql1=sql_queries.select_balances
    cursor.execute(sql1, (pelaaja,))
    pelaajanLompako = cursor.fetchone()[0]
    return pelaajanLompako

def nukyinen_tanki(pelaaja):
    sql1=sql_queries.curent_fule
    cursor.execute(sql1,(pelaaja,))
    fuel = cursor.fetchone()[0]
    return fuel

def maxfule(pelaaja):
    sql1=sql_queries.plane_id
    cursor.execute(sql1,(pelaaja,))
    plane_id = cursor.fetchone()[0]
    sql2=sql_queries.tank_capacity_by_id
    cursor.execute(sql2, (plane_id,))
    tank_capacity = cursor.fetchone()[0]
    return tank_capacity

def matkan_kulutus (pelaaja,km):
    sql1=sql_queries.curent_fule
    cursor.execute(sql1, (pelaaja,))
    fule = cursor.fetchone()
    kulutus = km * 1.2
    return kulutus

def tankausmatkan_jalken(pelaaja,km):
    sql1=sql_queries.curent_fule
    cursor.execute(sql1,(pelaaja,))
    fule =cursor.fetchone()
    kulutus = km * 1.2
    new_fule=fule[0]-kulutus
    sql2=sql_queries.fule_update
    cursor.execute(sql2,(new_fule,pelaaja,))
    return new_fule
#smagler funkiton
def smugler_item_shop(user):
    sql1=sql_queries.get_balance
    cursor.execute(sql1, (user,))
    balance=cursor.fetchone()[0]
    print(f"balans:|{balance}€|")
    print("    Tavarat                        Hinta   ")
    print("-------------------------------------------------")
    print("1.  Segaret          ᝰ🚬    ^        20€     ")
    print("2.  Fake jacket        🧥    ^        60€     ")
    print("3.  Chemicals          🧪    ^       200€     ")
    print("4.  Hand Watch         ⌚    ^       900€     ")
    print("5.  Alcohole           🍾    ^     1,800€   ")
    print("6.  Antiquities       📜🏺   ^     4,000€         ")
    print("7.  Golde bar          🧈    ^    14,000€     ")
    print("8.  Advance Tecnologia 🦾🤖  ^    20,000€     ")
    print("                     Back                     ")
    buy=input("  what you are buying ? : ")
    if buy == '1':
        if balance >= 20:
            print(f"you bouth Segaret your balans will be {balance - 20}€")
            newbalance = balance - 20
            sql1 = sql_queries.update_balance
            cursor.execute(sql1, (newbalance, user))
    elif buy == '2':
        if balance >= 60:
            print(f"you bouth Fake jacket your balans will be {balance - 60}€")
            newbalance = balance - 60
            sql1 = sql_queries.update_balance
            cursor.execute(sql1, (newbalance, user))
    elif buy == '3':
        if balance >= 200:
            print(f"you bouth Chemicals your balans will be {balance - 200}€")
            newbalance = balance - 200
            sql1 = sql_queries.update_balance
            cursor.execute(sql1, (newbalance, user))
    elif buy == '4':
        if balance >=900:
            print(f"you bouth Hand Watch your balans will be {balance - 900}€")
            newbalance = balance - 900
            sql1 = sql_queries.update_balance
            cursor.execute(sql1, (newbalance, user))
    elif buy == '5':
        if balance >= 1800:
            print(f"you bouth Alcohole your balans will be {balance - 1800}€")
            newbalance = balance - 1800
            sql1 = sql_queries.update_balance
            cursor.execute(sql1, (newbalance, user))
    elif buy == '6':
        if balance >= 4000:
            print(f"you bouth Antiquities your balans will be {balance - 4000}€")
            newbalance = balance - 20
            sql1 = sql_queries.update_balance
            cursor.execute(sql1, (newbalance, user))
    elif buy == '7':
        if balance >= 14000:
            print(f"you bouth Gold bar your balans will be {balance - 14000}€")
            newbalance = balance - 20
            sql1 = sql_queries.update_balance
            cursor.execute(sql1, (newbalance, user))
    elif buy == '8':
        if balance >= 20000:
            print(f"you bouth Advance Tecnologia your balans will be {balance - 20000}€")
            newbalance = balance - 20
            sql1 = sql_queries.update_balance
            cursor.execute(sql1, (newbalance, user))
    else:
        print (" leaving item shope you did not buy any thing ")




smugler_item_shop("qwe")