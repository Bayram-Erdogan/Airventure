import mysql.connector
import random
import time
import os
import sql_queries
import utilities

# === DATABASE CONNECTION ===
con = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='flight_game_project',
    user='root',
    password='4444',
    autocommit=True,
    buffered=True
)

cursor = con.cursor()

def get_country(player):
    cursor.execute("SELECT municipality FROM game WHERE username=%s", (player,))
    res = cursor.fetchone()
    return res[0]

def post_game_to_game_for_smuggler(user_id, username, game_name,player_role,plane_id):
    sql= sql_queries.post_game_to_game_tbl_for_smuggler
    cursor.execute(sql, (user_id,username, game_name,player_role,plane_id))

def create_a_game_for_smuggler_role(username):
    game_name = input("Please enter your game name : ")
    player_role = "SMUGGLER"
    plane_id=10
    user=utilities.get_user_by_username(username)
    user_id=user[0]
    post_game_to_game_for_smuggler(user_id, username, game_name, player_role,plane_id)

def get_balance(player):
    cursor.execute("SELECT balance FROM users WHERE username=%s", (player,))
    res = cursor.fetchone()[0]
    return res

def update_balance(player, new_balance):
    cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (new_balance, player))

def update_country(player, new_country):
    cursor.execute("UPDATE game SET municipality = %s WHERE username = %s", (new_country, player))

def update_leaderboard(player, score):
    cursor.execute("INSERT INTO leaderboard (username, score) VALUES (%s, %s)", (player, score))

def show_leaderboard():
    cursor.execute("SELECT username, score FROM leaderboard ORDER BY score DESC LIMIT 10")
    print("\n🏆 Leaderboard:")
    for rank, (user, score) in enumerate(cursor.fetchall(), start=1):
        print(f"{rank}. {user} — {score}€")

    else:
        cursor.execute("SELECT balance FROM users WHERE username=%s", (player,))
        res = cursor.fetchone()
        return res[0] if res else 0

def update_balance(player, new_balance):
    cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (new_balance, player))

def update_country(player, new_country):
    cursor.execute("UPDATE game SET municipality = %s WHERE username = %s", (new_country, player))

