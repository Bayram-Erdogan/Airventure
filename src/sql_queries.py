#GAMES
get_game_by_username="select * from game where username = %s"
get_games_by_username="select * from game where username = %s"
get_game_by_game_name = "select * from game where game_name= %s"
get_games_by_user_id = "select * from game where user_id= %s"
get_current_fuel= "select current_fuel from game where username= %s"
get_municipality_by_name= "select municipality from game where username = %s "

post_game_to_game_tbl_for_pilot = ("insert into game "
                                   "(user_id, username, game_name, player_role, plane_id,"
                                   "current_fuel, co2_budget, co2_consumed)"
                                   "values (%s, %s, %s, %s, %s, %s, %s, %s)")

post_game_to_game_tbl_for_smuggler = ("insert into game (user_id, username, game_name, player_role)"
                                      "values (%s, %s, %s, %s)")

update_game_airport_municipality="update game set airport=%s, municipality =%s where game_name=%s"
update_current_fuel= "update game set current_fuel = %s where username =%s"

#USER
get_user_by_username="select * from users where username = %s"
get_usernames = "select username from users"
get_balance="select balance from users where username = %s"
get_plane_id="select plane_id from users where username = %s"

update_balance="update users set balance = %s where username = %s"

post_user="insert into users (username, total_co2, plane_id, balance) values (%s, %s, %s, %s)"

#COUNTRY
get_iso_country_by_country_name="select iso_country from country where name = %s"

#AIRPORT
get_airports_ident="select ident from airport where iso_country = %s"
get_municipality_by_ident=" select municipality from airport where ident = %s"
get_locations_by_ident = "select latitude_deg, longitude_deg from airport where ident=%s"

update_place_B=" update game set municipality = %s, airport = %s where username = %s"


#PLANES
get_passenger_capacity_by_plane_id = "select passenger_capacity from planes where id=%s"
get_plane_by_plane_id="select * from planes where id = %s"
get_tank_capacity_by_id= "select tank_capacity from planes where id=%s"
