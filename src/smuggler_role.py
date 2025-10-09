import os
import random
import sys
import time
import mysql.connector
from dotenv import load_dotenv
import utilities
import sql_queries

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
cursor = connection.cursor(buffered=True)

products = [
    "Vintage Wine Collection",
    "High-end Watches",
    "Specialty Coffee Beans",
    "Counterfeit Luxury Handbags",
    "Rare Botanical Extracts",
    "High-capacity Mining Hardware",
    "Prototype Electronics",
    "Luxury Perfume Shipment",
    "Antique Replica Sculptures",
    "Pharmaceutical Samples"
]

risks =[
  "clean_pass",
  "bribe_encounter",
  "customs_seizure"
]

def get_random_product():
    product = random.choice(products)
    return product

def get_random_tree_country(country):
    sql = sql_queries.get_random_tree_country
    cursor.execute(sql, (country,))
    result = cursor.fetchall()

    country_names = []
    for row in result:
        country_names.append(row[0])

    if len(country_names) <= 3:
        return country_names

    countries = random.sample(country_names, 3)
    return countries

def get_a_task(game_id,departure_municipality,country):
    product =get_random_product()
    stop_1,stop_2, arrival_country=get_random_tree_country(country)
    start_situation=input(f"Your mission is to take {product} to {arrival_country}. On your way to {arrival_country}, "
                          f"you must first stop by {stop_1}.\nThen you will stop by {stop_2} and from there you will go"
                          f"to {arrival_country}.\n"
                          f"Are you ready to fly? (Y/N)\n").lower().strip()

    if start_situation == "y":
        return stop_1, stop_2, arrival_country,product
    elif start_situation == "n":
        print("You chose not to start the game. Exiting.")
        sys.exit()

def start_for_smuggler(game_id, departure_municipality):
    sql = sql_queries.get_iso_country_by_municipality
    cursor.execute(sql, (departure_municipality,))
    country = cursor.fetchone()[0]
    print(country)

    stop_1, stop_2, arrival_country, product = get_a_task(game_id, departure_municipality, country)
    countries = [stop_1, stop_2, arrival_country]

    sql = sql_queries.get_user_id_by_game_id
    cursor.execute(sql, (game_id,))
    user_id= cursor.fetchone()[0]

    post_task_log(game_id, departure_municipality, stop_1, stop_2, arrival_country, product)
    task_id=get_task_id(departure_municipality, stop_1, stop_2, arrival_country, product)

    current_location = departure_municipality

    for next_country in countries:
        get_a_ticket(user_id,game_id)
        fly_for_task(current_location, next_country)

        risk_result = get_a_risk(current_location, next_country)

        if risk_result == "FAILED":
            update_task_status('FAILED', task_id)
            print("Mission failed! Game over.")
            return

        current_location = next_country
        print(current_location)

    update_task_status('SUCCESS', task_id)
    print("Mission completed successfully!")

def get_a_ticket(user_id, game_id):
    sql = sql_queries.get_balance
    cursor.execute(sql, (user_id,))
    balance = cursor.fetchone()[0]

    plane_id=get_plane_id_by_game(game_id)

    sql = sql_queries.get_ticket_price_by_plane_id
    cursor.execute(sql, (plane_id,))
    ticket_price = cursor.fetchone()[0]

    balance = balance - ticket_price
    sql_balance = sql_queries.update_balance
    cursor.execute(sql_balance, (balance,user_id,))

    #print(f"Get a ticket from {departure_municipality} to {arrival_country}")


    print()
    return

def fly_for_task(departure_municipality, arrival_country):
    print(f"{departure_municipality} -----> {arrival_country}\n")
    input("Press Enter to start the flight...")

    for i in range(3, 0, -1):
        print(i)
        time.sleep(0.5)

    print("Take off!\n")

    CYAN = "\033[96m"
    RESET = "\033[0m"

    total_steps = 10
    for step in range(total_steps + 1):

        clouds = "☁️☁️☁️" * step
        plane = "✈️"

        percent = (step / total_steps) * 100
        print(f"{CYAN}Flight progress: {percent:5.1f}%{RESET} - {clouds}{plane}")

        time.sleep(0.5)

    print(f"\n🛬 Landing completed! Arrived at {arrival_country}.\n")

def get_a_risk(current_location, next_country):
    index = random.randint(0, len(risks) - 1)

    if risks[index] == "clean_pass":
        print("Clean pass! No issues at this stop.")
        return "SUCCESS"

    elif risks[index] == "bribe_encounter":
        print("Bribe encounter! An officer is stopping you.")
        bribe = 50
        choice = input("Try to Escape (E) or Pay the Bribe (P)? ").lower().strip()

        if choice == "e":
            chance = random.randint(1, 2)
            if chance == 1:
                print(f"You escaped, but had to pay double bribe: {bribe * 2} €")
            else:
                print(f"You didn't escape, paying double bribe: {bribe * 2} €")
            return "SUCCESS"

        elif choice == "p":
            print(f"You paid the bribe: {bribe} €")
            return "SUCCESS"

    elif risks[index] == "customs_seizure":
        print("Customs seizure! You got caught.")
        return "FAILED"

def post_task_log(game_id,departure_municipality,stop_1, stop_2, arrival_country, product):
    sql=sql_queries.post_task_log
    cursor.execute(sql, (game_id,departure_municipality,stop_1, stop_2, arrival_country, product))

def update_task_status(status, task_id):
    sql=sql_queries.update_task_status
    cursor.execute(sql, (status, task_id))

def get_task_id(departure_municipality, stop_1, stop_2, arrival_country, product):
    sql = sql_queries.get_task_id
    cursor.execute(sql, (departure_municipality, stop_1, stop_2, arrival_country, product))
    result=cursor.fetchone()
    return result[0]

def get_plane_id_by_game(game_id):
    sql=sql_queries.get_plane_id_by_game_id
    cursor.execute(sql, (game_id,))
    result=cursor.fetchone()
    plane_id =result[0]
    return plane_id

# This function allows the player to create a game with the smuggler role.
def create_a_game_for_smuggler_role(username):
    game_name = input("Please enter your game name : ")
    player_role = "SMUGGLER"
    plane_id=10
    user=utilities.get_user_by_username(username)
    user_id=user[0]
    post_game_to_game_for_smuggler(user_id, username, game_name, player_role,plane_id)

    utilities.country_identifier(game_name, player_role)

# This function opens a game record in the table by sending the information generated according to the smuggler role
# to the game table.
def post_game_to_game_for_smuggler(user_id, username, game_name,player_role,plane_id):
    sql= sql_queries.post_game_to_game_tbl_for_smuggler
    cursor.execute(sql, (user_id,username, game_name,player_role,plane_id))