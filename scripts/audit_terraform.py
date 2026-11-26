"""Offline, source-located HCL subset analysis; NOT Terraform parsing or planning.

Recognizes balanced blocks/attributes, traversals and template interpolations.
Never imports an AWS SDK, invokes Terraform or reads tfvars/state/credentials.
"""
import argparse
import copy
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "infrastructure/terraform"


def tokens(text):
    result = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        if text.startswith(("//", "#"), i):
            j = text.find("\n", i)
            i = len(text) if j < 0 else j + 1
            continue
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            if j < 0:
                raise ValueError("Unclosed comment")
            i = j + 2
            continue
        h = re.match(r"<<-?([A-Za-z_][A-Za-z0-9_]*)[^\n]*\n", text[i:])
        if h:
            tail = i + h.end()
            end = re.search(r"(?m)^\s*" + re.escape(h[1]) + r"\s*$", text[tail:])
            if not end:
                raise ValueError("Unclosed heredoc")
            j = tail + end.end()
            result.append(("template", text[i:j], i, j))
            i = j
            continue
        if text[i] == '"':
            j = i + 1
            while j < len(text):
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == '"':
                    break
                j += 1
            if j >= len(text):
                raise ValueError("Unclosed string")
            result.append(("string", text[i:j + 1], i, j + 1))
            i = j + 1
            continue
        op = re.match(r"==|!=|>=|<=|&&|\|\||=>|\.\.\.", text[i:])
        if op:
            j = i + len(op[0])
            result.append(("symbol", op[0], i, j))
            i = j
            continue
        m = re.match(r"[A-Za-z_][A-Za-z0-9_-]*", text[i:])
        j = i + (len(m[0]) if m else 1)
        result.append(("identifier" if m else "symbol", text[i:j], i, j))
        i = j
    return result


def close_index(ts, start):
    opening = ts[start][1]
    closing = {"{": "}", "[": "]", "(": ")"}[opening]
    depth = 1
    for i in range(start + 1, len(ts)):
        if ts[i][0] in ("string", "template"):
            continue
        if ts[i][1] == opening:
            depth += 1
        elif ts[i][1] == closing:
            depth -= 1
            if not depth:
                return i
    raise ValueError("Unclosed delimiter")


def attributes(text, ts, start, end):
    """Return only direct attributes; nested blocks stay in the raw body."""
    attrs = {}
    i = start
    while i < end:
        if ts[i][0] == "identifier" and i + 1 < end and ts[i + 1][1] == "=":
            name = ts[i][1]
            value_start = i + 2
            j = value_start
            while j < end:
                if ts[j][1] in ("{", "[", "(") and ts[j][0] == "symbol":
                    j = close_index(ts, j) + 1
                    continue
                if j > value_start and ts[j][0] == "identifier" and j + 1 < end and ts[j + 1][1] == "=":
                    break
                # A direct nested block starts on a new logical attribute boundary.
                if j > value_start and ts[j][0] == "identifier" and j + 1 < end and ts[j + 1][1] == "{":
                    break
                j += 1
            if j > value_start:
                attrs[name] = text[ts[value_start][2]:ts[j - 1][3]].strip().rstrip(",").strip()
            i = j
        elif ts[i][1] == "{" and ts[i][0] == "symbol":
            i = close_index(ts, i) + 1
        else:
            i += 1
    return attrs


def blocks(path, base=BASE):
    path, base = path.resolve(), base.resolve()
    text = path.read_text(encoding="utf8")
    ts = tokens(text)
    result = []
    i = 0
    while i < len(ts):
        if ts[i][0] != "identifier":
            raise ValueError(f"Unexpected top-level token {path}:{ts[i]}")
        kind = ts[i][1]
        labels = []
        j = i + 1
        while j < len(ts) and ts[j][1] != "{":
            if ts[j][0] == "string":
                labels.append(json.loads(ts[j][1]))
            j += 1
        end = close_index(ts, j)
        attrs = attributes(text, ts, j + 1, end)
        result.append({"kind": kind, "labels": labels, "attrs": attrs,
                       "body": text[ts[j][3]:ts[end][2]],
                       "file": path.relative_to(base).as_posix(),
                       "line": text.count("\n", 0, ts[i][2]) + 1,
                       "end_line": text.count("\n", 0, ts[end][3]) + 1})
        i = end + 1
    return result


