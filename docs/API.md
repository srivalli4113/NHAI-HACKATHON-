# API Endpoints

Base path: `/api`

## Auth

- `POST /auth/login`: returns bearer session token.
- `POST /auth/logout`: invalidates current session.
- `GET /auth/me`: current admin identity.

## Employees

- `POST /employees/register`: multipart form with employee fields and photograph.
- `GET /employees`: list registered employees.
- `GET /employees/{employee_id}`: get one employee.
- `DELETE /employees/{employee_id}`: soft-delete employee.

## Recognition

- `POST /recognition/identify`: identify faces from uploaded image.
- `POST /recognition/attendance`: identify and persist attendance event.

## Liveness

- `POST /liveness/check`: calculate liveness score for image/frame.

## Dashboard

- `GET /dashboard/metrics`: aggregate totals and chart series.

## Audit

- `GET /audit/logs`: paginated audit events.
- `GET /audit/export.csv`: CSV export.
- `GET /audit/export.xlsx`: Excel export.

## Benchmark

- `POST /benchmark/run`: local CPU benchmark over synthetic and stored samples.

## Datalake

- `POST /datalake/sync/local`: export queued events to local JSONL.
- `POST /datalake/sync/rest`: attempt REST sync with configured endpoint.
- `GET /datalake/queue`: inspect queue.

