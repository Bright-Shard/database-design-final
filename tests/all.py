import importlib
import os

if __package__ == None:
	import utils
else:
	from tests import utils

import psycopg

import normflix
from normflix import db


def run_all_tests():
	print("Deleting old database tables")
	try:
		db.reset()
	except psycopg.errors.InvalidCatalogName:
		# Couldn't delete the NormFlix database because it didn't exist
		# We just ignore this error since we only want to delete the database if
		# it already existed anyways
		pass
	print("Creating NormFlix database tables")
	db.setup()
	print("Database setup")

	@db.with_db
	def inner(conn):
		app = normflix.build_app(conn)
		client = app.test_client()

		for test in utils.ALL_TESTS:
			print(f"Running '{test.__module__}.{test.__name__}'")
			test(app, client)
			print("Succeeded")

	inner()


test_modules = [
	importlib.import_module(f".{pkg[:-3]}", "tests")
	for pkg in [
		file
		for file in os.listdir(os.path.dirname(os.path.abspath(__file__)))
		if file not in ["utils.py", "tests.py"] and file.endswith(".py")
	]
]

if __name__ == "__main__":
	run_all_tests()
