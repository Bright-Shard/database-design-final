This document describes the customer API endpoints for NormFlix.





# `/accounts/*` Endpoints

These endpoints are for account management.



## `POST /accounts/new`

Create a new NormFlix account.

### Request Headers

No headers are necessary for this endpoint.

### Request Body

```json
{
	"username": {
		"description": "The username for the new account.",
		"type": "string"
	},
	"password": {
		"description": "The password for the new account. The password can be transmitted in plaintext; in prod, this will be protected by HTTPS, and the server hashes the password as soon as it receives it.",
		"type": "string"
	},
	"email": {
		"description": "An email address that can be used to contact the owner of this account.",
		"type": "email"
	}
}
```

### Response

If the request is successful, the server will respond with `HTTP 200/OK`. If the username or email for the account is already used, the server will respond with `HTTP 409/CONFLICT` instead.



## `POST /accounts/token`

Login to an account and create a new bearer token for that account. That bearer token can then be used for authentication with any other API endpoints that need it.

### Request Headers

No headers are necessary for this endpoint.

### Request Body

```json
{
	"username": {
		"description": "The username of the account to login to & generate a new API key for.",
		"type": "string"
	},
	"password": {
		"description": "The user's password to authenticate with.",
		"type": "string"
	}
}
```

### Response

If the request is successful, the server will respond with `HTTP 200/OK`, with this body:

```json
{
	"bearer_token": {
		"description": "The new bearer token for the account.",
		"type": "string"
	}
}
```

If the request used bad credentials, the server will respond with `HTTP 401/UNAUTHORIZED`.



## `PUT /accounts/subscription`

Change which subscription the account uses. To cancel the subscription, see `DELETE /accounts/subscription`.

### Request Headers

This endpoint requires using a bearer token for authentication, like so:

```
Authorization: Bearer {your_token_goes_here}
```

### Request Body

```json
{
	"subscription": {
		"description": "The name of the subscription plan the account is switching to.",
		"enum": ["basic", "standard", "premium"]
	}
}
```

### Response

The server will respond with `HTTP 200/OK` if changing subscriptions succeeded. If the bearer token was invalid, the server will respond with `HTTP 403/FORBIDDEN`.



## `DELETE /accounts/subscription`

Cancel the account's subscription. The user will lose access to their NormFlix content, but their account still exists, so they can re-activate their subscription at any time.

### Request Headers

This endpoint requires using a bearer token for authentication, like so:

```
Authorization: Bearer {your_token_goes_here}
```

### Request Body

No body is needed for this request.

### Response

The server will respond with `HTTP 200/OK` if cancelling the subscription succeeded. If the bearer token was invalid, the server will respond with `HTTP 403/FORBIDDEN`.



## `PUT /accounts/email`

Change the email associated with a specific account.

### Request Headers

This endpoint requires using a bearer token for authentication, like so:

```
Authorization: Bearer {your_token_goes_here}
```

### Request Body

```json
{
	"email": {
		"description": "The new email to use for this account.",
		"type": "email"
	}
}
```

### Response

The server will respond with `HTTP 200/OK` if changing the email succeeded. If the bearer token was invalid, the server will respond with `HTTP 403/FORBIDDEN`.



## `PUT /accounts/password`

Change the password associated with a specific account.

### Request Headers

This endpoint requires using a bearer token for authentication, like so:

```
Authorization: Bearer {your_token_goes_here}
```

### Request Body

```json
{
	"password": {
		"description": "The new password to use for this account.",
		"type": "string"
	}
}
```

### Response

The server will respond with `HTTP 200/OK` if changing the password succeeded. If the bearer token was invalid, the server will respond with `HTTP 403/FORBIDDEN`.





# `/profiles/<name>/*` Endpoints

These API endpoints are for getting the data of one specific profile from a user's account.



## `POST /profiles/<name>/new`

This endpoint allows a user to create a new profile on their account.

### Request Headers

This endpoint requires using a bearer token for authentication, like so:

```
Authorization: Bearer {your_token_goes_here}
```

### Request Body

This endpoint doesn't need a body.

### Response

