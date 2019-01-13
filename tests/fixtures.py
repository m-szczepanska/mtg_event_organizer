from event_organizer.models import Player, Tournament, Match

#
# Design Pattern: Factory
def gen_player(
        first_name="John",
        last_name="Doe",
        email="john@doe.test.com",
        password="P@ssw0rd!"
    ):
    player = Player(
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    player.set_password(password)

    return player

def gen_tournament(
        name='test tournament 1',
        date_beginning='2018-12-17 10:00:00',
        date_ending='2018-12-17 10:00:00',
        player_dicts=None
        # [
        # {"first_name": "John"},
        # {"last_name": "Fryc"},
        # {"email": "Fryc@john.com"},
        # {"password": "Fryc"}
        # ]
    ):
    tournament = Tournament(
        name=name,
        date_beginning=date_beginning,
        date_ending=date_ending,
    )
    if player_dicts:
        tournament.save()
        players = [gen_player(**player_dict) for player_dict in player_dicts]
        tournament.players.set(players)
    tournament.save()

    return tournament
