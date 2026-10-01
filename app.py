from flask import Flask, Response, request, g
import psycopg2
import os
import time

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST
)

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "flask_app_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "flask_app_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

ERROR_COUNT = Counter(
    "flask_app_errors_total",
    "Total number of HTTP errors",
    ["method", "endpoint", "status"]
)

APP_UPTIME = Gauge(
    "flask_app_uptime_seconds",
    "Application uptime in seconds"
)

START_TIME = time.time()


def get_db_connection():
    retries = 10

    while retries > 0:
        try:
            connection = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "hellodb"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "postgres"),
                port=os.getenv("DB_PORT", "5432")
            )
            return connection

        except psycopg2.OperationalError:
            retries -= 1
            print("Waiting for PostgreSQL...")
            time.sleep(2)

    raise Exception("Could not connect to PostgreSQL")


@app.before_request
def before_request():
    g.start_time = time.time()


@app.after_request
def after_request(response):
    endpoint = request.endpoint or "unknown"
    method = request.method
    status = str(response.status_code)

    latency = time.time() - g.start_time

    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).inc()

    REQUEST_LATENCY.labels(
        method=method,
        endpoint=endpoint
    ).observe(latency)

    if response.status_code >= 400:
        ERROR_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()

    APP_UPTIME.set(time.time() - START_TIME)

    return response


@app.route("/")
def hello():
    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            message TEXT NOT NULL
        )
    """)

    cursor.execute(
        "INSERT INTO messages (message) VALUES (%s)",
        ("Hello World from PostgreSQL!",)
    )

    connection.commit()

    cursor.execute(
        "SELECT message FROM messages ORDER BY id DESC LIMIT 1"
    )

    message = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return message


@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)