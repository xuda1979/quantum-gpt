#!/usr/bin/env python3
"""Fetch latest quantum SDK documentation into a local Markdown corpus.

The crawler intentionally uses only Python's standard library so it can run
before the rest of the local RAG dependencies are installed. It follows links
only within each source's configured documentation prefixes.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = ROOT / "configs" / "quantum_doc_sources.json"
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "external" / "quantum-sdk-docs-latest"
DEFAULT_MANIFEST = ROOT / "artifacts" / "quantum-rag" / "qwen36-docs-fetch-manifest.json"

USER_AGENT = "quantum-gpt-qwen36-rag-doc-fetcher/1.0 (+local RAG corpus builder)"

BLOCK_TAGS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "br",
    "dd",
    "div",
    "dl",
    "dt",
    "figcaption",
    "footer",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "li",
    "main",
    "nav",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "td",
    "th",
    "tr",
    "ul",
}

SKIP_TAGS = {"script", "style", "svg", "canvas", "noscript"}

STATIC_PATH_SEGMENTS = {
    "_images",
    "_static",
    "assets",
    "css",
    "fonts",
    "images",
    "img",
    "js",
    "static",
}

STATIC_EXTENSIONS = {
    ".css",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".js",
    ".map",
    ".pdf",
    ".png",
    ".svg",
    ".ttf",
    ".webp",
    ".woff",
    ".woff2",
    ".zip",
}


@dataclass(frozen=True)
class DocSource:
    source_id: str
    name: str
    seeds: tuple[str, ...]
    allowed_prefixes: tuple[str, ...]


@dataclass(frozen=True)
class FetchedPage:
    source: DocSource
    url: str
    title: str
    text: str
    links: tuple[str, ...]
    content_type: str
    fetched_at: str


class TextAndLinkExtractor(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.parts: list[str] = []
        self.links: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in BLOCK_TAGS:
            self.parts.append("\n")
        for key, value in attrs:
            if key.lower() != "href" or not value:
                continue
            self.links.append(urllib.parse.urljoin(self.base_url, value))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        stripped = data.strip()
        if stripped:
            self.parts.append(stripped)
            self.parts.append(" ")

    def text(self) -> str:
        joined = "".join(self.parts)
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in joined.splitlines()]
        compact_lines: list[str] = []
        previous_blank = False
        for line in lines:
            if not line:
                if not previous_blank:
                    compact_lines.append("")
                previous_blank = True
                continue
            compact_lines.append(html.unescape(line))
            previous_blank = False
        return "\n".join(compact_lines).strip()


def canonicalize_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    if scheme in {"http", "https"} and path != "/" and path.endswith("/index.html"):
        path = path[: -len("index.html")]
    query = ""
    return urllib.parse.urlunsplit((scheme, netloc, path, query, ""))


def is_static_asset_url(url: str) -> bool:
    parsed = urllib.parse.urlsplit(url)
    path = parsed.path.lower()
    parts = {part for part in path.split("/") if part}
    if parts & STATIC_PATH_SEGMENTS:
        return True
    return any(path.endswith(extension) for extension in STATIC_EXTENSIONS)


def is_allowed_url(url: str, source: DocSource) -> bool:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https", "file"}:
        return False
    canonical = canonicalize_url(url)
    if is_static_asset_url(canonical):
        return False
    return any(canonical.startswith(prefix) for prefix in source.allowed_prefixes)


def safe_slug(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    raw = (parsed.netloc + parsed.path).strip("/") or "index"
    raw = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-")
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    return f"{raw[:90] or 'page'}-{digest}"


def extract_title(raw_html: str, fallback: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", raw_html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return fallback
    title = re.sub(r"\s+", " ", html.unescape(match.group(1))).strip()
    return title or fallback


def decode_body(body: bytes, content_type: str) -> str:
    charset = "utf-8"
    match = re.search(r"charset=([A-Za-z0-9._-]+)", content_type, flags=re.IGNORECASE)
    if match:
        charset = match.group(1)
    return body.decode(charset, errors="replace")


def fetch_page(url: str, source: DocSource, *, timeout: float) -> FetchedPage:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
        content_type = response.headers.get("content-type", "")

    fetched_at = dt.datetime.now(dt.timezone.utc).isoformat()
    lowered_type = content_type.lower()
    if "text/html" in lowered_type or url.endswith(("/", ".html", ".htm")):
        raw_html = decode_body(body, content_type)
        title = extract_title(raw_html, fallback=url)
        extractor = TextAndLinkExtractor(url)
        extractor.feed(raw_html)
        links = tuple(
            dict.fromkeys(
                canonicalize_url(link) for link in extractor.links if is_allowed_url(link, source)
            )
        )
        return FetchedPage(
            source=source,
            url=canonicalize_url(url),
            title=title,
            text=extractor.text(),
            links=links,
            content_type=content_type,
            fetched_at=fetched_at,
        )

    if (
        url.endswith((".md", ".txt", ".rst"))
        or "text/plain" in lowered_type
        or "text/markdown" in lowered_type
    ):
        text = decode_body(body, content_type).strip()
        return FetchedPage(
            source=source,
            url=canonicalize_url(url),
            title=url.rsplit("/", 1)[-1] or url,
            text=text,
            links=(),
            content_type=content_type,
            fetched_at=fetched_at,
        )

    raise ValueError(f"unsupported content type: {content_type or 'unknown'}")


def write_page(page: FetchedPage, output_dir: Path) -> Path:
    source_dir = output_dir / page.source.source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    path = source_dir / f"{safe_slug(page.url)}.md"
    body = "\n".join(
        [
            f"# {page.title}",
            "",
            f"Source: {page.url}",
            f"Documentation set: {page.source.name}",
            f"Fetched at: {page.fetched_at}",
            "",
            page.text,
            "",
        ]
    )
    path.write_text(body, encoding="utf-8")
    return path


def load_sources(path: Path) -> list[DocSource]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    sources: list[DocSource] = []
    for item in payload.get("sources", []):
        sources.append(
            DocSource(
                source_id=str(item["id"]),
                name=str(item["name"]),
                seeds=tuple(canonicalize_url(str(url)) for url in item.get("seeds", [])),
                allowed_prefixes=tuple(
                    canonicalize_url(str(url)) for url in item.get("allowed_prefixes", [])
                ),
            )
        )
    return sources


def crawl_source(
    source: DocSource,
    *,
    output_dir: Path,
    max_pages: int,
    max_depth: int,
    timeout: float,
    sleep_seconds: float,
    dry_run: bool = False,
) -> dict[str, object]:
    queue: deque[tuple[str, int]] = deque((seed, 0) for seed in source.seeds)
    seen: set[str] = set()
    written: list[str] = []
    errors: list[dict[str, str]] = []

    while queue:
        if max_pages > 0 and len(written) >= max_pages:
            break
        url, depth = queue.popleft()
        url = canonicalize_url(url)
        if url in seen or not is_allowed_url(url, source):
            continue
        seen.add(url)

        if dry_run:
            written.append(url)
            continue

        try:
            page = fetch_page(url, source, timeout=timeout)
        except (urllib.error.URLError, TimeoutError, ValueError, UnicodeError) as exc:
            errors.append({"url": url, "error": str(exc)})
            continue

        if page.text:
            path = write_page(page, output_dir)
            written.append(path.as_posix())

        if depth < max_depth:
            for link in page.links:
                if link not in seen:
                    queue.append((link, depth + 1))

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    return {
        "id": source.source_id,
        "name": source.name,
        "seed_count": len(source.seeds),
        "seen_count": len(seen),
        "written_count": len(written),
        "written": written,
        "errors": errors,
    }


def select_sources(sources: Iterable[DocSource], selected_ids: list[str]) -> list[DocSource]:
    if not selected_ids:
        return list(sources)
    selected = set(selected_ids)
    return [source for source in sources if source.source_id in selected]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--source", action="append", default=[], help="Source id to crawl; repeatable."
    )
    parser.add_argument(
        "--max-pages-per-source", type=int, default=0, help="0 means no explicit page cap."
    )
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--sleep-seconds", type=float, default=0.15)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sources = select_sources(load_sources(args.sources), args.source)
    if not sources:
        raise SystemExit("No documentation sources selected.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = [
        crawl_source(
            source,
            output_dir=args.output_dir,
            max_pages=args.max_pages_per_source,
            max_depth=args.max_depth,
            timeout=args.timeout,
            sleep_seconds=args.sleep_seconds,
            dry_run=args.dry_run,
        )
        for source in sources
    ]
    summary = {
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "sources_path": args.sources.as_posix(),
        "output_dir": args.output_dir.as_posix(),
        "source_count": len(results),
        "total_written": sum(int(item["written_count"]) for item in results),
        "results": results,
    }
    args.manifest_json.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
