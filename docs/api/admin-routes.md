This document describes the internal API endpoints for NormFlix. Most of these endpoints use similar API routes to the customer routes for simplicity. However, they require using a bearer token for a NormFlix account; normal users cannot use these APIs.





# `/accounts/*` Endpoints

These endpoints are for account management.





# `/movies/*` Endpoints

For managing movies in NormFlix's library.



## `POST /movies/new`

Add a new movie to the NormFlix library.

### Request Headers

This endpoint requires using a bearer token for authentication, like so:

```
Authorization: Bearer {your_token_goes_here}
```

To use this endpoint, the bearer token must be associated with an account that has `priv_add_media`.

### Request Body

```json
{
	"name": {
		"description": "The name of the movie being added to the library.",
		"type": "string"
	},
	"description": {
		"description": "The description of the movie being added to the library.",
		"type": "string"
	}
}
```

### Response

If the request was successful, the server will respond with `HTTP 200/OK` like so:

```json
{
	"movie_id": {
		"description": "The new UUID for the movie that's been added to the library.",
		"type": "uuid"
	}
}
```

If the bearer token was invalid, or it was for a user account that doesn't have `priv_add_media`, then the server will respond with `HTTP 404/NOT FOUND`. This is an internal API, so it intentionally tries to hide itself when errors happen.
