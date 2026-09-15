import pytest

from api_client import DeskApi
from data import BASE_AD_PAYLOAD, BASE_USER_PAYLOAD
from email_generator import generate_unique_email
from utils import merge_dicts


@pytest.fixture
def api() -> DeskApi:
    return DeskApi()


@pytest.fixture
def user_payload() -> dict:
    return merge_dicts(BASE_USER_PAYLOAD, {"email": generate_unique_email()})


@pytest.fixture
def registered_user(api: DeskApi, user_payload: dict) -> dict:
    response = api.register_user(user_payload)
    assert response.status_code in (200, 201), response.text
    return user_payload


@pytest.fixture
def auth_token(api: DeskApi, registered_user: dict) -> str:
    return api.auth_token_from_login(
        {
            "email": registered_user["email"],
            "password": registered_user["password"],
        }
    )


@pytest.fixture
def another_registered_user(api: DeskApi) -> dict:
    payload = merge_dicts(BASE_USER_PAYLOAD, {"email": generate_unique_email()})
    response = api.register_user(payload)
    assert response.status_code in (200, 201), response.text
    return payload


@pytest.fixture
def another_auth_token(api: DeskApi, another_registered_user: dict) -> str:
    return api.auth_token_from_login(
        {
            "email": another_registered_user["email"],
            "password": another_registered_user["password"],
        }
    )


@pytest.fixture
def created_ad(api: DeskApi, auth_token: str) -> dict:
    response = api.create_ad(BASE_AD_PAYLOAD, auth_token)
    assert response.status_code in (200, 201), response.text
    response_json = response.json()
    ad_id = api.extract_entity_id(response_json)
    assert ad_id is not None, f"ID объявления не найден в ответе: {response.text}"
    return {
        "id": ad_id,
        "response_json": response_json,
    }
