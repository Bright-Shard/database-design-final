"""
Connects to the running PostgreSQL container, deletes NormFlix's database, then
recreates that database and all of its tables. Useful if you change any of the
database code for NormFlix.
"""

import psycopg

if __package__ == None:
	import utils
else:
	from bin import utils

from normflix import db

if __name__ == "__main__":
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
	print("Done")
