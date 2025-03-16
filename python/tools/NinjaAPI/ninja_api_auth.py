"""Module for communicating with NinjaRMM API."""

from logging import getLogger
from urllib.parse import urljoin
from typing import Literal
from dataclasses import dataclass, field
import time
import os
import requests


LOGGER = getLogger(__name__)


@dataclass
class OAUTHResponse:
    """Data class for OAuth response."""
    access_token: str
    token_type: str
    expires_in: int
    scope: str
    obtained_at: float = field(default_factory=time.time, init=False)

    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return time.time() > self.obtained_at + self.expires_in


class NinjaRMMAPI:
    """
    Class for interacting with the NinjaRMM API.

    Environment Variables:
        NINJA_ENVIRONMENT: str
        NINJA_CLIENT_ID: str
        NINJA_CLIENT_SECRET: str
        NINJA_BASE_URL: str
        NINJA_DOCS_PATH: str

    Attributes:
        base_url (str): The base URL for the API.
        docs_path (str): The path to the API documentation.
        documentation (dict): The API documentation.

    Methods:
        request(method, path, **kwargs): Make a request to the NinjaRMM API.
        refresh_documentation(): Refresh API documentation.
        get_sorted_docs(): Return sorted documentation.
        url_base_join(*args): Join the base URL with additional path components.
    """

    def __init__(self):
        self._environment = os.getenv("NINJA_ENVIRONMENT")
        self._client_id = os.getenv("NINJA_CLIENT_ID")
        self._client_secret = os.getenv("NINJA_CLIENT_SECRET")
        self._base_url = os.getenv("NINJA_BASE_URL")
        self._docs_path = os.getenv("NINJA_DOCS_PATH")

        missing_env_vars = [
            var for var, value in {
                "NINJA_ENVIRONMENT": self._environment,
                "NINJA_CLIENT_ID": self._client_id,
                "NINJA_CLIENT_SECRET": self._client_secret,
                "NINJA_BASE_URL": self._base_url,
                "NINJA_DOCS_PATH": self._docs_path,
            }.items() if not value
        ]
        valid_environments = ["app", "us2", "ca", "eu", "oc"]

        if missing_env_vars:
            raise ValueError(
                f"The following environment variables are not set: {', '.join(missing_env_vars)}"
            )
        if not self._environment in valid_environments:
            raise ValueError(
                f"Invalid NINJA_ENVIRONMENT. Must be one of: {', '.join(valid_environments)}"
            )

        self._token_url = f"https://{self._environment}.ninjarmm.com/ws/oauth/token"
        self._oauth: OAUTHResponse = self._request_credentials()
        self.documentation = {}
        self.refresh_documentation()

    @property
    def base_url(self) -> str:
        """Get the base URL for the API."""
        return self._base_url

    @property
    def docs_path(self) -> str:
        """Get the path to the API documentation."""
        return self._docs_path

    def _request_credentials(self) -> OAUTHResponse:
        """Get access token from NinjaRMM API."""
        LOGGER.info("Requesting credentials from NinjaRMM API.")
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": "monitoring management control"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(self._token_url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        oauth_response = OAUTHResponse(
            access_token=response.json()["access_token"],
            token_type=response.json()["token_type"],
            expires_in=response.json()["expires_in"],
            scope=response.json()["scope"],
        )
        return oauth_response

    def _authenticate(self) -> None:
        """Ensure the client is authenticated by checking token expiration."""
        if self._oauth.is_expired():
            LOGGER.info("OAuth token expired, refreshing.")
            self._oauth = self._request_credentials()

    def url_base_join(self, *args) -> str:
        """Join the base URL with additional path components."""
        return urljoin(self.base_url, "/".join(args))

    def request(
            self,
            method: Literal["get", "post", "put", "delete", "patch"],
            path: str,
            **kwargs
        ) -> dict:
        """Make a request to NinjaRMM API."""
        LOGGER.info("Making %s request to URL: %s", method.upper(), path)

        self._authenticate()
        response = getattr(requests, method)(
            url=self.url_base_join(path),
            headers={
                "accept": "application/json",
                "Authorization": f"{self._oauth.token_type} {self._oauth.access_token}"
            },
            timeout=kwargs.pop("timeout", 10),
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    def refresh_documentation(self) -> dict:
        """Refresh API Documentation."""
        LOGGER.info("Refreshing API documentation.")
        self.documentation = self.request("get", self.docs_path)

    def get_sorted_docs(self) -> dict:
        """
        Return sorted documentation.

        Example Query:
        sorted_paths = api.get_sorted_docs()
        sorted_paths["paths"]["system"]["methods"]["get"]["getOrganizations"]["path"]
        """
        LOGGER.info("Sorting API documentation paths by tags.")
        sorted_docs = {
            "openapi_version": self.documentation.get("openapi", ""),
            "info": self.documentation.get("info", {}),
            "security": self.documentation.get("security", []),
            "tags": self.documentation.get("tags", []),
            "paths": {
                tag["name"].lower(): {
                    "description": tag["description"],
                    "methods": {}
                    } for tag in self.documentation["tags"]
                },
            "components": self.documentation.get("components", {})
        }

        for path, methods in self.documentation["paths"].items():
            for method, details in methods.items():
                for tag in details["tags"]:
                    sorted_docs["paths"][tag.lower()]["methods"].setdefault(
                        method, {}
                    )[details["operationId"]] = {
                        "path": path,
                        "summary": details.get("summary", ""),
                        "description": details.get("description", ""),
                        "parameters": details.get("parameters", []),
                        "requestBody": details.get("requestBody", {}),
                        "responses": details.get("responses", {})
                    }
        return sorted_docs
