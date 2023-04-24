# syntax=docker/dockerfile:1.2


# base
FROM python:3.10.2-slim-buster AS base
ENV PYTHONUNBUFFERED=1 \
   PIP_DISABLE_PIP_VERSION_CHECK=1 


# build
FROM base AS build
ENV BUILD_DIR=/build \
    PYTHONPATH=/build
WORKDIR $BUILD_DIR
COPY requirements.txt .
RUN pip3 wheel --wheel-dir=/wheels -r requirements.txt


# prod
FROM base AS prod
ENV APP_DIR=/app\
    PYTHONPATH=/app
COPY . $APP_DIR
WORKDIR $APP_DIR
COPY --from=build /wheels /wheels
RUN pip3 install \
  --no-index \
  --no-cache-dir \
  --find-links=/wheels \
  -r requirements.txt
EXPOSE 5000
ENV FLASK_APP=./recommender_api/api.py
ENTRYPOINT ["python3", "-m" ,"flask", "run", "--host=0.0.0.0", "--port=5000"]
