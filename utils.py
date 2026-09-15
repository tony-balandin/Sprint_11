from copy import deepcopy
from typing import Any


def merge_dicts(base: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = deepcopy(base)
    if extra:
        payload.update(extra)
    return payload


def extract_token(response_json: dict[str, Any]) -> str | None:
    token_keys = ("token", "accessToken", "access_token", "jwt")

    def _extract_from_dict(source: dict[str, Any]) -> str | None:
        for key in token_keys:
            value = source.get(key)
            if isinstance(value, str) and value:
                return value
            if isinstance(value, dict):
                nested = _extract_from_dict(value)
                if nested:
                    return nested
        return None

    direct = _extract_from_dict(response_json)
    if direct:
        return direct

    data = response_json.get("data")
    if isinstance(data, dict):
        return _extract_from_dict(data)

    return None


def extract_entity_id(response_json: dict[str, Any]) -> int | str | None:
    id_keys = ("id", "_id", "advertisementId", "adId", "postId", "itemId")

    def _extract_from_dict(source: dict[str, Any]) -> int | str | None:
        for key in id_keys:
            if key in source and source[key] is not None:
                return source[key]
        for value in source.values():
            if isinstance(value, dict):
                nested = _extract_from_dict(value)
                if nested is not None:
                    return nested
        return None

    direct = _extract_from_dict(response_json)
    if direct is not None:
        return direct

    data = response_json.get("data")
    if isinstance(data, dict):
        return _extract_from_dict(data)

    return None
