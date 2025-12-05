from http import HTTPStatus

from flask.testing import FlaskClient

if __package__ == None:
	import utils
else:
	from tests import utils

import normflix as normflix


@utils.normflix_test
def new_account(app, client: FlaskClient):
	response = client.post(
		"/accounts/new",
		json={"username": "test", "password": "password", "email": "bruh"},
	)
	assert response.status_code == HTTPStatus.OK

	# Verify that we error if the client tries to create an account with an
	# existing username or password
	response = client.post(
		"/accounts/new",
		json={"username": "test", "password": "password2", "email": "bruh"},
	)
	assert response.status_code == HTTPStatus.CONFLICT
	response = client.post(
		"/accounts/new",
		json={"username": "test2", "password": "password3", "email": "bruh"},
	)
	assert response.status_code == HTTPStatus.CONFLICT
