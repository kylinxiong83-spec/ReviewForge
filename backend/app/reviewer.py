import re
from dataclasses import dataclass

from .schemas import AnalyzeRequest, Finding, ReviewResult, Severity


@dataclass(frozen=True)
class Rule:
    pattern: re.Pattern[str]
    severity: Severity
    category: str
    title: str
    explanation: str
    recommendation: str
    confidence: float


RULES = [
    Rule(
        re.compile(r"(?i)(api[_-]?key|secret|password)\s*[=:]\s*['\"][^'\"]{8,}"),
        Severity.critical,
        "security",
        "Possible hard-coded credential",
        "The added line appears to contain a credential that could leak through version control.",
        "Load the value from a secret manager or environment variable and rotate the exposed value.",
        0.96,
    ),
    Rule(
        re.compile(r"\b(eval|exec)\s*\("),
        Severity.high,
        "security",
        "Dynamic code execution",
        "Executing dynamically constructed code can allow untrusted input to run with application privileges.",
        "Replace dynamic execution with an explicit parser or an allow-listed dispatch table.",
        0.92,
    ),
    Rule(
        re.compile(r"(?i)(f['\"].*(SELECT|INSERT|UPDATE|DELETE)|(SELECT|INSERT|UPDATE|DELETE).*(\+|\.format\())"),
        Severity.high,
        "security",
        "SQL query built through string interpolation",
        "Interpolating values into SQL can create an injection path and makes queries harder to cache.",
        "Use parameterized queries or the query builder provided by the database library.",
        0.89,
    ),
    Rule(
        re.compile(r"^\s*except\s*:\s*$"),
        Severity.medium,
        "reliability",
        "Bare exception handler",
        "A bare exception catches shutdown signals and hides the reason an operation failed.",
        "Catch the narrowest expected exception and log enough context to diagnose failures.",
        0.95,
    ),
    Rule(
        re.compile(r"(dangerouslySetInnerHTML|\.innerHTML\s*=)"),
        Severity.high,
        "security",
        "Unescaped HTML injection surface",
        "Rendering raw HTML can introduce cross-site scripting when the value includes user-controlled data.",
        "Render structured elements or sanitize the HTML with a maintained allow-list sanitizer.",
        0.90,
    ),
    Rule(
        re.compile(r"\bconsole\.log\("),
        Severity.low,
        "maintainability",
        "Debug logging left in application code",
        "Unstructured logs add noise and can accidentally expose request data.",
        "Use the application logger with an appropriate level and structured fields.",
        0.82,
    ),
]


def _parse_added_lines(diff: str) -> list[tuple[str, int, str]]:
    file_name = "unknown"
    new_line = 0
    added: list[tuple[str, int, str]] = []
    for raw in diff.splitlines():
        if raw.startswith("+++ b/"):
            file_name = raw[6:]
            continue
        if raw.startswith("@@"):
            match = re.search(r"\+(\d+)", raw)
            if match:
                new_line = int(match.group(1)) - 1
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            new_line += 1
            added.append((file_name, new_line, raw[1:]))
        elif not raw.startswith("-"):
            new_line += 1
    return added


def analyze(request: AnalyzeRequest) -> ReviewResult:
    added = _parse_added_lines(request.diff)
    findings: list[Finding] = []
    seen: set[tuple[str, int, str]] = set()
    for file_name, line_number, line in added:
        for rule in RULES:
            key = (file_name, line_number, rule.title)
            if rule.pattern.search(line) and key not in seen:
                seen.add(key)
                findings.append(
                    Finding(
                        file=file_name,
                        line=max(line_number, 1),
                        severity=rule.severity,
                        category=rule.category,
                        title=rule.title,
                        explanation=rule.explanation,
                        recommendation=rule.recommendation,
                        confidence=rule.confidence,
                    )
                )

    penalties = {Severity.critical: 30, Severity.high: 18, Severity.medium: 9, Severity.low: 3}
    score = max(0, 100 - sum(penalties[item.severity] for item in findings))
    if not findings:
        summary = "No high-confidence issues were detected in the added lines. Human review is still recommended."
    else:
        summary = f"Detected {len(findings)} actionable issue{'s' if len(findings) != 1 else ''} across {len({f.file for f in findings})} file(s)."
    return ReviewResult(
        repository=request.repository,
        pull_request=request.pull_request,
        score=score,
        summary=summary,
        lines_reviewed=len(added),
        findings=findings,
    )
