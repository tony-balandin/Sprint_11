class TestUserLogin:
    def test_login_registered_user(self, api, registered_user):
        response = api.login_user(
            {
                "email": registered_user["email"],
                "password": registered_user["password"],
            }
        )

        assert response.status_code in (200, 201), response.text
        assert api.extract_token(response.json()) is not None
