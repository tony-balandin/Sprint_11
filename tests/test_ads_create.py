from data import BASE_AD_PAYLOAD


class TestAdCreation:
    def test_create_ad_in_any_category(self, api, auth_token):
        response = api.create_ad(BASE_AD_PAYLOAD, auth_token)

        assert response.status_code in (200, 201), response.text
        assert api.extract_entity_id(response.json()) is not None
