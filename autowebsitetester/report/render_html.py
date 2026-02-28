from __future__ import annotations

from autowebsitetester.types import ScanResult


def render_html(result: ScanResult) -> str:
    items = []
    for bug in result.failures:
        items.append(
            f"""
            <article>
              <h3>{bug.title}</h3>
              <p><strong>Severity:</strong> {bug.severity.value}</p>
              <p><strong>URL:</strong> {bug.page_url}</p>
              <p><strong>Message:</strong> {bug.message}</p>
            </article>
            """
        )

    bug_block = "\n".join(items) if items else "<p>No bugs detected.</p>"
    return f"""
<!doctype html>
<html>
<head>
  <meta charset='utf-8'/>
  <title>AutoWebsiteTester Report</title>
</head>
<body>
  <h1>AutoWebsiteTester Scan Report</h1>
  <p>Root URL: {result.root_url}</p>
  <p>Visited pages: {len(result.visited_urls)}</p>
  <p>Actions executed: {len(result.actions)}</p>
  <p>Bugs found: {len(result.failures)}</p>
  <section>
    <h2>Bugs</h2>
    {bug_block}
  </section>
</body>
</html>
""".strip()
