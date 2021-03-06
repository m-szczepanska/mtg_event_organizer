from datetime import datetime, timezone
from math import ceil, log
from uuid import uuid4

from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q, Max
from django.db import models


class Player(models.Model):
    """ Model containing four basic informations from players about themselves.
    Args:
        first_name - string; max length 255 chars
        second_name - string; max length 255 chars
        email - unique string; max length 254 chars
        _password - hashed string
    """
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    email = models.EmailField(max_length=254, blank=False, unique=True)
    _password = models.CharField(max_length=255, blank=False)  # hashed

    def check_password(self, password_plaintext):
        return check_password(password_plaintext, self._password)

    # TODO: Add validation when creating player
    def set_password(self, password_plaintext):
        password_hashed = make_password(password_plaintext)
        self._password = password_hashed
        self.save()

    @property
    def full_name(self):
        full_name = self.first_name + " " + self.last_name
        return full_name

    def calculate_score_1(self, matches_list):
        score = 0
        for match in matches_list:
            if match.player_1_score > match.player_2_score:
                score += 3
            elif match.draws > 0 and match.player_1_score == match.player_2_score:
                score += 1
            # in case of players records score incorrectly
            elif match.player_1_score == match.player_2_score:
                if match.player_1_score > 0 and match.player_2_score > 0:
                    score += 1
        return score

    def calculate_score_2(self, matches_list):
        score = 0
        for match in matches_list:
            if match.player_2_score > match.player_1_score:
                score += 3
            elif match.draws > 0 and match.player_2_score == match.player_1_score:
                score += 1
            # in case of players records score incorrectly
            elif match.player_2_score == match.player_1_score:
                if match.player_2_score > 0 and match.player_1_score > 0:
                    score += 1
        return score

    def get_score_in_tournament(self, tournament_id):
        matches_player_1 = Match.objects.filter(
            player_1_id=self.id, tournament_id=tournament_id).all()
        matches_player_2 = Match.objects.filter(
            player_2_id=self.id, tournament_id=tournament_id).all()
        score_sum = self.calculate_score_1(matches_player_1) + \
            self.calculate_score_2(matches_player_2)
        return score_sum

    # def did_not_drop(self, tournament_id):
    #     tournament = Tournament.objects.get(id=tournament_id)
    #     through_model = TournamentPlayers.objects.get(tournament=tournament, player=self)
    #     dropped_from_tour = through_model.player_dropped
    #     if dropped_from_tour:
    #         return None
    #     else:
    #         return self

    def get_current_tournaments(self):
        # return list of tours objects that are ongoing and that the player
        # takes part in
        tournaments = Tournament.objects.filter(players__id=self.id).all()
        current_tours = [t for t in tournaments if not t.is_finished]
        return current_tours

    def get_player_history(self):
        tournaments_all = Tournament.objects.filter(
            players__id=self.id).all()
        tournaments_finished = [t for t in tournaments_all if t.past_rounds]
        return tournaments_finished

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


