from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from event_organizer.models import Player, Tournament, Match
from event_organizer.serializers import (
    GetPlayerSerializer,
    CreatePlayerSerializer,
    UpdatePlayerSerializer,
    TournamentListSerializer,
    TournamentDetailSerializer,
    MatchListSerializer,
    MatchDetailSerializer,
    MatchCreateSerializer,
    TournamentCreateSerializer
)


@csrf_exempt
def player_list(request):
    """
    List all players.
    """
    if request.method == 'GET':
        players = Player.objects.all()
        serializer = GetPlayerSerializer(players, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CreatePlayerSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        new_player = Player(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email']
        )
        new_player.set_password(data['password'])  # also saves the instance

        serializer_return = GetPlayerSerializer(new_player)
        return JsonResponse(serializer_return.data, safe=False, status=201)


@csrf_exempt
def player_details(request, id):
    """
    Retrieve, update or delete a player.
    """
    try:
        player = Player.objects.get(id=id)
    except Player.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = GetPlayerSerializer(player)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        # No changing passwords here!
        data = JSONParser().parse(request)
        serializer = UpdatePlayerSerializer(player, data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        player.first_name = data['first_name']
        player.last_name = data['last_name']
        player.email_name = data['email']
        player.save()

        serializer_return = GetPlayerSerializer(player)
        return JsonResponse(serializer_return.data, safe=False)

    elif request.method == 'DELETE':
        player.delete()
        return HttpResponse(status=204)


@csrf_exempt
def tournament_list(request):
    if request.method == 'GET':
        tournaments = Tournament.objects.all()
        serializer = TournamentListSerializer(tournaments, many=True)
        return JsonResponse(serializer.data, safe=False)
# TODO: add POST using player_ids (list of integers) - new serializer
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = TournamentCreateSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        new_tournament = Tournament(
            name=data['name'],
            date_beginning=data['date_beginning'],
            date_ending=data['date_ending']
        )
        new_tournament.save()

        serializer_return = TournamentListSerializer(new_tournament)
        return JsonResponse(serializer_return.data, safe=False)


@csrf_exempt
def tournament_detail(request, id):
    try:
        tournament = Tournament.objects.get(id=id)
    except Tournament.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        tournament = Tournament.objects.get(id=id)
        serializer = TournamentDetailSerializer(tournament, many=False)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = TournamentCreateSerializer(tournament, data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        tournament.name = data['name']
        tournament.date_beginning = data['date_beginning']
        tournament.date_ending = data['date_ending']
        tournament.save()
        serializer_return = TournamentDetailSerializer(tournament)
        return JsonResponse(serializer_return.data, safe=False)

    elif request.method == 'DELETE':
        tournament.delete()
        return HttpResponse(status=204)

@csrf_exempt
def match_detail(request, tournament_id, match_id):
    try:
        match = Match.objects.get(id=match_id)
    except Tournament.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        match = Match.objects.get(id=match_id)
        serializer = MatchDetailSerializer(match, many=False)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = MatchCreateSerializer(match, data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        match.player_1_score = data['player_1_score']
        match.player_2_score = data['player_2_score']
        match.draws = data['draws']
        match.round = data['round']
        match.save()
        serializer_return = MatchDetailSerializer(match)
        return JsonResponse(serializer_return.data, safe=False)

    elif request.method == 'DELETE':
        tournament.delete()
        return HttpResponse(status=204)


@csrf_exempt
def match_list(request, tournament_id):
    if request.method == 'GET':
        matches = Match.objects.all()
        serializer = MatchListSerializer(matches, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = MatchCreateSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        new_match = Match(
            player_1_id=data['player_1_id'],
            player_2_id=data['player_2_id'],
            tournament_id=data['tournament_id'],
            player_1_score=data['player_1_score'],
            player_2_score=data['player_2_score'],
            draws=data['draws'],
            round=data['round']
        )
        new_match.save()
        serializer_return = MatchListSerializer(new_match)
        return JsonResponse(serializer_return.data, safe=False)
