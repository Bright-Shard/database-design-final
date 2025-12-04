import http
import json
import typing as t
from http import HTTPStatus

import flask
from flask import Response, request
from flask.sansio.scaffold import T_route
from pydantic import BaseModel, ValidationError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType


class HttpCode(Response):
	"""
	Utility class that lets you return an empty HTTP response with a specific
	HTTP status code from a Flask handler.
	"""

	UNPROCESSIBLE_ENTITY: "HttpCode"
	OK: "HttpCode"

	def __init__(self, val: int | HTTPStatus):
		super().__init__(status=val)


HttpCode.UNPROCESSIBLE_ENTITY = HttpCode(HTTPStatus.UNPROCESSABLE_ENTITY)
HttpCode.OK = HttpCode(HTTPStatus.OK)


class HttpCodeAndMessage(Response):
	"""
	Utility class that lets you return an HTTP response with the specified HTTP
	code and message from a Flask handler.
	"""

	def __init__(self, code: int | HTTPStatus, msg: str):
		super().__init__(response=msg, status=code)


class Blueprint(flask.Blueprint):
	"""
	Adds some utilities to the default Flask `Blueprint` class.
	"""

	def route(self, rule: str, deserialize: type, **options: t.Any):
		"""
		Redefines the `@app.route` decorator to add a `deserialize` arg. You can
		pass a Pydantic class in that argument, and this decorator will
		automatically deserialize any client-provided JSON into that class.

		# Example
		```py
		import pydantic
		import json

		class MyApiArguments(pydantic.BaseModel):
			some_arg: str
			some_number: int

		@app.route("/endpoint", deserialize=MyApiArguments, methods=["POST"])
		def handler(args: MyApiArguments):
			# `args` will now be automatically deserialized from JSON to
			# `MyApiArguments` for you
			# If there's any errors with the JSON, the Pydantic errors are
			# automatically sent back to the client
			print(f"Got args {json.dumps(args)}")
		```
		"""

		def decorator(handler: t.Callable[..., Response]):
			def wrapper() -> Response:
				# Try to get JSON from the client's request, or simply use an
				# empty dictionary if there isn't any
				try:
					args = request.get_json(force=True)
				except (BadRequest, UnsupportedMediaType):
					args = {}

				# Try to create an instance of the Pydantic class with that JSON
				try:
					val = deserialize(**args)
				except ValidationError as e:
					# If it fails show the Pydantic errors to the client so they
					# know what fields are missing
					return HttpCodeAndMessage(HTTPStatus.UNPROCESSABLE_ENTITY, e.json())

				# Otherwise call the route handler as normal
				return handler(val)

			# Call the original route method
			return super(Blueprint, self).route(rule, **options)(wrapper)

		return decorator

	def post(self, rule: str, deserialize: type, **options: t.Any):
		"""
		Adds the `deserialize` argument to `@app.post`.
		"""
		return self.route(rule, deserialize, methods=["POST"], **options)

	def get(self, rule: str, deserialize: type, **options: t.Any):
		"""
		Adds the `deserialize` argument to `@app.get`.
		"""
		return self.route(rule, deserialize, methods=["GET"], **options)
