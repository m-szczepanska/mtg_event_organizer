from random import shuffle

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from event_organizer.models import Player, Tournament, Match
from event_organizer.serializers import (TournamentPairingsSerializer)


def check_unique_pairings(current_pairings, past_pairings):
    duplicate_index = []
    unique = True
    for i in range(len(current_pairings)):
        pair = current_pairings[i]
        if len(pair) < 2:
            pair = [pair[0], None]
        if pair in past_pairings or pair[::-1] in past_pairings:
            unique = False
            duplicate_index.append(i)
    return unique, duplicate_index

def generate_unique_pairings(duplicates, pairings):
    if isinstance(duplicates, int): # if duplicates is only one number
        duplicates = [duplicates]
    for duplicate in duplicates:
        duplicate_pair = pairings[duplicate]
        len_pairings = len(pairings)
        if duplicate < (len_pairings - 1):
            another_pair_to_change = pairings[duplicate + 1]
            if len(another_pair_to_change) > 1 and len(duplicate_pair) > 1:
                pairings[duplicate] = [duplicate_pair[0], another_pair_to_change[0]]
            # change the value of a pair in list in place
            elif len(another_pair_to_change) > 1 and len(duplicate_pair) < 2:
                pairings[duplicate] = [duplicate_pair[0], another_pair_to_change[0]]
                pairings[duplicate + 1] = [another_pair_to_change[1]]
            else: # if another pair to shuffle its player ids contains of one player id
                new_pairs = [duplicate_pair[0], another_pair_to_change[0]], [duplicate_pair[1]]
                pairings[duplicate] = [duplicate_pair[0], another_pair_to_change[0]]
                pairings[duplicate + 1] = [duplicate_pair[1]]
        else: # if duplicate is the last index of list pairings
            another_pair_to_change = pairings[duplicate - 1]
            pairings[duplicate - 1] = [another_pair_to_change[0], duplicate_pair[0]]
            if len(another_pair_to_change) > 1 and len(duplicate_pair) > 1:
                pairings[duplicate] = [another_pair_to_change[1], duplicate_pair[1]]
            elif len(another_pair_to_change) > 1 and len(duplicate_pair) < 2:
                pairings[duplicate] = [another_pair_to_change[1]]
            else:
                pairings[duplicate] = [duplicate_pair[1]]
    return pairings

def generate_pairings_list(player_ids):
    # pairings format e.g [[1, 5], [2, 4], [3, 6]]
    # shuffle(player_ids)
    pairings = []
    pairing = []
    while player_ids:
        if len(pairing) < 2:
            pairing.append(player_ids.pop(0))
        else:
            pairings.append(pairing)
            pairing = []
    if pairing:  # odd number of players
        pairings.append(pairing)

    return pairings

def generate_matches(pairings, tournament):
    round_num = tournament.round_number_next

    for pair in pairings:
        if len(pair) == 2:
            match = Match(
                player_1_id=pair[0],
                player_2_id=pair[1],
                tournament_id=tournament.id,
                player_1_score=0,
                player_2_score=0,
                draws=0,
                round=round_num
            )
        else:
            match = Match(
                player_1_id=pair[0],
                player_2_id=None,
                tournament_id=tournament.id,
                player_1_score=2,
                player_2_score=0,
                draws=0,
                round=round_num
            )
        match.save()

def get_players_by_score(player_ids, players, tournament):
    results = {}
    # Creates histogram => result = {"9": [1, 3], "6": [2, 4]}
    for player in players:
        player_score = player.get_score_in_tournament(
            tournament_id=tournament.id)
        if player_score not in results:
            results[player_score] = []
        results[player_score].append(player.id)

    for score in results:  # Shuffle ids within a score (pair)
        shuffle(results[score])
    sorted_results = sorted(results.items(), reverse=True)
    ids_list = []
    for ids in sorted_results:
        ids_list += ids[1]

    return ids_list

def allow_duplicates_in_pairings(unique, duplicates, pairings, past_pairings):
    # allow duplicates if while goes over 4 times
    counter = 0
    while unique != True:
        if counter < 5:
            pairings = generate_unique_pairings(duplicates, pairings)
            unique, duplicates = check_unique_pairings(pairings, past_pairings)
            counter += 1
            print(counter)
        else:
            unique = True

    return pairings


@csrf_exempt
def tournament_pairings(request, tournament_id):  # Main function in pairings
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return HttpResponse(status=404)

    if not tournament.is_current_round_finished:
        return HttpResponse("current round not finished yet")

    players = tournament.players.all()
    player_ids = [player.id for player in tournament.players.all()]

    if player_ids:
        ids_list = get_players_by_score(player_ids, players, tournament)
        pairings = generate_pairings_list(ids_list)
        past_pairings = tournament.past_round_pairings
        unique, duplicates = check_unique_pairings(pairings, past_pairings)

        pairings = allow_duplicates_in_pairings(
            unique, duplicates, pairings, past_pairings)

        generate_matches(pairings, tournament)

        tournament.update_rounds_number(number=None)
        serializer_return = TournamentPairingsSerializer(tournament)
        return JsonResponse(serializer_return.data, safe=False)

    else:
        return HttpResponse(
        'No players in this tournament yet. Add players first.')
