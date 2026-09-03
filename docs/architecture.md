# CloudOps Architecture

## Overview

CloudOps is a cloud infrastructure monitoring and incident management platform designed to provide centralized visibility into server health, application availability, alerts, and operational incidents.

The project follows a modular architecture so that monitoring, incident management, database operations, notifications, and deployment components can evolve independently.

The initial implementation uses FastAPI as the backend application framework, PostgreSQL as the application database, Prometheus for infrastructure metrics, Node Exporter for Linux system metrics, Nginx as the reverse proxy, and Docker for deployment.

---

## High-Level Architecture

```text
                                Internet
                                   |
                                   |
                                 HTTPS
                                   |
                                   v
                              +----------+
                              |  Nginx   |
                              | Reverse  |
                              |  Proxy   |
                              +----+-----+
                                   |
                                   |
                                   v
                            +--------------+
                            |   FastAPI    |
                            | CloudOps API |
                            +------+-------+
                                   |
             +---------------------+----------------------+
             |                     |                      |
             |                     |                      |
             v                     v                      v
      +--------------+      +-------------+        +-------------+
      | PostgreSQL   |      | Prometheus  |        | Alert Engine|
      | Application  |      | Monitoring  |        |             |
      | Database     |      |             |        +------+------+ 
      +--------------+      +------+------+               |
                                   |                      |
                                   |                      v
                                   |               +--------------+
                                   |               | Notification |
                                   |               |   Service    |
                                   |               +------+-------+
                                   |                      |
                                   v                      |
                            +--------------+              |
                            |Node Exporter |              |
                            +------+-------+              |
                                   |                      |
                                   v                      v
                            +--------------+       +-------------+
                            | Linux Server |       | Discord /   |
                            | Infrastructure|      | Email       |
                            +--------------+       +-------------+
```

---

## Main Components

## 1. FastAPI Application

FastAPI is the main backend application for CloudOps.

It is responsible for:

* Exposing REST API endpoints
* User authentication
* Role-based access control
* Server inventory management
* Monitoring configuration
* Health check processing
* Incident management
* Alert rule management
* Incident timeline management
* Notification integration
* Database operations
* Application health endpoints

The FastAPI application acts as the main interface between users, the application database, monitoring services, and external notification systems.

---

## 2. PostgreSQL Database

PostgreSQL is used as the primary application database.

It stores structured CloudOps application data.

Planned data includes:

* Users
* Roles
* Servers
* Services
* Health checks
* Incidents
* Incident events
* Alert rules
* Alerts
* Audit logs

Prometheus metrics are not intended to be stored directly inside PostgreSQL.

PostgreSQL is primarily responsible for application and operational records.

---

## 3. SQLAlchemy

SQLAlchemy will be used as the Object Relational Mapper between FastAPI and PostgreSQL.

Responsibilities include:

* Database connections
* Defining database models
* Querying application data
* Creating records
* Updating records
* Managing relationships between tables

Example flow:

```text
FastAPI Endpoint
       |
       v
SQLAlchemy Model
       |
       v
PostgreSQL
```

---

## 4. Alembic

Alembic will manage database schema migrations.

Instead of manually modifying the production database, database changes will be stored as migration files.

Example:

```text
Application Model Updated
          |
          v
Generate Migration
          |
          v
Review Migration
          |
          v
Apply Migration
          |
          v
Database Updated
```

This provides a traceable database change history.

---

## 5. Prometheus

Prometheus is responsible for infrastructure monitoring.

Prometheus will collect time-series metrics from monitored systems.

Metrics may include:

* CPU usage
* Memory usage
* Disk availability
* Load average
* Network statistics
* Filesystem information
* System uptime
* Infrastructure availability

Prometheus will periodically scrape configured monitoring endpoints.

Architecture:

```text
Linux Server
     |
     v
Node Exporter
     |
     v
Prometheus
     |
     v
CloudOps
```

---

## 6. Node Exporter

Node Exporter exposes operating system and hardware metrics from Linux hosts.

Each monitored Linux server can run Node Exporter.

Metrics exposed by Node Exporter may include:

* CPU usage
* Memory statistics
* Filesystem usage
* Disk statistics
* Network statistics
* Load average
* System uptime

Example:

