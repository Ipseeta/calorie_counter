from flask import jsonify
from app.exceptions.api_exceptions import APIException

def register_error_handlers(app):
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        response = {
            "error": error.message,
            "status": "error",
            "error_type": error.error_type
        }
        return jsonify(response), error.status_code

    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "An internal server error occurred",
            "status": "error",
            "error_type": "server_error"
        }), 500 