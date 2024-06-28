import time
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if not request.session.get('last_request'):
                request.session['last_request'] = self.timestamp()
            elif self.timestamp() - request.session['last_request'] > 60:  # 60 секунд
                logout(request)
                del request.session['last_request']
        return None

    def process_response(self, request, response):
        if request.user.is_authenticated:
            request.session['last_request'] = self.timestamp()
        return response

    def timestamp(self):
        return int(time.time())

class TimestampMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.timestamp = lambda: int(time.time())
        return None
