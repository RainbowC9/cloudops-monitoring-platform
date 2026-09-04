# CloudOps Architecture

## Overview

CloudOps is a cloud infrastructure monitoring and incident management platform designed to provide centralized visibility into server health, application availability, infrastructure alerts, and operational incidents.

The project follows a modular architecture so that database operations, monitoring, incident management, alerting, notifications, and deployment components can evolve independently.

CloudOps is being developed incrementally. Components described in this document are clearly identified as either currently implemented or planned.

Current project version:

```text
v0.1.0
```

Current implementation stage:

```text
PostgreSQL Foundation
```

---

## 1. High-Level Architecture

The planned production architecture is:

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
                                   v
                            +--------------+
                            |   FastAPI    |
                            | CloudOps API |
                            +------+-------+
                                   |
             +---------------------+----------------------+
             |                     |                      |
             v                     v                      v
      +--------------+      +-------------+        +-------------+
      | PostgreSQL   |      | Prometheus  |        | Alert Engine|
      | Application  |      | Monitoring  |        |             |
      | Database     |      |             |        +------+------+
      +--------------+      +------+------+               |
                                   |                      |
                                   v                      v
                            +--------------+        +--------------+
                            |Node Exporter |        | Notification |
                            +------+-------+        |   Service    |
                                   |                +------+-------+
                                   v                       |
                            +--------------+               v
                            | Linux Server |        +-------------+
                            |Infrastructure|        | Discord /   |
                            +--------------+        | Email       |
                                                    +-------------+
```

Not all components shown above are implemented yet.

---

# 2. Current Architecture

The current local development environment is:

```text
Client / Browser
       |
       v
    FastAPI
       |
       v
   SQLAlchemy
       |
       v
    Psycopg
       |
       v
  PostgreSQL
```

Current implemented components:

```text
FastAPI                  Implemented
Application Config       Implemented
PostgreSQL               Implemented
SQLAlchemy               Implemented
Psycopg                  Implemented
Database Readiness       Implemented
Alembic Environment      Implemented

Database Models          Not Yet Implemented
Database Tables          Not Yet Created
Authentication           Not Yet Implemented
Prometheus               Not Yet Implemented
Node Exporter            Not Yet Implemented
Incident Management      Not Yet Implemented
Alert Engine             Not Yet Implemented
Docker                   Not Yet Implemented
Nginx                    Not Yet Implemented
CI/CD                    Not Yet Implemented
```

---

# 3. FastAPI Application

FastAPI is the main backend application framework for CloudOps.

Current responsibilities include:

- Exposing REST API endpoints
- Loading application configuration
- Providing application health information
- Performing database readiness checks
- Providing interactive API documentation

Current API endpoints:

```text
GET /
GET /health
GET /ready
```

Planned future responsibilities include:

- User authentication
- Role-based access control
- Server inventory management
- Monitoring configuration
- Infrastructure metrics
- Incident management
- Alert rule management
- Incident timeline management
- Notification integration
- Audit logging

The FastAPI application will act as the central interface between users, PostgreSQL, Prometheus, monitoring services, and external notification systems.

---

# 4. Application Configuration

Application configuration is managed using Pydantic Settings.

Configuration is defined in:

```text
app/config.py
```

The configuration flow is:

```text
.env
  |
  v
Pydantic Settings
  |
  v
Application Configuration
  |
  +----------> FastAPI
  |
  +----------> SQLAlchemy
  |
  `----------> Alembic
```

Current configuration includes:

```text
APP_NAME
APP_ENV
APP_DEBUG
APP_VERSION
DATABASE_URL
SECRET_KEY
```

`SECRET_KEY` is currently optional because authentication has not yet been implemented.

---

# 5. PostgreSQL

PostgreSQL provides persistent storage for CloudOps application data.

The local development PostgreSQL environment is currently configured and connected successfully.

Current configuration:

```text
Database:
cloudops

Application User:
cloudops_user

Host:
localhost

Port:
5432
```

Current database flow:

```text
FastAPI
   |
   v
SQLAlchemy
   |
   v
Psycopg
   |
   v
PostgreSQL
```

