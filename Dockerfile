FROM python:3.10.8-alpine3.16

ENV POETRY_VERSION=1.1.13
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /src

ENV PYTHONPATH="$PYTHONPATH:/src/app"
COPY poetry.lock pyproject.toml /src/

RUN apk update && apk add build-base postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-dev
COPY app /src/app/
COPY README.md /src
COPY CHANGELOG.md /src
# COPY alembic.ini /src/
# COPY alembic /src/alembic

RUN env | grep BUILD_ > /src/build_envs.txt; exit 0

COPY prestart.sh /src/
RUN chmod +x prestart.sh
ENTRYPOINT ["./prestart.sh"]
