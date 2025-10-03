#GAMES
get_game_by_username="select * from game where username = %s"
post_game_to_game_tbl_for_pilot = ("insert into game (user_id, username, game_name, player_role, plane_id)"
                                   "values (%s, %s, %s, %s, %s)")
post_game_to_game_tbl_for_smuggler = ("insert into game (user_id, username, game_name, player_role)"
                                      "values (%s, %s, %s, %s)")
get_games_by_username="select game_name from game where username = %s"
get_game_by_game_name = "select * from game where game_name=%s"

update_game_airport="update game set airport=%s, municipality =%s where username=%s"

#USER
get_user_by_username="select * from users where username = %s"
get_username = "select username from users;"

post_user="insert into users (username, total_co2, plane_id, balance) values (%s, %s, %s, %s)"

#COUNTRY
get_iso_country_by_country_name="select iso_country from country where name = %s"

#AIRPORT
get_airports_ident="select ident from airport where iso_country = %s"
get_municipality_by_ident=" select municipality from airport where ident = %s"


#PLANES
get_passenger_capacity_by_plane_id = "select passenger_capacity from planes where id=%s"