def traversals(expression):
    ts = tokens(expression)
    refs = []
    for kind, value, _, _ in ts:
        if kind in ("string", "template"):
            for match in re.finditer(r"(?<!\$)\$\{(.*?)\}|%\{(.*?)\}", value, re.S):
                refs.extend(traversals(match[1] or match[2]))
    i = 0
    while i < len(ts):
        if ts[i][0] != "identifier":
            i += 1
            continue
        if i > 0 and ts[i - 1][1] == ".":
            i += 1
            continue
        parts = [ts[i][1]]
        j = i + 1
        while j < len(ts):
            if ts[j][1] == "[":
                j = close_index(ts, j) + 1
            elif ts[j][1] == "." and j + 1 < len(ts) and ts[j + 1][0] == "identifier":
                parts.append(ts[j + 1][1])
                j += 2
            else:
                break
        if len(parts) >= 2:
            refs.append(parts)
        i += 1  # Also inspect traversals inside index expressions.
    return refs


def build(base=BASE):
    all_blocks = [b for p in sorted(base.rglob("*.tf")) for b in blocks(p, base)]
    calls = {b["labels"][0]: b for b in all_blocks if b["kind"] == "module" and "/" not in b["file"]}
    scope_dirs = {"root": "."}
    for name, call in calls.items():
        scope_dirs["module." + name] = json.loads(call["attrs"]["source"]).removeprefix("./")
    directories = {v: k for k, v in scope_dirs.items()}
    nodes = {}
    edges = {}
    unresolved = []

    def node(scope, address, kind, block=None, **extra):
        key = scope + "::" + address
        item = {"id": key, "scope": scope, "address": address, "kind": kind, **extra}
        if block:
            item.update(file=block["file"], line=block["line"], end_line=block["end_line"])
        nodes[key] = item
        return key

    def edge(source, target, relation, evidence="", file=None, line=None):
        if source == target:
            return
        assert source in nodes and target in nodes, (source, target)
        key = (source, target, relation, evidence)
        edges[key] = {"source": source, "target": target, "relation": relation,
                      "evidence": evidence, "file": file, "line": line,
                      "confidence": "STATIC_SOURCE"}

    root_node = node("root", "directory", "module_scope")
    for scope in scope_dirs:
        if scope != "root":
            node(scope, "directory", "module_scope")
    for b in all_blocks:
        directory = Path(b["file"]).parent.as_posix()
        scope = directories[directory]
        b["scope"] = scope
        kind, labels = b["kind"], b["labels"]
        addresses = []
        if kind == "resource":
            addresses = [(".".join(labels), kind, b["attrs"])]
        elif kind == "data":
            addresses = [("data." + ".".join(labels), kind, b["attrs"])]
        elif kind in ("variable", "output", "module", "provider"):
            prefix = "var" if kind == "variable" else kind
            addresses = [(prefix + "." + labels[0], kind, b["attrs"])]
        elif kind == "locals":
            addresses = [("local." + k, "local", {"value": v}) for k, v in b["attrs"].items()]
        elif kind in ("terraform", "moved"):
            # A version requirement is metadata, not an AWS provider instance.
            b["ids"] = []
            continue
        else:
            raise ValueError("Unsupported block " + kind)
        b["ids"] = []
        for address, node_kind, attrs in addresses:
            nid = node(scope, address, node_kind, b, attrs=attrs)
            b["ids"].append(nid)
            edge(scope + "::directory", nid, "contains", "module scope")
    provider = "root::provider.aws"

    def resolve(scope, parts):
        head = parts[0]
        if head == "module":
            if len(parts) >= 3 and "module." + parts[1] in scope_dirs:
                return "module." + parts[1] + "::output." + parts[2]
            return scope + "::module." + parts[1]
        if head in ("var", "local", "output", "provider"):
            return scope + "::" + ".".join(parts[:2])
        if head == "data" and len(parts) >= 3:
            return scope + "::" + ".".join(parts[:3])
        if head.startswith("aws_") or head == "terraform_data":
            return scope + "::" + ".".join(parts[:2])
        return None

    def references(scope, expression, destination, relation, b):
        for parts in traversals(expression):
            source = resolve(scope, parts)
            if source is None:
                continue
            evidence = ".".join(parts)
            if source in nodes:
                edge(source, destination, relation, evidence, b["file"], b["line"])
            else:
                unresolved.append({"scope": scope, "reference": evidence, "file": b["file"], "line": b["line"]})

    for b in all_blocks:
        scope, kind = b["scope"], b["kind"]
        if kind in ("terraform", "moved"):
            continue
        for nid in b["ids"]:
            if kind == "module":
                call_name = b["labels"][0]
                child = "module." + call_name
                edge(nid, child + "::directory", "module_source", b["attrs"]["source"], b["file"], b["line"])
                for key, value in b["attrs"].items():
                    if key == "source":
                        continue
                    if key in ("count", "for_each", "depends_on"):
                        references(scope, value, nid, key, b)
                    else:
                        port = node(scope, "module." + call_name + ".input." + key, "module_input", b, expression=value)
                        references(scope, value, port, "input_expression", b)
                        target = child + "::var." + key
                        assert target in nodes, target
                        edge(port, target, "input_binding", key, b["file"], b["line"])
                if "count" in b["attrs"] or "for_each" in b["attrs"]:
                    for target in list(nodes.values()):
                        if target["scope"] == child and target["kind"] in ("resource", "data", "output"):
                            edge(nid, target["id"], "module_condition", b["attrs"].get("count", b["attrs"].get("for_each")), b["file"], b["line"])
                continue
            if kind == "locals":
                references(scope, nodes[nid]["attrs"]["value"], nid, "reference", b)
            else:
                references(scope, b["body"], nid, "reference", b)
                for meta in ("count", "for_each", "depends_on"):
                    if meta in b["attrs"]:
                        references(scope, b["attrs"][meta], nid, meta, b)
            if (kind == "resource" and b["labels"][0].startswith("aws_")) or kind == "data":
                edge(provider, nid, "provider", "inherited aws provider", b["file"], b["line"])
    # Explicit module depends_on is a conservative all-resource ordering barrier.
    for name, call in calls.items():
        if "depends_on" not in call["attrs"]:
            continue
        for parts in traversals(call["attrs"]["depends_on"]):
            for source in list(nodes.values()):
                matches = (source["scope"] == "module." + parts[1] and source["kind"] in ("resource", "data")) if parts[:1] == ["module"] else source["id"] == "root::" + ".".join(parts[:2])
                if not matches:
                    continue
                for target in list(nodes.values()):
                    if target["scope"] == "module." + name and target["kind"] in ("resource", "data"):
                        edge(source["id"], target["id"], "module_depends_on", call["attrs"]["depends_on"], call["file"], call["line"])
    result = {"method": "custom offline lexical/static HCL subset analysis; NOT Terraform graph/plan",
              "files": len(list(base.rglob('*.tf'))), "nodes": list(nodes.values()), "edges": list(edges.values()),
              "unresolved": unresolved, "blocks": all_blocks,
              "resource_declarations": sum(b["kind"] == "resource" for b in all_blocks),
              "variables": sum(b["kind"] == "variable" for b in all_blocks)}
    return result


