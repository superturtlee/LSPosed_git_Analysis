#!/usr/bin/env python3
"""Compute external contribution ratio trend for LSPosed.

External contributors are defined as contributors outside the LSPosed GitHub org.
The script reports:
1) Main branch stats (origin/main or origin/master fallback)
2) Whole repository stats across all branches
3) Monthly ratio trend and overall summary for both scopes

Usage example:
  python lsposed_external_contrib_stats.py \
    --repo-url https://github.com/LSPosed/LSPosed.git \
    --output-dir ./output \
    --github-token "$GITHUB_TOKEN"
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import matplotlib.pyplot as plt


DEFAULT_REPO_URL = "https://github.com/LSPosed/LSPosed.git"
DEFAULT_OWNER = "LSPosed"
DEFAULT_REPO = "LSPosed"
DEFAULT_ORG = "LSPosed"

NOREPLY_PATTERNS = [
    re.compile(r"^\d+\+([^@]+)@users\.noreply\.github\.com$", re.IGNORECASE),
    re.compile(r"^([^@]+)@users\.noreply\.github\.com$", re.IGNORECASE),
]


@dataclass(frozen=True)
class Commit:
    sha: str
    date: str  # YYYY-MM-DD
    author_name: str
    author_email: str


@dataclass
class StatRow:
    month: str
    total: int
    external: int
    internal: int

    @property
    def external_ratio(self) -> float:
        if self.total == 0:
            return 0.0
        return self.external / self.total


@dataclass(frozen=True)
class Classification:
    is_external: bool
    is_bot: bool
    login: Optional[str]


@dataclass
class FileRatioRow:
    file_path: str
    total_lines: int
    internal_lines: int
    external_lines: int

    @property
    def internal_ratio(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return self.internal_lines / self.total_lines


IdentityCache = Dict[str, Dict[str, Classification]]


def new_identity_cache() -> IdentityCache:
    return {"email": {}, "login": {}}


def _cache_identity(
    cache: IdentityCache,
    info: Classification,
    *,
    author_name: str,
    author_email: str,
    login: Optional[str],
) -> None:
    e = author_email.strip().lower()
    if e and e != "unknown":
        cache["email"][e] = info
    if login:
        cache["login"][login.lower()] = info


def _get_cached_identity(
    cache: IdentityCache,
    *,
    author_name: str,
    author_email: str,
    login: Optional[str],
) -> Optional[Classification]:
    e = author_email.strip().lower()
    if e and e in cache["email"]:
        return cache["email"][e]
    if login:
        l = login.lower()
        if l in cache["login"]:
            return cache["login"][l]
    return None


def run_git(args: List[str], repo_dir: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        capture_output=True,
        text=False,
        check=False,
    )
    stdout = proc.stdout.decode("utf-8", errors="replace")
    stderr = proc.stderr.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(
            f"git command failed: {' '.join(args)}\n"
            f"stdout: {stdout}\n"
            f"stderr: {stderr}"
        )
    return stdout


def ensure_repo(repo_url: str, repo_dir: Path) -> None:
    if (repo_dir / ".git").exists() or (repo_dir / "HEAD").exists():
        # Existing clone (normal or bare)
        try:
            run_git(["remote", "set-url", "origin", repo_url], repo_dir)
        except RuntimeError:
            pass
        run_git(["fetch", "--all", "--prune", "--tags"], repo_dir)
        return

    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["git", "clone", "--filter=blob:none", repo_url, str(repo_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Failed to clone repository.\nstdout: {proc.stdout}\nstderr: {proc.stderr}"
        )


def build_headers(token: Optional[str]) -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "lsposed-external-contrib-stats",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_get_json(url: str, headers: Dict[str, str]) -> object:
    req = Request(url, headers=headers)
    with urlopen(req, timeout=30) as resp:
        payload = resp.read().decode("utf-8")
        return json.loads(payload)


def fetch_org_members(org: str, token: Optional[str]) -> Set[str]:
    headers = build_headers(token)
    members: Set[str] = set()
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/members?per_page=100&page={page}"
        try:
            data = github_get_json(url, headers)
        except HTTPError as exc:
            if exc.code in (403, 401):
                raise RuntimeError(
                    "GitHub API auth/rate limit issue while fetching org members. "
                    "Provide --github-token for higher rate limits."
                ) from exc
            raise
        except URLError as exc:
            raise RuntimeError(f"Network error while fetching org members: {exc}") from exc

        if not isinstance(data, list) or not data:
            break

        for user in data:
            login = (user or {}).get("login") if isinstance(user, dict) else None
            if isinstance(login, str) and login:
                members.add(login.lower())

        page += 1

    if not members:
        print(
            "[WARN] No public org members found via API. "
            "Classification may skew to external.",
            file=sys.stderr,
        )

    return members


def infer_login_from_email(email: str) -> Optional[str]:
    e = email.strip().lower()
    if not e:
        return None

    for pat in NOREPLY_PATTERNS:
        m = pat.match(e)
        if m:
            return m.group(1).lower()

    # Fallback: local-part can sometimes equal GitHub login.
    if "@" in e:
        local, _ = e.split("@", 1)
        if re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?", local):
            return local

    return None


def fetch_commit_identity(
    owner: str,
    repo: str,
    sha: str,
    token: Optional[str],
    headers_cache: Optional[Dict[str, str]] = None,
) -> tuple[Optional[str], bool]:
    headers = headers_cache or build_headers(token)
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    try:
        data = github_get_json(url, headers)
    except HTTPError as exc:
        raise RuntimeError(
            f"GitHub API error while fetching commit {sha}: HTTP {exc.code}. "
            "Please provide a valid --github-token and retry."
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"Network error while fetching commit {sha}: {exc}") from exc

    if not isinstance(data, dict):
        return None, False

    is_bot = False
    author = data.get("author")
    if isinstance(author, dict):
        user_type = author.get("type")
        if isinstance(user_type, str) and user_type.lower() == "bot":
            is_bot = True
        login = author.get("login")
        if isinstance(login, str) and login:
            normalized = login.lower()
            if normalized.endswith("[bot]"):
                is_bot = True
            return normalized, is_bot

    committer = data.get("committer")
    if isinstance(committer, dict):
        user_type = committer.get("type")
        if isinstance(user_type, str) and user_type.lower() == "bot":
            is_bot = True
        login = committer.get("login")
        if isinstance(login, str) and login:
            normalized = login.lower()
            if normalized.endswith("[bot]"):
                is_bot = True
            return normalized, is_bot

    return None, is_bot


def looks_like_bot(login: Optional[str], author_name: str, author_email: str) -> bool:
    parts = [
        (login or "").lower(),
        author_name.strip().lower(),
        author_email.strip().lower(),
    ]
    if any("[bot]" in p for p in parts):
        return True
    if any(p.endswith("bot") for p in parts if p):
        return True
    if any("bot@users.noreply.github.com" in p for p in parts):
        return True
    return False


def parse_commits(raw: str) -> List[Commit]:
    commits: List[Commit] = []
    for line in raw.splitlines():
        # sha\tdate\tname\temail
        parts = line.split("\t")
        if len(parts) != 4:
            continue
        sha, date_s, name, email = parts
        try:
            datetime.strptime(date_s, "%Y-%m-%d")
        except ValueError:
            continue
        commits.append(Commit(sha=sha, date=date_s, author_name=name, author_email=email))
    return commits


def collect_commits(repo_dir: Path, revspec: str) -> List[Commit]:
    out = run_git(
        [
            "log",
            revspec,
            "--date=short",
            "--pretty=format:%H%x09%ad%x09%an%x09%ae",
        ],
        repo_dir,
    )
    return parse_commits(out)


def select_main_ref(repo_dir: Path) -> str:
    refs = run_git(["branch", "-r"], repo_dir)
    if "origin/main" in refs:
        return "origin/main"
    if "origin/master" in refs:
        return "origin/master"
    # Last fallback: current HEAD
    return "HEAD"


def classify_commits(
    commits: Iterable[Commit],
    org_members: Set[str],
    owner: str,
    repo: str,
    token: Optional[str],
    identity_cache: IdentityCache,
) -> Dict[str, Classification]:
    """Return mapping sha -> classification result."""
    headers = build_headers(token)
    result: Dict[str, Classification] = {}

    for c in commits:
        login: Optional[str] = None
        is_bot = False

        # Drop obvious bot commits immediately.
        if looks_like_bot(None, c.author_name, c.author_email):
            info = Classification(is_external=False, is_bot=True, login=None)
            result[c.sha] = info
            _cache_identity(
                identity_cache,
                info,
                author_name=c.author_name,
                author_email=c.author_email,
                login=None,
            )
            continue

        guessed = infer_login_from_email(c.author_email)
        if guessed:
            login = guessed

        cached = _get_cached_identity(
            identity_cache,
            author_name=c.author_name,
            author_email=c.author_email,
            login=login,
        )
        if cached is not None:
            result[c.sha] = cached
            continue

        if login is None and c.author_name:
            normalized_name = c.author_name.strip().lower()
            if normalized_name in org_members:
                login = normalized_name

        # Unresolved identity must be checked via API.
        if login is None:
            login, api_is_bot = fetch_commit_identity(owner, repo, c.sha, token, headers)
            is_bot = is_bot or api_is_bot

        if looks_like_bot(login, c.author_name, c.author_email):
            is_bot = True

        if login is not None:
            info = Classification(
                is_external=login.lower() not in org_members,
                is_bot=is_bot,
                login=login,
            )
            result[c.sha] = info
            _cache_identity(
                identity_cache,
                info,
                author_name=c.author_name,
                author_email=c.author_email,
                login=login,
            )
        else:
            # API checked but still no login (for example deleted account). This is
            # treated as external and still participates unless marked as bot.
            info = Classification(
                is_external=True,
                is_bot=is_bot,
                login=None,
            )
            result[c.sha] = info
            _cache_identity(
                identity_cache,
                info,
                author_name=c.author_name,
                author_email=c.author_email,
                login=None,
            )

    return result


def filter_non_bot_commits(
    commits: Iterable[Commit],
    class_map: Dict[str, Classification],
) -> List[Commit]:
    return [c for c in commits if not class_map.get(c.sha, Classification(True, False, None)).is_bot]


def monthly_stats(
    commits: Iterable[Commit],
    class_map: Dict[str, Classification],
) -> List[StatRow]:
    bucket: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "external": 0})

    for c in commits:
        info = class_map.get(c.sha)
        if info and info.is_bot:
            continue

        month = c.date[:7]
        bucket[month]["total"] += 1
        if info is None or info.is_external:
            bucket[month]["external"] += 1

    rows: List[StatRow] = []
    for month in sorted(bucket.keys()):
        total = bucket[month]["total"]
        external = bucket[month]["external"]
        rows.append(StatRow(month=month, total=total, external=external, internal=total - external))

    return rows


def monthly_email_sets(
    commits: Iterable[Commit],
    class_map: Dict[str, Classification],
) -> Dict[str, Dict[str, Set[str]]]:
    by_month: Dict[str, Dict[str, Set[str]]] = defaultdict(
        lambda: {"internal": set(), "external": set()}
    )

    for c in commits:
        info = class_map.get(c.sha)
        if info and info.is_bot:
            continue

        month = c.date[:7]
        email = c.author_email.strip().lower()
        if not email:
            continue

        is_external = True if info is None else info.is_external
        if is_external:
            by_month[month]["external"].add(email)
        else:
            by_month[month]["internal"].add(email)

    return dict(by_month)


def print_monthly_email_sets(title: str, data: Dict[str, Dict[str, Set[str]]]) -> None:
    print(f"\n[{title} - Monthly Email Sets]")
    for month in sorted(data.keys()):
        internal_emails = sorted(data[month]["internal"])
        external_emails = sorted(data[month]["external"])
        print(
            f"{month} | internal({len(internal_emails)}): {json.dumps(internal_emails, ensure_ascii=False)}"
        )
        print(
            f"{month} | external({len(external_emails)}): {json.dumps(external_emails, ensure_ascii=False)}"
        )


def list_files_at_ref(repo_dir: Path, ref: str) -> List[str]:
    # Use git grep -I to keep text files only; binary files are excluded.
    out = run_git(["grep", "-I", "--name-only", "-e", ".", ref, "--"], repo_dir)
    files: List[str] = []
    prefix = f"{ref}:"
    for raw in out.splitlines():
        line = raw.strip()
        if not line:
            continue
        # When searching in a specific ref, git grep may output "<ref>:<path>".
        if line.startswith(prefix):
            line = line[len(prefix):]
        files.append(line)
    # Deduplicate while preserving order.
    seen: Set[str] = set()
    uniq: List[str] = []
    for f in files:
        if f in seen:
            continue
        seen.add(f)
        uniq.append(f)
    return uniq


def ensure_commit_classification(
    sha: str,
    class_map: Dict[str, Classification],
    identity_cache: IdentityCache,
    org_members: Set[str],
    owner: str,
    repo: str,
    token: Optional[str],
    author_name: str,
    author_email: str,
) -> Classification:
    existing = class_map.get(sha)
    if existing is not None:
        return existing

    if not author_name:
        author_name = "unknown"
    if not author_email:
        author_email = "unknown"

    if looks_like_bot(None, author_name, author_email):
        info = Classification(is_external=False, is_bot=True, login=None)
        class_map[sha] = info
        _cache_identity(
            identity_cache,
            info,
            author_name=author_name,
            author_email=author_email,
            login=None,
        )
        return info

    guessed = infer_login_from_email(author_email)
    cached = _get_cached_identity(
        identity_cache,
        author_name=author_name,
        author_email=author_email,
        login=guessed,
    )
    if cached is not None:
        class_map[sha] = cached
        return cached

    if guessed is None and author_name:
        n = author_name.strip().lower()
        if n in org_members:
            guessed = n

    if guessed is None:
        login, api_is_bot = fetch_commit_identity(owner, repo, sha, token)
        if api_is_bot:
            info = Classification(is_external=False, is_bot=True, login=login)
            class_map[sha] = info
            return info
        guessed = login

    if guessed is None:
        info = Classification(is_external=True, is_bot=False, login=None)
    else:
        info = Classification(
            is_external=guessed.lower() not in org_members,
            is_bot=looks_like_bot(guessed, author_name, author_email),
            login=guessed,
        )
    class_map[sha] = info
    _cache_identity(
        identity_cache,
        info,
        author_name=author_name,
        author_email=author_email,
        login=guessed,
    )
    return info


def write_file_internal_ratio_csv(rows: Iterable[FileRatioRow], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "total_lines", "internal_lines", "external_lines", "internal_ratio"])
        for r in rows:
            writer.writerow(
                [
                    r.file_path,
                    r.total_lines,
                    r.internal_lines,
                    r.external_lines,
                    f"{r.internal_ratio:.6f}",
                ]
            )


def generate_file_line_stats(
    repo_dir: Path,
    ref: str,
    stats_root: Path,
    class_map: Dict[str, Classification],
    identity_cache: IdentityCache,
    org_members: Set[str],
    owner: str,
    repo: str,
    token: Optional[str],
) -> List[FileRatioRow]:
    results: List[FileRatioRow] = []
    files = list_files_at_ref(repo_dir, ref)
    print(f"Generating per-file .stat outputs for {len(files)} files...")

    for file_path in files:
        blame_cmd = ["blame", "--line-porcelain", ref, "--", file_path]
        try:
            out = run_git(blame_cmd, repo_dir)
        except RuntimeError:
            # Skip binary or unblamable files.
            continue

        stat_file = stats_root / (file_path + ".stat")
        stat_file.parent.mkdir(parents=True, exist_ok=True)

        internal_lines = 0
        external_lines = 0
        total_lines = 0

        lines = out.splitlines()
        i = 0
        with stat_file.open("w", encoding="utf-8") as sf:
            while i < len(lines):
                first = lines[i]
                if not first:
                    i += 1
                    continue

                m = re.match(r"^([0-9a-f]{40})\s+\d+\s+\d+(?:\s+\d+)?$", first)
                if not m:
                    i += 1
                    continue

                sha = m.group(1)
                i += 1

                author_name = "unknown"
                author_mail = "unknown"
                line_text = ""

                while i < len(lines):
                    row = lines[i]
                    i += 1
                    if row.startswith("author "):
                        author_name = row[7:].strip() or "unknown"
                    elif row.startswith("author-mail "):
                        author_mail = row[12:].strip().strip("<>") or "unknown"
                    elif row.startswith("\t"):
                        line_text = row[1:]
                        break

                info = ensure_commit_classification(
                    sha=sha,
                    class_map=class_map,
                    identity_cache=identity_cache,
                    org_members=org_members,
                    owner=owner,
                    repo=repo,
                    token=token,
                    author_name=author_name,
                    author_email=author_mail,
                )

                username = info.login or infer_login_from_email(author_mail) or author_name.strip() or "unknown"

                # Each line-porcelain record represents one final file line.
                if info.is_bot:
                    label = "bot"
                elif info.is_external:
                    label = "external"
                    external_lines += 1
                    total_lines += 1
                else:
                    label = "internal"
                    internal_lines += 1
                    total_lines += 1

                sf.write(f"[{label}][{username}][{author_mail}]{line_text}\n")

        results.append(
            FileRatioRow(
                file_path=file_path,
                total_lines=total_lines,
                internal_lines=internal_lines,
                external_lines=external_lines,
            )
        )

    results.sort(key=lambda r: (-r.internal_ratio, -r.internal_lines, r.file_path))
    return results


def print_file_internal_ratio_top(rows: Iterable[FileRatioRow], limit: int = 50) -> None:
    items = list(rows)
    print("\n[File Internal Ratio Ranking]")
    for idx, r in enumerate(items[:limit], start=1):
        print(
            f"{idx}. {r.file_path} | internal_ratio={r.internal_ratio:.2%} "
            f"(internal={r.internal_lines}, external={r.external_lines}, total={r.total_lines})"
        )


def write_ratio_line_chart(
    main_rows: Iterable[StatRow],
    all_rows: Iterable[StatRow],
    output_file: Path,
) -> None:
    main_map = {r.month: r.external_ratio for r in main_rows}
    all_map = {r.month: r.external_ratio for r in all_rows}
    months = sorted(set(main_map.keys()) | set(all_map.keys()))

    if not months:
        return

    y_main = [main_map.get(m) for m in months]
    y_all = [all_map.get(m) for m in months]

    output_file.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 5), dpi=140)
    plt.plot(months, y_main, marker="o", linewidth=1.8, label="Main Branch")
    plt.plot(months, y_all, marker="s", linewidth=1.8, label="Whole Repo")
    plt.title("LSPosed External Contribution Ratio Trend")
    plt.xlabel("Month")
    plt.ylabel("External Ratio")
    plt.ylim(0, 1)
    plt.grid(alpha=0.3, linestyle="--")
    plt.legend()
    step = max(1, len(months) // 12)
    ticks = list(range(0, len(months), step))
    plt.xticks(ticks=ticks, labels=[months[i] for i in ticks], rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def summary(rows: Iterable[StatRow]) -> Dict[str, object]:
    total = 0
    external = 0
    min_month = None
    max_month = None

    for r in rows:
        total += r.total
        external += r.external
        if min_month is None or r.month < min_month:
            min_month = r.month
        if max_month is None or r.month > max_month:
            max_month = r.month

    internal = total - external
    ratio = (external / total) if total else 0.0

    return {
        "period_start": min_month,
        "period_end": max_month,
        "total_commits": total,
        "external_commits": external,
        "internal_commits": internal,
        "external_ratio": ratio,
    }


def write_monthly_csv(rows: Iterable[StatRow], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["month", "total_commits", "external_commits", "internal_commits", "external_ratio"])
        for r in rows:
            writer.writerow([r.month, r.total, r.external, r.internal, f"{r.external_ratio:.6f}"])


def write_summary_json(data: Dict[str, object], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def print_summary_block(title: str, data: Dict[str, object]) -> None:
    print(f"\n[{title}]")
    print(f"period: {data.get('period_start')} -> {data.get('period_end')}")
    print(f"total commits: {data.get('total_commits')}")
    print(f"external commits: {data.get('external_commits')}")
    print(f"internal commits: {data.get('internal_commits')}")
    print(f"external ratio: {float(data.get('external_ratio', 0.0)):.2%}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Track external contribution ratio changes for LSPosed repo, "
            "including main-branch and whole-repo stats."
        )
    )
    p.add_argument("--repo-url", default=DEFAULT_REPO_URL, help="Git repository URL")
    p.add_argument("--owner", default=DEFAULT_OWNER, help="GitHub repository owner")
    p.add_argument("--repo", default=DEFAULT_REPO, help="GitHub repository name")
    p.add_argument("--org", default=DEFAULT_ORG, help="GitHub org used to define internal contributors")
    p.add_argument(
        "--cache-dir",
        default=".cache/lsposed_repo",
        help="Directory used to clone/fetch repository cache",
    )
    p.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for csv/json reports",
    )
    p.add_argument(
        "--github-token",
        default=os.getenv("GITHUB_TOKEN"),
        help="GitHub token (or use env GITHUB_TOKEN)",
    )
    p.add_argument(
        "--file-line-stats-ref",
        default="",
        help="Git ref used for per-file .stat generation (default: detected main ref)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_dir = Path(args.cache_dir).resolve()
    out_dir = Path(args.output_dir).resolve()

    print("Preparing local repository cache...")
    ensure_repo(args.repo_url, repo_dir)

    print("Fetching org members...")
    org_members = fetch_org_members(args.org, args.github_token)
    print(f"Public members in org '{args.org}': {len(org_members)}")

    print("Collecting commits from main branch and all branches...")
    main_ref = select_main_ref(repo_dir)
    commits_main = collect_commits(repo_dir, main_ref)
    commits_all = collect_commits(repo_dir, "--all")

    # Deduplicate all-branch commits by SHA (git log --all can still be unique already,
    # but this keeps behavior explicit and stable).
    uniq_all: Dict[str, Commit] = {c.sha: c for c in commits_all}
    commits_all = list(uniq_all.values())

    print(f"Main scope commits ({main_ref}): {len(commits_main)}")
    print(f"Whole-repo commits (--all): {len(commits_all)}")

    all_for_classification = {c.sha: c for c in commits_all}
    for c in commits_main:
        all_for_classification[c.sha] = c
    identity_cache = new_identity_cache()

    print("Classifying commit authors as internal/external...")
    external_map = classify_commits(
        all_for_classification.values(),
        org_members=org_members,
        owner=args.owner,
        repo=args.repo,
        token=args.github_token,
        identity_cache=identity_cache,
    )

    non_bot_main = filter_non_bot_commits(commits_main, external_map)
    non_bot_all = filter_non_bot_commits(commits_all, external_map)
    print(f"Main non-bot commits: {len(non_bot_main)}")
    print(f"Whole-repo non-bot commits: {len(non_bot_all)}")

    monthly_main = monthly_stats(non_bot_main, external_map)
    monthly_all = monthly_stats(non_bot_all, external_map)
    email_sets_main = monthly_email_sets(non_bot_main, external_map)
    email_sets_all = monthly_email_sets(non_bot_all, external_map)

    summary_main = summary(monthly_main)
    summary_all = summary(monthly_all)

    write_monthly_csv(monthly_main, out_dir / "main_branch_monthly.csv")
    write_monthly_csv(monthly_all, out_dir / "whole_repo_monthly.csv")

    write_summary_json(
        {
            "scope": "main_branch",
            "ref": main_ref,
            "exclude_bots": True,
            **summary_main,
        },
        out_dir / "main_branch_summary.json",
    )
    write_summary_json(
        {
            "scope": "whole_repo",
            "ref": "--all",
            "exclude_bots": True,
            **summary_all,
        },
        out_dir / "whole_repo_summary.json",
    )

    write_ratio_line_chart(monthly_main, monthly_all, out_dir / "external_ratio_trend.png")

    line_stats_ref = args.file_line_stats_ref.strip() or main_ref
    file_ratio_rows = generate_file_line_stats(
        repo_dir=repo_dir,
        ref=line_stats_ref,
        stats_root=out_dir / "stats",
        class_map=external_map,
        identity_cache=identity_cache,
        org_members=org_members,
        owner=args.owner,
        repo=args.repo,
        token=args.github_token,
    )
    write_file_internal_ratio_csv(file_ratio_rows, out_dir / "file_internal_ratio_ranking.csv")

    print_summary_block(f"Main branch ({main_ref})", summary_main)
    print_summary_block("Whole repo (--all)", summary_all)
    print_monthly_email_sets(f"Main branch ({main_ref})", email_sets_main)
    print_monthly_email_sets("Whole repo (--all)", email_sets_all)
    print_file_internal_ratio_top(file_ratio_rows)

    print("\nOutputs:")
    print(f"- {out_dir / 'main_branch_monthly.csv'}")
    print(f"- {out_dir / 'whole_repo_monthly.csv'}")
    print(f"- {out_dir / 'main_branch_summary.json'}")
    print(f"- {out_dir / 'whole_repo_summary.json'}")
    print(f"- {out_dir / 'external_ratio_trend.png'}")
    print(f"- {out_dir / 'file_internal_ratio_ranking.csv'}")
    print(f"- {out_dir / 'stats'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
