FROM python:3.14-alpine AS BUILDER

WORKDIR /default
COPY ../requirements.txt .

RUN pip install -r requirements.txt && pip check

FROM python:3.14-alpine AS RUNNER

WORKDIR /app
COPY /API ./app/

COPY --from=BUILDER /default ./app/

EXPOSE 8000
CMD [ "" ]