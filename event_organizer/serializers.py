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

    def validate(self, attrs):
        if attrs['password'] != attrs['password_repeat']:
            raise serializers.ValidationError('Passwords did not match.')
        player = Player.objects.filter(email=attrs['email']).first()
        if player:
            raise serializers.ValidationError(
                'Player with this email already exists.')
        return attrs


class UpdatePlayerSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    last_name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    email = serializers.EmailField(
        required=True, allow_blank=False)

    def validate(self, attrs):
        player = Player.objects.filter(email=attrs['email']).first()
        if player and player.id != self.instance.id:
            raise serializers.ValidationError(
                'Player with this email already exists.')
        return attrs


class TournamentListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField()


class TournamentCreateSerializer(serializers.Serializer):
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField()

# TournamentCreateSerializer for tournament_list POST

class MatchSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    player_1 = GetPlayerSerializer(required=True)
    player_2 = GetPlayerSerializer(required=True)
    player_1_score = serializers.IntegerField(max_value=3, min_value=0)
    player_2_score = serializers.IntegerField(max_value=3, min_value=0)
    draws = serializers.IntegerField(max_value=5, min_value=0)


class MatchListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    player_1 = GetPlayerSerializer(required=True)
    player_2 = GetPlayerSerializer(required=True)
    player_1_score = serializers.IntegerField(max_value=3, min_value=0)
    player_2_score = serializers.IntegerField(max_value=3, min_value=0)
    draws = serializers.IntegerField(max_value=5, min_value=0)


class TournamentDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    date_beginning = serializers.DateTimeField()
    date_ending = serializers.DateTimeField()
    players = GetPlayerSerializer(many=True)
    matches = MatchSerializer(many=True, read_only=True)
