from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from event_organizer.models import Player, Tournament, Match
from event_organizer.serializers import (
    GetPlayerSerializer,
    CreatePlayerSerializer,
    UpdatePlayerSerializer,
    TournamentSerializer,
    MatchSerializer
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
        return JsonResponse(serializer_return.data, safe=False)


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
        # TODO: Remember about unique mails; if updating mail, check if a
        #       player with this mail already exists in DB
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
        serializer = TournamentSerializer(tournaments, many=True)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def match_list(request):
    if request.method == 'GET':
        matches = Match.objects.all()
        serializer = MatchSerializer(matches, many=True)
        return JsonResponse(serializer.data, safe=False)
