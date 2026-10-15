"use client";

import { FormEvent, useState } from "react";

type Finding = {
  file: string;
  line: number;
  severity: "critical" | "high" | "medium" | "low";
  category: string;
  title: string;
  explanation: string;
  recommendation: string;
  confidence: number;
};

type Result = {
  repository: string;
  pull_request: number;
  score: number;
  summary: string;
  lines_reviewed: number;
  findings: Finding[];
};

const demoDiff = `diff --git a/server/user.py b/server/user.py
--- a/server/user.py
+++ b/server/user.py
@@ -18,2 +18,5 @@ def get_user(user_id):
+    api_key = "sk-this-should-never-be-committed"
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    return eval(input())`;

const initial: Result = {
  repository: "kylin-xiong/sample-api",
  pull_request: 42,
  score: 34,
  summary: "Detected 3 actionable issues across 1 file.",
  lines_reviewed: 3,
  findings: [
    {
      file: "server/user.py",
      line: 19,
      severity: "critical",
      category: "security",
      title: "Possible hard-coded credential",
      explanation: "The added line appears to contain a credential that could leak through version control.",
      recommendation: "Load the value from a secret manager and rotate the exposed value.",
      confidence: 0.96,
    },
    {
      file: "server/user.py",
      line: 20,
      severity: "high",
      category: "security",
      title: "SQL query built through string interpolation",
      explanation: "Interpolating values into SQL can create an injection path.",
      recommendation: "Use a parameterized query or the library's query builder.",
      confidence: 0.89,
    },
    {
      file: "server/user.py",
      line: 21,
      severity: "high",
      category: "security",
      title: "Dynamic code execution",
      explanation: "Executing dynamically constructed code can allow untrusted input to run with application privileges.",
      recommendation: "Replace dynamic execution with an explicit parser or an allow-listed dispatch table.",
      confidence: 0.92,
    },
  ],
};

export default function Home() {
  const [diff, setDiff] = useState(demoDiff);
  const [result, setResult] = useState<Result>(initial);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("Demo results are loaded. Run the review to call the API.");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setMessage("Analyzing added lines and ranking findings…");
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/reviews/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repository: "kylin-xiong/sample-api", pull_request: 42, diff }),
      });
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      setResult(await response.json());
      setMessage("Review completed and stored in the audit history.");
    } catch (error) {
      setMessage(`Could not reach the local API. Start Docker Compose and try again. ${String(error)}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <nav>
        <div className="brand"><span className="mark">RF</span>ReviewForge</div>
        <div className="navlinks"><a href="#review">Review</a><a href="#architecture">Architecture</a><a href="https://github.com" target="_blank">GitHub ↗</a></div>
      </nav>

      <section className="hero">
        <div className="eyebrow"><span /> Evidence-driven code review</div>
        <h1>Ship with confidence,<br /><em>not guesswork.</em></h1>
        <p>ReviewForge turns pull request diffs into traceable findings with line-level evidence, confidence scores, and concrete fixes.</p>
        <div className="heroActions"><a className="primary" href="#review">Analyze a diff <b>→</b></a><a className="secondary" href="#architecture">See how it works</a></div>
        <div className="trust"><span>✓ Deterministic baseline</span><span>✓ Signed webhooks</span><span>✓ Human-readable evidence</span></div>
      </section>

      <section className="workspace" id="review">
        <div className="workspaceHeader">
          <div><span className="live" /> LIVE REVIEW</div>
          <span>kylin-xiong/sample-api&nbsp;&nbsp;·&nbsp;&nbsp;PR #42</span>
        </div>
        <div className="workspaceGrid">
          <form onSubmit={submit} className="diffPanel">
            <div className="panelTitle"><span>Pull request diff</span><span>{diff.split("\n").length} lines</span></div>
            <textarea value={diff} onChange={(event) => setDiff(event.target.value)} aria-label="Pull request diff" />
            <div className="formFooter"><small>{message}</small><button disabled={loading}>{loading ? "Reviewing…" : "Run review →"}</button></div>
          </form>

          <div className="resultsPanel">
            <div className="scoreRow">
              <div className={`score ${result.score > 75 ? "good" : result.score > 45 ? "warn" : "risk"}`}><b>{result.score}</b><span>/100</span></div>
              <div><strong>Merge confidence</strong><p>{result.summary}</p></div>
            </div>
            <div className="metrics"><div><b>{result.findings.length}</b><span>findings</span></div><div><b>{result.lines_reviewed}</b><span>lines reviewed</span></div><div><b>{result.findings.length ? Math.round(result.findings.reduce((a, f) => a + f.confidence, 0) / result.findings.length * 100) : 100}%</b><span>avg. confidence</span></div></div>
            <div className="findings">
              {result.findings.length === 0 ? <div className="empty">No high-confidence issues detected.</div> : result.findings.map((finding, index) => (
                <article key={`${finding.file}-${finding.line}-${index}`}>
                  <div className="findingTop"><span className={`badge ${finding.severity}`}>{finding.severity}</span><code>{finding.file}:{finding.line}</code><span>{Math.round(finding.confidence * 100)}%</span></div>
                  <h3>{finding.title}</h3>
                  <p>{finding.explanation}</p>
                  <div className="fix"><b>Suggested fix</b>{finding.recommendation}</div>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="architecture" id="architecture">
        <div><span className="sectionNumber">01</span><h2>Designed for<br />explainability.</h2><p>Every finding links back to a changed line, a named rule, and a confidence score. The deterministic engine runs offline; model-based reviewers can be added without hiding the evidence.</p></div>
        <div className="flow">
          <div><b>GitHub</b><span>Signed webhook</span></div><i>→</i><div><b>FastAPI</b><span>Validation + API</span></div><i>→</i><div><b>Celery</b><span>Async analysis</span></div><i>→</i><div><b>Postgres</b><span>Audit history</span></div>
        </div>
      </section>

      <footer><div className="brand"><span className="mark">RF</span>ReviewForge</div><span>Built by Kylin Xiong · 2026</span></footer>
    </main>
  );
}