def mermaid(nodes, edges):
    ids = {n["id"]: f"n{i}" for i, n in enumerate(nodes)}
    lines = ["flowchart LR"]
    for n in nodes:
        label = n["id"].replace('"', "'").replace("::", " / ")
        lines.append(f'  {ids[n["id"]]}["{label}"]')
    grouped = defaultdict(set)
    for e in edges:
        if e["source"] in ids and e["target"] in ids:
            grouped[(e["source"], e["target"])].add(e["relation"])
    for (src, dst), kinds in sorted(grouped.items()):
        relation = ",".join(sorted(kinds))
        lines.append(f'  {ids[src]} -->|"{relation}"| {ids[dst]}')
    return "\n".join(lines)


def serializable(graph):
    """Separate HCL attribute names from expressions, never resolved credentials."""
    result = copy.deepcopy(graph)
    result['attribute_schema'] = 'attributes are name/expression records, not evaluated values'
    for item in result['nodes'] + result['blocks']:
        if 'attrs' in item:
            item['attributes'] = [{'name': key, 'expression': value} for key, value in item.pop('attrs').items()]
    return result


def read_inventory(path):
    result = json.loads(Path(path).read_text(encoding='utf8'))
    result.pop('attribute_schema', None)
    for item in result['nodes'] + result['blocks']:
        if 'attributes' in item:
            item['attrs'] = {record['name']: record['expression'] for record in item.pop('attributes')}
    return result


