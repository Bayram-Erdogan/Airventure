class Player:
    def __init__(
        self,
        username,
        game_name=None,
        balance=1000,
        player_role=None,
        plane_id=None,
        airport=None,
        current_fuel=0,
        co2_consumed=0,
        co2_budget=5000,
        flight_duration=0
    ):
        self.game_name = game_name
        self.username = username
        self.balance = balance
        self.player_role = player_role
        self.plane_id = plane_id
        self.airport = airport
        self.current_fuel = current_fuel
        self.co2_consumed = co2_consumed
        self.co2_budget = co2_budget
        self.flight_duration = flight_duration

    def __str__(self):
        return (
            f"game name: {self.game_name} "
            f"username: {self.username} "
            f"balance: {self.balance} "
            f"player_role: {self.player_role} "
            f"plane_id: {self.plane_id} "
            f"airport: {self.airport} "
            f"current_fuel: {self.current_fuel} "
            f"co2_consumed: {self.co2_consumed} "
            f"co2_budget: {self.co2_budget} "
            f"flight_duration: {self.flight_duration} "
        )