# === NEIGHBOR MAP ===
neighbors = {
    "Finland": ["Sweden", "Norway", "Russia", "Estonia"],
    "Sweden": ["Finland", "Norway", "Denmark", "Estonia", "Latvia"],
    "Norway": ["Sweden", "Finland", "Russia", "Denmark", "United Kingdom"],
    "Denmark": ["Germany", "Sweden", "Norway", "United Kingdom"],
    "Germany": ["Denmark", "Poland", "Netherlands", "Belgium", "France", "Switzerland", "Austria", "Czech Republic", "Luxembourg"],
    "Poland": ["Germany", "Czech Republic", "Slovakia", "Ukraine", "Belarus", "Lithuania", "Sweden"],
    "France": ["Belgium", "Luxembourg", "Germany", "Switzerland", "Italy", "Spain", "Andorra", "Monaco", "United Kingdom"],
    "Spain": ["France", "Portugal", "Andorra", "United Kingdom", "Italy"],
    "Portugal": ["Spain", "United Kingdom"],
    "Italy": ["France", "Switzerland", "Austria", "Slovenia", "San Marino", "Vatican City", "Croatia", "Malta"],
    "Austria": ["Germany", "Czech Republic", "Slovakia", "Hungary", "Slovenia", "Italy", "Switzerland", "Liechtenstein"],
    "Switzerland": ["Germany", "France", "Italy", "Austria", "Liechtenstein"],
    "Netherlands": ["Germany", "Belgium", "United Kingdom"],
    "Belgium": ["France", "Netherlands", "Germany", "Luxembourg", "United Kingdom"],
    "Luxembourg": ["Belgium", "Germany", "France"],
    "Czech Republic": ["Germany", "Poland", "Slovakia", "Austria"],
    "Slovakia": ["Czech Republic", "Poland", "Ukraine", "Hungary", "Austria"],
    "Hungary": ["Slovakia", "Ukraine", "Romania", "Serbia", "Croatia", "Slovenia", "Austria"],
    "Romania": ["Ukraine", "Moldova", "Bulgaria", "Serbia", "Hungary"],
    "Serbia": ["Hungary", "Romania", "Bulgaria", "North Macedonia", "Kosovo", "Montenegro", "Bosnia and Herzegovina", "Croatia"],
    "Croatia": ["Slovenia", "Hungary", "Serbia", "Bosnia and Herzegovina", "Montenegro", "Italy"],
    "Slovenia": ["Italy", "Austria", "Hungary", "Croatia"],
    "Bosnia and Herzegovina": ["Croatia", "Serbia", "Montenegro"],
    "Montenegro": ["Croatia", "Bosnia and Herzegovina", "Serbia", "Kosovo", "Albania", "Italy"],
    "Albania": ["Montenegro", "Kosovo", "North Macedonia", "Greece", "Italy"],
    "North Macedonia": ["Serbia", "Kosovo", "Albania", "Greece", "Bulgaria"],
    "Bulgaria": ["Romania", "Serbia", "North Macedonia", "Greece"],
    "Greece": ["Albania", "North Macedonia", "Bulgaria", "Italy"],
    "Kosovo": ["Serbia", "Montenegro", "Albania", "North Macedonia"],
    "Ukraine": ["Poland", "Slovakia", "Hungary", "Romania", "Moldova", "Belarus", "Russia"],
    "Belarus": ["Latvia", "Lithuania", "Poland", "Ukraine", "Russia"],
    "Lithuania": ["Latvia", "Belarus", "Poland", "Russia", "Sweden"],
    "Latvia": ["Estonia", "Lithuania", "Belarus", "Russia", "Sweden"],
    "Estonia": ["Latvia", "Russia", "Finland", "Sweden"],
    "Moldova": ["Romania", "Ukraine"],
    "Andorra": ["France", "Spain"],
    "Monaco": ["France", "Italy"],
    "San Marino": ["Italy"],
    "Vatican City": ["Italy"],
    "Liechtenstein": ["Switzerland", "Austria"],
    "United Kingdom": ["Ireland", "France", "Belgium", "Netherlands", "Norway", "Denmark", "Spain", "Portugal"],
    "Ireland": ["United Kingdom", "France"],
    "Malta": ["Italy"],
    "Russia": ["Norway", "Finland", "Estonia", "Latvia", "Lithuania", "Poland", "Belarus", "Ukraine"]
}

# === GAME START ===
player = "fahad"

