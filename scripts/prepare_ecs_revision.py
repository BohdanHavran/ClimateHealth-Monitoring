"""Pure task-definition preparation; never calls AWS or prints credentials."""
import argparse
import json
import re
from pathlib import Path

FIELDS = {"family", "taskRoleArn", "executionRoleArn", "networkMode", "containerDefinitions",
          "volumes", "placementConstraints", "requiresCompatibilities", "cpu", "memory",
          "pidMode", "ipcMode", "proxyConfiguration", "inferenceAccelerators", "ephemeralStorage",
          "runtimePlatform", "enableFaultInjection"}


def prepare(base, image, family, account, task_role, execution_role):
    if not re.fullmatch(r"[0-9]{12}", account):
        raise ValueError("Invalid approved account")
    if not re.fullmatch(re.escape(account) + r"\.dkr\.ecr\.us-east-1\.amazonaws\.com/[a-z0-9/_-]+@sha256:[a-f0-9]{64}", image):
        raise ValueError("Approved account and immutable ECR image required")
    if base.get("family") != family or base.get("networkMode") != "bridge":
        raise ValueError("Reviewed family/bridge configuration required")
    if base.get("taskRoleArn") != task_role or base.get("executionRoleArn") != execution_role:
        raise ValueError("Role handoff mismatch")
    if any(not x.startswith("arn:aws:iam::" + account + ":role/") for x in [task_role, execution_role]):
        raise ValueError("Cross-account role rejected")
    result = json.loads(json.dumps({k: v for k, v in base.items() if k in FIELDS}))
    containers = result.get("containerDefinitions", [])
    if len(containers) != 1 or containers[0].get("name") != "backend":
        raise ValueError("Exactly one reviewed backend container required")
    for value in containers[0].get("environment", []):
        if re.search("PASS|SECRET|TOKEN|ACCESS_KEY|PRIVATE_KEY", value.get("name", ""), re.I):
            raise ValueError("Credentials must use secret references")
    containers[0]["image"] = image
    return result


def main():
    p=argparse.ArgumentParser()
    for key in ["input", "output", "image", "family", "account", "task-role", "execution-role"]:
        p.add_argument("--"+key,required=True)
    args=p.parse_args()
    base=json.loads(Path(args.input).read_text(encoding="utf8"))
    result=prepare(base,args.image,args.family,args.account,args.task_role,args.execution_role)
    Path(args.output).write_text(json.dumps(result),encoding="utf8")


if __name__ == "__main__":
    main()