The server will reply with `HTTP 200/OK` if the request succeeds. If the user cannot add any more profiles to their account (because they're at the max for their subscription plan), the server will reply with `HTTP 426/UPGRADE REQUIRED`. If there's already a profile on this account with the same name, the server will reply with `HTTP 409/CONFLICT`. If the bearer token was invalid, the server will respond with `HTTP 403/FORBIDDEN`.



## `DELETE /profiles/<name>`

This endpoint allows a user to delete a profile from their account.

### Request Headers

This endpoint requires using a bearer token for authentication, like so:

```
Authorization: Bearer {your_token_goes_here}
```

### Request Body

This endpoint doesn't need a body.

### Response

The server will reply with `HTTP 200/OK` if the request succeeds. If the bearer token was invalid, the server will respond with `HTTP 403/FORBIDDEN`.



## `PUT /profiles/<name>/name`

This endpoint lets a user change the name for a profile on their account.

### Request Headers

This endpoint requires using a bearer token for authentication, like so:

```
Authorization: Bearer {your_token_goes_here}
```

### Request Body

```json
{
	"name": {
		"description": "The new name to give the profile.",
		"type": "string"
	}
}
```

### Response

The server will reply with `HTTP 200/OK` if the request succeeds. If the bearer token was invalid, the server will respond with `HTTP 403/FORBIDDEN`.



## `GET /profiles/<name>/progress`

Get the watch progress for a profile on a particular piece of media.

### Request Headers

This endpoint requires using a bearer token for authentication, like so:

```
Authorization: Bearer {your_token_goes_here}
```

### Request Body

```json
{
	"kind": {
		"description": "Which type of watch progress you want to get. `movie_watch_progress` gets the profile's watch progress through a particular movie. `tv_show_watch_progress` gets the profile's watch progress through a particular TV show episode.",
		"enum": ["movie_watch_progress", "tv_show_watch_progress"]
	},
	"movie_id": {
		"description": "The ID of the movie to get the watch progress of. Only necessary for requests where `kind = movie_watch_progress`.",
		"type": "uuid",
		"optional": true
	},
	"tv_show_id": {
		"description": "The ID of the TV show that has the episode to get the watch progress of. Only necessary for requests where `kind = tv_show_watch_progress`.",
		"type": "uuid",
		"optional": true
	},
	"tv_show_season": {
		"description": "The number of the TV show season that has the episode to get the watch progress of. Only necessary for requests where `kind = tv_show_watch_progress`.",
		"type": "number",
		"optional": true
	},
	"tv_show_episode": {
		"description": "The number of the TV show episode to get the watch progress of. Only necessary for requests where `kind = tv_show_watch_progress`.",
		"type": "number",
		"optional": true
	},
}
```

### Response

If the request was successful, the server will reply with `HTTP 200/OK` with the following content:

```json
{
	"progress": {
		"description": "How far the profile made it into the requested piece of media, in seconds. Will be set to null if the profile hasn't started watching this media.",
		"type": "number"
	}
}
```

If the bearer token was invalid, the server will respond with `HTTP 403/FORBIDDEN`.



## `POST /profiles/<name>/progress` & `PUT /profiles/<name>/progress`

Create or update the watch progress for a profile on a particular piece of media.

Both of these HTTP methods take the same arguments and have similar responses, but they do different things. The `POST` request creates the initial watch progress data, and `PUT` later updates it. Trying to send a `PUT` request to update watch progress without first sending the `POST` request is an error.

### Request Headers

This endpoint requires using a bearer token for authentication, like so:

```
Authorization: Bearer {your_token_goes_here}
```

### Request Body

```json
{
	"kind": {
		"description": "Which type of watch progress you want to set. `movie_watch_progress` sets the profile's watch progress through a particular movie. `tv_show_watch_progress` sets the profile's watch progress through a particular TV show episode.",
		"enum": ["movie_watch_progress", "tv_show_watch_progress"]
	},
	"movie_id": {
		"description": "The ID of the movie to get the watch progress of. Only necessary for requests where `kind = movie_watch_progress`.",
		"type": "uuid",
		"optional": true
	},
	"tv_show_id": {
		"description": "The ID of the TV show that has the episode to get the watch progress of. Only necessary for requests where `kind = tv_show_watch_progress`.",
		"type": "uuid",
		"optional": true
	},
	"tv_show_season": {
		"description": "The number of the TV show season that has the episode to get the watch progress of. Only necessary for requests where `kind = tv_show_watch_progress`.",
		"type": "number",
		"optional": true
	},
	"tv_show_episode": {
		"description": "The number of the TV show episode to get the watch progress of. Only necessary for requests where `kind = tv_show_watch_progress`.",
		"type": "number",
		"optional": true
	},
	"progress": {
		"description": "How much of the piece of media that this profile has watched, in seconds.",
		"type": "number"
	}
}
```

### Response

If the request was successful, the server will reply with `HTTP 200/OK`. If the bearer token was invalid, the server will respond with `HTTP 403/FORBIDDEN`.





# `/movies/*` Endpoints

These API endpoints are for browsing the movie catalog and streaming movies.





# `/shows/*` Endpoints

These API endpoints are for browsing the TV shows on NormFlix and streaming episodes from them.
