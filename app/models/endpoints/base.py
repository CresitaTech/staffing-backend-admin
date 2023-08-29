import json
import logging
from json import JSONDecodeError

import requests
from django.conf import settings

logger = logging.getLogger('naviswiss')


class EndpointsClient:
    """
    Class to manage communication with Naviswiss_Endpoints
    """

    headers = None
    request_date = None
    response = None
    status_code = None
    response_data = None
    errors = None
    request = None

    def __init__(self, request, auth_token=None):
        if request is None:
            raise ValueError("request is required")

        self.request = request

        authorization = None
        if auth_token:
            authorization = auth_token
        elif 'trulocal_token' in request.session:
            authorization = request.session['trulocal_token']

        if authorization is not None:
            self.headers = {'Authorization': authorization}

    @staticmethod
    def generate_url(endpoint):
        while endpoint.startswith('/'):
            endpoint = endpoint[1:]
        return "{}{}".format(settings.ENDPOINTS_URL, endpoint)

    def send_request(self, data, endpoint, method='POST'):
        """
        Send a request to the endpoints and populate response variables
        """
        url = EndpointsClient.generate_url(endpoint)

        try:
            if method == 'POST':
                self.response = requests.post(url=url, json=data, headers=self.headers, verify=True, timeout=20)
            elif method == 'GET':
                self.response = requests.get(url=url, json=data, headers=self.headers, verify=True, timeout=20)
        except requests.ConnectionError as e:
            logger.error(f"Connection error for endpoint {endpoint} - {e}")
            self.status_code = 500
            return False
        except requests.Timeout as e:
            logger.error(f"Timeout error for endpoint {endpoint} - {e}")
            self.status_code = 500
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Unhandled {type(e).__name__} error for endpoint {endpoint} - {e}")
            self.status_code = 500
            return False

        self.status_code = self.response.status_code
        try:
            if self.response.text is not None and self.response.text != "":
                self.response_data = json.loads(self.response.text)
            return True
        except JSONDecodeError as je:
            logger.warning(f"JSONDecodeError| {str(je)} ")
            return False
        except Exception as e:
            logger.warning(e.args)
            return False

    def is_successful_response(self):
        return 200 <= self.status_code < 300

    def error_message(self):
        error = ""
        if not self.response_data:
            status = 'Failed'
            if self.status_code == 404:
                error = 'not_found'
            else:
                error = 'unknown'
        elif 'error_message' in self.response_data:
            error = self.response_data['error_message']
            status = self.response_data['status']
        else:
            status = self.response_data['status']

        if error:
            if error == "logged_out":
                error = "You have been logged out."
            elif error == "denied" or error == "Failed: Permission Denied":
                error = "Incorrect email and password."
            elif error == 'not_found':
                error = 'Page not found'
            elif error == 'unknown':
                error = 'Unknown error'
        return "{}: {}".format(status, error)

    def base_request(self):
        return {
            "client_id": settings.CLIENT_ID,
            "client_secret": settings.CLIENT_SECRET,
        }
