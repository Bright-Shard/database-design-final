import subprocess

import psycopg

from . import config

try:
	subprocess.run(["podman", "-v"], stdout=subprocess.DEVNULL)
	CONTAINER_RUNTIME = "podman"
except FileNotFoundError:
	CONTAINER_RUNTIME = "docker"


def download_postgres():
	subprocess.run([CONTAINER_RUNTIME, "pull", "docker.io/postgres"])


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
	with psycopg.connect(config.POSTGRES_SETUP_CONN_URL, autocommit=True) as conn:
		conn.execute(f"CREATE DATABASE {config.POSTGRES_DATABASE}")
