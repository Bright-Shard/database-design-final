import base64
import typing as t
from functools import wraps
from http import HTTPStatus
from uuid import UUID

import flask
from flask import Response, jsonify, request
from psycopg import Connection
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType


class HttpCode(Response):
	"""
	Utility class that lets you return an empty HTTP response with a specific
	HTTP status code from a Flask handler.
	"""

	UNPROCESSIBLE_ENTITY: "HttpCode"
	OK: "HttpCode"
	INTERNAL_SERVER_ERROR: "HttpCode"
	CONFLICT: "HttpCode"
	UNAUTHORIZED: "HttpCode"

	def __init__(self, val: int | HTTPStatus):
		super().__init__(status=val)


HttpCode.UNPROCESSIBLE_ENTITY = HttpCode(HTTPStatus.UNPROCESSABLE_ENTITY)
HttpCode.OK = HttpCode(HTTPStatus.OK)
HttpCode.INTERNAL_SERVER_ERROR = HttpCode(HTTPStatus.INTERNAL_SERVER_ERROR)
HttpCode.CONFLICT = HttpCode(HTTPStatus.CONFLICT)
HttpCode.UNAUTHORIZED = HttpCode(HTTPStatus.UNAUTHORIZED)


class HttpCodeAndMessage(Response):
	"""
	Utility class that lets you return an HTTP response with the specified HTTP
	code and message from a Flask handler.
	"""

	def __init__(self, code: int | HTTPStatus, msg: str):
		super().__init__(response=msg, status=code)


def HttpCodeAndJSON(code: int | HTTPStatus, msg: dict) -> Response:
	response = jsonify(msg)
	response.status_code = code
	return response


class Auth:
	def __init__(self, user_id: UUID):
		self.user_id = user_id


type Route = t.Callable[..., Response]
type RouteDecorator = t.Callable[[Route], Route]


def auth(
	error_code: HttpCode = HttpCode.UNAUTHORIZED,
) -> RouteDecorator:
	def decorator(func: Route) -> Route:
		@wraps(func)
		def wrapper(*args, **kwargs):
			if "Authorization" not in request.headers:
				return error_code
			token = request.headers["Authorization"]
			if not token.startswith("Bearer "):
				return error_code
			token = token[len("Bearer ") :]

			conn = get_db()
			with conn.cursor() as cur:
				query = cur.execute(
					"SELECT user_id FROM bearer_tokens WHERE token = %s",
					(UUID(bytes=base64.urlsafe_b64decode(token)),),
				).fetchone()
				if query is None:
					return error_code

				user_id = query[0]

			return func(Auth(user_id), *args, **kwargs)

		return wrapper

	return decorator


def deserialize(ty: type) -> RouteDecorator:
	def decorator(func: Route) -> Route:
		@wraps(func)
		def wrapper(*args, **kwargs):
			# Try to get JSON from the client's request, or simply use an
			# empty dictionary if there isn't any
			try:
				json = request.get_json(force=True)
			except (BadRequest, UnsupportedMediaType):
				json = {}

			# Try to create an instance of the Pydantic class with that JSON
			try:
				val = ty(**json)
			except ValidationError as e:
				# If it fails show the Pydantic errors to the client so they
				# know what fields are missing
				return HttpCodeAndMessage(HTTPStatus.UNPROCESSABLE_ENTITY, e.json())

			# Otherwise call the route as normal
			return func(val, *args, **kwargs)

		return wrapper

	return decorator


def get_db() -> Connection:
	"""
	Gets the database connection from the global Flask app and returns it with
	the correct type. This mostly helps out Python type-checkers.
	"""
	return flask.current_app.extensions["db"]
