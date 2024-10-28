
from google.auth.transport import requests
from google.oauth2 import id_token
from .models import Users
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from .serializers import CustomTokenObtainPairSerializer


class Google():
    @staticmethod
    def validate(access_token):
        try:
            id_info = id_token.verify_oauth2_token(access_token, requests.Request(), settings.GOOGLE_CLIENT_ID)
            if "accounts.google.com" in id_info['iss']:
                return id_info
        except Exception as e:
            return 'token is invalid or has expired'


def login_social_user(email, password):
    user = authenticate(email=email, password=password)

    if not user:
        raise AuthenticationFailed('Invalid credentials')

    token_serializer = CustomTokenObtainPairSerializer(
        data = {'email': email, 'password': password, 'role':'user'}
    )

    if token_serializer.is_valid():
        try:
            token_data = token_serializer.validated_data

            return{
                'id': user.id,
                'user': user.username,
                'email': user.email,
                # 'role': user.role,
                'access_token': token_data['access'],
                'refresh_token': token_data['refresh']
            }
        except KeyError as e:
            raise AuthenticationFailed(detail = f'Missing key: {str(e)}')
    else:
        raise AuthenticationFailed('token generation failed')


    # user_tokens = user.token()
    # return {
    #     'email' : user.email,
    #     'username' : user.get_full_name,
    #     'access_token' : str(user_tokens.get('access')),
    #     'refresh_token' : str(user_tokens.get('refresh'))
    # }
 

def register_social_user(provider, email, first_name, last_name):
    user = Users.objects.filter(email = email)
    if user.exists():
        if provider == user[0].auth_provider:
            result = login_social_user(email, settings.SOCIAL_AUTH_PASSWORD)
            return result
        else:
            raise AuthenticationFailed(
                detail= f"please continue your login with {user[0].auth_provider}"
            )
    else:
        new_user = {
            'email' : email,
            'username' : first_name,
            'last_name' : last_name,
            'password' : settings.SOCIAL_AUTH_PASSWORD 
        }
        register_user = Users.objects.create_user(**new_user)
        register_user.auth_provider = provider
        register_user.is_verified = True
        register_user.save()
        login_social_user(email=register_user.email, password=settings.SOCIAL_AUTH_PASSWORD )