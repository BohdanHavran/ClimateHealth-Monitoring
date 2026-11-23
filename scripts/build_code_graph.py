"""Optional installed Graphify AST-only analysis; never reads datasets or secrets."""
from pathlib import Path
import json

from graphify.extract import extract
from graphify.build import build_from_json
from graphify.cluster import cluster
from graphify.export import to_json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/graphify"
OUT.mkdir(parents=True, exist_ok=True)
files = sorted(ROOT.glob("*.py")) + sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "tests").glob("*.py"))
files += sorted((ROOT / "climate_health").glob("*.py")) + sorted((ROOT / "ml_service").glob("*.py"))
data = extract(files, cache_root=OUT / ".cache", root=ROOT, parallel=False)
graph = build_from_json(data, directed=True, root=ROOT)
communities = cluster(graph)
to_json(graph, communities, str(OUT / "graph.json"), force=True)
summary = {"mode": "AST-only, no semantic LLM extraction", "files": [str(p.relative_to(ROOT)) for p in files],
           "nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(), "communities": len(communities),
           "limitations": "Templates, SQL, runtime wiring, external services and data provenance require manual analysis. Missing edges do not prove independence."}
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k != "files"}))
