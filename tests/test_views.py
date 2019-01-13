import json

from rest_framework import status
from django.test import TestCase, Client
from django.db.utils import IntegrityError

from event_organizer.models import Player, Tournament, Match
from event_organizer.serializers import (
    GetPlayerSerializer, TournamentListSerializer, TournamentDetailSerializer,
    MatchDetailSerializer, MatchListSerializer, AddPlayersToTournamentSerializer)

from tests.fixtures import gen_player, gen_tournament

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

    def test_player_put_400_for_empy_field(self):
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

    def test_players_list_ok(self):
        response = client.get(f'{BASE_URL}/events/players/')
        expected = GetPlayerSerializer(self.players, many=True).data

        self.assertEqual(response.json(), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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


class TestTournamentListViews(TestCase):

    def test_tournaments_ok(self):
        response = client.get(f'{BASE_URL}/events/tournaments/')
        expected = TournamentListSerializer(self.tournaments, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)

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

    def test_tournaments_post_ok(self):
        payload = {
            "name": "test_post_tournament",
            "date_beginning": "2019-12-13 10:00:00",
            "date_ending": "2019-12-15 16:00:00",
        }
        response = client.post(
            f'{BASE_URL}/events/tournaments/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        response_clean_time = self.cleanup_datetime_fields(
            response.json(), many=False)

        self.assertEqual(
            response_clean_time['name'], payload['name'])
        self.assertEqual(
            response_clean_time['date_beginning'], payload['date_beginning'])
        self.assertEqual(
            response_clean_time['date_ending'], payload['date_ending'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_tournaments_post_404(self):
        payload = {
            "name": "",
            "date_beginning": "2019-12-13 10:00:00",
            "date_ending": "2019-12-15 16:00:00",

        }
        response = client.post(
            f'{BASE_URL}/events/tournaments/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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

    # 404 - GET missing
    # 201 - DELETE
    # 404 - DELETE missing
    # 200 - PUT ok
    # 400 - PUT not ok - for all failure cases
    def test_tournament_ok(self):
        response = client.get(
            f'{BASE_URL}/events/tournaments/{self.tournament.id}/'
        )
        expected = TournamentDetailSerializer(self.tournament).data
        response_clean_time = self.cleanup_datetime_fields(
            response.json(), many=False)

        self.assertEqual(response_clean_time, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_404(self):
        response = client.get(f'{BASE_URL}/events/tournaments/9999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_tournament_delete_ok(self):
        response = client.delete(
            f'{BASE_URL}/events/tournaments/{self.tournament.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_tournament_delete_404(self):
        response = client.delete(f'{BASE_URL}/events/tournaments/9999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tournament_put_ok(self):
        payload = {
            "name": "test tournament 1",
            "date_beginning": "2019-12-13 10:00:00",
            "date_ending": "2019-12-15 16:00:00"
        }
        response = client.put(
            f'{BASE_URL}/events/tournaments/{self.tournament.id}/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        response_clean_time = self.cleanup_datetime_fields(
            response.json(), many=False)

        self.assertEqual(
            response_clean_time['name'], payload['name'])
        self.assertEqual(
            response_clean_time['date_beginning'], payload['date_beginning'])
        self.assertEqual(
            response_clean_time['date_ending'], payload['date_ending'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_tournament_put_400(self):
        payload = {
            "name": "test tournament 1",
            "date_beginning": "2019-12-13 10:00:00",
            "date_ending": " "
        }
        response = client.put(
            f'{BASE_URL}/events/tournaments/{self.tournament.id}/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestMatchListView(TestCase):
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
                email="email.email@mailu.com",
            ),
            gen_player(
                first_name="Muniek",
                last_name="Kot",
                email="email.false@mailu.com",
            )
        ]
        tournament = Tournament(
            name='tournament_test_1',
            date_beginning='2019-01-02 10:00:00',
            date_ending='2019-01-03 10:00:00'
        )
        # TEMP: set players
        tournament.save()
        tournament.players.set(players)
        self.matches = [
            Match(
                player_1_id=players[0].id,
                player_2_id=players[1].id,
                tournament_id=tournament.id,
                player_1_score=1,
                player_2_score=2,
                draws=0,
                round=1),
            Match(
                player_1_id=players[1].id,
                player_2_id=players[2].id,
                tournament_id=tournament.id,
                player_1_score=2,
                player_2_score=0,
                draws=0,
                round=2)
        ]
        for match in self.matches:
            match.save()

        # tournament_2 made to check if matches from another tournament
        # don't show up in match_list
        tournament_2 = Tournament(
            name='tournament_test_2',
            date_beginning='2019-01-02 10:00:00',
            date_ending='2019-01-03 10:00:00'
        )
        tournament_2.save()
        tournament_2.players.set(players)
        Match(
            player_1_id=players[2].id,
            player_2_id=players[1].id,
            tournament_id=tournament_2.id,
            player_1_score=2,
            player_2_score=1,
            draws=0,
            round=1
        ).save()

    def test_match_get_ok(self):
        response = client.get(
            f'{BASE_URL}/events/tournaments/{self.matches[0].tournament_id}/matches/'
        )
        expected = MatchListSerializer(self.matches, many=True).data

        self.assertEqual(response.json(), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_match_post_ok(self):
        payload = {
            "player_1_id": self.matches[0].player_1_id,
            "player_2_id": self.matches[0].player_2_id,
            "player_1_score": self.matches[0].player_1_score,
            "player_2_score": self.matches[0].player_2_score,
            "draws": self.matches[0].draws,
            "round": self.matches[0].round,
        }
        response = client.post(
            f'{BASE_URL}/events/tournaments/{self.matches[0].tournament_id}/matches/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(
            response.json()['player_1_score'], payload['player_1_score'])
        self.assertEqual(
            response.json()['player_2_score'], payload['player_2_score'])
        self.assertEqual(
            response.json()['draws'], payload['draws'])
        self.assertEqual(
            response.json()['round'], payload['round'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_match_post_404(self):
        # confirm you can't create a match in nonexistent tournament
        payload = {
            "player_1_id": self.matches[0].player_1_id,
            "player_2_id": self.matches[0].player_2_id,
            "player_1_score": self.matches[0].player_1_score,
            "player_2_score": self.matches[0].player_2_score,
            "draws": self.matches[0].draws,
            "round": self.matches[0].round,
        }
        response = client.post(
            f'{BASE_URL}/events/tournaments/9999/matches/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND)


class TestMatchDetailView(TestCase):
    base_url = f'{BASE_URL}/events/tournaments'

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
                email="email.email@mailu.com",
            )
        ]
        tournament = Tournament(
            name='tournament_test_1',
            date_beginning='2019-01-02 10:00:00',
            date_ending='2019-01-03 10:00:00'
        )
        # TEMP: set players
        tournament.save()
        tournament.players.set(players)
        self.match = Match(
            player_1_id=players[0].id,
            player_2_id=players[1].id,
            tournament_id=tournament.id,
            player_1_score=1,
            player_2_score=2,
            draws=0,
            round=1
        )
        self.match.save()

    def test_match_get_ok(self):
        response = client.get(
            f'{self.base_url}/{self.match.tournament_id}/matches/{self.match.id}/'
        )
        expected = MatchDetailSerializer(self.match).data

        self.assertEqual(response.json(), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_match_put_ok(self):
        payload = {
            "player_1_id": self.match.player_1_id,
            "player_2_id": self.match.player_2_id,
            "tournament_id": self.match.tournament.id,
            "player_1_score": 1,
            "player_2_score": 1,
            "draws": 1,
            "round": self.match.round
        }

        response = client.put(
            f'{self.base_url}/{self.match.tournament_id}/matches/{self.match.id}/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(
            response.json()['player_1_id'], payload['player_1_id'])
        self.assertEqual(
            response.json()['player_2_id'], payload['player_2_id'])
        self.assertEqual(
            response.json()['tournament_id'], payload['tournament_id'])
        self.assertEqual(
            response.json()['player_1_score'], payload['player_1_score'])
        self.assertEqual(
            response.json()['player_2_score'], payload['player_2_score'])
        self.assertEqual(
            response.json()['draws'], payload['draws'])
        self.assertEqual(
            response.json()['round'], payload['round'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_match_put_400_for_player_score(self):
        payload = {
            "player_1_id": self.match.player_1_id,
            "player_2_id": self.match.player_2_id,
            "tournament_id": self.match.tournament.id,
            "player_1_score": 11,
            "player_2_score": 1,
            "draws": 1,
            "round": self.match.round
        }
        response = client.put(
            f'{self.base_url}/{self.match.tournament_id}/matches/{self.match.id}/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_match_put_400_for_empty_field(self):
        payload = {
            "player_1_id": self.match.player_1_id,
            "player_2_id": self.match.player_2_id,
            "tournament_id": "",
            "player_1_score": 11,
            "player_2_score": 1,
            "draws": 1,
            "round": self.match.round
        }
        response = client.put(
            f'{self.base_url}/{self.match.tournament_id}/matches/{self.match.id}/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_match_delete_ok(self):
        response = client.delete(
            f'{self.base_url}/{self.match.tournament_id}/matches/{self.match.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_match_delete_404_tournament_missing(self):
        tournament = Tournament(
            name='tournament_delete_test',
            date_beginning='2019-01-02 10:00:00',
            date_ending='2019-01-03 10:00:00'
        )
        tournament.save()

        response = client.delete(
            f'{self.base_url}/{tournament.id}/matches/{self.match.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TestAddPlayersToTournament(TestCase):
    def setUp(self):
        self.players = [
            Player(
                first_name="Fryderyk",
                last_name="Chopin",
                email="email.email@false.com",
            ),
            Player(
                first_name="Immanuel",
                last_name="Kant",
                email="email.email@mailu.com",
            )
        ]
        self.tournament = Tournament(
            name='tournament_test_1',
            date_beginning='2019-01-02 10:00:00',
            date_ending='2019-01-03 10:00:00'
        )
        self.tournament.save()
        for player in self.players:
            player.save()

    def test_add_player_to_tournament_ok(self):
        payload = {
            "player_ids": [self.players[0].id]
        }
        response = client.post(
            f'{BASE_URL}/events/tournaments/{self.tournament.id}/add_players/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        errors = response.json()['errors']
        data = response.json()['data']

        self.assertEqual(len(errors['player_id_missing']), 0)
        self.assertEqual(len(data['players']), 1)
        self.assertEqual(data['players'][0]["id"], payload["player_ids"][0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_player_to_tournament_wrong_player_id(self):
        payload = {
            "player_ids": [999]
        }
        response = client.post(
            f'{BASE_URL}/events/tournaments/{self.tournament.id}/add_players/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        errors = response.json()['errors']
        data = response.json()['data']

        self.assertEqual(len(errors['player_id_missing']), 1)
        self.assertEqual(len(data['players']), 0)
        self.assertEqual(errors['player_id_missing'][0], payload["player_ids"][0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_player_to_tournament_wrong_tournament_id(self):
        payload = {
            "player_ids": [[self.players[0].id]]
        }
        response = client.post(
            f'{BASE_URL}/events/tournaments/999/add_players/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_two_players_to_tournament_ok(self):
        payload = {
            "player_ids": [self.players[0].id, self.players[1].id]
        }
        response = client.post(
            f'{BASE_URL}/events/tournaments/{self.tournament.id}/add_players/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        errors = response.json()['errors']
        data = response.json()['data']

        self.assertEqual(len(errors['player_id_missing']), 0)
        self.assertEqual(len(data['players']), 2)
        self.assertEqual(data['players'][0]["id"], payload["player_ids"][0])
        self.assertEqual(data['players'][1]["id"], payload["player_ids"][1])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_two_the_same_players_to_tournament_ok(self):
        payload = {
            "player_ids": [self.players[0].id, self.players[0].id]
        }
        response = client.post(
            f'{BASE_URL}/events/tournaments/{self.tournament.id}/add_players/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        errors = response.json()['errors']
        data = response.json()['data']

        self.assertEqual(len(errors['player_id_missing']), 0)
        self.assertEqual(len(data['players']), 1)
        self.assertEqual(data['players'][0]["id"], payload["player_ids"][0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
