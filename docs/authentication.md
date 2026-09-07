# CloudOps Authentication

## Overview

CloudOps uses token-based authentication to protect application resources.

Authentication is implemented using:

```text
Username / Email
       |
       v
Password Verification
       |
       v
JWT Access Token
       |
       v
Authenticated API Request
       |
       v
Role-Based Authorization
```

---

## Password Security

CloudOps does not store plaintext passwords.

Passwords are hashed before being stored in PostgreSQL.

Current password flow:

```text
Plaintext Password
       |
       v
Argon2 Password Hash
       |
       v
PostgreSQL
```

The stored value is placed in:

```text
users.password_hash
```

The original password cannot be recovered from the stored hash.

---

## JWT Authentication

Successful login returns a JSON Web Token.

Endpoint:

```http
POST /api/auth/login
```

Example response:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer",
  "expires_in": 1800
}
```

The token contains the authenticated user ID in the JWT subject claim.

Tokens have a limited lifetime.

Current development configuration:

```text
Algorithm:
HS256

Access Token Lifetime:
30 minutes
```

---

## Secret Key

JWT tokens are signed using the application `SECRET_KEY`.

The real secret is stored only inside:

```text
.env
```

The repository provides only a safe placeholder inside:

```text
.env.example
```

The production secret must never be committed to source control.

---

## Authentication Flow

```text
Client
   |
   | username + password
   v
POST /api/auth/login
   |
   v
Find User
   |
   v
Verify Password
   |
   +---------------------+
   |                     |
Invalid                Valid
   |                     |
   v                     v
401 Unauthorized     Create JWT
                         |
                         v
                    Access Token
                         |
                         v
                 Authenticated Request
                         |
                         v
                    Decode JWT
                         |
                         v
                     Load User
```

---

## Current User

Endpoint:

```http
GET /api/auth/me
```

Requires:

```text
Bearer JWT
```

Example response:

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.test",
  "role": "Admin",
  "is_active": true
}
```

Passwords and password hashes are never included in API responses.

---

## Role-Based Access Control

CloudOps currently defines three roles:

```text
Admin
Engineer
Viewer
```

Permission hierarchy:

```text
Admin
|
|-- Admin Resources
|-- Engineer Resources
`-- Viewer Resources


Engineer
|
|-- Engineer Resources
`-- Viewer Resources


Viewer
|
`-- Viewer Resources
```

---

## Admin

Admin users can access:

```text
Admin
Engineer
Viewer
```

permission levels.

---

## Engineer

Engineer users can access:

```text
Engineer
Viewer
```

permission levels.

---

## Viewer

Viewer users receive read-oriented access.

---

## Current Authentication Endpoints

```text
POST /api/auth/login

GET /api/auth/me

GET /api/auth/access/viewer

GET /api/auth/access/engineer

GET /api/auth/access/admin
```

---

## HTTP Authentication Responses

### 401 Unauthorized

Returned when authentication credentials are missing or invalid.

Example:

```text
Invalid JWT
Expired JWT
Incorrect username
Incorrect password
```

### 403 Forbidden

Returned when authentication succeeds but the user does not have sufficient permissions.

Example:

```text
Viewer attempts to access an Admin resource
```

---

## Initial Admin

The first CloudOps administrator is created using:

```text
scripts/seed_admin.py
```

Run:

```bash
python -m scripts.seed_admin
```

The administrator password is requested interactively and is never stored inside the repository.

---

## Security Principles

CloudOps authentication follows these principles:

- Never store plaintext passwords
- Never expose password hashes through APIs
- Never commit JWT secrets
- Use short-lived access tokens
- Require authentication for protected resources
- Apply authorization separately from authentication
- Use dedicated application database accounts
- Disable inactive users
- Use HTTPS in production

---

## Current Authentication Status

```text
Password Hashing          Implemented
Argon2                    Implemented
JWT Access Tokens         Implemented
Login Endpoint            Implemented
Current User Endpoint     Implemented
RBAC                      Implemented
Admin Role                Implemented
Engineer Role             Implemented
Viewer Role               Implemented
Initial Admin Seed        Implemented
Authentication Tests      Implemented
HTTPS                     Planned
Refresh Tokens            Future Enhancement
```