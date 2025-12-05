import importlib
import os

# Automatically imports all the other Python files in this folder
ROUTES = [
	importlib.import_module(f".{pkg[:-3]}", __name__)
	for pkg in [
		file
		for file in os.listdir(os.path.dirname(os.path.abspath(__file__)))
		if not file.startswith("__") and file.endswith(".py")
	]
]
