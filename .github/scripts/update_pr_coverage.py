#!/usr/bin/env python3
"""
Update the coverage section of the current pull request body.

Runs `coverage report`, then writes the result between HTML comment markers in
the PR description. Existing content is preserved; the generated section is
replaced on subsequent runs.

Requires GH_TOKEN (or gh auth) with permission to edit pull requests.
"""

import os
import re
import subprocess
import tempfile

START_MARKER = "<!-- coverage-report:start -->"
END_MARKER = "<!-- coverage-report:end -->"


def run(*args: str) -> str:
    result = subprocess.run(args, check=True, text=True, capture_output=True)
    return result.stdout


def build_section(python_version: str) -> str:
    report = run("coverage", "report").strip()
    total = next((line for line in report.splitlines() if line.startswith("TOTAL")), "")

    return (
        f"{START_MARKER}\n"
        f"### 🧪 Test coverage (Python {python_version})\n\n"
        f"`{total.strip()}`\n\n"
        "<details>\n"
        "<summary>Per-file report</summary>\n\n"
        "```\n"
        f"{report}\n"
        "```\n\n"
        "</details>\n"
        f"{END_MARKER}"
    )


def main() -> None:
    pr_number = os.environ["PR_NUMBER"]
    python_version = os.environ.get("PYTHON_VERSION", "3.12")

    body = run("gh", "pr", "view", pr_number, "--json", "body", "-q", ".body").strip()
    section = build_section(python_version)

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )
    if pattern.search(body):
        new_body = pattern.sub(section, body)
    elif body:
        new_body = f"{body}\n\n{section}"
    else:
        new_body = section

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
        handle.write(new_body + "\n")
        body_file = handle.name

    try:
        subprocess.run(
            ["gh", "pr", "edit", pr_number, "--body-file", body_file],
            check=True,
        )
    finally:
        os.unlink(body_file)


if __name__ == "__main__":
    main()
