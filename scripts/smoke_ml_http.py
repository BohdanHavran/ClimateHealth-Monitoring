"""Synthetic technical request through real Flask -> local FastAPI HTTP; no DB."""
import json
import os
from pathlib import Path
import secrets
import socket
import sys
from threading import Thread
from time import monotonic, sleep

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def main():
    import requests
    import uvicorn
    from werkzeug.serving import make_server
    from ml_service.app import app as ml_app
    from climat import app as backend

    token = secrets.token_urlsafe(32)
    previous = {name:os.environ.get(name) for name in ('ML_SERVICE_TOKEN','ML_SERVICE_URL')}
    listener = socket.socket()
    listener.bind(('127.0.0.1',0)); listener.listen(128)
    os.environ['ML_SERVICE_TOKEN'] = token
    os.environ['ML_SERVICE_URL'] = 'http://127.0.0.1:'+str(listener.getsockname()[1])
    ml = uvicorn.Server(uvicorn.Config(ml_app,log_level='critical',access_log=False))
    ml_thread = Thread(target=lambda:ml.run(sockets=[listener]),daemon=True)
    server = make_server('127.0.0.1',0,backend)
    web_thread = Thread(target=server.serve_forever,daemon=True)
    ml_thread.start(); web_thread.start()
    try:
        deadline = monotonic()+10
        while not ml.started and monotonic()<deadline:
            sleep(.05)
        if not ml.started:
            raise RuntimeError('ML startup timeout')
        payload = {'region_id':'synthetic-region','issue_time':'2026-01-01T12:00:00Z',
                   'horizon_days':1,'feature_schema_version':'climate-v1',
                   'features':[{'name':'temperature','value':3.4,'unit':'C',
                                'event_time':'2026-01-01T00:00:00Z',
                                'available_at':'2026-01-01T01:00:00Z','source':'synthetic-fixture'}]}
        response = requests.post(f'http://127.0.0.1:{server.server_port}/api/v1/predictions',json=payload,timeout=10)
        result = response.json()['data']
        assert response.status_code == 503 and result['value'] is None
        assert result['reason'] == 'model_unavailable' and result['model_version'] is None
        report = {'fixture':'synthetic technical test only', 'backend_status':response.status_code,
                  'ml_reason':result['reason'],'value':result['value'],'database_access':False,
                  'transport':'real loopback Flask -> authenticated FastAPI HTTP'}
        (ROOT/'docs/reports/phase2-ml-http.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print('Real Flask -> ML HTTP passed: honest 503 model_unavailable, no prediction')
    finally:
        server.shutdown(); web_thread.join(timeout=5); server.server_close()
        ml.should_exit = True; ml_thread.join(timeout=5); listener.close()
        for name,value in previous.items():
            if value is None:
                os.environ.pop(name,None)
            else:
                os.environ[name] = value


if __name__ == '__main__':
    main()
