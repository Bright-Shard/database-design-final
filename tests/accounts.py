from http import HTTPStatus

from flask.app import Flask
from flask.testing import FlaskClient

if __package__ == None:
	import utils
	from utils import normflix_test
else:
	from tests import utils
	from tests.utils import normflix_test

import normflix as normflix


@normflix_test
def new_account(app: Flask, client: FlaskClient):
	"""
	Test an example API flow for when a new user signs up.
	"""
	response = client.post(
		"/accounts/new",
		json={"username": "test", "password": "password", "email": "bruh"},
	)
	assert response.status_code == HTTPStatus.OK

	# Get a bearer token for the new account
	response = client.post(
		"/accounts/token", json={"username": "test", "password": "password"}
	)
	assert response.status_code == HTTPStatus.OK
	json = response.json
	assert json is not None
	token = json["bearer_token"]

	# Then try to use the bearer token
	response = client.put(
		"/accounts/email",
		headers={"Authorization": f"Bearer {token}"},
		json={"email": "new-email@example.com"},
	)
	assert response.status_code == HTTPStatus.OK
	response = client.put(
		"/accounts/subscription",
		headers={"Authorization": f"Bearer {token}"},
		json={"subscription": "basic"},
	)
	assert response.status_code == HTTPStatus.OK
	response = client.delete(
		"/accounts/subscription",
		headers={"Authorization": f"Bearer {token}"},
	)
	assert response.status_code == HTTPStatus.OK
	response = client.put(
		"/accounts/password",
		headers={"Authorization": f"Bearer {token}"},
		json={"password": "new_passworD!23"},
	)
	assert response.status_code == HTTPStatus.OK


@normflix_test
def invalid_args(app: Flask, client: FlaskClient):
	"""
	Testing that the API errors when we pass invalid arguments to it
	"""
	# Verify that we error if the client tries to create an account with an
	# existing username or password
	client.post(
		"/accounts/new",
		json={
			"username": "invalid_args_user",
			"password": "password",
			"email": "invalid_args_email",
		},
	)
	response = client.post(
		"/accounts/new",
		json={
			"username": "invalid_args_user",
			"password": "password2",
			"email": "bruh",
		},
	)
	assert response.status_code == HTTPStatus.CONFLICT
	response = client.post(
		"/accounts/new",
		json={
			"username": "invalid_args_user2",
			"password": "password3",
			"email": "invalid_args_email",
		},
	)
	assert response.status_code == HTTPStatus.CONFLICT

	# Verify that we can't get an API key for a nonexistant account
	response = client.post(
		"/accounts/token",
		json={"username": "invalid_args_user", "password": "password123"},
	)
	assert response.status_code == HTTPStatus.UNAUTHORIZED
	assert response.json is None

	json = client.post(
		"/accounts/token",
		json={"username": "invalid_args_user", "password": "password"},
	).json
	assert json is not None
	token = json["bearer_token"]

	# Verify that we can only set the subscription to "basic", "standard", or
	# "premium"
	for plan in ["basic", "standard", "premium"]:
		response = client.put(
			"/accounts/subscription",
			headers={"Authorization": f"Bearer {token}"},
			json={"subscription": plan},
		)
		assert response.status_code == HTTPStatus.OK
	response = client.put(
		"/accounts/subscription",
		headers={"Authorization": f"Bearer {token}"},
		json={"subscription": "this subscription plan does not exist"},
	)
	assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
