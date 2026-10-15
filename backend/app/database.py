from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from .config import get_settings
from .schemas import ReviewResult


class Base(DeclarativeBase):
    pass


class ReviewRun(Base):
    __tablename__ = "review_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository: Mapped[str] = mapped_column(String(240), index=True)
    pull_request: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    score: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(String(500))
    lines_reviewed: Mapped[int] = mapped_column(Integer)
    findings: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


engine = create_engine(get_settings().database_url)


def init_database() -> None:
    Base.metadata.create_all(engine)


def save_result(result: ReviewResult) -> ReviewRun:
    row = ReviewRun(
        repository=result.repository,
        pull_request=result.pull_request,
        score=result.score,
        summary=result.summary,
        lines_reviewed=result.lines_reviewed,
        findings=[finding.model_dump(mode="json") for finding in result.findings],
    )
    with Session(engine) as session:
        session.add(row)
        session.commit()
        session.refresh(row)
        return row


def list_results(limit: int = 20) -> list[ReviewRun]:
    with Session(engine) as session:
        return list(session.query(ReviewRun).order_by(ReviewRun.id.desc()).limit(limit))