```text
PROD-WEB-01
     |
     | system metrics
     v
Node Exporter
     |
     | HTTP metrics endpoint
     v
Prometheus
```

---

## 7. Monitoring Engine

CloudOps will contain an application-level monitoring engine.

This component is responsible for checks that are not necessarily handled directly through Node Exporter.

Examples include:

* HTTP endpoint availability
* API health checks
* Website status checks
* HTTP response times
* Database connectivity
* Application service availability

Example health check:

```text
CloudOps
   |
   | HTTP request
   v
https://example.com/health
   |
   v
HTTP 200
   |
   v
Healthy
```

If the check fails:

```text
HTTP Check
   |
   v
Timeout / Error
   |
   v
Alert Evaluation
   |
   v
Incident
```

---

## 8. Alert Engine

The alert engine evaluates monitoring data against configured thresholds.

Example threshold configuration:

```text
CPU Warning:      70%
CPU Critical:     90%

Memory Warning:   75%
Memory Critical:  90%

Disk Warning:     80%
Disk Critical:    95%
```

Example alert flow:

```text
Prometheus Metric
       |
       v
CPU = 94%
       |
       v
Alert Engine
       |
       v
Critical Threshold Exceeded
       |
       v
Check Existing Alert
       |
       +-------------------+
       |                   |
      Yes                  No
       |                   |
       v                   v
Update Existing       Create Alert
       |                   |
       +---------+---------+
                 |
                 v
         Incident Evaluation
```

---

## 9. Incident Management

CloudOps will manage operational incidents caused by infrastructure, application, or service problems.

Each incident may include:

* Incident number
* Title
* Description
* Severity
* Status
* Related server
* Related alert
* Assigned engineer
* Created timestamp
* Acknowledged timestamp
* Resolved timestamp
* Closed timestamp

Example:

```text
INC-2026-0001

Title:
Critical CPU Usage

Server:
PROD-WEB-01

Severity:
P1 - Critical

Status:
Investigating
```

---

## 10. Incident Lifecycle

The planned incident lifecycle is:

```text
OPEN
  |
  v
ACKNOWLEDGED
  |
  v
INVESTIGATING
  |
  v
RESOLVED
  |
  v
CLOSED
```

Not every system event necessarily has to move through every state automatically.

Engineers will be able to manage incident status through the CloudOps application.

---

## 11. Incident Timeline

CloudOps will maintain an event history for each incident.

Example:

```text
14:32 Incident Created

14:35 Incident Acknowledged

14:38 Assigned to Engineer

14:41 Investigation Started

14:55 CPU usage returned to normal

15:02 Incident Resolved

15:10 Incident Closed
```

Instead of overwriting the history, each important event will be stored separately.

Planned database table:

```text
incident_events

id
incident_id
event_type
description
created_by
created_at
```

This provides a complete operational audit trail.

---

## 12. Incident Deduplication

Monitoring systems may detect the same problem repeatedly.

For example:

```text
14:30 CPU 94%
14:31 CPU 95%
14:32 CPU 93%
14:33 CPU 96%
```

CloudOps should not create four separate incidents for the same active CPU problem.

Planned logic:

```text
Threshold Exceeded
        |
        v
Search Active Incidents
        |
        v
Same Server + Same Alert Type?
        |
       / \
     Yes  No
      |    |
      v    v
 Update   Create
Existing   New
Incident Incident
```

This prevents alert and incident duplication.

---

## 13. Notification Service

CloudOps will support external notifications.

Initial planned integration:

* Discord webhook

Future integrations may include:

* Email
* Slack
* Microsoft Teams

Example:

```text
Critical Alert
      |
      v
Incident Created
      |
      v
Notification Service
      |
      v
Discord Webhook
```

Example notification:

```text
CLOUDOPS ALERT

Severity:
P1 Critical

Server:
PROD-WEB-01

Issue:
CPU Usage Critical

Current:
94%

Threshold:
90%

Incident:
INC-2026-0001
```

---

## 14. Nginx

Nginx will act as the public reverse proxy for CloudOps.

Instead of exposing FastAPI directly to the internet:

```text
Internet
   |
   v
Nginx
   |
   v
FastAPI
```

Nginx responsibilities include:

* Reverse proxy
* HTTPS termination
* Routing requests to FastAPI
* Managing public HTTP connections
* Redirecting HTTP traffic to HTTPS
* Supporting production deployment

