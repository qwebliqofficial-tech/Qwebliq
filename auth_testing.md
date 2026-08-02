# Qwebliq authentication verification

1. Log in through `POST /api/auth/login` using the administrator in
   `/app/memory/test_credentials.md`.
2. Confirm that `access_token` and `refresh_token` cookies are set and that
   `GET /api/auth/me` returns the authenticated profile.
3. Confirm that `GET /api/admin/overview` is available to the administrator.
4. Confirm that an unauthenticated call to an admin route returns 401.
5. Confirm five failed logins result in a temporary lockout and a successful
   login clears prior attempts.