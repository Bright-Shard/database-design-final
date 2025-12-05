import sys
from pathlib import Path
from typing import Callable

from flask import Flask
from flask.testing import FlaskClient

# Lets Python files in this folder import normflix even though it's in a parent
# folder

sys.path.append(str(Path(__file__).absolute().parent.parent))

import normflix
from normflix import db

type Test = Callable[[Flask, FlaskClient], None]

ALL_TESTS: list[Test] = []


def normflix_test(test: Test) -> Callable[[], None]:
	ALL_TESTS.append(test)

	@db.with_db
	def wrapped(conn):
		app = normflix.build_app(conn)
		test(app, app.test_client())

	return wrapped
