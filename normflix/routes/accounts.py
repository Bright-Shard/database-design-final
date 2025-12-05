import base64
import uuid
from http import HTTPStatus
from uuid import UUID

import flask
from flask import Blueprint, Response
from psycopg.errors import UniqueViolation
from pydantic import BaseModel

from normflix.utils import Auth, HttpCode, HttpCodeAndJSON, auth, deserialize, get_db

bp = flask.Blueprint("accounts", __name__, url_prefix="/accounts")


class NewAccountArgs(BaseModel):
	username: str
	password: str
	email: str


@bp.post("/new")
@deserialize(NewAccountArgs)
def new(args: NewAccountArgs) -> Response:
	db = get_db()
	with db.cursor() as cur:
		try:
			cur.execute(
				"""
				INSERT INTO users
					(
						user_id,
						username,
						password_hash,
						email,
						priv_add_media,
						priv_read_user_data,
						priv_write_user_data
					)
				VALUES
					(%s, %s, %s, %s, %s, %s, %s)
				""",
				(
					uuid.uuid4(),
					args.username,
					args.password,
					args.email,
					False,
					False,
					False,
				),
			)
		except UniqueViolation:
			return HttpCode.CONFLICT

		return HttpCode.OK


class AccountTokenArgs(BaseModel):
	username: str
	password: str


@bp.post("/token")
@deserialize(AccountTokenArgs)
def create_bearer_token(args: AccountTokenArgs):
	conn = get_db()
	with conn.cursor() as cur:
		query = cur.execute(
			"SELECT user_id FROM users WHERE (username = %s AND password_hash = %s)",
			(args.username, args.password),
		).fetchone()

		if query is None:
			return HttpCode.UNAUTHORIZED
		user_id: UUID = query[0]
		token = uuid.uuid4()

		cur.execute(
			"""
			INSERT INTO bearer_tokens (token, user_id) VALUES (%s, %s)
			""",
			(token, user_id),
		)

		return HttpCodeAndJSON(
			HTTPStatus.OK,
			{"bearer_token": base64.urlsafe_b64encode(token.bytes).decode()},
		)


@bp.put("/email")
@auth()
def set_email(auth: Auth) -> Response:
	return HttpCode.OK
