from http import HTTPStatus
from typing import Literal
from uuid import UUID

from flask import Blueprint
from psycopg.errors import UniqueViolation
from pydantic import BaseModel

from normflix.utils import Auth, HttpCode, HttpCodeAndJSON, auth, deserialize, get_db

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


class WatchProgressArgs:
	kind: Literal["movie_watch_progress", "tv_show_watch_progress"]
	movie_id: UUID | None
	tv_show_id: UUID | None
	tv_show_season: int | None
	tv_show_episode: int | None
	progress: int | None


@bp.get("/<string:name>/progress")
@deserialize(WatchProgressArgs)
@auth()
def get_watch_progress(auth: Auth, name: str, args: WatchProgressArgs):
	progress = None
	with get_db().cursor() as cur:
		if args.kind == "movie_watch_progress":
			if (
				args.tv_show_id is None
				or args.tv_show_season is None
				or args.tv_show_episode is None
			):
				return HttpCode.UNPROCESSIBLE_ENTITY

			query = cur.execute(
				"SELECT progress_seconds FROM watched_tv_show_episodes WHERE (user_id = %s AND profile_name = %s AND tv_show_id = %s AND season_number = %s AND episode_number = %s)",
				(
					auth.user_id,
					name,
					args.tv_show_id,
					args.tv_show_season,
					args.tv_show_episode,
				),
			).fetchone()
			if query is None:
				return HttpCodeAndJSON(HTTPStatus.OK, {"progress": None})
			progress = query[0]
		elif args.kind == "tv_show_watch_progress":
			if args.movie_id is None:
				return HttpCode.UNPROCESSIBLE_ENTITY

			query = cur.execute(
				"SELECT progress_seconds FROM watched_movies WHERE (user_id = %s AND profile_name = %s AND movie_id = %s)",
				(auth.user_id, name, args.movie_id),
			).fetchone()
			if query is None:
				return HttpCodeAndJSON(HTTPStatus.OK, {"progress": None})
			progress = query[0]

		return HttpCodeAndJSON(HTTPStatus.OK, {"progress": progress})


@bp.put("/<string:name>/progress")
@deserialize(WatchProgressArgs)
@auth()
def set_watch_progress(auth: Auth, name: str, args: WatchProgressArgs):
	if args.progress is None:
		return HttpCode.UNPROCESSIBLE_ENTITY

	with get_db().cursor() as cur:
		if args.kind == "movie_watch_progress":
			if (
				args.tv_show_id is None
				or args.tv_show_season is None
				or args.tv_show_episode is None
			):
				return HttpCode.UNPROCESSIBLE_ENTITY

			cur.execute(
				"UPDATE watched_tv_show_episodes SET progress_seconds = %s WHERE (user_id = %s AND profile_name = %s AND tv_show_id = %s AND season_number = %s AND episode_number = %s)",
				(
					args.progress,
					auth.user_id,
					name,
					args.tv_show_id,
					args.tv_show_season,
					args.tv_show_episode,
				),
			)
		elif args.kind == "tv_show_watch_progress":
			if args.movie_id is None:
				return HttpCode.UNPROCESSIBLE_ENTITY

			cur.execute(
				"UPDATE watched_movies SET progress_seconds = %s WHERE (user_id = %s AND profile_name = %s AND movie_id = %s)",
				(args.progress, auth.user_id, name, args.movie_id),
			)

		return HttpCode.OK
