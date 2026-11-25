"""Offline USD estimates, not observed AWS bills. No AWS calls or resources."""
import csv
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RATES = {"t3.nano": .0052, "t3.micro": .0104, "t3.small": .0208,
         "t3.medium": .0416, "t3.large": .0832, "gp3": .08,
         "ipv4": .005, "fargate_vcpu": .04048, "fargate_gib": .004445,
         "alb": .0225, "lcu": .008, "nat": .045, "nat_gb": .045,
         "endpoint": .01, "endpoint_gb": .01, "rds": .016, "rds_gp3": .115}
BACKENDS = {"ecs_micro": ("t3.micro", None), "ecs_small": ("t3.small", None),
            "fargate_025_05": (None, (.25,.5)), "fargate_025_1": (None,(.25,1)),
            "fargate_05_1": (None,(.5,1)), "compose_small": ("t3.small",None)}
AI = ["off", "small_active", "medium_active", "small_demo80", "medium_demo80"]
NETWORKS = ["no_nat", "nat_gateway", "nat_nano", "nat_micro", "endpoints5"]


def estimate(backend="ecs_small", hours=80, alb=True, database="rds", ai="off",
             network="no_nat", cloudfront="paygo", db_schedule="persistent"):
    machine, fargate = BACKENDS[backend]
    private_backend = network in ["nat_gateway", "nat_nano", "nat_micro"]
    parts = {}
    parts["backend_compute"] = hours * (RATES[machine] if machine else
        fargate[0]*RATES["fargate_vcpu"] + fargate[1]*RATES["fargate_gib"])
    parts["backend_ebs"] = 20*RATES["gp3"] if machine else 0
    parts["backend_ipv4"] = 0 if private_backend else hours*RATES["ipv4"]
    parts["alb_hourly_lcu_ipv4"] = hours*(RATES["alb"] + .1*RATES["lcu"] + 2*RATES["ipv4"]) if alb else 0
    db_hours = 730 if db_schedule == "persistent" else hours
    parts["mysql_compute"] = db_hours*(RATES["rds"] if database == "rds" else RATES["t3.small"])
    parts["mysql_storage"] = 20*RATES["rds_gp3"] if database == "rds" else 30*RATES["gp3"]
    parts["rds_managed_secret"] = .405 if database == "rds" else 0
    ai_type = "t3.medium" if ai.startswith("medium") else "t3.small"
    ai_hours = min(hours,80) if ai.endswith("demo80") else hours
    parts["ai_compute"] = 0 if ai == "off" else ai_hours*RATES[ai_type]
    parts["ai_ebs"] = 0 if ai == "off" else 20*RATES["gp3"]
    parts["s3_storage_requests"] = 5*.023 + .005 + .004
    parts["cloudfront_delivery"] = .95 if cloudfront == "paygo" else 0
    parts["cloudfront_functions"] = .001 if cloudfront == "paygo" else 0
    parts["ecr_5gb"] = .50
    parts["cloudwatch"] = .50+.03+.30
    parts["snapshots_10gb"] = 10*.05
    # One existing DNS hosted zone (or equivalent external DNS): no domain registration.
    parts["dns_reserve"] = .50
    # Weather request egress reserve only; CloudFront viewer transfer is above, not billed twice.
    parts["non_cdn_transfer"] = 1*.09
    parts["network"] = 0
    if network == "nat_gateway":
        parts["network"] = hours*(RATES["nat"]+RATES["ipv4"]) + 10*RATES["nat_gb"]
    if network in ["nat_nano", "nat_micro"]:
        kind = "t3.nano" if network == "nat_nano" else "t3.micro"
        parts["network"] = hours*(RATES[kind]+RATES["ipv4"]) + 8*RATES["gp3"]
    if network == "endpoints5":
        parts["network"] = 5*hours*RATES["endpoint"] + 10*RATES["endpoint_gb"]
    # Example: four releases with 30 minutes extra capacity each, not a fixed AWS fee.
    parts["deployment_surge"] = 2*(RATES[machine]+RATES["ipv4"]+20*.08/730) if machine else (1/3)*(parts["backend_compute"]/hours + (0 if private_backend else RATES["ipv4"]))
    invalid = ""
    if not alb and fargate:
        invalid = "No stable HTTPS origin designed for direct Fargate; cost-only row, not deployable architecture"
    elif not alb and private_backend:
        invalid = "Private backend has no approved public origin/VPC-origin design; cost-only row"
    elif backend == "ecs_micro":
        invalid = "1 GiB host unbenchmarked; default 1024 MiB task cannot fit with 512 MiB reserved"
    total = sum(parts.values())
    return {"backend":backend,"hours":hours,"alb":alb,"database":database,"db_schedule":db_schedule,
            "ai":ai,"network":network,"cloudfront":cloudfront,"limitation":invalid,
            **{k:round(v,6) for k,v in parts.items()},"total_usd":round(total,2),
            "reserve20_usd":round(total*1.2,2),"credit100_months":round(100/(total*1.2),2)}


def main():
    reports = ROOT/"docs/reports"
    reports.mkdir(parents=True,exist_ok=True)
    rows = [estimate(b,h,a,d,i,n,c,s) for b,h,a,d,i,n,c,s in itertools.product(
        BACKENDS,[80,730],[False,True],["rds","ec2"],AI,NETWORKS,["paygo","free_conditional"],["persistent","with_backend"])]
    with (reports/"aws-architecture-cost-matrix.csv").open("w",encoding="utf8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    examples={f"{b}_{h}":estimate(b,h) for b in BACKENDS for h in [80,730]}
    for h in [80,730]:
        examples[f"recommended_ai80_{h}"]=estimate(hours=h,ai="small_demo80")
        examples[f"recommended_db_scheduled_{h}"]=estimate(hours=h,db_schedule="with_backend")
        examples[f"compose_no_alb_{h}"]=estimate("compose_small",h,alb=False)
    (reports/"aws-ecs-cost-summary.json").write_text(json.dumps({"date":"2026-11-24","region":"us-east-1","rates":RATES,"rows":len(rows),"examples":examples},indent=2),encoding="utf8")
    for k,v in examples.items():print(k,v["total_usd"],v["reserve20_usd"])
    print("Estimated combinations:",len(rows))


if __name__ == "__main__":
    main()
