import uuid

import flask
from psycopg.errors import UniqueViolation
from pydantic import BaseModel

from normflix.utils import Blueprint, HttpCode, get_db

bp = Blueprint("accounts", __name__, url_prefix="/accounts")


class NewAccountArgs(BaseModel):
	username: str
	password: str
	email: str


@bp.post("/new", deserialize=NewAccountArgs)
def new(args: NewAccountArgs) -> flask.Response:
	db = get_db()
	with db.cursor() as cur:
		try:
			cur.execute(
				"""
				INSERT INTO users
					(
						user_id,
						user_name,
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
