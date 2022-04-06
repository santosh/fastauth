import os

import pytest
from fastapi.testclient import TestClient

from main import app, get_db
from fastauth.database import DBInitTest

@pytest.fixture
def delete_database():
    os.unlink("./test.db")


def get_test_db():
    session = None
    try:
        session = DBInitTest("sqlite:///./test.db").get_session()
        session = session()
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = get_test_db


client = TestClient(app)


class TestUserRegistration:
    """TestUserRegistration tests /users/register"""

    def test_get_request_returns_405(self):
        """registration endpoint does only expect a post request"""
        response = client.get("/users/register")
        assert response.status_code == 405

    def test_post_request_without_body_returns_422(self):
        """body should have username, password and fullname"""
        response = client.post("/users/register")
        assert response.status_code == 422

    def test_post_request_with_improper_body_returns_422(self):
        """all of username, password and fullname is required"""
        response = client.post(
            "/users/register",
            json={"username": "santosh"}
        )
        assert response.status_code == 422

    def test_post_request_with_proper_body_returns_201(self, delete_database):
        response = client.post(
            "/users/register",
            json={"username": "santosh", "password": "sntsh", "fullname": "Santosh Kumar"}
        )
        assert response.status_code == 201


class TestUserLogin:
    """TestUserLogin tests /users/auth"""

    def test_get_request_returns_405(self):
        """login endpoint does only expect a post request"""
        response = client.get("/users/auth")
        assert response.status_code == 405

    def test_post_request_without_body_returns_422(self):
        """body should have username, password and fullname"""
        response = client.post("/users/auth")
        assert response.status_code == 422

    def test_post_request_with_improper_body_returns_422(self):
        """both username and password is required"""
        response = client.post(
            "/users/auth",
            json={"username": "santosh"}
        )
        assert response.status_code == 422

    def test_post_request_with_proper_body_returns_200_with_jwt_token(self):
        response = client.post(
            "/users/auth",
            json={"username": "santosh", "password": "sntsh"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 2
