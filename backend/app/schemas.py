from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class Finding(BaseModel):
    file: str
    line: int = Field(ge=1)
    severity: Severity
    category: str
    title: str
    explanation: str
    recommendation: str
    confidence: float = Field(ge=0, le=1)


class AnalyzeRequest(BaseModel):
    repository: str = "demo/repository"
    pull_request: int = Field(default=1, ge=1)
    diff: str = Field(min_length=1, max_length=250_000)


class ReviewResult(BaseModel):
    repository: str
    pull_request: int
    score: int = Field(ge=0, le=100)
    summary: str
    lines_reviewed: int
    findings: list[Finding]


class ReviewRecord(ReviewResult):
    id: int
    status: str

