from django.urls import path
from event_organizer.views import (
    player_list, player_details, tournament_list, tournament_detail,
    match_detail, match_list, add_players_to_tournament, register_view,
    players_current_tournaments, player_history, login, register_request_view,
    password_reset_request, reset_password_view, logout)
from event_organizer.pairing_view import tournament_pairings

urlpatterns = [
    path('players/', player_list),
    path('players/<int:id>/', player_details),
    path('tournaments/', tournament_list),
    path('tournaments/<int:id>/', tournament_detail),
    path('tournaments/<int:tournament_id>/matches/', match_list),
    path(
        'tournaments/<int:tournament_id>/matches/<int:match_id>/',
        match_detail
    ),
    path('tournaments/<int:id>/add_players/', add_players_to_tournament),
    path('tournaments/<int:tournament_id>/pairings/', tournament_pairings),
    path('players/<int:id>/current_tournaments/', players_current_tournaments),
    path('players/<int:id>/player_history/', player_history),
    path('login/', login),
    path('register_request/', register_request_view),
    path('register/<uuid:token_uuid>/', register_view),
    path('password_reset_request/', password_reset_request),
    path('password_reset/<uuid:token_uuid>/', reset_password_view),
    path('players_settings/', player_details),
    path('logout/', logout),
    path('send_invitation/', register_request_view),
]
