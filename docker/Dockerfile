FROM python:3.11-slim as base

ARG NAME

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app
ENV NAME=${NAME}
ENV AWS_DEFAULT_REGION ap-northeast-1

RUN pip install --no-cache-dir --upgrade pip==24.0


FROM base as ml
ENV ENV=ml

COPY requirements/ml.txt /app/requirements/ml.txt
RUN pip install --no-cache-dir -r requirements/ml.txt
COPY ./ml /app/ml

CMD ["python", "-m", "ml.main"]


FROM ml as predictor
ENV ENV=predictor

COPY requirements/predictor.txt /app/requirements/predictor.txt
RUN pip install --no-cache-dir -r requirements/predictor.txt
COPY ./predictor /app/predictor
EXPOSE 8080

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "--timeout", "60", "predictor.main:app"]


FROM ml as predictor-canary
ENV ENV=predictor-canary

COPY requirements/predictor.txt /app/requirements/predictor.txt
RUN pip install --no-cache-dir -r requirements/predictor.txt
COPY ./predictor /app/predictor
EXPOSE 8080

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "--timeout", "60", "predictor.main:app"]


FROM base as local
ENV SYSTEM_ENV=local
COPY requirements /app/requirements

RUN pip install --no-cache-dir -r requirements/ml.txt \
    && pip install --no-cache-dir -r requirements/predictor.txt \
    && pip install --no-cache-dir -r requirements/dev.txt
