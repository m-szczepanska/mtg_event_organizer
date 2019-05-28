from random import shuffle

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


from event_organizer.models import (
    Player, Tournament, TournamentPlayers, Match, Token, CreateAccountToken,
    PasswordResetToken
)
from event_organizer.pairing_view import (
    check_unique_pairings, generate_unique_pairings, generate_pairings_list,
    generate_matches, get_players_by_score, allow_duplicates_in_pairings
)
from event_organizer.serializers import (TournamentPairingsSerializer)


def tournament_pairings(tournament):  # Main function in pairings
    players_all = tournament.players.all()
    players = [player for player in players_all]
    player_ids = [player.id for player in players]

    ids_list = get_players_by_score(player_ids, players, tournament)
    pairings = generate_pairings_list(ids_list)
    past_pairings = tournament.past_round_pairings
    unique, duplicates = check_unique_pairings(pairings, past_pairings)

    pairings = allow_duplicates_in_pairings(
        unique, duplicates, pairings, past_pairings)

    if tournament.rounds_number >= tournament.round_number_next:
        generate_matches(pairings, tournament)

    tournament.update_rounds_number(number=None)

if len(Player.objects.all()) == 0:
    players = [
        {
            "first_name": "Jon",
            "last_name": "Fynkel",
            "email": "marsza11jm@gmail.com"
        },
        {
            "first_name": "Luis XS",
            "last_name": "Wargas",
            "email": "playluis@mtg.cos"
        },
        {
            "first_name": "Seth",
            "last_name": "Mantism",
            "email": "playseth@mtg.cos"
        },
        {
            "first_name": "Benek",
            "last_name": "Stark",
            "email": "playbenek@mtg.cos"
        },
        {
            "first_name": "Paulo",
            "last_name": "Rosa",
            "email": "playpaulo@mtg.cos"
        },
        {
            "first_name": "The",
            "last_name": "Jester",
            "email": "playjester@mtg.cos"
        }
    ]
    # Genereate players
    for player in players:
        new_player = Player.objects.create(
            first_name = player["first_name"],
            last_name = player["last_name"],
            email = player["email"])
        new_player.set_password("password1")

if len(Tournament.objects.all()) == 0:
    tournaments = [
        {
            "name": "Vintage",
            "date_beginning": "2019-04-24T10:00:00Z",
            "date_ending": "2019-04-25T10:00:00Z"
        },
        {
            "name": "Legacy",
            "date_beginning": "2019-05-24T10:00:00Z",
            "date_ending": "2019-05-25T10:00:00Z"
        },
        {
            "name": "Modern",
            "date_beginning": "2019-06-2T10:00:00Z",
            "date_ending": "2019-06-25T10:00:00Z"
        }
    ]
    # Generate tournaments
    for tour in tournaments:
        new_tournament = Tournament.objects.create(
            name = tour["name"],
            date_beginning = tour["date_beginning"],
            date_ending = tour["date_ending"]
        )
        new_tournament.save()

# Add players to tournaments and generate pairings
tour_vintage = Tournament.objects.get(name='Vintage')
for player in Player.objects.all():
    TournamentPlayers.objects.create(
        tournament=tour_vintage,
        player=player
    )
tournament_pairings(tour_vintage)

tour_legacy = Tournament.objects.get(name='Legacy')
for player in Player.objects.all().exclude(first_name='Benek'):
    TournamentPlayers.objects.create(
        tournament=tour_legacy,
        player=player
    )
tournament_pairings(tour_legacy)

tour_modern = Tournament.objects.get(name='Modern')
for player in Player.objects.all()[:4]:
    TournamentPlayers.objects.create(
        tournament=tour_modern,
        player=player
    )
tournament_pairings(tour_modern)
