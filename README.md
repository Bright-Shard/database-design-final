# NormFlix

This is the source code for the final project of my database design class. For the sake of building my resume, I'm also putting this code on GitHub - but it's just my submission for my final project, this isn't the same as a personal project that I plan on maintaining and completing.

The final project was basically just to create the backend database and API for the fake, definitely-not-a-Netflix-clone company NormFlix. We had to use either PostgreSQL or MongoDB for the database, and had to make the API in Python with Flask.



# Features

Loosely speaking, the final project has to be able to:
- Handle user authentication
- Let accounts use one of the available subscription plans (basic, standard, or premium)
- Store multiple profiles for every account (so different people can each have their own profile under one account)
	- Each profile has a watch history that stores the exact time a user stopped watching
	- Each profile has a "wishlist" of movies/shows they want to watch
	- Profiles have a "continue watching" button that lets them keep watching the last movie/TV show they were just watching, and pick up right where they left off
	- The number of profiles one account can have depends on which subscription plan the account is paying for
- The backend can store both movies and TV shows
	- TV shows have seasons, and seasons have episodes
	- Each episode/movie can have multiple media files that can be streamed (different files can be used for e.g. different languages, or watching at 1080p vs 4k)



# Project Layout

- [`docs/`](./docs) has the documentation for the API and database structure.
- [`tests/`](./tests) has tests to verify the API works as intended.
- [`normflix/`](./normflix) contains the actual source code for the API.
- [`bin/`](./bin) contains binaries for running the API, starting the database, etc.



# Running NormFlix

The scripts in [`bin/`](./bin) are for running NormFlix.

For running NormFlix from one file, you can run `run.py`.

For local development, I recommend using the `setup_db.py`, `start_api.py`, and `start_db.py` files instead. When you change code, you usually only have to restart one of those files, which means faster startup times, which means faster iteration speed.



# Tests

You can run all tests by running the [`tests/utils.py`](./tests/utils.py) file.



# Dependencies

If you use Nix, the included [Nix shell](./shell.nix) will install everything for you.

NormFlix needs:
- Python 3 (tested with 3.13)
- Docker or Podman
- The following Python libraries (can install with Pip):
	- `flask`
	- `psycopg[binary]` 
	- `pydantic`

The API server is implemented in Python with Flask, and uses psycopg to talk to a PostgreSQL database. That database runs in a container, using either Docker or Podman.

To serve the API and database, NormFlix will bind to the ports specified in [`normflix/config.py`](./normflix/config.py).
