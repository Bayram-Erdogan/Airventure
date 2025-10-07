#GAMES
get_game_by_username="select * from game where username = %s"
get_games_by_username="select * from game where username = %s"
get_game_by_game_name = "select * from game where game_name = %s"
get_game_by_game_id = "select * from game where id = %s"
get_games_by_user_id = "select * from game where user_id = %s"
get_current_fuel= "select current_fuel from game where id = %s"
get_municipality_by_name= "select municipality from game where username = %s "
get_flight_duration_minutes_by_game_id = "select flight_duration_minutes from game where id = %s"
get_departure_airport_ident_by_game_id= "select airport from game where id = %s"

post_game_to_game_tbl_for_pilot = ("insert into game "
                                   "(user_id, username, game_name, player_role, plane_id,"
                                   "current_fuel, co2_budget, co2_consumed)"
                                   "values (%s, %s, %s, %s, %s, %s, %s, %s)")

post_game_to_game_tbl_for_smuggler = ("insert into game (user_id, username, game_name, player_role)"
                                      "values (%s, %s, %s, %s)")

update_game_airport_municipality="update game set airport=%s, municipality =%s where game_name = %s"
update_current_fuel= "update game set current_fuel = %s where id =%s"
update_game_by_game_id = ("update game set municipality = %s, airport = %s, current_fuel = %s,"
                          "co2_consumed = %s, co2_budget = %s, flight_duration_minutes = %s "
                          "where id = %s")

#USER
get_user_by_username="select * from users where username = %s"
get_usernames = "select username from users"
get_balance="select balance from users where id = %s"
get_user_id_by_username = "select id from users where username = %s"


update_user_balance_by_user_id="update users set balance = %s where id = %s"
update_user_plane_id = "update users set plane_id = %s where id = %s"


update_balance="update users set balance = %s where username = %s"
update_user_last_login="update users set last_login = %s where id = %s"

post_user="insert into users (username, total_co2, plane_id, balance) values (%s, %s, %s, %s)"

#COUNTRY
get_iso_country_by_country_name="select iso_country from country where name = %s"
get_iso_country_by_airport_ident = "select iso_country from airport where ident = %s"

#AIRPORT
get_airports_ident="select ident from airport where iso_country = %s"
get_municipality_by_ident=" select municipality from airport where ident = %s"
get_locations_by_ident = "select latitude_deg, longitude_deg from airport where ident = %s"
get_airport_by_ident = "select name from airport where ident = %s"

update_place_B=" update game set municipality = %s, airport = %s where username = %s"


#PLANES
get_passenger_capacity_by_plane_id = "select passenger_capacity from planes where id = %s"
get_plane_by_plane_id="select * from planes where id = %s"
get_tank_capacity_by_id= "select tank_capacity from planes where id = %s"
get_ticket_price_by_plane_id = "select ticket from planes where id = %s"
get_plane_id="select plane_id from users where username = %s"
get_max_speed_by_plane_id = "select max_speed from planes where id = %s"

#FLIGHT_LOG
post_flight_log=("insert into flight_log "
                 "(game_id, plane_id, departure_airport, arrival_airport, flight_duration,"
                 "passengers_count, revenue, weather) "
                 "values (%s, %s, %s, %s, %s, %s, %s, %s)")

#GOAL
get_weather="select description from goal"
get_goal_id ="select id from goal where description = %s"

#GOAL_REACHED
get_goal_reached = "select 1 from goal_reached where game_id=%s and goal_id = %s;"
post_goal_reached="insert into goal_reached (game_id, goal_id, user_id) values (%s, %s, %s)"