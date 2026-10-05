from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.publication import PublicationOut


class ManuscriptFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    publication_id: UUID
    version_number: int
    original_filename: str
    mime_type: str
    size_bytes: int
    sha256: str
    is_original_submission: bool
    public_on_publish: bool
    uploaded_at: datetime


class TrustSnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    submission_id: str
    publication_id: UUID
    manuscript_file_id: UUID | None
    submission_sequence: int
    publication_version: int
    fingerprint_sha256: str
    immutable: bool
    submitted_at: datetime


class TrustAccessEventOut(BaseModel):
    id: UUID
    actor_name: str
    actor_role: str | None
    action: str
    object_type: str | None
    details: dict
    event_hash: str
    created_at: datetime


class EditorTrustState(BaseModel):
    assigned_to_me: bool
    confidentiality_accepted: bool
    conflict_decision: str | None
    can_access_manuscript: bool


class TrustOverviewOut(BaseModel):
    publication_id: UUID
    files: list[ManuscriptFileOut]
    snapshots: list[TrustSnapshotOut]
    latest_snapshot: TrustSnapshotOut | None
    editor_state: EditorTrustState | None = None


class ConflictDeclarationRequest(BaseModel):
    decision: str = Field(pattern="^(no_conflict|recuse)$")
    note: str | None = Field(default=None, max_length=2000)


class ReviewPackageOut(BaseModel):
    publication: PublicationOut
    files: list[ManuscriptFileOut]


class PublicCertificateVerification(BaseModel):
    submission_id: str
    valid: bool
    submitted_at: datetime
    fingerprint_sha256: str
    publication_status: str
    published_title: str | None = None
