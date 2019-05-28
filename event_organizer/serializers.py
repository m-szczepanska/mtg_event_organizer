from rest_framework import serializers

from event_organizer.models import Player, Tournament, Match
from player_services.services import (MinimumLengthValidator,
    NumericPasswordValidator)


class GetPlayerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    last_name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    email = serializers.EmailField(
        required=True, allow_blank=False)
    full_name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)


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
        elif not MinimumLengthValidator.validate(data['password']):
            raise serializers.ValidationError(
                'Passwords must have at least 8 characters')
        elif not NumericPasswordValidator.validate(data['password']):
            raise serializers.ValidationError(
                'Password must contain at least 1 digit')

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


class TournamentListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField(required=False)
    is_finished = serializers.BooleanField(read_only=True)


class TournamentCreateSerializer(serializers.Serializer):
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField(required=False)


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


class MatchSubmitScoreSerializer(serializers.Serializer):
    player_1_score = serializers.IntegerField(max_value=3, min_value=0)
    player_2_score = serializers.IntegerField(max_value=3, min_value=0)
    draws = serializers.IntegerField(max_value=5, min_value=0)


class MatchDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    player_1_id = serializers.IntegerField(required=True)
    player_2_id = serializers.IntegerField(required=True)
    player_1_name = serializers.CharField(read_only=True)
    player_2_name = serializers.CharField(read_only=True)
    tournament_id = serializers.IntegerField(required=True)
    player_1_score = serializers.IntegerField(max_value=3, min_value=0)
    player_2_score = serializers.IntegerField(max_value=3, min_value=0)
    draws = serializers.IntegerField(max_value=5, min_value=0)
    round = serializers.IntegerField(max_value=50, min_value=0)
    is_finished = serializers.BooleanField(read_only=True)


class StandingsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    score = serializers.IntegerField(read_only=True)


class TournamentDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField(required=False)
    rounds_number = serializers.IntegerField(read_only=True)
    players = GetPlayerSerializer(many=True)
    current_round = MatchDetailSerializer(many=True, read_only=True)
    past_rounds = MatchDetailSerializer(many=True, read_only=True)
    is_finished = serializers.BooleanField(read_only=True)
    is_current_round_finished = serializers.BooleanField(read_only=True)
    standings = StandingsSerializer(many=True, read_only=True)


class AddPlayersToTournamentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    date_beginning = serializers.DateTimeField(read_only=True)
    date_ending = serializers.DateTimeField(read_only=True, required=False)
    players = GetPlayerSerializer(read_only=True, many=True)


class TournamentPairingsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    date_beginning = serializers.DateTimeField(read_only=True)
    date_ending = serializers.DateTimeField(read_only=True, required=False)
    players = GetPlayerSerializer(read_only=True, many=True)
    current_round = MatchDetailSerializer(many=True, read_only=True)
    is_current_round_finished = serializers.BooleanField(read_only=True)
    rounds_number = serializers.IntegerField(read_only=True)
    standings = StandingsSerializer(many=True, read_only=True)


class PlayersCurrentTournaments(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField(required=False)
    current_round = MatchDetailSerializer(many=True, read_only=True)
    rounds_number = serializers.IntegerField(read_only=True)
    current_round_number = serializers.IntegerField(read_only=True)


class PlayersTournamentHistory(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField(required=False)
    is_finished = serializers.BooleanField(read_only=True)
    rounds_number = serializers.IntegerField(read_only=True)
    score = serializers.SerializerMethodField()

    class Meta:
        model = Player

    def score(self, Tournament):
        return Tournament.score_by_player_id(self.id)


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
                'Email dosn\'t exists in the database')
        if not player.check_password(data['password']):
            raise serializers.ValidationError(
                'Password inncorect')
        return data


class TokenSerializer(serializers.Serializer):
    player_id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField()
    uuid = serializers.CharField(
        required=True, allow_blank=False)
    is_expired = serializers.BooleanField(read_only=True)


class RegisterRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
            required=True, allow_blank=False)

    def validate(self, data):
        # TODO: make mail not case sensitive
        player = Player.objects.filter(email=data['email']).first()
        if player:
            raise serializers.ValidationError(
                'Email already exists in the database')
        return data


class RegisterTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
            required=True, allow_blank=False)
    created_at = serializers.DateTimeField()
    uuid = serializers.CharField(
        required=True, allow_blank=False)
    was_used = serializers.BooleanField(read_only=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
            required=True, allow_blank=False)

    def validate(self, data):
        # TODO: make mail not case sensitive
        player = Player.objects.filter(email=data['email']).first()
        if not player:
            raise serializers.ValidationError(
                'Email does not exist in the database')
        return data


class PasswordResetTokenSerializer(serializers.Serializer):
    player = GetPlayerSerializer(many=False)
    created_at = serializers.DateTimeField()
    uuid = serializers.CharField(
        required=True, allow_blank=False)
    was_used = serializers.BooleanField(read_only=True)


class PasswordPlayerSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    password_repeat = serializers.CharField(
        required=True, allow_blank=False, max_length=255)

    def validate(self, data):
        if data['password'] != data['password_repeat']:
            raise serializers.ValidationError('Passwords did not match.')

        elif not MinimumLengthValidator.validate(data['password']):
            raise serializers.ValidationError(
                'Passwords must have at least 8 characters')
        elif not NumericPasswordValidator.validate(data['password']):
            raise serializers.ValidationError(
                'Password must contain at least 1 digit')
        return data


class TounamentPlayersDrop(serializers.Serializer):
    player_dropped = serializers.BooleanField(required=True)


class TounamentPlayersDrop2(serializers.Serializer):
    tournament = TournamentDetailSerializer(read_only=True)
    player = GetPlayerSerializer(read_only=True)
    player_dropped = serializers.BooleanField(required=True)
