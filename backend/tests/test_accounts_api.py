import json
import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from accounts.models import User


def unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


class AccountsAPITests(APITestCase):
    """
    Real API tests for accounts endpoints:
      - register (POST /api/register/)
      - login (POST /api/login/)
      - profile (GET/PUT /api/profile/)
    These tests exercise the real DRF views and authentication flow (JWT + token).
    """

    def setUp(self):
        self.client = APIClient()
        # Reverse names are defined in accounts.urls (included under /api/ in project urls).
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.profile_url = reverse("profile")

    def test_register_success(self):
        email = unique_email()
        payload = {
            "email": email,
            "password": "strongpass123",
            "password2": "strongpass123",
            "name": "Test User",
            "role": "empleado",
            "plan": "free",
        }

        resp = self.client.post(self.register_url, payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        # Response should include tokens and user info
        assert "access" in resp.data
        assert "refresh" in resp.data
        assert "token" in resp.data
        assert "user" in resp.data
        assert resp.data["user"]["email"] == email

        # Verify user exists in DB
        assert User.objects.filter(email=email).exists()

    def test_register_duplicate_email(self):
        email = unique_email()
        payload = {
            "email": email,
            "password": "strongpass123",
            "password2": "strongpass123",
            "name": "Test User",
            "role": "empleado",
            "plan": "free",
        }

        # First registration should succeed
        r1 = self.client.post(self.register_url, payload, format="json")
        assert r1.status_code == status.HTTP_201_CREATED, r1.data

        # Second registration with same email should fail
        r2 = self.client.post(self.register_url, payload, format="json")
        assert r2.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT), r2.data

    def test_register_password_mismatch(self):
        payload = {
            "email": unique_email(),
            "password": "password1",
            "password2": "password2",
            "name": "Test User",
            "role": "empleado",
            "plan": "free",
        }
        resp = self.client.post(self.register_url, payload, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        # Expect a validation error about passwords not matching in response content
        body = json.dumps(resp.data)
        assert "password" in body.lower() or "match" in body.lower()

    def _create_user(self, email=None, password="testpass123", **extra):
        if email is None:
            email = unique_email()
        params = {"email": email, "password": password, "name": extra.pop("name", "Auto User")}
        params.update(extra)
        user = User.objects.create_user(**params)
        return user

    def _login_and_get_access(self, email, password):
        resp = self.client.post(self.login_url, {"email": email, "password": password}, format="json")
        assert resp.status_code == status.HTTP_200_OK, getattr(resp, "data", resp.content)
        # login view returns both 'access' and 'refresh'
        access = resp.data.get("access")
        assert access, "Login response did not include access token"
        return access, resp.data

    def test_login_success(self):
        email = unique_email()
        password = "testpass123"
        # Create user in DB
        self._create_user(email=email, password=password, name="Login User", plan="free")

        # Login
        access, data = self._login_and_get_access(email, password)
        assert "token" in data  # legacy simple token
        assert "refresh" in data
        assert data["user"]["email"] == email

    def test_login_invalid_credentials(self):
        email = unique_email()
        password = "right-password"
        self._create_user(email=email, password=password, name="Login User")
        # Attempt with wrong password
        resp = self.client.post(self.login_url, {"email": email, "password": "wrong"}, format="json")
        # Accept either 400 or 401 depending on serializer implementation; ensure no tokens returned
        assert resp.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED)
        assert not resp.data.get("access") and not resp.data.get("refresh")

    def test_profile_requires_authentication(self):
        # Unauthenticated request should be rejected
        resp = self.client.get(self.profile_url)
        assert resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_profile_with_jwt_access_and_update(self):
        # Create and login user to get JWT access token
        email = unique_email()
        password = "testpass123"
        user = self._create_user(email=email, password=password, name="Profile User", plan="free")

        access, login_data = self._login_and_get_access(email, password)
        # Use Bearer token to authenticate subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # GET profile
        resp_get = self.client.get(self.profile_url)
        assert resp_get.status_code == status.HTTP_200_OK, resp_get.data
        assert resp_get.data["email"] == email

        # Update profile (change plan)
        new_plan = "pro" if resp_get.data.get("plan") == "free" else "free"
        resp_put = self.client.put(self.profile_url, {"plan": new_plan}, format="json")
        assert resp_put.status_code == status.HTTP_200_OK, resp_put.data
        assert resp_put.data["plan"] == new_plan

        # Ensure change persisted in DB
        user.refresh_from_db()
        assert user.plan == new_plan

    def test_profile_with_token_authentication(self):
        # Some clients might use legacy token authentication. Ensure it works too.
        email = unique_email()
        password = "testpass123"
        user = self._create_user(email=email, password=password, name="Token User", plan="free")

        # Login will also return a simple token
        resp = self.client.post(self.login_url, {"email": email, "password": password}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        simple_token = resp.data.get("token")
        assert simple_token

        # Use Token authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {simple_token}")
        resp_profile = self.client.get(self.profile_url)
        assert resp_profile.status_code == status.HTTP_200_OK
        assert resp_profile.data["email"] == email
