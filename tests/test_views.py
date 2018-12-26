import json

from rest_framework import status
from django.test import TestCase, Client
from django.db.utils import IntegrityError

from event_organizer.models import Player, Tournament
from event_organizer.serializers import (
    GetPlayerSerializer, TournamentListSerializer, TournamentDetailSerializer)

from tests.fixtures import gen_player, gen_tournament
# TODO: one class for one view

client = Client()
BASE_URL='//127.0.0.1:8000'


class TestPlayerDetailsViews(TestCase):

    def setUp(self):
        self.players = [
            gen_player(),
            gen_player(
                first_name="Immanuel",
                last_name="Kant",
                email="email.email1@false.com",
            )
        ]
        # for player in self.players:
        #     player.set_password("pass")

    def test_player_ok(self):
        response = client.get(
            f'{BASE_URL}/events/players/{self.players[0].id}/')
        expected = GetPlayerSerializer(self.players[0]).data
        # expected = GetPlayerSerializer(Player.objects.all(), many=True).data

        self.assertEqual(response.json(), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_player_404(self):
        response = client.get(f'{BASE_URL}/events/players/9999999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_player_delete_ok(self):
        response = client.delete(
            f'{BASE_URL}/events/players/{self.players[0].id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_player_put_ok(self):
        payload = {
            'first_name': 'Immanuel',
            'last_name': 'Bach',
            'email': "email.email1@false.com"
        }
        response = client.put(
            f'{BASE_URL}/events/players/{self.players[1].id}/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        resp_json = response.json()

        self.assertEqual(resp_json['first_name'], payload['first_name'])
        self.assertEqual(resp_json['last_name'], payload['last_name'])
        self.assertEqual(resp_json['email'], payload['email'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_player_put_error(self):
        payload = {
            'first_name': '',
            'last_name': 'Bach',
            'email': "email.email1@false.com"
        }
        response = client.put(
            f'{BASE_URL}/events/players/{self.players[1].id}/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        resp_json = response.json()
        with self.assertRaises(AssertionError):
            self.assertEqual(resp_json['first_name'], payload['first_name'])
            self.assertEqual(resp_json['last_name'], payload['last_name'])
            self.assertEqual(resp_json['email'], payload['email'])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestPlayerListViews(TestCase):

    def setUp(self):
        self.players = [
            gen_player(),
            gen_player(
                first_name="Immanuel",
                last_name="Kant",
                email="email.email1@false.com",
            )
        ]

    def test_players_post_ok(self):
        payload = {
            'first_name': 'Mr',
            'last_name': 'Postman',
            'email': 'postman@test.email.com',
            'password': 'postmanpassword',
            'password_repeat': 'postmanpassword'
        }
        response = client.post(
            f'{BASE_URL}/events/players/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        resp_json = response.json()

        self.assertEqual(resp_json['first_name'], payload['first_name'])
        self.assertEqual(resp_json['last_name'], payload['last_name'])
        self.assertEqual(resp_json['email'], payload['email'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_players_list_ok(self):
        response = client.get(f'{BASE_URL}/events/players/')
        expected = GetPlayerSerializer(self.players, many=True).data

        self.assertEqual(response.json(), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_player_post_duplicate_email(self):
        player_dicts = [
            {
                'first_name': 'Mr',
                'last_name': 'Postman',
                'email': 'john@doe.test.com',
                'password': 'postmanpassword',
                'password_repeat': 'postmanpassword'
            },
            {
                'first_name': 'Immanuel',
                'last_name': 'Kant',
                'email': 'john@doe.test.com',
                'password': 'postmanpassword',
                'password_repeat': 'postmanpassword'
            }
        ]
        for elem in player_dicts:
            response = client.post(
                f'{BASE_URL}/events/players/',
                data=json.dumps(elem),
                content_type='application/json')
        expected = {
            'non_field_errors': ['Player with this email already exists.']}

        self.assertEqual(response.json(), expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#
#         with self.assertRaises(IntegrityError):
#             for player in self.players:
#                 player.set_password("pass")  # this saves the model
#
#     # def test_players_not_unique_email(self):
#     #     self.assertRaises(IntegrityError, self.test_player_save())


class TestTournamentListViews(TestCase):

    def setUp(self):
        players = [
            gen_player(
                first_name="Fryderyk",
                last_name="Chopin",
                email="email.email@false.com",
            ),
            gen_player(
                first_name="Immanuel",
                last_name="Kant",
                email="email.email1@false.com",
            )
        ]
        self.tournaments = [
            Tournament(
                name='tournament_test_1',
                date_beginning='2019-01-02 10:00:00',
                date_ending='2019-01-03 10:00:00'
            ),
            Tournament(
                name='tournament_test_2',
                date_beginning='2019-02-02 10:00:00',
                date_ending='2019-02-03 10:00:00'
            )
        ]
        for tournament in self.tournaments:
            tournament.save()
            tournament.players.set(players)
            tournament.save()

    def cleanup_datetime_fields(self, response_json, many=True):
        """Why we need this? Because psycopg2 returns datetime in the following
        format: "YYYY-MM-DDTHH:MM:SSZ", where T and Z are actual chars T and Z.
        Serializers return times in "YYYY-MM-DD HH:MM:SS" format.
        Here we fix the discrepancy since we use the serializers to check for
        expected values.
        """
        field_names = ['date_beginning', 'date_ending']
        if many:
            for i in range(len(response_json)):
                for f in field_names:
                    response_json[i][f] = response_json[i][f].replace('T', ' ')
                    response_json[i][f] = response_json[i][f].replace('Z', '')
        else:
            for f in field_names:
                response_json[f] = response_json[f].replace('T', ' ')
                response_json[f] = response_json[f].replace('Z', '')
        return response_json

    def test_tournaments_ok(self):
        response = client.get(f'{BASE_URL}/events/tournaments/')
        expected = TournamentListSerializer(self.tournaments, many=True).data
        response_clean_time = self.cleanup_datetime_fields(response.json())

        self.assertEqual(response_clean_time, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTournamentDetailViews(TestCase):

    def setUp(self):
        player_dict = [{
            "first_name": "John",
            "last_name": "Fryc",
            "email": "Fryc@john.com",
        }]
        self.tournament = gen_tournament(player_dicts=player_dict)

    def cleanup_datetime_fields(self, response_json, many=True):
        field_names = ['date_beginning', 'date_ending']
        if many:
            for i in range(len(response_json)):
                for f in field_names:
                    response_json[i][f] = response_json[i][f].replace('T', ' ')
                    response_json[i][f] = response_json[i][f].replace('Z', '')
        else:
            for f in field_names:
                response_json[f] = response_json[f].replace('T', ' ')
                response_json[f] = response_json[f].replace('Z', '')
        return response_json

    def test_tournament_ok(self):
        response = client.get(f'{BASE_URL}/events/tournaments/{self.tournament.id}/')
        expected = TournamentDetailSerializer(self.tournament).data
        response_clean_time = self.cleanup_datetime_fields(
            response.json(), many=False)

        self.assertEqual(response_clean_time, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# class TestMatchListViews(TestCase):
