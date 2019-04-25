import functools
from django.http import HttpResponse
from event_organizer.models import Token


def uppercase(func):
    @functools.wraps(func)
    def wrapper():
        return func().upper()
    return wrapper


def is_authorized(func):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            result = request.META.get('HTTP_AUTHORIZATION')
            if not result:
                return HttpResponse(status=400)
            print(result)
            result_split = result.split(':')
            if not result_split:
                return HttpResponse(status=400)
            player_id = result_split[0]
            uuid = result_split[1]
            token = Token.objects.get(uuid=uuid)
            print(token)
            if token.player_id != int(player_id):
                print('bad id player')
                return HttpResponse(status=401)
        except Token.DoesNotExist:
            print('token doesnt exist')
            return HttpResponse(status=401)

        return func(request, *args, **kwargs)
    return wrapper
