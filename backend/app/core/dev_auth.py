import uuid

# TEMPORARY: until Phase 8 adds real Supabase Auth, every request is treated
# as this one fixed development user. Replace with the real authenticated
# user's ID (from a verified JWT) in Phase 8. Do not rely on this in production.
DEV_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def get_current_user_id() -> uuid.UUID:
    """Placeholder for the real auth dependency added in Phase 8."""
    return DEV_USER_ID