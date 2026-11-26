"""Dependency-free source checks. NOT Terraform parsing, fmt, validate or plan."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "infrastructure/terraform"


def balanced(text):
    stack=[];i=0
    pairs={"}":"{", "]":"[", ")":"("}
    while i<len(text):
        if text.startswith("//",i) or text[i]=="#":
            end=text.find("\n",i);i=len(text) if end<0 else end+1;continue
        if text.startswith("/*",i):
            end=text.find("*/",i+2)
            assert end>=0,"Unclosed comment"
            i=end+2;continue
        if text.startswith("<<",i):
            match=re.match(r"<<-?([A-Za-z_][A-Za-z0-9_]*)",text[i:])
            if match:
                end=re.search(r"(?m)^\s*"+re.escape(match.group(1))+r"\s*$",text[i+len(match.group(0)):])
                assert end,"Unclosed heredoc"
                i+=len(match.group(0))+end.end();continue
        if text[i]=='"':
            i+=1
            while i<len(text):
                if text[i]=="\\":i+=2;continue
                if text[i]=='"':i+=1;break
                i+=1
            else:raise AssertionError("Unclosed string")
            continue
        char=text[i]
        if char in "{[(":stack.append(char)
        if char in "}])":assert stack and stack.pop()==pairs[char],"Unbalanced delimiters"
        i+=1
    assert not stack,"Unclosed delimiters"


def main():
    files=list(BASE.rglob("*.tf"));assert files
    assert {p.name for p in BASE.glob("*.tf")} == {"main.tf", "provider.tf", "variable.tf", "output.tf", "data.tf"}, "Unexpected root scaffold"
    assert {p.name for p in BASE.iterdir() if p.is_dir()} == {"modules"}, "Only modules may be nested under the active root"
    provider=(BASE/"provider.tf").read_text(encoding="utf8")
    assert re.search(r'(?m)^\s*region\s*=\s*var\.aws_region\s*$', provider)
    assert 'version = "= 6.74.0"' in provider
    assert 'required_version = ">= 1.11.0, < 2.0.0"' in provider
    assert not re.search(r'(?m)^\s*(access_key|secret_key|profile|shared_credentials_files|assume_role)\s*[={]',provider)
    root_text="\n".join(p.read_text(encoding="utf8") for p in BASE.glob("*.tf"))
    variables=dict(re.findall(r'variable\s+"([^"\n]+)"\s*\{(.*?)^\}',root_text,re.M|re.S))
    assert set(re.findall(r'\bvar\.([a-z_]+)',root_text))<=variables.keys(), "Undeclared root input"
    assert "region" not in variables and "account_id" not in variables
    assert "owner" not in variables and "aws_account_id" not in variables
    assert 'data "aws_caller_identity" "current"' in root_text
    assert root_text.count("data.aws_caller_identity.current.account_id") == 3, "Preserve all three ARN account checks"
    for name in ["aws_region", "environment"]:
        assert name in variables and not re.search(r'(?m)^\s*default\s*=',variables[name]), (name,"Must be an explicit HCP input")
    for name in ["infrastructure_reviewed", "application_window_open", "service_enabled", "ai_enabled", "allow_deployment_capacity", "artifacts_provisioned", "database_provisioned", "edge_provisioned", "backend_provisioned", "ai_provisioned", "ai_runtime_reviewed"]:
        assert re.search(r'\bdefault\s*=\s*false\b',variables[name]), (name,"Activation gate changed")
    workflow=(ROOT/".github/workflows/terraform-ci.yml").read_text(encoding="utf8")
    assert "python scripts/check_infrastructure_sources.py" in workflow
    assert "infrastructure/terraform/aws" not in workflow
    hcp=(ROOT/"docs/HCP_TERRAFORM.md").read_text(encoding="utf8")
    assert "infrastructure/terraform/aws" not in hcp
    assert "/infrastructure/terraform/**" in hcp
    assert all(f"`{name}`" in hcp for name in variables), "HCP variable inventory incomplete"
    for p in files:
        text=p.read_text(encoding="utf8");balanced(text)
        assert not re.search(r'\bbackend\s+"',text),"HCP state only"
        assert not re.search(r'(?m)^\s*cloud\s*\{',text),"VCS-only root has no cloud block"
        assert not re.search(r'source\s*=\s*"(?:[A-Za-z]:|/|\\)',text),"Absolute module source"
    main=(BASE/"main.tf").read_text(encoding="utf8")
    modules=dict(re.findall(r'module\s+"([^"\n]+)"\s*\{(.*?)^\}',main,re.M|re.S))
    assert len(modules)==8
    outputs={}
    for name,body in modules.items():
        source=re.search(r'source\s*=\s*"([^"\n]+)"',body).group(1)
        directory=(BASE/source).resolve();assert directory.is_relative_to(BASE.resolve()) and directory.is_dir()
        text="\n".join(p.read_text(encoding="utf8") for p in directory.glob("*.tf"))
        inputs=set(re.findall(r'variable\s+"([^"\n]+)"',text))
        assert set(re.findall(r'\bvar\.([a-z_]+)',text))<=inputs, (name,"Undeclared child input")
        declarations=dict(re.findall(r'variable\s+"([^"\n]+)"\s*\{(.*?)^\}',text,re.M|re.S))
        required={key for key,value in declarations.items() if not re.search(r'(?m)^\s*default\s*=',value)}
        assigned=set(re.findall(r'(?m)^\s*([a-z_]+)\s*=',body)) - {"source","count","depends_on","providers","for_each"}
        assert assigned<=inputs,(name,assigned-inputs)
        assert required<=assigned,(name,"Missing required child inputs",required-assigned)
        outputs[name]=set(re.findall(r'output\s+"([^"\n]+)"',text))
    for name,out in re.findall(r'module\.([a-z_]+)(?:\[[^]]+\])?\.([a-z_]+)', main+(BASE/"output.tf").read_text()):
        assert out in outputs[name],(name,out)
    assert not (BASE/"environments").exists() and not (BASE/"bootstrap").exists()
    for p in (ROOT/"infrastructure/ci").glob("*.json.example"):
        obj=json.loads(p.read_text(encoding="utf8"))
        if p.name.startswith("hcp-"):
            conditions=obj["Statement"][0]["Condition"]["StringEquals"]
            assert conditions["app.terraform.io:aud"]=="aws.workload.identity"
            assert "*" not in conditions["app.terraform.io:sub"]
            assert conditions["app.terraform.io:sub"].endswith(":plan" if "-plan-" in p.name else ":apply")
    with (ROOT/"docs/reports/aws-architecture-cost-matrix.csv").open(encoding="utf8",newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==4800
    costs=["backend_compute","backend_ebs","backend_ipv4","alb_hourly_lcu_ipv4","mysql_compute","mysql_storage","rds_managed_secret","ai_compute","ai_ebs","s3_storage_requests","cloudfront_delivery","cloudfront_functions","ecr_5gb","cloudwatch","snapshots_10gb","dns_reserve","non_cdn_transfer","network","deployment_surge"]
    for row in rows:
        total=sum(float(row[k]) for k in costs)
        assert abs(round(total,2)-float(row["total_usd"]))<=.011
        assert abs(round(total*1.2,2)-float(row["reserve20_usd"]))<=.011
    print(json.dumps({"status":"passed","active_root":BASE.relative_to(ROOT).as_posix(),"root_inputs":len(variables),"terraform_files_lexically_checked":len(files),"local_module_contracts":len(modules),"cost_rows":len(rows),"terraform_execution":False,"provider_schema_validated":False}))


if __name__ == "__main__":
    main()