---

## 15. HTTPS

The production application will use HTTPS.

Planned flow:

```text
Browser
   |
   | HTTPS
   v
Nginx
   |
   | Internal HTTP
   v
FastAPI
```

SSL/TLS certificates will be configured during the production deployment phase.

---

## 16. Docker

Docker will containerize the CloudOps application and related services.

The planned Docker environment includes:

```text
Docker Compose
|
|-- cloudops-api
|     FastAPI
|
|-- cloudops-db
|     PostgreSQL
|
|-- prometheus
|
|-- node-exporter
|
`-- nginx
```

Benefits include:

* Consistent environments
* Easier deployment
* Service isolation
* Simplified dependency management
* Easier local development
* Easier production setup

---

## 17. Docker Compose

Docker Compose will define the CloudOps multi-container environment.

Planned services:

```text
services:

cloudops-api
cloudops-db
prometheus
node-exporter
nginx
```

Development and production configurations may be separated.

Example:

```text
compose.yaml
compose.production.yaml
```

---

## 18. GitHub Actions

GitHub Actions will be used for Continuous Integration and Continuous Deployment.

Planned CI/CD workflow:

```text
Developer
    |
    | git push
    v
GitHub
    |
    v
GitHub Actions
    |
    |-- Install dependencies
    |
    |-- Run linting
    |
    |-- Run automated tests
    |
    |-- Build Docker image
    |
    `-- Deploy
             |
             v
        Linux Server
```

CI/CD will be implemented after the core application becomes stable.

---

## 19. Application Health Endpoint

CloudOps provides a health endpoint.

Current endpoint:

```http
GET /health
```

Current response:

```json
{
  "status": "healthy"
}
```

The endpoint will later provide additional checks.

Example future response:

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

This endpoint can be used by:

* Monitoring systems
* Docker health checks
* Load balancers
* Deployment validation
* External uptime checks

---

## 20. Planned Database Architecture

The initial database design includes:

```text
users
roles

servers
services

health_checks

incidents
incident_events

alert_rules
alerts

audit_logs
```

High-level relationship:

```text
                   User
                    |
                    |
                Assigned To
                    |
                    v
                  Incident
                 /        \
                /          \
               v            v
          Incident       Alert
           Events          |
                           |
                           v
                         Server
                         /    \
                        /      \
                       v        v
                 Health Check Service
```

---

## 21. Server Entity

The `servers` table will represent infrastructure monitored by CloudOps.

Planned fields:

```text
servers

id
name
hostname
ip_address
environment
operating_system
status
created_at
updated_at
```

Example:

```text
Name:
PROD-WEB-01

Hostname:
prod-web-01

Environment:
Production

Operating System:
Ubuntu Linux

Status:
Online
```

---

## 22. Health Check Entity

Planned fields:

```text
health_checks

id
server_id
check_type
status
response_time
checked_at
details
```

Possible check types:

```text
HTTP
API
DATABASE
SERVER
SERVICE
```

---

## 23. Alert Rules Entity

Planned fields:

```text
alert_rules

id
server_id
metric
warning_threshold
critical_threshold
enabled
created_at
updated_at
```

Example:

```text
Metric:
CPU

Warning:
70

Critical:
90

Enabled:
true
```

---

## 24. Alerts Entity

Planned fields:

```text
alerts

id
server_id
alert_rule_id
metric
value
severity
status
triggered_at
resolved_at
```

Possible status values:

```text
ACTIVE
ACKNOWLEDGED
RESOLVED
```

---

## 25. Incidents Entity

Planned fields:

```text
incidents

id
incident_number
server_id
alert_id
title
description
severity
status
assigned_to
created_at
acknowledged_at
resolved_at
closed_at
```

---

## 26. Incident Events Entity

Planned fields:

```text
incident_events

id
incident_id
event_type
description
created_by
created_at
```

---

## 27. Audit Logs

Security-sensitive and administrative actions may be recorded in an audit log.

Examples:

* User created
* User role changed
* Server registered
* Server deleted
* Alert rule modified
* Incident assigned
* Incident closed

Planned fields:

```text
audit_logs

id
user_id
action
resource_type
resource_id
details
created_at
```

---

## 28. Authentication Architecture

