from data import BASE_USER_PAYLOAD
from email_generator import generate_unique_email
from utils import merge_dicts


class TestUserRegistration:
    def test_register_new_user_with_unique_email(self, api):
        payload = merge_dicts(BASE_USER_PAYLOAD, {"email": generate_unique_email()})

        response = api.register_user(payload)

        assert response.status_code in (200, 201), response.text

    def test_register_existing_user_twice(self, api):
        payload = merge_dicts(BASE_USER_PAYLOAD, {"email": generate_unique_email()})
        first_response = api.register_user(payload)
        second_response = api.register_user(payload)

        assert first_response.status_code in (200, 201), first_response.text
        assert second_response.status_code in (400, 409), second_response.text
