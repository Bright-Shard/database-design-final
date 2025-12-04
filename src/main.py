import multiprocessing
import time

import psycopg
from flask import Flask

from . import config, db, routes


# Build the Flask app that serves our API server
def build_app(db_connection: psycopg.Connection) -> Flask:
	app = Flask(__name__)

	for route in routes.ROUTES:
		app.register_blueprint(route.bp)

	return app


# Downloads PostgreSQL, starts its container, then runs all the necessary setup
# code for creating the tables/columns/etc that NormFlix needs.
def setup_db():
	db.download_postgres()
	# Starting the database takes over the current process, so we start a
	# background process and start it in there
	p = multiprocessing.Process(target=db.start_container)
	p.start()
	# Give Postgres time to start
	time.sleep(3)
	db.setup()


if __name__ == "__main__":
	setup_db()

	with psycopg.connect(config.POSTGRES_RUN_CONN_URL) as conn:
		build_app(conn).run(host=config.HOST, port=config.API_PORT)

	db.stop_container()