Authentication will be added in a later development phase.

Planned user roles:

```text
Admin
Engineer
Viewer
```

High-level permissions:

```text
Admin
|
|-- Manage users
|-- Manage servers
|-- Manage alert rules
|-- Manage incidents
`-- View monitoring


Engineer
|
|-- View servers
|-- View monitoring
|-- Acknowledge alerts
|-- Manage incidents
`-- Resolve incidents


Viewer
|
|-- View servers
|-- View monitoring
`-- View incidents
```

---

## 29. REST API Architecture

FastAPI routers will separate application responsibilities.

Planned layout:

```text
app/
|
|-- routers/
|     |
|     |-- auth.py
|     |-- servers.py
|     |-- monitoring.py
|     |-- incidents.py
|     `-- alerts.py
|
|-- models/
|
|-- schemas/
|
|-- services/
|
|-- database.py
|
`-- main.py
```

This keeps endpoint routing separate from business logic.

---

## 30. Service Layer

Business logic will be placed under:

```text
app/services/
```

Planned service modules:

```text
monitoring.py
prometheus.py
alerts.py
notifications.py
```

Responsibilities:

### monitoring.py

* HTTP health checks
* Service availability
* Health status evaluation

### prometheus.py

* Query Prometheus
* Retrieve infrastructure metrics
* Normalize monitoring data

### alerts.py

* Evaluate thresholds
* Generate alerts
* Resolve alerts
* Trigger incidents

### notifications.py

* Send Discord notifications
* Handle future notification integrations

---

## 31. Request Flow

Example request for server details:

```text
Browser
   |
   v
Nginx
   |
   v
FastAPI Router
   |
   v
Service Layer
   |
   v
SQLAlchemy
   |
   v
PostgreSQL
   |
   v
FastAPI Response
   |
   v
Browser
```

---

## 32. Monitoring Data Flow

```text
Linux Server
     |
     v
Node Exporter
     |
     v
Prometheus
     |
     v
CloudOps Monitoring Service
     |
     +--------------------+
     |                    |
     v                    v
Dashboard            Alert Engine
                          |
                          v
                       Incident
                          |
                          v
                    Notification
```

---

## 33. Application Monitoring Flow

```text
CloudOps Monitoring Engine
           |
           v
      HTTP Request
           |
           v
     Target Service
           |
      +----+----+
      |         |
   Success     Failure
      |         |
      v         v
   Healthy     Alert
                 |
                 v
              Incident
```

---

## 34. Production Deployment Architecture

The planned production environment is:

```text
                         Internet
                            |
                            v
                      HTTPS Request
                            |
                            v
                      +-----------+
                      |   Nginx   |
                      +-----+-----+
                            |
                            v
                      +-----------+
                      | FastAPI   |
                      +-----+-----+
                            |
               +------------+-------------+
               |                          |
               v                          v
         +-----------+              +------------+
         |PostgreSQL |              | Prometheus |
         +-----------+              +------+-----+
                                          |
                                          v
                                   +-------------+
                                   |Node Exporter|
                                   +-------------+
```

All application components will run on a Linux VPS during the initial production release.

---

## 35. Deployment Flow

```text
Local Development
       |
       | git push
       v
GitHub Repository
       |
       v
GitHub Actions
       |
       | Run tests
       | Build
       | Deploy
       v
Linux VPS
       |
       v
Docker Compose
       |
       +-- FastAPI
       +-- PostgreSQL
       +-- Prometheus
       +-- Node Exporter
       `-- Nginx
```

---

## 36. Environments

CloudOps will use separate environments.

```text
Development
     |
     v
Staging
     |
     v
Production
```

### Development

Runs locally on the developer machine.

### Staging

Used for deployment testing before production.

### Production

Public portfolio deployment.

A single VPS may initially host both staging and production environments using separate configurations.

---

## 37. Environment Variables

Sensitive configuration will use environment variables.

Example public template:

```env
APP_NAME=CloudOps
APP_ENV=development
APP_DEBUG=true
APP_VERSION=0.1.0

DATABASE_URL=postgresql://cloudops:password@localhost:5432/cloudops

SECRET_KEY=replace-with-your-secret-key
```

Real values must be stored in:

```text
.env
```

The `.env` file must never be committed to Git.

---

## 38. Security Principles

