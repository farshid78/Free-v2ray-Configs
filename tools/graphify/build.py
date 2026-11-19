#!/usr/bin/env python3
"""Rebuild graphify-out/graph.html with this project's UI overlay.

graphify's HTML export ships a search box that only fills a dropdown and a
community legend whose click handler can never solo a community.  Patching the
installed package is not durable: a reinstall, an upgrade or a fresh clone
reverts it silently.  So this tool renders the page with the *unmodified*
package and injects ui.css + ui.js before </body>.  Reinstalling graphify cannot
break the page -- run this tool and the fixed page is regenerated.

    python -X utf8 tools/graphify/build.py

The tool continues inside .cache/gv and creates that virtualenv with the pinned
graphify when it is missing.  The page is drawn from graphify-out/graph.json,
the artifact GRAPH_REPORT.md and obsidian/ also describe, so a rebuild after a
cache wipe or a graphify upgrade cannot change the counts it shows.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT_DIR = ROOT / "graphify-out"
CACHE = ROOT / ".cache"
VENV = CACHE / "gv"
PIN = "graphifyy==0.1.14"
MARKER = "<!-- graphify overlay: tools/graphify/build.py -->"
REEXEC_ENV = "GRAPHIFY_OVERLAY_REEXEC"


def _rel(path: Path) -> str:
    return os.path.relpath(path, ROOT)


def _run(argv: list[str]) -> None:
    if subprocess.run(argv, cwd=ROOT).returncode:
        raise SystemExit(f"command failed: {' '.join(argv)}")


def _venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _bootstrap(venv: Path) -> Path:
    """Create the venv and install the pinned graphify when they are missing."""
    python = _venv_python(venv)
    if not python.exists():
        print(f"[overlay] creating {_rel(venv)} ...", flush=True)
        _run([sys.executable, "-m", "venv", str(venv)])
    probe = subprocess.run([str(python), "-c", "import graphify.export"],
                           capture_output=True, cwd=ROOT)
    if probe.returncode:
        print(f"[overlay] installing {PIN} ...", flush=True)
        _run([str(python), "-m", "pip", "install",
              "--disable-pip-version-check", PIN])
    return python


def _delegate(venv: Path) -> None:
    """Continue in the interpreter that owns graphify and its dependencies."""
    python = _bootstrap(venv)
    if Path(sys.prefix).resolve() == venv.resolve():
        return
    if os.environ.get(REEXEC_ENV):
        raise SystemExit(f"cannot switch to {_rel(python)}; invoke it directly: "
                         f"{python} {_rel(Path(__file__).resolve())}")
    print(f"[overlay] switching to {_rel(python)}", flush=True)
    child = subprocess.run([str(python), str(Path(__file__).resolve()), *sys.argv[1:]],
                           cwd=ROOT, env=dict(os.environ, **{REEXEC_ENV: "1"}))
    raise SystemExit(child.returncode)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _communities_from_nodes(graph: Any) -> dict[int, list[str]]:
    groups: dict[int, list[str]] = {}
    for node_id, attrs in graph.nodes(data=True):
        groups.setdefault(int(attrs.get("community", 0)), []).append(node_id)
    return groups


def _labels() -> dict[int, str]:
    """Community labels live in the repo; graphify only keeps them in its cache."""
    artifact = OUT_DIR / "community-labels.json"
    cached = CACHE / "gv_labels.json"
    source = artifact if artifact.exists() else cached
    if not source.exists():
        return {}
    labels = {int(cid): str(text) for cid, text in _read_json(source).items()}
    if source is cached:
        artifact.write_text(
            json.dumps(labels, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return labels


def _graph() -> tuple[Any, dict[int, list[str]], dict[int, str]]:
    """Return (graph, {community: [node ids]}, {community: label}).

    Built from graphify-out/graph.json alone: the cached extraction depends on
    which graphify build is installed (the PyPI release still keeps isolated
    code nodes that upstream's HEAD prunes), and the page must keep describing
    the same graph as GRAPH_REPORT.md and obsidian/.
    """
    import networkx as nx

    payload = _read_json(OUT_DIR / "graph.json")
    graph = nx.Graph()
    for node in payload["nodes"]:
        graph.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
    for link in payload.get("links", []):
        attrs = {k: v for k, v in link.items() if k not in ("source", "target")}
        if link["source"] in graph and link["target"] in graph:
            graph.add_edge(link["source"], link["target"], **attrs)
    graph.graph["hyperedges"] = payload.get("hyperedges", [])
    return graph, _communities_from_nodes(graph), _labels()


def _render(out_path: Path) -> tuple[int, int, int]:
    from graphify.export import to_html
    graph, communities, labels = _graph()
    to_html(graph, communities, str(out_path), labels)
    return graph.number_of_nodes(), graph.number_of_edges(), len(communities)


def _inject(out_path: Path) -> None:
    html = out_path.read_text(encoding="utf-8")
    if MARKER in html:
        return
    if html.count("</body>") != 1:
        raise SystemExit(f"{_rel(out_path)} has no single </body>; refusing to inject")
    css = (HERE / "ui.css").read_text(encoding="utf-8").strip()
    js = (HERE / "ui.js").read_text(encoding="utf-8").strip()
    block = f"{MARKER}\n<style>\n{css}\n</style>\n<script>\n{js}\n</script>\n</body>"
    out_path.write_text(html.replace("</body>", block, 1), encoding="utf-8")


def _embedded(html: str, name: str) -> list:
    """Read one of graphify's inline `const NAME = [...]` arrays back as JSON."""
    prefix = f"const {name} = "
    start = html.index(prefix) + len(prefix)
    value, _ = json.JSONDecoder().raw_decode(html, start)
    return value


def _verify(out_path: Path, nodes: int, edges: int, communities: int) -> None:
    html = out_path.read_text(encoding="utf-8")
    problems = []
    if MARKER not in html:
        problems.append("overlay block missing")
    if "function applyVisibility" not in html:
        problems.append("ui.js not injected")
    for name, expected in (("RAW_NODES", nodes), ("RAW_EDGES", edges),
                           ("LEGEND", communities)):
        try:
            got = len(_embedded(html, name))
        except ValueError:
            problems.append(f"{name} unreadable")
            continue
        if got != expected:
            problems.append(f"{name} has {got} rows, expected {expected}")
    if problems:
        raise SystemExit("generated page is inconsistent: " + "; ".join(problems))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--venv", default=str(VENV),
                        help="virtualenv that owns graphify (default: .cache/gv)")
    parser.add_argument("--out", default=str(OUT_DIR / "graph.html"),
                        help="page to write (default: graphify-out/graph.html)")
    parser.add_argument("--no-venv", action="store_true",
                        help="render with the running interpreter instead")
    args = parser.parse_args()

    venv = Path(args.venv).expanduser()
    venv = (venv if venv.is_absolute() else ROOT / venv).resolve()
    if not args.no_venv:
        _delegate(venv)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nodes, edges, communities = _render(out_path)
    _inject(out_path)
    _verify(out_path, nodes, edges, communities)
    print(f"[overlay] {_rel(out_path)}: {nodes} nodes, {edges} edges, "
          f"{communities} communities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
