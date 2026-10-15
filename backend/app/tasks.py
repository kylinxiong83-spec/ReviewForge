from celery import Celery

from .config import get_settings
from .database import init_database, save_result
from .github import fetch_pull_request_diff
from .reviewer import analyze
from .schemas import AnalyzeRequest

settings = get_settings()
celery = Celery("reviewforge", broker=settings.redis_url, backend=settings.redis_url)


@celery.task(name="review_pull_request")
def review_pull_request(repository: str, pull_request: int) -> int:
    init_database()
    diff = fetch_pull_request_diff(repository, pull_request, settings.github_token)
    result = analyze(AnalyzeRequest(repository=repository, pull_request=pull_request, diff=diff))
    return save_result(result).id