The architecture follows several basic security principles.

### Secrets

Never store:

* Passwords
* API tokens
* Database credentials
* Discord webhooks
* SSH keys
* Private keys

inside GitHub.

### Authentication

Passwords will be hashed before being stored.

### Authorization

Role-based access control will restrict sensitive operations.

### HTTPS

Production communication will use HTTPS.

### Database

Database credentials will use environment variables.

### Infrastructure

The public project will use fictional or demo infrastructure.

Real company servers, IP addresses, credentials, and operational data must not be included.

---

## 39. Demo Infrastructure

CloudOps may use fictional infrastructure during development.

Example:

```text
PROD-WEB-01
PROD-DB-01
STAGING-01
BACKUP-01
```

Possible demo states:

```text
PROD-WEB-01    Healthy
PROD-DB-01     Healthy
STAGING-01     Warning
BACKUP-01      Critical
```

This allows CloudOps features to be demonstrated without connecting the project to private company infrastructure.

---

## 40. Logging

CloudOps will generate application logs.

Example:

```text
2026-09-03 14:30:00 INFO Application started

2026-09-03 14:31:00 INFO Health check successful PROD-WEB-01

2026-09-03 14:32:00 WARNING CPU threshold exceeded PROD-WEB-01

2026-09-03 14:32:01 CRITICAL Critical CPU alert created

2026-09-03 14:32:02 INFO Incident INC-2026-0001 created

2026-09-03 14:32:03 INFO Discord notification sent
```

Logs will be useful for:

* Troubleshooting
* Debugging
* Incident analysis
* Deployment verification
* Monitoring failures

---

## 41. Testing Architecture

Automated tests will be stored in:

```text
tests/
```

Planned tests include:

```text
tests/

test_health.py
test_auth.py
test_servers.py
test_monitoring.py
test_alerts.py
test_incidents.py
```

Testing will include:

* API endpoint tests
* Database tests
* Authentication tests
* Permission tests
* Server CRUD tests
* Monitoring logic tests
* Alert threshold tests
* Incident lifecycle tests

---

## 42. Repository Architecture

Planned final repository structure:

```text
cloudops-monitoring-platform/
|
|-- app/
|   |
|   |-- main.py
|   |-- config.py
|   |-- database.py
|   |
|   |-- models/
|   |
|   |-- schemas/
|   |
|   |-- routers/
|   |
|   |-- services/
|   |
|   |-- templates/
|   |
|   `-- static/
|
|-- tests/
|
|-- migrations/
|
|-- prometheus/
|   `-- prometheus.yml
|
|-- nginx/
|   `-- nginx.conf
|
|-- docs/
|   |
|   |-- architecture.md
|   |-- project-plan.md
|   |-- deployment.md
|   |
|   `-- screenshots/
|
|-- .github/
|   `-- workflows/
|
|-- .env.example
|-- .gitignore
|-- Dockerfile
|-- compose.yaml
|-- compose.production.yaml
|-- requirements.txt
|-- README.md
`-- LICENSE
```

---

## 43. Architecture Evolution

The architecture is intentionally being implemented incrementally.

Current phase:

```text
Phase 1
Foundation & Architecture
```

Future phases will introduce:

```text
Phase 2
Authentication & Server Inventory

Phase 3
Monitoring Engine

Phase 4
Prometheus & Infrastructure Metrics

Phase 5
Incident Management

Phase 6
Alert Automation

Phase 7
Docker & Production Deployment

Phase 8
CI/CD, Testing & Documentation
```

The architecture document will be updated as implementation decisions change.

---

## 44. Future Architecture Improvements

Possible post-v1.0 improvements include:

* Grafana dashboards
* Redis
* Celery or another background task queue
* WebSockets
* Kubernetes
* Multiple monitoring agents
* High availability deployment
* Centralized log management
* SSL certificate monitoring
* Backup monitoring
* SLA management
* Alert escalation
* Maintenance windows
* Multiple organizations
* Distributed monitoring
* External API integrations

These features are considered future enhancements and are not required for the initial CloudOps v1.0 release.

---

## Architecture Status

Current architecture status:

```text
Status:
Initial Design

Project Version:
v0.1.0

Development Phase:
Foundation & Architecture
```

This document will evolve together with the CloudOps implementation.