The application uses a dedicated PostgreSQL account instead of using the PostgreSQL administrator account.

```text
postgres
   |
   `-- PostgreSQL Administrator

cloudops_user
   |
   `-- CloudOps Application User
```

Database credentials are stored locally using environment variables.

They are not committed to GitHub.

---

# 6. SQLAlchemy

SQLAlchemy provides the database access layer between FastAPI and PostgreSQL.

Current architecture:

```text
FastAPI
   |
   v
Application Logic
   |
   v
SQLAlchemy
   |
   v
Psycopg
   |
   v
PostgreSQL
```

Database configuration is stored in:

```text
app/database.py
```

The current database module provides:

- SQLAlchemy engine
- Database session factory
- SQLAlchemy declarative base
- Database session dependency
- Database connection validation

The project uses:

```python
class Base(DeclarativeBase):
    pass
```

Future SQLAlchemy models will inherit from this base.

Example:

```python
class Server(Base):
    ...
```

Application models have not yet been implemented.

---

# 7. Psycopg

Psycopg provides the PostgreSQL database driver used by SQLAlchemy.

Current database connection format:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

CloudOps uses:

```text
SQLAlchemy
    |
    v
Psycopg
    |
    v
PostgreSQL
```

The real database URL is stored only in the local `.env` file.

---

# 8. Database Connection Management

CloudOps uses a shared SQLAlchemy engine.

The engine uses:

```text
pool_pre_ping=True
```

This allows SQLAlchemy to validate pooled database connections before using them.

Database sessions are created through:

```text
SessionLocal
```

Request flow:

```text
FastAPI Request
      |
      v
   get_db()
      |
      v
Database Session
      |
      v
PostgreSQL
      |
      v
Close Session
```

This ensures that database sessions are closed after use.

---

# 9. Application Health Checks

CloudOps separates application liveness from application readiness.

This allows monitoring systems to distinguish between:

```text
Application process is running
```

and:

```text
Application is actually ready to operate
```

---

## 9.1 Liveness Endpoint

Current endpoint:

```http
GET /health
```

Purpose:

> Confirm that the CloudOps FastAPI application is running.

Current response:

```json
{
  "status": "healthy",
  "application": "CloudOps",
  "version": "0.1.0"
}
```

The liveness endpoint does not depend on PostgreSQL availability.

---

## 9.2 Readiness Endpoint

Current endpoint:

```http
GET /ready
```

Purpose:

> Confirm that CloudOps can successfully connect to its required PostgreSQL database.

Successful response:

```json
{
  "status": "ready",
  "database": "connected",
  "application": "CloudOps",
  "version": "0.1.0"
}
```

The readiness check executes a simple database operation:

```sql
SELECT 1;
```

Current readiness flow:

```text
Client
   |
   v
GET /ready
   |
   v
FastAPI
   |
   v
SQLAlchemy
   |
   v
SELECT 1
   |
   v
PostgreSQL
   |
   +---------------------+
   |                     |
Success                 Failure
   |                     |
   v                     v
200 OK            503 Service Unavailable
   |                     |
   v                     v
Ready                Not Ready
```

If PostgreSQL is unavailable, CloudOps returns:

```json
{
  "status": "not_ready",
  "database": "unavailable",
  "application": "CloudOps",
  "version": "0.1.0"
}
```

with:

```text
HTTP 503 Service Unavailable
```

---

# 10. Alembic

Alembic provides database migration management for CloudOps.

The migration environment has been initialized.

Current structure:

```text
migrations/
|
|-- versions/
|
|-- env.py
|
|-- README
|
`-- script.py.mako

alembic.ini
```

Alembic will be responsible for:

- Creating database tables
- Modifying database tables
- Adding columns
- Removing columns
- Creating constraints
- Updating indexes
- Maintaining schema version history

---

## 10.1 Migration Architecture

The planned migration process is:

```text
SQLAlchemy Models
       |
       v
Base.metadata
       |
       v
Alembic
       |
       v
