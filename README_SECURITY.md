# HR Portal Security / API Changes

## Authentication

- Browser pages continue to use Flask's secure HTTP-only session cookie.
- REST APIs use JWT Bearer authentication.
- Access tokens are short-lived (15 minutes).
- Refresh tokens can obtain a new access token through `POST /api/refresh`.
- `POST /api/logout` revokes the current access token for the running application.

## Password security

Passwords are never stored as plain text. Registration uses Werkzeug's password hashing and login uses `check_password_hash()`.

Password requirements:
- minimum 8 characters
- uppercase letter
- lowercase letter
- number
- special character

## Public/private key security

JWTs use **RS256**, an asymmetric RSA signing algorithm.

- `keys/private.pem` signs JWTs and must remain secret.
- `keys/public.pem` verifies JWT signatures.
- If the keys do not exist, `config/jwt_keys.py` generates a new 2048-bit RSA pair automatically.
- The private key is excluded by `.gitignore` and must never be committed.

This is signing/authentication, not password encryption. Passwords should remain hashed.

## REST API examples

### Register

`POST /api/register`

```json
{
  "email": "employee@example.com",
  "password": "SecurePass1!",
  "role": "employee",
  "employee_id": 1
}
```

### Login

`POST /api/login`

```json
{
  "email": "employee@example.com",
  "password": "SecurePass1!"
}
```

The response contains `access_token` and `refresh_token`.

### Authenticated request

```text
Authorization: Bearer <access_token>
```

### Current user

`GET /api/me`

### Refresh

`POST /api/refresh`

Use the refresh token in the Authorization header.

### Logout

`POST /api/logout`

## RBAC matrix

| API operation | HR | Manager | Employee |
|---|---:|---:|---:|
| View employees | Yes | Yes | Own/direct access where applicable |
| Create/update/delete employee | Yes | No | No |
| View attendance | Yes | Yes | Own |
| Mark attendance | Yes | Yes | Own |
| Create/view leave | Yes | Yes | Own |
| Approve/reject leave | Yes | Yes | No |
| View/upload documents | Yes | Yes | Own |

## Important deployment notes

1. Set a strong Flask `SECRET_KEY` in production.
2. Move database credentials into environment variables before deployment.
3. Never commit `keys/private.pem`.
4. Run behind HTTPS in production.
5. For a multi-instance production deployment, store revoked JWT IDs in Redis/database instead of the current in-memory set.
