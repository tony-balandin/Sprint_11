from data import UPDATED_AD_PAYLOAD


class TestAdUpdate:
    def test_update_any_field_in_own_ad(self, api, auth_token, created_ad):
        response = api.update_ad(created_ad["id"], UPDATED_AD_PAYLOAD, auth_token)

        assert response.status_code in (200, 201), response.text

    def test_cannot_update_other_users_ad(self, api, another_auth_token, created_ad):
        response = api.update_ad(created_ad["id"], UPDATED_AD_PAYLOAD, another_auth_token)

        assert response.status_code in (401, 403, 404), response.text
