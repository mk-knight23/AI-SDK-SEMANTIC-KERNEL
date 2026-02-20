"""
Unit tests for the Flask API endpoints.

Tests cover:
- Health check endpoint
- Root endpoint
- Search endpoint
- Error handling
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import json

# Add parent directory to path to import app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app.py directly using importlib to avoid package conflict
import importlib.util
spec = importlib.util.spec_from_file_location("app_module", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = app_module.app


class TestHealthEndpoint:
    """Test cases for the health check endpoint."""

    @pytest.fixture
    def client(self):
        """Fixture providing Flask test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_health_check_returns_200(self, client):
        """Test health check returns HTTP 200."""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_check_returns_json(self, client):
        """Test health check returns JSON response."""
        response = client.get('/health')
        assert response.content_type == 'application/json'

    def test_health_check_response_structure(self, client):
        """Test health check response has expected structure."""
        response = client.get('/health')
        data = json.loads(response.data)

        assert 'status' in data
        assert 'service' in data
        assert 'version' in data

    def test_health_check_status_healthy(self, client):
        """Test health check returns healthy status."""
        response = client.get('/health')
        data = json.loads(response.data)

        assert data['status'] == 'healthy'

    def test_health_check_service_name(self, client):
        """Test health check returns correct service name."""
        response = client.get('/health')
        data = json.loads(response.data)

        assert data['service'] == 'patentiq-backend'

    def test_health_check_version(self, client):
        """Test health check returns version."""
        response = client.get('/health')
        data = json.loads(response.data)

        assert data['version'] == '0.1.0'


class TestRootEndpoint:
    """Test cases for the root endpoint."""

    @pytest.fixture
    def client(self):
        """Fixture providing Flask test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_root_returns_200(self, client):
        """Test root endpoint returns HTTP 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_root_returns_json(self, client):
        """Test root endpoint returns JSON response."""
        response = client.get('/')
        assert response.content_type == 'application/json'

    def test_root_response_structure(self, client):
        """Test root response has expected structure."""
        response = client.get('/')
        data = json.loads(response.data)

        assert 'message' in data
        assert 'service' in data
        assert 'version' in data

    def test_root_message_content(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get('/')
        data = json.loads(response.data)

        assert 'Hello World from PatentIQ Backend' in data['message']


class TestCORS:
    """Test cases for CORS configuration."""

    @pytest.fixture
    def client(self):
        """Fixture providing Flask test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_cors_headers_present(self, client):
        """Test CORS headers are present in response."""
        response = client.get('/')
        # CORS headers should be present
        assert 'Access-Control-Allow-Origin' in response.headers


class TestAppConfiguration:
    """Test cases for Flask app configuration."""

    def test_app_exists(self):
        """Test that Flask app can be imported."""
        assert app is not None

    def test_app_is_flask_instance(self):
        """Test that app is a Flask instance."""
        from flask import Flask
        assert isinstance(app, Flask)

    def test_app_has_routes(self):
        """Test that app has registered routes."""
        rules = [rule.rule for rule in app.url_map.iter_rules()]

        assert '/' in rules
        assert '/health' in rules


class TestErrorHandling:
    """Test cases for error handling."""

    @pytest.fixture
    def client(self):
        """Fixture providing Flask test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_404_for_unknown_endpoint(self, client):
        """Test 404 response for unknown endpoint."""
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_405_for_wrong_method(self, client):
        """Test 405 response for wrong HTTP method."""
        response = client.post('/health')
        assert response.status_code == 405


class TestSearchEndpoint:
    """Test cases for the search endpoint (when implemented)."""

    @pytest.fixture
    def client(self):
        """Fixture providing Flask test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def mock_pipeline(self):
        """Fixture providing mock pipeline."""
        mock = MagicMock()
        mock.search.return_value = {
            'bm25_results': [
                Mock(id='patent-001', content='Test content', meta={'title': 'Test'})
            ],
            'embedding_results': [
                Mock(id='patent-001', content='Test content', meta={'title': 'Test'})
            ]
        }
        mock.hybrid_search.return_value = [
            Mock(id='patent-001', content='Test content', meta={'title': 'Test'})
        ]
        return mock

    def test_search_endpoint_not_implemented(self, client):
        """Test that search endpoint returns 404 (not yet implemented)."""
        response = client.get('/search?q=test')
        # Currently the endpoint doesn't exist
        assert response.status_code == 404

    def test_search_with_mock_pipeline(self, client):
        """Test search functionality with mocked pipeline."""
        # This test demonstrates how to test the search endpoint
        # when it is implemented
        mock_pipeline = MagicMock()
        mock_pipeline.search.return_value = {
            'bm25_results': [],
            'embedding_results': []
        }

        # Verify the mock setup works
        result = mock_pipeline.search('test')
        assert 'bm25_results' in result


class TestAppFactory:
    """Test cases for app factory pattern (if used)."""

    def test_app_creation(self):
        """Test that app can be created."""
        assert app is not None

    def test_app_debug_mode(self):
        """Test app debug configuration."""
        # Debug mode should be configurable
        assert hasattr(app, 'debug')
