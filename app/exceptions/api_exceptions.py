from http import HTTPStatus

class APIException(Exception):
    def __init__(self, message: str, status_code: int, error_type: str):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(self.message) 