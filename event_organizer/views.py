from random import random

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from event_organizer.models import (
Player, Tournament, Match, Token, CreateAccountToken, PasswordResetToken
)
from event_organizer.serializers import (
    GetPlayerSerializer, CreatePlayerSerializer, UpdatePlayerSerializer,
    TournamentListSerializer, TournamentDetailSerializer, MatchListSerializer,
    MatchDetailSerializer, MatchCreateSerializer, TournamentCreateSerializer,
    AddPlayersToTournamentSerializer, TournamentPairingsSerializer,
    PlayersCurrentTournaments, PlayersTournamentHistory, TokenSerializer,
    LoginSerializer, RegisterTokenSerializer, RegisterRequestSerializer,
    PasswordResetRequestSerializer, PasswordResetTokenSerializer,
    PasswordPlayerSerializer
)
from event_organizer.decorators import view_auth
from player_services.services import (
    send_password_reset_mail, check_token_validity, send_user_register_mail,
    MinimumLengthValidator, NumericPasswordValidator)


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
def players_current_tournaments(request, id):
    try:
        player = Player.objects.get(id=id)
    except Player.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        if len(player.get_current_tournaments()) == 1:
            serializer = TournamentPairingsSerializer(
                player.get_current_tournaments()[0], many=False)
        elif len(player.get_current_tournaments()) > 1:
            serializer = PlayersCurrentTournaments(
                player.get_current_tournaments(), many=True)
        else:
            return []
    return JsonResponse(serializer.data, safe=False)

# @view_auth
@csrf_exempt
def player_history(request, id):
    try:
        player = Player.objects.get(id=id)
    except Player.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        tournaments = player.get_player_history()
        serializer = PlayersTournamentHistory(tournaments, many=True)

        # This should be doable with a SerializerMethodField?
        data = serializer.data
        zipped = zip(tournaments, data)
        # a = [1, 2]
        # b = ['a', 'b', 'c']
        # zipped = zip(a, b)  # [[1, 'a'], [2, 'b']]
        for tournament, tournament_dict in zipped:
            tournament_dict['score'] = tournament.score_by_player_id(id)
        return JsonResponse(data, safe=False)


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

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = TournamentCreateSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        else:
            new_tournament = Tournament(
                name=data['name'],
                date_beginning=data['date_beginning'],
                date_ending=data['date_ending']
                )
            new_tournament.save()

            serializer_return = TournamentListSerializer(new_tournament)
            return JsonResponse(serializer_return.data, safe=False, status=201)


@csrf_exempt
def add_players_to_tournament(request, id):
    if request.method == 'POST':
        try:
            tournament = Tournament.objects.get(id=id)
        except Tournament.DoesNotExist:
            return HttpResponse(status=404)

        data = JSONParser().parse(request) # get JSON from request
        player_ids = data.get('player_ids', [])

        # Cannot do this in serializer since you can't add players to tournament
        # there. Moving validation logic there would mean you have to query for
        # players in two places which is inefficient and ugly.
        missing_ids = []
        for player_id in player_ids:
            try:
                player = Player.objects.get(id=player_id)
                tournament.players.add(player)
            except Player.DoesNotExist:
                missing_ids.append(player_id)

        serializer = AddPlayersToTournamentSerializer(tournament)
        return_data = {
            "data": serializer.data,
            "errors": {"player_id_missing": missing_ids}
        }

        return JsonResponse(return_data, safe=False)


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
        match = Match.objects.get(id=match_id, tournament_id=tournament_id)
    except Match.DoesNotExist:
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
        match.delete()
        return HttpResponse(status=204)


@csrf_exempt
def match_list(request, tournament_id):
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        matches = Match.objects.filter(tournament_id=tournament_id).all()
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
            tournament_id=tournament_id,
            player_1_score=data['player_1_score'],
            player_2_score=data['player_2_score'],
            draws=data['draws'],
            round=data['round']
        )
        new_match.save()
        serializer_return = MatchListSerializer(new_match)
        return JsonResponse(serializer_return.data, safe=False, status=201)


@csrf_exempt
def login(request):
    """
    Login a player.
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = LoginSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        player = Player.objects.get(email=data['email'])
        token = Token(player_id=player.id)
        token.save()
        serializer_return = TokenSerializer(token)
        return JsonResponse(serializer_return.data, safe=False, status=201)

@csrf_exempt
def register_request_view(request):
    """
    Register request from a player.
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = RegisterRequestSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        token = CreateAccountToken(email=data['email'])
        token.save()
        send_user_register_mail(data['email'], token.uuid)
        serializer_return = RegisterTokenSerializer(token)
        return JsonResponse(serializer_return.data, safe=False, status=201)


@csrf_exempt
def register_view(request, token_uuid):
    """
    Register a player.
    """
    if request.method == 'POST':
        check_result = check_token_validity(CreateAccountToken, token_uuid)
        if check_result:
            return JsonResponse(check_result, status=403)

        else:
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
def password_reset_request(request):
    """
    Password reset request from a player.
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = PasswordResetRequestSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        player = Player.objects.get(email=data['email'])
        token = PasswordResetToken(player=player)
        token.save()
        send_password_reset_mail(data['email'], token.uuid)
        serializer_return = PasswordResetTokenSerializer(token)
        return JsonResponse(serializer_return.data, safe=False, status=201)


@csrf_exempt
def reset_password_view(request, token_uuid):
    """
    Reset players password.
    """
    if request.method == 'POST':
        try:
            token = PasswordResetToken.objects.get(uuid=token_uuid)
            if not token.is_valid:
                context = {"error": "Token expired"}
                return JsonResponse(context, status=403)
        except:
            context = {"error": "Invalid token"}
            return JsonResponse(context, status=403)

        player = token.player
        data = JSONParser().parse(request)
        serializer = PasswordPlayerSerializer(player, data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        player.set_password(data['password'])  # also saves the instance
        serializer_return = GetPlayerSerializer(player)
        return JsonResponse(serializer_return.data, safe=False, status=201)
