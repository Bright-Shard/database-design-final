These are features that I would like to implement if I actually ran this service, but didn't have time to before this project was due.

- Ratings for media. Movies, TV shows, and even individual seasons/episodes would each have a rating (stored as a float) between 0 and 5.
- 2FA. It's just good for security.
- Make `/accounts/new` actually validate that the email it receives is an email
- Find a better way to setup the Postgres database user (e.g. prehashed password)
- Actually hash user passwords instead of storing them unencrypted
- Handle users having more profiles than they're allowed to have after downgrading their subscription (e.g. user has 7 profiles on premium, then downgrades to basic)
- Allow deleting accounts
	- Would also need to delete all bearer tokens for the deleted account
