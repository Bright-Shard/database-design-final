"""
Downloads a PostgreSQL container in Podman or Docker (whichever is installed)
and starts that container.

Note that this doesn't actually create the NormFlix database in PostgreSQL, use
`setup_db.py` for that.
"""

if __package__ == None:
	import utils
else:
	from bin import utils

from normflix import db

if __name__ == "__main__":
	db.download_postgres()
	db.start_container()
