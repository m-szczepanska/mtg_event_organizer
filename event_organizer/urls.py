from django.urls import path
from event_organizer.views import (
    player_list, player_details, tournament_list, match_list)

urlpatterns = [
    path('players/', player_list),
    path('players/<int:id>/', player_details),
    path('tournaments/', tournament_list),
    path('matches/', match_list)  # tournaments/<int:id>/matches/
]
