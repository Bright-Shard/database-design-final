if __package__ == None:
	import utils
else:
	from bin import utils

from normflix import run_api, run_db

run_db()
run_api()
