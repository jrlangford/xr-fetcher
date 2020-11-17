from rest_framework import throttling

class ApplicationRateThrottle(throttling.SimpleRateThrottle):
    scope = 'oauth_application'

    def get_cache_key(self, request, view):
        if request.auth and request.auth.application:
            ident = request.auth.application.id
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
