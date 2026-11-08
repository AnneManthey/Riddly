REMEMBER_ME_SESSION_AGE = 30 * 24 * 60 * 60
REMEMBER_ME_SESSION_KEY = 'remember_me'


class RememberMeSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.user.is_authenticated
            and request.session.get(REMEMBER_ME_SESSION_KEY)
        ):
            request.session.set_expiry(REMEMBER_ME_SESSION_AGE)
            request.session.modified = True
        return response
