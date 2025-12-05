from http import HTTPStatus

from flask import Blueprint
from psycopg.errors import UniqueViolation
from pydantic import BaseModel

from normflix.utils import Auth, HttpCode, auth, deserialize, get_db

bp = Blueprint("profiles", __name__, url_prefix="/profiles")


@bp.post("/<string:name>/new")
@auth()
def new(auth: Auth, name: str):
	with get_db().cursor() as cur:
		query = cur.execute(
			"SELECT subscription FROM users WHERE user_id = %s", (auth.user_id,)
		).fetchone()
		assert query is not None
		subscription = query[0]
		if subscription is None:
			return HttpCode(HTTPStatus.UPGRADE_REQUIRED)

		query = cur.execute(
			"SELECT max_profiles FROM subscriptions WHERE name = %s", (subscription,)
		).fetchone()
		assert query is not None
		max_profiles = query[0]
		query = cur.execute(
			"SELECT count(profile_name) FROM profiles WHERE user_id = %s",
			(auth.user_id,),
		).fetchone()
		assert query is not None
		current_profiles = query[0]

		if current_profiles < max_profiles:
			try:
				cur.execute(
					"INSERT INTO profiles (user_id, profile_name) VALUES (%s, %s)",
					(auth.user_id, name),
				)
			except UniqueViolation:
				return HttpCode.CONFLICT
			return HttpCode.OK
		else:
			return HttpCode(HTTPStatus.UPGRADE_REQUIRED)


@bp.delete("/<string:name>")
@auth()
def delete(auth: Auth, name: str):
	with get_db().cursor() as cur:
		cur.execute(
			"DELETE FROM profiles WHERE (user_id = %s AND profile_name = %s)",
			(auth.user_id, name),
		)
		return HttpCode.OK


class RenameProfileArgs(BaseModel):
	name: str


@bp.put("/<string:name>/name")
@deserialize(RenameProfileArgs)
@auth()
def rename(auth: Auth, name: str, args: RenameProfileArgs):
	with get_db().cursor() as cur:
		cur.execute(
			"UPDATE profiles SET profile_name = %s WHERE (profile_name = %s AND user_id = %s)",
			(args.name, name, auth.user_id),
		)
	return HttpCode.OK