Autogenerated Migration
       |
       v
Migration Review
       |
       v
PostgreSQL
```

---

## 10.2 Migration Configuration

Database credentials are not stored directly in:

```text
alembic.ini
```

Instead, Alembic retrieves the database URL using the application configuration.

Current configuration flow:

```text
.env
   |
   v
app/config.py
   |
   v
migrations/env.py
   |
   v
Alembic
   |
   v
PostgreSQL
```

This avoids storing real database credentials in GitHub.

---

## 10.3 Initial Migration Status

The Alembic migration environment is initialized, but the first migration has intentionally not been created yet.

Current status:

```text
Alembic Environment:     Configured
Database Models:         Not Yet Implemented
Database Tables:         Not Yet Created
Initial Migration:       Not Yet Created
```

The first migration will be generated after the initial CloudOps database models are implemented.

This prevents creating an unnecessary empty migration.

---

# 11. Planned Database Architecture

The initial CloudOps database is planned to contain:

```text
roles
users

servers
services

health_checks

alert_rules
alerts

incidents
incident_events

audit_logs
```

These tables have not yet been created.

The final database schema will be defined during the next development phase.

---

# 12. Planned Database Relationships

High-level planned relationships:

```text
                       Role
                        |
                        v
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
        Incident Events      Alert
                               |
                               v
                             Server
                            /      \
                           /        \
                          v          v
                  Health Checks    Services
                           \
                            \
                             v
                         Alert Rules
```

The exact relationships may change during schema implementation.

---

# 13. Planned Role Entity

The `roles` table will define user access levels.

Planned roles:

```text
Admin
Engineer
Viewer
```

Possible fields:

```text
roles

id
name
description
created_at
updated_at
```

---

# 14. Planned User Entity

The `users` table will represent CloudOps users.

Possible fields:

```text
users

id
role_id
username
email
password_hash
is_active
created_at
updated_at
```

Passwords will never be stored as plaintext.

---

# 15. Planned Server Entity

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

# 16. Planned Service Entity

The `services` table will represent services associated with monitored infrastructure.

Possible fields:

```text
services

id
server_id
name
service_type
endpoint
status
created_at
updated_at
```

Possible service types:

```text
HTTP
API
DATABASE
APPLICATION
SYSTEM
```

---

# 17. Planned Health Check Entity

The `health_checks` table will store application and service health results.

Possible fields:

```text
health_checks

id
server_id
service_id
check_type
status
response_time
details
checked_at
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

# 18. Planned Alert Rules Entity

The `alert_rules` table will define monitoring thresholds.

Possible fields:

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

Warning Threshold:
70

Critical Threshold:
90

Enabled:
true
```

---

# 19. Planned Alerts Entity

The `alerts` table will store monitoring alerts.

Possible fields:

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

Possible alert states:

```text
ACTIVE
ACKNOWLEDGED
RESOLVED
```

---

# 20. Planned Incident Entity

The `incidents` table will represent operational incidents.

Possible fields:

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

# 21. Planned Incident Event Entity

Each significant incident change will be recorded separately.

Possible fields:

```text
incident_events

id
incident_id
event_type
description
created_by
created_at
```

Example timeline:

```text
14:32 Incident Created

14:35 Incident Acknowledged

14:38 Assigned to Engineer

14:41 Investigation Started

14:55 CPU usage returned to normal

15:02 Incident Resolved

15:10 Incident Closed
```

This provides an operational audit trail without overwriting incident history.

---

# 22. Planned Audit Log Entity

Administrative and security-sensitive activities may be recorded.

Examples include:

- User created
- User role changed
- Server registered
- Server removed
- Alert rule modified
- Incident assigned
- Incident resolved
- Incident closed

Possible fields:

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

# 23. Authentication Architecture

Authentication has not yet been implemented.

Planned roles:

```text
Admin
Engineer
Viewer
```

Planned permissions:

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

Authentication will be implemented after the database foundation and models are completed.

---

# 24. Prometheus

Prometheus will provide infrastructure metric collection.

Prometheus is not yet implemented.

Planned metrics include:

- CPU usage
- Memory usage
- Disk usage
- Filesystem availability
- System load
- Network statistics
- System uptime
- Infrastructure availability

Planned flow:

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

# 25. Node Exporter

Node Exporter will expose Linux operating system and hardware metrics.

Node Exporter is not yet implemented.

Planned metrics include:

- CPU
- Memory
- Disk
- Filesystem
- Network
- Load average
- Uptime

Planned flow:

```text
PROD-WEB-01
     |
     | System Metrics
     v
