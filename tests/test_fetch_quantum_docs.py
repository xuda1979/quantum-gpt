from __future__ import annotations

import json
from pathlib import Path

from scripts.fetch_quantum_docs import crawl_source, load_sources


def test_fetch_quantum_docs_crawls_allowed_file_links(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    page1 = site / "index.html"
    page2 = site / "install.html"
    page1.write_text(
        "<html><head><title>Root</title></head><body>"
        "<main><h1>Quantum SDK</h1><a href='install.html'>Install</a></main>"
        "<script>ignore_me()</script></body></html>",
        encoding="utf-8",
    )
    page2.write_text(
        "<html><head><title>Install</title></head><body>"
        "<p>Use the local CPU simulator for smoke tests.</p>"
        "</body></html>",
        encoding="utf-8",
    )

    manifest = tmp_path / "sources.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "id": "local-docs",
                        "name": "Local docs",
                        "seeds": [page1.as_uri()],
                        "allowed_prefixes": [site.as_uri()],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    source = load_sources(manifest)[0]
    result = crawl_source(
        source,
        output_dir=tmp_path / "out",
        max_pages=10,
        max_depth=2,
        timeout=5,
        sleep_seconds=0,
    )

    assert result["written_count"] == 2
    written = sorted((tmp_path / "out" / "local-docs").glob("*.md"))
    assert len(written) == 2
    combined = "\n".join(path.read_text(encoding="utf-8") for path in written)
    assert "Quantum SDK" in combined
    assert "local CPU simulator" in combined
    assert "ignore_me" not in combined
