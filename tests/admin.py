from http import HTTPStatus

from flask.app import Flask
from flask.testing import FlaskClient

if __package__ is None:
	import utils
	from utils import normflix_test
else:
	from tests import utils
	from tests.utils import normflix_test

import normflix as normflix


@normflix_test
def new_movie(app: Flask, client: FlaskClient):
	"""
	Test adding a new movie to the NormFlix library with the admin account.
	"""

	# Get a bearer token for the admin account
	response = client.post(
		"/accounts/token",
		json={
			"username": normflix.config.ADMIN_USER,
			"password": normflix.config.ADMIN_PASSWORD,
		},
	)
	assert response.status_code == HTTPStatus.OK
	json = response.json
	assert json is not None
	token = json["bearer_token"]

	response = client.post(
		"/movies/new",
		headers={"Authorization": f"Bearer {token}"},
		json={"name": "A True Bruh Moment", "description": "The bruhest of moments."},
	)
	assert response.status_code == HTTPStatus.OK
	assert response.json is not None
	assert "movie_id" in response.json
