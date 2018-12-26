from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
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
    players = models.ManyToManyField(Player)

    def get_player_history(self, player):
        player_tournaments_all = Tournament.objects.filter(
            Q(player_1=player) | Q(player_2=player)
        )
        return player_tournaments_all

    def __str__(self):
        return "%s" % (self.name)


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


    # TODO: Move to player model; add tests
    def get_player_matches(self, player):
        player_matches_all = Match.objects.filter(
            Q(player_1=player) | Q(player_2=player)
        )
        return player_matches_all

    @property
    def tournament_name(self):
        return self.tournament.name
