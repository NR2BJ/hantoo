import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    __table_args__ = (UniqueConstraint("account_id", "snapshot_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kis_accounts.id"), nullable=False
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)

    total_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    cash_balance: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    holdings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    daily_pnl: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    total_pnl: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