Node Exporter
     |
     | Metrics Endpoint
     v
Prometheus
```

---

# 26. Monitoring Engine

CloudOps will include an application-level monitoring engine.

This component is not yet implemented.

Planned checks include:

- HTTP endpoint availability
- API availability
- Website status
- HTTP response latency
- Database connectivity
- Application service availability

Example planned flow:

```text
CloudOps
   |
   | HTTP Request
   v
Target Service
   |
   +------------------+
   |                  |
HTTP 200          Timeout / Error
   |                  |
   v                  v
Healthy              Alert
```

---

# 27. Alert Engine

The CloudOps alert engine is planned but not yet implemented.

It will evaluate monitoring metrics against configurable thresholds.

Example thresholds:

```text
CPU Warning:      70%
CPU Critical:     90%

Memory Warning:   75%
Memory Critical:  90%

Disk Warning:     80%
Disk Critical:    95%
```

Planned alert flow:

```text
Monitoring Metric
       |
       v
Threshold Evaluation
       |
       v
Threshold Exceeded
       |
       v
Check Existing Alert
       |
      / \
    Yes  No
     |    |
     v    v
 Update  Create
 Alert   Alert
     \    /
      \  /
       v
Incident Evaluation
```

---

# 28. Incident Management

Incident management is planned but not yet implemented.

Each incident may include:

- Incident number
- Title
- Description
- Severity
- Status
- Related server
- Related alert
- Assigned engineer
- Created time
- Acknowledged time
- Resolved time
- Closed time

Planned severity levels:

```text
P1 - Critical
P2 - High
P3 - Medium
P4 - Low
```

---

# 29. Incident Lifecycle

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

Engineers will manage incidents through the CloudOps application.

---

# 30. Incident Deduplication

Infrastructure monitoring may repeatedly detect the same condition.

For example:

```text
14:30 CPU 94%
14:31 CPU 95%
14:32 CPU 93%
14:33 CPU 96%
```

CloudOps should not create multiple active incidents for the same condition.

Planned deduplication flow:

```text
Threshold Exceeded
        |
        v
Search Active Incidents
        |
        v
Same Server + Same Alert?
        |
       / \
     Yes  No
      |    |
      v    v
 Update   Create
Existing   New
Incident Incident
```

---

# 31. Notification Service

External notifications are planned but not yet implemented.

Initial planned integration:

```text
Discord Webhook
```

Possible future integrations:

- Email
- Slack
- Microsoft Teams

Planned flow:

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

# 32. REST API Architecture

As CloudOps grows, API routes will be separated into FastAPI routers.

Planned structure:

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
|-- config.py
|
|-- database.py
|
`-- main.py
```

This keeps routing, database models, schemas, configuration, and business logic separate.

---

# 33. Service Layer

Business logic will eventually be separated from API routes.

Planned location:

```text
app/services/
```

Planned modules:

```text
monitoring.py
prometheus.py
alerts.py
notifications.py
```

Responsibilities:

### monitoring.py

- HTTP health checks
- Service availability
- Health status evaluation

### prometheus.py

- Query Prometheus
- Retrieve infrastructure metrics
- Normalize monitoring information

### alerts.py

- Evaluate thresholds
- Create alerts
- Resolve alerts
- Trigger incidents
- Prevent duplicate incidents

### notifications.py

- Send Discord notifications
- Support future notification integrations

---

# 34. Request Flow

Current database-backed request architecture:

```text
Client
   |
   v
FastAPI Route
   |
   v
Application Logic
   |
   v
SQLAlchemy
   |
   v
