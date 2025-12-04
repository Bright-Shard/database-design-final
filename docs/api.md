The NormFlix API is broken into two parts:
- The [customer API](./api/customer-routes.md), which is intended for public use
- The [admin API](./api/admin-routes.md), which is intended for internal NormFlix usage.

All API endpoints follow a few common rules:
- Data is always transmitted in JSON. Requests send data with JSON, the server responds in JSON.
- `GET` is used to get data from the server, `POST` is used to create new data, `PUT` is used to update data, `DELETE` is used to delete data.
- The API uses `snake_case` naming.
- Endpoints always use plural words (e.g. `/accounts`, `/profiles`, `/movies`) so they're a little easier to remember.
- Each endpoint defines its request and response JSON using something like JSON schema. All fields are required unless the field has `"optional": true`. If an API request is missing any fields, the server replies with an error message that tells the user which fields they're missing (this is powered by the Pydantic library).
- In these docs, API routes use `<variable>` for templating. For example, for the API route `GET /profile/<name>`, you'd call `GET /profile/Mom` to get the profile for "Mom".
