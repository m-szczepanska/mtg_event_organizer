from django.urls import path
from event_organizer.views import (
    player_list, player_details, tournament_list, tournament_detail,
    match_detail, match_list, add_players_to_tournament,
    players_current_tournaments, player_history, login)
from event_organizer.pairing_view import tournament_pairings

urlpatterns = [
    path('players/', player_list),
    path('players/<int:id>/', player_details),
    path('tournaments/', tournament_list),
    path('tournaments/<int:id>/', tournament_detail),
    path('tournaments/<int:tournament_id>/matches/', match_list),
    path('tournaments/<int:tournament_id>/matches/<int:match_id>/', match_detail),
    path('tournaments/<int:id>/add_players/', add_players_to_tournament),
    path('tournaments/<int:tournament_id>/pairings/', tournament_pairings),
    path('players/<int:id>/current_tournaments/', players_current_tournaments),
    path('players/<int:id>/player_history/', player_history),
    path('login/', login)
      # tournaments/<int:id>/matches/
]
