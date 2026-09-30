from flask import Flask
import psycopg2
import os
import time

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)