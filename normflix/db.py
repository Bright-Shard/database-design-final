import subprocess
from typing import Callable

import psycopg

from . import config

try:
	subprocess.run(["podman", "-v"], stdout=subprocess.DEVNULL)
	CONTAINER_RUNTIME = "podman"
except FileNotFoundError:
	CONTAINER_RUNTIME = "docker"


def download_postgres():
	subprocess.run(
		[CONTAINER_RUNTIME, "pull", f"docker.io/postgres:{config.POSTGRES_VERSION}"]
	)


def start_container():
	subprocess.run(
		[
			CONTAINER_RUNTIME,
			"run",
			"--rm",
			"--name",
			config.POSTGRES_CONTAINER_NAME,
			"-p",
			f"{config.DATABASE_PORT}:5432",
			"-e",
			f"POSTGRES_PASSWORD={config.POSTGRES_PASSWORD}",
			"-e",
			f"POSTGRES_USER={config.POSTGRES_USER}",
			"docker.io/postgres",
		],
		stdout=subprocess.DEVNULL,
	)


def stop_container():
	subprocess.run(
		[CONTAINER_RUNTIME, "stop", config.POSTGRES_CONTAINER_NAME],
		stdout=subprocess.DEVNULL,
	)


def container_is_running():
	return (
		subprocess.run(
			[CONTAINER_RUNTIME, "ps", "-a"], stdout=subprocess.PIPE
		).stdout.find(config.POSTGRES_CONTAINER_NAME.encode())
		!= -1
	)


def setup():
	"""
	Connects to the PostgreSQL database and creates the database, tables,
	columns, and constraints used by NormFlix.
	"""
	with psycopg.connect(config.POSTGRES_SETUP_CONN_URL, autocommit=True) as conn:
		conn.execute(f"CREATE DATABASE {config.POSTGRES_DATABASE}")

	with psycopg.connect(config.POSTGRES_RUN_CONN_URL, autocommit=True) as conn:
		# user-related tables
		conn.execute(
			"""
			CREATE TABLE subscriptions (
				name text PRIMARY KEY,
				max_profiles int NOT NULL,
				base_price_dollars float NOT NULL
			)
		"""
		).execute(
			"""
			CREATE TABLE users (
				user_id uuid PRIMARY KEY,
				username text NOT NULL UNIQUE,
				password_hash text NOT NULL,
				email text NOT NULL UNIQUE,
				subscription text REFERENCES subscriptions (name),
				priv_add_media boolean NOT NULL,
				priv_read_user_data boolean NOT NULL,
				priv_write_user_data boolean NOT NULL
			)
			"""
		).execute(
			"""
			CREATE TABLE profiles (
				user_id uuid NOT NULL REFERENCES users (user_id),
				profile_name text NOT NULL UNIQUE,
				active boolean NOT NULL
			)
			"""
		).execute(
			"""
			CREATE TABLE bearer_tokens (
				token uuid PRIMARY KEY,
				user_id uuid NOT NULL REFERENCES users (user_id)
			)
			"""
		)
		# media-related tables
		conn.execute(
			"""
			CREATE TABLE movies (
				movie_id uuid PRIMARY KEY,
				name text NOT NULL,
				description text NOT NULL
			)
			"""
		).execute(
			"""
			CREATE TABLE tv_shows (
				tv_show_id uuid PRIMARY KEY,
				name text NOT NULL,
				description text NOT NULL
			)
			"""
		).execute(
			"""
			CREATE TABLE tv_show_seasons (
				tv_show_id uuid NOT NULL REFERENCES tv_shows (tv_show_id),
				number int NOT NULL,
				name text NOT NULL,
				description text NOT NULL,

				UNIQUE (tv_show_id, number)
			)
			"""
		).execute(
			"""
			CREATE TABLE tv_show_episodes (
				tv_show_id uuid NOT NULL REFERENCES tv_shows (tv_show_id),
				season_number int NOT NULL,
				number int NOT NULL,
				name text NOT NULL,
				description text NOT NULL,

				UNIQUE (tv_show_id, season_number, number),
				FOREIGN KEY (tv_show_id, season_number) REFERENCES tv_show_seasons (tv_show_id, number)
			)
			"""
		)
		# wishlist & history-related tables
		conn.execute(
			"""
			CREATE TABLE watched_movies (
				user_id uuid NOT NULL REFERENCES users (user_id),
				progress_seconds bigint NOT NULL,
				last_watched timestamp NOT NULL,
				movie_id uuid NOT NULL REFERENCES movies (movie_id)
			)
			"""
		).execute(
			"""
			CREATE TABLE watched_tv_show_episodes (
				user_id uuid NOT NULL REFERENCES users (user_id),
				progress_seconds bigint NOT NULL,
				last_watched timestamp NOT NULL,
				tv_show_id uuid NOT NULL REFERENCES tv_shows (tv_show_id),
				season_number int NOT NULL,
				episode_number int NOT NULL,

				FOREIGN KEY (tv_show_id, season_number, episode_number) REFERENCES tv_show_episodes (tv_show_id, season_number, number)
			)
			"""
		)
		# file storage-related tables
		conn.execute(
			"""
			CREATE TYPE media_type AS ENUM ('movie', 'tv_show_episode')
			"""
		).execute(
			"""
			CREATE TABLE movie_files (
				file_id uuid PRIMARY KEY,
				movie_id uuid NOT NULL REFERENCES movies (movie_id),
				resolution text NOT NULL,
				language text NOT NULL,
				file_path text NOT NULL UNIQUE
			)
			"""
		).execute(
			"""
			CREATE TABLE tv_show_episode_files (
				file_id uuid PRIMARY KEY,
				tv_show_id uuid NOT NULL REFERENCES tv_shows (tv_show_id),
				season_number int NOT NULL,
				episode_number int NOT NULL,
				resolution text NOT NULL,
				language text NOT NULL,
				file_path text NOT NULL UNIQUE,

				FOREIGN KEY (tv_show_id, season_number, episode_number) REFERENCES tv_show_episodes (tv_show_id, season_number, number)
			)
			"""
		)


def reset():
	"""
	Deletes the database NormFlix uses.
	"""
	with psycopg.connect(config.POSTGRES_SETUP_CONN_URL, autocommit=True) as conn:
		conn.execute(f"DROP DATABASE {config.POSTGRES_DATABASE}")


def with_db(func: Callable[[psycopg.Connection], None]) -> Callable[[], None]:
	def wrapped():
		with psycopg.connect(config.POSTGRES_RUN_CONN_URL, autocommit=True) as conn:
			func(conn)

	return wrapped
