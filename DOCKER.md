# FitForge Docker Runbook

## 1. Create your runtime env file

Copy `.env.docker.example` to `.env` and fill in:

- `SECRET_KEY`
- `DATABASE_URL`
- `NVIDIA_API_KEY`

For Supabase, keep this shape:

```text
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

## 2. Build and start

```bash
docker compose up --build
```

The `web` container runs migrations and static collection on startup, then starts Gunicorn.

## 3. Open the app

Use Nginx:

```text
http://localhost/
```

Or hit Django directly:

```text
http://localhost:8000/
```

## 4. Useful commands

Create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

Run migrations manually:

```bash
docker compose exec web python manage.py migrate
```

Collect static manually:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

See logs:

```bash
docker compose logs -f web
```

Stop containers:

```bash
docker compose down
```
