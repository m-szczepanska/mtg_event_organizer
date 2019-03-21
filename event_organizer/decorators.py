import functools


def uppercase(func):
    @functools.wraps(func)
    def wrapper():
        return func().upper()
    return wrapper


def view_auth(func):
    @functools.wraps(func)
    def wrapper(player_id, uuid):
        try:
            token = Token.objects.get(player_id=player_id)
        except Token.DoesNotExist:
            return HttpResponse(status=401)
