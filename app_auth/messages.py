from dataclasses import dataclass

@dataclass(frozen=True)
class AuthMessages:
    INVALID_CREDENTIALS:    str = "Invalid credentials."
    LOGOUT_SUCCESS:         str = "User logged out successfully."
    INVALID_TOKEN:          str = "The provided token is invalid or has expired."
    INACTIVE_USER:          str = "User account is inactive."