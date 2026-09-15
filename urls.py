BASE_URL = "https://qa-desk.stand.praktikum-services.ru"

API_PREFIXES = (
    "/api",
    "/api/v1",
    "/v1",
    "",
)

REGISTER_SUFFIXES = (
    "/users",
    "/users/",
    "/users/register",
    "/users/signup",
    "/auth/register",
    "/auth/signup",
    "/auth/sign-up",
    "/signup",
    "/register",
)

LOGIN_SUFFIXES = (
    "/auth/login",
    "/auth/signin",
    "/auth/sign-in",
    "/users/login",
    "/users/signin",
    "/signin",
    "/sign-in",
    "/login",
)


def build_paths(suffixes: tuple[str, ...]) -> tuple[str, ...]:
    paths: list[str] = []
    for prefix in API_PREFIXES:
        for suffix in suffixes:
            path = f"{prefix}{suffix}" or "/"
            if path not in paths:
                paths.append(path)
    return tuple(paths)


REGISTER_PATHS = build_paths(REGISTER_SUFFIXES)
LOGIN_PATHS = build_paths(LOGIN_SUFFIXES)
CREATE_AD_PATH = "/api/create-listing"
LISTING_ITEM_PATH = "/api/listings/{ad_id}"
UPDATE_AD_PATH = "/api/update-offer/{ad_id}"
DELETE_AD_PATH = "/api/listings/{ad_id}"
