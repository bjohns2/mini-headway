from fastapi import Header

DEV_PROVIDER_ID = 1


def current_provider_id(x_user_id: int | None = Header(default=None)) -> int:
    return x_user_id if x_user_id is not None else DEV_PROVIDER_ID
