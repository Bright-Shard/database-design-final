import flask
from pydantic import BaseModel

from src.utils import Blueprint, HttpCode

bp = Blueprint("accounts", __name__, url_prefix="/accounts")


class NewAccountArgs(BaseModel):
	username: str
	password: str
	email: str


@bp.post("/new", deserialize=NewAccountArgs)
def new(args: NewAccountArgs) -> flask.Response:
	return HttpCode.OK
