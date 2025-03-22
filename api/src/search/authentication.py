import base64
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions

class OctoxlabsAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Octoxlabs '):
            return None
            
        try:
            token = auth_header.split(' ')[1]
            username = base64.b64decode(token).decode('utf-8')
            
            try:
                user = User.objects.get(username=username, defaults={'is_active': True})
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed('Invalid authentication token')
                
            return (user, None)
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Invalid authentication token: {str(e)}') 