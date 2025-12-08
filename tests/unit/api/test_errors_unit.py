"""
Unit tests for API error handling functions.

Tests verify that error responses are formatted correctly with
appropriate status codes and error messages.
"""
from app.api import errors as err


def test_error_response_returns_correct_status_and_message(app):
    """Test that error_response returns correct status code and message."""
    payload, status = err.error_response(404, "missing")
    
    assert status == 404
    assert payload["error"]
    assert payload["message"] == "missing"


def test_bad_request_returns_400_status(app):
    """Test that bad_request returns 400 status with error message."""
    payload, status = err.bad_request("nope")
    
    assert status == 400
    assert payload["message"] == "nope"


def test_http_exception_handler_extracts_status_code_from_exception(app):
    """Test that handle_exception extracts status code from exception."""
    class CustomException(Exception):
        code = 403

    payload, status = err.handle_exception(CustomException())
    
    assert status == 403
    assert "error" in payload
