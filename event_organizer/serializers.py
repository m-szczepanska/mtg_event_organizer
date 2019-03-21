from rest_framework import serializers

from event_organizer.models import Player, Tournament, Match


class GetPlayerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    last_name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    email = serializers.EmailField(
        required=True, allow_blank=False)


class CreatePlayerSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    last_name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    email = serializers.EmailField(
        required=True, allow_blank=False)
    password = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    password_repeat = serializers.CharField(
        required=True, allow_blank=False, max_length=255)

    def validate(self, data):
        if data['password'] != data['password_repeat']:
            raise serializers.ValidationError('Passwords did not match.')
        player = Player.objects.filter(email=data['email']).first()
        if player:
            raise serializers.ValidationError(
                'Player with this email already exists.')
        return data


class UpdatePlayerSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    last_name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    email = serializers.EmailField(
        required=True, allow_blank=False)

    def validate(self, data):
        player = Player.objects.filter(email=data['email']).first()
        if player and player.id != self.instance.id:
            raise serializers.ValidationError(
                'Player with this email already exists.')
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True, allow_blank=False)
    password = serializers.CharField(
        required=True, allow_blank=False, max_length=255)

    def validate(self, data):
        # TODO: make mail not case sensitive
        player = Player.objects.filter(email=data['email']).first()
        if not player:
            raise serializers.ValidationError(
                'Email dosn\'t exists in the database .')
        if not player.check_password(data['password']):
            raise serializers.ValidationError(
                'Password inncorect.')
        return data

class TokenSerializer(serializers.Serializer):
    player_id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField()
    uuid = serializers.CharField(
        required=True, allow_blank=False)
    is_expired = serializers.BooleanField(read_only=True)


class TournamentListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField()
    is_finished = serializers.BooleanField(read_only=True)


class TournamentCreateSerializer(serializers.Serializer):
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField()


class MatchListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    player_1_score = serializers.IntegerField(max_value=3, min_value=0)
    player_2_score = serializers.IntegerField(max_value=3, min_value=0)
    draws = serializers.IntegerField(max_value=5, min_value=0)
    round = serializers.IntegerField(max_value=50, min_value=0)


class MatchCreateSerializer(serializers.Serializer):
    player_1_id = serializers.IntegerField(required=True)
    player_2_id = serializers.IntegerField(required=False)
    player_1_score = serializers.IntegerField(max_value=3, min_value=0)
    player_2_score = serializers.IntegerField(max_value=3, min_value=0)
    draws = serializers.IntegerField(max_value=5, min_value=0)
    round = serializers.IntegerField(max_value=50, min_value=0)


class MatchDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    player_1_id = serializers.IntegerField(required=True)
    player_2_id = serializers.IntegerField(required=True)
    tournament_id = serializers.IntegerField(required=True)
    player_1_score = serializers.IntegerField(max_value=3, min_value=0)
    player_2_score = serializers.IntegerField(max_value=3, min_value=0)
    draws = serializers.IntegerField(max_value=5, min_value=0)
    round = serializers.IntegerField(max_value=50, min_value=0)


class TournamentDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField()
    rounds_number = serializers.IntegerField(read_only=True)
    players = GetPlayerSerializer(many=True)
    current_round = MatchDetailSerializer(many=True, read_only=True)
    past_rounds = MatchDetailSerializer(many=True, read_only=True)
    is_finished = serializers.BooleanField(read_only=True)


class AddPlayersToTournamentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    date_beginning = serializers.DateTimeField(read_only=True)
    date_ending = serializers.DateTimeField(read_only=True)
    players = GetPlayerSerializer(read_only=True, many=True)


class TournamentPairingsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    date_beginning = serializers.DateTimeField(read_only=True)
    date_ending = serializers.DateTimeField(read_only=True)
    players = GetPlayerSerializer(read_only=True, many=True)
    current_round = MatchDetailSerializer(many=True, read_only=True)
    is_current_round_finished = serializers.BooleanField(read_only=True)
    rounds_number = serializers.IntegerField(read_only=True)


class PlayersCurrentTournaments(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField()
    current_round = MatchDetailSerializer(many=True, read_only=True)
    rounds_number = serializers.IntegerField(read_only=True)


class PlayersTournamentHistory(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField()
    is_finished = serializers.BooleanField(read_only=True)
    # scores = serializers.CharField(read_only=True)
    rounds_number = serializers.IntegerField(read_only=True)
