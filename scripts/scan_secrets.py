"""Offline detect-secrets over Git candidates/index/history; never prints values."""
import argparse
import json
import re
from pathlib import Path
import subprocess
import tempfile

from detect_secrets import SecretsCollection
from detect_secrets.settings import default_settings

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),*args],cwd=ROOT)


def scan(staged=False, history=False, known_secret_env=None):
    findings, count = [], 0
    paths = git('ls-files','-z',*([] if staged else ['--cached','--others','--exclude-standard'])).decode('utf8').split('\0')
    known_secret = None
    if known_secret_env:
        from inspect_mysql import legacy_password
        known_secret = legacy_password(known_secret_env).encode('utf8')
    with tempfile.TemporaryDirectory() as temporary, default_settings():
        for relative in sorted(set(filter(None,paths))):
            source = ROOT / relative
            if staged:
                content = git('show',':'+relative)
                source = Path(temporary) / Path(relative).name
                source.write_bytes(content)
            if not source.is_file():
                continue
            if known_secret:
                # A common word may also occur in identifiers such as db_password.
                # Match complete credential values, not arbitrary substrings or usernames.
                text = source.read_bytes().decode('utf8',errors='replace')
                value = re.escape(known_secret.decode('utf8'))
                pattern = r'''(?im)(?:DB_PASS|DB_PASSWORD|MYSQL_PASSWORD|MYSQL_ROOT_PASSWORD|password)["']?\s*[:=]\s*["']?''' + value + r'''(?:["']|\s|$)'''
                uri = r'://[^\s/:]+:' + value + '@'
                if re.search(pattern,text) or re.search(uri,text):
                    findings.append({'file':relative,'line':0,'rule':'Known local database credential value'})
            collection = SecretsCollection()
            collection.scan_file(str(source))
            count += 1
            findings.extend({'file':relative,'line':secret.line_number,'rule':secret.type}
                            for _,secret in collection)
        if history:
            with default_settings() as history_settings:
                # Historical paths can be deleted or renamed in the working tree.
                # scan_diff must inspect their added lines, not require a current file.
                history_settings.disable_filters('detect_secrets.filters.common.is_invalid_file')
                commits = git('rev-list','--all').decode().splitlines()
                for commit in commits:
                    collection = SecretsCollection()
                    # A textual patch for each commit; binary contents are excluded by Git.
                    patch = git('show','--format=','--root',commit).decode('utf8',errors='replace')
                    collection.scan_diff(patch)
                    findings.extend({'file':filename,'line':secret.line_number,'rule':secret.type,
                                     'commit':commit} for filename,secret in collection)
    return {'mode':'index' if staged else 'git candidates','files_scanned':count,
            'history_scanned':history,'known_local_secret_checked':bool(known_secret),'findings':findings,
            'limitations':'Offline heuristics, no live credential verification; not a guarantee of no secrets.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--staged',action='store_true')
    parser.add_argument('--history',action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--known-secret-env', help='Optional local-only exact match; never printed or saved')
    args = parser.parse_args()
    result = scan(args.staged,args.history,args.known_secret_env)
    if args.output:
        Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(bool(result['findings']))
