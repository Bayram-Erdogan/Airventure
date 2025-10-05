import mysql.connector

import time
con = mysql.connector.connect(

    host='127.0.0.1',
    port=3306,
    database='flight_game_project',
    user='root',
    password='4444',
    autocommit=True,
    buffered=True
)
import random
import sql_queries
cursor = con.cursor()
def balanc(player):
    sql0=sql_queries.get_balance
    cursor.execute(sql0,(player,))
    wallet =cursor.fetchall()[0]
    return wallet[0]
def update_balance(player,new_balance):
    cursor.execute("update users set balance=%s where username=%s",(new_balance,player))
def update_location(player,new_location):
    cursor.execute("update game set municipality=%s where username=%s",(new_location,player))
while True:
    money =balanc("fahad")
    countrys = []
    options = []
    kerta = 1
    cursor.execute("SELECT name FROM country where continent= 'EU' ORDER BY RAND() LIMIT 3")
    countries = cursor.fetchall()
    for c in countries:
        countrys.append(c[0])
    stuff = ["jewelry", "cigarette", "Diamonds", "Hand Watch ", "Alcohole"]
    ilegal=["Stolen Gold ","Antiquities","Advance Teknologia",]
    low_risk =["Holidays","Low staff","Technical Issue",]
    random_number = random.randint(0,len(stuff)-1)
    options.append(stuff[random_number])
    print("💼 Welcome to SMUGGLER LIFE 💼")
    print("You are a smuggler traveling between countries in europa.\n")
    print(f"\n💰 Money: {money}€ ")
    print("Available missions:")
    for i in range(2):
        random_number = random.randint(0,len(ilegal)-1)
        options.append(ilegal[random_number])
    print(f"{kerta}.normal risk mission smuggle {options[0]} To {countrys[0]}.")
    kerta += 1
    print(f"{kerta}.medium risk mission smuggle {options[1]} To {countrys[1]}")
    kerta += 1
    print(f"{kerta}.high risk mission smuggle {options[2]} To {countrys[2]}")
    chois=input("witch mission you would like to choose (1/2/3 or q to quit): ")
    if chois=='q':
        print("you decided to quit the game")
        break
    if chois=='1':
        print(f"your mission will be Smuggling {options[0]} to {countrys[0]}  ")
        print(f"the mission is Low risk because of {low_risk[random_number]}")
        sucsesrtae = 0.6
        reward = random.randint(30,150)
        target=countrys[0]
    elif chois=='2':
        print(f"your mission will be Smuggling {options[1]} to {countrys[1]}")
        print("the mission is medium risk")
        sucsesrtae = 0.4
        reward = random.randint(300,800)
        target=countrys[1]
    elif chois=='3':
        print(f"your mission will be Smuggling {options[2]} to {countrys[2]}")
        print("the mission is high risk")
        sucsesrtae = 0.1
        reward = random.randint(900,1500)
        target=countrys[2]
    else:
        print("invalid choice")
        continue
    time.sleep(1)
    print("starting mission...\n")
    time.sleep(1)
    if random.random() <= sucsesrtae:
        money += reward
        print(f"✅ SUCCESS! You earned {reward}€.")
        update_location("fahad",target)
    else:
        if chois=='1':
            loss=reward*0.5
        else:
            loss=reward
        money -= loss
        print(f"🚨 FAILED! You got caught smuggling {options[int(chois)-1]} in {countrys[int(chois)-1]}.")
        print(f"❌ Lost {loss:.2f}€.")
    update_balance("fahad",money)
    print(f"\n💰 New balance: {money}€")
    time.sleep(2)
