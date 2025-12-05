import multiprocessing
import time

import psycopg
from flask import Flask

from normflix import config

from . import db, routes


# Build the Flask app that serves our API server
def build_app(db_connection: psycopg.Connection) -> Flask:
	app = Flask(__name__)

	for route in routes.ROUTES:
		app.register_blueprint(route.bp)
	app.extensions["db"] = db_connection

	return app


# Downloads PostgreSQL, starts its container, then runs all the necessary setup
# code for creating the tables/columns/etc that NormFlix needs.
def run_db():
	db.download_postgres()
	# Starting the database takes over the current process, so we start a
	# background process and start it in there
	p = multiprocessing.Process(target=db.start_container)
	p.start()
	# Give Postgres time to start
	time.sleep(3)
	db.setup()
	p.join()


@db.with_db
def run_api(conn):
	build_app(conn).run(host=config.HOST, port=config.API_PORT)
