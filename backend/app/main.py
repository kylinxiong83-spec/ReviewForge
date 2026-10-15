import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_database, list_results, save_result
from .github import fetch_pull_request_diff, verify_signature
from .reviewer import analyze
from .schemas import AnalyzeRequest, ReviewRecord, ReviewResult
from .tasks import review_pull_request

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="ReviewForge API",
    version="0.1.0",
    description="Evidence-driven pull request review for engineering teams.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/reviews/analyze", response_model=ReviewResult)
def analyze_diff(request: AnalyzeRequest) -> ReviewResult:
    result = analyze(request)
    save_result(result)
    return result


@app.get("/api/reviews", response_model=list[ReviewRecord])
def recent_reviews() -> list[ReviewRecord]:
    return [
        ReviewRecord(
            id=row.id,
            repository=row.repository,
            pull_request=row.pull_request,
            status=row.status,
            score=row.score,
            summary=row.summary,
            lines_reviewed=row.lines_reviewed,
            findings=row.findings,
        )
        for row in list_results()
    ]


@app.post("/api/github/webhook", status_code=202)
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(default=""),
    x_github_event: str = Header(default=""),
) -> dict[str, str]:
    payload = await request.body()
    if not verify_signature(payload, x_hub_signature_256, settings.github_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    if x_github_event != "pull_request":
        return {"status": "ignored"}
    body = json.loads(payload)
    if body.get("action") not in {"opened", "reopened", "synchronize"}:
        return {"status": "ignored"}
    repository = body["repository"]["full_name"]
    pull_request = int(body["number"])
    if settings.reviewforge_eager:
        diff = fetch_pull_request_diff(repository, pull_request, settings.github_token)
        save_result(analyze(AnalyzeRequest(repository=repository, pull_request=pull_request, diff=diff)))
    else:
        review_pull_request.delay(repository, pull_request)
    return {"status": "queued"}

