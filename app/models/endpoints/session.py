import logging

from django.core.cache import cache

from webdb.models import User
from .base import EndpointsClient

logger = logging.getLogger('naviswiss')


class SessionEndpointsClient(EndpointsClient):
    def login(self, email, password, apply_to_session=True):
        login_request = self.base_request()
        login_request['email'] = email
        login_request['password'] = password
        if self.send_request(login_request, 'authenticate') and self.status_code == 200:
            if apply_to_session:
                session = self.request.session
                if 'access_token' in self.response_data:
                    session["naviswiss_token"] = self.response_data['access_token']
                    session["naviswiss_refresh"] = self.response_data['refresh']
                else:
                    session["naviswiss_token"] = None
                    session["naviswiss_refresh"] = None
                session["naviswiss_user_email"] = email
                user = User.objects.get(email=email)
                session["naviswiss_user_id"] = user.user_id
                session.save()
            # Anywhere that is looking for the access token to be returned, a new account is being created
            # So the user will never have 2FA enabled
            return (
                self.response_data['access_token']
                if 'access_token' in self.response_data
                else self.response_data['tf_key']
            )
        else:
            return False

    def login_2fa(self, user_id, token, tf_key, apply_to_session=True):
        login_request = self.base_request()
        login_request['user'] = user_id
        login_request['token'] = token
        login_request['tf_key'] = tf_key
        if self.send_request(login_request, 'authenticate/2fa') and self.status_code == 200:
            if apply_to_session:
                session = self.request.session
                session["naviswiss_token"] = self.response_data['access_token']
                session["naviswiss_refresh"] = self.response_data['refresh']
                session.save()
            return self.response_data['access_token']
        else:
            return False

    def logout(self):
        if self.headers and self.headers.get('Authorization'):
            data = {'token': self.headers['Authorization']}
            r = False
            if self.send_request(data, 'logout') and self.is_successful_response():
                r = True
            else:
                r = False
        else:
            r = True
        self.clear_cookies()
        logger.debug("User logged out")
        return r

    def forgot_password(self, email):
        request_data = self.base_request()
        request_data['email'] = email
        if self.send_request(request_data, 'password/reset') and self.is_successful_response():
            return True
        else:
            return False

    def reset_password(self, key, new_password):
        request_data = self.base_request()
        request_data['reset_key'] = key
        request_data['new_pass'] = new_password
        if self.send_request(request_data, 'password/change') and self.is_successful_response():
            return True
        else:
            return False

    def clear_cookies(self):
        session = self.request.session
        session.flush()
        session.save()

    def check_token_status(self, user_id):
        key = f"user_{user_id}_token_valid"
        token_valid = cache.get(key, False)
        if token_valid:
            # Token response is still cached and it is unlikely that the user has
            # switched devices multiple times in 30 minutes
            return True

        token_request = self.base_request()
        if self.send_request(token_request, 'check_auth_status') and self.status_code == 200:
            # Cache the token response for 30 minutes
            cache.set(key, True, 1800)
            return True

        return False
