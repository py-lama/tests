"""Integration tests for HTTP endpoints using pytest-httpbin."""
import pytest
import requests
from http import HTTPStatus

# Test data for the echo endpoint
ECHO_TEST_DATA = {
    "test": "data",
    "number": 123,
    "nested": {"key": "value"}
}


def test_httpbin_get(httpbin):
    """Test a simple GET request to httpbin."""
    response = requests.get(httpbin.url + "/get")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "args" in data
    assert "headers" in data
    assert "origin" in data
    assert "url" in data


def test_httpbin_post(httpbin):
    """Test a POST request with JSON data to httpbin."""
    response = requests.post(httpbin.url + "/post", json=ECHO_TEST_DATA)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "json" in data
    assert data["json"] == ECHO_TEST_DATA
    assert "url" in data


@pytest.mark.parametrize("status_code", [200, 201, 400, 404, 500])
def test_httpbin_status_codes(httpbin, status_code):
    """Test various status codes with httpbin."""
    response = requests.get(f"{httpbin.url}/status/{status_code}")
    assert response.status_code == status_code


def test_httpbin_headers(httpbin):
    """Test that custom headers are returned by httpbin."""
    headers = {
        "X-Test-Header": "test-value",
        "User-Agent": "test-agent"
    }
    response = requests.get(httpbin.url + "/headers", headers=headers)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "headers" in data
    assert data["headers"]["X-Test-Header"] == "test-value"
    assert data["headers"]["User-Agent"] == "test-agent"


class TestHTTPEndpointsWithSession:
    """Test HTTP endpoints using a session for connection pooling."""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create a requests session for connection pooling."""
        with requests.Session() as session:
            yield session
    
    def test_httpbin_get_with_session(self, httpbin, session):
        """Test GET request using a session."""
        response = session.get(httpbin.url + "/get")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "url" in data
    
    def test_httpbin_post_with_session(self, httpbin, session):
        """Test POST request with JSON data using a session."""
        response = session.post(httpbin.url + "/post", json=ECHO_TEST_DATA)
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data["json"] == ECHO_TEST_DATA
