from http import HTTPStatus
from typing import Any, Dict, Optional

class APIException(Exception):
    """
    Custom API Exception class for handling application errors
    """
    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_type: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = str(message)
        self.status_code = status_code
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary format for JSON serialization
        """
        error_response = {
            "success": False,
            "error": {
                "message": self.message,
                "type": self.error_type,
                "status": self.status_code
            }
        }
        
        if self.details:
            error_response["error"]["details"] = self.details
            
        return error_response

    @classmethod
    def invalid_image(cls, message: str = "Invalid image provided") -> 'APIException':
        return cls(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="INVALID_IMAGE"
        )

    @classmethod
    def invalid_file_type(cls, content_type: Optional[str] = None) -> 'APIException':
        message = "Uploaded file is not an image"
        if content_type:
            message += f" (received: {content_type})"
        return cls(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="INVALID_FILE_TYPE"
        )

    @classmethod
    def invalid_image_format(cls, format: Optional[str] = None) -> 'APIException':
        message = "Invalid image file format"
        if format:
            message += f": {format}"
        return cls(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="INVALID_IMAGE_FORMAT"
        )

    @classmethod
    def missing_image(cls) -> 'APIException':
        return cls(
            message="No image file provided",
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="MISSING_IMAGE"
        )

    @classmethod
    def empty_image(cls) -> 'APIException':
        return cls(
            message="No selected image file",
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="EMPTY_IMAGE"
        )

    @classmethod
    def service_unavailable(cls, service: str = "service") -> 'APIException':
        return cls(
            message=f"The {service} is temporarily unavailable",
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            error_type="SERVICE_UNAVAILABLE"
        )

    @classmethod
    def parse_error(cls, details: Optional[Dict[str, Any]] = None) -> 'APIException':
        return cls(
            message="Failed to parse the response",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_type="PARSE_ERROR",
            details=details
        )