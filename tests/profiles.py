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
def new_profile(app: Flask, client: FlaskClient):
	"""
	Test an example API flow for a new profile on a new account.
	"""
	client.post(
		"/accounts/new",
		json={
			"username": "new_profile_account",
			"password": "password",
			"email": "new_profile_email@example.com",
		},
	)

	# Get a bearer token for the new account
	response = client.post(
		"/accounts/token",
		json={"username": "new_profile_account", "password": "password"},
	).json
	assert response is not None
	token = response["bearer_token"]

	# Set a subscription plan for it
	client.put(
		"/accounts/subscription",
		headers={"Authorization": f"Bearer {token}"},
		json={"subscription": "premium"},
	)

	# Create a new profile
	response = client.post(
		"/profiles/test/new", headers={"Authorization": f"Bearer {token}"}
	)
	assert response.status_code == HTTPStatus.OK

	# Create a dummy movie
	response = client.post(
		"/accounts/token",
		json={
			"username": normflix.config.ADMIN_USER,
			"password": normflix.config.ADMIN_PASSWORD,
		},
	).json
	assert response is not None
	admin_token = response["bearer_token"]
	response = client.post(
		"/movies/new",
		headers={"Authorization": f"Bearer {admin_token}"},
		json={"name": "new_profile Test Media", "description": "e"},
	).json
	assert response is not None
	movie_id = response["movie_id"]

	# Get the profile's watch time for a movie they haven't watched
	response = client.get(
		"/profiles/test/progress",
		headers={"Authorization": f"Bearer {token}"},
		json={"kind": "movie_watch_progress", "movie_id": movie_id},
	)
	assert response.status_code == HTTPStatus.OK
	assert response.json is not None
	assert response.json["progress"] is None

	# Set the watch time
	response = client.post(
		"/profiles/test/progress",
		headers={"Authorization": f"Bearer {token}"},
		json={"kind": "movie_watch_progress", "movie_id": movie_id, "progress": 30},
	)
	assert response.status_code == HTTPStatus.OK

	# Get the watch time again and verify it's correct
	response = client.get(
		"/profiles/test/progress",
		headers={"Authorization": f"Bearer {token}"},
		json={"kind": "movie_watch_progress", "movie_id": movie_id},
	)
	assert response.status_code == HTTPStatus.OK
	assert response.json is not None
	assert response.json["progress"] == 30

	# Update the watch time and verify it's still correct
	response = client.put(
		"/profiles/test/progress",
		headers={"Authorization": f"Bearer {token}"},
		json={"kind": "movie_watch_progress", "movie_id": movie_id, "progress": 67},
	)
	assert response.status_code == HTTPStatus.OK
	response = client.get(
		"/profiles/test/progress",
		headers={"Authorization": f"Bearer {token}"},
		json={"kind": "movie_watch_progress", "movie_id": movie_id},
	).json
	assert response is not None
	assert response["progress"] == 67
