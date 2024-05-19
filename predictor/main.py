import json
import os
import random
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import polars as pl
from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from ml.utils.consts import INTERNAL_NAMESPACE
from ml.utils.logger.logger_config import get_logger
from predictor.schemas.request import BidRequest
from predictor.utils.setup import get_ecs_instance_id, get_predictor_models

env = os.environ.get("ENV")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    app.state.predictor_models = get_predictor_models(os.getenv("REVISION"))
    app.state.instance = get_ecs_instance_id()
    if os.getenv("SYSTEM_ENV") == "local":
        app.state.pushgateway_url = "pushgateway:9091"
    else:
        app.state.pushgateway_url = f"pushgateway.{INTERNAL_NAMESPACE}:9091"

    logger.info(f"Instance ID: {app.state.instance}")
    logger.info(f"Pushgateway URL: {app.state.pushgateway_url}")
    logger.info("start server")
    yield
    logger.info("shutdown server")


app = FastAPI(lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )


@app.get("/")
async def health_check() -> dict[str, str]:
    logger.info("health check method was called")
    return {"Hello": "World"}


@app.post("/predict")
def predict(bid_request: BidRequest) -> dict[str, float | str]:
    start_time = time.time()
    try:
        logger.info(f"predict method call: {bid_request}")
        df = pl.DataFrame(json.loads(bid_request.json()))
        predictor_models = app.state.predictor_models
        model_name = random.choice(list(predictor_models.keys()))
        model = predictor_models[model_name]
        preprocessed = model.preprocessor.transform(df)
        pred = model.model.predict(preprocessed)
        logger.info(f"model: {model_name}, predict value: {pred}")
        end_time = time.time()
        logger.info(f"Prediction time: {end_time - start_time}")
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
    return {"prediction": pred, "model": model_name}
