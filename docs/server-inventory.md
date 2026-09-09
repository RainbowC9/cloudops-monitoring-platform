# CloudOps Server Inventory

## Overview

The CloudOps Server Inventory provides centralized management of infrastructure registered with the platform.

The Server Inventory API supports:

- Server registration
- Server listing
- Server details
- Server updates
- Server deactivation
- Search
- Filtering
- Pagination
- Dashboard summary information
- Role-based access control
- Audit logging

---

## Architecture

```text
Authenticated User
        |
        v
FastAPI Server API
        |
        v
Request Validation
        |
        v
RBAC Authorization
        |
        v
SQLAlchemy
        |
        v
PostgreSQL
```

---

## Server Fields

Each server contains:

```text
id
name
hostname
ip_address
environment
operating_system
status
is_active
created_at
updated_at
```

---

## Environments

Supported environments:

```text
development
staging
production
```

---

## Server Status

Supported status values:

```text
unknown
online
offline
warning
critical
maintenance
```

---

## API Endpoints

### Register Server

```http
POST /api/servers
```

Access:

```text
Admin
Engineer
```

Example:

```json
{
  "name": "PROD-WEB-01",
  "hostname": "prod-web-01.demo.local",
  "ip_address": "192.0.2.10",
  "environment": "production",
  "operating_system": "Ubuntu Linux 24.04",
  "status": "online"
}
```

---

### List Servers

```http
GET /api/servers
```

Access:

```text
Admin
Engineer
Viewer
```

Supported query parameters:

```text
page
page_size
search
environment
status
include_inactive
```

---

### Server Summary

```http
GET /api/servers/summary
```

Provides dashboard-ready inventory totals.

Example:

```json
{
  "total": 3,
  "active": 3,
  "inactive": 0,
  "by_status": {
    "online": 2,
    "warning": 1
  },
  "by_environment": {
    "production": 2,
    "staging": 1
  }
}
```

---

### Server Details

```http
GET /api/servers/{server_id}
```

Access:

```text
Admin
Engineer
Viewer
```

---

### Update Server

```http
PUT /api/servers/{server_id}
```

Access:

```text
Admin
Engineer
```

Only provided fields are updated.

---

### Deactivate Server

```http
PATCH /api/servers/{server_id}/deactivate
```

Access:

```text
Admin
```

CloudOps uses soft deactivation instead of permanently deleting infrastructure records.

This preserves historical relationships with:

```text
alerts
incidents
health checks
audit logs
```

---

## Validation

CloudOps validates server information before persistence.

### IP Addresses

Both IPv4 and IPv6 are supported.

Invalid addresses are rejected.

Example valid address:

```text
192.0.2.10
```

Example invalid address:

```text
999.999.999.999
```

---

## Hostname Validation

Hostnames:

- Are normalized to lowercase
- Cannot contain spaces
- Cannot contain invalid symbols
- Cannot contain empty labels
- Cannot begin or end a label with a hyphen
- Cannot exceed standard hostname lengths

---

## Duplicate Protection

CloudOps prevents duplicate server identity based on:

```text
Server Name
Hostname
```

Duplicate requests return:

```text
HTTP 409 Conflict
```

---

## Pagination

Default pagination:

```text
page=1
page_size=20
```

Maximum page size:

```text
100
```

Response:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0,
  "total_pages": 0
}
```

---

## Search

Server inventory can be searched using:

```text
name
hostname
IP address
```

Example:

```http
GET /api/servers?search=WEB
```

---

## Filtering

Environment:

```http
GET /api/servers?environment=production
```

Status:

```http
GET /api/servers?status=warning
```

Inactive servers:

```http
GET /api/servers?include_inactive=true
```

---

## Role-Based Access

| Operation | Admin | Engineer | Viewer |
|---|---|---|---|
| List servers | Yes | Yes | Yes |
| View server | Yes | Yes | Yes |
| View summary | Yes | Yes | Yes |
| Register server | Yes | Yes | No |
| Update server | Yes | Yes | No |
| Deactivate server | Yes | No | No |

---

## Audit Logging

Server changes generate audit events.

Current actions:

```text
server.created
server.updated
server.deactivated
```

Audit records contain:

```text
user
action
resource
server ID
change details
timestamp
```

---

## Deactivation Strategy

CloudOps intentionally does not permanently delete server records through the API.

Instead:

```text
Active Server
     |
     v
Admin Deactivates
     |
     v
is_active = false
     |
     v
Hidden From Default Inventory
```

Historical operational information is preserved.

---

## Dashboard Integration

The endpoint:

```http
GET /api/servers/summary
```

is designed for future dashboard cards.

Example:

```text
Total Servers        4
Active Servers       3
Inactive Servers     1

Online               2
Warning              1
Critical             0
```

---

## Demo Infrastructure

Public CloudOps demonstrations use fictional infrastructure.

Examples:

```text
PROD-WEB-01
PROD-DB-01
STAGING-01
BACKUP-01
```

Real company infrastructure, private IP information, credentials, and customer data must not be committed to this repository.

---

## Current Status

```text
Server Registration       Implemented
Server Listing            Implemented
Server Details            Implemented
Server Update             Implemented
Server Deactivation       Implemented
IP Validation             Implemented
Hostname Validation       Implemented
Search                    Implemented
Filtering                 Implemented
Pagination                Implemented
Server Summary            Implemented
RBAC                      Implemented
Audit Logging             Implemented
Automated Tests           Implemented
Monitoring Metrics        Planned
```