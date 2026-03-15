from __future__ import annotations

from io import BytesIO
from typing import Any, Iterable

import requests
from requests import Response
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from data import BASE_AD_PAYLOAD
from urls import (
    BASE_URL,
    CREATE_AD_PATH,
    DELETE_AD_PATH,
    LISTING_ITEM_PATH,
    LOGIN_PATHS,
    REGISTER_PATHS,
    UPDATE_AD_PATH,
)
from utils import extract_entity_id, extract_token, merge_dicts


disable_warnings(InsecureRequestWarning)


class DeskApi:
    def __init__(self, base_url: str = BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({"Accept": "application/json"})

    def _request(self, method: str, path: str, **kwargs: Any) -> Response:
        return self.session.request(method=method, url=f"{self.base_url}{path}", timeout=5, **kwargs)

    @staticmethod
    def _score_response(response: Response, success_statuses: tuple[int, ...]) -> tuple[int, int]:
        if response.status_code in success_statuses:
            return (0, response.status_code)
        if 200 <= response.status_code < 300:
            return (1, response.status_code)
        if response.status_code in (400, 401, 403, 405, 409, 415, 422):
            return (2, response.status_code)
        if response.status_code == 404:
            return (4, response.status_code)
        return (3, response.status_code)

    def _request_first_working(
        self,
        method: str,
        paths: Iterable[str],
        success_statuses: tuple[int, ...],
        request_variants: Iterable[dict[str, Any]] | None = None,
        acceptable_statuses: tuple[int, ...] | None = None,
    ) -> Response:
        variants = tuple(request_variants or ({},))
        allowed_statuses = success_statuses + tuple(acceptable_statuses or ())
        best_response: Response | None = None
        best_score: tuple[int, int] | None = None

        for path in paths:
            for variant in variants:
                response = self._request(method, path, **variant)
                if response.status_code in success_statuses:
                    return response
                score = self._score_response(response, success_statuses)
                if response.status_code in allowed_statuses or best_response is None:
                    if best_score is None or score < best_score:
                        best_score = score
                        best_response = response

        if best_response is None:
            raise RuntimeError("Не удалось выполнить запрос: список путей пуст")
        return best_response

    @staticmethod
    def _auth_headers(token: str, content_type: str | None = None) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {token}"}
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    @staticmethod
    def _register_variants(payload: dict[str, Any]) -> tuple[dict[str, Any], ...]:
        candidates = [
            payload,
            {"name": payload.get("name"), "email": payload.get("email"), "password": payload.get("password")},
            {"username": payload.get("name"), "email": payload.get("email"), "password": payload.get("password")},
            {"fullName": payload.get("name"), "email": payload.get("email"), "password": payload.get("password")},
        ]
        variants: list[dict[str, Any]] = []
        seen: set[tuple[tuple[str, Any], ...]] = set()
        for item in candidates:
            key = tuple(sorted(item.items()))
            if key in seen:
                continue
            seen.add(key)
            variants.append({"json": item})
            variants.append({"data": item})
        return tuple(variants)

    @staticmethod
    def _login_variants(payload: dict[str, Any]) -> tuple[dict[str, Any], ...]:
        candidates = [
            payload,
            {"email": payload.get("email"), "password": payload.get("password")},
            {"login": payload.get("email"), "password": payload.get("password")},
            {"username": payload.get("email"), "password": payload.get("password")},
        ]
        variants: list[dict[str, Any]] = []
        seen: set[tuple[tuple[str, Any], ...]] = set()
        for item in candidates:
            key = tuple(sorted(item.items()))
            if key in seen:
                continue
            seen.add(key)
            variants.append({"json": item})
            variants.append({"data": item})
        return tuple(variants)

    @staticmethod
    def _multipart_payload(payload: dict[str, Any], include_image: bool = True) -> MultipartEncoder:
        fields: dict[str, Any] = {
            "name": str(payload["name"]),
            "category": str(payload["category"]),
            "condition": str(payload["condition"]),
            "city": str(payload["city"]),
            "description": str(payload["description"]),
            "price": str(payload["price"]),
        }
        if include_image:
            image_stream = BytesIO(
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
                b"\x00\x00\x00\x0cIDATx\x9cc````\x00\x00\x00\x04\x00\x01\x0b\xe7\x02\x9d\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            fields["images"] = ("image.png", image_stream, "image/png")
        return MultipartEncoder(fields=fields)

    def register_user(self, payload: dict[str, Any]) -> Response:
        return self._request_first_working(
            method="POST",
            paths=REGISTER_PATHS,
            success_statuses=(200, 201),
            acceptable_statuses=(400, 409, 422),
            request_variants=self._register_variants(payload),
        )

    def login_user(self, payload: dict[str, Any]) -> Response:
        return self._request_first_working(
            method="POST",
            paths=LOGIN_PATHS,
            success_statuses=(200, 201),
            request_variants=self._login_variants(payload),
        )

    def auth_token_from_login(self, payload: dict[str, Any]) -> str:
        response = self.login_user(payload)
        assert response.status_code in (200, 201), response.text
        token = self.extract_token(response.json())
        assert token, f"Токен не найден в ответе: {response.text}"
        return token

    def create_ad(self, payload: dict[str, Any], token: str) -> Response:
        multipart = self._multipart_payload(payload, include_image=True)
        headers = self._auth_headers(token, multipart.content_type)
        return self._request("POST", CREATE_AD_PATH, headers=headers, data=multipart)

    def get_ad(self, ad_id: int | str, token: str) -> Response:
        return self._request("GET", LISTING_ITEM_PATH.format(ad_id=ad_id), headers=self._auth_headers(token))

    def update_ad(self, ad_id: int | str, payload: dict[str, Any], token: str) -> Response:
        current_response = self.get_ad(ad_id, token)
        current_payload: dict[str, Any] = {}
        if current_response.status_code == 200:
            try:
                current_payload = current_response.json()
            except ValueError:
                current_payload = {}

        image_payload = {
            "img1": current_payload.get("img1"),
            "img2": current_payload.get("img2"),
            "img3": current_payload.get("img3"),
        }
        update_payload = merge_dicts(BASE_AD_PAYLOAD, image_payload)
        update_payload = merge_dicts(update_payload, payload)

        return self._request(
            "PATCH",
            UPDATE_AD_PATH.format(ad_id=ad_id),
            headers=self._auth_headers(token, "application/json"),
            json=update_payload,
        )

    def delete_ad(self, ad_id: int | str, token: str) -> Response:
        return self._request("DELETE", DELETE_AD_PATH.format(ad_id=ad_id), headers=self._auth_headers(token))

    @staticmethod
    def extract_token(response_json: dict[str, Any]) -> str | None:
        return extract_token(response_json)

    @staticmethod
    def extract_entity_id(response_json: dict[str, Any]) -> int | str | None:
        return extract_entity_id(response_json)
