"""Module for communicating with NinjaRMM API."""

from logging import getLogger
from typing import Union, Literal
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

    def __str__(self):
        return f"access_token: {self.access_token}, token_type: {self.token_type}, " \
               f"expires_in: {self.expires_in}, scope: {self.scope}, obtained_at: {self.obtained_at}"

    def __repr__(self):
        return f"OAUTHResponse(access_token={self.access_token}, token_type={self.token_type}, " \
               f"expires_in={self.expires_in}, scope={self.scope}, obtained_at={self.obtained_at})"


class NinjaRMMAPI:
    """
    Class for interacting with the NinjaRMM API.

    Environment Variables:
    NINJA_CLIENT_ID: str
    NINJA_CLIENT_SECRET: str
    NINJA_BASE_URL: str
    NINJA_DOCS_PATH: str
    """

    def __init__(self):
        self._client_id = os.getenv("NINJA_CLIENT_ID")
        self._client_secret = os.getenv("NINJA_CLIENT_SECRET")
        self._base_url = os.getenv("NINJA_BASE_URL")
        self._docs_path = os.getenv("NINJA_DOCS_PATH")

        if not self._client_id:
            raise ValueError("NINJA_CLIENT_ID environment variable is not set.")
        if not self._client_secret:
            raise ValueError("NINJA_CLIENT_SECRET environment variable is not set")
        if not self.base_url:
            raise ValueError("NINJA_BASE_URL environment variable is not set")
        if not self.docs_path:
            raise ValueError("NINJA_DOCS_PATH environment variable is not set")

        self._token_url = "https://app.ninjarmm.com/ws/oauth/token"
        self._oauth: OAUTHResponse = self._request_credentials()
        self._primary_headers = {
            "accept": "application/json",
            "Authorization": f"{self._oauth.token_type} {self._oauth.access_token}"
        }

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

    def _is_token_expired(self) -> bool:
        """Check if the access token is expired."""
        expired = time.time() > self._oauth.obtained_at + self._oauth.expires_in
        if expired:
            LOGGER.info("OAuth token has expired.")
        return expired

    def _authenticate(self) -> None:
        """Ensure the client is authenticated by checking token expiration."""
        if self._is_token_expired():
            LOGGER.info("Re-authenticating due to expired token.")
            self._oauth = self._request_credentials()

    def urljoin(self, *args) -> str:
        """Join URL parts."""
        return "/".join(map(lambda x: str(x).strip("/"), args))

    def request(
            self,
            request_type: Union[
                Literal["get"], Literal["post"], Literal["put"], Literal["delete"], Literal["patch"]
                ],
            path: str,
            params=None,
            data=None,
            timeout: int = 10
        ) -> dict:
        """Make a request to NinjaRMM API."""
        LOGGER.info("Making %s request to URL: %s", request_type.upper(), path)
        if request_type == "get":
            request_method = requests.get
        elif request_type == "post":
            request_method = requests.post
        elif request_type == "put":
            request_method = requests.put
        elif request_type == "delete":
            request_method = requests.delete
        elif request_type == "patch":
            request_method = requests.patch
        else:
            raise ValueError("Invalid request type.")

        self._authenticate()
        response = request_method(
            self.urljoin(self.base_url, path),
            headers=self._primary_headers,
            data=data, timeout=timeout,
            params=params
            )
        response.raise_for_status()
        return response.json()

    def get_docs(self) -> dict:
        """Get the API documentation."""
        LOGGER.info("Fetching API documentation.")
        return self.request("get", self.docs_path)

    def get_openapi_version(self) -> str:
        """Get the OpenAPI version from the API documentation."""
        LOGGER.info("Fetching OpenAPI version.")
        return self.get_docs()["openapi"]

    def get_docs_tags(self) -> list:
        """Get the tags from the API documentation."""
        LOGGER.info("Fetching API documentation tags.")
        return list(self.get_docs()["tags"])

    def get_docs_paths(self) -> dict:
        """Get the paths from the API documentation."""
        LOGGER.info("Fetching API documentation paths.")
        return self.get_docs()["paths"]

    def get_docs_schema(self) -> dict:
        """Get the schema from the API documentation."""
        LOGGER.info("Fetching API documentation schema.")
        return self.get_docs()["components"]["schemas"]

    def get_docs_info(self) -> dict:
        """Get the info from the API documentation."""
        LOGGER.info("Fetching API documentation info.")
        return self.get_docs()["info"]

    def get_docs_sorted_paths(self) -> dict:
        """
        Use tags to sort paths into a dictionary.

        Example Query:
        sorted_paths = api.get_docs_sorted_paths()
        sorted_paths["organization checklists"]["methods"]["get"]["getClientChecklist"]["path"])
        """
        LOGGER.info("Sorting API documentation paths by tags.")
        tags = self.get_docs_tags()
        paths = self.get_docs_paths()
        sorted_paths = {
            tag["name"].casefold(): {
            "description": tag["description"],
            "methods": {
                "get": {},
                "post": {},
                "put": {},
                "delete": {},
                "patch": {}
            }
            } for tag in tags
        }

        for path, path_data in paths.items():
            for method, method_data in path_data.items():
                for tag in method_data["tags"]:
                    tag_key = tag.casefold()
                    sorted_paths[tag_key]["methods"][method][method_data["operationId"]] = {
                        "path": path,
                        "summary": method_data["summary"],
                        "description": method_data["description"],
                        "parameters": method_data.get("parameters", []),
                        "requestBody": method_data.get("requestBody", {}),
                        "responses": method_data.get("responses", {})
                    }

        return sorted_paths
