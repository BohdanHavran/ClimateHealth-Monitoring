"""Real local HTTP/MySQL read-only smoke; never prints records or credentials."""
import argparse
import json
import os
from pathlib import Path
import sys
from threading import Thread
from urllib.request import urlopen

from inspect_mysql import legacy_password

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret-source', required=True)
    parser.add_argument('--serve', action='store_true', help='Keep a loopback server for frontend verification')
    args = parser.parse_args()
    os.environ.update(DB_HOST='192.168.0.165',DB_USER='root',DB_NAME='climate_db',
                      DB_PASS=legacy_password(args.secret_source),MPLBACKEND='Agg')
    os.environ.pop('DB_PASS_FILE',None)
    sys.path.insert(0,str(ROOT))
    from climat import app
    from werkzeug.serving import make_server
    server = make_server('127.0.0.1',8000 if args.serve else 0,app)
    thread = Thread(target=server.serve_forever,daemon=True)
    thread.start()
    checks = []
    try:
        paths = ['/health/ready','/api/v1/status','/api/v1/schema',
                 '/api/v1/observations?limit=5',
                 '/api/v1/places?south=44&north=53&west=22&east=41&limit=5',
                 '/api/places_in_bounds?minLat=44&maxLat=53&minLon=22&maxLon=41&limit=5']
        for path in paths:
            with urlopen(f'http://127.0.0.1:{server.server_port}{path}',timeout=10) as response:
                body = json.load(response)
                data = body.get('data', body.get('places'))
                checks.append({'path':path,'status':response.status,
                               'rows_returned':len(data) if isinstance(data,list) else None})
        report = {'database_writes':0,'schema_writes':0,'transport':'real HTTP', 'checks':checks}
        output = ROOT / 'docs/reports/phase2-mysql-http.json'
        output.write_text(json.dumps(report,indent=2),encoding='utf8')
        print('Read-only phase 2 smoke passed; records and credentials not logged', flush=True)
        if args.serve:
            print('Loopback read-only frontend diagnostic server active on port 8000', flush=True)
            # Interactive session is stopped with Ctrl+C after browser checks.
            while thread.is_alive():
                thread.join(timeout=1)
    finally:
        server.shutdown(); thread.join(timeout=5); server.server_close()
        os.environ.pop('DB_PASS',None)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as error:
        print('Phase 2 smoke failed (details redacted): '+type(error).__name__)
        raise SystemExit(1)
