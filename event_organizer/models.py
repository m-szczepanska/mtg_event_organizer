from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from django.db import models


class Player(models.Model):
    """What is this, what does it do, why
    """
    # TODO: add integer, autoincrementing id
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    email = models.EmailField(max_length=254, blank=False)  # TODO unique?
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
    name = models.CharField(max_length=255, blank=False, default="mtg event")
    date_beginning = models.DateTimeField(auto_now=False, auto_now_add=False) #in "YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format."
    date_ending = models.DateTimeField(auto_now=False, auto_now_add=False) #albo models.DateField()?
    players = models.ManyToManyField(Player)

    def get_player_history(self, player):
        player_tournaments_all = Tournament.objects.filter(
            Q(player_1=player) | Q(player_2=player)
        )
        return player_tournaments_all

    def __str__(self):
        return "%s" % (self.name)


class Match(models.Model):
    player_1 = models.OneToOneField(
        Player,
        on_delete=models.CASCADE,
        related_name='player_1'
        )
    player_2 = models.OneToOneField(
        Player,
        on_delete=models.CASCADE,
        related_name='player_2'
    )
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player_1_score = models.PositiveSmallIntegerField()
    player_2_score = models.PositiveSmallIntegerField()
    draws = models.IntegerField(default=0)

    def get_player_matches(self, player):
        player_matches_all = Match.objects.filter(
            Q(player_1=player) | Q(player_2=player)
        )
        return player_matches_all
    
    @property
    def tournament_name(self):
        return self.tournament.name
