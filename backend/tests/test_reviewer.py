from app.reviewer import analyze
from app.schemas import AnalyzeRequest, Severity

DEMO_DIFF = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,2 +1,5 @@
 def load_user(user_id):
+    api_key = "sk-this-should-never-be-committed"
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    return eval(input())
"""


def test_detects_security_findings() -> None:
    result = analyze(AnalyzeRequest(repository="kylin/demo", pull_request=7, diff=DEMO_DIFF))
    assert result.lines_reviewed == 3
    assert result.score < 50
    assert len(result.findings) == 3
    assert all(item.severity in {Severity.critical, Severity.high} for item in result.findings)


def test_clean_diff_receives_full_score() -> None:
    diff = """diff --git a/math.py b/math.py
--- a/math.py
+++ b/math.py
@@ -1 +1,2 @@
+def add(left, right):
+    return left + right
"""
    result = analyze(AnalyzeRequest(diff=diff))
    assert result.score == 100
    assert result.findings == []