Psycopg
   |
   v
PostgreSQL
   |
   v
FastAPI Response
   |
   v
Client
```

After production deployment, Nginx will be added before FastAPI.

---

# 35. Planned Monitoring Data Flow

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
Dashboard             Alert Engine
                           |
                           v
                        Incident
                           |
                           v
                     Notification
```

---

# 36. Docker

Docker containerization is planned but not yet implemented.

Planned services:

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

- Consistent environments
- Easier deployment
- Service isolation
- Dependency management
- Persistent service configuration
- Easier production setup

---

# 37. Docker Compose

Docker Compose will manage the CloudOps multi-container environment.

Planned services:

```text
services:

cloudops-api
cloudops-db
prometheus
node-exporter
nginx
```

Development and production configurations may eventually be separated:

```text
compose.yaml

compose.production.yaml
```

---

# 38. Nginx

Nginx is planned for the production deployment phase.

It will act as the public reverse proxy.

Planned architecture:

```text
Internet
   |
   v
Nginx
   |
   v
FastAPI
```

Responsibilities will include:

- Reverse proxying
- HTTPS termination
- Routing requests to FastAPI
- HTTP-to-HTTPS redirection
- Public request handling

---

# 39. HTTPS

Production traffic will use HTTPS.

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

SSL/TLS certificates will be configured during the deployment phase.

---

# 40. GitHub Actions

GitHub Actions will provide Continuous Integration and Continuous Deployment.

It is not yet implemented.

Planned workflow:

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

---

# 41. Production Deployment Architecture

The planned initial production architecture is:

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

The first production release is expected to run on a Linux VPS.

---

# 42. Deployment Flow

Planned deployment workflow:

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
       | Run Tests
       |
       | Build
       |
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

# 43. Environments

CloudOps is planned to support:

```text
Development
     |
     v
Staging
     |
     v
Production
```

## Development

Currently implemented.

Runs locally on the development machine.

Current database:

```text
Local PostgreSQL
```

## Staging

Planned.

Will be used for deployment validation before production changes.

## Production

Planned.

Will provide the public portfolio deployment.

---

# 44. Environment Variables

Sensitive and environment-specific configuration is stored using environment variables.

Public example:

```env
APP_NAME=CloudOps
APP_ENV=development
APP_DEBUG=true
APP_VERSION=0.1.0

DATABASE_URL=postgresql+psycopg://cloudops_user:CHANGE_ME@localhost:5432/cloudops

SECRET_KEY=
```

The real local configuration is stored in:

```text
.env
```

The `.env` file must never be committed to GitHub.

The repository contains:

```text
.env.example
```

instead.

---

# 45. Security Principles

CloudOps follows several basic security principles.

## Secrets

Never commit:

- Database passwords
- API tokens
- Authentication tokens
- Discord webhooks
- SSH private keys
- Private certificates
- Real `.env` files

## Database Accounts

The application uses:

```text
cloudops_user
```

instead of the PostgreSQL administrator account.

## Authentication

Passwords will be hashed before database storage when authentication is implemented.

## Authorization

Role-based access control will restrict privileged operations.

## HTTPS

Production traffic will use HTTPS.

## Infrastructure Privacy

The public project will use fictional or demonstration infrastructure.

Real company:

- IP addresses
- Credentials
- Customer information
- Production databases
- Infrastructure details

must not be added to the repository.

---

# 46. Demo Infrastructure

CloudOps will use fictional infrastructure for demonstrations.

Example:

```text
PROD-WEB-01
PROD-DB-01
STAGING-01
BACKUP-01
```

Possible demonstration states:

```text
PROD-WEB-01    Healthy
PROD-DB-01     Healthy
STAGING-01     Warning
BACKUP-01      Critical
```

This allows the system to demonstrate realistic CloudOps workflows without exposing real infrastructure.

---

# 47. Logging

Application logging will be expanded throughout development.

Example future logs:

