import uuid

from flask import Blueprint
from pydantic.main import BaseModel

from normflix.utils import Auth, HttpCode, HttpCodeAndJSON, auth, deserialize, get_db

bp = Blueprint("movies", __name__, url_prefix="/movies")


class NewMovieArgs(BaseModel):
	name: str
	description: str


@bp.post("/new")
@deserialize(NewMovieArgs)
@auth(error_code=HttpCode(404))
def new(auth: Auth, args: NewMovieArgs):
	with get_db().cursor() as cur:
		query = cur.execute(
			"SELECT priv_add_media FROM users WHERE user_id = %s", (auth.user_id,)
		).fetchone()
		assert query is not None
		if not query[0]:
			# user doesn't have add media permissions
			return HttpCode(404)

		movie_id = uuid.uuid4()
		cur.execute(
			"INSERT INTO movies (movie_id, name, description) VALUES (%s, %s, %s)",
			(movie_id, args.name, args.description),
		)

		return HttpCodeAndJSON(200, {"movie_id": movie_id})
