# CloudOps Health Check Engine

## Overview

The CloudOps Health Check Engine monitors registered services and records their availability and response time.

Current monitoring types:

```text
HTTP
TCP
```

Health-check results are persisted in PostgreSQL.

---

## Architecture

```text
Registered Server
       |
       v
Registered Service
       |
       +----------------------+
       |                      |
       v                      v
 HTTP Service            TCP Service
       |                      |
       v                      v
 HTTP Request            TCP Connection
       |                      |
       +----------+-----------+
                  |
                  v
          Health Check Result
                  |
          +-------+-------+
          |               |
          v               v
       Healthy         Unhealthy
          |               |
          +-------+-------+
                  |
                  v
            PostgreSQL
```

---

## Service Types

### HTTP

HTTP monitoring checks:

```text
Target resolution
HTTP connectivity
HTTP status code
Response latency
```

Example:

```text
http://127.0.0.1:8001/health
```

HTTP responses from `200` through `399` are considered healthy.

---

### TCP

TCP monitoring checks whether CloudOps can establish a connection to a configured host and port.

Example:

```text
Host:
127.0.0.1

Port:
8001
```

---

## Service Status

Services use:

```text
unknown
healthy
unhealthy
```

New services begin as:

```text
unknown
```

After a health check, CloudOps updates the service status with the latest result.

---

## Service API

```text
POST  /api/services

GET   /api/services

GET   /api/services/{service_id}

PUT   /api/services/{service_id}

PATCH /api/services/{service_id}/deactivate
```

---

## Health Check API

### Run Health Check

```http
POST /api/health-checks/services/{service_id}/run
```

Access:

```text
Admin
Engineer
```

---

### Health Check History

```http
GET /api/health-checks
```

Supported filters:

```text
server_id
service_id
check_type
status
page
page_size
```

---

### Latest Service Health

```http
GET /api/health-checks/services/{service_id}/latest
```

Returns the newest recorded result for the selected service.

---

### Monitoring Summary

```http
GET /api/health-checks/summary
```

Example:

```json
{
  "total_checks": 3,
  "healthy_checks": 2,
  "unhealthy_checks": 1,
  "monitored_services": 3,
  "by_type": {
    "http": 1,
    "tcp": 2
  }
}
```

---

## Persistence

Health check results are stored in:

```text
health_checks
```

The service's latest status is also stored in:

```text
services.status
```

Flow:

```text
Run Check
   |
   v
Check Result
   |
   +-------> health_checks
   |
   `-------> services.status
```

---

## Audit Logging

Manual health-check executions generate:

```text
health_check.executed
```

Service management actions include:

```text
service.created
service.updated
service.deactivated
```

---

## RBAC

| Operation | Admin | Engineer | Viewer |
|---|---|---|---|
| View services | Yes | Yes | Yes |
| View health checks | Yes | Yes | Yes |
| View monitoring summary | Yes | Yes | Yes |
| Register service | Yes | Yes | No |
| Update service | Yes | Yes | No |
| Run health check | Yes | Yes | No |
| Deactivate service | Yes | No | No |

---

## Monitoring Safety

Health checks should only target infrastructure that the operator owns or is authorized to monitor.

CloudOps rejects several inappropriate network target categories such as unspecified, multicast, reserved, and link-local addresses.

Loopback addresses are allowed for local development.

---

## Current Status

```text
Service Inventory          Implemented
HTTP Monitoring            Implemented
TCP Monitoring             Implemented
Response-Time Tracking     Implemented
Health History             Implemented
Latest Health Result       Implemented
Monitoring Summary         Implemented
Status Synchronization     Implemented
Audit Logging              Implemented
RBAC                       Implemented
Automated Tests            Implemented

Scheduled Monitoring       Planned
Prometheus Integration     Planned
Node Exporter              Planned
Alert Automation           Planned
```