```text
2026-09-04 10:30:00 INFO Application started

2026-09-04 10:31:00 INFO Database readiness check successful

2026-09-04 10:32:00 INFO Health check successful PROD-WEB-01

2026-09-04 10:33:00 WARNING CPU threshold exceeded PROD-WEB-01

2026-09-04 10:33:01 CRITICAL Critical CPU alert created

2026-09-04 10:33:02 INFO Incident INC-2026-0001 created

2026-09-04 10:33:03 INFO Discord notification sent
```

Logging will support:

- Troubleshooting
- Debugging
- Monitoring analysis
- Incident analysis
- Deployment verification

---

# 48. Testing Architecture

Automated tests have not yet been implemented.

Planned test structure:

```text
tests/
|
|-- test_health.py
|-- test_database.py
|-- test_auth.py
|-- test_servers.py
|-- test_monitoring.py
|-- test_alerts.py
`-- test_incidents.py
```

Planned testing includes:

- Root endpoint tests
- Liveness endpoint tests
- Readiness endpoint tests
- Database connectivity tests
- Authentication tests
- Permission tests
- Server CRUD tests
- Monitoring logic tests
- Alert threshold tests
- Incident lifecycle tests

---

# 49. Current Repository Architecture

The repository currently contains:

```text
cloudops-monitoring-platform/
|
|-- app/
|   |
|   |-- __init__.py
|   |-- config.py
|   |-- database.py
|   `-- main.py
|
|-- migrations/
|   |
|   |-- versions/
|   |-- env.py
|   |-- README
|   `-- script.py.mako
|
|-- docs/
|   |
|   |-- architecture.md
|   `-- project-plan.md
|
|-- .env.example
|-- .gitignore
|-- alembic.ini
|-- requirements.txt
|-- README.md
`-- LICENSE
```

The private local file:

```text
.env
```

is intentionally excluded from Git.

---

# 50. Planned Final Repository Architecture

The repository is expected to eventually expand to:

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
|-- alembic.ini
|-- Dockerfile
|-- compose.yaml
|-- compose.production.yaml
|-- requirements.txt
|-- README.md
`-- LICENSE
```

---

# 51. Architecture Evolution

CloudOps is intentionally being developed incrementally.

Overall roadmap:

```text
Phase 1
Foundation & Architecture

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

Current implementation stage:

```text
PostgreSQL Foundation
```

Current completed database foundation:

```text
PostgreSQL Database          Completed
Application Database User    Completed
SQLAlchemy                   Completed
Psycopg                      Completed
Database Connection          Completed
Readiness Endpoint           Completed
Alembic Initialization       Completed
```

Next implementation stage:

```text
Design CloudOps Database Schema
```

The next stage will introduce SQLAlchemy models for:

```text
roles
users
servers
services
health_checks
alert_rules
alerts
incidents
incident_events
audit_logs
```

After the models are created, the first real Alembic migration will be generated and applied to PostgreSQL.

---

# 52. Future Architecture Improvements

Potential post-v1.0 enhancements include:

- Grafana dashboards
- Redis
- Background job workers
- Celery or another task queue
- WebSockets
- Kubernetes
- Multiple monitoring agents
- High availability
- Centralized logging
- SSL certificate expiry monitoring
- Backup monitoring
- SLA tracking
- Alert escalation
- Maintenance windows
- Multiple organizations
- Distributed monitoring
- External API integrations

These features are outside the initial CloudOps `v1.0` scope.

---

# Architecture Status

Current status:

```text
Project:
CloudOps Monitoring Platform

Project Version:
v0.1.0

Overall Phase:
Phase 1 - Foundation & Architecture

Current Implementation Stage:
PostgreSQL Foundation

FastAPI:
Implemented

PostgreSQL:
Implemented

SQLAlchemy:
Implemented

Psycopg:
Implemented

Liveness Endpoint:
Implemented

Readiness Endpoint:
Implemented

Alembic Environment:
Implemented

Database Models:
Not Yet Implemented

Database Tables:
Not Yet Created

Initial Migration:
Not Yet Created
```

Next task:

```text
Issue #4
Design CloudOps Database Schema
```

This document will continue to evolve together with the CloudOps implementation.