class TestAdDeletion:
    def test_delete_own_ad(self, api, auth_token, created_ad):
        response = api.delete_ad(created_ad["id"], auth_token)

        assert response.status_code in (200, 202, 204), response.text