def smuggler_role(player):
    money = get_balance(player)
    current = get_country(player)

    cursor.execute("SELECT name FROM country WHERE continent='EU' ORDER BY RAND() LIMIT 1")
    res = cursor.fetchone()
    target = res[0]

    goods = ["Gold", "Diamond", "Cigarette", "Jewelry", "Alcohol"]
    chosen_good = random.choice(goods)
    base_reward = random.randint(500, 1500)

    print('''                     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
                         ▓  Welcome to SMUGGLER LIFE 💼                              ▓
                        ▓   My name is gustavo                                     ▓
                         ▓  But you can call me gus                                 ▓ 
                        ▓  im the one who give missions next task going to be      ▓''')
    print(f"                     ▓      You are smuggling {chosen_good} from {current} to {target}. ▓")
    print('''                     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
                                        ▓▓
                                    ▓▓
                         ███████████
                        █░░░░░░░░░░░█
                        █░░ o   o ░░█
                        █░░░ ▄▄▄ ░░░█
                         ███████████
                            ███
                        ███████████
                       █ █ █ █ █ █ █
                      █  █████████  █
                     █   █████████   █
                        ███████████
    ''')

    print(f"💰 Balance: {money}€")
    print("You have 13 moves to reach your target.\n")

    max_moves = 13
    moves = 0
    penalty_half_final = False
    while True:
        if current == target:
            final_reward = 300
            money += final_reward
            update_balance(player, money)
            update_country(player, target)
            print(f"\n✅ You reached {target} in {moves} moves!")
            print(f"You earned 300€. Final balance: {money}€")
            print("🎉 Mission complete. Game over.")
            update_leaderboard(player, money)
            show_leaderboard()
            moves=0
            current = get_country(player)

            cursor.execute("SELECT name FROM country WHERE continent='EU' ORDER BY RAND() LIMIT 1")
            res = cursor.fetchone()
            target = res[0]
            chosen_good = random.choice(goods)

            print('''                     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
                      ▓  you are geting into                                                   ▓
                      ▓  Its nice to work withe you,                                        ▓
                      ▓                                                                      ▓ 
                                            ''')
            print(f"                     ▓ next mission     You are smuggling {chosen_good} from {current} to {target}. ▓")
            print("                      ▓   if you face any trouble you can call me i wont answer anyway▓")
            print('''                     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
                                                            ▓▓
                                                        ▓▓
                                             ███████████
                                            █░░░░░░░░░░░█
                                            █░░ o   o ░░█
                                            █░░░ ▄▄▄ ░░░█
                                             ███████████
                                                ███
                                            ███████████
                                           █ █ █ █ █ █ █
                                          █  █████████  █
                                         █   █████████   █
                                            ███████████
                        ''')

        if moves >= max_moves:
            print("\n😵 You got lost after 13 moves! Mission failed.")
            update_leaderboard(player, money)
            show_leaderboard()

        # === FIX ADDED HERE ===
        if current not in neighbors or not neighbors[current]:
            current = "Finland"
            update_country(player, current)
        # === END FIX ===

        choices = neighbors[current]
        print(f"\n🌍 You are in {current}. Move {moves + 1}/{max_moves}")
        print("Choose your next move:")
        for i, c in enumerate(choices, start=1):
            print(f"{i}. Travel to {c}")
        print(f"{len(choices) + 1}. ✈️ Use plane to go straight to {target} (60% risk)")
        print("q. Quit game")

        choice = input("Your choice: ").strip()
        if choice == 'q':
            print("You quit the game.")
            update_leaderboard(player, money)
            show_leaderboard()

        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(choices) + 1:
            print("Invalid choice.")
            continue

        # Police encounter
        if random.randint(1, 5) == 1:
            print("\n🚔 Police stopped you!")
            print("1) Lie")
            print("2) Tell the truth")
            pol = input("Choose (1/2): ").strip()
            if pol == '1':
                print("You lied to police...")
                if random.randint(1, 10) <= 2:
                    print("😅 Your lie worked! Continue your trip.")
                else:
                    print("😱 They found out your lie!.")
                    money = 0
                    update_balance(player, money)
                    print("All your money is confiscated.")
                    update_leaderboard(player, money)
                    show_leaderboard()

            elif pol == '2':
                print("You told the truth. They fined you 50% of your reward.")
                penalty_half_final = True
            else:
                print("Police didn’t like your hesitation. You're detained.")
                money = 0
                update_balance(player, money)
                update_leaderboard(player, money)
                show_leaderboard()

        if int(choice) == len(choices) + 1:
            print(f"✈️ You decided to fly directly to {target}.")
            plane = "🛫"
            print("Loding 🛬")
            for i in range(4):
                os.system("cls" if os.name == "nt" else "clear")
                print("Loading ☁︎" + "☁︎" * i + plane)
                time.sleep(0.4)
            if random.random() <= 0.6:
                print("🚨 You got caught smuggling at the airport!")
                money = 0
                update_balance(player, money)
                print("All money lost. Game over.")
                update_leaderboard(player, money)
                show_leaderboard()
            else:
                print("✅ You made it safely using the plane!")
                current = target
                continue

        chosen_country = choices[int(choice) - 1]
        print(f"You chose {chosen_country}...")
        time.sleep(1)
        current = chosen_country
        update_country(player, current)
        moves += 1
