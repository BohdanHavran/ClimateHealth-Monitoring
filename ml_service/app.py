import hmac
import json
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ml_contract import ContractError, evaluate_unavailable_request

app = FastAPI(title="Climate health ML boundary", version="0.2.0", docs_url=None, redoc_url=None)


@app.get("/health/live")
def live():
    return {"status": "ok", "model_status": "unavailable"}


@app.post("/api/v1/predict")
async def predict(request: Request):
    token = os.getenv("ML_SERVICE_TOKEN", "")
    header = request.headers.get("authorization", "")
    if not token or not hmac.compare_digest(header.encode(), ("Bearer " + token).encode()):
        return JSONResponse({"error": {"code": "unauthorized"}}, status_code=401)
    # Enforce the limit while receiving, even if Content-Length is absent.
    chunks, size = [], 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > 262144:
            return JSONResponse({"error": {"code": "request_too_large"}}, status_code=413)
        chunks.append(chunk)
    try:
        payload = json.loads(b"".join(chunks))
        result = evaluate_unavailable_request(payload)
        if payload["feature_schema_version"] != "climate-v1":
            raise ContractError("Unsupported feature schema")
    except (ValueError, TypeError, KeyError):
        return JSONResponse({"error": {"code": "invalid_features"}}, status_code=422)
    return JSONResponse(result, status_code=503)
