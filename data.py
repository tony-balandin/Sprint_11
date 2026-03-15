DEFAULT_PASSWORD = "Practicum_Desk_2026!"
DEFAULT_NAME_PREFIX = "Tony"

BASE_USER_PAYLOAD = {
    "name": DEFAULT_NAME_PREFIX,
    "password": DEFAULT_PASSWORD,
}

BASE_AD_PAYLOAD = {
    "name": "test",
    "category": "Авто",
    "condition": "Новый",
    "city": "Москва",
    "description": "test",
    "price": "100",
}

UPDATED_AD_PAYLOAD = {
    "description": "updated by api test",
}
