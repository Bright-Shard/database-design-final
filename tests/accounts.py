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

	# Verify that we can get an API key for the new account
	response = client.post(
		"/accounts/token", json={"username": "test", "password": "password"}
	)
	assert response.status_code == HTTPStatus.OK
	json = response.json
	assert json is not None
	token = json["bearer_token"]

	# Verify that we can't get an API key for a nonexistant account
	response = client.post(
		"/accounts/token", json={"username": "test", "password": "password123"}
	)
	assert response.status_code == HTTPStatus.UNAUTHORIZED
	assert response.json is None

	# Then try to use the bearer token
	response = client.put(
		"/accounts/email", headers={"Authorization": f"Bearer {token}"}
	)
	assert response.status_code == HTTPStatus.OK
