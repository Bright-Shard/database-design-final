"""
Runs the NormFlix Flask API.
"""

if __package__ == None:
	import utils
else:
	from bin import utils

from normflix import run_api

if __name__ == "__main__":
	print("Starting API")
	run_api()
