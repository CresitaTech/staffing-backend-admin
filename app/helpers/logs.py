import logging

logger = logging.getLogger(__name__)


class WriteLog:
    logging.basicConfig(filename='/var/log/nginx/staff-audit-logger.log', level=logging.DEBUG, force=True)
    logger = logging.getLogger('staff-audit-logger')
    logger.setLevel(logging.DEBUG)

    def __init__(self):
        print('Object initiated')

    def request(self, request_info):
        self.logger.info('request_response', request_info)
        return request_info  # if you don't need it

    def login(self, login_info):
        self.logger.info('login', login_info)
        return login_info

    def crud(self, crud_info):
        self.logger.info('action', crud_info)
        return crud_info