class Tournament(models.Model):
    """ Model containing four basic informations about game tournaments.
    Args:
        name - string; max length 255 chars, default value='mtg event'
        date_beginning - in "YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format
        date_ending - in "YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format
        players - related Player instance
    """
    name = models.CharField(max_length=255, blank=False, default="mtg event")
    date_beginning = models.DateTimeField(auto_now=False, auto_now_add=False)
    date_ending = models.DateTimeField(auto_now=False, auto_now_add=False)
    players = models.ManyToManyField(
        Player,
        through='TournamentPlayers',
        through_fields=('tournament', 'player'),
        related_name='tournaments'
    )
    rounds_number = models.IntegerField(blank=False, default=1)

    class Meta:
        ordering = ('date_beginning',)

    @property
    def current_round(self):
        # No pairings were generated yet
        if not self.matches.all():
            return []
        else:
            max_round = self.matches.aggregate(Max('round'))['round__max']
            current_round_matches = self.matches.filter(round=max_round)
            in_play_matches = []
            for match in current_round_matches:
                if not match.is_finished:
                    in_play_matches.append(match)
            if in_play_matches:
                return current_round_matches
            else:
                return self.matches.filter(round=(max_round + 1))

    @property
    def current_round_number(self):
        num = self.round_number_next
        return num

    @property
    def is_current_round_finished(self):
        for match in self.current_round:
            if not match.is_finished:
                return False
        return True

    @property
    def is_finished(self):
        return (
            self.round_number_next > self.rounds_number and
            self.is_current_round_finished
        )

    @property
    def past_rounds(self):
        if self.is_current_round_finished:
            max_round = self.round_number_next
        else:
            max_round = self.matches.aggregate(Max('round'))['round__max']
        past_round_matches = self.matches.exclude(round=max_round)
        return past_round_matches

    @property
    def past_round_pairings(self):
        past_round_matches = self.past_rounds
        list_pairings = [
            [match.player_1_id, match.player_2_id]
            for match in past_round_matches.all()
        ]
        return list_pairings

    @property
    def round_number_next(self):
        round = 1
        if not self.matches.all():
            pass
        elif self.is_current_round_finished:
            round += self.matches.aggregate(Max('round'))['round__max']
        else:
            return self.matches.aggregate(Max('round'))['round__max']
        return round

    @property
    def standings(self):
        players = self.players.all()
        scores = []
        for player in players:
            player_score = player.get_score_in_tournament(self.id)
            scores.append({
                "id": player.id,
                "first_name": player.first_name,
                "last_name": player.last_name,
                "score": player_score

                # TODO: Add tiebreakers
            })
        scores.sort(key=lambda x: x["score"], reverse=True)
        for i in range(len(scores)):
            scores[i]["order"] = i + 1
        return scores

    def __str__(self):
        return "%s" % (self.name)

    def score_by_player_id(self, player_id):
        player = Player.objects.get(id=player_id)
        player_score = player.get_score_in_tournament(self.id)
        return player_score

    def update_rounds_number(self, number=None):
        # number is value to override the number of rounds if we want to play
        # more (or fewer) rounds than we should play (e.g. 4 rounds - 8 players)
        players_number = self.players.count()
        if players_number:
            if number is None:
                self.rounds_number = ceil(log(players_number, 2))
            else:
                self.rounds_number = number
            self.save()


class TournamentPlayers(models.Model):
    """ A custom model that represents the intermediate table
        established with a many-to-many relationship between Player model
        and Tournament model.
    """
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
    )
    player_dropped = models.BooleanField(default=False)


class Match(models.Model):
    """ Model containing four basic informations about matches in tournaments.
    Args:
        player_1 - related Player instance
        player_2 - related Player instance
        tournament - related Tournament instance
        player_1_score - positive integer
        player_2_score - positive integer
        draws - integer, default value = 0
        round - integer, default value = 0
    """
    player_1 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='player_1'
    )
    player_2 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='player_2',
        null=True
    )
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name='matches')
    player_1_score = models.PositiveSmallIntegerField()
    player_2_score = models.PositiveSmallIntegerField()
    draws = models.IntegerField(default=0)
    round = models.IntegerField(default=1)

    class Meta:
        ordering = ('round',)

    # TODO: Move to player model; add tests
    def get_player_matches(self, player):
        player_matches_all = Match.objects.filter(
            Q(player_1=player) | Q(player_2=player)
        )
        return player_matches_all

    @property
    def player_1_name(self):
        first_name = self.player_1.first_name
        last_name = self.player_1.last_name

        return f'{last_name}, {first_name}'

    @property
    def player_2_name(self):
        first_name = self.player_2.first_name
        last_name = self.player_2.last_name

        return f'{last_name}, {first_name}'

    @property
    def tournament_name(self):
        return self.tournament.name

    @property
    def is_finished(self):
        return self.player_1_score or self.player_2_score or self.draws


class Token(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    uuid = models.CharField(max_length=200, default=uuid4)
    is_expired = models.BooleanField(default=False)

    # This is an example of a FactoryMethod design pattern
    # @classmethod
    # def create(cls, player_id, is_expired):
    #     instance = cls(uuid=uuid4(), player_id=player_id)
    #     instance.save()
    #     return instance


class PasswordResetToken(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=200, default=uuid4)
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    was_used = models.BooleanField(default=False)

    @property
    def is_valid(self):
        timedelta = datetime.now(timezone.utc) - self.created_at
        return timedelta.days < 1 and not self.was_used


class CreateAccountToken(models.Model):
    email = models.EmailField(max_length=254)
    uuid = models.CharField(max_length=200, default=uuid4)
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    was_used = models.BooleanField(default=False)

    @property
    def is_valid(self):
        timedelta = datetime.now(timezone.utc) - self.created_at
        return timedelta.days < 1 and not self.was_used
