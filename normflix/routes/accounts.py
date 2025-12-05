import base64
import uuid
from http import HTTPStatus
from typing import Literal
from uuid import UUID

import flask
from flask import Response
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


class SetSubscriptionArgs(BaseModel):
	subscription: Literal["basic", "standard", "premium"]


@bp.put("/subscription")
@deserialize(SetSubscriptionArgs)
@auth()
def set_subscription(auth: Auth, args: SetSubscriptionArgs) -> Response:
	with get_db().cursor() as cur:
		cur.execute(
			"UPDATE users SET subscription = %s WHERE user_id = %s",
			(args.subscription, auth.user_id),
		)
	return HttpCode.OK


@bp.delete("/subscription")
@auth()
def delete_subscription(auth: Auth) -> Response:
	with get_db().cursor() as cur:
		cur.execute(
			"UPDATE users SET subscription = NULL WHERE user_id = %s",
			(auth.user_id,),
		)
	return HttpCode.OK


class SetEmailArgs(BaseModel):
	email: str


@bp.put("/email")
@deserialize(SetEmailArgs)
@auth()
def set_email(auth: Auth, args: SetEmailArgs) -> Response:
	with get_db().cursor() as cur:
		cur.execute(
			"UPDATE users SET email = %s WHERE user_id = %s", (args.email, auth.user_id)
		)
	return HttpCode.OK


class SetPasswordArgs(BaseModel):
	password: str


@bp.put("/password")
@deserialize(SetPasswordArgs)
@auth()
def set_password(auth: Auth, args: SetPasswordArgs) -> Response:
	with get_db().cursor() as cur:
		cur.execute(
			"UPDATE users SET password_hash = %s WHERE user_id = %s",
			(args.password, auth.user_id),
		)
	return HttpCode.OK
