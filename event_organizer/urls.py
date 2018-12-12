from django.urls import path
from event_organizer.views import (
    player_list, player_details, tournament_list, tournament_detail, match_detail, match_list)

urlpatterns = [
    path('players/', player_list),
    path('players/<int:id>/', player_details),
    path('tournaments/', tournament_list),
    path('tournaments/<int:id>/', tournament_detail),
    path('tournaments/<int:tournament_id>/matches/', match_list),
    path('tournaments/<int:tournament_id>/matches/<int:match_id>/', match_detail)  # tournaments/<int:id>/matches/
]
