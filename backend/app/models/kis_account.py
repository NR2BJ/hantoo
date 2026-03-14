import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, LargeBinary, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class KISAccount(Base):
    __tablename__ = "kis_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)  # personal, shared
    environment: Mapped[str] = mapped_column(String(10), nullable=False, default="prod")

    # Encrypted credentials (AES-256 via Fernet)
    app_key_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    app_secret_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    account_number: Mapped[str] = mapped_column(String(20), nullable=False)
    product_code: Mapped[str] = mapped_column(String(2), nullable=False, default="01")
    hts_id: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Token state (cached)
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    owner = relationship("User", back_populates="kis_accounts")
    access_grants = relationship("KISAccountAccess", back_populates="account")


class KISAccountAccess(Base):
    __tablename__ = "kis_account_access"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kis_accounts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    permission: Mapped[str] = mapped_column(String(20), nullable=False, default="trade")
    granted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    account = relationship("KISAccount", back_populates="access_grants")
    user = relationship(
        "User", back_populates="account_access",
        primaryjoin="KISAccountAccess.user_id == foreign(User.id)",
        foreign_keys=[user_id]
    )