def export(graph, out):
    out.mkdir(parents=True, exist_ok=True)
    (out/"terraform-inventory.json").write_text(json.dumps(serializable(graph),ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    ids = {n["id"]: f"n{i}" for i,n in enumerate(graph["nodes"])}
    dot = ['digraph terraform {', '  rankdir=LR;', '  node [shape=box,fontname="Arial"];']
    for n in graph["nodes"]:
        dot.append(f'  {ids[n["id"]]} [label={json.dumps(n["id"])}];')
    for e in graph["edges"]:
        style = "dotted" if e["relation"] in ("contains","module_source") else "solid"
        dot.append(f'  {ids[e["source"]]} -> {ids[e["target"]]} [label={json.dumps(e["relation"])},style={style}];')
    dot.append('}')
    (out/"terraform-dependencies.dot").write_text("\n".join(dot)+"\n",encoding="utf8")
    intro = """# Terraform Dependency Graph

Метод: власний offline lexical/static аналіз HCL. Graphify0.9.104 викликано, але його HCL extractor не працює без tree_sitter_hcl; пакет не встановлювався. Це НЕ terraform graph/Plan та не provider validation.

Стрілка A → B означає «B залежить від A». contains/module_source — лише структура, вони не визначають виконання. provider — успадкування root AWS provider. input_expression → input_binding показує реальну передачу input до child variable; module output references привʼязано до конкретного child output. count/for_each і module_condition залишають умовні вузли символічними, без розгортання instances. depends_on та module_depends_on — явні барʼєри.

Повний граф усіх видів вузлів: [DOT](terraform-dependencies.dot), [JSON з file/line/evidence](terraform-inventory.json). Нижче граф розбито за scopes для читабельності та обмежень Mermaid GitHub. Кожен scope включає свої вузли й зовнішні джерела залежностей; мережеві звʼязки показані ОКРЕМО в NETWORK_GRAPH.md.
"""
    sections = [intro]
    deps = [e for e in graph["edges"] if e["relation"] not in ("contains","module_source")]
    for scope in sorted({n["scope"] for n in graph["nodes"]}):
        selected = [e for e in deps if next(n for n in graph['nodes'] if n['id']==e['target'])['scope']==scope]
        wanted = {n['id'] for n in graph['nodes'] if n['scope']==scope}
        wanted.update(e['source'] for e in selected)
        ns = [n for n in graph['nodes'] if n['id'] in wanted]
        sections.append(f"\n## {scope}\n\n```mermaid\n{mermaid(ns,selected)}\n```\n")
    sections.append("\n## Непідтверджені traversals\n\n" + (json.dumps(graph['unresolved'],ensure_ascii=False,indent=2) if graph['unresolved'] else "Не залишилось нерозвʼязаних підтримуваних traversals. Це не доказ повноти Terraform semantics: динамічні conditions/instances та provider/schema/state не обчислювалися."))
    (out/"DEPENDENCY_GRAPH.md").write_text("\n".join(sections)+"\n",encoding="utf8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="docs/terraform")
    args=parser.parse_args()
    graph=build()
    export(graph,ROOT/args.output)
    print(json.dumps({"nodes":len(graph['nodes']),"edges":len(graph['edges']),"resources":graph['resource_declarations'],"variables":graph['variables'],"kinds":dict(Counter(n['kind'] for n in graph['nodes'])),"unresolved":len(graph['unresolved'])}))


if __name__ == "__main__":
    main()
