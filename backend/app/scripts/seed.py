from datetime import datetime, timezone

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.publication import (
    Publication,
    PublicationStatus,
    PublicationVersion,
)
from app.models.user import (
    User,
    UserRole,
)


def get_or_create_user(
    db,
    email,
    first,
    last,
    role,
    **kwargs,
):
    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if user:
        user.is_active = True
        user.is_email_verified = True

        if user.email_verified_at is None:
            user.email_verified_at = (
                datetime.now(timezone.utc)
            )

        return user

    user = User(
        email=email,
        password_hash=hash_password(
            "ChangeMe123!"
        ),
        first_name=first,
        last_name=last,
        role=role,
        is_active=True,
        is_email_verified=True,
        email_verified_at=(
            datetime.now(timezone.utc)
        ),
        **kwargs,
    )

    db.add(user)
    db.flush()

    return user


def main():
    db = SessionLocal()

    try:
        editor = get_or_create_user(
            db,
            "editor@agp.local",
            "AGP",
            "Editor",
            UserRole.super_admin,
            institution="Africa & Global Power",
            country="Nigeria",
            expertise=(
                "Editorial policy, "
                "research integrity, "
                "African affairs"
            ),
        )

        researcher = get_or_create_user(
            db,
            "researcher@agp.local",
            "Amina",
            "Okafor",
            UserRole.researcher,
            institution=(
                "Centre for African Futures"
            ),
            country="Nigeria",
            expertise=(
                "AI governance, digital policy, "
                "political economy"
            ),
            bio=(
                "Researcher studying technology "
                "governance and Africa's position "
                "in global systems."
            ),
        )

        exists = db.scalar(
            select(Publication).where(
                Publication.slug
                == (
                    "africa-ai-governance-"
                    "beyond-policy-importation"
                )
            )
        )

        if not exists:
            pub = Publication(
                author_id=researcher.id,
                title=(
                    "Africa's AI Governance "
                    "Challenge: Beyond Policy "
                    "Importation"
                ),
                slug=(
                    "africa-ai-governance-"
                    "beyond-policy-importation"
                ),
                abstract=(
                    "African governments are "
                    "adopting artificial "
                    "intelligence strategies at "
                    "speed, but durable governance "
                    "will depend on institutions, "
                    "local evidence and "
                    "implementation capacity rather "
                    "than imported policy templates."
                ),
                body=(
                    "Artificial intelligence "
                    "governance in Africa is often "
                    "framed as a choice between "
                    "adapting external regulatory "
                    "models and delaying action. "
                    "That framing is too narrow.\n\n"
                    "This demonstration publication "
                    "shows how long-form research "
                    "will appear in AGP."
                ),
                publication_type=(
                    "policy analysis"
                ),
                topic="AI & Technology",
                region="Africa",
                keywords=[
                    "AI governance",
                    "Africa",
                    "digital policy",
                ],
                references=[
                    {
                        "title": (
                            "African Union "
                            "Continental Artificial "
                            "Intelligence Strategy"
                        ),
                        "url": "https://au.int/",
                    }
                ],
                methodology=(
                    "Desk research and comparative "
                    "policy analysis."
                ),
                limitations=(
                    "Demonstration content only; "
                    "not a completed empirical "
                    "study."
                ),
                policy_implications=(
                    "Strengthen local regulatory "
                    "capacity, research "
                    "infrastructure and cross-border "
                    "policy coordination."
                ),
                status=(
                    PublicationStatus.published
                ),
                current_version=1,
                published_at=(
                    datetime.now(timezone.utc)
                ),
            )

            db.add(pub)
            db.flush()

            db.add(
                PublicationVersion(
                    publication_id=pub.id,
                    version_number=1,
                    title=pub.title,
                    abstract=pub.abstract,
                    body=pub.body,
                    created_by_id=(
                        researcher.id
                    ),
                    change_note=(
                        "Initial publication"
                    ),
                )
            )

        db.commit()

        print(
            "Seed complete. "
            "Development editor and researcher "
            "accounts are email-verified."
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()