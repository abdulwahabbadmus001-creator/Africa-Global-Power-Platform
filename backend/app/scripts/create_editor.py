from datetime import (
    datetime,
    timezone,
)
from getpass import getpass

from sqlalchemy import select

from app.core.security import (
    hash_password,
)
from app.db.session import SessionLocal
from app.models.user import (
    User,
    UserRole,
)


ALLOWED_ROLES = {
    "reviewer": UserRole.reviewer,
    "editor": UserRole.editor,
    "senior_editor": (
        UserRole.senior_editor
    ),
    "managing_editor": (
        UserRole.managing_editor
    ),
    "super_admin": (
        UserRole.super_admin
    ),
}


def main() -> None:
    print("")
    print(
        "Africa & Global Power "
        "— Editorial Account Provisioning"
    )
    print("-" * 60)

    email = input(
        "Editorial email: "
    ).strip().lower()

    first_name = input(
        "First name: "
    ).strip()

    last_name = input(
        "Last name: "
    ).strip()

    print("")
    print(
        "Available roles:"
    )

    for role_name in ALLOWED_ROLES:
        print(
            f"  - {role_name}"
        )

    print("")

    role_input = input(
        "Role: "
    ).strip().lower()

    if role_input not in ALLOWED_ROLES:
        raise SystemExit(
            "Invalid editorial role."
        )

    password = getpass(
        "Password: "
    )

    password_confirm = getpass(
        "Confirm password: "
    )

    if password != password_confirm:
        raise SystemExit(
            "Passwords do not match."
        )

    if len(password) < 12:
        raise SystemExit(
            "Editorial passwords must "
            "contain at least 12 characters."
        )

    db = SessionLocal()

    try:
        existing = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if existing:
            raise SystemExit(
                "An account with this email "
                "already exists."
            )

        user = User(
            email=email,
            password_hash=(
                hash_password(
                    password
                )
            ),
            first_name=first_name,
            last_name=last_name,
            role=(
                ALLOWED_ROLES[
                    role_input
                ]
            ),
            institution=(
                "Africa & Global Power"
            ),
            is_active=True,
            is_email_verified=True,
            email_verified_at=(
                datetime.now(
                    timezone.utc
                )
            ),
            editor_mfa_enabled=False,
            editor_mfa_generation=1,
        )

        db.add(user)

        db.commit()

        print("")
        print(
            "Editorial account created."
        )

        print(
            f"Email: {email}"
        )

        print(
            f"Role: {role_input}"
        )

        print("")
        print(
            "The editor must now sign in "
            "through /editorial/login and "
            "configure an authenticator app."
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()