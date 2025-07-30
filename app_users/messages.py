from dataclasses import dataclass

@dataclass(frozen=True)
class UserMessages:
    USER_NOT_FOUND:             str = "User not found."
    USER_CREATED:               str = "User created successfully."
    USER_UPDATED:               str = "User updated successfully."
    USER_DELETED:               str = "User set as inactive successfully."
    USERNAME_TAKEN:             str = "Username is already taken."
    USER_PROTECTED:             str = "Cannot update/delete superuser account."
    INVALID_USER_ID:            str = "User ID must be greater than zero."

    # Password-related messages
    PASSWORD_TOO_SHORT:         str = "Password must be at least 8 characters long."
    PASSWORD_MISSING_UPPER:     str = "Password must contain at least one uppercase letter."
    PASSWORD_MISSING_LOWER:     str = "Password must contain at least one lowercase letter."
    PASSWORD_MISSING_DIGIT:     str = "Password must contain at least one digit."
    PASSWORD_MISSING_SPECIAL:   str = "Password must contain at least one special character."